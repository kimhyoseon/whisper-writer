# <img src="./assets/ww-logo.png" alt="WhisperWriter 아이콘" width="25" height="25"> WhisperWriter (한국어 음성 입력기)

마이크로 말하면 자동으로 글자로 바꿔주는 프로그램입니다.
키보드 단축키를 누르고 말하면, 현재 열려있는 창에 바로 텍스트가 입력됩니다.

한국어 음성인식에 최적화된 Whisper 모델(`whisper-small-komixv2`)을 기본으로 사용합니다.

<p align="center">
    <img src="./assets/ww-demo-image-02.gif" alt="WhisperWriter 데모" width="340" height="136">
</p>

---

## 어떻게 동작하나요?

1. 프로그램을 실행하면 시스템 트레이(작업표시줄 오른쪽)에 아이콘이 생깁니다
2. `Ctrl + Shift + Space`를 누르면 녹음이 시작됩니다
3. 말을 하면 자동으로 텍스트로 변환됩니다
4. 변환된 텍스트가 현재 커서 위치에 자동 입력됩니다

---

## 설치 방법

### 1단계: 필요한 프로그램 설치

아래 두 가지를 먼저 설치해주세요:

- **Python 3.11** : https://www.python.org/downloads/release/python-3119/
  - 설치할 때 **"Add Python to PATH"에 반드시 체크**해주세요
- **Git** : https://git-scm.com/downloads

### 2단계: 프로젝트 다운로드

윈도우 검색에서 "명령 프롬프트" 또는 "cmd"를 검색해서 열고, 아래 명령어를 한 줄씩 입력해주세요:

```
git clone https://github.com/kimhyoseon/whisper-writer.git
cd whisper-writer
```

### 3단계: 가상환경 만들기

```
python -m venv venv
venv\Scripts\activate
```

> 위 명령어를 실행하면 프롬프트 앞에 `(venv)`가 표시됩니다. 이게 보여야 정상입니다.

### 4단계: 필요한 패키지 설치

```
pip install -r requirements.txt
```

> 설치에 몇 분 정도 걸릴 수 있습니다. 끝날 때까지 기다려주세요.

### 5단계: 프로그램 실행

```
python run.py
```

처음 실행하면 설정 화면이 나타납니다. 설정을 저장하면 프로그램이 시작됩니다.

### 6단계: 바로가기 및 자동 실행 등록 (선택)

아래 명령어를 실행하면 **바탕화면 바로가기**가 생기고, **컴퓨터를 켤 때 자동으로 실행**됩니다:

```
python install.py
```

설치 후에는 바탕화면의 **WhisperWriter** 아이콘을 더블클릭하면 바로 실행됩니다.

> 되돌리고 싶으면 `python install.py --uninstall`을 실행하세요. 바로가기와 자동 실행이 제거됩니다.

---

## 사용 방법

### 기본 사용법

1. `python run.py`로 프로그램을 실행합니다
2. 글자를 입력하고 싶은 곳(메모장, 브라우저, 카카오톡 등)을 클릭합니다
3. **`Ctrl + Shift + Space`** 를 누릅니다
4. 마이크에 대고 말합니다
5. 말을 멈추면 자동으로 텍스트가 입력됩니다

### 녹음 모드 설명

| 모드 | 동작 방식 |
|------|-----------|
| **continuous** (기본) | 말을 멈추면 텍스트 입력 후 자동으로 다시 녹음 시작. 단축키를 다시 누르면 중지 |
| **voice_activity_detection** | 말을 멈추면 텍스트 입력 후 녹음 중지. 다시 단축키를 눌러야 녹음 시작 |
| **press_to_toggle** | 단축키를 누르면 녹음 시작, 다시 누르면 녹음 중지 |
| **hold_to_record** | 단축키를 누르고 있는 동안만 녹음, 손을 떼면 중지 |

### 설정 변경

시스템 트레이의 아이콘을 우클릭하면 **"설정"** 메뉴가 나타납니다.

<p align="center">
    <img src="./assets/ww-settings-demo.gif" alt="설정 화면" width="350" height="350">
</p>

---

## 주요 설정 안내

### 음성인식 모델

기본값으로 한국어에 최적화된 로컬 모델이 설정되어 있어 별도 설정 없이 바로 사용 가능합니다.

| 설정 | 기본값 | 설명 |
|------|--------|------|
| use_api | `false` | `false` = 내 컴퓨터에서 처리 (무료), `true` = OpenAI API 사용 (유료) |
| model | `seastar105/whisper-small-komixv2` | 한국어 최적화 모델. 더 정확한 인식을 원하면 `seastar105/whisper-medium-komixv2` 선택 |
| device | `auto` | 자동으로 GPU/CPU 선택. NVIDIA GPU가 있으면 `cuda` 선택 시 더 빠름 |

### 녹음 설정

| 설정 | 기본값 | 설명 |
|------|--------|------|
| activation_key | `ctrl+shift+space` | 녹음 시작/중지 단축키 |
| recording_mode | `continuous` | 위의 녹음 모드 설명 참고 |
| silence_duration | `900` | 말을 멈추고 몇 밀리초 후에 녹음을 중지할지 (0.9초) |

---

## NVIDIA GPU가 있는 경우 (선택사항)

NVIDIA GPU가 있으면 음성인식 속도가 훨씬 빨라집니다. GPU를 사용하려면:

1. [CUDA Toolkit 12](https://developer.nvidia.com/cuda-downloads)를 설치합니다
2. [cuDNN 8 for CUDA 12](https://developer.nvidia.com/cudnn)를 설치합니다
3. 설정에서 device를 `cuda`로 변경합니다

> GPU가 없어도 CPU로 정상 동작합니다. 다만 약간 느릴 수 있습니다.

---

## 문제 해결

### "python을 찾을 수 없습니다"
- Python 설치 시 **"Add Python to PATH"** 를 체크했는지 확인하세요
- 명령 프롬프트를 닫고 다시 열어보세요

### 마이크가 동작하지 않습니다
- Windows 설정 > 개인 정보 > 마이크에서 마이크 접근이 허용되어 있는지 확인하세요
- 설정에서 `sound_device`를 올바른 마이크 번호로 지정해보세요
- 마이크 번호 확인 방법: `python -m sounddevice`

### 한국어 인식이 잘 안 됩니다
- 설정에서 language를 `ko`로 지정해보세요
- 모델을 `seastar105/whisper-medium-komixv2`로 변경하면 더 정확합니다 (대신 더 느림)

### 프로그램이 멈춥니다
- 첫 실행 시 모델을 다운로드하므로 시간이 걸릴 수 있습니다. 잠시 기다려주세요

---

## 다시 실행하기

`python install.py`를 실행했다면 **바탕화면 아이콘**을 더블클릭하면 됩니다.
컴퓨터를 켜면 자동으로 실행되므로 별도 조작이 필요 없습니다.

설치 스크립트를 실행하지 않은 경우, 명령 프롬프트에서:

```
cd whisper-writer
venv\Scripts\activate
python run.py
```

---

## 원본 프로젝트

이 프로젝트는 [savbell/whisper-writer](https://github.com/savbell/whisper-writer)를 기반으로 한국어 사용에 맞게 수정한 버전입니다.

## 라이선스

GNU General Public License. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.
