from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run_child() -> int:
    from main import main
    return main()


def run_supervisor() -> int:
    restart_count = 0
    max_restarts = 3
    while True:
        code = subprocess.call([sys.executable, str(ROOT / 'run_preview.py'), '--child'])
        if code != 42:
            return code
        restart_count += 1
        if restart_count > max_restarts:
            return code
        try:
            from app.recovery import show_restart_notice
            show_restart_notice()
        except Exception:
            pass


if __name__ == '__main__':
    if '--child' in sys.argv:
        raise SystemExit(run_child())
    raise SystemExit(run_supervisor())
