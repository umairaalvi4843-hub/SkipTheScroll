# ScrollLess— Skip the Scroll

Prompt Engineering mini-project, Bennett University, B.Tech Sem 5.
Problem C18: Terms and conditions in plain language.

## What this does
Compares prompt strategies (v0-v4) for detecting and explaining unfair
clauses in Terms of Service. Uses UNFAIR-ToS (LexGLUE) as a sentence-level
benchmark and our own Indian-context documents for full-document tests.

## Reproduce
1. `pip install -r requirements.txt`
2. Set API key in `.env` (see `configs/model_config.yaml` for model).
3. Run dataset audit: `python src/dataset_audit.py`
4. Run pipeline on a sample: `python src/pipeline.py --input data/indian_docs/sample.txt --version v4`
5. Run evaluation: `python src/evaluation.py --version v4 --split dev`

## Repo layout
- `prompts/` — v0 to v4 prompt files + CHANGELOG
- `data/` — samples, Indian docs (with URL + date), gold labels
- `src/` — pipeline, verifier, evaluation scripts
- `results/` — dataset audit, demo outputs, per-version eval CSVs
- `docs/` — design, diagrams, technical report, evidence screenshots
- `configs/` — model configuration

## Team
Skip the Scroll — see CONTRIBUTION_LOG.md

## Limitations
See docs/design.md section "Limitations".
