import sys
import time
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QGraphicsOpacityEffect, QGraphicsBlurEffect,
    QGraphicsScene, QGraphicsPixmapItem
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QObject,
    pyqtSignal, QRectF
)
from PyQt6.QtGui import (
    QPainter, QPainterPath, QColor, QPen, QBrush, QPixmap, QImage,
    QLinearGradient, QRadialGradient, QTransform
)


def clamp_byte(v):
    return 0 if v < 0 else 255 if v > 255 else int(v)


class LiquidGlassNotification(QWidget):
    """Liquid glass notification: simulated backdrop blur + layered lighting"""

    def __init__(self, message, shortcut, duration=3.0):
        super().__init__()
        self.message = message
        self.shortcut = shortcut
        self.duration = float(duration)

        # Window flags and attributes
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Start fully opaque
        self.setWindowOpacity(1.0)

        # Geometry
        self.width = 320  # Reduced from 380
        self.height = 40  # Reduced from 56
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width - 10
        y = screen.height() - self.height - 60  # Changed from y = 120 to bottom-right
        self.setGeometry(x, y, self.width, self.height)

        # UI
        self.setup_ui()

        # Backdrop buffers
        self._backdrop_img = None
        self._need_backdrop_refresh = True
        self._avg_bg_color = QColor(255, 255, 255)
        self._noise_tile = self._make_noise_tile(64)

        # Throttled updater for backdrop capture on move/resize
        self._backdrop_timer = QTimer(self)
        self._backdrop_timer.setSingleShot(True)
        self._backdrop_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._backdrop_timer.timeout.connect(self._update_backdrop_now)

        # Opacity effect and animation
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        self.fade_animation = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self.fade_animation.setDuration(220)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_animation.finished.connect(self.close)

        # Timers
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.hide_timer.timeout.connect(self.start_fade_out)

        self.force_close_timer = QTimer(self)
        self.force_close_timer.setSingleShot(True)
        self.force_close_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.force_close_timer.timeout.connect(self.force_close)

    # ---------- lifecycle ----------

    def showEvent(self, event):
        # Backdrop ready right after show
        QTimer.singleShot(0, self._update_backdrop_now)

        # Auto-dismiss timers
        self.hide_timer.start(int(self.duration * 1000))
        self.force_close_timer.start(int(self.duration * 1000) + 1000)
        super().showEvent(event)

    def moveEvent(self, event):
        self._schedule_backdrop_update()
        super().moveEvent(event)

    def resizeEvent(self, event):
        self._schedule_backdrop_update()
        super().resizeEvent(event)

    # ---------- timers and closing ----------

    def start_fade_out(self):
        if self._opacity_effect.opacity() <= 0.01:
            self.close()
            return
        self.fade_animation.start()

    def force_close(self):
        if self.isVisible():
            self.hide()
            self.close()

    # ---------- UI ----------

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)  # Small padding for breathing room

        self.message_label = QLabel(self.message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                color: #121212;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 500;
                background: transparent;
                border: none;
                padding: 0px;
                letter-spacing: 0.1px;
                margin: 0px;
            }
        """)
        layout.addWidget(self.message_label)

    # ---------- backdrop blur & helpers ----------

    def _schedule_backdrop_update(self):
        self._need_backdrop_refresh = True
        self._backdrop_timer.start(16)  # ~60fps throttle during movement

    def _update_backdrop_now(self):
        try:
            geo = self.frameGeometry()
            x, y, w, h = int(geo.x()), int(geo.y()), int(geo.width()), int(geo.height())
            screen = QApplication.primaryScreen()
            if not screen or w <= 0 or h <= 0:
                return

            shot = screen.grabWindow(0, x, y, w, h)  # QPixmap under our window
            if shot.isNull():
                return

            dpr = shot.devicePixelRatio()
            size_px = shot.size()  # device pixels

            # Blur via graphics scene for quality
            scene = QGraphicsScene()
            item = QGraphicsPixmapItem(shot)
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(28.0)
            item.setGraphicsEffect(blur)
            scene.addItem(item)
            scene.setSceneRect(QRectF(0, 0, size_px.width(), size_px.height()))

            img = QImage(size_px, QImage.Format.Format_ARGB32_Premultiplied)
            img.setDevicePixelRatio(dpr)
            img.fill(0)
            p = QPainter(img)
            scene.render(p, target=QRectF(0, 0, size_px.width(), size_px.height()))
            p.end()

            # Brightness/contrast micro lift to avoid gray sludge on dark UIs
            self._backdrop_img = self._adjust_brightness_contrast(img, brightness=0.05, contrast=0.05)

            # Average color for faint tint
            self._avg_bg_color = self._compute_average_color(self._backdrop_img)

            self._need_backdrop_refresh = False
            self.update()
        except Exception:
            self._backdrop_img = None
            self._need_backdrop_refresh = False
            self.update()

    def _adjust_brightness_contrast(self, img: QImage, brightness=0.0, contrast=0.0) -> QImage:
        # brightness, contrast in [-1..+1] small values
        if img is None:
            return None
        out = QImage(img.size(), QImage.Format.Format_ARGB32_Premultiplied)
        out.setDevicePixelRatio(img.devicePixelRatio())
        w, h = img.width(), img.height()

        # Map factors
        b = int(255 * brightness)  # +/- 12 for 0.05
        c = contrast
        c_factor = (259 * (c * 255 + 255)) / (255 * (259 - c * 255)) if c != 0 else 1.0

        for y in range(h):
            src = img.scanLine(y)
            dst = out.scanLine(y)
            src_mv = memoryview(src)
            dst_mv = memoryview(dst)
            for x in range(0, w * 4, 4):
                b0 = src_mv[x + 0]
                g0 = src_mv[x + 1]
                r0 = src_mv[x + 2]
                a0 = src_mv[x + 3]

                r = clamp_byte((c_factor * (r0 - 128) + 128) + b)
                g = clamp_byte((c_factor * (g0 - 128) + 128) + b)
                bch = clamp_byte((c_factor * (b0 - 128) + 128) + b)

                dst_mv[x + 0] = bch
                dst_mv[x + 1] = g
                dst_mv[x + 2] = r
                dst_mv[x + 3] = a0
        return out

    def _compute_average_color(self, img: QImage) -> QColor:
        if img is None:
            return QColor(255, 255, 255)
        w, h = img.width(), img.height()
        step_x = max(1, w // 24)
        step_y = max(1, h // 12)
        rs = gs = bs = count = 0
        for y in range(0, h, step_y):
            line = memoryview(img.scanLine(y))
            for x in range(0, w, step_x):
                i = x * 4
                b0 = line[i + 0]
                g0 = line[i + 1]
                r0 = line[i + 2]
                rs += r0
                gs += g0
                bs += b0
                count += 1
        if count == 0:
            return QColor(255, 255, 255)
        return QColor(int(rs / count), int(gs / count), int(bs / count))

    def _make_noise_tile(self, size: int) -> QImage:
        img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(0)
        rng = random.Random(1337)
        for y in range(size):
            for x in range(size):
                v = rng.randint(118, 138)
                img.setPixel(x, y, QColor(v, v, v, 18).rgba())
        return img

    # ---------- painting ----------

    def paintEvent(self, event):
        if self._need_backdrop_refresh and not self._backdrop_timer.isActive():
            self._update_backdrop_now()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        radius = self.height // 2
        rect_w = self.width
        rect_h = self.height

        capsule = QPainterPath()
        capsule.addRoundedRect(0, 0, rect_w, rect_h, radius, radius)

        # Clip to capsule
        painter.save()
        painter.setClipPath(capsule)

        # 0) blurred backdrop
        if self._backdrop_img is not None:
            painter.drawImage(0, 0, self._backdrop_img)

        # 1) faint background-aware tint
        tint = QColor(self._avg_bg_color)
        tint.setRed(int((tint.red() + 255) / 2))
        tint.setGreen(int((tint.green() + 255) / 2))
        tint.setBlue(int((tint.blue() + 255) / 2))
        painter.fillPath(capsule, QBrush(QColor(tint.red(), tint.green(), tint.blue(), 36)))  # ~14%

        # 2) translucent white layer
        painter.fillPath(capsule, QBrush(QColor(255, 255, 255, 60)))  # ~24%

        # 3) static micro-noise
        if self._noise_tile is not None:
            brush = QBrush(QPixmap.fromImage(self._noise_tile))
            brush.setTransform(QTransform())
            painter.fillPath(capsule, brush)

        painter.restore()

        # Shadows: ambient + tiny contact
        ambient = QPainterPath()
        ambient.addRoundedRect(-3, -3, rect_w + 6, rect_h + 6, radius + 3, radius + 3)
        painter.fillPath(ambient, QBrush(QColor(0, 0, 0, 16)))

        contact = QPainterPath()
        contact.addRoundedRect(6, rect_h - 5, rect_w - 12, 3, 2, 2)
        painter.fillPath(contact, QBrush(QColor(0, 0, 0, 22)))

        # Directional highlights (assume light from top-left)
        top_grad = QLinearGradient(0, 0, 0, rect_h * 0.55)
        top_grad.setColorAt(0.0, QColor(255, 255, 255, 56))
        top_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        top_rect = QPainterPath()
        top_rect.addRoundedRect(2, 2, rect_w - 4, rect_h * 0.55, radius - 2, radius - 2)
        painter.fillPath(top_rect, QBrush(top_grad))

        hotspot = QRadialGradient(rect_w * 0.28, rect_h * 0.28, rect_h * 0.6)
        hotspot.setColorAt(0.0, QColor(255, 255, 255, 70))
        hotspot.setColorAt(0.35, QColor(255, 255, 255, 24))
        hotspot.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillPath(capsule, QBrush(hotspot))

        side = QPainterPath()
        side.addRoundedRect(3, 3, 3, rect_h - 6, 1, 1)
        painter.fillPath(side, QBrush(QColor(255, 255, 255, 26)))

        painter.setPen(QPen(QColor(255, 255, 255, 38), 1))
        painter.drawPath(capsule)

        halo = QPainterPath()
        halo.addRoundedRect(-1, -1, rect_w + 2, rect_h + 2, radius + 1, radius + 1)
        painter.fillPath(halo, QBrush(QColor(0, 0, 0, 12)))

    # ---------- external API ----------

    def show_notification(self):
        self.show()

    def closeEvent(self, event):
        try:
            self.hide_timer.stop()
            self.force_close_timer.stop()
            self.fade_animation.stop()
            self._backdrop_timer.stop()
        except Exception:
            pass
        self.deleteLater()
        event.accept()


class PyQt6NotificationSystem(QObject):
    """
    Thread-safe notification system.
    Call suggest_shortcut(...) from any thread; it queues to the GUI thread.
    """
    show_requested = pyqtSignal(str, str, float)  # action, shortcut, duration

    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications = []
        self.show_requested.connect(self._on_show_requested, type=Qt.ConnectionType.QueuedConnection)
        print("PyQt6 Notification system started")

    def suggest_shortcut(self, action, shortcut, duration=3.0):
        self.show_requested.emit(action, shortcut, float(duration))

    def _on_show_requested(self, action, shortcut, duration):
        try:
            message = f"Use {shortcut} for {action.lower()}"
            notification = LiquidGlassNotification(message, shortcut, duration)
            notification.show_notification()
            self.notifications.append(notification)  # keep reference
            self.notifications = [n for n in self.notifications if n.isVisible()]
            print(f"🔔 NOTIFICATION: {message}")
        except Exception as e:
            print(f"Error showing PyQt6 notification: {e}")
            print(f"🔔 NOTIFICATION: Use {shortcut} for {action.lower()}")

    def stop(self):
        for notification in self.notifications:
            if notification.isVisible():
                notification.close()
        self.notifications.clear()


# Demo and usage
if __name__ == "__main__":
    app = QApplication(sys.argv)

    notifier = PyQt6NotificationSystem()

    # Single example: call from GUI thread
    notifier.suggest_shortcut("Copy", "Ctrl+C", duration=3.0)

    # No second demo notification, no micro-scale animation
    QTimer.singleShot(6000, app.quit)
    sys.exit(app.exec())
