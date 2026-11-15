# Prompt Version Changelog

## v0 — baseline
- Single-line instruction. No role, no categories, no schema.
- Purpose: establish a floor for comparison.

## v1 — role + taxonomy
- Added role (consumer-rights assistant).
- Added the 8 UNFAIR-ToS categories as an in-prompt list.
- Added constraints: only flag what is in text, no legal advice.
- Expected effect: better category coverage, fewer invented clauses.

## v2 — structured output + few-shot
- Added strict JSON schema.
- Added one worked example clause object.
- Added exact-quote rule.
- Expected effect: valid JSON rate up, hallucinated quotes down.

## v3 — chaining
- Split into three prompts: extract candidates, classify, summarise.
- Each stage's output feeds the next.
- Expected effect: better recall on long documents, cleaner JSON per stage.

## v4 — verifier stage
- Added a verifier prompt plus a programmatic string-match check (src/verifier.py).
- Any clause whose quote is not found verbatim is marked quote_verified=false.
- Expected effect: hallucinated-quote rate drops toward zero by construction.
