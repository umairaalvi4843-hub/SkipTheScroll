# Pilot run — v2 on Swiggy T&C section (2026-10-15)

## What worked
- Produced valid JSON matching schema.
- Verbatim quotes verified against source (quote_verified=true on all clauses shown).
- Correct categories: Unilateral change, Contract by using, Unilateral termination, Content removal.
- Hindi/Hinglish explanations are genuine and readable.

## What needs tuning
- risk_level looks heuristic and inconsistent (e.g. "unilateral termination" marked high but "unilateral change" only medium; both arguably high).
- No gold labels for risk_level in UNFAIR-ToS, so v3 will replace model-invented risk with a deterministic category-to-risk mapping.

## Evaluation note — json_valid_pct on v0/v1
v0 and v1 return prose summaries by design (clauses: []). The eval script
reports json_valid_pct=100% because no parse was attempted, not because
output is valid JSON. This metric is meaningful only for v2+ (structured
output versions). Noted in report as a limitation of the metric for prose
baselines.