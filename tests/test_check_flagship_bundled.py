"""CLI parity for scripts/check_flagship_bundled.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_check_flagship_bundled_script_exits_zero() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_flagship_bundled.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "OK:" in proc.stdout
