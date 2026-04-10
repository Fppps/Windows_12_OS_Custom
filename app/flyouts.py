from __future__ import annotations

from datetime import datetime
from urllib.parse import quote_plus

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from .services import NetworkService, RuntimeState, WeatherService
from .widgets import AcrylicPanel, IconCanvas, set_shadow


class ActionButton(QPushButton):
    def __init__(self, text: str, icon_kind: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self.setStyleSheet(
            """
            QPushButton {
                background: rgba(255,255,255,0.08);
                color: #f6fbff;
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 14px;
                padding: 8px 12px;
                text-align: left;
                font-weight: 600;
            }
            QPushButton:hover { background: rgba(255,255,255,0.13); }
            """
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        if icon_kind:
            layout.addWidget(IconCanvas(icon_kind, 18))
        label = QLabel(text)
        label.setStyleSheet('color: white; font-size: 13px; font-weight: 600;')
        layout.addWidget(label, 1)


class FlyoutPanel(AcrylicPanel):
    def __init__(self, radius: int = 24, parent: QWidget | None = None) -> None:
        super().__init__(radius, parent)
        self.apply_surface('rgba(10, 19, 42, 0.86)', 'rgba(255,255,255,0.16)')
        set_shadow(self, blur=34, y_offset=12, alpha=95)


class StartMenuPanel(FlyoutPanel):
    open_this_pc = Signal()
    open_settings = Signal()
    open_welcome = Signal()
    sign_out = Signal()

    def __init__(self, apps: list[dict], parent: QWidget | None = None) -> None:
        super().__init__(24, parent)
        self.resize(420, 332)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        title = QLabel('Start')
        title.setStyleSheet('font-size: 28px; font-weight: 700; color: white;')
        layout.addWidget(title)

        sub = QLabel('Minimal preview shell, with This PC as the main app surface.')
        sub.setStyleSheet('font-size: 13px; color: rgba(255,255,255,0.70);')
        sub.setWordWrap(True)
        layout.addWidget(sub)

        for app in apps:
            btn = ActionButton(app['name'], app.get('icon'))
            action = app.get('action')
            if action == 'explorer':
                btn.clicked.connect(self.open_this_pc)
            elif action == 'settings':
                btn.clicked.connect(self.open_settings)
            elif action == 'welcome':
                btn.clicked.connect(self.open_welcome)
            layout.addWidget(btn)

        btn_sign_out = ActionButton('Sign out', 'user')
        btn_sign_out.clicked.connect(self.sign_out)
        layout.addWidget(btn_sign_out)
        layout.addStretch(1)


class SearchPanel(FlyoutPanel):
    open_this_pc = Signal()
    open_settings = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(24, parent)
        self.resize(520, 260)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        title = QLabel('Search')
        title.setStyleSheet('font-size: 26px; font-weight: 700; color: white;')
        layout.addWidget(title)

        self.query = QLineEdit()
        self.query.setPlaceholderText('Search the web')
        self.query.setMinimumHeight(42)
        self.query.returnPressed.connect(self.search_web)
        self.query.setStyleSheet(
            'QLineEdit { background: rgba(255,255,255,0.10); color: white; border: 1px solid rgba(255,255,255,0.16); border-radius: 14px; padding: 0 14px; font-size: 14px; }'
        )
        layout.addWidget(self.query)

        btn_search = ActionButton('Open web results in your browser', 'search')
        btn_search.clicked.connect(self.search_web)
        btn_pc = ActionButton('Open This PC', 'pc')
        btn_pc.clicked.connect(self.open_this_pc)
        btn_settings = ActionButton('Open Settings', 'control')
        btn_settings.clicked.connect(self.open_settings)
        layout.addWidget(btn_search)
        layout.addWidget(btn_pc)
        layout.addWidget(btn_settings)
        layout.addStretch(1)

    def search_web(self) -> None:
        query = self.query.text().strip() or 'Windows 12 Preview'
        QDesktopServices.openUrl(QUrl(f'https://www.google.com/search?q={quote_plus(query)}'))


class WeatherPanel(FlyoutPanel):
    open_settings = Signal()

    def __init__(self, weather_data: dict, parent: QWidget | None = None) -> None:
        super().__init__(24, parent)
        self.resize(340, 320)
        self.weather_data = weather_data
        self.service = WeatherService(weather_data)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title = QLabel(f"{weather_data['temperature']}  {weather_data['condition']}")
        title.setStyleSheet('font-size: 28px; font-weight: 700; color: white;')
        layout.addWidget(title)

        subtitle = QLabel(f"{weather_data['location']}  High {weather_data['high']}  Low {weather_data['low']}")
        subtitle.setStyleSheet('font-size: 13px; color: rgba(255,255,255,0.74);')
        layout.addWidget(subtitle)

        buttons = [
            (f"Current conditions: {weather_data['condition']}", 'search', self.service.open_general),
            (f"Wind: {weather_data['wind']}", 'network', self.service.open_wind),
            (f"Humidity: {weather_data['humidity']}", 'display', self.service.open_humidity),
            (f"Forecast: {weather_data['forecast']}", 'search', self.service.open_forecast),
        ]
        for text, icon, handler in buttons:
            btn = ActionButton(text, icon)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        btn_settings = ActionButton('Open Settings', 'control')
        btn_settings.clicked.connect(self.open_settings)
        layout.addWidget(btn_settings)
        layout.addStretch(1)


class NetworkPanel(FlyoutPanel):
    open_settings = Signal()

    def __init__(self, system_data: dict, parent: QWidget | None = None) -> None:
        super().__init__(22, parent)
        self.resize(340, 276)
        network = system_data['network']
        self.service = NetworkService(network)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel(network['name'])
        title.setStyleSheet('font-size: 24px; font-weight: 700; color: white;')
        layout.addWidget(title)

        rows = [
            (network['status'], 'network', self.service.open_general),
            (f"Signal: {network['strength']}", 'network', self.service.open_signal),
            (f"Adapter: {network['adapter']}", 'network', self.service.open_adapter),
        ]
        for text, icon, handler in rows:
            btn = ActionButton(text, icon)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        btn_settings = ActionButton('Open Network & internet settings', 'network')
        btn_settings.clicked.connect(self.open_settings)
        layout.addWidget(btn_settings)
        layout.addStretch(1)


class SoundPanel(FlyoutPanel):
    open_settings = Signal()

    def __init__(self, system_data: dict, runtime_state: RuntimeState, parent: QWidget | None = None) -> None:
        super().__init__(22, parent)
        self.resize(320, 250)
        self.runtime_state = runtime_state
        self.volume = int(runtime_state.volume)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel(system_data['sound']['output'])
        title.setStyleSheet('font-size: 24px; font-weight: 700; color: white;')
        layout.addWidget(title)

        self.volume_label = QLabel('Volume: 0%')
        self.volume_label.setStyleSheet('font-size: 13px; color: rgba(255,255,255,0.80);')
        layout.addWidget(self.volume_label)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        btn_down = ActionButton('Volume down', 'volume')
        btn_down.clicked.connect(lambda: self.adjust(-5))
        btn_up = ActionButton('Volume up', 'volume')
        btn_up.clicked.connect(lambda: self.adjust(5))
        row_layout.addWidget(btn_down)
        row_layout.addWidget(btn_up)
        layout.addWidget(row)

        btn_settings = ActionButton('Open Sound settings', 'control')
        btn_settings.clicked.connect(self.open_settings)
        layout.addWidget(btn_settings)
        layout.addStretch(1)
        self._sync()

    def adjust(self, amount: int) -> None:
        self.volume = max(0, min(100, self.volume + amount))
        self.runtime_state.volume = self.volume
        self._sync()

    def _sync(self) -> None:
        self.volume_label.setText(f'Volume: {self.volume}%')


class DisplayPanel(FlyoutPanel):
    open_settings = Signal()

    def __init__(self, system_data: dict, runtime_state: RuntimeState, parent: QWidget | None = None) -> None:
        super().__init__(22, parent)
        self.resize(320, 260)
        self.runtime_state = runtime_state
        self.brightness = int(runtime_state.brightness)
        self.night_light = bool(runtime_state.night_light)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel('Display')
        title.setStyleSheet('font-size: 24px; font-weight: 700; color: white;')
        layout.addWidget(title)

        self.brightness_label = QLabel('Brightness: 0%')
        self.brightness_label.setStyleSheet('font-size: 13px; color: rgba(255,255,255,0.80);')
        layout.addWidget(self.brightness_label)

        self.night_label = QLabel('Night light: Off')
        self.night_label.setStyleSheet('font-size: 13px; color: rgba(255,255,255,0.80);')
        layout.addWidget(self.night_label)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        btn_down = ActionButton('Brightness down', 'display')
        btn_down.clicked.connect(lambda: self.adjust(-5))
        btn_up = ActionButton('Brightness up', 'display')
        btn_up.clicked.connect(lambda: self.adjust(5))
        row_layout.addWidget(btn_down)
        row_layout.addWidget(btn_up)
        layout.addWidget(row)

        btn_night = ActionButton('Toggle night light', 'display')
        btn_night.clicked.connect(self.toggle_night_light)
        btn_settings = ActionButton('Open Display settings', 'control')
        btn_settings.clicked.connect(self.open_settings)
        layout.addWidget(btn_night)
        layout.addWidget(btn_settings)
        layout.addStretch(1)
        self._sync()

    def adjust(self, amount: int) -> None:
        self.brightness = max(0, min(100, self.brightness + amount))
        self.runtime_state.brightness = self.brightness
        self._sync()

    def toggle_night_light(self) -> None:
        self.night_light = not self.night_light
        self.runtime_state.night_light = self.night_light
        self._sync()

    def _sync(self) -> None:
        self.brightness_label.setText(f'Brightness: {self.brightness}%')
        self.night_label.setText(f"Night light: {'On' if self.night_light else 'Off'}")


class CalendarPanel(FlyoutPanel):
    sign_out = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(22, parent)
        self.resize(300, 220)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel('Calendar')
        title.setStyleSheet('font-size: 24px; font-weight: 700; color: white;')
        layout.addWidget(title)

        self.time_label = QLabel('')
        self.time_label.setStyleSheet('font-size: 18px; font-weight: 600; color: white;')
        layout.addWidget(self.time_label)
        self.date_label = QLabel('')
        self.date_label.setStyleSheet('font-size: 13px; color: rgba(255,255,255,0.80);')
        layout.addWidget(self.date_label)

        btn_lock = ActionButton('Sign out to lock screen', 'user')
        btn_lock.clicked.connect(self.sign_out)
        layout.addWidget(btn_lock)
        layout.addStretch(1)
        self.refresh()

    def refresh(self) -> None:
        now = datetime.now()
        self.time_label.setText(now.strftime('%I:%M %p').lstrip('0'))
        self.date_label.setText(now.strftime('%A, %B ') + str(now.day) + now.strftime(', %Y'))


class AboutPanel(FlyoutPanel):
    open_settings = Signal()
    open_welcome = Signal()

    def __init__(self, system_data: dict, parent: QWidget | None = None) -> None:
        super().__init__(22, parent)
        self.resize(360, 248)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel(system_data['preview_name'])
        title.setStyleSheet('font-size: 24px; font-weight: 700; color: white;')
        layout.addWidget(title)

        for line in [
            system_data['copy_line'],
            f"Build {system_data['build_number']}",
            f"Update label {system_data['update_label']}",
        ]:
            row = QLabel(line)
            row.setStyleSheet('font-size: 13px; color: rgba(255,255,255,0.80);')
            layout.addWidget(row)

        btn_welcome = ActionButton('Open welcome screen', 'update')
        btn_welcome.clicked.connect(self.open_welcome)
        btn_settings = ActionButton('Open Settings', 'control')
        btn_settings.clicked.connect(self.open_settings)
        layout.addWidget(btn_welcome)
        layout.addWidget(btn_settings)
        layout.addStretch(1)
