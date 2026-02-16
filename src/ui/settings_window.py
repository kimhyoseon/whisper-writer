import os
import sys
import keyring
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QMessageBox, QTabWidget, QWidget, QSizePolicy, QSpacerItem, QToolButton, QStyle, QFileDialog
)
from PyQt5.QtCore import Qt, QCoreApplication, QProcess, pyqtSignal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.base_window import BaseWindow
from utils import ConfigManager

KEYRING_SERVICE = 'whisperwriter'
KEYRING_API_KEY = 'openai_api_key'

# Korean labels for settings
LABEL_MAP = {
    # model_options
    'use_api': '온라인 API 사용',
    'language': '인식 언어',
    'temperature': '결과 다양성',
    'initial_prompt': '인식 힌트 문구',
    'model': '음성 인식 모델',
    'base_url': 'API 서버 주소',
    'api_key': 'API 키',
    'device': '처리 장치',
    'compute_type': '처리 방식',
    'condition_on_previous_text': '이전 결과 참고',
    'vad_filter': '무음 자동 감지',
    'beam_size': '인식 정밀도',
    'model_path': '모델 파일 위치',
    # recording_options
    'activation_key': '시작 단축키',
    'input_backend': '키 감지 방식',
    'recording_mode': '녹음 방식',
    'sound_device': '마이크 선택',
    'sample_rate': '음질 (Hz)',
    'silence_duration': '말 끝난 후 대기 (ms)',
    'min_duration': '최소 녹음 길이 (ms)',
    # post_processing
    'writing_key_press_delay': '타이핑 속도 (초)',
    'remove_trailing_period': '마침표 자동 제거',
    'add_trailing_space': '끝에 공백 추가',
    'remove_capitalization': '모두 소문자로',
    'input_method': '타이핑 방식',
    # misc
    'print_to_terminal': '터미널에 로그 표시',
    'hide_status_window': '상태 표시 숨기기',
    'noise_on_completion': '완료 시 소리 알림',
}

# Korean tab names
TAB_NAME_MAP = {
    'model_options': '음성 인식',
    'recording_options': '녹음',
    'post_processing': '텍스트 변환',
    'misc': '기타',
}

# Korean descriptions for settings
DESC_MAP = {
    'use_api': '켜면 인터넷을 통해 OpenAI 서버로 음성을 보내 변환합니다. 끄면 내 컴퓨터에서 직접 변환합니다.',
    'language': '어떤 언어를 인식할지 설정합니다. ko=한국어, en=영어, ja=일본어',
    'temperature': '0에 가까울수록 정확한 결과, 높을수록 다양한 결과를 냅니다. 보통 0.0이 좋습니다.',
    'initial_prompt': '음성 인식 전에 참고할 문구입니다. 특정 용어나 문맥을 미리 알려줄 수 있습니다. 보통 비워두세요.',
    'model': '음성을 텍스트로 바꾸는 AI 모델을 선택합니다.',
    'base_url': 'API 서버 주소입니다. OpenAI 기본값을 그대로 사용하세요.',
    'api_key': 'OpenAI에서 발급받은 API 키입니다. 온라인 모드 사용 시 필요합니다.',
    'device': '음성 인식을 어디서 처리할지 선택합니다. cpu=일반 처리, cuda=그래픽카드, auto=자동',
    'compute_type': '처리 속도와 메모리 사이의 균형입니다. int8=가볍고 빠름, float32=정밀하지만 무거움',
    'condition_on_previous_text': '켜면 이전에 인식한 내용을 참고해서 다음 인식을 합니다. 끄는 것을 권장합니다.',
    'vad_filter': '켜면 음성이 없는 무음 구간을 자동으로 건너뜁니다.',
    'beam_size': '숫자가 클수록 정확하지만 느려집니다. 기본값 5를 권장합니다.',
    'model_path': '모델 파일이 저장된 폴더 경로입니다. 비워두면 자동으로 다운로드합니다.',
    'activation_key': '이 키 조합을 누르면 녹음이 시작됩니다. 예: ctrl+shift+space',
    'input_backend': '키보드 입력을 감지하는 방식입니다. auto로 두면 자동으로 선택됩니다.',
    'recording_mode': '녹음 방식을 선택합니다.\n- continuous: 계속 녹음 (단축키로 중지)\n- voice_activity_detection: 말이 끝나면 자동 중지\n- press_to_toggle: 단축키로 시작/중지\n- hold_to_record: 단축키 누르고 있는 동안만 녹음',
    'sound_device': '사용할 마이크를 선택합니다. 비워두면 기본 마이크를 사용합니다.',
    'sample_rate': '녹음 품질입니다. 16000이 기본값이며 대부분의 경우 충분합니다.',
    'silence_duration': '말이 끝난 후 이 시간(밀리초)만큼 기다렸다가 녹음을 중지합니다. 1500 = 1.5초',
    'min_duration': '이 시간(밀리초)보다 짧은 녹음은 무시합니다. 실수로 눌렀을 때 방지용입니다.',
    'writing_key_press_delay': '변환된 텍스트를 입력할 때 글자 사이의 간격(초)입니다. 너무 빠르면 일부 프로그램에서 누락될 수 있습니다.',
    'remove_trailing_period': '켜면 변환 결과 끝의 마침표(.)를 자동으로 제거합니다.',
    'add_trailing_space': '켜면 변환 결과 끝에 공백을 추가하여 다음 단어와 자연스럽게 이어집니다.',
    'remove_capitalization': '켜면 영문을 모두 소문자로 변환합니다.',
    'input_method': '변환된 텍스트를 입력하는 방식입니다. Windows에서는 pynput을 사용하세요.',
    'print_to_terminal': '켜면 프로그램 실행 상태와 변환 결과를 터미널 창에 표시합니다.',
    'hide_status_window': '켜면 녹음/변환 중 화면 하단에 나타나는 상태 표시를 숨깁니다.',
    'noise_on_completion': '켜면 음성 변환이 완료될 때 알림 소리를 재생합니다.',
}


class SettingsWindow(BaseWindow):
    settings_closed = pyqtSignal()
    settings_saved = pyqtSignal()

    def __init__(self):
        super().__init__('설정', 700, 700)
        self.schema = ConfigManager.get_schema()
        self.init_settings_ui()

    def init_settings_ui(self):
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        self.create_tabs()
        self.create_buttons()

        self.use_api_checkbox = self.findChild(QCheckBox, 'model_options_use_api_input')
        if self.use_api_checkbox:
            self.use_api_checkbox.stateChanged.connect(lambda: self.toggle_api_local_options(self.use_api_checkbox.isChecked()))
            self.toggle_api_local_options(self.use_api_checkbox.isChecked())

    def create_tabs(self):
        for category, settings in self.schema.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab.setLayout(tab_layout)
            tab_name = TAB_NAME_MAP.get(category, category.replace('_', ' ').capitalize())
            self.tabs.addTab(tab, tab_name)

            self.create_settings_widgets(tab_layout, category, settings)
            tab_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def create_settings_widgets(self, layout, category, settings):
        for sub_category, sub_settings in settings.items():
            if isinstance(sub_settings, dict) and 'value' in sub_settings:
                self.add_setting_widget(layout, sub_category, sub_settings, category)
            else:
                for key, meta in sub_settings.items():
                    self.add_setting_widget(layout, key, meta, category, sub_category)

    def create_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        reset_button = QPushButton('초기화')
        reset_button.setCursor(Qt.PointingHandCursor)
        reset_button.clicked.connect(self.reset_settings)

        save_button = QPushButton('저장')
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #6387FF;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #789BFF;
            }
            QPushButton:pressed {
                background-color: #4F6FE0;
            }
        """)
        save_button.clicked.connect(self.save_settings)

        button_layout.addWidget(reset_button)
        button_layout.addWidget(save_button)
        self.main_layout.addLayout(button_layout)

    def add_setting_widget(self, layout, key, meta, category, sub_category=None):
        item_layout = QHBoxLayout()
        item_layout.setSpacing(8)

        label_text = LABEL_MAP.get(key, key.replace('_', ' ').capitalize())
        label = QLabel(f"{label_text}:")
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        widget = self.create_widget_for_type(key, meta, category, sub_category)
        if not widget:
            return

        desc_text = DESC_MAP.get(key, meta.get('description', ''))
        help_button = self.create_help_button(desc_text)

        item_layout.addWidget(label)
        if isinstance(widget, QWidget):
            item_layout.addWidget(widget)
        else:
            item_layout.addLayout(widget)
        item_layout.addWidget(help_button)
        layout.addLayout(item_layout)

        widget_name = f"{category}_{sub_category}_{key}_input" if sub_category else f"{category}_{key}_input"
        label_name = f"{category}_{sub_category}_{key}_label" if sub_category else f"{category}_{key}_label"
        help_name = f"{category}_{sub_category}_{key}_help" if sub_category else f"{category}_{key}_help"

        label.setObjectName(label_name)
        help_button.setObjectName(help_name)

        if isinstance(widget, QWidget):
            widget.setObjectName(widget_name)
        else:
            line_edit = widget.itemAt(0).widget()
            if isinstance(line_edit, QLineEdit):
                line_edit.setObjectName(widget_name)

    def create_widget_for_type(self, key, meta, category, sub_category):
        meta_type = meta.get('type')
        current_value = self.get_config_value(category, sub_category, key, meta)

        if meta_type == 'bool':
            return self.create_checkbox(current_value, key)
        elif meta_type == 'str' and 'options' in meta:
            return self.create_combobox(current_value, meta['options'])
        elif meta_type == 'str':
            return self.create_line_edit(current_value, key)
        elif meta_type in ['int', 'float']:
            return self.create_line_edit(str(current_value))
        return None

    def create_checkbox(self, value, key):
        widget = QCheckBox()
        widget.setChecked(value)
        widget.setCursor(Qt.PointingHandCursor)
        if key == 'use_api':
            widget.setObjectName('model_options_use_api_input')
        return widget

    def create_combobox(self, value, options):
        widget = QComboBox()
        widget.addItems(options)
        widget.setCurrentText(value)
        widget.setCursor(Qt.PointingHandCursor)
        return widget

    def create_line_edit(self, value, key=None):
        widget = QLineEdit(value)
        if key == 'api_key':
            widget.setEchoMode(QLineEdit.Password)
            stored_key = keyring.get_password(KEYRING_SERVICE, KEYRING_API_KEY)
            widget.setText(stored_key or value or '')
        elif key == 'model_path':
            layout = QHBoxLayout()
            layout.addWidget(widget)
            browse_button = QPushButton('찾아보기')
            browse_button.setCursor(Qt.PointingHandCursor)
            browse_button.clicked.connect(lambda: self.browse_model_path(widget))
            layout.addWidget(browse_button)
            layout.setContentsMargins(0, 0, 0, 0)
            container = QWidget()
            container.setLayout(layout)
            return container
        return widget

    def create_help_button(self, description):
        help_button = QToolButton()
        help_button.setText('?')
        help_button.setFixedSize(24, 24)
        help_button.setStyleSheet("""
            QToolButton {
                color: #8C8C9B;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #37374A;
                border-radius: 12px;
                background: transparent;
            }
            QToolButton:hover {
                color: #E6E6EB;
                border-color: #6387FF;
                background-color: rgba(99, 135, 255, 0.1);
            }
        """)
        help_button.setCursor(Qt.PointingHandCursor)
        help_button.setToolTip(description)
        help_button.clicked.connect(lambda: self.show_description(description))
        return help_button

    def get_config_value(self, category, sub_category, key, meta):
        if sub_category:
            return ConfigManager.get_config_value(category, sub_category, key) or meta['value']
        return ConfigManager.get_config_value(category, key) or meta['value']

    def browse_model_path(self, widget):
        file_path, _ = QFileDialog.getOpenFileName(self, "Whisper 모델 파일 선택", "", "모델 파일 (*.bin);;모든 파일 (*)")
        if file_path:
            widget.setText(file_path)

    def show_description(self, description):
        QMessageBox.information(self, '설명', description)

    def save_settings(self):
        self.iterate_settings(self.save_setting)

        # Store API key securely via OS credential manager
        api_key = ConfigManager.get_config_value('model_options', 'api', 'api_key') or ''
        if api_key:
            keyring.set_password(KEYRING_SERVICE, KEYRING_API_KEY, api_key)
        else:
            try:
                keyring.delete_password(KEYRING_SERVICE, KEYRING_API_KEY)
            except keyring.errors.PasswordDeleteError:
                pass

        # Remove API key from config before saving to disk
        ConfigManager.set_config_value(None, 'model_options', 'api', 'api_key')

        ConfigManager.save_config()
        QMessageBox.information(self, '설정 저장', '설정이 저장되었습니다. 앱을 재시작합니다.')
        self.settings_saved.emit()
        self.hide()

    def save_setting(self, widget, category, sub_category, key, meta):
        value = self.get_widget_value_typed(widget, meta.get('type'))
        if sub_category:
            ConfigManager.set_config_value(value, category, sub_category, key)
        else:
            ConfigManager.set_config_value(value, category, key)

    def reset_settings(self):
        ConfigManager.reload_config()
        self.update_widgets_from_config()

    def update_widgets_from_config(self):
        self.iterate_settings(self.update_widget_value)

    def update_widget_value(self, widget, category, sub_category, key, meta):
        if sub_category:
            config_value = ConfigManager.get_config_value(category, sub_category, key)
        else:
            config_value = ConfigManager.get_config_value(category, key)

        self.set_widget_value(widget, config_value, meta.get('type'))

    def set_widget_value(self, widget, value, value_type):
        if isinstance(widget, QCheckBox):
            widget.setChecked(value)
        elif isinstance(widget, QComboBox):
            widget.setCurrentText(value)
        elif isinstance(widget, QLineEdit):
            widget.setText(str(value) if value is not None else '')
        elif isinstance(widget, QWidget) and widget.layout():
            line_edit = widget.layout().itemAt(0).widget()
            if isinstance(line_edit, QLineEdit):
                line_edit.setText(str(value) if value is not None else '')

    def get_widget_value_typed(self, widget, value_type):
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QComboBox):
            return widget.currentText() or None
        elif isinstance(widget, QLineEdit):
            text = widget.text()
            if value_type == 'int':
                if not text:
                    return None
                try:
                    value = int(text)
                    if value < 0 or value > 1000000:
                        QMessageBox.warning(self, '입력 오류', f'유효한 범위의 정수를 입력해 주세요. (0~1,000,000)')
                        return None
                    return value
                except ValueError:
                    QMessageBox.warning(self, '입력 오류', f'숫자를 입력해 주세요: "{text}"')
                    return None
            elif value_type == 'float':
                if not text:
                    return None
                try:
                    value = float(text)
                    if value < 0 or value > 1000:
                        QMessageBox.warning(self, '입력 오류', f'유효한 범위의 숫자를 입력해 주세요. (0~1,000)')
                        return None
                    return value
                except ValueError:
                    QMessageBox.warning(self, '입력 오류', f'숫자를 입력해 주세요: "{text}"')
                    return None
            else:
                return text or None
        elif isinstance(widget, QWidget) and widget.layout():
            line_edit = widget.layout().itemAt(0).widget()
            if isinstance(line_edit, QLineEdit):
                return line_edit.text() or None
        return None

    def toggle_api_local_options(self, use_api):
        self.iterate_settings(lambda w, c, s, k, m: self.toggle_widget_visibility(w, c, s, k, use_api))

    def toggle_widget_visibility(self, widget, category, sub_category, key, use_api):
        if sub_category in ['api', 'local']:
            widget.setVisible(use_api if sub_category == 'api' else not use_api)

            label = self.findChild(QLabel, f"{category}_{sub_category}_{key}_label")
            help_button = self.findChild(QToolButton, f"{category}_{sub_category}_{key}_help")

            if label:
                label.setVisible(use_api if sub_category == 'api' else not use_api)
            if help_button:
                help_button.setVisible(use_api if sub_category == 'api' else not use_api)

    def iterate_settings(self, func):
        for category, settings in self.schema.items():
            for sub_category, sub_settings in settings.items():
                if isinstance(sub_settings, dict) and 'value' in sub_settings:
                    widget = self.findChild(QWidget, f"{category}_{sub_category}_input")
                    if widget:
                        func(widget, category, None, sub_category, sub_settings)
                else:
                    for key, meta in sub_settings.items():
                        widget = self.findChild(QWidget, f"{category}_{sub_category}_{key}_input")
                        if widget:
                            func(widget, category, sub_category, key, meta)

    def closeEvent(self, event):
        event.ignore()
        reply = QMessageBox.question(
            self,
            '저장하지 않고 닫기',
            '저장하지 않고 닫으시겠습니까?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            ConfigManager.reload_config()
            self.update_widgets_from_config()
            self.settings_closed.emit()
            self.hide()
