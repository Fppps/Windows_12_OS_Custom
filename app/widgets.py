from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


def set_shadow(widget: QWidget, blur: int = 32, y_offset: int = 12, alpha: int = 95) -> None:
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, y_offset)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)


class WallpaperWidget(QWidget):
    def __init__(self, image_path: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._image_path = image_path

    def paintEvent(self, event) -> None:  # pragma: no cover
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        width = rect.width()
        height = rect.height()

        if self._image_path:
            pix = QPixmap(self._image_path)
            if not pix.isNull():
                scaled = pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                x = (self.width() - scaled.width()) // 2
                y = (self.height() - scaled.height()) // 2
                painter.drawPixmap(x, y, scaled)
                return

        base = QLinearGradient(0, 0, width, height)
        base.setColorAt(0.0, QColor("#1b1479"))
        base.setColorAt(0.35, QColor("#2436b8"))
        base.setColorAt(0.72, QColor("#1550ca"))
        base.setColorAt(1.0, QColor("#7839dd"))
        painter.fillRect(rect, base)

        def blob(cx: float, cy: float, radius: float, colors: list[tuple[float, str]], stretch_x: float = 1.0, stretch_y: float = 1.0) -> None:
            gradient = QRadialGradient(cx, cy, radius)
            for stop, color in colors:
                gradient.setColorAt(stop, QColor(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            painter.save()
            painter.translate(cx, cy)
            painter.scale(stretch_x, stretch_y)
            painter.drawEllipse(QRectF(-radius, -radius, radius * 2, radius * 2))
            painter.restore()

        blob(width * 0.02, height * 0.66, height * 0.42, [(0.0, "#f39fff"), (0.45, "#b450df"), (1.0, "#00000000")], 1.05, 1.18)
        blob(width * 0.58, height * 0.12, height * 0.30, [(0.0, "#52e4ff"), (0.46, "#2d7ef2"), (1.0, "#00000000")], 1.52, 0.70)
        blob(width * 0.32, height * 0.92, height * 0.34, [(0.0, "#34dfff"), (0.50, "#2477dc"), (1.0, "#00000000")], 1.15, 1.05)
        blob(width * 0.90, height * 0.78, height * 0.30, [(0.0, "#f2a2ff"), (0.46, "#a84ce4"), (1.0, "#00000000")], 1.28, 1.03)

        ribbon = QPainterPath()
        ribbon.moveTo(width * 0.30, height * 0.52)
        ribbon.cubicTo(width * 0.44, height * 0.30, width * 0.54, height * 0.22, width * 0.72, height * 0.12)
        ribbon.cubicTo(width * 0.88, height * 0.05, width * 0.90, height * 0.34, width * 0.75, height * 0.50)
        ribbon.cubicTo(width * 0.62, height * 0.67, width * 0.44, height * 0.74, width * 0.36, height * 0.88)
        ribbon.cubicTo(width * 0.24, height * 0.68, width * 0.22, height * 0.60, width * 0.30, height * 0.52)
        painter.setBrush(QColor(17, 20, 110, 150))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(ribbon)

        ribbon_two = QPainterPath()
        ribbon_two.moveTo(width * 0.48, height * 0.55)
        ribbon_two.cubicTo(width * 0.60, height * 0.42, width * 0.68, height * 0.42, width * 0.81, height * 0.35)
        ribbon_two.cubicTo(width * 0.79, height * 0.61, width * 0.66, height * 0.78, width * 0.55, height * 0.78)
        ribbon_two.cubicTo(width * 0.45, height * 0.79, width * 0.42, height * 0.63, width * 0.48, height * 0.55)
        painter.setBrush(QColor(0, 26, 123, 168))
        painter.drawPath(ribbon_two)

        vignette = QRadialGradient(width * 0.5, height * 0.5, max(width, height) * 0.8)
        vignette.setColorAt(0.66, QColor(0, 0, 0, 0))
        vignette.setColorAt(1.0, QColor(0, 0, 0, 60))
        painter.fillRect(rect, vignette)


def _pen(color: str | QColor, width: float = 1.6) -> QPen:
    pen = QPen(QColor(color))
    pen.setWidthF(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def draw_symbol_icon(painter: QPainter, kind: str, rect: QRectF, accent: str = "#58b7ff", mono: bool = False) -> None:  # pragma: no cover
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    fg = QColor("#2d3548") if mono else QColor(accent)
    fg2 = QColor("#7a4cff") if not mono else QColor("#2d3548")
    light = QColor("#eaf4ff") if not mono else QColor("#2d3548")
    outline = QColor("#f6fbff") if not mono else QColor("#2d3548")
    dark = QColor("#2457b5") if not mono else QColor("#2d3548")

    inner = QRectF(rect.adjusted(rect.width() * 0.12, rect.height() * 0.12, -rect.width() * 0.12, -rect.height() * 0.12))

    if kind == "windows":
        gap = inner.width() * 0.10
        tile_w = (inner.width() - gap) / 2.0
        tile_h = (inner.height() - gap) / 2.0
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#4ab6ff") if not mono else fg)
        for dx in [0, tile_w + gap]:
            for dy in [0, tile_h + gap]:
                painter.drawRoundedRect(QRectF(inner.left() + dx, inner.top() + dy, tile_w, tile_h), 2, 2)
    elif kind == "search":
        painter.setPen(_pen(fg, inner.width() * 0.10))
        circle = QRectF(inner.left(), inner.top(), inner.width() * 0.62, inner.height() * 0.62)
        painter.drawEllipse(circle)
        painter.drawLine(circle.center().x() + circle.width() * 0.28, circle.center().y() + circle.height() * 0.28, inner.right(), inner.bottom())
    elif kind == "folder":
        painter.setPen(Qt.PenStyle.NoPen)
        tab = QRectF(inner.left(), inner.top() + inner.height() * 0.10, inner.width() * 0.46, inner.height() * 0.22)
        body = QRectF(inner.left(), inner.top() + inner.height() * 0.24, inner.width(), inner.height() * 0.56)
        painter.setBrush(QColor("#f2c43d") if not mono else fg)
        painter.drawRoundedRect(tab, 4, 4)
        painter.setBrush(QColor("#ffd857") if not mono else fg)
        painter.drawRoundedRect(body, 6, 6)
    elif kind == "edge":
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#2fd0af") if not mono else fg)
        painter.drawEllipse(inner)
        painter.setBrush(QColor("#2a6cf3") if not mono else fg)
        path = QPainterPath()
        path.moveTo(inner.left() + inner.width() * 0.18, inner.center().y())
        path.cubicTo(inner.left() + inner.width() * 0.28, inner.bottom(), inner.right(), inner.bottom(), inner.right(), inner.center().y())
        path.cubicTo(inner.right(), inner.top() + inner.height() * 0.24, inner.left() + inner.width() * 0.46, inner.top(), inner.left() + inner.width() * 0.18, inner.center().y())
        painter.drawPath(path)
        painter.setBrush(QColor("#dffcff") if not mono else QColor("white"))
        painter.drawEllipse(QRectF(inner.left() + inner.width() * 0.26, inner.top() + inner.height() * 0.27, inner.width() * 0.44, inner.height() * 0.44))
    elif kind == "store":
        body = QRectF(inner.left() + inner.width() * 0.08, inner.top() + inner.height() * 0.24, inner.width() * 0.84, inner.height() * 0.56)
        handle = QRectF(inner.left() + inner.width() * 0.28, inner.top() + inner.height() * 0.10, inner.width() * 0.44, inner.height() * 0.24)
        painter.setBrush(QColor("#1f4be2") if not mono else fg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(body, 6, 6)
        painter.setPen(_pen("#e9f4ff" if not mono else fg, inner.width() * 0.08))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(handle, 30 * 16, 120 * 16)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#3ab0ff") if not mono else fg)
        plus_h = QRectF(inner.center().x() - inner.width() * 0.16, inner.center().y() - inner.height() * 0.04, inner.width() * 0.32, inner.height() * 0.08)
        plus_v = QRectF(inner.center().x() - inner.width() * 0.04, inner.center().y() - inner.height() * 0.16, inner.width() * 0.08, inner.height() * 0.32)
        painter.drawRoundedRect(plus_h, 2, 2)
        painter.drawRoundedRect(plus_v, 2, 2)
    elif kind == "mail":
        body = QRectF(inner.left() + inner.width() * 0.05, inner.top() + inner.height() * 0.18, inner.width() * 0.90, inner.height() * 0.64)
        painter.setBrush(QColor("#2376ff") if not mono else fg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(body, 7, 7)
        painter.setPen(_pen("#eaf4ff" if not mono else fg, inner.width() * 0.08))
        painter.drawLine(body.left() + body.width() * 0.08, body.top() + body.height() * 0.12, body.center().x(), body.center().y())
        painter.drawLine(body.right() - body.width() * 0.08, body.top() + body.height() * 0.12, body.center().x(), body.center().y())
    elif kind == "widgets":
        painter.setPen(Qt.PenStyle.NoPen)
        colors = [QColor("#0e75ff"), QColor("#35b1ff"), QColor("#f0c340"), QColor("#2d67d3")]
        sizes = [(0.00, 0.00, 0.44, 0.32), (0.50, 0.00, 0.30, 0.32), (0.00, 0.40, 0.30, 0.40), (0.36, 0.40, 0.44, 0.40)]
        for idx, (x, y, w, h) in enumerate(sizes):
            painter.setBrush(colors[idx] if not mono else fg)
            painter.drawRoundedRect(QRectF(inner.left() + inner.width() * x, inner.top() + inner.height() * y, inner.width() * w, inner.height() * h), 4, 4)
    elif kind == "pc":
        screen = QRectF(inner.left() + inner.width() * 0.05, inner.top() + inner.height() * 0.05, inner.width() * 0.90, inner.height() * 0.58)
        base_rect = QRectF(inner.left() + inner.width() * 0.32, inner.top() + inner.height() * 0.68, inner.width() * 0.36, inner.height() * 0.10)
        stand_rect = QRectF(inner.left() + inner.width() * 0.45, inner.top() + inner.height() * 0.60, inner.width() * 0.10, inner.height() * 0.12)
        grad = QLinearGradient(screen.topLeft(), screen.bottomRight())
        grad.setColorAt(0, QColor("#5ce2ff") if not mono else fg)
        grad.setColorAt(1, QColor("#2570d4") if not mono else fg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawRoundedRect(screen, 6, 6)
        painter.setBrush(QColor("#2d3548") if not mono else fg)
        painter.drawRoundedRect(stand_rect, 2, 2)
        painter.drawRoundedRect(base_rect, 4, 4)
    elif kind == "recycle":
        lid = QRectF(inner.left() + inner.width() * 0.24, inner.top() + inner.height() * 0.10, inner.width() * 0.52, inner.height() * 0.10)
        body = QRectF(inner.left() + inner.width() * 0.20, inner.top() + inner.height() * 0.22, inner.width() * 0.60, inner.height() * 0.56)
        painter.setBrush(QColor("#edf1ff") if not mono else fg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(lid, 2, 2)
        painter.drawRoundedRect(body, 6, 6)
        painter.setPen(_pen("#22a6ff" if not mono else light, inner.width() * 0.06))
        painter.drawArc(QRectF(body.left() + body.width() * 0.18, body.top() + body.height() * 0.18, body.width() * 0.30, body.height() * 0.30), 30 * 16, 200 * 16)
        painter.drawArc(QRectF(body.left() + body.width() * 0.44, body.top() + body.height() * 0.34, body.width() * 0.26, body.height() * 0.26), 190 * 16, 200 * 16)
        painter.drawArc(QRectF(body.left() + body.width() * 0.28, body.top() + body.height() * 0.46, body.width() * 0.26, body.height() * 0.26), 320 * 16, 200 * 16)
    elif kind == "control":
        body = QRectF(inner.left() + inner.width() * 0.06, inner.top() + inner.height() * 0.15, inner.width() * 0.88, inner.height() * 0.66)
        painter.setBrush(QColor("#e2f4ff") if not mono else fg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(body, 7, 7)
        colors = [QColor("#ee9c29"), QColor("#2a8ff7"), QColor("#31c1c4")]
        bars = [0.26, 0.50, 0.74]
        for idx, cy in enumerate(bars):
            painter.setPen(_pen("#2b79df" if not mono else fg, inner.width() * 0.07))
            y = body.top() + body.height() * cy
            painter.drawLine(body.left() + body.width() * 0.18, y, body.right() - body.width() * 0.12, y)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(colors[idx] if not mono else fg)
            x = body.left() + body.width() * (0.28 if idx == 0 else 0.63 if idx == 1 else 0.43)
            painter.drawEllipse(QRectF(x, y - body.height() * 0.10, body.height() * 0.20, body.height() * 0.20))
    elif kind == "doc":
        page = QRectF(inner.left() + inner.width() * 0.18, inner.top() + inner.height() * 0.08, inner.width() * 0.64, inner.height() * 0.74)
        painter.setBrush(QColor("#ebf2ff") if not mono else fg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(page, 5, 5)
        painter.setPen(_pen("#2a7bf6" if not mono else light, inner.width() * 0.06))
        for row in [0.30, 0.46, 0.62]:
            y = page.top() + page.height() * row
            painter.drawLine(page.left() + page.width() * 0.14, y, page.right() - page.width() * 0.14, y)
    elif kind == "sheet":
        page = QRectF(inner.left() + inner.width() * 0.18, inner.top() + inner.height() * 0.08, inner.width() * 0.64, inner.height() * 0.74)
        painter.setBrush(QColor("#eafff1") if not mono else fg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(page, 5, 5)
        painter.setPen(_pen("#1f9f4d" if not mono else light, inner.width() * 0.05))
        for row in [0.30, 0.48, 0.66]:
            y = page.top() + page.height() * row
            painter.drawLine(page.left() + page.width() * 0.14, y, page.right() - page.width() * 0.14, y)
        for col in [0.36, 0.58]:
            x = page.left() + page.width() * col
            painter.drawLine(x, page.top() + page.height() * 0.18, x, page.bottom() - page.height() * 0.14)
    elif kind == "image":
        frame = QRectF(inner.left() + inner.width() * 0.08, inner.top() + inner.height() * 0.16, inner.width() * 0.84, inner.height() * 0.58)
        painter.setBrush(QColor("#ebf2ff") if not mono else fg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(frame, 5, 5)
        painter.setBrush(QColor("#87d0ff") if not mono else light)
        painter.drawEllipse(QRectF(frame.left() + frame.width() * 0.12, frame.top() + frame.height() * 0.12, frame.height() * 0.18, frame.height() * 0.18))
        mountains = QPainterPath()
        mountains.moveTo(frame.left() + frame.width() * 0.14, frame.bottom() - frame.height() * 0.16)
        mountains.lineTo(frame.left() + frame.width() * 0.42, frame.top() + frame.height() * 0.38)
        mountains.lineTo(frame.left() + frame.width() * 0.58, frame.bottom() - frame.height() * 0.16)
        mountains.lineTo(frame.left() + frame.width() * 0.72, frame.top() + frame.height() * 0.50)
        mountains.lineTo(frame.right() - frame.width() * 0.12, frame.bottom() - frame.height() * 0.16)
        mountains.closeSubpath()
        painter.setBrush(QColor("#4a75ff") if not mono else light)
        painter.drawPath(mountains)
    elif kind == "video":
        frame = QRectF(inner.left() + inner.width() * 0.10, inner.top() + inner.height() * 0.20, inner.width() * 0.80, inner.height() * 0.52)
        painter.setBrush(QColor("#102c72") if not mono else fg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(frame, 6, 6)
        triangle = QPainterPath()
        triangle.moveTo(frame.left() + frame.width() * 0.40, frame.top() + frame.height() * 0.26)
        triangle.lineTo(frame.right() - frame.width() * 0.28, frame.center().y())
        triangle.lineTo(frame.left() + frame.width() * 0.40, frame.bottom() - frame.height() * 0.26)
        triangle.closeSubpath()
        painter.setBrush(QColor("#7fd4ff") if not mono else light)
        painter.drawPath(triangle)
    elif kind == "code":
        painter.setPen(_pen("#7fd4ff" if not mono else fg, inner.width() * 0.08))
        painter.drawLine(inner.left() + inner.width() * 0.22, inner.center().y(), inner.left() + inner.width() * 0.42, inner.top() + inner.height() * 0.26)
        painter.drawLine(inner.left() + inner.width() * 0.22, inner.center().y(), inner.left() + inner.width() * 0.42, inner.bottom() - inner.height() * 0.26)
        painter.drawLine(inner.right() - inner.width() * 0.22, inner.center().y(), inner.right() - inner.width() * 0.42, inner.top() + inner.height() * 0.26)
        painter.drawLine(inner.right() - inner.width() * 0.22, inner.center().y(), inner.right() - inner.width() * 0.42, inner.bottom() - inner.height() * 0.26)
        painter.drawLine(inner.center().x() + inner.width() * 0.06, inner.top() + inner.height() * 0.18, inner.center().x() - inner.width() * 0.06, inner.bottom() - inner.height() * 0.18)
    elif kind == "sync":
        painter.setPen(_pen("#58b7ff" if not mono else fg, inner.width() * 0.08))
        painter.drawArc(QRectF(inner.left() + inner.width() * 0.10, inner.top() + inner.height() * 0.18, inner.width() * 0.50, inner.height() * 0.50), 30 * 16, 240 * 16)
        painter.drawArc(QRectF(inner.left() + inner.width() * 0.38, inner.top() + inner.height() * 0.32, inner.width() * 0.44, inner.height() * 0.44), 210 * 16, 230 * 16)
    elif kind == "shield":
        path = QPainterPath()
        path.moveTo(inner.center().x(), inner.top())
        path.lineTo(inner.right(), inner.top() + inner.height() * 0.20)
        path.lineTo(inner.right() - inner.width() * 0.06, inner.center().y() + inner.height() * 0.18)
        path.lineTo(inner.center().x(), inner.bottom())
        path.lineTo(inner.left() + inner.width() * 0.06, inner.center().y() + inner.height() * 0.18)
        path.lineTo(inner.left(), inner.top() + inner.height() * 0.20)
        path.closeSubpath()
        painter.setBrush(QColor("#2f81ff") if not mono else fg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        painter.setPen(_pen("#eaf4ff" if not mono else light, inner.width() * 0.07))
        painter.drawLine(inner.center().x(), inner.top() + inner.height() * 0.20, inner.center().x(), inner.bottom() - inner.height() * 0.18)
    elif kind == "update":
        painter.setPen(_pen("#58b7ff" if not mono else fg, inner.width() * 0.08))
        painter.drawArc(QRectF(inner.left() + inner.width() * 0.10, inner.top() + inner.height() * 0.10, inner.width() * 0.64, inner.height() * 0.64), 40 * 16, 260 * 16)
        painter.drawLine(inner.right() - inner.width() * 0.18, inner.top() + inner.height() * 0.20, inner.right() - inner.width() * 0.06, inner.top() + inner.height() * 0.08)
        painter.drawLine(inner.right() - inner.width() * 0.18, inner.top() + inner.height() * 0.20, inner.right() - inner.width() * 0.04, inner.top() + inner.height() * 0.26)
    elif kind == "network":
        painter.setPen(_pen("#2d3548" if mono else "#344055", inner.width() * 0.07))
        for span, y in [(0.64, 0.70), (0.44, 0.56), (0.24, 0.42)]:
            arc = QRectF(inner.center().x() - inner.width() * span / 2, inner.top() + inner.height() * y - inner.width() * span / 2, inner.width() * span, inner.width() * span)
            painter.drawArc(arc, 35 * 16, 110 * 16)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#344055") if mono else QColor("#344055"))
        painter.drawEllipse(QRectF(inner.center().x() - inner.width() * 0.05, inner.bottom() - inner.height() * 0.14, inner.width() * 0.10, inner.height() * 0.10))
    elif kind == "volume":
        speaker = QPainterPath()
        speaker.moveTo(inner.left() + inner.width() * 0.18, inner.center().y())
        speaker.lineTo(inner.left() + inner.width() * 0.34, inner.top() + inner.height() * 0.34)
        speaker.lineTo(inner.left() + inner.width() * 0.46, inner.top() + inner.height() * 0.34)
        speaker.lineTo(inner.left() + inner.width() * 0.46, inner.bottom() - inner.height() * 0.34)
        speaker.lineTo(inner.left() + inner.width() * 0.34, inner.bottom() - inner.height() * 0.34)
        speaker.closeSubpath()
        painter.setBrush(QColor("#344055") if mono else QColor("#344055"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(speaker)
        painter.setPen(_pen("#344055", inner.width() * 0.06))
        painter.drawArc(QRectF(inner.left() + inner.width() * 0.34, inner.top() + inner.height() * 0.24, inner.width() * 0.40, inner.height() * 0.52), -45 * 16, 90 * 16)
    elif kind == "display":
        painter.setBrush(QColor("#344055") if mono else QColor("#344055"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(inner.left() + inner.width() * 0.10, inner.top() + inner.height() * 0.16, inner.width() * 0.80, inner.height() * 0.48), 5, 5)
        painter.drawRoundedRect(QRectF(inner.left() + inner.width() * 0.44, inner.top() + inner.height() * 0.66, inner.width() * 0.12, inner.height() * 0.10), 2, 2)
        painter.drawRoundedRect(QRectF(inner.left() + inner.width() * 0.30, inner.top() + inner.height() * 0.78, inner.width() * 0.40, inner.height() * 0.06), 2, 2)
    elif kind == "user":
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#344055") if mono else QColor("#344055"))
        painter.drawEllipse(QRectF(inner.left() + inner.width() * 0.30, inner.top() + inner.height() * 0.12, inner.width() * 0.40, inner.height() * 0.34))
        painter.drawRoundedRect(QRectF(inner.left() + inner.width() * 0.20, inner.top() + inner.height() * 0.52, inner.width() * 0.60, inner.height() * 0.22), 6, 6)
    elif kind == "more":
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#344055") if mono else QColor("#344055"))
        r = inner.width() * 0.08
        for offset in [0.30, 0.50, 0.70]:
            painter.drawEllipse(QRectF(inner.left() + inner.width() * offset - r, inner.center().y() - r, r * 2, r * 2))
    elif kind == "chevron":
        painter.setPen(_pen("#344055" if mono else "#344055", inner.width() * 0.08))
        painter.drawLine(inner.left() + inner.width() * 0.24, inner.center().y() + inner.height() * 0.08, inner.center().x(), inner.top() + inner.height() * 0.32)
        painter.drawLine(inner.center().x(), inner.top() + inner.height() * 0.32, inner.right() - inner.width() * 0.24, inner.center().y() + inner.height() * 0.08)
    elif kind == "camera":
        body = QRectF(inner.left() + inner.width() * 0.16, inner.top() + inner.height() * 0.24, inner.width() * 0.68, inner.height() * 0.48)
        painter.setBrush(QColor("#344055") if mono else QColor("#344055"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(body, 5, 5)
        painter.setBrush(QColor("#f8fbff") if not mono else QColor("white"))
        painter.drawEllipse(QRectF(inner.left() + inner.width() * 0.34, inner.top() + inner.height() * 0.34, inner.width() * 0.24, inner.height() * 0.24))
    else:
        painter.setBrush(fg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(inner, 6, 6)

    painter.restore()


class AcrylicPanel(QFrame):
    def __init__(self, radius: int = 24, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._radius = radius
        self.setObjectName("AcrylicPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        set_shadow(self)

    def apply_surface(self, tint: str, border: str) -> None:
        self.setStyleSheet(
            f"""
            QFrame#AcrylicPanel {{
                background: {tint};
                border: 1px solid {border};
                border-radius: {self._radius}px;
            }}
            """
        )


class IconCanvas(QWidget):
    def __init__(self, kind: str, size: int = 22, accent: str = "#58b7ff", mono: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.kind = kind
        self.accent = accent
        self.mono = mono
        self.setFixedSize(size, size)

    def paintEvent(self, event) -> None:  # pragma: no cover
        painter = QPainter(self)
        draw_symbol_icon(painter, self.kind, QRectF(self.rect()), self.accent, self.mono)


class SearchPill(AcrylicPanel):
    clicked = Signal()

    def __init__(self, placeholder: str, compact: bool = False, parent: QWidget | None = None) -> None:
        radius = 22 if compact else 26
        super().__init__(radius, parent)
        self.compact = compact
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        height = 44 if compact else 64
        self.setFixedHeight(height)
        self.apply_surface("rgba(246,249,255,0.84)", "rgba(255,255,255,0.45)")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16 if compact else 20, 8, 16 if compact else 20, 8)
        layout.setSpacing(12)

        layout.addWidget(IconCanvas("search", 18 if compact else 22, mono=True))

        text = QLabel(placeholder)
        text.setStyleSheet(
            f"color: #525f73; font-size: {'13px' if compact else '17px'}; font-weight: 500;"
        )
        layout.addWidget(text, 1)

        if not compact:
            layout.addWidget(IconCanvas("camera", 20, mono=True))
            layout.addWidget(IconCanvas("more", 20, mono=True))

    def mousePressEvent(self, event) -> None:  # pragma: no cover
        self.clicked.emit()
        super().mousePressEvent(event)


class DesktopShortcut(QPushButton):
    def __init__(self, kind: str, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.kind = kind
        self.label = label
        self.setFixedSize(96, 118)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")

    def paintEvent(self, event) -> None:  # pragma: no cover
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.underMouse() or self.isDown():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 22))
            painter.drawRoundedRect(self.rect().adjusted(4, 4, -4, -4), 12, 12)

        icon_box = QRectF(18, 6, 56, 56)
        painter.setPen(QPen(QColor(255, 255, 255, 36), 1.2))
        painter.setBrush(QColor(255, 255, 255, 14))
        painter.drawRoundedRect(icon_box, 12, 12)
        draw_symbol_icon(painter, self.kind, icon_box.adjusted(6, 6, -6, -6), mono=False)

        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        text_rect = QRectF(4, 68, self.width() - 8, 42)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap, self.label)



class TaskbarIconButton(QToolButton):
    def __init__(self, kind: str, parent: QWidget | None = None, active: bool = False) -> None:
        super().__init__(parent)
        self.kind = kind
        self.active = active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(44, 44)
        self.setStyleSheet("QToolButton { background: transparent; border: none; }")

    def set_active(self, active: bool) -> None:
        self.active = active
        self.update()

    def paintEvent(self, event) -> None:  # pragma: no cover
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())

        if self.underMouse() or self.isDown():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 40))
            painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 12, 12)

        draw_symbol_icon(painter, self.kind, rect.adjusted(9, 9, -9, -9), mono=False)

        if self.active:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#3faefb"))
            painter.drawRoundedRect(QRectF(rect.center().x() - 7, rect.bottom() - 5, 14, 3), 1.5, 1.5)


class WeatherWidget(QWidget):
    clicked = Signal()

    def __init__(self, title: str, subtitle: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(54)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)

        weather_dot = QWidget()
        weather_dot.setFixedSize(26, 26)
        weather_dot.setStyleSheet(
            """
            QWidget {
                border-radius: 13px;
                background: qradialgradient(cx: 0.35, cy: 0.35, radius: 0.95,
                    stop: 0 #ffb02a,
                    stop: 0.55 #ff6a00,
                    stop: 1 #c72b00);
            }
            """
        )
        layout.addWidget(weather_dot)

        column = QVBoxLayout()
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        top = QLabel(title)
        top.setStyleSheet("color: #3b4353; font-size: 14px; font-weight: 700;")
        bottom = QLabel(subtitle)
        bottom.setStyleSheet("color: #5d6678; font-size: 13px; font-weight: 500;")
        column.addWidget(top)
        column.addWidget(bottom)
        layout.addLayout(column)

    def mousePressEvent(self, event) -> None:  # pragma: no cover
        self.clicked.emit()
        super().mousePressEvent(event)


class ToggleButton(QPushButton):
    def __init__(self, text: str, state: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setChecked(state)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self.sync_style()
        self.toggled.connect(lambda _: self.sync_style())

    def sync_style(self) -> None:
        if self.isChecked():
            self.setStyleSheet(
                """
                QPushButton {
                    background: rgba(88, 183, 255, 0.95);
                    color: #08162a;
                    border: 1px solid rgba(255,255,255,0.24);
                    border-radius: 14px;
                    font-weight: 700;
                    padding: 10px 14px;
                }
                """
            )
        else:
            self.setStyleSheet(
                """
                QPushButton {
                    background: rgba(255,255,255,0.08);
                    color: #f6fbff;
                    border: 1px solid rgba(255,255,255,0.12);
                    border-radius: 14px;
                    font-weight: 600;
                    padding: 10px 14px;
                }
                """
            )


class SectionTitle(QLabel):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setStyleSheet(
            """
            QLabel {
                color: rgba(255,255,255,0.90);
                font-size: 15px;
                font-weight: 700;
                padding-bottom: 4px;
            }
            """
        )


class SurfaceButton(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(38)
        self.setStyleSheet(
            """
            QPushButton {
                background: rgba(255,255,255,0.08);
                color: #f6fbff;
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 12px;
                padding: 10px 12px;
                text-align: left;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.13);
            }
            """
        )


class InfoCard(AcrylicPanel):
    def __init__(self, title: str, subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(20, parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 700;")
        layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet("color: rgba(255,255,255,0.74); font-size: 12px;")
        layout.addWidget(self.subtitle_label)

    def set_subtitle(self, value: str) -> None:
        self.subtitle_label.setText(value)


def hstack(*widgets: QWidget, spacing: int = 10, margins: tuple[int, int, int, int] = (0, 0, 0, 0)) -> QWidget:
    box = QWidget()
    layout = QHBoxLayout(box)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    for widget in widgets:
        layout.addWidget(widget)
    return box


def vstack(*widgets: QWidget, spacing: int = 10, margins: tuple[int, int, int, int] = (0, 0, 0, 0)) -> QWidget:
    box = QWidget()
    layout = QVBoxLayout(box)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    for widget in widgets:
        layout.addWidget(widget)
    return box


class SlideAnimator:
    def __init__(self, widget: QWidget) -> None:
        self.widget = widget
        self.animation = QPropertyAnimation(widget, b"pos", widget)
        self.animation.setDuration(220)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.shown_point = QPoint()
        self.hidden_point = QPoint()
        self._hide_when_done = False
        self.animation.finished.connect(self._on_finished)

    def configure(self, shown_point: QPoint, hidden_point: QPoint) -> None:
        self.shown_point = shown_point
        self.hidden_point = hidden_point

    def _on_finished(self) -> None:
        if self._hide_when_done:
            self.widget.hide()

    def slide_to(self, point: QPoint) -> None:
        self._hide_when_done = False
        self.animation.stop()
        self.widget.show()
        self.animation.setStartValue(self.widget.pos())
        self.animation.setEndValue(point)
        self.animation.start()

    def slide_up_or_down(self, show: bool) -> None:
        target = self.shown_point if show else self.hidden_point
        self._hide_when_done = not show
        self.animation.stop()
        self.widget.show()
        self.animation.setStartValue(self.widget.pos())
        self.animation.setEndValue(target)
        self.animation.start()
