from __future__ import annotations

from typing import Dict, List, Tuple

try:
    import numpy as np
    from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, SpectralClustering
    from sklearn.mixture import GaussianMixture
    _SKLEARN_AVAILABLE = True
except Exception:
    np = None
    KMeans = AgglomerativeClustering = DBSCAN = SpectralClustering = GaussianMixture = None
    _SKLEARN_AVAILABLE = False


def vectorize_keywords(keyword_counts: Dict[str, int]) -> Tuple[List[str], 'np.ndarray']:
    keys = list(keyword_counts.keys())
    counts = [keyword_counts[k] for k in keys]
    if not _SKLEARN_AVAILABLE:
        raise RuntimeError('scikit-learn is required for clustering algorithms')
    arr = np.array(counts).reshape(-1, 1).astype(float)
    return keys, arr


def run_kmeans(keyword_counts: Dict[str, int], n_clusters: int = 3):
    keys, arr = vectorize_keywords(keyword_counts)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(arr)
    centers = kmeans.cluster_centers_.tolist()
    return {keys[i]: int(labels[i]) for i in range(len(keys))}, centers


def run_agglomerative(keyword_counts: Dict[str, int], n_clusters: int = 3):
    keys, arr = vectorize_keywords(keyword_counts)
    model = AgglomerativeClustering(n_clusters=n_clusters)
    labels = model.fit_predict(arr)
    return {keys[i]: int(labels[i]) for i in range(len(keys))}, []


def run_dbscan(keyword_counts: Dict[str, int], eps: float = 0.5, min_samples: int = 2):
    keys, arr = vectorize_keywords(keyword_counts)
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(arr)
    return {keys[i]: int(labels[i]) for i in range(len(keys))}, []


def run_gmm(keyword_counts: Dict[str, int], n_components: int = 3):
    keys, arr = vectorize_keywords(keyword_counts)
    model = GaussianMixture(n_components=n_components, random_state=42)
    labels = model.fit_predict(arr)
    centers = model.means_.tolist()
    return {keys[i]: int(labels[i]) for i in range(len(keys))}, centers


def run_spectral(keyword_counts: Dict[str, int], n_clusters: int = 3):
    keys, arr = vectorize_keywords(keyword_counts)
    if len(keys) < 2:
        return {}, []
    n_neighbors = min(10, max(2, len(keys) - 1))
    model = SpectralClustering(
        n_clusters=n_clusters,
        affinity='nearest_neighbors',
        n_neighbors=n_neighbors,
        random_state=42,
    )
    labels = model.fit_predict(arr)
    return {keys[i]: int(labels[i]) for i in range(len(keys))}, []
