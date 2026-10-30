"""Path-specific directions: each concept set against the other two, pooled.

  d_X = mean(moderate profile + X sentence) - mean(moderate profile + sentences of the other two sets),
  X in {commitment, mission, leaving}, over the estimation profiles, from the sentence-token means
  cached by scripts/profile_directions.py. The three sets have equal size, so the three directions sum
  to zero and lie in one plane. Stability comes from a fixed-seed 20/20 split of each set's sentences.

Outputs: directions/profile_it_pathspecific_L{8,13}.npz (keys commitment, mission, leaving, capability,
{name}_half_a, {name}_half_b), results/capcom/path_*.csv.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from profile_directions import CACHE, DIRS, LAYERS, RES, SENT_SETS, cos, directions, splits, unit  # noqa: E402

SEED = 0


def sentence_means(L, pairs):
    S = np.load(CACHE / f"sentences_L{L}.npy")
    sidx = pd.read_csv(CACHE / "sentences_index.csv")
    keep = sidx["pair_id"].isin(pairs).to_numpy()
    per = (pd.DataFrame(S[keep]).assign(set=sidx["set"][keep].to_numpy(), idx=sidx["idx"][keep].to_numpy())
           .groupby(["set", "idx"]).mean())
    return {s: per.loc[s].to_numpy() for s in SENT_SETS}


def path_dirs(vecs):
    return {x: vecs[x].mean(0) - np.concatenate([vecs[o] for o in SENT_SETS if o != x]).mean(0) for x in SENT_SETS}


def main():
    est = splits()["estimation"]
    items = pd.read_csv(ROOT / "items_capcom.csv")
    words = (ROOT / "data" / "activations_it_capcom" / "words.txt").read_text().split()
    widx = {w: i for i, w in enumerate(words)}
    rng = np.random.default_rng(SEED)
    half = {s: rng.permutation(40) for s in SENT_SETS}
    cos_rows, stab_rows, proj_rows, val_rows = [], [], [], []
    for L in LAYERS:
        vecs = sentence_means(L, est)
        d = path_dirs(vecs)
        d_a = path_dirs({s: v[half[s][:20]] for s, v in vecs.items()})
        d_b = path_dirs({s: v[half[s][20:]] for s, v in vecs.items()})
        cap = directions(L, est)["capability"]
        np.savez(DIRS / f"profile_it_pathspecific_L{L}.npz", capability=cap, **d,
                 **{f"{k}_half_a": v for k, v in d_a.items()}, **{f"{k}_half_b": v for k, v in d_b.items()})
        for a, b in (("commitment", "mission"), ("commitment", "leaving"), ("mission", "leaving")):
            cos_rows.append(dict(layer=L, pair=f"{a}~{b}", cosine=cos(d[a], d[b])))
        for x in SENT_SETS:
            cos_rows.append(dict(layer=L, pair=f"capability~{x}", cosine=cos(cap, d[x])))
            stab_rows.append(dict(layer=L, direction=x, cos_half_a_vs_half_b=cos(d_a[x], d_b[x]),
                                  norm=float(np.linalg.norm(d[x]))))
        X = np.load(ROOT / "data" / "activations_it_capcom" / f"acts_L{L}.npy").mean(1)
        for x in SENT_SETS:
            pr = X @ unit(d[x])
            p = items.assign(proj=[pr[widx[w]] for w in items["word"]])
            nm = p.loc[p["list"] == "neutral", "proj"].mean()
            for lst, g in p.groupby("list", sort=False):
                proj_rows.append(dict(layer=L, direction=x, list=lst, n=len(g), mean_proj=g["proj"].mean(),
                                      sd_proj=g["proj"].std(), mean_minus_neutral=g["proj"].mean() - nm))
            rated = p.dropna(subset=["warriner_valence"])
            r, pval = stats.pearsonr(rated["proj"], rated["warriner_valence"])
            val_rows.append(dict(layer=L, direction=x, n_words=len(rated), r_proj_valence=r, p=pval))
    out = dict(path_cosines=cos_rows, path_stability=stab_rows, path_word_projections=proj_rows,
               path_valence_correlation=val_rows)
    pd.set_option("display.width", 220, "display.precision", 3)
    for k, rows in out.items():
        df = pd.DataFrame(rows)
        df.to_csv(RES / f"{k}.csv", index=False)
        print(k)
        print(df.pivot_table(index=["layer", "direction"], columns="list", values="mean_minus_neutral")
              if k == "path_word_projections" else df.to_string(index=False))


if __name__ == "__main__":
    main()
