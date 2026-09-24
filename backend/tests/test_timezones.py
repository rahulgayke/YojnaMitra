"""Cross-platform timezone regression tests for registry review dates."""

from __future__ import annotations

import os
import subprocess
import sys


def test_india_timezone_loads_without_system_timezone_database() -> None:
    """Load Asia/Kolkata from packaged tzdata, even without an OS timezone database."""

    # Disable the OS timezone path to reproduce the Windows/minimal-container case.
    env = os.environ.copy()
    env["PYTHONTZPATH"] = ""
    result = subprocess.run(
        [sys.executable, "-c", "from zoneinfo import ZoneInfo; print(ZoneInfo('Asia/Kolkata'))"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Asia/Kolkata"
