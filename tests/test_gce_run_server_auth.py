"""Run API key / anonymous-run policy for scripts/gce_run_server.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "scripts" / "gce_run_server.py"


def _load_server_module(
    monkeypatch,
    *,
    api_key: str = "",
    allow_anonymous: str = "0",
) -> object:
    monkeypatch.setenv("FRAGILITY_RUN_API_KEY", api_key)
    monkeypatch.setenv("FRAGILITY_ALLOW_ANONYMOUS_RUNS", allow_anonymous)
    monkeypatch.setenv("FRAGILITY_PUBLIC_ROOT", str(ROOT / "artifacts" / "test_runs_public"))
    spec = importlib.util.spec_from_file_location("gce_run_server_test", SERVER_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gce_run_server_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_check_api_key_closed_when_unset(monkeypatch) -> None:
    mod = _load_server_module(monkeypatch, api_key="", allow_anonymous="0")

    class H(BaseHTTPRequestHandler):
        def __init__(self) -> None:
            self.headers = {}

    err = mod._check_api_key(H())  # type: ignore[arg-type]
    assert err is not None
    assert "live-runs-disabled" in err


def test_check_api_key_open_when_anonymous_opt_in(monkeypatch) -> None:
    mod = _load_server_module(monkeypatch, api_key="", allow_anonymous="1")

    class H(BaseHTTPRequestHandler):
        def __init__(self) -> None:
            self.headers = {}

    assert mod._check_api_key(H()) is None  # type: ignore[arg-type]


def test_check_api_key_rejects_wrong_key(monkeypatch) -> None:
    mod = _load_server_module(monkeypatch, api_key="secret")

    class H(BaseHTTPRequestHandler):
        def __init__(self) -> None:
            self.headers = {"X-Fragility-Run-Key": "wrong"}

    assert mod._check_api_key(H()) is not None  # type: ignore[arg-type]


def test_post_run_returns_403_style_when_closed(monkeypatch, tmp_path) -> None:
    public = tmp_path / "public"
    runs = public / "runs"
    runs.mkdir(parents=True)
    mod = _load_server_module(monkeypatch, api_key="", allow_anonymous="0")
    mod.RUNS_DIR = runs
    mod.RUN_API_KEY = ""
    mod.ALLOW_ANONYMOUS_RUNS = False

    server = mod.ThreadingHTTPServer(("127.0.0.1", 0), mod._Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{port}"
        health = json.loads(urlopen(f"{base}/api/health", timeout=2).read())
        assert health["run_auth_required"] is True
        assert health["live_runs_enabled"] is False

        body = json.dumps(
            {
                "mode": "aggregate",
                "seed": 1,
                "horizon": 8,
                "generations": 2,
                "population": 4,
            }
        ).encode()
        req = Request(f"{base}/api/run", data=body, method="POST", headers={"Content-Type": "application/json"})
        try:
            urlopen(req, timeout=2)
            raise AssertionError("expected 401")
        except HTTPError as exc:
            assert exc.code == 401
            payload = json.loads(exc.read().decode())
            assert "live-runs-disabled" in payload.get("error", "")
    finally:
        server.shutdown()


def test_post_run_returns_401_without_key(monkeypatch, tmp_path) -> None:
    public = tmp_path / "public"
    runs = public / "runs"
    runs.mkdir(parents=True)
    mod = _load_server_module(monkeypatch, api_key="test-key-123")
    mod.RUNS_DIR = runs
    mod.RUN_API_KEY = "test-key-123"

    server = mod.ThreadingHTTPServer(("127.0.0.1", 0), mod._Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{port}"
        health = json.loads(urlopen(f"{base}/api/health", timeout=2).read())
        assert health["run_auth_required"] is True

        body = json.dumps(
            {
                "mode": "aggregate",
                "seed": 1,
                "horizon": 8,
                "generations": 2,
                "population": 4,
            }
        ).encode()
        req = Request(f"{base}/api/run", data=body, method="POST", headers={"Content-Type": "application/json"})
        try:
            urlopen(req, timeout=2)
            raise AssertionError("expected 401")
        except HTTPError as exc:
            assert exc.code == 401
            payload = json.loads(exc.read().decode())
            assert "unauthorized" in payload.get("error", "")
    finally:
        server.shutdown()
