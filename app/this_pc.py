from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QPoint, Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .flyouts import ActionButton
from .widgets import AcrylicPanel, IconCanvas, InfoCard, SectionTitle, set_shadow
from .window_frame import TitleBar


class FileRowButton(QPushButton):
    def __init__(self, entry: dict, border: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.entry = entry
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setStyleSheet(
            f'''
            QPushButton {{
                background: rgba(255,255,255,0.04);
                color: white;
                border: 1px solid {border};
                border-radius: 16px;
                text-align: left;
            }}
            QPushButton:hover {{ background: rgba(255,255,255,0.08); }}
            '''
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)
        layout.addWidget(IconCanvas(entry['icon'], 24))

        text_col = QVBoxLayout()
        name = QLabel(entry['name'])
        name.setStyleSheet('font-size: 14px; font-weight: 700; color: white;')
        meta = QLabel(f"{entry['location']}   {entry['modified']}   {entry['size']}")
        meta.setStyleSheet('font-size: 12px; color: rgba(255,255,255,0.65);')
        text_col.addWidget(name)
        text_col.addWidget(meta)
        layout.addLayout(text_col, 1)


class FolderTileButton(QPushButton):
    def __init__(self, name: str, icon: str, border: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.folder_name = name
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f'''
            QPushButton {{
                background: rgba(255,255,255,0.05);
                color: white;
                border: 1px solid {border};
                border-radius: 16px;
                text-align: left;
            }}
            QPushButton:hover {{ background: rgba(255,255,255,0.10); }}
            '''
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        layout.addWidget(IconCanvas(icon, 28), 0, Qt.AlignmentFlag.AlignLeft)
        label = QLabel(name)
        label.setStyleSheet('font-size: 13px; font-weight: 600; color: white;')
        layout.addWidget(label)


class ThisPCWindow(QMainWindow):
    def __init__(self, theme: dict, files_data: list[dict], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(1180, 760)
        self.setStyleSheet('QMainWindow { background: transparent; } QLabel { color: white; }')
        self._files = files_data
        self._theme = theme

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
        shell_layout.addWidget(TitleBar('This PC', 'pc', self))

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(18, 16, 18, 18)
        content_layout.setSpacing(16)
        shell_layout.addWidget(content, 1)

        nav = QListWidget()
        nav.setFixedWidth(220)
        nav.setStyleSheet(
            'QListWidget { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.10); border-radius: 16px; color: white; padding: 8px; } '
            'QListWidget::item { padding: 9px 8px; border-radius: 10px; } '
            'QListWidget::item:selected { background: rgba(255,255,255,0.10); }'
        )
        for item in ['Home', 'Desktop', 'Documents', 'Downloads', 'Pictures', 'Music', 'Videos', 'This PC', 'OneDrive']:
            QListWidgetItem(item, nav)
        nav.setCurrentRow(7)
        content_layout.addWidget(nav)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setSpacing(14)
        content_layout.addWidget(right, 1)

        header = QLabel('This PC')
        header.setStyleSheet('font-size: 32px; font-weight: 700;')
        right_layout.addWidget(header)

        self.feedback = QLabel('Select a folder or file to view its action.')
        self.feedback.setStyleSheet('font-size: 12px; color: rgba(255,255,255,0.70);')
        right_layout.addWidget(self.feedback)

        toolbar_panel = AcrylicPanel(18)
        toolbar_panel.apply_surface(theme['surface_soft'], theme['surface_border'])
        toolbar_layout = QHBoxLayout(toolbar_panel)
        toolbar_layout.setContentsMargins(14, 14, 14, 14)
        toolbar_layout.setSpacing(10)
        for text, handler in [('Open selected item', lambda: self.feedback.setText('Open action is ready for the selected item.')), ('Refresh', self.refresh_view), ('Properties', lambda: self.feedback.setText('Properties view can be expanded in the next build.'))]:
            button = ActionButton(text, 'folder')
            button.clicked.connect(handler)
            toolbar_layout.addWidget(button)
        right_layout.addWidget(toolbar_panel)

        stat_row = QWidget()
        stat_layout = QHBoxLayout(stat_row)
        stat_layout.setContentsMargins(0, 0, 0, 0)
        stat_layout.setSpacing(12)
        for title, text in [('Devices and drives', '3 drives available'), ('Storage', '824 GB free of 1.2 TB'), ('Cloud state', 'OneDrive connected')]:
            card = InfoCard(title, text)
            card.apply_surface(theme['surface_soft'], theme['surface_border'])
            stat_layout.addWidget(card)
        right_layout.addWidget(stat_row)

        folders_panel = AcrylicPanel(18)
        folders_panel.apply_surface(theme['surface_soft'], theme['surface_border'])
        folders_layout = QVBoxLayout(folders_panel)
        folders_layout.setContentsMargins(16, 16, 16, 16)
        folders_layout.setSpacing(12)
        folders_layout.addWidget(SectionTitle('Folders'))
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        folders = [('Desktop', 'folder'), ('Documents', 'doc'), ('Downloads', 'folder'), ('Pictures', 'image'), ('Videos', 'video'), ('Music', 'folder')]
        for i, (name, icon) in enumerate(folders):
            tile = FolderTileButton(name, icon, theme['surface_border'])
            tile.clicked.connect(lambda checked=False, folder=name: self.feedback.setText(f'Opened {folder} view in This PC.'))
            grid.addWidget(tile, i // 3, i % 3)
        folders_layout.addLayout(grid)
        right_layout.addWidget(folders_panel)

        recent_panel = AcrylicPanel(18)
        recent_panel.apply_surface(theme['surface_soft'], theme['surface_border'])
        recent_layout = QVBoxLayout(recent_panel)
        recent_layout.setContentsMargins(16, 16, 16, 16)
        recent_layout.setSpacing(10)
        recent_layout.addWidget(SectionTitle('Recent files'))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setSpacing(10)
        for entry in files_data:
            row = FileRowButton(entry, theme['surface_border'])
            row.clicked.connect(lambda checked=False, e=entry: self.feedback.setText(f"Selected {e['name']} from {e['location']}"))
            row.customContextMenuRequested.connect(lambda pos, button=row: self._show_context_menu(button, pos))
            body_layout.addWidget(row)
        body_layout.addStretch(1)
        scroll.setWidget(body)
        recent_layout.addWidget(scroll)
        right_layout.addWidget(recent_panel, 1)

        self._entry_anim = QPropertyAnimation(self, b'windowOpacity', self)
        self._entry_anim.setDuration(260)
        self._entry_anim.setStartValue(0.0)
        self._entry_anim.setEndValue(1.0)
        self._entry_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def refresh_view(self) -> None:
        self.feedback.setText('This PC refreshed.')

    def _show_context_menu(self, button: FileRowButton, pos: QPoint) -> None:
        menu = QMenu(self)
        menu.setStyleSheet('QMenu { background: #101b31; color: white; border: 1px solid rgba(255,255,255,0.15); padding: 8px; } QMenu::item { padding: 8px 18px; border-radius: 8px; } QMenu::item:selected { background: rgba(255,255,255,0.10); }')
        open_action = menu.addAction('Open')
        copy_action = menu.addAction('Copy path')
        prop_action = menu.addAction('Properties')
        action = menu.exec(button.mapToGlobal(pos))
        if action == open_action:
            self.feedback.setText(f"Opened {button.entry['name']}")
        elif action == copy_action:
            self.feedback.setText(f"Copied path: {button.entry['location']}\\{button.entry['name']}")
        elif action == prop_action:
            self.feedback.setText(f"Properties: {button.entry['size']}  Modified {button.entry['modified']}")

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.setWindowOpacity(0.0)
        self._entry_anim.start()
