# Problem Class Map

Use this file only to widen the candidate set when the problem class is ambiguous or multiple method families are plausible.

## Estimation or Fitting
- Common candidates:
  - `RANSAC`
  - `Levenberg-Marquardt`
  - `bundle adjustment`
  - `ICP`
- Prefer when:
  - noisy correspondences or outliers exist
  - parameters must be estimated from geometric or numeric observations
- Watch for:
  - local minima
  - sensitivity to initialization
  - runtime growth with dense iterative refinement

## Optimization or Scheduling
- Common candidates:
  - greedy heuristics
  - dynamic programming
  - ILP or MIP
  - local search
- Prefer when:
  - objective and constraints can be stated explicitly
  - trade-offs between optimality and latency matter
- Watch for:
  - greedy choices that fail global optimality
  - exact solvers that do not meet runtime limits

## Search or Retrieval
- Common candidates:
  - `BM25`
  - dense ANN retrieval
  - hybrid retrieval
  - reranker on top-k candidates
- Prefer when:
  - matching depends on text relevance, semantic similarity, or both
  - recall and latency must be balanced
- Watch for:
  - dense retrieval with weak embeddings
  - reranking costs that dominate latency

## Ranking or Reranking
- Common candidates:
  - rules plus weighted scoring
  - pairwise reranker
  - listwise ranking
  - learning-to-rank
- Prefer when:
  - candidate generation already exists
  - ordering quality matters more than binary retrieval
- Watch for:
  - label scarcity
  - offline metrics that fail to match online behavior

## Detection, Segmentation, or Pose
- Common candidates:
  - detector-based pipeline
  - keypoint-based model
  - segmentation-based approach
  - detector plus tracker
- Prefer when:
  - object localization, pose, or boundary quality is the main target
  - throughput and annotation budget constrain model choice
- Watch for:
  - heavy models that miss real-time targets
  - detector misses that cascade into later stages

## Forecasting
- Common candidates:
  - moving average or exponential smoothing
  - ARIMA or SARIMA
  - tree-based regressors
  - sequence models
- Prefer when:
  - the problem has temporal structure and a prediction horizon
- Watch for:
  - weak seasonality assumptions
  - overfitting with small time series

## Control or Tracking
- Common candidates:
  - Kalman filter
  - particle filter
  - model predictive control
  - tracker with detector refresh
- Prefer when:
  - the system evolves over time with noisy observations
- Watch for:
  - mismatch between motion model and reality
  - unstable updates under delayed observations

## Recommendation or Matching
- Common candidates:
  - rules plus filters
  - matrix factorization
  - two-tower retrieval
  - graph-based methods
- Prefer when:
  - user-item or entity-entity matching is the core task
- Watch for:
  - cold-start behavior
  - feature drift and sparse feedback

## System Performance or Scaling
- Common candidates:
  - batching
  - caching
  - async pipelines
  - data layout or vectorization changes
- Prefer when:
  - the bottleneck is throughput, latency, or resource waste
- Watch for:
  - stale-cache behavior
  - queue buildup
  - hidden memory spikes

## Workflow Orchestration
- Common candidates:
  - explicit rule engine
  - state machine
  - DAG scheduler
  - event-driven orchestration
- Prefer when:
  - ordering, retries, and branch logic are the main difficulty
- Watch for:
  - hidden state transitions
  - weak idempotency or retry semantics
