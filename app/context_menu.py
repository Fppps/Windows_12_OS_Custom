from __future__ import annotations

from PySide6.QtCore import QPoint, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from .flyouts import ActionButton, FlyoutPanel


class DesktopContextMenu(FlyoutPanel):
    open_this_pc = Signal()
    open_settings = Signal()
    open_welcome = Signal()
    refresh_desktop = Signal()
    cycle_wallpaper = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(18, parent)
        self.setFixedWidth(240)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        entries = [
            ('Open This PC', 'pc', self.open_this_pc),
            ('Open Settings', 'control', self.open_settings),
            ('Refresh desktop', 'sync', self.refresh_desktop),
            ('Cycle wallpaper', 'image', self.cycle_wallpaper),
            ('Welcome screen', 'update', self.open_welcome),
        ]
        for text, icon, signal in entries:
            button = ActionButton(text, icon)
            button.clicked.connect(signal)
            button.clicked.connect(self.hide)
            layout.addWidget(button)

    def popup_at(self, point: QPoint) -> None:
        parent = self.parentWidget()
        if parent is None:
            self.move(point)
        else:
            x = max(10, min(point.x(), parent.width() - self.width() - 10))
            y = max(10, min(point.y(), parent.height() - self.height() - 10))
            self.move(x, y)
        self.show()
        self.raise_()
