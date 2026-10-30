"""Quickstart: the direction measurement and the baseline ratings on 2 profile pairs.

Pairs 1 and 2 only: 4 profiles, 2 x 160 profile + sentence prompts, then 4 x 6 x 10 = 240 rating
prompts. Writes results/quickstart/ (gitignored) and leaves the committed results alone.
"""
import gc
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / ".hf_cache"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from baseline_ratings import build_jobs, rate, summarize  # noqa: E402
from profile_directions import LAYERS, MODEL, SENT_SETS, STIM, cos, extract, user_text  # noqa: E402
from src.device import get_device  # noqa: E402

PAIRS = [1, 2]
OUT = ROOT / "results" / "quickstart"


def measure():
    load_dotenv(ROOT / ".env")
    token, device = os.environ["HF_TOKEN"], get_device()
    tok = AutoTokenizer.from_pretrained(MODEL, token=token)
    model = AutoModelForCausalLM.from_pretrained(MODEL, token=token, dtype=torch.bfloat16,
                                                 attn_implementation="eager").to(device).eval()
    system = (STIM / "system_prompt.txt").read_text().strip()
    prof = pd.read_csv(STIM / "profiles.csv")
    prof = prof[prof["pair_id"].isin(PAIRS)]
    sents = pd.read_csv(STIM / "sentences.csv")
    P = extract([(user_text(system, t), t) for t in prof["text"]], tok, model, device)
    mod = prof[prof["level"] == "moderate"]
    idx = pd.DataFrame([dict(pair_id=r.pair_id, set=s.set) for r in mod.itertuples() for s in sents.itertuples()])
    S = extract([(user_text(system, r.text, s.sentence), s.sentence) for r in mod.itertuples()
                 for s in sents.itertuples()], tok, model, device)
    rows = []
    for L in LAYERS:
        levels = prof["level"].to_numpy()
        d = {"capability": P[L][levels == "extreme"].mean(0) - P[L][levels == "moderate"].mean(0)}
        neutral = S[L][(idx["set"] == "neutral").to_numpy()].mean(0)
        for s in SENT_SETS:
            d[s] = S[L][(idx["set"] == s).to_numpy()].mean(0) - neutral
            rows.append(dict(layer=L, pair=f"capability~{s}", cosine=cos(d["capability"], d[s])))
        assert all(np.isfinite(v).all() for v in d.values())
    del model
    gc.collect()
    if device.type == "mps":
        torch.mps.empty_cache()
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    cosines = measure()
    cosines.to_csv(OUT / "cosines.csv", index=False)
    t1 = time.time()
    r = rate([j for j in build_jobs() if j["pair_id"] in PAIRS])
    r.to_csv(OUT / "baseline_ratings.csv", index=False)
    mass, pen = summarize(r)
    mass.to_csv(OUT / "baseline_mass.csv")
    pen.to_csv(OUT / "baseline_penalty.csv", index=False)
    pd.set_option("display.width", 200, "display.precision", 3)
    print(cosines.to_string(index=False))
    print(mass)
    print(f"measurement {t1 - t0:.0f}s, baseline {time.time() - t1:.0f}s, total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
