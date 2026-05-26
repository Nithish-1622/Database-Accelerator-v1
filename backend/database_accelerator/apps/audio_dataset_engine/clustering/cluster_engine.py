from __future__ import annotations

from typing import Dict, List, Tuple

try:
    from sklearn.cluster import KMeans
    import numpy as np
    _SKLEARN_AVAILABLE = True
except Exception:
    KMeans = None
    np = None
    _SKLEARN_AVAILABLE = False


def vectorize_keywords(keyword_counts: Dict[str, int]) -> Tuple[List[str], 'np.ndarray']:
    keys = list(keyword_counts.keys())
    counts = [keyword_counts[k] for k in keys]
    if _SKLEARN_AVAILABLE:
        arr = np.array(counts).reshape(-1, 1).astype(float)
    else:
        # simple list of lists
        arr = [[float(c)] for c in counts]
    return keys, arr


def run_kmeans(keyword_counts: Dict[str, int], n_clusters: int = 3):
    keys, arr = vectorize_keywords(keyword_counts)
    if _SKLEARN_AVAILABLE:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(arr)
        centers = kmeans.cluster_centers_.tolist()
        return {keys[i]: int(labels[i]) for i in range(len(keys))}, centers

    # fallback: bin by quantiles (simple)
    counts = [v for v in keyword_counts.values()]
    if not counts:
        return {}, []
    sorted_vals = sorted(set(counts))
    bins = min(n_clusters, len(sorted_vals))
    thresholds = [sorted_vals[int(i * len(sorted_vals) / bins)] for i in range(1, bins)]
    labels = {}
    for k, v in keyword_counts.items():
        label = 0
        for t in thresholds:
            if v > t:
                label += 1
        labels[k] = label
    centers = []
    return labels, centers
