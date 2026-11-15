# Dataset Audit — UNFAIR-ToS (coastalcph/lex_glue, config: unfair_tos)

Columns: `['text', 'labels']`


## Split summary

| Split | Rows | Empty label % | Multi-label % |
|---|---|---|---|
| train | 5532 | 88.61 | 1.14 |
| validation | 2275 | 89.89 | 0.79 |
| test | 1607 | 89.3 | 0.87 |

## Per-class counts

| Category | Train | Validation | Test |
|---|---|---|---|
| Limitation of liability | 191 | 67 | 38 |
| Unilateral termination | 139 | 59 | 38 |
| Unilateral change | 122 | 28 | 38 |
| Content removal | 73 | 32 | 13 |
| Contract by using | 76 | 18 | 23 |
| Choice of law | 39 | 18 | 13 |
| Jurisdiction | 34 | 18 | 16 |
| Arbitration | 28 | 9 | 7 |

## Notes

- Dataset is sentence-level, multi-label.
- Labels follow European consumer law definitions (Lippi et al. 2019).
- TODO: check LexGLUE GitHub for split-by-document vs split-by-sentence.
- Micro-F1 is inflated by majority 'no unfair clause' class; report macro-F1 as primary metric.
- Test split per-class counts (38, 38, 38, 13, 23, 13, 16, 7) suggest stratification; dev sample will still be seeded from train+validation.
- Verified on 2026-10-XX against Hugging Face card coastalcph/lex_glue.