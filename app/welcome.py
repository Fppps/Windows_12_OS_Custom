from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .flyouts import ActionButton, FlyoutPanel


class WelcomeScreen(FlyoutPanel):
    continue_to_desktop = Signal()
    open_this_pc = Signal()
    open_settings = Signal()

    def __init__(self, welcome_data: dict, parent: QWidget | None = None) -> None:
        super().__init__(30, parent)
        self.welcome_data = welcome_data
        self.resize(760, 460)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        badge = QLabel(welcome_data.get('badge', 'Windows 12 Preview'))
        badge.setStyleSheet('color: rgba(255,255,255,0.78); font-size: 13px; font-weight: 700; letter-spacing: 0.4px;')
        layout.addWidget(badge)

        title = QLabel(welcome_data.get('title', 'Welcome'))
        title.setWordWrap(True)
        title.setStyleSheet('color: white; font-size: 34px; font-weight: 700;')
        layout.addWidget(title)

        for text in welcome_data.get('paragraphs', []):
            label = QLabel(text)
            label.setWordWrap(True)
            label.setStyleSheet('color: rgba(255,255,255,0.86); font-size: 15px;')
            layout.addWidget(label)

        note = QLabel(welcome_data.get('footnote', ''))
        note.setWordWrap(True)
        note.setStyleSheet('color: rgba(255,255,255,0.62); font-size: 12px;')
        layout.addWidget(note)

        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 8, 0, 0)
        actions_layout.setSpacing(10)
        btn_continue = ActionButton('Continue to desktop', 'windows')
        btn_continue.clicked.connect(self._animate_out)
        btn_pc = ActionButton('Open This PC', 'pc')
        btn_pc.clicked.connect(self.open_this_pc)
        btn_settings = ActionButton('Open Settings', 'control')
        btn_settings.clicked.connect(self.open_settings)
        actions_layout.addWidget(btn_continue)
        actions_layout.addWidget(btn_pc)
        actions_layout.addWidget(btn_settings)
        layout.addWidget(actions)
        layout.addStretch(1)

        self._anim = QPropertyAnimation(self, b'windowOpacity', self)
        self._anim.setDuration(260)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.finished.connect(self._finish_hide)
        self._hide_after = False

    def popup_centered(self) -> None:
        parent = self.parentWidget()
        if parent is not None:
            self.move(max((parent.width() - self.width()) // 2, 0), max((parent.height() - self.height()) // 2, 0))
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self._hide_after = False
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def _animate_out(self) -> None:
        self._hide_after = True
        self._anim.stop()
        self._anim.setStartValue(self.windowOpacity())
        self._anim.setEndValue(0.0)
        self._anim.start()

    def _finish_hide(self) -> None:
        if self._hide_after:
            self.hide()
            self.continue_to_desktop.emit()
