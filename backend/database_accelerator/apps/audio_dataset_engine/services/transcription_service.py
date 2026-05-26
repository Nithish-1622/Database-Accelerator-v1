from __future__ import annotations

from typing import Optional

from django.db import transaction

from ..models import AudioUpload, TranscriptModel
from ..transcription.transcriber import WhisperTranscriber


class TranscriptionService:
    @staticmethod
    def transcribe_audio(audio_id, transcript_override: Optional[str] = None, model_name: str = 'small') -> dict:
        try:
            audio = AudioUpload.objects.get(id=audio_id)
        except AudioUpload.DoesNotExist:
            return {'success': False, 'message': 'Audio upload not found'}

        transcriber = WhisperTranscriber(model_name=model_name)
        try:
            result = transcriber.audio_to_text(audio.audio_file.path, transcript_override=transcript_override)
        except Exception as e:
            # Return a clear failure message (e.g., ffmpeg missing)
            return {'success': False, 'message': str(e)}

        with transaction.atomic():
            transcript_record, _ = TranscriptModel.objects.update_or_create(
                audio=audio,
                defaults={
                    'transcript': result['text'],
                    'model_name': model_name if transcript_override is None else f'{model_name}-override',
                    'language': result.get('language', '') or '',
                },
            )
            audio.status = AudioUpload.Status.PROCESSING if not result['text'] else AudioUpload.Status.COMPLETED
            audio.processing_stage = AudioUpload.ProcessingStage.TRANSCRIPTION
            audio.save(update_fields=['status', 'processing_stage', 'updated_at'])

        return {'success': True, 'transcript': transcript_record}

    @staticmethod
    def list_transcripts(audio_id=None):
        queryset = TranscriptModel.objects.select_related('audio').all()
        if audio_id is not None:
            queryset = queryset.filter(audio_id=audio_id)
        return queryset.order_by('-created_at')
