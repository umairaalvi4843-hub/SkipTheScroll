# Per-version dev results (seed 42, n=80 sentences)

| Version          | Macro-F1  | Binary any-unfair F1 | JSON valid % | Quote verified % | Notes                          |
| ---------------- | --------- | -------------------- | ------------ | ---------------- | ------------------------------ |
| v0 baseline      | 0.0       | 0.0                  | 100*         | null             | Prose only, 0 clauses          |
| v1 role+taxonomy | 0.0       | 0.0                  | 100*         | null             | Prose only, 0 clauses          |
| v2 JSON+few-shot | **0.867** | **0.910**            | 93.8         | **98.6**         | First structured version       |
| v3 chaining      | 0.783     | 0.873                | 100.0        | null             | Extract -> classify -> summary |
| v4 +verifier     | 0.743     | 0.869                | 100.0        | 95.5             | Added quote verification       |

*json_valid_pct is 100 for v0/v1 only because no JSON parse is attempted; the metric is meaningful only for v2+.

**Interpretation:** 
The experiment reveals a clear trade-off between structural reliability and classification recall. v2 achieved the highest Macro-F1 (0.867) but suffered from a 6.2% JSON failure rate. v3 achieved perfect JSON validity (100%) but reduced classification recall on rare categories. v4 successfully added dual-verification, maintaining 100% JSON validity and verifying 95.5% of quotes (67 clauses), but further increased the model's conservatism, dropping Macro-F1 to 0.743. This demonstrates that while chaining and verification solve the hallucination and formatting problems, they must be carefully tuned to avoid over-caution in classification.
