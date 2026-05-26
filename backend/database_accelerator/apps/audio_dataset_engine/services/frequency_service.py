from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Tuple

from ..models import AudioUpload, KeywordModel, FrequencyModel


class FrequencyService:
    @staticmethod
    def compute_top_k(audio_id, top_k: int = 50) -> List[Tuple[str, int]]:
        kws = KeywordModel.objects.filter(audio_id=audio_id)
        counts = [(k.keyword, k.frequency) for k in kws]
        counts_sorted = sorted(counts, key=lambda x: -x[1])[:top_k]
        return counts_sorted

    @staticmethod
    def compute_term_histogram(audio_id) -> Dict[str, int]:
        kws = KeywordModel.objects.filter(audio_id=audio_id)
        return {k.keyword: k.frequency for k in kws}

    @staticmethod
    def compute_cooccurrence(audio_id) -> Dict[Tuple[str, str], int]:
        # naive co-occurrence across transcript segments isn't implemented; approximate by keyword presence
        kws = list(KeywordModel.objects.filter(audio_id=audio_id))
        keywords = [k.keyword for k in kws]
        co = defaultdict(int)
        for i in range(len(keywords)):
            for j in range(i + 1, len(keywords)):
                a, b = keywords[i], keywords[j]
                co[(a, b)] += 1
        return dict(co)
