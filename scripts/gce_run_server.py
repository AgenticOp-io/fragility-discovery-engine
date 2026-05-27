#!/usr/bin/env python3
"""
GCE-side HTTP backend for the public workbench "Run a scenario" page.

Runs on the VM, bound to 127.0.0.1; nginx proxies /api/ → here.
Spawns short, capped subprocess runs of the engine CLIs and writes their
artifacts under the public web root so the viewers can load them.

Routes
------
GET  /api/health           : liveness + queue depth
POST /api/run              : enqueue a new run (validated, capped)
GET  /api/run/<id>         : status of one run
GET  /api/runs             : recent run summaries

All artifacts live in ``{PUBLIC_ROOT}/runs/<id>/`` and are served as static
files by nginx; the JSON viewers load them via ``/runs/<id>/best_replay.json``.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
import uuid
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_ROOT = Path(os.environ.get("FRAGILITY_PUBLIC_ROOT", "/var/www/fragility/public"))
RUNS_DIR = PUBLIC_ROOT / "runs"
PYTHON_BIN = os.environ.get("FRAGILITY_PYTHON", sys.executable)
LISTEN_HOST = os.environ.get("FRAGILITY_RUNNER_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("FRAGILITY_RUNNER_PORT", "8765"))

MAX_CONCURRENT = 2
RUN_TIMEOUT_S = 180

CAPS = {
    "horizon": (4, 48),
    "generations": (1, 12),
    "population": (4, 32),
    "seed": (0, 2**31 - 1),
}
# Optional starting-level knob exposed on the run page (flag name, default value).
MODE_INITIAL: dict[str, tuple[str, float]] = {
    "resource_cascade": ("--initial-overload", 0.06),
    "service_backlog": ("--initial-backlog", 0.06),
    "liquidity_ladder": ("--initial-margin", 0.06),
    "inventory_buffer": ("--initial-stock", 0.88),
    "coevolution_resource_cascade": ("--initial-overload", 0.05),
    "coevolution_service_backlog": ("--initial-backlog", 0.05),
    "coevolution_liquidity_ladder": ("--initial-margin", 0.06),
    "coevolution_inventory_buffer": ("--initial-stock", 0.88),
}
RUNS_INDEX = RUNS_DIR / "index.json"
MODES = {
    "aggregate",
    "network",
    "resource_cascade",
    "service_backlog",
    "liquidity_ladder",
    "inventory_buffer",
    # Co-evolution variants: same domain physics, attacker/defender alternating search.
    # Output is pareto_front.json (+ best_replay.json). horizon = attacker_horizon.
    "coevolution_aggregate",
    "coevolution_network",
    "coevolution_resource_cascade",
    "coevolution_service_backlog",
    "coevolution_liquidity_ladder",
    "coevolution_inventory_buffer",
}
# Modes whose CLI honors --horizon / --attacker-horizon.
# Fixed-horizon modes ignore the horizon field (script uses its own default).
HORIZON_AWARE_MODES = {
    "aggregate",
    "network",
    "coevolution_aggregate",
    "coevolution_network",
}
# Modes that output a Pareto front as primary artifact (linked to pareto viewer).
PARETO_MODES = {
    "coevolution_aggregate",
    "coevolution_network",
    "coevolution_resource_cascade",
    "coevolution_service_backlog",
    "coevolution_liquidity_ladder",
    "coevolution_inventory_buffer",
}

_active = 0
_active_lock = threading.Lock()


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate(body: dict) -> tuple[dict, str | None]:
    mode = str(body.get("mode", "aggregate"))
    if mode not in MODES:
        return {}, f"mode must be one of {sorted(MODES)}"
    out: dict[str, object] = {"mode": mode}
    for k, (lo, hi) in CAPS.items():
        v = body.get(k)
        if v is None:
            return {}, f"{k} is required"
        try:
            iv = int(v)
        except (TypeError, ValueError):
            return {}, f"{k} must be an integer"
        if not (lo <= iv <= hi):
            return {}, f"{k} must be in [{lo}, {hi}]"
        out[k] = iv
    if mode in MODE_INITIAL:
        default_initial = MODE_INITIAL[mode][1]
        raw = body.get("initial_level")
        if raw is None:
            out["initial_level"] = default_initial
        else:
            try:
                fv = float(raw)
            except (TypeError, ValueError):
                return {}, "initial_level must be a number between 0 and 1"
            if not (0.0 <= fv <= 1.0):
                return {}, "initial_level must be in [0.0, 1.0]"
            out["initial_level"] = fv
    return out, None


def _append_initial_flag(cmd: list[str], req: dict) -> None:
    mode = str(req["mode"])
    if mode in MODE_INITIAL:
        flag, default = MODE_INITIAL[mode]
        cmd.extend([flag, str(req.get("initial_level", default))])


def _rebuild_runs_index() -> None:
    if not RUNS_DIR.is_dir():
        return
    items: list[dict] = []
    for run_dir in RUNS_DIR.iterdir():
        if not run_dir.is_dir() or run_dir.name == "index.json":
            continue
        sp = run_dir / "status.json"
        if sp.is_file():
            try:
                items.append(json.loads(sp.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
    items.sort(key=lambda row: str(row.get("started_utc", "")), reverse=True)
    RUNS_INDEX.write_text(
        json.dumps({"schema": "fragility-runs-index-v1", "runs": items[:100]}, indent=2),
        encoding="utf-8",
    )


def _update_runs_index(entry: dict) -> None:
    try:
        if RUNS_INDEX.is_file():
            data = json.loads(RUNS_INDEX.read_text(encoding="utf-8"))
            runs: list[dict] = list(data.get("runs") or [])
        else:
            runs = []
    except (OSError, json.JSONDecodeError):
        runs = []
    run_id = entry.get("id")
    runs = [row for row in runs if row.get("id") != run_id]
    runs.insert(0, entry)
    RUNS_INDEX.write_text(
        json.dumps({"schema": "fragility-runs-index-v1", "runs": runs[:100]}, indent=2),
        encoding="utf-8",
    )


def _build_cmd(req: dict, run_dir: Path) -> list[str]:
    """Translate validated request → whitelisted CLI argv. Never accepts shell input."""

    mode = req["mode"]
    replay = run_dir / "best_replay.json"
    minimized = run_dir / "minimized_replay.json"
    seed = str(req["seed"])
    gens = str(req["generations"])
    pop = str(req["population"])
    horizon = str(req["horizon"])
    scripts_dir = ROOT / "scripts"

    if mode == "aggregate":
        return [
            PYTHON_BIN, str(scripts_dir / "run_ga_demo.py"),
            "--seed", seed, "--generations", gens, "--population-size", pop,
            "--export-replay", str(replay), "--export-minimized-replay", str(minimized),
        ]
    if mode == "network":
        # ER topology, capped node count. Same seed drives both GA and graph for reproducibility.
        return [
            PYTHON_BIN, str(scripts_dir / "run_network_demo.py"),
            "--ga-seed", seed, "--graph-seed", seed,
            "--horizon", horizon, "--generations", gens, "--population-size", pop,
            "--nodes", "32", "--graph-kind", "erdos_renyi", "--er-p", "0.12",
            "--export-replay", str(replay),
        ]
    if mode == "resource_cascade":
        cmd = [
            PYTHON_BIN, str(scripts_dir / "run_resource_cascade_ga_demo.py"),
            "--seed", seed, "--generations", gens, "--population-size", pop,
            "--export-replay", str(replay), "--export-minimized-replay", str(minimized),
        ]
        _append_initial_flag(cmd, req)
        return cmd
    if mode == "service_backlog":
        cmd = [
            PYTHON_BIN, str(scripts_dir / "run_service_backlog_ga_demo.py"),
            "--seed", seed, "--generations", gens, "--population-size", pop,
            "--export-replay", str(replay), "--export-minimized-replay", str(minimized),
        ]
        _append_initial_flag(cmd, req)
        return cmd
    if mode == "liquidity_ladder":
        cmd = [
            PYTHON_BIN, str(scripts_dir / "run_liquidity_ladder_ga_demo.py"),
            "--seed", seed, "--generations", gens, "--population-size", pop,
            "--export-replay", str(replay), "--export-minimized-replay", str(minimized),
        ]
        _append_initial_flag(cmd, req)
        return cmd
    if mode == "inventory_buffer":
        cmd = [
            PYTHON_BIN, str(scripts_dir / "run_inventory_buffer_ga_demo.py"),
            "--seed", seed, "--generations", gens, "--population-size", pop,
            "--export-replay", str(replay), "--export-minimized-replay", str(minimized),
        ]
        _append_initial_flag(cmd, req)
        return cmd

    # --- Co-evolution modes ---
    # All coevolution variants use the shared run_coevolution.py script.
    # horizon → --attacker-horizon; generations → --attacker-generations + --defender-generations
    # population → --attacker-population + --defender-population; rounds fixed at 1 for the web UI.
    pareto = run_dir / "pareto_front.json"
    coev_domain = mode.split("coevolution_", 1)[1]  # e.g. "aggregate"
    base_coev = [
        PYTHON_BIN, str(scripts_dir / "run_coevolution.py"),
        "--mode", coev_domain,
        "--seed", seed,
        "--attacker-generations", gens,
        "--attacker-population", pop,
        "--defender-generations", gens,
        "--defender-population", pop,
        "--rounds", "1",
        "--export-pareto-json", str(pareto),
        "--export-replay", str(replay),
    ]
    if coev_domain in ("aggregate", "network"):
        base_coev += ["--attacker-horizon", horizon]
    if coev_domain == "network":
        base_coev += ["--nodes", "32", "--graph-kind", "erdos_renyi", "--er-p", "0.12",
                      "--graph-seed", seed]
    _append_initial_flag(base_coev, req)
    return base_coev

    raise ValueError(f"no command builder for mode {mode!r}")


def _viewer_urls(mode: str, run_id: str, run_dir: Path) -> dict[str, str | None]:
    """Return viewer URL(s) for the artifacts produced by a completed run."""
    replay = run_dir / "best_replay.json"
    pareto = run_dir / "pareto_front.json"
    out: dict[str, str | None] = {"viewer_url": None, "pareto_url": None}
    if replay.is_file():
        out["viewer_url"] = f"/artifacts/replay_viewer/index.html#src=/runs/{run_id}/best_replay.json"
    if pareto.is_file():
        out["pareto_url"] = f"/artifacts/pareto_viewer/index.html#src=/runs/{run_id}/pareto_front.json"
    return out


def _run(req: dict, run_dir: Path, status_path: Path) -> None:
    """Spawn the whitelisted CLI for ``req['mode']`` with a hard wall-clock cap."""

    mode = req["mode"]
    is_pareto_mode = mode in PARETO_MODES
    primary_path = run_dir / ("pareto_front.json" if is_pareto_mode else "best_replay.json")

    cmd = _build_cmd(req, run_dir)
    started = _now()
    t0 = time.time()
    log_path = run_dir / "stdout.log"
    err_path = run_dir / "stderr.log"
    try:
        with log_path.open("w", encoding="utf-8") as lo, err_path.open("w", encoding="utf-8") as le:
            proc = subprocess.Popen(cmd, cwd=ROOT, stdout=lo, stderr=le)
            try:
                rc = proc.wait(timeout=RUN_TIMEOUT_S)
            except subprocess.TimeoutExpired:
                proc.kill()
                rc = -1
    except Exception as exc:
        _write_status(
            status_path,
            req=req,
            state="failed",
            started=started,
            error=f"spawn-failed: {exc}",
        )
        return

    state = "done" if rc == 0 and primary_path.is_file() else "failed"
    urls = _viewer_urls(mode, run_dir.name, run_dir)
    extra: dict[str, object] = {
        "exit_code": rc,
        "elapsed_s": round(time.time() - t0, 2),
        **urls,
        "artifacts": [p.name for p in run_dir.iterdir() if p.is_file()],
        "cli": [str(c) for c in cmd],
    }
    if state == "failed":
        try:
            extra["stderr_tail"] = err_path.read_text(encoding="utf-8")[-2000:]
        except OSError:
            pass
    _write_status(status_path, req=req, state=state, started=started, **extra)
    try:
        _update_runs_index(json.loads(status_path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        pass


def _write_status(path: Path, *, req: dict, state: str, started: str, **extra: object) -> None:
    payload: dict[str, object] = {
        "schema": "fragility-run-status-v1",
        "id": path.parent.name,
        "request": req,
        "state": state,
        "started_utc": started,
        "updated_utc": _now(),
    }
    payload.update(extra)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _enqueue(req: dict) -> dict:
    global _active
    with _active_lock:
        if _active >= MAX_CONCURRENT:
            return {"error": "busy", "active": _active, "max": MAX_CONCURRENT}
        _active += 1
    run_id = uuid.uuid4().hex[:12]
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    status_path = run_dir / "status.json"
    _write_status(status_path, req=req, state="running", started=_now())

    def _worker() -> None:
        global _active
        try:
            _run(req, run_dir, status_path)
        finally:
            with _active_lock:
                _active -= 1

    threading.Thread(target=_worker, daemon=True).start()
    mode = req["mode"]
    initial_viewer = (
        f"/artifacts/pareto_viewer/index.html#src=/runs/{run_id}/pareto_front.json"
        if mode in PARETO_MODES
        else f"/artifacts/replay_viewer/index.html#src=/runs/{run_id}/best_replay.json"
    )
    return {
        "id": run_id,
        "state": "running",
        "status_url": f"/api/run/{run_id}",
        "viewer_url": initial_viewer,
    }


def _list_runs(limit: int = 25) -> list[dict]:
    if RUNS_INDEX.is_file():
        try:
            data = json.loads(RUNS_INDEX.read_text(encoding="utf-8"))
            rows = list(data.get("runs") or [])
            if rows:
                return rows[:limit]
        except (OSError, json.JSONDecodeError):
            pass
    if not RUNS_DIR.is_dir():
        return []
    items = []
    for run_dir in sorted(RUNS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        if not run_dir.is_dir():
            continue
        sp = run_dir / "status.json"
        if sp.is_file():
            try:
                items.append(json.loads(sp.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
    return items


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: dict | list) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/health":
            self._send(
                200,
                {
                    "ok": True,
                    "active": _active,
                    "max": MAX_CONCURRENT,
                    "modes": sorted(MODES),
                    "horizon_aware_modes": sorted(HORIZON_AWARE_MODES),
                    "pareto_modes": sorted(PARETO_MODES),
                    "caps": {k: list(v) for k, v in CAPS.items()},
                    "initial_modes": sorted(MODE_INITIAL.keys()),
                    "timeout_s": RUN_TIMEOUT_S,
                },
            )
            return
        if path == "/api/runs":
            self._send(200, _list_runs())
            return
        if path.startswith("/api/run/"):
            run_id = path[len("/api/run/") :].strip("/")
            sp = RUNS_DIR / run_id / "status.json"
            if not sp.is_file():
                self._send(404, {"error": "not-found"})
                return
            self._send(200, json.loads(sp.read_text(encoding="utf-8")))
            return
        self._send(404, {"error": "not-found"})

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/api/run":
            self._send(404, {"error": "not-found"})
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > 2048:
            self._send(400, {"error": "missing-or-oversize-body"})
            return
        try:
            body = json.loads(self.rfile.read(length))
        except json.JSONDecodeError as exc:
            self._send(400, {"error": f"invalid-json: {exc}"})
            return
        req, err = _validate(body if isinstance(body, dict) else {})
        if err:
            self._send(400, {"error": err})
            return
        resp = _enqueue(req)
        self._send(202 if "id" in resp else 503, resp)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default=LISTEN_HOST)
    ap.add_argument("--port", type=int, default=LISTEN_PORT)
    args = ap.parse_args()
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    _rebuild_runs_index()
    server = ThreadingHTTPServer((args.host, args.port), _Handler)
    sys.stderr.write(
        f"fragility runner listening on http://{args.host}:{args.port} (runs → {RUNS_DIR})\n"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
