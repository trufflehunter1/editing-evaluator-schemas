"""Cosine between the gender direction of the base model and of the instruction-tuned model, per layer.

Reads directions/{base,it}_meanpool_gender_L{L}.npz (written by scripts/validate_gender.py).
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DIRS = ROOT / "directions"
LAYERS = [4, 8, 13, 18]


def cos(u, v):
    return float(u @ v / np.linalg.norm(u) / np.linalg.norm(v))


def compare():
    return pd.DataFrame([dict(layer=L, cos_base_it=cos(np.load(DIRS / f"base_meanpool_gender_L{L}.npz")["gender_direction"],
                                                       np.load(DIRS / f"it_meanpool_gender_L{L}.npz")["gender_direction"]))
                         for L in LAYERS])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "validation")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    df = compare()
    df.to_csv(a.out / "base_vs_it_cosines.csv", index=False)
    print(df.to_string(index=False))
