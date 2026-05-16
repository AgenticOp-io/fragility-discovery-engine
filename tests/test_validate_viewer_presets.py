"""scripts/validate_viewer_presets.py exits zero when bundled paths exist."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_validate_viewer_presets_script() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_viewer_presets.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "OK:" in proc.stdout
