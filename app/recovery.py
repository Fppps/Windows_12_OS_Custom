from __future__ import annotations

import os
import sys
import tempfile
import traceback
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


def crash_log_path() -> Path:
    return Path(tempfile.gettempdir()) / 'windows12_preview_crash.log'


def _write_crash_log(exc_type, exc_value, exc_tb) -> None:
    text = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    crash_log_path().write_text(text, encoding='utf-8')


def install_exception_hooks() -> None:
    def handler(exc_type, exc_value, exc_tb):
        _write_crash_log(exc_type, exc_value, exc_tb)
        os._exit(42)

    sys.excepthook = handler
    try:
        import threading
    except Exception:
        return

    def thread_handler(args):
        _write_crash_log(args.exc_type, args.exc_value, args.exc_traceback)
        os._exit(42)

    threading.excepthook = thread_handler


class RestartNotice(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet('background: #080f1f;')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(14)
        title = QLabel('Windows 12 Preview needs to restart')
        title.setStyleSheet('color: white; font-size: 28px; font-weight: 700;')
        body = QLabel('A preview shell function hit an unexpected error. The app is restarting automatically.')
        body.setWordWrap(True)
        body.setStyleSheet('color: rgba(255,255,255,0.82); font-size: 15px;')
        layout.addStretch(1)
        layout.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(body, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)


def show_restart_notice() -> None:
    app = QApplication.instance() or QApplication([])
    notice = RestartNotice()
    notice.showFullScreen()
    QTimer.singleShot(1600, app.quit)
    app.exec()
