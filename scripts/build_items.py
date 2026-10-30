"""Build the stratified set of 600 gender items from the Glasgow Norms.

Glasgow GEND is a 1-7 scale (1 = very feminine, 7 = very masculine). Sense-tagged entries such as
"arm (limb)" are dropped because the model sees only the bare word. The scale is cut into 0.5-wide
bins and items are allocated as evenly as possible across bins, so the extremes are oversampled
relative to the natural distribution.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "glasgow" / "13428_2018_1099_MOESM2_ESM.csv"
SEED = 0
N_GENDER = 600
BIN_EDGES = np.arange(1.0, 7.0 + 0.5, 0.5)


def load_glasgow() -> pd.DataFrame:
    raw = pd.read_csv(RAW, header=None, skiprows=2, encoding="utf-8-sig")
    df = pd.DataFrame({"item": raw[0], "glasgow_gender": raw[26].astype(float)})
    df = df[~df["item"].str.contains(r"[()\s]", regex=True)]
    return df.drop_duplicates("item").reset_index(drop=True)


def allocate(counts: np.ndarray, n: int) -> np.ndarray:
    """Spread n as evenly as possible across bins, capped by what each bin holds."""
    alloc = np.zeros_like(counts)
    while alloc.sum() < n:
        open_bins = np.flatnonzero(alloc < counts)
        need = n - alloc.sum()
        share = max(need // len(open_bins), 1)
        for b in open_bins:
            add = min(share, counts[b] - alloc[b], n - alloc.sum())
            alloc[b] += add
            if alloc.sum() == n:
                break
    return alloc


def stratified_sample(df: pd.DataFrame, col: str, n: int, rng: np.random.Generator) -> pd.DataFrame:
    bins = pd.cut(df[col], BIN_EDGES, include_lowest=True, labels=False)
    counts = np.bincount(bins, minlength=len(BIN_EDGES) - 1)
    alloc = allocate(counts, n)
    picks = [df[bins == b].sample(k, random_state=rng.integers(2**31)) for b, k in enumerate(alloc) if k]
    return pd.concat(picks)


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    items = stratified_sample(load_glasgow(), "glasgow_gender", N_GENDER, rng)
    items = items.sort_values("item").reset_index(drop=True)
    items.to_csv(ROOT / "items.csv", index=False)
    print(len(items), pd.cut(items["glasgow_gender"], BIN_EDGES, include_lowest=True).value_counts(sort=False).to_dict())
