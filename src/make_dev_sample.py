"""Create a seeded dev sample from UNFAIR-ToS train+validation."""
from datasets import load_dataset
import pandas as pd
import random
from collections import Counter
from pathlib import Path

LABEL_NAMES = [
    "Limitation of liability", "Unilateral termination", "Unilateral change",
    "Content removal", "Contract by using", "Choice of law", "Jurisdiction", "Arbitration",
]
SEED = 42
TARGET_TOTAL = 80
TARGET_PER_CLASS = 25

def main():
    ds = load_dataset("coastalcph/lex_glue", "unfair_tos")
    pool = list(ds["train"]) + list(ds["validation"])
    random.seed(SEED)
    random.shuffle(pool)
    per_class = Counter()
    picked = []
    for row in pool:
        labels = row["labels"] if isinstance(row["labels"], list) else [row["labels"]]
        if any(per_class[LABEL_NAMES[l]] < TARGET_PER_CLASS for l in labels) and len(picked) < int(TARGET_TOTAL * 0.8):
            picked.append(row)
            for l in labels:
                per_class[LABEL_NAMES[l]] += 1
    for row in pool:
        if len(picked) >= TARGET_TOTAL:
            break
        labels = row["labels"] if isinstance(row["labels"], list) else [row["labels"]]
        if len(labels) == 0 and row not in picked:
            picked.append(row)
    df = pd.DataFrame([{
        "text": r["text"],
        "labels": r["labels"],
        "label_names": [LABEL_NAMES[l] for l in (r["labels"] if isinstance(r["labels"], list) else [r["labels"]])],
    } for r in picked])
    Path("data/gold").mkdir(parents=True, exist_ok=True)
    df.to_csv("data/gold/dev_sample.csv", index=False)
    print(f"Wrote {len(df)} rows to data/gold/dev_sample.csv")
    print("Class distribution:")
    print(Counter([c for r in df["label_names"] for c in r]))

if __name__ == "__main__":
    main()
