import os
import logging
from pathlib import Path
import numpy as np
from utils import ConfigManager

logger = logging.getLogger(__name__)


def validate_model_path(model_path):
    """Validate model path to prevent path traversal attacks."""
    if not model_path:
        return None

    path = Path(model_path).resolve()

    # Block UNC paths (network shares)
    if str(path).startswith('\\\\'):
        raise ValueError(f"네트워크 경로는 허용되지 않습니다: {model_path}")

    # Must exist and be a directory (CTranslate2 models are directories)
    if not path.is_dir():
        raise ValueError(f"모델 경로가 존재하지 않거나 디렉토리가 아닙니다: {model_path}")

    # Check that path contains expected model files
    expected_files = ['model.bin', 'config.json']
    found = any((path / f).is_file() for f in expected_files)
    if not found:
        raise ValueError(f"유효한 모델 디렉토리가 아닙니다 (model.bin 또는 config.json 필요): {model_path}")

    return str(path)


def create_local_model():
    """
    Create a local model using the faster-whisper library.
    Imports are deferred to avoid loading torch (~164MB) and faster_whisper until needed.
    """
    from faster_whisper import WhisperModel

    ConfigManager.console_print('Creating local model...')
    local_model_options = ConfigManager.get_config_section('model_options')['local']
    compute_type = local_model_options['compute_type']
    model_path = local_model_options.get('model_path')

    if compute_type == 'int8':
        device = 'cpu'
        ConfigManager.console_print('Using int8 quantization, forcing CPU usage.')
    else:
        device = local_model_options['device']

    try:
        if model_path:
            model_path = validate_model_path(model_path)
            ConfigManager.console_print(f'Loading model from: {model_path}')
            model = WhisperModel(model_path,
                                 device=device,
                                 compute_type=compute_type,
                                 download_root=None)
        else:
            model = WhisperModel(local_model_options['model'],
                                 device=device,
                                 compute_type=compute_type)
    except Exception as e:
        ConfigManager.console_print(f'Error initializing WhisperModel: {e}')
        ConfigManager.console_print('Falling back to CPU.')
        model = WhisperModel(model_path or local_model_options['model'],
                             device='cpu',
                             compute_type=compute_type,
                             download_root=None if model_path else None)

    ConfigManager.console_print('Local model created.')
    return model

def transcribe_local(audio_data, local_model=None):
    """
    Transcribe an audio file using a local model.
    """
    if not local_model:
        local_model = create_local_model()
    model_options = ConfigManager.get_config_section('model_options')

    # Convert int16 to float32
    audio_data_float = audio_data.astype(np.float32) / 32768.0

    response = local_model.transcribe(audio=audio_data_float,
                                      language=model_options['common']['language'],
                                      initial_prompt=model_options['common']['initial_prompt'],
                                      condition_on_previous_text=model_options['local']['condition_on_previous_text'],
                                      temperature=model_options['common']['temperature'],
                                      vad_filter=model_options['local']['vad_filter'],
                                      beam_size=model_options['local'].get('beam_size', 5),)
    return ''.join([segment.text for segment in list(response[0])])

def transcribe_api(audio_data):
    """
    Transcribe an audio file using the OpenAI API.
    Imports deferred to avoid loading openai (~35MB) when using local model.
    """
    import io
    import soundfile as sf
    from openai import OpenAI

    import keyring

    model_options = ConfigManager.get_config_section('model_options')
    api_key = keyring.get_password('whisperwriter', 'openai_api_key') or os.getenv('OPENAI_API_KEY')
    base_url = model_options['api']['base_url'] or 'https://api.openai.com/v1'

    # Validate base_url uses HTTPS for remote servers
    from urllib.parse import urlparse
    parsed = urlparse(base_url)
    if parsed.hostname not in ('localhost', '127.0.0.1') and parsed.scheme != 'https':
        raise ValueError("API 서버 주소는 HTTPS만 허용됩니다.")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    byte_io = io.BytesIO()
    sample_rate = ConfigManager.get_config_section('recording_options').get('sample_rate') or 16000
    sf.write(byte_io, audio_data, sample_rate, format='wav')
    byte_io.seek(0)

    response = client.audio.transcriptions.create(
        model=model_options['api']['model'],
        file=('audio.wav', byte_io, 'audio/wav'),
        language=model_options['common']['language'],
        prompt=model_options['common']['initial_prompt'],
        temperature=model_options['common']['temperature'],
    )
    return response.text

def post_process_transcription(transcription):
    """
    Apply post-processing to the transcription.
    """
    transcription = transcription.strip()
    if not transcription:
        return ''
    post_processing = ConfigManager.get_config_section('post_processing')
    if post_processing['remove_trailing_period'] and transcription.endswith('.'):
        transcription = transcription[:-1]
    if post_processing['add_trailing_space']:
        transcription += ' '
    if post_processing['remove_capitalization']:
        transcription = transcription.lower()

    return transcription

def transcribe(audio_data, local_model=None):
    """
    Transcribe audio date using the OpenAI API or a local model, depending on config.
    """
    if audio_data is None:
        return ''

    if ConfigManager.get_config_value('model_options', 'use_api'):
        transcription = transcribe_api(audio_data)
    else:
        transcription = transcribe_local(audio_data, local_model)

    return post_process_transcription(transcription)

