from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMainWindow, QVBoxLayout, QWidget

from .flyouts import ActionButton
from .widgets import AcrylicPanel, InfoCard, SectionTitle, ToggleButton, set_shadow
from .window_frame import TitleBar


class SettingsWindow(QMainWindow):
    def __init__(self, theme: dict, settings_data: dict, on_wallpaper, on_sign_out, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._settings_data = settings_data
        self._on_wallpaper = on_wallpaper
        self._on_sign_out = on_sign_out
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(1220, 780)
        self.setStyleSheet('QMainWindow { background: transparent; } QLabel { color: white; }')

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        shell = AcrylicPanel(20)
        shell.apply_surface(theme['surface'], theme['surface_border'])
        set_shadow(shell, blur=42, y_offset=14, alpha=110)
        root_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        shell_layout.addWidget(TitleBar('Settings', 'control', self))

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(18, 16, 18, 18)
        body_layout.setSpacing(16)
        shell_layout.addWidget(body, 1)

        self.nav = QListWidget()
        self.nav.setFixedWidth(250)
        self.nav.setStyleSheet(
            'QListWidget { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.10); border-radius: 16px; color: white; padding: 8px; } '
            'QListWidget::item { padding: 9px 8px; border-radius: 10px; } '
            'QListWidget::item:selected { background: rgba(255,255,255,0.10); }'
        )
        for item in settings_data['categories']:
            QListWidgetItem(item['name'], self.nav)
        self.nav.currentRowChanged.connect(self._update_page)
        body_layout.addWidget(self.nav)

        self.page = QWidget()
        self.page_layout = QVBoxLayout(self.page)
        self.page_layout.setSpacing(14)
        body_layout.addWidget(self.page, 1)

        self.page_title = QLabel('Settings')
        self.page_title.setStyleSheet('font-size: 32px; font-weight: 700;')
        self.page_layout.addWidget(self.page_title)

        self.page_description = QLabel('')
        self.page_description.setWordWrap(True)
        self.page_description.setStyleSheet('font-size: 13px; color: rgba(255,255,255,0.74);')
        self.page_layout.addWidget(self.page_description)

        home_panel = AcrylicPanel(18)
        home_panel.apply_surface(theme['surface_soft'], theme['surface_border'])
        home_layout = QVBoxLayout(home_panel)
        home_layout.setContentsMargins(16, 16, 16, 16)
        home_layout.setSpacing(12)
        home_layout.addWidget(SectionTitle('Home cards'))
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        self.cards = []
        for idx, card_data in enumerate(settings_data.get('home_cards', [])):
            card = InfoCard(card_data['title'], card_data['text'])
            card.apply_surface(theme['surface_soft'], theme['surface_border'])
            grid.addWidget(card, idx // 3, idx % 3)
            self.cards.append(card)
        home_layout.addLayout(grid)
        self.page_layout.addWidget(home_panel)

        self.summary_card = InfoCard('Preview channel', settings_data['preview_card'])
        self.summary_card.apply_surface(theme['surface_soft'], theme['surface_border'])
        self.page_layout.addWidget(self.summary_card)

        self.controls_panel = AcrylicPanel(18)
        self.controls_panel.apply_surface(theme['surface_soft'], theme['surface_border'])
        self.controls_layout = QVBoxLayout(self.controls_panel)
        self.controls_layout.setContentsMargins(16, 16, 16, 16)
        self.controls_layout.setSpacing(10)
        self.controls_layout.addWidget(SectionTitle('Quick controls'))
        toggle_row = QWidget()
        toggle_row_layout = QHBoxLayout(toggle_row)
        toggle_row_layout.setContentsMargins(0, 0, 0, 0)
        toggle_row_layout.setSpacing(10)
        self.energy_toggle = ToggleButton('Energy Saver', True)
        self.focus_toggle = ToggleButton('Focus Assist', False)
        self.night_light_toggle = ToggleButton('Night Light', False)
        toggle_row_layout.addWidget(self.energy_toggle)
        toggle_row_layout.addWidget(self.focus_toggle)
        toggle_row_layout.addWidget(self.night_light_toggle)
        self.controls_layout.addWidget(toggle_row)
        self.page_layout.addWidget(self.controls_panel)

        self.actions_panel = AcrylicPanel(18)
        self.actions_panel.apply_surface(theme['surface_soft'], theme['surface_border'])
        actions_layout = QVBoxLayout(self.actions_panel)
        actions_layout.setContentsMargins(16, 16, 16, 16)
        actions_layout.setSpacing(10)
        actions_layout.addWidget(SectionTitle('Actions'))

        for text, target in [
            ('Set Aurora wallpaper', 'aurora.png'),
            ('Set Ocean wallpaper', 'ocean.png'),
            ('Set Violet wallpaper', 'violet.png'),
            ('Set Bloom wallpaper', 'bloom.png'),
            ('Sign out to login screen', None),
        ]:
            button = ActionButton(text, 'image' if target else 'user')
            if target:
                button.clicked.connect(lambda checked=False, value=target: self._on_wallpaper(value))
            else:
                button.clicked.connect(self._on_sign_out)
            actions_layout.addWidget(button)
        self.page_layout.addWidget(self.actions_panel)
        self.page_layout.addStretch(1)

        self._entry_anim = QPropertyAnimation(self, b'windowOpacity', self)
        self._entry_anim.setDuration(240)
        self._entry_anim.setStartValue(0.0)
        self._entry_anim.setEndValue(1.0)
        self._entry_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.nav.setCurrentRow(0)

    def _update_page(self, row: int) -> None:
        if row < 0:
            return
        category = self._settings_data['categories'][row]
        self.page_title.setText(category['name'])
        self.page_description.setText(category['description'])
        self.summary_card.title_label.setText(category['card_title'])
        self.summary_card.set_subtitle(category['card_text'])

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.setWindowOpacity(0.0)
        self._entry_anim.start()
