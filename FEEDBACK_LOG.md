# Feedback Log — Skip the Scroll

## Conversation 1 — October 2026
**Who:** Senior Student (Computer Science)
**Where:** In person project review
**What they said:**
- Emphasized that since modern LLMs are powerful, the project must show a clear progression of prompt iterations (v0 to v4) to prove that prompt engineering is the core work.
- Raised a crucial point about the "risk level" output: if the LLM just guesses what is "high" or "low" risk, it is not scientifically measurable. 
- Warned that Hindi/Hinglish outputs can be inconsistent and subjective, so we need a human grading rubric rather than just trusting the model.
- Praised the automatic quote verification logic, noting it directly solves the hallucination problem that most LLM projects ignore.

**What we changed in response:**
- Implemented a deterministic, hardcoded category-to-risk mapping (`configs/risk_mapping.yaml`) so the model cannot guess risk levels. 
- Created a strict dev/test split to ensure the high F1 scores were not due to contamination.
- Kept the quote verification as a core feature (using both LLM and code string-matching).
- Added a human evaluation rubric plan for Hindi outputs to the M3 roadmap.