"""Main pipeline: text in, structured JSON out. Supports v0 to v4 with --debug."""
import json
import argparse
from pathlib import Path
from src.llm_client import load_prompt, call_llm
from src.verifier import verify_all

DISCLAIMER = "This is information only, not legal advice. Consult a qualified professional for decisions."

def _debug_dump(name, content, debug_dir):
    if debug_dir:
        p = Path(debug_dir)
        p.mkdir(parents=True, exist_ok=True)
        (p / f"{name}.txt").write_text(content if isinstance(content, str) else json.dumps(content, indent=2))

def _safe_json(raw, default):
    """Try to parse JSON; handle ```json fences and single-object wrapping."""
    if raw is None:
        return default
    s = raw.strip()
    if s.startswith("```"):
        # strip code fences
        s = s.strip("`")
        if s.lower().startswith("json"):
            s = s[4:]
        s = s.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return default

def _extract_clauses(classified):
    """Handle all the shapes Gemini returns."""
    if isinstance(classified, list):
        return classified
    if isinstance(classified, dict):
        if "clauses" in classified and isinstance(classified["clauses"], list):
            return classified["clauses"]
        # Sometimes wrapped as {"response": {"clauses": [...]}}
        for v in classified.values():
            if isinstance(v, dict) and "clauses" in v and isinstance(v["clauses"], list):
                return v["clauses"]
            if isinstance(v, list):
                return v
    return []

def run_v0(text, debug_dir=None):
    raw = call_llm(load_prompt("v0").format(text=text))
    return {"document_title": None, "summary": raw, "clauses": [], "disclaimer": DISCLAIMER}

def run_v1(text, debug_dir=None):
    raw = call_llm(load_prompt("v1").format(text=text))
    return {"document_title": None, "summary": raw, "clauses": [], "disclaimer": DISCLAIMER}

def run_v2(text, debug_dir=None):
    raw = call_llm(load_prompt("v2").format(text=text), expect_json=True)
    _debug_dump("v2_raw", raw, debug_dir)
    out = _safe_json(raw, {"document_title": None, "summary": "", "clauses": [], "disclaimer": DISCLAIMER, "json_error": raw})
    out["clauses"] = verify_all(_extract_clauses(out.get("clauses", [])), text)
    out.setdefault("disclaimer", DISCLAIMER)
    return out

def run_v3(text, debug_dir=None):
    extract_raw = call_llm(load_prompt("v3", "extract").format(text=text), expect_json=True)
    _debug_dump("v3_extract_raw", extract_raw, debug_dir)
    candidates = _safe_json(extract_raw, [])
    if not isinstance(candidates, list):
        candidates = _extract_clauses(candidates)

    classify_raw = call_llm(
        load_prompt("v3", "classify").format(candidates=json.dumps(candidates)),
        expect_json=True,
    )
    _debug_dump("v3_classify_raw", classify_raw, debug_dir)
    classified = _safe_json(classify_raw, {"clauses": []})
    clauses = _extract_clauses(classified)

    summary = call_llm(load_prompt("v3", "summary").format(text=text))
    _debug_dump("v3_summary_raw", summary, debug_dir)

    return {
        "document_title": None,
        "summary": summary,
        "clauses": clauses,
        "disclaimer": DISCLAIMER,
    }

def run_v4(text, debug_dir=None):
    out = run_v3(text, debug_dir=debug_dir)
    if out["clauses"]:
        verify_raw = call_llm(
            load_prompt("v4", "verify").format(
                source=text,
                clauses=json.dumps(out["clauses"]),
            ),
            expect_json=True,
        )
        _debug_dump("v4_verify_raw", verify_raw, debug_dir)
        verdict = _safe_json(verify_raw, {"results": []})
        llm_verdict = verdict.get("results", []) if isinstance(verdict, dict) else verdict
        for c, v in zip(out["clauses"], llm_verdict):
            c["llm_says_found"] = v.get("found") if isinstance(v, dict) else None
    out["clauses"] = verify_all(out["clauses"], text)
    return out

RUNNERS = {"v0": run_v0, "v1": run_v1, "v2": run_v2, "v3": run_v3, "v4": run_v4}

def run(text, version, debug_dir=None):
    return RUNNERS[version](text, debug_dir=debug_dir)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--version", default="v4", choices=list(RUNNERS))
    p.add_argument("--out", default=None)
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    text = Path(args.input).read_text()
    debug_dir = f"results/demo/debug_{Path(args.input).stem}_{args.version}" if args.debug else None
    result = run(text, args.version, debug_dir=debug_dir)

    out_path = args.out or f"results/demo/{Path(args.input).stem}_{args.version}.json"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Wrote {out_path}")
    if debug_dir:
        print(f"Debug dumps in {debug_dir}/")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
