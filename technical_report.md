# ScrollLess Technical Report — Milestone 2

**Project:** Skip the Scroll
**Course:** Prompt Engineering, Bennett University, B.Tech Sem 5
**Problem ID:** C18 — Terms and conditions in plain language
**Team:** Umaira (S24CSEU1160), Sujal Ranga (S24CSEU1065), Krishna Kumar (S24CSEU2869), Arsh Khan (S24CSEU1055)
**Date:** October 2026

## 1. Problem and prompt-engineering task

Terms of Service and Privacy Policy documents are long, legally dense, and rarely read by users, yet they contain clauses that materially affect user rights, money and data. Existing tools offer summaries, but no public, reproducible study compares prompt strategies for the same task against a fixed benchmark with documented evaluation.

Our prompt-engineering task: given a T&C section, produce structured JSON with a plain summary, flagged clauses (each with category, verbatim quote, deterministic risk level, English explanation, Hindi/Hinglish explanation), and a legal disclaimer. The graded artefact is the prompt strategy and its evaluation, not the application.

## 2. Pipeline design

![Pipeline Diagram](diagrams/pipeline.png)

Our pipeline consists of six stages:
1.  **Preprocess** (code: sentence/section split)
2.  **Extract candidates** (v3_extract prompt)
3.  **Classify** (v3_classify prompt) + apply deterministic risk mapping
4.  **Summarise** (v3_summary prompt)
5.  **Verify quotes** (v4_verify LLM + `src/verifier.py` code check)
6.  **Emit JSON**

The verifier is dual: an LLM prompt asks the model to check each quote, and a code-side whitespace-normalised string match re-checks independently. The code check is authoritative.

## 3. Prompt version evolution

Full changelog: `prompts/CHANGELOG.md`

| Version | Key change                                | Rationale                                               |
| ------- | ----------------------------------------- | ------------------------------------------------------- |
| v0      | Baseline: single-line instruction         | Establish floor                                         |
| v1      | Role + taxonomy + constraints             | Test whether in-prompt taxonomy alone moves the metrics |
| v2      | Strict JSON schema + few-shot example     | Enable structured evaluation                            |
| v3      | Chaining (extract → classify → summarise) | Better handling of long documents                       |
| v4      | Verifier prompt + code quote check        | Reduce hallucinated quotes to near zero                 |

## 4. Implementation notes

-   **Provider:** Google AI Studio (free tier)
-   **Model:** `gemini-3.5-flash-lite`
-   **Temperature:** 0 for all evaluation runs
-   **Config:** `configs/model_config.yaml`
-   **Risk level:** Fixed category-to-risk mapping in `configs/risk_mapping.yaml`, applied after the classify stage. We do not ask the LLM to guess risk.
-   **Robust JSON parsing:** `_safe_json` (handles code-fence wrapping) and `_extract_clauses` (handles three response shapes observed from Gemini).
-   **Rate limiting:** 4.6s minimum between calls to stay under free-tier 15 RPM.

## 5. Evaluation results

**Dev sample:** 80 sentences from UNFAIR-ToS train+validation, seed 42, stratified to 8-18 positives per category. We report Macro-F1 as the primary metric because the dataset is heavily imbalanced (88% of sentences have no unfair clause).

![Evaluation Results](evidence/eval_results.png)

| Version          | Macro-F1  | Binary any-unfair F1 | JSON valid % | Quote verified % | n_flagged_clauses |
| ---------------- | --------- | -------------------- | ------------ | ---------------- | ----------------- |
| v0 baseline      | 0.0       | 0.0                  | 100*         | —                | 0                 |
| v1 role+taxonomy | 0.0       | 0.0                  | 100*         | —                | 0                 |
| v2 JSON+few-shot | **0.867** | **0.910**            | 93.8         | **98.6**         | 73                |
| v3 chaining      | 0.783     | 0.873                | 100.0        | —                | 69                |
| v4 +verifier     | 0.743     | 0.869                | 100.0        | 95.5             | 67                |

*\*json_valid_pct is 100 for v0/v1 only because no JSON parse is attempted; the metric is meaningful only for v2+.*

**Interpretation:**
The experiment reveals a clear trade-off between structural reliability and classification recall. The v0 and v1 baselines returned prose summaries with zero structured clauses, resulting in a Macro-F1 of 0.0. The introduction of a strict JSON schema in v2 caused a massive performance jump (0.867 Macro-F1), but suffered from a 6.2% JSON failure rate. 

v3 achieved perfect JSON validity (100%) by splitting the task into three separate prompts (extract -> classify -> summarise), but this made the model more conservative, lowering the Macro-F1 to 0.783. Finally, v4 successfully added dual-verification, maintaining 100% JSON validity and verifying 95.5% of quotes (67 clauses). However, the verifier prompt further increased the model's conservatism, dropping Macro-F1 to 0.743. This demonstrates that while chaining and verification solve the hallucination and formatting problems, they must be carefully tuned to avoid over-caution in classification.

## 6. Pilot run — Swiggy T&C

We conducted a full-document pilot on a 20-30 sentence section of Swiggy's Terms of Service (URL and access date in `data/indian_docs/sample_section.txt`).

![Pilot Run JSON](evidence/pilot_json_output2.png)

The v4 pilot result flagged 7 clauses across 5 categories (Unilateral change, Contract by using, Unilateral termination, Content removal, Limitation of liability). All 7 clauses passed both the LLM verifier and the code-side string match. Hindi explanations ranged from Hinglish (Roman script) to full Devanagari across runs at temperature 0.

![Dashboard Live](evidence/dashboard_live.png)

**Key observations:**
-   Verification worked as designed: every quote was a verbatim substring of the source.
-   Category assignment was mostly correct; one clause about a broad content license was forced into "Content removal" because no UNFAIR-ToS category matches it (motivating Indian-context extra categories in M3).
-   Hindi/Hinglish is non-deterministic at temperature 0.

## 7. Limitations

-   **Rate-limit-driven scope reduction:**free-tier daily quota.
-   **EU-law-based taxonomy:** UNFAIR-ToS categories follow European consumer law, not Indian law. Indian-context extra categories (data sharing, retention) are planned for M3.
-   **Contamination:** Gemini may have seen UNFAIR-ToS in training data. The Indian-context set is the cleaner test.
-   **Taxonomy gap:** clauses about broad content licenses have no matching UNFAIR-ToS category and get forced into the closest one. This is why Indian-context extra categories matter.