from django.db import transaction

from ..models import AudioUpload
from ..utils.validators import validate_audio_file


class AudioUploadService:
    @staticmethod
    def register_upload(uploaded_file):
        validation = validate_audio_file(uploaded_file)
        if not validation['valid']:
            return {'success': False, 'message': validation['message']}

        filename = uploaded_file.name
        file_size = int(getattr(uploaded_file, 'size', 0) or 0)

        try:
            with transaction.atomic():
                record = AudioUpload.objects.create(
                    filename=filename,
                    audio_file=uploaded_file,
                    file_path='',
                    file_size=file_size,
                    duration=None,
                    status=AudioUpload.Status.QUEUED,
                    processing_stage=AudioUpload.ProcessingStage.QUEUED,
                )
                record.file_path = record.audio_file.name
                record.save(update_fields=['file_path', 'updated_at'])
        except Exception as exc:
            return {'success': False, 'message': f'Failed to store audio file: {exc}'}

        return {'success': True, 'record': record}

    @staticmethod
    def get_upload(audio_id):
        try:
            return AudioUpload.objects.get(id=audio_id)
        except AudioUpload.DoesNotExist:
            return None
