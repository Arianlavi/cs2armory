import math

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer, QRectF, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QPainterPath


class SplashScreen(QWidget):

    WIDTH = 460
    HEIGHT = 260

    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(self.WIDTH, self.HEIGHT)
        self._center_on_screen()

        self._angle = 0.0
        self._pulse = 0.0
        self._opacity = 1.0
        self._status = "Initializing..."

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)
        self._anim = None

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.x() + (screen.width() - self.WIDTH) // 2
        y = screen.y() + (screen.height() - self.HEIGHT) // 2
        self.move(x, y)

    def set_status(self, text: str):
        self._status = text
        self.update()

    def _tick(self):
        self._angle = (self._angle + 2.4) % 360
        self._pulse = (self._pulse + 0.06) % (2 * math.pi)
        self.update()

    def _get_opacity(self):
        return self._opacity

    def _set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)

    windowOpacityProp = pyqtProperty(float, _get_opacity, _set_opacity)

    def finish(self, target_window):

        self._timer.stop()
        anim = QPropertyAnimation(self, b"windowOpacityProp")
        anim.setDuration(260)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)

        def _done():
            self.close()
            target_window.show()
            target_window.raise_()
            target_window.activateWindow()

        anim.finished.connect(_done)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        self._anim = anim

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(0, 0, self.width(), self.height())
        panel = QPainterPath()
        panel.addRoundedRect(rect.adjusted(1, 1, -1, -1), 18, 18)

        bg = QLinearGradient(0, 0, 0, self.height())
        bg.setColorAt(0, QColor(19, 19, 23, 247))
        bg.setColorAt(1, QColor(11, 11, 13, 247))
        painter.fillPath(panel, bg)
        painter.setPen(QPen(QColor(212, 160, 48, 170), 1.3))
        painter.drawPath(panel)

        cx, cy = self.width() / 2, 96

        ring_r = 46
        painter.setPen(QPen(QColor(212, 160, 48, 55), 3))
        painter.drawEllipse(QRectF(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2))

        painter.setPen(QPen(QColor(232, 184, 64, 235), 4, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(QRectF(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2),
                         int(self._angle * 16), int(110 * 16))

        glow = 0.55 + 0.45 * math.sin(self._pulse)
        cross = QColor(232, 184, 64)
        cross.setAlphaF(min(1.0, 0.5 + 0.5 * glow))
        painter.setPen(QPen(cross, 2.3))
        gap, arm = 7, 13
        painter.drawLine(int(cx - gap - arm), int(cy), int(cx - gap), int(cy))
        painter.drawLine(int(cx + gap), int(cy), int(cx + gap + arm), int(cy))
        painter.drawLine(int(cx), int(cy - gap - arm), int(cx), int(cy - gap))
        painter.drawLine(int(cx), int(cy + gap), int(cx), int(cy + gap + arm))
        painter.setBrush(cross)
        painter.drawEllipse(QRectF(cx - 2, cy - 2, 4, 4))
        painter.setBrush(Qt.NoBrush)

        title_font = QFont("Segoe UI", 15, QFont.Bold)
        title_font.setLetterSpacing(QFont.AbsoluteSpacing, 3)
        painter.setPen(QColor(234, 234, 238))
        painter.setFont(title_font)
        painter.drawText(QRectF(0, 148, self.width(), 30), Qt.AlignCenter, "CS2  ARMORY")

        painter.setPen(QColor(138, 138, 158))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(QRectF(0, 180, self.width(), 20), Qt.AlignCenter, "SERVER FIREWALL MANAGER")

        painter.setPen(QColor(212, 160, 48))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(QRectF(20, self.height() - 40, self.width() - 40, 20), Qt.AlignCenter, self._status)

        bar_rect = QRectF(30, self.height() - 18, self.width() - 60, 4)
        track = QPainterPath()
        track.addRoundedRect(bar_rect, 2, 2)
        painter.fillPath(track, QColor(38, 38, 44))

        chunk_w = bar_rect.width() * 0.28
        offset = (self._angle / 360.0) * (bar_rect.width() + chunk_w) - chunk_w
        chunk_rect = QRectF(bar_rect.x() + max(0, min(offset, bar_rect.width() - chunk_w)),
                             bar_rect.y(), chunk_w, bar_rect.height())
        chunk = QPainterPath()
        chunk.addRoundedRect(chunk_rect, 2, 2)
        grad = QLinearGradient(chunk_rect.left(), 0, chunk_rect.right(), 0)
        grad.setColorAt(0, QColor(212, 160, 48))
        grad.setColorAt(1, QColor(232, 184, 64))
        painter.fillPath(chunk, grad)
