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

from django.test import Client, override_settings
from database_accelerator.apps.audio_dataset_engine.services.upload_service import AudioUploadService


def make_audio_file(name='sample.wav', content_type='audio/wav'):
    payload = b'RIFF' + b'\x00' * 256
    return SimpleUploadedFile(name, payload, content_type=content_type)


def main():
    temp_media_root = tempfile.mkdtemp(prefix='audio-export-')
    with override_settings(MEDIA_ROOT=temp_media_root):
        result = AudioUploadService.register_upload(make_audio_file())
        if not result['success']:
            raise SystemExit('upload failed')
        record = result['record']
        client = Client()

        # attempt CSV keywords export
        resp = client.get(f'/api/audio/export/{record.id}/keywords/csv/')
        print('keywords csv status=', resp.status_code)
        if resp.status_code != 200:
            print('content=', getattr(resp, 'content', b''))
            raise SystemExit('export failed')

        # attempt json export
        resp2 = client.get(f'/api/audio/export/{record.id}/keywords/json/')
        print('keywords json status=', resp2.status_code)
        if resp2.status_code != 200:
            raise SystemExit('json export failed')

        print('EXPORT_VALIDATION_OK')


if __name__ == '__main__':
    main()
