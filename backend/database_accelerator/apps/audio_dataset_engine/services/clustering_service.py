from __future__ import annotations

from typing import Dict, List

from django.db import transaction

from ..models import AudioUpload, ClusterModel, ClusterMember, KeywordModel
from ..clustering.cluster_engine import run_kmeans


class ClusteringService:
    @staticmethod
    def cluster_keywords(audio_id, n_clusters: int = 3, algorithm: str = 'kmeans') -> dict:
        try:
            audio = AudioUpload.objects.get(id=audio_id)
        except AudioUpload.DoesNotExist:
            return {'success': False, 'message': 'Audio not found'}

        kws = KeywordModel.objects.filter(audio=audio)
        keyword_counts = {k.keyword: k.frequency for k in kws}

        labels, centers = run_kmeans(keyword_counts, n_clusters=n_clusters)

        with transaction.atomic():
            cluster = ClusterModel.objects.create(audio=audio, algorithm=algorithm, parameters={'n_clusters': n_clusters})
            for kw_text, label in labels.items():
                kw_obj = kws.filter(keyword=kw_text).first()
                ClusterMember.objects.create(cluster=cluster, keyword=kw_obj, keyword_text=kw_text, weight=float(keyword_counts.get(kw_text, 0)))

        return {'success': True, 'cluster_id': str(cluster.id), 'labels': labels, 'centers': centers}
