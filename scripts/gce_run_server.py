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
MODES = {"aggregate"}

_active = 0
_active_lock = threading.Lock()


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate(body: dict) -> tuple[dict, str | None]:
    mode = str(body.get("mode", "aggregate"))
    if mode not in MODES:
        return {}, f"mode must be one of {sorted(MODES)}"
    out = {"mode": mode}
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
    return out, None


def _run_aggregate(req: dict, run_dir: Path, status_path: Path) -> None:
    """Run the aggregate GA CLI with the user's capped parameters."""

    replay_path = run_dir / "best_replay.json"
    minimized_path = run_dir / "minimized_replay.json"
    cmd = [
        PYTHON_BIN,
        str(ROOT / "scripts" / "run_ga_demo.py"),
        "--seed",
        str(req["seed"]),
        "--generations",
        str(req["generations"]),
        "--population-size",
        str(req["population"]),
        "--export-replay",
        str(replay_path),
        "--export-minimized-replay",
        str(minimized_path),
    ]
    started = _now()
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

    state = "done" if rc == 0 and replay_path.is_file() else "failed"
    viewer_url = f"/artifacts/replay_viewer/index.html#src=/runs/{run_dir.name}/best_replay.json"
    extra: dict[str, object] = {
        "exit_code": rc,
        "viewer_url": viewer_url if state == "done" else None,
        "artifacts": [p.name for p in run_dir.iterdir() if p.is_file()],
    }
    if state == "failed":
        try:
            extra["stderr_tail"] = err_path.read_text(encoding="utf-8")[-2000:]
        except OSError:
            pass
    _write_status(status_path, req=req, state=state, started=started, **extra)


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
            if req["mode"] == "aggregate":
                _run_aggregate(req, run_dir, status_path)
            else:
                _write_status(
                    status_path,
                    req=req,
                    state="failed",
                    started=_now(),
                    error=f"mode {req['mode']} not yet supported on this host",
                )
        finally:
            with _active_lock:
                _active -= 1

    threading.Thread(target=_worker, daemon=True).start()
    return {
        "id": run_id,
        "state": "running",
        "status_url": f"/api/run/{run_id}",
        "viewer_url": f"/artifacts/replay_viewer/index.html#src=/runs/{run_id}/best_replay.json",
    }


def _list_runs(limit: int = 25) -> list[dict]:
    if not RUNS_DIR.is_dir():
        return []
    items = []
    for run_dir in sorted(RUNS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
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
            self._send(200, {"ok": True, "active": _active, "max": MAX_CONCURRENT, "modes": sorted(MODES)})
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
