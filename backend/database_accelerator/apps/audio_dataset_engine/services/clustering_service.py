from __future__ import annotations

from typing import Dict, List, Optional

import time

from django.db import transaction

from ..models import AudioUpload, ClusterModel, ClusterMember, KeywordModel
from ..clustering.cluster_engine import (
    run_kmeans,
    run_agglomerative,
    run_dbscan,
    run_gmm,
    run_spectral,
    vectorize_keywords,
)

try:
    from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
except Exception:
    silhouette_score = davies_bouldin_score = calinski_harabasz_score = None


class ClusteringService:
    @staticmethod
    def cluster_keywords(
        audio_id,
        n_clusters: int = 3,
        algorithm: str = 'kmeans',
        eps: float = 0.5,
        min_samples: int = 2,
    ) -> dict:
        try:
            audio = AudioUpload.objects.get(id=audio_id)
        except AudioUpload.DoesNotExist:
            return {'success': False, 'message': 'Audio not found'}

        kws = KeywordModel.objects.filter(audio=audio)
        keyword_counts = {k.keyword: k.frequency for k in kws}

        if not keyword_counts:
            return {'success': False, 'message': 'No keywords available for clustering'}

        if algorithm == 'all':
            return ClusteringService.cluster_all(
                audio,
                kws,
                keyword_counts,
                n_clusters=n_clusters,
                eps=eps,
                min_samples=min_samples,
            )

        result = ClusteringService._run_single_algorithm(
            algorithm,
            keyword_counts,
            n_clusters=n_clusters,
            eps=eps,
            min_samples=min_samples,
        )

        if not result.get('success'):
            return result

        with transaction.atomic():
            cluster = ClusterModel.objects.create(audio=audio, algorithm=algorithm, parameters=result.get('parameters', {}))
            for kw_text, label in result['labels'].items():
                kw_obj = kws.filter(keyword=kw_text).first()
                ClusterMember.objects.create(
                    cluster=cluster,
                    keyword=kw_obj,
                    keyword_text=kw_text,
                    weight=float(keyword_counts.get(kw_text, 0)),
                )

        return {
            'success': True,
            'cluster_id': str(cluster.id),
            'labels': result['labels'],
            'centers': result.get('centers', []),
            'metrics': result.get('metrics'),
            'elapsed_ms': result.get('elapsed_ms'),
            'algorithm': algorithm,
        }

    @staticmethod
    def cluster_all(
        audio: AudioUpload,
        kws,
        keyword_counts: Dict[str, int],
        n_clusters: int = 3,
        eps: float = 0.5,
        min_samples: int = 2,
    ) -> dict:
        algorithms = ['kmeans', 'agglomerative', 'dbscan', 'gmm', 'spectral']
        results = {}
        recommended = None

        for algo in algorithms:
            result = ClusteringService._run_single_algorithm(
                algo,
                keyword_counts,
                n_clusters=n_clusters,
                eps=eps,
                min_samples=min_samples,
            )
            if not result.get('success'):
                results[algo] = result
                continue

            with transaction.atomic():
                cluster = ClusterModel.objects.create(audio=audio, algorithm=algo, parameters=result.get('parameters', {}))
                for kw_text, label in result['labels'].items():
                    kw_obj = kws.filter(keyword=kw_text).first()
                    ClusterMember.objects.create(
                        cluster=cluster,
                        keyword=kw_obj,
                        keyword_text=kw_text,
                        weight=float(keyword_counts.get(kw_text, 0)),
                    )

            result['cluster_id'] = str(cluster.id)
            results[algo] = result

            score = ClusteringService._score_metrics(result.get('metrics'))
            if score is not None and (recommended is None or score > recommended['score']):
                recommended = {
                    'algorithm': algo,
                    'score': score,
                    'metrics': result.get('metrics'),
                }

        return {
            'success': True,
            'results': results,
            'recommended': recommended,
        }

    @staticmethod
    def _run_single_algorithm(
        algorithm: str,
        keyword_counts: Dict[str, int],
        n_clusters: int = 3,
        eps: float = 0.5,
        min_samples: int = 2,
    ) -> dict:
        start = time.perf_counter()
        try:
            if algorithm == 'kmeans':
                labels, centers = run_kmeans(keyword_counts, n_clusters=n_clusters)
                params = {'n_clusters': n_clusters}
            elif algorithm == 'agglomerative':
                labels, centers = run_agglomerative(keyword_counts, n_clusters=n_clusters)
                params = {'n_clusters': n_clusters}
            elif algorithm == 'dbscan':
                labels, centers = run_dbscan(keyword_counts, eps=eps, min_samples=min_samples)
                params = {'eps': eps, 'min_samples': min_samples}
            elif algorithm == 'gmm':
                labels, centers = run_gmm(keyword_counts, n_components=n_clusters)
                params = {'n_components': n_clusters}
            elif algorithm == 'spectral':
                labels, centers = run_spectral(keyword_counts, n_clusters=n_clusters)
                params = {'n_clusters': n_clusters}
            else:
                return {'success': False, 'message': f'Unsupported algorithm: {algorithm}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        metrics = ClusteringService._compute_metrics(keyword_counts, labels)
        return {
            'success': True,
            'labels': labels,
            'centers': centers,
            'metrics': metrics,
            'elapsed_ms': elapsed_ms,
            'parameters': params,
        }

    @staticmethod
    def _compute_metrics(keyword_counts: Dict[str, int], labels: Dict[str, int]) -> Optional[dict]:
        if silhouette_score is None:
            return None

        keys, arr = vectorize_keywords(keyword_counts)
        label_list = [labels.get(k, -1) for k in keys]

        # exclude noise for cluster count
        unique_labels = sorted({l for l in label_list if l != -1})
        cluster_count = len(unique_labels)
        if cluster_count < 2:
            return {
                'cluster_count': cluster_count,
                'silhouette': None,
                'davies_bouldin': None,
                'calinski_harabasz': None,
            }

        try:
            silhouette = float(silhouette_score(arr, label_list))
        except Exception:
            silhouette = None
        try:
            davies = float(davies_bouldin_score(arr, label_list))
        except Exception:
            davies = None
        try:
            calinski = float(calinski_harabasz_score(arr, label_list))
        except Exception:
            calinski = None

        return {
            'cluster_count': cluster_count,
            'silhouette': silhouette,
            'davies_bouldin': davies,
            'calinski_harabasz': calinski,
        }

    @staticmethod
    def _score_metrics(metrics: Optional[dict]) -> Optional[float]:
        if not metrics:
            return None
        silhouette = metrics.get('silhouette')
        calinski = metrics.get('calinski_harabasz')
        davies = metrics.get('davies_bouldin')
        if silhouette is not None:
            return silhouette
        if calinski is not None:
            return calinski / 1000.0
        if davies is not None:
            return -davies
        return None
