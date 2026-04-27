# Profile Comparisons and Reflection

This project evolved from a simple additive scorer into a pipeline with retrieval, ranking, guardrails, and reliability gates. The biggest insight was that recommendation quality depends on both which candidates are retrieved and how they are ranked. In the earlier version, every song was scored globally, so contradictory profiles could create strange outcomes. In the updated system, retrieval happens first (strict, relaxed, then fallback), and only those candidates are ranked. That design made the behavior easier to reason about and easier to debug because each recommendation includes a retrieval reason and a confidence label.

Comparing profiles still highlights tradeoffs. High-Energy Pop generally receives medium/high confidence recommendations because the catalog has strong matches in both energy and mood. In contrast, profiles like Zero-Energy EDM or Aggressive Lullaby often trigger fallback retrieval and produce mostly low-confidence outputs. That is expected and now visible through both explanation text and reliability metrics. The reliability report plus quality gates gave me a concrete way to judge system health beyond anecdotal examples. The strongest lesson was that good AI systems need testable behavior contracts, not only clever scoring formulas.

Architecture reference: see the system diagram in [README.md](README.md) under the Design and Architecture section.

## Reflection and Ethics

### 1) Limitations and biases in this system

The biggest limitation is catalog size. With only 17 songs, the system can return the least-bad option instead of a truly good match. The retriever and scorer also rely on manually chosen labels and weights, so they can encode bias from my assumptions (for example, what counts as "happy" valence or which mood aliases should map together). Another limitation is that the reliability summary is averaged, which can hide weak behavior on hard edge cases.

### 2) Potential misuse and prevention

This project could be misused by presenting confidence values as if they were guaranteed truth, or by using a small, biased catalog to make broad claims about user taste. To reduce misuse, I documented that this is a classroom prototype, exposed confidence labels directly in outputs, added structured logs and quality gates, and included clear limitations in [README.md](README.md) and [model_card.md](model_card.md). If this became a real product, I would add stronger governance: larger representative data, periodic bias audits, and human review before deploying changes.

### 3) What surprised me during reliability testing

Two things surprised me. First, contradictory profiles (like Zero-Energy EDM) triggered fallback retrieval more often than expected, which pushed confidence down even when scores looked numerically reasonable. Second, overall quality gates could still pass while specific profiles remained weak, which showed me that aggregate metrics are useful but not sufficient without per-profile checks.

### 4) Collaboration with AI during this project

One helpful AI suggestion was to add retrieval-stage traceability and confidence labels to every recommendation explanation. That made debugging and evaluation much clearer.

One flawed AI suggestion appeared during early retrieval changes: the candidate set sometimes returned fewer than k results, which broke expected behavior in tests. I fixed that by adding controlled backfill to preserve top-k guarantees and then added tests to prevent the regression from returning.
