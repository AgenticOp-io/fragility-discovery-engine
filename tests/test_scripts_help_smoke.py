"""Every scripts/*.py CLI must exit 0 on ``--help``.

Non-ASCII text in ArgumentParser descriptions breaks ``--help`` on Windows consoles
using legacy cp1252 (UnicodeEncodeError during print_help).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

_SCRIPT_NAMES = sorted(
    p.name for p in (ROOT / "scripts").glob("*.py") if p.name != "__init__.py"
)


@pytest.mark.parametrize("script_name", _SCRIPT_NAMES)
def test_script_help_exits_zero(script_name: str) -> None:
    script_path = ROOT / "scripts" / script_name
    proc = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    assert proc.returncode == 0, f"{script_name}: stderr={proc.stderr!r} stdout={proc.stdout!r}"
