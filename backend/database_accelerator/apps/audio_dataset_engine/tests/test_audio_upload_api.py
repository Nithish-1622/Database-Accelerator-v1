import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from database_accelerator.apps.audio_dataset_engine.models import AudioUpload


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class AudioUploadApiTests(APITestCase):
    def _make_wav(self):
        payload = b'RIFF' + b'\x00' * 128
        return SimpleUploadedFile('sample.wav', payload, content_type='audio/wav')

    def test_rejects_invalid_extension(self):
        file_obj = SimpleUploadedFile('sample.txt', b'not audio', content_type='text/plain')
        url = reverse('audio-upload')
        response = self.client.post(url, {'audio_file': file_obj}, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Unsupported audio format', str(response.data))

    def test_upload_creates_audio_record(self):
        url = reverse('audio-upload')
        response = self.client.post(url, {'audio_file': self._make_wav()}, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        record = AudioUpload.objects.get(id=response.data['id'])
        self.assertEqual(record.status, AudioUpload.Status.QUEUED)
        self.assertTrue(Path(record.file_path).name.endswith('.wav'))

    def test_status_endpoint_returns_upload(self):
        created = AudioUpload.objects.create(
            filename='sample.wav',
            audio_file='audio/sample.wav',
            file_path='audio/sample.wav',
            file_size=10,
            duration=None,
            status=AudioUpload.Status.QUEUED,
            processing_stage=AudioUpload.ProcessingStage.QUEUED,
        )
        url = reverse('audio-status', kwargs={'audio_id': created.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(created.id))
