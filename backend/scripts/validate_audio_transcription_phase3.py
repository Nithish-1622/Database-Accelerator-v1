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

from database_accelerator.apps.audio_dataset_engine.models import AudioUpload, TranscriptModel
from database_accelerator.apps.audio_dataset_engine.services.upload_service import AudioUploadService
from database_accelerator.apps.audio_dataset_engine.services.transcription_service import TranscriptionService


def make_audio_file(name='speech.wav', content_type='audio/wav'):
    payload = b'RIFF' + b'\x00' * 256
    return SimpleUploadedFile(name, payload, content_type=content_type)


def main():
    temp_media_root = tempfile.mkdtemp(prefix='audio-phase3-')
    with override_settings(MEDIA_ROOT=temp_media_root):
        upload = AudioUploadService.register_upload(make_audio_file())
        if not upload['success']:
            raise SystemExit(upload['message'])

        record = upload['record']
        result = TranscriptionService.transcribe_audio(
            audio_id=record.id,
            transcript_override='AI improves systems and databases',
            model_name='small',
        )
        if not result['success']:
            raise SystemExit(result['message'])

        transcript = result['transcript']
        fetched = TranscriptModel.objects.get(id=transcript.id)
        if 'AI improves systems' not in fetched.transcript:
            raise SystemExit('Transcript text was not stored correctly')

        print('VALIDATION_OK')
        print('audio_id=', record.id)
        print('transcript_id=', fetched.id)
        print('transcript=', fetched.transcript)
        print('model_name=', fetched.model_name)
        print('audio_status=', AudioUpload.objects.get(id=record.id).status)
        print('temp_media_root=', temp_media_root)

        TranscriptModel.objects.filter(id=fetched.id).delete()
        AudioUpload.objects.filter(id=record.id).delete()


if __name__ == '__main__':
    main()
