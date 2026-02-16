"""
WhisperWriter 설치 스크립트
- 바탕화면 바로가기 생성
- 시작 프로그램 등록 (Windows 시작 시 자동 실행)
"""

import os
import sys
import winreg

def get_project_dir():
    return os.path.dirname(os.path.abspath(__file__))

def get_python_exe():
    """가상환경의 pythonw.exe 경로를 반환 (콘솔창 없이 실행)"""
    venv_pythonw = os.path.join(get_project_dir(), 'venv', 'Scripts', 'pythonw.exe')
    if os.path.exists(venv_pythonw):
        return venv_pythonw
    venv_python = os.path.join(get_project_dir(), 'venv', 'Scripts', 'python.exe')
    if os.path.exists(venv_python):
        return venv_python
    return sys.executable

def create_shortcut(shortcut_path, target, arguments, working_dir, icon_path, description):
    """Windows 바로가기(.lnk) 파일 생성"""
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.Arguments = arguments
        shortcut.WorkingDirectory = working_dir
        shortcut.IconLocation = icon_path
        shortcut.Description = description
        shortcut.save()
        return True
    except ImportError:
        return create_shortcut_vbs(shortcut_path, target, arguments, working_dir, icon_path, description)

def create_shortcut_vbs(shortcut_path, target, arguments, working_dir, icon_path, description):
    """pywin32가 없을 때 VBScript로 바로가기 생성"""
    import subprocess
    import tempfile

    vbs = f'''Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortCut("{shortcut_path}")
oLink.TargetPath = "{target}"
oLink.Arguments = "{arguments}"
oLink.WorkingDirectory = "{working_dir}"
oLink.IconLocation = "{icon_path}"
oLink.Description = "{description}"
oLink.Save
'''
    vbs_path = os.path.join(tempfile.gettempdir(), 'create_shortcut.vbs')
    with open(vbs_path, 'w', encoding='utf-8') as f:
        f.write(vbs)

    result = subprocess.run(['cscript', '//nologo', vbs_path], capture_output=True, text=True)
    os.remove(vbs_path)
    return result.returncode == 0

def add_to_startup(name, command):
    """시작 프로그램에 등록 (레지스트리)"""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"  [실패] 시작 프로그램 등록 오류: {e}")
        return False

def remove_from_startup(name):
    """시작 프로그램에서 제거"""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return True
    except Exception:
        return False

def install():
    project_dir = get_project_dir()
    python_exe = get_python_exe()
    run_script = os.path.join(project_dir, 'run.py')
    icon_path = os.path.join(project_dir, 'assets', 'ww-logo.ico')

    print("=" * 50)
    print("  WhisperWriter 설치")
    print("=" * 50)
    print()

    # 1. 바탕화면 바로가기
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop, "WhisperWriter.lnk")

    print("[1/2] 바탕화면 바로가기 생성 중...")
    if create_shortcut(shortcut_path, python_exe, f'"{run_script}"', project_dir, icon_path, "WhisperWriter - 음성 입력기"):
        print(f"  [완료] {shortcut_path}")
    else:
        print("  [실패] 바로가기를 만들지 못했습니다.")

    # 2. 시작 프로그램 등록
    startup_command = f'"{python_exe}" "{run_script}"'

    print("[2/2] 시작 프로그램 등록 중...")
    if add_to_startup("WhisperWriter", startup_command):
        print("  [완료] Windows 시작 시 자동으로 실행됩니다.")

    print()
    print("=" * 50)
    print("  설치 완료!")
    print("  바탕화면의 WhisperWriter 아이콘을 더블클릭하면 실행됩니다.")
    print("=" * 50)

def uninstall():
    print("=" * 50)
    print("  WhisperWriter 제거")
    print("=" * 50)
    print()

    # 1. 바탕화면 바로가기 삭제
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop, "WhisperWriter.lnk")

    print("[1/2] 바탕화면 바로가기 삭제 중...")
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
        print("  [완료] 바로가기 삭제됨")
    else:
        print("  [건너뜀] 바로가기가 없습니다")

    # 2. 시작 프로그램 제거
    print("[2/2] 시작 프로그램 제거 중...")
    if remove_from_startup("WhisperWriter"):
        print("  [완료] 시작 프로그램에서 제거됨")

    print()
    print("=" * 50)
    print("  제거 완료!")
    print("=" * 50)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--uninstall':
        uninstall()
    else:
        install()
