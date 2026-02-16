import os
import sys
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, Qt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.base_window import BaseWindow

class MainWindow(BaseWindow):
    openSettings = pyqtSignal()
    startListening = pyqtSignal()
    closeApp = pyqtSignal()

    def __init__(self):
        super().__init__('WhisperWriter', 340, 200)
        self.initMainUI()

    def initMainUI(self):
        # Subtitle
        subtitle = QLabel('음성을 텍스트로 변환합니다')
        subtitle.setFont(QFont('Segoe UI', 10))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #8C8C9B; margin-bottom: 4px;")

        self.main_layout.addStretch(1)
        self.main_layout.addWidget(subtitle)

        # Buttons
        start_btn = QPushButton('시작')
        start_btn.setFont(QFont('Segoe UI', 11, QFont.DemiBold))
        start_btn.setFixedSize(130, 48)
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #6387FF;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #789BFF;
            }
            QPushButton:pressed {
                background-color: #4F6FE0;
            }
        """)
        start_btn.clicked.connect(self.startPressed)

        settings_btn = QPushButton('설정')
        settings_btn.setFont(QFont('Segoe UI', 11))
        settings_btn.setFixedSize(130, 48)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.clicked.connect(self.openSettings.emit)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch(1)
        button_layout.addWidget(start_btn)
        button_layout.addWidget(settings_btn)
        button_layout.addStretch(1)

        self.main_layout.addLayout(button_layout)
        self.main_layout.addStretch(1)

    def closeEvent(self, event):
        self.closeApp.emit()

    def startPressed(self):
        self.startListening.emit()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
