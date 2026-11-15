"""Audit the UNFAIR-ToS dataset and save findings to results/dataset_audit.md"""
from datasets import load_dataset
import json
from collections import Counter
from pathlib import Path

LABEL_NAMES = [
    "Limitation of liability",
    "Unilateral termination",
    "Unilateral change",
    "Content removal",
    "Contract by using",
    "Choice of law",
    "Jurisdiction",
    "Arbitration",
]

def audit_split(split_name, data):
    rows = data[split_name]
    n = len(rows)
    label_counts = Counter()
    empty = 0
    multi = 0
    for row in rows:
        labels = row["labels"]
        if isinstance(labels, int):
            labels = [labels]
        if len(labels) == 0:
            empty += 1
        elif len(labels) > 1:
            multi += 1
        for l in labels:
            label_counts[LABEL_NAMES[l]] += 1
    return {
        "split": split_name,
        "n_rows": n,
        "empty_label_pct": round(100 * empty / n, 2) if n else 0,
        "multi_label_pct": round(100 * multi / n, 2) if n else 0,
        "per_class_counts": dict(label_counts),
    }

def main():
    print("Loading UNFAIR-ToS...")
    ds = load_dataset("coastalcph/lex_glue", "unfair_tos")
    print(f"Columns: {ds['train'].column_names}")
    print(f"Sample row: {ds['train'][0]}")
    results = {"columns": ds["train"].column_names, "splits": []}
    for split in ["train", "validation", "test"]:
        results["splits"].append(audit_split(split, ds))
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "dataset_audit.json", "w") as f:
        json.dump(results, f, indent=2)
    lines = ["# Dataset Audit — UNFAIR-ToS (coastalcph/lex_glue, config: unfair_tos)\n"]
    lines.append(f"Columns: `{results['columns']}`\n")
    lines.append("\n## Split summary\n")
    lines.append("| Split | Rows | Empty label % | Multi-label % |")
    lines.append("|---|---|---|---|")
    for s in results["splits"]:
        lines.append(f"| {s['split']} | {s['n_rows']} | {s['empty_label_pct']} | {s['multi_label_pct']} |")
    lines.append("\n## Per-class counts\n")
    lines.append("| Category | Train | Validation | Test |")
    lines.append("|---|---|---|---|")
    for cat in LABEL_NAMES:
        row = [cat]
        for s in results["splits"]:
            row.append(str(s["per_class_counts"].get(cat, 0)))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("\n## Notes\n")
    lines.append("- Dataset is sentence-level, multi-label.")
    lines.append("- Labels follow European consumer law definitions (Lippi et al. 2019).")
    lines.append("- TODO: check LexGLUE GitHub for split-by-document vs split-by-sentence.")
    lines.append("- Micro-F1 is inflated by majority 'no unfair clause' class; report macro-F1 as primary metric.")
    with open(out_dir / "dataset_audit.md", "w") as f:
        f.write("\n".join(lines))
    print("Saved results/dataset_audit.md and results/dataset_audit.json")

if __name__ == "__main__":
    main()
