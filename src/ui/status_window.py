import sys
import os
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPainter, QPainterPath, QBrush, QPen
from PyQt5.QtWidgets import QApplication, QLabel, QHBoxLayout, QGraphicsOpacityEffect, QWidget
from PyQt5.QtCore import QRectF

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.base_window import COLORS


class StatusWindow(QWidget):
    statusSignal = pyqtSignal(str)
    closeSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initStatusUI()
        self.statusSignal.connect(self.updateStatus)
        self.is_dragging = False

    def initStatusUI(self):
        self.setWindowTitle('WhisperWriter Status')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(220, 56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(10)

        # Status dot (colored circle indicator)
        self.dot_label = QLabel()
        self.dot_label.setFixedSize(12, 12)
        self.dot_label.setStyleSheet("""
            background-color: #FF5A5A;
            border-radius: 6px;
        """)

        self.status_label = QLabel('녹음 중...')
        self.status_label.setFont(QFont('Segoe UI', 11, QFont.DemiBold))
        self.status_label.setStyleSheet("color: #E6E6EB; background: transparent;")

        layout.addStretch(1)
        layout.addWidget(self.dot_label)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

    def paintEvent(self, event):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 28, 28)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(30, 30, 36, 240)))
        painter.setPen(QPen(QColor(55, 55, 65), 1))
        painter.drawPath(path)

    def show(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = screen_geometry.height() - self.height() - 80
        self.move(x, y)
        super().show()

    def closeEvent(self, event):
        self.closeSignal.emit()
        super().closeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_dragging:
            self.move(event.globalPos() - self.start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    @pyqtSlot(str)
    def updateStatus(self, status):
        if status == 'recording':
            self.dot_label.setStyleSheet("""
                background-color: #FF5A5A;
                border-radius: 6px;
            """)
            self.status_label.setText('녹음 중...')
            self.show()
        elif status == 'transcribing':
            self.dot_label.setStyleSheet("""
                background-color: #6387FF;
                border-radius: 6px;
            """)
            self.status_label.setText('변환 중...')

        if status in ('idle', 'error', 'cancel'):
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    status_window = StatusWindow()
    status_window.show()

    QTimer.singleShot(3000, lambda: status_window.statusSignal.emit('transcribing'))
    QTimer.singleShot(6000, lambda: status_window.statusSignal.emit('idle'))

    sys.exit(app.exec_())
