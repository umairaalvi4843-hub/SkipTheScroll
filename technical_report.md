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
  
  ## 8. Test Table

The following table documents 50 representative test inputs used to validate the pipeline. These cover normal cases (unfair clauses from the benchmark and pilot), edge cases (long documents, formatting variations, API rate limits), and invalid cases (empty input, non-legal text).

| Test ID | Input Type               | Test Input                                                                                | Expected Output                                                | Actual Output                                            | Pass or Fail |
| ------- | ------------------------ | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------- | ------------ |
| 1       | Normal (Benchmark)       | "We reserve the right to modify these Terms at any time without notice."                  | Unilateral change, high risk, verified                         | Unilateral change, high risk, verified                   | Pass         |
| 2       | Normal (Benchmark)       | "Any dispute shall be resolved by binding arbitration in Mumbai."                         | Arbitration, high risk, verified                               | Arbitration, high risk, verified                         | Pass         |
| 3       | Normal (Benchmark)       | "Your continued use of the Platform constitutes your acceptance of the amended Terms."    | Contract by using, medium risk, verified                       | Contract by using, medium risk, verified                 | Pass         |
| 4       | Normal (Benchmark)       | "The company may terminate your account at its sole discretion."                          | Unilateral termination, high risk, verified                    | Unilateral termination, high risk, verified              | Pass         |
| 5       | Normal (Benchmark)       | "We are not liable for any indirect or consequential damages."                            | Limitation of liability, high risk, verified                   | Limitation of liability, high risk, verified             | Pass         |
| 6       | Normal (Benchmark)       | "The terms shall be governed by the laws of the State of California."                     | Choice of law, medium risk, verified                           | Choice of law, medium risk, verified                     | Pass         |
| 7       | Normal (Benchmark)       | "We may remove any content that violates our community guidelines."                       | Content removal, medium risk, verified                         | Content removal, medium risk, verified                   | Pass         |
| 8       | Normal (Benchmark)       | "All disputes shall be subject to the exclusive jurisdiction of the courts of Bangalore." | Jurisdiction, medium risk, verified                            | Jurisdiction, medium risk, verified                      | Pass         |
| 9       | Normal (Benchmark)       | "By using this service you agree to be bound by these terms."                             | Contract by using, medium risk, verified                       | Contract by using, medium risk, verified                 | Pass         |
| 10      | Normal (Benchmark)       | "You agree to indemnify and hold harmless the company from any claims."                   | Limitation of liability, high risk, verified                   | Limitation of liability, high risk, verified             | Pass         |
| 11      | Normal (Pilot)           | Swiggy clause on unilateral changes.                                                      | Unilateral change, high risk, verified                         | Unilateral change, high risk, verified                   | Pass         |
| 12      | Normal (Pilot)           | Swiggy clause on account suspension without notice.                                       | Unilateral termination, high risk, verified                    | Unilateral termination, high risk, verified              | Pass         |
| 13      | Normal (Pilot)           | Swiggy clause on no refunds.                                                              | Limitation of liability, high risk, verified                   | Limitation of liability, high risk, verified             | Pass         |
| 14      | Normal (Pilot)           | Swiggy clause on broad content license.                                                   | Content removal, medium risk, verified                         | Content removal, medium risk, verified                   | Pass         |
| 15      | Normal (Pilot)           | Swiggy clause on promotional SMS.                                                         | Unilateral change, high risk, verified                         | Unilateral change, high risk, verified                   | Pass         |
| 16      | Normal (Pilot)           | Swiggy clause on delivery delays.                                                         | Limitation of liability, high risk, verified                   | Limitation of liability, high risk, verified             | Pass         |
| 17      | Normal (Dashboard)       | Paste Swiggy text into live Streamlit UI and click Analyse.                               | Render 7 risk cards with color coded pills and verified badges | 7 cards rendered with correct colors and verified badges | Pass         |
| 18      | Normal (Dashboard)       | Paste generic tech platform terms into live UI.                                           | Render 3 risk cards with correct categories                    | 3 cards rendered with correct categories                 | Pass         |
| 19      | Normal (Dashboard)       | Change prompt version to v2 and analyse.                                                  | Pipeline runs using v2 JSON schema prompt                      | v2 pipeline executed successfully                        | Pass         |
| 20      | Normal (Dashboard)       | Change prompt version to v3 and analyse.                                                  | Pipeline runs using v3 chaining prompt                         | v3 pipeline executed successfully                        | Pass         |
| 21      | Normal (Dashboard)       | Change prompt version to v4 and analyse.                                                  | Pipeline runs using v4 verifier prompt                         | v4 pipeline executed successfully                        | Pass         |
| 22      | Normal (Dashboard)       | Verify the disclaimer is visible at the top.                                              | Disclaimer "Information only, not legal advice" is displayed   | Disclaimer displayed correctly                           | Pass         |
| 23      | Normal (Dashboard)       | Verify the About tab loads project details.                                               | About tab shows project description and versions               | About tab loaded correctly                               | Pass         |
| 24      | Normal (Dashboard)       | Verify risk pills are color coded correctly.                                              | High risk is red, Medium is yellow, Low is green               | Colors matched the risk levels                           | Pass         |
| 25      | Normal (Dashboard)       | Verify Hindi explanations are generated.                                                  | Hindi text appears below the English explanation               | Hindi text generated successfully                        | Pass         |
| 26      | Edge (Long Text)         | 500 words of dense legal text from a real Indian app.                                     | Multiple clauses extracted, JSON remains valid                 | Clauses extracted, JSON valid                            | Pass         |
| 27      | Edge (Very Long Text)    | 1500 words of dense legal text.                                                           | Pipeline handles chunking and returns valid JSON               | Clauses extracted, JSON valid                            | Pass         |
| 28      | Edge (Language)          | Text containing legal jargon requiring Hinglish output.                                   | explanation_hi generated in Roman script or Devanagari         | explanation_hi generated in Hinglish                     | Pass         |
| 29      | Edge (Verifier)          | A quote where the model hallucinates one word differently from the source.                | Code side verifier flags quote as unverified                   | quote_verified set to false                              | Pass         |
| 30      | Edge (Whitespace)        | Quote with extra spaces or newlines.                                                      | Code side verifier normalizes whitespace and finds match       | quote_verified set to true                               | Pass         |
| 31      | Edge (Empty Clauses)     | Text with no unfair clauses.                                                              | clauses array is empty, valid JSON                             | clauses array empty, valid JSON                          | Pass         |
| 32      | Edge (Formatting)        | Model returns JSON wrapped in markdown code fences.                                       | _safe_json strips fences and parses JSON                       | JSON parsed successfully                                 | Pass         |
| 33      | Edge (API Limit)         | Trigger 429 rate limit by rapid calls.                                                    | Pipeline retries with exponential backoff                      | Pipeline waited and retried successfully                 | Pass         |
| 34      | Edge (Model Choice)      | Switch model from Gemini to GPT in config.                                                | Pipeline routes to OpenAI and returns JSON                     | Pipeline routed to GPT successfully                      | Pass         |
| 35      | Edge (Risk Mapping)      | Category not present in the risk mapping file.                                            | Default risk level applied, no crash                           | Default risk level applied, no crash                     | Pass         |
| 36      | Edge (Unicode)           | Input contains non English characters and emojis.                                         | Pipeline handles UTF-8 and returns valid JSON                  | UTF-8 handled, JSON valid                                | Pass         |
| 37      | Edge (JSON Error)        | Force model to return invalid JSON.                                                       | _safe_json catches error and returns empty clauses             | Empty clauses returned gracefully                        | Pass         |
| 38      | Edge (Timeout)           | Network timeout during API call.                                                          | Retry logic executes and succeeds                              | Retry logic succeeded on second attempt                  | Pass         |
| 39      | Edge (Clause Extraction) | Text with a clause split across paragraphs.                                               | Pipeline extracts the full quote across lines                  | Full quote extracted and verified                        | Pass         |
| 40      | Edge (Hindi Rubric)      | Input where Hindi output might be wrong.                                                  | Output still returns, flagged for human review                 | Output returned, flagged for M3 review                   | Pass         |
| 41      | Invalid (Empty)          | Empty text box in the dashboard.                                                          | App displays warning toast, no API call made                   | Warning displayed, no API call made                      | Pass         |
| 42      | Invalid (Non Legal)      | A recipe for chocolate cake instead of a legal document.                                  | No clauses flagged, valid JSON returned                        | No clauses flagged, valid JSON returned                  | Pass         |
| 43      | Invalid (Short)          | A 1 sentence input with no unfair clauses.                                                | No clauses flagged, empty clauses array                        | No clauses flagged, empty clauses array                  | Pass         |
| 44      | Invalid (Language)       | Input containing only emojis or special characters.                                       | No clauses flagged, valid JSON, summary generated              | No clauses flagged, valid JSON                           | Pass         |
| 45      | Invalid (URL)            | Input containing only a website URL.                                                      | No clauses flagged, valid JSON                                 | No clauses flagged, valid JSON                           | Pass         |
| 46      | Invalid (Code)           | Input containing raw Python code.                                                         | No clauses flagged, valid JSON                                 | No clauses flagged, valid JSON                           | Pass         |
| 47      | Invalid (HTML)           | Input containing HTML tags.                                                               | Pipeline strips HTML or treats as text, no crash               | Pipeline treated tags as text, no crash                  | Pass         |
| 48      | Invalid (Numbers)        | Input containing only numbers.                                                            | No clauses flagged, valid JSON                                 | No clauses flagged, valid JSON                           | Pass         |
| 49      | Invalid (Mixed)          | Input containing a mix of legal text and a random essay.                                  | Only legal clauses flagged, essay ignored                      | Legal clauses flagged, essay ignored                     | Pass         |
| 50      | Invalid (Repeat)         | Repeatedly paste the same Swiggy text 3 times.                                            | Pipeline handles duplicates and returns consistent JSON        | Results consistent across runs                           | Pass         |

## 7. Limitations

-   **Rate-limit-driven scope reduction:**free-tier daily quota.
-   **EU-law-based taxonomy:** UNFAIR-ToS categories follow European consumer law, not Indian law. Indian-context extra categories (data sharing, retention) are planned for M3.
-   **Contamination:** Gemini may have seen UNFAIR-ToS in training data. The Indian-context set is the cleaner test.
-   **Taxonomy gap:** clauses about broad content licenses have no matching UNFAIR-ToS category and get forced into the closest one. This is why Indian-context extra categories matter.
-   
