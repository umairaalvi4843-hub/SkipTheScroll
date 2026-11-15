"""Evaluate a prompt version on the dev sample."""
import json
import argparse
import pandas as pd
from pathlib import Path
from sklearn.metrics import f1_score
from tqdm import tqdm
from src.pipeline import run

LABEL_NAMES = [
    "Limitation of liability", "Unilateral termination", "Unilateral change",
    "Content removal", "Contract by using", "Choice of law", "Jurisdiction", "Arbitration",
]

def to_binary_set(label_names):
    return set(label_names)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--version", required=True)
    p.add_argument("--split", default="dev")
    args = p.parse_args()
    df = pd.read_csv(f"data/gold/{args.split}_sample.csv")
    y_true = []
    y_pred = []
    json_valid = 0
    quote_checks = []
    for _, row in tqdm(df.iterrows(), total=len(df)):
        text = row["text"]
        true_labels = eval(row["label_names"]) if isinstance(row["label_names"], str) else row["label_names"]
        out = run(text, args.version)
        if "json_error" not in out:
            json_valid += 1
        pred_labels = [c.get("category") for c in out.get("clauses", []) if c.get("category") in LABEL_NAMES]
        pred_labels = list(set(pred_labels))
        y_true.append(to_binary_set(true_labels))
        y_pred.append(to_binary_set(pred_labels))
        for c in out.get("clauses", []):
            quote_checks.append(c.get("quote_verified", False))
    rows = []
    for cat in LABEL_NAMES:
        tp = sum(1 for t, p in zip(y_true, y_pred) if cat in t and cat in p)
        fp = sum(1 for t, p in zip(y_true, y_pred) if cat not in t and cat in p)
        fn = sum(1 for t, p in zip(y_true, y_pred) if cat in t and cat not in p)
        prec = tp / (tp + fp) if (tp + fp) else 0
        rec = tp / (tp + fn) if (tp + fn) else 0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
        rows.append({"category": cat, "precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3), "support": sum(1 for t in y_true if cat in t)})
    per_class = pd.DataFrame(rows)
    macro_f1 = per_class["f1"].mean()
    y_true_bin = [1 if len(t) > 0 else 0 for t in y_true]
    y_pred_bin = [1 if len(p) > 0 else 0 for p in y_pred]
    binary_f1 = f1_score(y_true_bin, y_pred_bin)
    summary = {
        "version": args.version,
        "split": args.split,
        "n_rows": len(df),
        "macro_f1": round(macro_f1, 3),
        "binary_any_unfair_f1": round(binary_f1, 3),
        "json_valid_pct": round(100 * json_valid / len(df), 1),
        "quote_verified_pct": round(100 * sum(quote_checks) / len(quote_checks), 1) if quote_checks else None,
        "n_flagged_clauses": len(quote_checks),
    }
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    per_class.to_csv(out_dir / f"eval_{args.version}_{args.split}_per_class.csv", index=False)
    (out_dir / f"eval_{args.version}_{args.split}_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(per_class.to_string(index=False))

if __name__ == "__main__":
    main()
