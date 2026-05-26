from __future__ import annotations

from typing import Dict, Iterable, List

from django.db import transaction

from ..models import AudioUpload, KeywordModel, FrequencyModel
from ..keyword_engine.extractor import extract_keywords_from_text


class KeywordService:
    @staticmethod
    def extract_and_store(audio_id, text: str, top_k: int = 200) -> dict:
        try:
            audio = AudioUpload.objects.get(id=audio_id)
        except AudioUpload.DoesNotExist:
            return {'success': False, 'message': 'Audio not found'}

        counts, most = extract_keywords_from_text(text, top_k=top_k)

        created = []
        with transaction.atomic():
            # clear existing keywords for this audio
            KeywordModel.objects.filter(audio=audio).delete()
            FrequencyModel.objects.filter(audio=audio).delete()

            for kw, freq in most:
                if not kw:
                    continue
                k = KeywordModel.objects.create(audio=audio, keyword=kw, frequency=int(freq), timestamps=[])
                FrequencyModel.objects.create(audio=audio, keyword=kw, count=int(freq))
                created.append({'keyword': kw, 'frequency': int(freq)})

            audio.processing_stage = AudioUpload.ProcessingStage.KEYWORD_EXTRACTION
            audio.status = AudioUpload.Status.COMPLETED if created else AudioUpload.Status.FAILED
            audio.save(update_fields=['processing_stage', 'status', 'updated_at'])

        return {'success': True, 'keywords': created, 'counts': counts}

    @staticmethod
    def list_keywords(audio_id=None):
        qs = KeywordModel.objects.all()
        if audio_id is not None:
            qs = qs.filter(audio_id=audio_id)
        return qs.order_by('-frequency')

    @staticmethod
    def list_frequencies(audio_id=None):
        qs = FrequencyModel.objects.all()
        if audio_id is not None:
            qs = qs.filter(audio_id=audio_id)
        return qs.order_by('-count')
