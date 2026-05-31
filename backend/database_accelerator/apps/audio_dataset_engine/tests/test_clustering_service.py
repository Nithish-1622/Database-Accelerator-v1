from unittest.mock import patch

from django.test import TestCase

from database_accelerator.apps.audio_dataset_engine.models import AudioUpload, KeywordModel
from database_accelerator.apps.audio_dataset_engine.services.clustering_service import ClusteringService


class ClusteringServiceSweepTests(TestCase):
    def setUp(self):
        self.audio = AudioUpload.objects.create(
            filename='sample.wav',
            audio_file='audio/sample.wav',
            file_path='audio/sample.wav',
            file_size=10,
            duration=None,
            status=AudioUpload.Status.COMPLETED,
            processing_stage=AudioUpload.ProcessingStage.KEYWORD_EXTRACTION,
        )
        KeywordModel.objects.create(audio=self.audio, keyword='alpha', frequency=3, timestamps=[])
        KeywordModel.objects.create(audio=self.audio, keyword='beta', frequency=5, timestamps=[])
        KeywordModel.objects.create(audio=self.audio, keyword='gamma', frequency=8, timestamps=[])

    def _fake_run_single_algorithm(self, algorithm, keyword_counts, n_clusters=8, eps=0.5, min_samples=2):
        labels = {keyword: index % 2 for index, keyword in enumerate(keyword_counts)}
        metrics = {
            'cluster_count': 2,
            'silhouette': round(float(n_clusters) / 10.0, 3),
            'davies_bouldin': round(1.0 / max(n_clusters, 1), 3),
            'calinski_harabasz': float(n_clusters) * 10.0,
        }
        return {
            'success': True,
            'labels': labels,
            'centers': [],
            'metrics': metrics,
            'elapsed_ms': float(n_clusters),
            'parameters': {
                'n_clusters_requested': n_clusters,
                'n_clusters_effective': n_clusters,
            },
        }

    @patch.object(ClusteringService, '_run_single_algorithm')
    def test_cluster_all_returns_k_sweep_payload(self, mock_run):
        mock_run.side_effect = self._fake_run_single_algorithm

        keyword_counts = {item.keyword: item.frequency for item in KeywordModel.objects.filter(audio=self.audio)}
        result = ClusteringService.cluster_all(self.audio, KeywordModel.objects.filter(audio=self.audio), keyword_counts)

        self.assertTrue(result['success'])
        self.assertIn('k_sweep', result)
        self.assertEqual(result['k_sweep']['range'], [3, 4, 5, 6, 7, 8])

        kmeans_series = result['k_sweep']['algorithms']['kmeans']['points']
        self.assertEqual([point['requested_k'] for point in kmeans_series], [3, 4, 5, 6, 7, 8])
        self.assertEqual(result['k_sweep']['algorithms']['kmeans']['best']['requested_k'], 8)