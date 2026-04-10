from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton

from .widgets import IconCanvas


class TitleBar(QFrame):
    def __init__(self, title: str, icon_kind: str, window: QMainWindow) -> None:
        super().__init__(window)
        self._window = window
        self._drag_pos: QPoint | None = None
        self.setFixedHeight(44)
        self.setStyleSheet('background: rgba(255,255,255,0.04); border-top-left-radius: 18px; border-top-right-radius: 18px;')
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 10, 0)
        layout.setSpacing(8)
        layout.addWidget(IconCanvas(icon_kind, 18))
        title_label = QLabel(title)
        title_label.setStyleSheet('color: white; font-size: 13px; font-weight: 600;')
        layout.addWidget(title_label)
        layout.addStretch(1)
        for label, action in [('_', self._window.showMinimized), ('□', self._toggle), ('✕', self._window.close)]:
            btn = QPushButton(label)
            btn.setFixedSize(34, 26)
            btn.clicked.connect(action)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                'QPushButton { background: transparent; color: white; border: none; border-radius: 8px; font-size: 13px; } '
                'QPushButton:hover { background: rgba(255,255,255,0.10); }'
            )
            layout.addWidget(btn)

    def _toggle(self) -> None:
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton and not self._window.isMaximized():
            self._window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None
        event.accept()
