from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .widgets import AcrylicPanel, set_shadow


class LoginScreen(QWidget):
    login_success = Signal(str)

    def __init__(self, wallpapers_dir: Path, user_data: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        wallpaper_path = wallpapers_dir / user_data.get('login_wallpaper', 'violet.png')
        fallback = wallpapers_dir / 'aurora.png'
        self._wallpaper = QPixmap(str(wallpaper_path if wallpaper_path.exists() else fallback))
        self._user_data = user_data
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top = QWidget()
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(0, 40, 50, 0)
        top_layout.addStretch(1)

        clock_box = QVBoxLayout()
        clock_box.setSpacing(2)
        self.time_label = QLabel('7:17')
        self.time_label.setStyleSheet('color: white; font-size: 66px; font-weight: 600;')
        self.date_label = QLabel('Wednesday, April 8')
        self.date_label.setStyleSheet('color: rgba(255,255,255,0.85); font-size: 18px;')
        clock_box.addWidget(self.time_label, 0, Qt.AlignmentFlag.AlignRight)
        clock_box.addWidget(self.date_label, 0, Qt.AlignmentFlag.AlignRight)
        top_layout.addLayout(clock_box)
        root.addWidget(top, 1)

        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 92)
        bottom_layout.addStretch(1)

        self.panel = AcrylicPanel(30)
        self.panel.apply_surface('rgba(8, 17, 38, 0.78)', 'rgba(255,255,255,0.16)')
        set_shadow(self.panel, blur=42, y_offset=18, alpha=110)
        self.panel.setFixedSize(430, 388)

        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(32, 26, 32, 26)
        panel_layout.setSpacing(16)

        welcome = QLabel('Welcome')
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setStyleSheet('color: rgba(255,255,255,0.70); font-size: 14px; font-weight: 700; letter-spacing: 0.3px;')
        panel_layout.addWidget(welcome)

        avatar = QFrame()
        avatar.setFixedSize(74, 74)
        avatar.setStyleSheet('background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.22); border-radius: 37px;')
        avatar_layout = QVBoxLayout(avatar)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_label = QLabel(user_data.get('initials', 'W1'))
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet('color: white; font-size: 22px; font-weight: 700;')
        avatar_layout.addWidget(avatar_label)
        panel_layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignHCenter)

        title = QLabel(user_data.get('name', 'Preview User'))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('color: white; font-size: 28px; font-weight: 650;')
        panel_layout.addWidget(title)

        sub = QLabel('Sign in to Windows 12 Preview')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet('color: rgba(255,255,255,0.76); font-size: 14px;')
        panel_layout.addWidget(sub)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText('Password')
        self.password.setMinimumHeight(44)
        self.password.setStyleSheet(
            'QLineEdit { background: rgba(255,255,255,0.10); color: white; border: 1px solid rgba(255,255,255,0.16); border-radius: 14px; padding: 0 14px; font-size: 14px; }'
        )
        self.password.returnPressed.connect(self._attempt_login)
        panel_layout.addWidget(self.password)

        hint = QLabel(f"Demo password: {user_data.get('password', 'preview')}")
        hint.setStyleSheet('color: rgba(255,255,255,0.60); font-size: 12px;')
        panel_layout.addWidget(hint)

        self.status = QLabel('')
        self.status.setStyleSheet('color: #ffd3d3; font-size: 12px;')
        panel_layout.addWidget(self.status)

        button = QPushButton('Sign in')
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(46)
        button.clicked.connect(self._attempt_login)
        button.setStyleSheet(
            'QPushButton { background: rgba(255,255,255,0.92); color: #10234b; border: none; border-radius: 14px; font-size: 15px; font-weight: 700; } QPushButton:hover { background: white; }'
        )
        panel_layout.addWidget(button)
        panel_layout.addStretch(1)

        bottom_layout.addWidget(self.panel)
        bottom_layout.addStretch(1)
        root.addWidget(bottom, 0)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.fade = QPropertyAnimation(self.opacity_effect, b'opacity', self)
        self.fade.setDuration(550)
        self.fade.setStartValue(1.0)
        self.fade.setEndValue(0.0)
        self.fade.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.fade.finished.connect(self._emit_success)
        self._pending_user = user_data.get('name', 'Preview User')

    def reset(self) -> None:
        self.password.clear()
        self.status.clear()
        self.opacity_effect.setOpacity(1.0)
        self.show()
        self.raise_()

    def _attempt_login(self) -> None:
        if self.password.text().strip() == self._user_data.get('password', 'preview'):
            self.status.setText('')
            self._pending_user = self._user_data.get('name', 'Preview User')
            self.fade.start()
        else:
            self.status.setText('Password is incorrect. Try the demo password shown above.')

    def _emit_success(self) -> None:
        self.login_success.emit(self._pending_user)

    def paintEvent(self, event) -> None:  # pragma: no cover
        painter = QPainter(self)
        if not self._wallpaper.isNull():
            scaled = self._wallpaper.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 38))
