"""Main pipeline: text in, structured JSON out. Supports v0 to v4."""
import json
import argparse
from pathlib import Path
from src.llm_client import load_prompt, call_llm
from src.verifier import verify_all

DISCLAIMER = "This is information only, not legal advice. Consult a qualified professional for decisions."

def run_v0(text):
    raw = call_llm(load_prompt("v0").format(text=text))
    return {"document_title": None, "summary": raw, "clauses": [], "disclaimer": DISCLAIMER}

def run_v1(text):
    raw = call_llm(load_prompt("v1").format(text=text))
    return {"document_title": None, "summary": raw, "clauses": [], "disclaimer": DISCLAIMER}

def run_v2(text):
    raw = call_llm(load_prompt("v2").format(text=text), expect_json=True)
    try:
        out = json.loads(raw)
    except json.JSONDecodeError:
        return {"document_title": None, "summary": "", "clauses": [], "disclaimer": DISCLAIMER, "json_error": raw}
    out["clauses"] = verify_all(out.get("clauses", []), text)
    out.setdefault("disclaimer", DISCLAIMER)
    return out

def run_v3(text):
    extract_raw = call_llm(load_prompt("v3", "extract").format(text=text), expect_json=True)
    try:
        candidates = json.loads(extract_raw)
    except json.JSONDecodeError:
        candidates = []
    classify_raw = call_llm(
        load_prompt("v3", "classify").format(candidates=json.dumps(candidates)),
        expect_json=True,
    )
    try:
        classified = json.loads(classify_raw)
    except json.JSONDecodeError:
        classified = {"clauses": []}
    summary = call_llm(load_prompt("v3", "summary").format(text=text))
    return {
        "document_title": None,
        "summary": summary,
        "clauses": classified.get("clauses", []),
        "disclaimer": DISCLAIMER,
    }

def run_v4(text):
    out = run_v3(text)
    if out["clauses"]:
        verify_raw = call_llm(
            load_prompt("v4", "verify").format(
                source=text,
                clauses=json.dumps(out["clauses"]),
            ),
            expect_json=True,
        )
        try:
            llm_verdict = json.loads(verify_raw).get("results", [])
        except json.JSONDecodeError:
            llm_verdict = []
        for c, v in zip(out["clauses"], llm_verdict):
            c["llm_says_found"] = v.get("found")
    out["clauses"] = verify_all(out["clauses"], text)
    return out

RUNNERS = {"v0": run_v0, "v1": run_v1, "v2": run_v2, "v3": run_v3, "v4": run_v4}

def run(text, version):
    return RUNNERS[version](text)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--version", default="v4", choices=list(RUNNERS))
    p.add_argument("--out", default=None)
    args = p.parse_args()
    text = Path(args.input).read_text()
    result = run(text, args.version)
    out_path = args.out or f"results/demo/{Path(args.input).stem}_{args.version}.json"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Wrote {out_path}")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
