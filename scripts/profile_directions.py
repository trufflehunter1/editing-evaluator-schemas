"""Concept directions from minimal contrasts in gemma-2-2b-it (layers 8 and 13).

Prompt format. Gemma 2's chat template has no system role, so the system context goes first in the
user turn, then a blank line, then the profile. When a sentence is added it follows the profile
after a blank line. The generation prompt is appended. Activations are the residual stream after
block L (HF hidden_states[L + 1]).

Pairs are split by a fixed seed into estimation (pair 1 + 9 others) and held-out (10). The
estimation set is also split 5/5 by seed for a split-half check.

  capability = mean over pairs of (extreme - moderate), using the mean over the profile tokens.
  commitment / mission / leaving = mean(moderate profile + pole sentence) - mean(moderate profile
      + neutral sentence), using the mean over the sentence tokens. All 40 pole sentences and all
      40 neutral sentences are crossed with every moderate profile in the split.

The script reports, per split and layer, the cosines of capability with commitment, mission and leaving.
It also projects the single-word lists of items_capcom.csv (IT model, K&B prompts, mean-pooled,
from data/activations_it_capcom/) onto each unit direction, and correlates the projection with
Warriner valence.

Outputs: data/profile_acts/ (cached activations, gitignored), directions/profile_*.npz,
results/capcom/*.csv.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / ".hf_cache"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from scipy import stats  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

sys.path.insert(0, str(ROOT))
from src.device import get_device  # noqa: E402
from src.items import attach_valence  # noqa: E402

MODEL = "google/gemma-2-2b-it"
LAYERS = [8, 13]
SEED, BATCH = 0, 8
STIM, CACHE, RES, DIRS = ROOT / "stimuli", ROOT / "data" / "profile_acts", ROOT / "results" / "capcom", ROOT / "directions"
SENT_SETS = ["commitment", "mission", "leaving"]


def splits():
    rng = np.random.default_rng(SEED)
    others = rng.permutation(np.arange(2, 21)).tolist()
    est, held = [1] + others[:9], others[9:]
    half = rng.permutation(est[1:]).tolist()
    return dict(estimation=sorted(est), heldout=sorted(held),
                est_half_a=sorted([1] + half[:4]), est_half_b=sorted(half[4:]))


def user_text(system, profile, sentence=None):
    return system + "\n\n" + profile + ("" if sentence is None else "\n\n" + sentence)


@torch.no_grad()
def extract(jobs, tok, model, device):
    """jobs: list of (user_text, span_text); returns {L: [n, d]} means over tokens overlapping span_text."""
    out = {L: [] for L in LAYERS}
    tok.padding_side = "right"
    for s in range(0, len(jobs), BATCH):
        batch = jobs[s:s + BATCH]
        texts = [tok.apply_chat_template([{"role": "user", "content": u}], tokenize=False, add_generation_prompt=True)
                 for u, _ in batch]
        enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False, return_offsets_mapping=True)
        offs = enc.pop("offset_mapping").tolist()
        enc = enc.to(device)
        hs = model(**enc, output_hidden_states=True, logits_to_keep=1).hidden_states
        masks = torch.zeros(enc["input_ids"].shape, device=device)
        for b, ((u, span), text) in enumerate(zip(batch, texts)):
            c0 = text.rindex(span)
            c1 = c0 + len(span)
            n = int(enc["attention_mask"][b].sum())
            idx = [t for t in range(n) if offs[b][t][0] < c1 and offs[b][t][1] > c0]
            assert idx
            masks[b, idx] = 1
        m = masks.unsqueeze(-1)
        for L in LAYERS:
            out[L].append(((hs[L + 1].float() * m).sum(1) / m.sum(1)).cpu().numpy())
        if (s // BATCH) % 10 == 0:
            print(f"{s + len(batch)}/{len(jobs)}", flush=True)
    return {L: np.concatenate(v) for L, v in out.items()}


def run_extraction():
    load_dotenv(ROOT / ".env")
    token, device = os.environ["HF_TOKEN"], get_device()
    tok = AutoTokenizer.from_pretrained(MODEL, token=token)
    model = AutoModelForCausalLM.from_pretrained(MODEL, token=token, dtype=torch.bfloat16,
                                                 attn_implementation="eager").to(device).eval()
    system = (STIM / "system_prompt.txt").read_text().strip()
    prof = pd.read_csv(STIM / "profiles.csv")
    sents = pd.read_csv(STIM / "sentences.csv")
    CACHE.mkdir(parents=True, exist_ok=True)

    if not (CACHE / "profiles_L8.npy").exists():
        acts = extract([(user_text(system, t), t) for t in prof["text"]], tok, model, device)
        for L, a in acts.items():
            np.save(CACHE / f"profiles_L{L}.npy", a)
        prof[["pair_id", "level"]].to_csv(CACHE / "profiles_index.csv", index=False)
    if not (CACHE / "sentences_L8.npy").exists():
        mod = prof[prof["level"] == "moderate"]
        idx = [(r.pair_id, s.set, s.idx) for r in mod.itertuples() for s in sents.itertuples()]
        jobs = [(user_text(system, r.text, s.sentence), s.sentence) for r in mod.itertuples() for s in sents.itertuples()]
        acts = extract(jobs, tok, model, device)
        for L, a in acts.items():
            np.save(CACHE / f"sentences_L{L}.npy", a)
        pd.DataFrame(idx, columns=["pair_id", "set", "idx"]).to_csv(CACHE / "sentences_index.csv", index=False)


def unit(v):
    return v / np.linalg.norm(v)


def cos(u, v):
    return float(unit(u) @ unit(v))


def directions(L, pairs):
    P = np.load(CACHE / f"profiles_L{L}.npy")
    pidx = pd.read_csv(CACHE / "profiles_index.csv")
    S = np.load(CACHE / f"sentences_L{L}.npy")
    sidx = pd.read_csv(CACHE / "sentences_index.csv")
    ext = P[[pidx.index[(pidx.pair_id == p) & (pidx.level == "extreme")][0] for p in pairs]]
    mod = P[[pidx.index[(pidx.pair_id == p) & (pidx.level == "moderate")][0] for p in pairs]]
    d = {"capability": (ext - mod).mean(0)}
    in_split = sidx["pair_id"].isin(pairs).to_numpy()
    neutral = S[in_split & (sidx["set"] == "neutral").to_numpy()].mean(0)
    for s in SENT_SETS:
        d[s] = S[in_split & (sidx["set"] == s).to_numpy()].mean(0) - neutral
    return d


def sentence_spread(L, pairs):
    """Per-sentence vectors (mean over the split's moderate profiles) and their spread and overlap.

    Reference (i), pole sets only: difference vector = sentence - neutral-set mean, and the set
    direction is the mean of those differences. Reference (ii), all four sets: difference vector =
    sentence - grand mean of all 160 sentences. Spread is the mean and SD of each sentence's cosine
    with its set direction. Overlap is the mean cosine between sentence difference vectors across two
    sets; within-set values leave out each sentence's cosine with itself.
    """
    S = np.load(CACHE / f"sentences_L{L}.npy")
    sidx = pd.read_csv(CACHE / "sentences_index.csv")
    keep = sidx["pair_id"].isin(pairs).to_numpy()
    per = (pd.DataFrame(S[keep]).assign(set=sidx["set"][keep].to_numpy(), idx=sidx["idx"][keep].to_numpy())
           .groupby(["set", "idx"]).mean())
    sets = ["mission", "leaving", "commitment", "neutral"]
    vecs = {s: per.loc[s].to_numpy() for s in sets}
    grand = np.concatenate(list(vecs.values())).mean(0)
    refs = {"vs_neutral_mean": vecs["neutral"].mean(0), "vs_grand_mean": grand}
    spread, overlap = [], []
    for ref_name, ref in refs.items():
        use = sets if ref_name == "vs_grand_mean" else sets[:3]
        diffs = {s: vecs[s] - ref for s in use}
        normed = {s: d / np.linalg.norm(d, axis=1, keepdims=True) for s, d in diffs.items()}
        for s in use:
            c = normed[s] @ unit(diffs[s].mean(0))
            spread.append(dict(layer=L, reference=ref_name, set=s, n=len(c), mean_cos_to_set_direction=c.mean(),
                               sd_cos=c.std(ddof=1)))
        for i, a in enumerate(use):
            for b in use[i:]:
                M = normed[a] @ normed[b].T
                vals = M[~np.eye(len(M), dtype=bool)] if a == b else M.ravel()
                overlap.append(dict(layer=L, reference=ref_name, set_a=a, set_b=b, mean_cos=vals.mean(),
                                    sd_cos=vals.std(ddof=1)))
    return spread, overlap


def analyze():
    RES.mkdir(parents=True, exist_ok=True)
    DIRS.mkdir(exist_ok=True)
    sp = splits()
    items = attach_valence(pd.read_csv(ROOT / "items_capcom.csv"))
    words = (ROOT / "data" / "activations_it_capcom" / "words.txt").read_text().split()
    widx = {w: i for i, w in enumerate(words)}
    names = ["capability"] + SENT_SETS
    cos_rows, stab_rows, proj_rows, val_rows, spread_rows, overlap_rows = [], [], [], [], [], []
    for L in LAYERS:
        D = {k: directions(L, v) for k, v in sp.items()}
        spr, ovl = sentence_spread(L, sp["estimation"])
        spread_rows += spr
        overlap_rows += ovl
        for k, d in D.items():
            np.savez(DIRS / f"profile_it_{k}_L{L}.npz", **d)
            for s in SENT_SETS:
                cos_rows.append(dict(layer=L, split=k, pair=f"capability~{s}", cosine=cos(d["capability"], d[s])))
            for a, b in (("commitment", "mission"), ("commitment", "leaving"), ("mission", "leaving")):
                cos_rows.append(dict(layer=L, split=k, pair=f"{a}~{b}", cosine=cos(d[a], d[b])))
        for n in names:
            stab_rows.append(dict(layer=L, direction=n, cos_estimation_vs_heldout=cos(D["estimation"][n], D["heldout"][n]),
                                  cos_half_a_vs_half_b=cos(D["est_half_a"][n], D["est_half_b"][n])))
        X = np.load(ROOT / "data" / "activations_it_capcom" / f"acts_L{L}.npy").mean(1)
        for n in names:
            pr = X @ unit(D["estimation"][n])
            items_p = items.assign(proj=[pr[widx[w]] for w in items["word"]])
            neutral_mean = items_p.loc[items_p["list"] == "neutral", "proj"].mean()
            for lst, g in items_p.groupby("list", sort=False):
                proj_rows.append(dict(layer=L, direction=n, list=lst, n=len(g), mean_proj=g["proj"].mean(),
                                      sd_proj=g["proj"].std(), mean_minus_neutral=g["proj"].mean() - neutral_mean))
            rated = items_p.dropna(subset=["warriner_valence"])
            r, pval = stats.pearsonr(rated["proj"], rated["warriner_valence"])
            val_rows.append(dict(layer=L, direction=n, n_words=len(rated), r_proj_valence=r, p=pval))
    out = dict(cosines=pd.DataFrame(cos_rows), stability=pd.DataFrame(stab_rows),
               word_projections=pd.DataFrame(proj_rows), valence_correlation=pd.DataFrame(val_rows),
               sentence_spread=pd.DataFrame(spread_rows), sentence_overlap=pd.DataFrame(overlap_rows))
    for k, df in out.items():
        df.to_csv(RES / f"{k}.csv", index=False)
    pd.Series({k: ",".join(map(str, v)) for k, v in sp.items()}).to_csv(RES / "splits.csv", header=["pairs"])
    pd.set_option("display.width", 220, "display.precision", 3)
    print(sp)
    print(out["cosines"].pivot_table(index=["layer", "pair"], columns="split", values="cosine"))
    print(out["stability"])
    print(out["word_projections"].pivot_table(index=["layer", "direction"], columns="list", values="mean_minus_neutral"))
    print(out["valence_correlation"])
    print(out["sentence_spread"])
    print(out["sentence_overlap"].pivot_table(index=["layer", "reference", "set_a"], columns="set_b", values="mean_cos"))


if __name__ == "__main__":
    if "--analyze-only" not in sys.argv:
        run_extraction()
    analyze()
