import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database_accelerator.settings')
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import django
django.setup()

from database_accelerator.apps.audio_dataset_engine.services.upload_service import AudioUploadService
from database_accelerator.apps.audio_dataset_engine.services.keyword_service import KeywordService
from database_accelerator.apps.audio_dataset_engine.models import KeywordModel, FrequencyModel


def main():
    temp_media_root = tempfile.mkdtemp(prefix='audio-phase4-')
    # register a fake audio record via the upload service (uses FileField storage)
    from django.core.files.uploadedfile import SimpleUploadedFile
    sample = SimpleUploadedFile('speech.wav', b'RIFF' + b'\x00' * 256, content_type='audio/wav')
    res = AudioUploadService.register_upload(sample)
    if not res['success']:
        raise SystemExit(res['message'])
    audio = res['record']

    text = 'AI AI model speech speech system database database token'
    result = KeywordService.extract_and_store(audio.id, text)
    if not result['success']:
        raise SystemExit(result.get('message'))

    kws = list(KeywordModel.objects.filter(audio=audio))
    freqs = list(FrequencyModel.objects.filter(audio=audio))
    if len(kws) == 0 or len(freqs) == 0:
        raise SystemExit('No keywords persisted')

    print('VALIDATION_OK')
    print('audio_id=', audio.id)
    print('keywords:', [(k.keyword, k.frequency) for k in kws])
    print('frequencies:', [(f.keyword, f.count) for f in freqs])

    # cleanup
    KeywordModel.objects.filter(audio=audio).delete()
    FrequencyModel.objects.filter(audio=audio).delete()
    audio.delete()


if __name__ == '__main__':
    main()
