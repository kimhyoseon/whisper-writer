from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont, QPainterPath, QGuiApplication, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow


# Dark theme color palette
COLORS = {
    'bg': QColor(30, 30, 36),           # Main background
    'bg_secondary': QColor(40, 40, 48),  # Card/section background
    'border': QColor(55, 55, 65),        # Subtle border
    'text': QColor(230, 230, 235),       # Primary text
    'text_muted': QColor(140, 140, 155), # Secondary text
    'accent': QColor(99, 135, 255),      # Blue accent
    'accent_hover': QColor(120, 155, 255),
    'danger': QColor(255, 90, 90),       # Close button hover
    'success': QColor(80, 200, 120),     # Green for status
}

# Global stylesheet for dark theme widgets
DARK_STYLESHEET = """
    QWidget {
        color: #E6E6EB;
        font-family: 'Segoe UI', sans-serif;
    }
    QLabel {
        color: #E6E6EB;
        background: transparent;
    }
    QPushButton {
        background-color: #2D2D38;
        color: #E6E6EB;
        border: 1px solid #37374A;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 13px;
        font-family: 'Segoe UI', sans-serif;
    }
    QPushButton:hover {
        background-color: #3A3A4A;
        border-color: #6387FF;
    }
    QPushButton:pressed {
        background-color: #252532;
    }
    QLineEdit {
        background-color: #252532;
        color: #E6E6EB;
        border: 1px solid #37374A;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
        selection-background-color: #6387FF;
    }
    QLineEdit:focus {
        border-color: #6387FF;
    }
    QComboBox {
        background-color: #252532;
        color: #E6E6EB;
        border: 1px solid #37374A;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
    }
    QComboBox:hover {
        border-color: #6387FF;
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #8C8C9B;
        margin-right: 8px;
    }
    QComboBox QAbstractItemView {
        background-color: #252532;
        color: #E6E6EB;
        border: 1px solid #37374A;
        selection-background-color: #6387FF;
        outline: none;
    }
    QCheckBox {
        color: #E6E6EB;
        spacing: 8px;
        font-size: 13px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid #37374A;
        background-color: #252532;
    }
    QCheckBox::indicator:checked {
        background-color: #6387FF;
        border-color: #6387FF;
    }
    QCheckBox::indicator:hover {
        border-color: #6387FF;
    }
    QTabWidget::pane {
        border: 1px solid #37374A;
        border-radius: 8px;
        background-color: #1E1E24;
        top: -1px;
    }
    QTabBar::tab {
        background-color: #252532;
        color: #8C8C9B;
        border: 1px solid #37374A;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 8px 18px;
        margin-right: 2px;
        font-size: 13px;
    }
    QTabBar::tab:selected {
        background-color: #1E1E24;
        color: #E6E6EB;
        border-bottom: 2px solid #6387FF;
    }
    QTabBar::tab:hover:!selected {
        background-color: #2D2D38;
        color: #E6E6EB;
    }
    QScrollBar:vertical {
        background-color: #1E1E24;
        width: 8px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background-color: #37374A;
        border-radius: 4px;
        min-height: 30px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #50506A;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QToolButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 4px;
    }
    QToolButton:hover {
        background-color: #37374A;
    }
    QMessageBox {
        background-color: #1E1E24;
    }
    QMessageBox QLabel {
        color: #E6E6EB;
    }
"""


class BaseWindow(QMainWindow):
    def __init__(self, title, width, height):
        super().__init__()
        self.initUI(title, width, height)
        self.setWindowPosition()
        self.is_dragging = False

    def initUI(self, title, width, height):
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(width, height)
        self.setStyleSheet(DARK_STYLESHEET)

        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(20, 14, 20, 20)
        self.main_layout.setSpacing(8)

        # Title bar
        title_bar = QWidget()
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(4, 0, 0, 0)

        title_label = QLabel('WhisperWriter')
        title_label.setFont(QFont('Segoe UI', 11, QFont.DemiBold))
        title_label.setStyleSheet("color: #8C8C9B;")

        close_button = QPushButton('×')
        close_button.setFixedSize(28, 28)
        close_button.setFont(QFont('Segoe UI', 14))
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 14px;
                color: #8C8C9B;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 90, 90, 0.15);
                color: #FF5A5A;
            }
        """)
        close_button.clicked.connect(self.handleCloseButton)

        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch(1)
        title_bar_layout.addWidget(close_button)

        self.main_layout.addWidget(title_bar)
        self.setCentralWidget(self.main_widget)

    def setWindowPosition(self):
        center_point = QGuiApplication.primaryScreen().availableGeometry().center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def handleCloseButton(self):
        self.close()

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

    def paintEvent(self, event):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 16, 16)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Dark background
        painter.setBrush(QBrush(COLORS['bg']))
        painter.setPen(QPen(COLORS['border'], 1))
        painter.drawPath(path)
