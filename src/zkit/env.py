"""Environment inspection helpers."""

from __future__ import annotations

import platform
import sys
from pathlib import Path


def check_env() -> dict[str, str]:
    """Return basic runtime information useful for debugging installations."""

    return {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
        "cwd": str(Path.cwd()),
    }
