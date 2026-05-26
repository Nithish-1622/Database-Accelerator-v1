import os
import sys
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database_accelerator.settings')
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import django
django.setup()

from database_accelerator.apps.audio_dataset_engine.services.keyword_service import KeywordService
from database_accelerator.apps.audio_dataset_engine.services.frequency_service import FrequencyService
from database_accelerator.apps.audio_dataset_engine.services.upload_service import AudioUploadService


def main():
    # register sample
    from django.core.files.uploadedfile import SimpleUploadedFile
    sample = SimpleUploadedFile('s.wav', b'RIFF' + b'\x00' * 256, content_type='audio/wav')
    res = AudioUploadService.register_upload(sample)
    audio = res['record']
    text = 'apple banana apple orange banana apple'
    KeywordService.extract_and_store(audio.id, text)

    top = FrequencyService.compute_top_k(audio.id, top_k=10)
    hist = FrequencyService.compute_term_histogram(audio.id)
    if not top or not hist:
        raise SystemExit('Frequency computation failed')
    print('VALIDATION_OK')
    print('top=', top)
    print('hist=', hist)

    # cleanup
    from database_accelerator.apps.audio_dataset_engine.models import KeywordModel, FrequencyModel
    KeywordModel.objects.filter(audio=audio).delete()
    FrequencyModel.objects.filter(audio=audio).delete()
    audio.delete()


if __name__ == '__main__':
    main()
