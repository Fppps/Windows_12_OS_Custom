from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from .config import AppConfig
from .context_menu import DesktopContextMenu
from .flyouts import AboutPanel, CalendarPanel, DisplayPanel, NetworkPanel, SearchPanel, SoundPanel, StartMenuPanel, WeatherPanel
from .login import LoginScreen
from .services import RuntimeState
from .settings import SettingsWindow
from .this_pc import ThisPCWindow
from .welcome import WelcomeScreen
from .widgets import (
    AcrylicPanel,
    DesktopShortcut,
    SearchPill,
    SlideAnimator,
    TaskbarIconButton,
    WallpaperWidget,
    WeatherWidget,
    set_shadow,
)


class Windows12Shell(QMainWindow):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config
        self.theme = self.config.load('theme.json')
        self.apps_data = self.config.load('apps.json')
        self.files_data = self.config.load('files.json')['files']
        self.wallpapers_data = self.config.load('wallpapers.json')
        self.system_data = self.config.load('system.json')
        self.weather_data = self.config.load('weather.json')
        self.settings_data = self.config.load('settings.json')
        self.welcome_data = self.config.load('welcome.json')
        self.context_menu_data = self.config.load('context_menu.json')
        self.wallpapers_dir = Path(__file__).resolve().parent.parent / 'assets' / 'wallpapers'
        self.current_wallpaper = self.wallpapers_data.get('default', 'aurora.png')
        self.current_user = self.system_data['user']['name']
        self.runtime_state = RuntimeState(self.system_data)

        self.this_pc_window: ThisPCWindow | None = None
        self.settings_window: SettingsWindow | None = None
        self.start_visible = False

        self.start_panel: StartMenuPanel | None = None
        self.search_panel: SearchPanel | None = None
        self.weather_panel: WeatherPanel | None = None
        self.network_panel: NetworkPanel | None = None
        self.sound_panel: SoundPanel | None = None
        self.display_panel: DisplayPanel | None = None
        self.calendar_panel: CalendarPanel | None = None
        self.about_panel: AboutPanel | None = None
        self.context_menu: DesktopContextMenu | None = None
        self.welcome_screen: WelcomeScreen | None = None
        self.start_animator: SlideAnimator | None = None

        self.start_button: TaskbarIconButton | None = None
        self.top_search: SearchPill | None = None
        self.clock_label: QLabel | None = None
        self.date_label: QLabel | None = None
        self.clock_button: QPushButton | None = None
        self.watermark_button: QPushButton | None = None
        self.desktop_frame: QWidget | None = None
        self.taskbar_wrap: QWidget | None = None

        self.setWindowTitle(self.system_data['preview_name'])
        self.resize(1600, 900)
        self.setMinimumSize(1280, 760)
        self.setStyleSheet('QMainWindow { background: #070b16; }')

        self._build_shell()
        self._wire_clock()
        self._position_overlays(initial=True)
        self._set_shell_visible(False)

    def _build_shell(self) -> None:
        container = QWidget()
        self.setCentralWidget(container)
        self.stack = QStackedLayout(container)
        self.stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self.wallpaper_widget = WallpaperWidget()
        self.stack.addWidget(self.wallpaper_widget)

        self.desktop_root = QWidget()
        self.desktop_root.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.desktop_root.customContextMenuRequested.connect(self._show_desktop_context_menu)
        self.stack.addWidget(self.desktop_root)
        self.stack.setCurrentWidget(self.desktop_root)

        self.base_layout = QVBoxLayout(self.desktop_root)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.setSpacing(0)

        self.desktop_frame = QWidget()
        desktop_layout = QVBoxLayout(self.desktop_frame)
        desktop_layout.setContentsMargins(10, 10, 10, 0)
        desktop_layout.setSpacing(0)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(0)
        self.desktop_column = self._build_desktop_column()
        top_row.addWidget(self.desktop_column, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        top_row.addStretch(1)
        desktop_layout.addLayout(top_row)
        desktop_layout.addStretch(1)

        self.watermark_button = self._build_watermark_button()
        desktop_layout.addWidget(self.watermark_button, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.base_layout.addWidget(self.desktop_frame, 1)

        self.taskbar_wrap = QWidget()
        taskbar_wrap_layout = QVBoxLayout(self.taskbar_wrap)
        taskbar_wrap_layout.setContentsMargins(0, 0, 0, 0)
        self.taskbar = self._build_taskbar()
        taskbar_wrap_layout.addWidget(self.taskbar)
        self.base_layout.addWidget(self.taskbar_wrap, 0)

        self.top_search = SearchPill('Search the web', compact=False)
        self.top_search.setParent(self.desktop_root)
        self.top_search.resize(412, 68)
        self.top_search.clicked.connect(self.toggle_search_panel)
        self.top_search.show()
        set_shadow(self.top_search, blur=34, y_offset=10, alpha=70)

        self.start_panel = StartMenuPanel(self.apps_data.get('start', []), self.desktop_root)
        self.start_panel.open_this_pc.connect(self.open_this_pc)
        self.start_panel.open_settings.connect(self.open_settings)
        self.start_panel.open_welcome.connect(self.show_welcome_screen)
        self.start_panel.sign_out.connect(self.show_login_screen)
        self.start_panel.hide()
        self.start_animator = SlideAnimator(self.start_panel)

        self.search_panel = SearchPanel(self.desktop_root)
        self.search_panel.open_this_pc.connect(self.open_this_pc)
        self.search_panel.open_settings.connect(self.open_settings)
        self.search_panel.hide()

        self.weather_panel = WeatherPanel(self.weather_data, self.desktop_root)
        self.weather_panel.open_settings.connect(self.open_settings)
        self.weather_panel.hide()

        self.network_panel = NetworkPanel(self.system_data, self.desktop_root)
        self.network_panel.open_settings.connect(self.open_settings)
        self.network_panel.hide()

        self.sound_panel = SoundPanel(self.system_data, self.runtime_state, self.desktop_root)
        self.sound_panel.open_settings.connect(self.open_settings)
        self.sound_panel.hide()

        self.display_panel = DisplayPanel(self.system_data, self.runtime_state, self.desktop_root)
        self.display_panel.open_settings.connect(self.open_settings)
        self.display_panel.hide()

        self.calendar_panel = CalendarPanel(self.desktop_root)
        self.calendar_panel.sign_out.connect(self.show_login_screen)
        self.calendar_panel.hide()

        self.about_panel = AboutPanel(self.system_data, self.desktop_root)
        self.about_panel.open_settings.connect(self.open_settings)
        self.about_panel.open_welcome.connect(self.show_welcome_screen)
        self.about_panel.hide()

        self.context_menu = DesktopContextMenu(self.desktop_root)
        self.context_menu.open_this_pc.connect(self.open_this_pc)
        self.context_menu.open_settings.connect(self.open_settings)
        self.context_menu.open_welcome.connect(self.show_welcome_screen)
        self.context_menu.refresh_desktop.connect(self.refresh_desktop)
        self.context_menu.cycle_wallpaper.connect(self.cycle_wallpaper)
        self.context_menu.hide()

        self.welcome_screen = WelcomeScreen(self.welcome_data, self.desktop_root)
        self.welcome_screen.continue_to_desktop.connect(self._continue_after_welcome)
        self.welcome_screen.open_this_pc.connect(self.open_this_pc)
        self.welcome_screen.open_settings.connect(self.open_settings)
        self.welcome_screen.hide()

        self.login_screen = LoginScreen(self.wallpapers_dir, self.system_data['user'], self.desktop_root)
        self.login_screen.login_success.connect(self._complete_login)
        self.login_screen.raise_()

        self._apply_wallpaper(self.current_wallpaper)

    def _build_desktop_column(self) -> QWidget:
        holder = QWidget()
        layout = QVBoxLayout(holder)
        layout.setContentsMargins(6, 4, 0, 0)
        layout.setSpacing(12)

        for app in self.apps_data.get('desktop', []):
            shortcut = DesktopShortcut(app.get('icon', 'pc'), app['name'])
            action = app.get('action')
            if action == 'explorer':
                shortcut.clicked.connect(self.open_this_pc)
            elif action == 'settings':
                shortcut.clicked.connect(self.open_settings)
            layout.addWidget(shortcut)
        layout.addStretch(1)
        return holder

    def _build_watermark_button(self) -> QPushButton:
        button = QPushButton()
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet('QPushButton { background: transparent; border: none; } QPushButton:hover { background: rgba(255,255,255,0.05); border-radius: 10px; }')
        button.clicked.connect(self.toggle_about_panel)

        layout = QVBoxLayout(button)
        layout.setContentsMargins(10, 6, 10, 8)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        watermark_one = QLabel(self.system_data['preview_name'])
        watermark_one.setStyleSheet('color: rgba(255,255,255,0.92); font-size: 18px; font-weight: 500;')
        watermark_two = QLabel(f"{self.system_data['copy_line']} Build {self.system_data['build_number']}   Update label {self.system_data['update_label']}")
        watermark_two.setStyleSheet('color: rgba(255,255,255,0.88); font-size: 15px; font-weight: 400;')
        layout.addWidget(watermark_one, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(watermark_two, 0, Qt.AlignmentFlag.AlignRight)
        return button

    def _build_taskbar(self) -> QWidget:
        bar = AcrylicPanel(0)
        bar.apply_surface(self.theme['taskbar'], self.theme['taskbar_border'])
        bar.setFixedHeight(74)
        bar.setStyleSheet(
            f"QFrame#AcrylicPanel {{ background: {self.theme['taskbar']}; border-top: 1px solid {self.theme['taskbar_border']}; border-left: none; border-right: none; border-bottom: none; border-radius: 0px; }}"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        weather = WeatherWidget(self.weather_data['temperature'], self.weather_data['condition'])
        weather.setFixedWidth(170)
        weather.clicked.connect(self.toggle_weather_panel)
        layout.addWidget(weather, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        center = QWidget()
        center_layout = QHBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)

        self.start_button = TaskbarIconButton('windows', active=False)
        self.start_button.clicked.connect(self.toggle_start)
        center_layout.addWidget(self.start_button)

        taskbar_search = SearchPill('Search', compact=True)
        taskbar_search.setFixedWidth(248)
        taskbar_search.clicked.connect(self.toggle_search_panel)
        center_layout.addWidget(taskbar_search)

        this_pc_button = TaskbarIconButton('pc', active=False)
        this_pc_button.clicked.connect(self.open_this_pc)
        center_layout.addWidget(this_pc_button)

        layout.addWidget(center, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        right = QWidget()
        right_layout = QHBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        chevron_button = TaskbarIconButton('chevron', active=False)
        chevron_button.clicked.connect(self.toggle_about_panel)
        network_button = TaskbarIconButton('network', active=False)
        network_button.clicked.connect(self.toggle_network_panel)
        volume_button = TaskbarIconButton('volume', active=False)
        volume_button.clicked.connect(self.toggle_sound_panel)
        display_button = TaskbarIconButton('display', active=False)
        display_button.clicked.connect(self.toggle_display_panel)
        for button in [chevron_button, network_button, volume_button, display_button]:
            right_layout.addWidget(button)

        self.clock_button = QPushButton()
        self.clock_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clock_button.setStyleSheet('QPushButton { background: transparent; border: none; border-radius: 10px; } QPushButton:hover { background: rgba(255,255,255,0.34); }')
        self.clock_button.clicked.connect(self.toggle_calendar_panel)
        time_layout = QVBoxLayout(self.clock_button)
        time_layout.setContentsMargins(8, 0, 0, 0)
        time_layout.setSpacing(0)
        self.clock_label = QLabel('--:--')
        self.clock_label.setStyleSheet('color: #283345; font-size: 14px; font-weight: 600;')
        self.date_label = QLabel('--/--/----')
        self.date_label.setStyleSheet('color: #364154; font-size: 14px; font-weight: 500;')
        time_layout.addWidget(self.clock_label, 0, Qt.AlignmentFlag.AlignRight)
        time_layout.addWidget(self.date_label, 0, Qt.AlignmentFlag.AlignRight)
        right_layout.addWidget(self.clock_button)

        layout.addWidget(right, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return bar

    def _wire_clock(self) -> None:
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

    def _update_clock(self) -> None:
        now = datetime.now()
        if self.clock_label:
            self.clock_label.setText(now.strftime('%I:%M %p').lstrip('0'))
        if self.date_label:
            self.date_label.setText(f'{now.month}/{now.day}/{now.year}')
        if self.login_screen:
            self.login_screen.time_label.setText(now.strftime('%I:%M').lstrip('0'))
            self.login_screen.date_label.setText(now.strftime('%A, %B ') + str(now.day))
        if self.calendar_panel:
            self.calendar_panel.refresh()

    def _complete_login(self, user_name: str) -> None:
        self.current_user = user_name
        self.login_screen.hide()
        self._set_shell_visible(True)
        self._hide_all_panels()
        self.show_welcome_screen()

    def _continue_after_welcome(self) -> None:
        pass

    def show_welcome_screen(self) -> None:
        if self.login_screen.isVisible():
            return
        self._hide_all_panels()
        if self.welcome_screen:
            self.welcome_screen.popup_centered()

    def show_login_screen(self) -> None:
        self._hide_all_panels()
        if self.this_pc_window is not None:
            self.this_pc_window.hide()
        if self.settings_window is not None:
            self.settings_window.hide()
        if self.welcome_screen is not None:
            self.welcome_screen.hide()
        self._set_shell_visible(False)
        self.login_screen.reset()
        self.login_screen.setGeometry(0, 0, self.desktop_root.width() or self.width(), self.desktop_root.height() or self.height())
        self.login_screen.raise_()

    def _set_shell_visible(self, visible: bool) -> None:
        if self.desktop_frame:
            self.desktop_frame.setVisible(visible)
        if self.taskbar_wrap:
            self.taskbar_wrap.setVisible(visible)
        if self.top_search:
            self.top_search.setVisible(visible)
        if not visible:
            self._hide_all_panels()

    def _apply_wallpaper(self, filename: str) -> None:
        from PySide6.QtGui import QPixmap

        self.current_wallpaper = filename
        image_path = self.wallpapers_dir / filename
        self.wallpaper_widget._image_path = str(image_path)
        self.wallpaper_widget.update()
        if self.login_screen and image_path.exists():
            self.login_screen._wallpaper = QPixmap(str(image_path))
            self.login_screen.update()

    def cycle_wallpaper(self) -> None:
        available = [item['file'] for item in self.wallpapers_data.get('available', [])]
        if not available:
            return
        try:
            idx = available.index(self.current_wallpaper)
        except ValueError:
            idx = -1
        self._apply_wallpaper(available[(idx + 1) % len(available)])

    def refresh_desktop(self) -> None:
        self.wallpaper_widget.update()
        self._position_overlays(initial=False)

    def _all_panels(self) -> dict[str, QWidget]:
        return {
            'start': self.start_panel,
            'search': self.search_panel,
            'weather': self.weather_panel,
            'network': self.network_panel,
            'sound': self.sound_panel,
            'display': self.display_panel,
            'calendar': self.calendar_panel,
            'about': self.about_panel,
            'context': self.context_menu,
        }

    def _hide_all_panels(self, except_name: str | None = None) -> None:
        for name, panel in self._all_panels().items():
            if panel is None or name == except_name:
                continue
            panel.hide()
        if except_name != 'start':
            self.start_visible = False
            if self.start_button:
                self.start_button.set_active(False)

    def _show_desktop_context_menu(self, point: QPoint) -> None:
        if self.login_screen.isVisible() or not self.context_menu:
            return
        self._hide_all_panels(except_name='context')
        self.context_menu.popup_at(point)

    def _position_overlays(self, initial: bool = False) -> None:
        width = self.desktop_root.width() or self.width()
        height = self.desktop_root.height() or self.height()
        taskbar_height = self.taskbar.height() or 74

        if self.top_search:
            self.top_search.move(max((width - self.top_search.width()) // 2, 0), 18)

        if self.search_panel:
            self.search_panel.move(max((width - self.search_panel.width()) // 2, 0), 96)
        if self.weather_panel:
            self.weather_panel.move(14, height - taskbar_height - self.weather_panel.height() - 14)

        right_stack_y = height - taskbar_height - 14
        for panel in [self.network_panel, self.sound_panel, self.display_panel, self.calendar_panel, self.about_panel]:
            if panel:
                panel.move(width - panel.width() - 18, right_stack_y - panel.height())

        if self.start_panel and self.start_animator:
            if self.start_button:
                start_origin = self.start_button.mapTo(self.desktop_root, QPoint(0, 0))
                start_x = start_origin.x() + (self.start_button.width() // 2) - (self.start_panel.width() // 2)
            else:
                start_x = (width - self.start_panel.width()) // 2
            start_x = max(14, min(start_x, width - self.start_panel.width() - 14))
            start_shown = QPoint(start_x, height - taskbar_height - self.start_panel.height() - 12)
            start_hidden = QPoint(start_x, height + 24)
            self.start_animator.configure(start_shown, start_hidden)
            if initial or not self.start_visible:
                self.start_panel.move(start_hidden)
            else:
                self.start_panel.move(start_shown)

        if self.context_menu and self.context_menu.isVisible():
            self.context_menu.move(min(self.context_menu.x(), width - self.context_menu.width() - 12), min(self.context_menu.y(), height - taskbar_height - self.context_menu.height() - 12))
        if self.welcome_screen and self.welcome_screen.isVisible():
            self.welcome_screen.move(max((width - self.welcome_screen.width()) // 2, 0), max((height - self.welcome_screen.height()) // 2, 0))

        self.login_screen.setGeometry(0, 0, width, height)
        if self.login_screen.isVisible():
            self.login_screen.raise_()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_overlays(initial=False)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
            return
        if event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showNormal()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        point = event.position().toPoint()
        open_panel_hit = False
        for panel in self._all_panels().values():
            if panel and panel.isVisible() and panel.geometry().contains(point):
                open_panel_hit = True
                break
        if self.welcome_screen and self.welcome_screen.isVisible() and self.welcome_screen.geometry().contains(point):
            open_panel_hit = True
        if not open_panel_hit:
            had_start = self.start_visible
            self._hide_all_panels()
            if had_start and self.start_panel and self.start_animator:
                self.start_animator.slide_up_or_down(False)
        super().mousePressEvent(event)

    def _toggle_panel(self, name: str) -> None:
        if self.login_screen.isVisible() or (self.welcome_screen and self.welcome_screen.isVisible()):
            return
        panel = self._all_panels()[name]
        if panel is None:
            return
        should_show = not panel.isVisible()
        had_start = self.start_visible
        self._hide_all_panels(except_name=name)
        if name == 'start':
            self.start_visible = should_show
            if self.start_button:
                self.start_button.set_active(should_show)
            if self.start_animator:
                self.start_animator.slide_up_or_down(should_show)
            return
        if had_start and self.start_panel and self.start_animator:
            self.start_visible = False
            if self.start_button:
                self.start_button.set_active(False)
            self.start_animator.slide_up_or_down(False)
        if should_show:
            panel.show()
            panel.raise_()
            if name == 'search':
                self.search_panel.query.setFocus()
        else:
            panel.hide()

    def toggle_start(self, force_hide: bool = False) -> None:
        if force_hide:
            if self.start_animator:
                self.start_visible = False
                if self.start_button:
                    self.start_button.set_active(False)
                self.start_animator.slide_up_or_down(False)
            return
        self._toggle_panel('start')

    def toggle_search_panel(self) -> None:
        self._toggle_panel('search')

    def toggle_weather_panel(self) -> None:
        self._toggle_panel('weather')

    def toggle_network_panel(self) -> None:
        self._toggle_panel('network')

    def toggle_sound_panel(self) -> None:
        self._toggle_panel('sound')

    def toggle_display_panel(self) -> None:
        self._toggle_panel('display')

    def toggle_calendar_panel(self) -> None:
        self._toggle_panel('calendar')

    def toggle_about_panel(self) -> None:
        self._toggle_panel('about')

    def open_this_pc(self) -> None:
        if self.login_screen.isVisible():
            return
        had_start = self.start_visible
        self._hide_all_panels()
        if self.welcome_screen and self.welcome_screen.isVisible():
            self.welcome_screen.hide()
        if had_start and self.start_panel and self.start_animator:
            self.start_animator.slide_up_or_down(False)
        if self.this_pc_window is None:
            self.this_pc_window = ThisPCWindow(self.theme, self.files_data, self)
        self.this_pc_window.show()
        self.this_pc_window.raise_()
        self.this_pc_window.activateWindow()

    def open_settings(self) -> None:
        if self.login_screen.isVisible():
            return
        had_start = self.start_visible
        self._hide_all_panels()
        if self.welcome_screen and self.welcome_screen.isVisible():
            self.welcome_screen.hide()
        if had_start and self.start_panel and self.start_animator:
            self.start_animator.slide_up_or_down(False)
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self.theme, self.settings_data, self._apply_wallpaper, self.show_login_screen, self)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
