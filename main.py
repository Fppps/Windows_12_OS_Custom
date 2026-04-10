from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from app.config import AppConfig
from app.native_bridge import init_native_layer
from app.recovery import install_exception_hooks
from app.shell import Windows12Shell


def main() -> int:
    install_exception_hooks()
    app = QApplication(sys.argv)
    app.setApplicationName('Windows 12 Preview')
    app.setOrganizationName('Preview Shell Lab')

    root = Path(__file__).resolve().parent
    native = init_native_layer(root)
    config = AppConfig(root / 'data')

    try:
        shell = Windows12Shell(config)
        shell.setProperty('native_version', native.version())
        shell.setProperty('native_loaded_from', native.loaded_from or '')
        shell.setProperty('native_blur_supported', native.desktop_blur_supported())
    except Exception as exc:  # pragma: no cover
        QMessageBox.critical(None, 'Windows 12 Preview', f'Failed to load the preview shell.\n\n{exc}')
        return 1

    shell.showFullScreen()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
