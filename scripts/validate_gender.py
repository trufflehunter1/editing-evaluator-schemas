"""Minimal validation: the gender direction against Glasgow GEND, and the evaluator's ratings.

Gender direction = mean(top-100 masculine words) - mean(top-100 feminine words), at layers 4, 8, 13 and 18, from
item vectors mean-pooled over tokens and averaged over the four prompts. Each item's projection on the unit
direction is correlated with Glasgow GEND, over all 600 items and over the 400 not used to build the direction.

Runs what is missing, in order: scripts/extract_activations.py for both models, scripts/behavioral_ratings.py,
then scripts/compare_models.py. Outputs in --out (default results/validation/): gender_direction_glasgow.csv,
evaluator_ratings.csv, evaluator_glasgow.csv, base_vs_it_cosines.csv; and directions/{base,it}_meanpool_gender_L*.npz.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.items import load_items, pole_sets  # noqa: E402

ACTS = {"base": ROOT / "data" / "activations", "it": ROOT / "data" / "activations_it"}
LAYERS = [4, 8, 13, 18]


def run(script, *args):
    subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args], check=True)


def correlations(model):
    words = (ACTS[model] / "words.txt").read_text().split()
    idx = {w: i for i, w in enumerate(words)}
    items = load_items()
    masc, fem = pole_sets()
    rest = items[~items["item"].isin(masc + fem)]
    rows = []
    for L in LAYERS:
        X = np.load(ACTS[model] / f"acts_L{L}.npy").mean(1)
        d = X[[idx[w] for w in masc]].mean(0) - X[[idx[w] for w in fem]].mean(0)
        np.savez(ROOT / "directions" / f"{model}_meanpool_gender_L{L}.npz", gender_direction=d)
        proj = X @ (d / np.linalg.norm(d))
        for name, sub in (("all", items), ("not_in_direction", rest)):
            x = proj[[idx[w] for w in sub["item"]]]
            rows.append(dict(model=model, layer=L, items=name, n=len(sub), pearson_r=stats.pearsonr(x, sub["glasgow_gender"])[0],
                             spearman_rho=stats.spearmanr(x, sub["glasgow_gender"])[0]))
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "validation")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    for model in ACTS:
        if not (ACTS[model] / "acts_L18.npy").exists():
            run("extract_activations.py", "--model", model)
    corr = pd.DataFrame(correlations("base") + correlations("it"))
    corr.to_csv(a.out / "gender_direction_glasgow.csv", index=False)
    print(corr.to_string(index=False))
    run("behavioral_ratings.py", "--out", str(a.out))
    run("compare_models.py", "--out", str(a.out))
