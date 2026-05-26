import os
import sys
import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database_accelerator.settings')
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import django
django.setup()

from django.test import override_settings

from database_accelerator.apps.audio_dataset_engine.models import AudioUpload
from database_accelerator.apps.audio_dataset_engine.services.upload_service import AudioUploadService


def make_audio_file(name='sample.wav', content_type='audio/wav'):
    payload = b'RIFF' + b'\x00' * 256
    return SimpleUploadedFile(name, payload, content_type=content_type)


def main():
    temp_media_root = tempfile.mkdtemp(prefix='audio-phase1-')
    with override_settings(MEDIA_ROOT=temp_media_root):
        invalid = AudioUploadService.register_upload(SimpleUploadedFile('bad.txt', b'hello', content_type='text/plain'))
        if invalid['success']:
            raise SystemExit('Invalid file was accepted unexpectedly')

        result = AudioUploadService.register_upload(make_audio_file())
        if not result['success']:
            raise SystemExit(result['message'])

        record = result['record']
        fetched = AudioUploadService.get_upload(record.id)
        if not fetched:
            raise SystemExit('Uploaded record was not found')

        print('VALIDATION_OK')
        print('record_id=', fetched.id)
        print('status=', fetched.status)
        print('stage=', fetched.processing_stage)
        print('file_path=', fetched.file_path)
        print('media_root=', temp_media_root)

        # Clean up the live-db row so repeated validations stay idempotent.
        AudioUpload.objects.filter(id=fetched.id).delete()


if __name__ == '__main__':
    main()
