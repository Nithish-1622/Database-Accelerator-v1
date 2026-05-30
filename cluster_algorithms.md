# Clustering Algorithms Deep Dive (Audio Dataset Engine)

## 1) Where Clustering Lives In This Codebase

- Endpoint: `backend/database_accelerator/apps/audio_dataset_engine/views.py`
  - `AudioClusterView.post(...)`
  - Reads:
    - `audio_id`
    - `n_clusters` (default now `8`)
    - `algorithm` (`kmeans`, `agglomerative`, `dbscan`, `gmm`, `spectral`, or `all`)
    - `eps` (for DBSCAN)
    - `min_samples` (for DBSCAN)
- Service orchestration: `backend/database_accelerator/apps/audio_dataset_engine/services/clustering_service.py`
  - Main APIs:
    - `cluster_keywords(...)`
    - `cluster_all(...)`
    - `_run_single_algorithm(...)`
  - Default cluster count constant:
    - `DEFAULT_N_CLUSTERS = 8`
  - Safety behavior for K-based algorithms (`kmeans`, `agglomerative`, `gmm`, `spectral`):
    - If keyword count < 2 => fail fast
    - Effective K = `max(2, min(requested_k, keyword_count))`
- Algorithm implementations: `backend/database_accelerator/apps/audio_dataset_engine/clustering/cluster_engine.py`

## 2) Input Representation (Important)

All algorithms currently cluster on a **single scalar feature per keyword**:

- Input map: `keyword_counts = {keyword: frequency}`
- Vectorization in `vectorize_keywords(...)`:
  - `keys = list(keyword_counts.keys())`
  - `arr = np.array(counts).reshape(-1, 1).astype(float)`

So each keyword is represented by just one value: its frequency.

Mathematically, each point is:

$$
x_i \in \mathbb{R}, \quad x_i = \text{frequency(keyword}_i\text{)}
$$

This has implications:

- Cluster geometry is 1D.
- Many duplicate frequencies can cause degenerate clustering (same point repeated).
- Algorithms that rely on richer structure (especially spectral) may not realize their full strength in 1D frequency-only space.

## 3) Evaluation Metrics In Service

Metrics are computed in `_compute_metrics(...)` (when scikit-learn metrics are available):

- Silhouette score (higher is better)
- Davies-Bouldin index (lower is better)
- Calinski-Harabasz index (higher is better)
- Cluster count (excluding noise label `-1`)
- Memory metrics from process RSS:
  - `memory_rss_mb`
  - `memory_delta_mb`

### 3.1 Silhouette

For point $i$:

- $a(i)$ = average intra-cluster distance
- $b(i)$ = minimum average distance to points in another cluster

$$
s(i) = \frac{b(i)-a(i)}{\max(a(i), b(i))}
$$

Overall silhouette is average of $s(i)$ over points. Range is approximately $[-1,1]$.

### 3.2 Davies-Bouldin

Cluster scatter $S_i$ and centroid distance $M_{ij}$:

$$
R_{ij} = \frac{S_i + S_j}{M_{ij}}, \quad DB = \frac{1}{k}\sum_i \max_{j \ne i} R_{ij}
$$

Lower DB means better separation relative to compactness.

### 3.3 Calinski-Harabasz

Ratio of between-cluster dispersion to within-cluster dispersion:

$$
CH = \frac{\mathrm{tr}(B_k)/(k-1)}{\mathrm{tr}(W_k)/(n-k)}
$$

Higher CH generally indicates better-defined clusters.

## 4) Recommendation Logic

`cluster_all(...)` computes each algorithm and chooses a recommended one by `_score_metrics(...)`:

1. If silhouette exists, score = silhouette
2. Else if calinski exists, score = calinski / 1000
3. Else if davies exists, score = -davies
4. Else score unavailable

So silhouette is the primary decision metric.

## 5) Algorithm-by-Algorithm Deep Dive

---

## 5.1 KMeans

### Code path

- Engine function: `run_kmeans(keyword_counts, n_clusters=...)`
- Model:
  - `KMeans(n_clusters=n_clusters, random_state=42)`

### Parameters passed in this project

- `n_clusters`: requested K (service now defaults to 8)
- `random_state=42`: deterministic centroid initialization sequence

### Core optimization

KMeans solves:

$$
\min_{\{C_j\}} \sum_{i=1}^{n} \min_{j \in \{1,...,k\}} ||x_i - \mu_j||^2
$$

where $\mu_j$ is centroid of cluster $C_j$.

### Iterative updates

1. Assignment:

$$
c_i = \arg\min_j ||x_i - \mu_j||^2
$$

2. Centroid update:

$$
\mu_j = \frac{1}{|C_j|}\sum_{x_i \in C_j} x_i
$$

Repeat until convergence.

### Complexity (rough)

- About $O(n \cdot k \cdot t)$ where $t$ = iterations.

### In this pipeline

- Usually very fast on 1D frequency vectors.
- Sensitive to K choice and duplicates.
- Produces centers (`cluster_centers_`) returned to caller.

---

## 5.2 Agglomerative Clustering (Hierarchical)

### Code path

- Engine function: `run_agglomerative(keyword_counts, n_clusters=...)`
- Model:
  - `AgglomerativeClustering(n_clusters=n_clusters)`

### Parameters passed in this project

- `n_clusters`
- Defaults for linkage/metric are scikit-learn defaults unless changed elsewhere.

### Core idea

Bottom-up merge process:

- Start with each point as its own cluster.
- Iteratively merge closest pair of clusters according to linkage criterion.
- Stop when desired cluster count is reached.

Linkage examples (conceptual):

- Single: minimum pairwise distance
- Complete: maximum pairwise distance
- Average: average pairwise distance
- Ward: variance-minimizing merge

### Complexity (rough)

- Typically heavier than KMeans for large $n$ (often around $O(n^2)$ memory/time behavior depending on implementation).

### In this pipeline

- No explicit centroid output in current implementation.
- Can handle non-spherical shapes in richer feature spaces, but here input is 1D frequency.

---

## 5.3 DBSCAN

### Code path

- Engine function: `run_dbscan(keyword_counts, eps=0.5, min_samples=2)`
- Model:
  - `DBSCAN(eps=eps, min_samples=min_samples)`

### Parameters passed in this project

- `eps`: neighborhood radius
- `min_samples`: minimum points in neighborhood for core point

### Core definitions

- Core point: at least `min_samples` points within radius `eps`
- Border point: not core, but reachable from a core point
- Noise point: neither core nor border (label `-1`)

### Algorithm intuition

- Build density-connected components.
- Any point not density-connected to a core component is noise.

### Complexity (rough)

- Depends on nearest-neighbor search structure; practical performance often near $O(n \log n)$ with indexing, worse otherwise.

### In this pipeline

- Does not use K.
- Good when you want automatic cluster count and outlier handling.
- Metrics can be undefined if too few non-noise clusters remain.

---

## 5.4 Gaussian Mixture Model (GMM)

### Code path

- Engine function: `run_gmm(keyword_counts, n_components=...)`
- Model:
  - `GaussianMixture(n_components=n_components, random_state=42)`

### Parameters passed in this project

- `n_components` (mapped from requested K)
- `random_state=42`

### Probabilistic model

Assumes data generated from a mixture:

$$
p(x) = \sum_{j=1}^{k} \pi_j \mathcal{N}(x \mid \mu_j, \Sigma_j)
$$

where:

- $\pi_j$ are mixture weights, $\sum_j \pi_j = 1$
- $\mathcal{N}(x \mid \mu_j, \Sigma_j)$ are Gaussian components

### Training (EM algorithm)

1. E-step: compute responsibilities

$$
\gamma_{ij} = P(z_i=j \mid x_i)
$$

2. M-step: update $\pi_j, \mu_j, \Sigma_j$ using $\gamma_{ij}$.

Repeat until log-likelihood convergence.

### In this pipeline

- Returns component means as centers.
- Can collapse to fewer effective clusters if data has low diversity (common with repeated 1D frequencies), causing warnings/degenerate metrics.

---

## 5.5 Spectral Clustering

### Code path

- Engine function: `run_spectral(keyword_counts, n_clusters=...)`
- Model:
  - `SpectralClustering(
      n_clusters=n_clusters,
      affinity='nearest_neighbors',
      n_neighbors=min(10, max(2, len(keys)-1)),
      random_state=42
    )`

### Parameters passed in this project

- `n_clusters`
- `affinity='nearest_neighbors'`
- `n_neighbors = min(10, max(2, n-1))`
- `random_state=42`

### Mathematical intuition

1. Build graph $G$ from points (nearest-neighbor affinity).
2. Construct adjacency matrix $W$.
3. Degree matrix $D$ with $D_{ii} = \sum_j W_{ij}$.
4. Graph Laplacian:

$$
L = D - W
$$

(or normalized variants).

5. Compute first $k$ eigenvectors of Laplacian.
6. Run KMeans in eigenvector space.

This can separate non-convex manifolds in richer spaces.

### In this pipeline

- On 1D frequency-only features, benefits may be limited and unstable as K grows.
- In measured runs, silhouette degraded at higher K compared to KMeans/Agglomerative/GMM.

## 6) Parameter Mapping Table (Code-Level)

| API field | Algorithms using it | Internal mapping |
|---|---|---|
| `n_clusters` | kmeans, agglomerative, spectral | `n_clusters` |
| `n_clusters` | gmm | mapped to `n_components` |
| `eps` | dbscan | `eps` |
| `min_samples` | dbscan | `min_samples` |
| `random_state` | kmeans, gmm, spectral | hardcoded `42` |
| `n_neighbors` | spectral | computed from data size |

## 7) What Changed For K In This Project

### Default K

- Old default: `3`
- New default: `8`

### Safety cap

For K-based algorithms, service now records and uses:

- `n_clusters_requested`
- `n_clusters_effective` (capped to available keyword count and minimum 2)

For GMM, similarly:

- `n_components_requested`
- `n_components_effective`

This prevents invalid requests when keyword count is small.

## 8) Empirical K-Sweep Result In This Repository

A benchmark run was generated at:

- `backend/benchmark_k_sweep.json`

Summary (`audios_evaluated = 16`):

- KMeans average silhouette by K:
  - K=2: 0.8031
  - K=3: 0.7534
  - K=4: 0.6941
  - K=5: 0.7472
  - K=6: 0.7565
  - K=7: 0.8590
  - K=8: 0.8763
- Agglomerative average silhouette by K:
  - K=2: 0.7075
  - K=3: 0.6137
  - K=4: 0.6073
  - K=5: 0.6538
  - K=6: 0.6619
  - K=7: 0.7516
  - K=8: 0.7668
- GMM average silhouette by K:
  - K=2: 0.4582
  - K=3: 0.4612
  - K=4: 0.6325
  - K=5: 0.7472
  - K=6: 0.7565
  - K=7: 0.8590
  - K=8: 0.8763
- Spectral average silhouette by K:
  - K=2: 0.4010
  - K=3: 0.5968
  - K=4: 0.6705
  - K=5: 0.2028
  - K=6: 0.1650
  - K=7: 0.1183
  - K=8: -0.0130

Interpretation:

- For this project's current feature space (1D frequency), higher K (7-8) improved KMeans/Agglomerative/GMM.
- Spectral worsened for large K.
- Since recommendation logic picks best algorithm per run, setting default K=8 gave better average quality in observed datasets while preserving algorithm competition.

## 9) Practical Notes And Limitations

1. Current clustering quality is constrained by 1D features.
   - Better semantic clusters usually need richer features (embeddings, co-occurrence vectors, TF-IDF, contextual embeddings).
2. Duplicate frequencies create degenerate behavior (especially for GMM/KMeans), as seen by convergence warnings.
3. K should ideally be data-adaptive.
   - Future enhancement: evaluate K candidates per algorithm per audio and auto-select by silhouette/CH/DB composite.
4. DBSCAN is sensitive to feature scale and `eps`.
   - In 1D raw counts, consider scaling (for example standardization/log transform) before DBSCAN.

## 10) Frontend Behavior

- `frontend/src/pages/AudioPage.jsx` now sends `n_clusters: 8` in pipeline clustering call.
- Backend still accepts explicit override; clients can pass any K, and service applies safe effective capping for K-based methods.

---

If you want, the next step can be an "auto-K mode" where backend computes K in a range (for example 2..10), picks per-algorithm best K, and returns that explanation directly to the UI.
