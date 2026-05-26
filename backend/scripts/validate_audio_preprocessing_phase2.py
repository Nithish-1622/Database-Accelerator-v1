import math
import os
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database_accelerator.settings')
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import django
django.setup()

from database_accelerator.apps.audio_dataset_engine.services.preprocessing_service import AudioPreprocessingService


def write_test_wav(path: Path, sample_rate: int = 16000) -> Path:
    tone_seconds = 2.0
    silence_seconds = 0.5
    t = np.linspace(0.0, tone_seconds, int(sample_rate * tone_seconds), endpoint=False)
    tone = 0.18 * np.sin(2.0 * math.pi * 440.0 * t)
    silence = np.zeros(int(sample_rate * silence_seconds), dtype=np.float32)
    waveform = np.concatenate([silence, tone, silence, tone])
    pcm = (np.clip(waveform, -1.0, 1.0) * 32767.0).astype(np.int16)

    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as audio_file:
        audio_file.setnchannels(1)
        audio_file.setsampwidth(2)
        audio_file.setframerate(sample_rate)
        audio_file.writeframes(pcm.tobytes())
    return path


def main():
    temp_root = Path(tempfile.mkdtemp(prefix='audio-phase2-'))
    source_path = write_test_wav(temp_root / 'input.wav')
    result = AudioPreprocessingService.process(str(source_path), output_dir=str(temp_root / 'processed'))

    cleaned_path = Path(result['cleaned_audio_path'])
    if not cleaned_path.exists():
        raise SystemExit('Cleaned audio file was not created')

    if result['segments_count'] < 1:
        raise SystemExit('Expected at least one segment')

    print('VALIDATION_OK')
    print('source_path=', result['source_path'])
    print('cleaned_audio_path=', result['cleaned_audio_path'])
    print('segments_count=', result['segments_count'])
    print('duration_seconds=', result['duration_seconds'])
    print('sample_rate=', result['sample_rate'])
    print('temp_root=', temp_root)


if __name__ == '__main__':
    main()
