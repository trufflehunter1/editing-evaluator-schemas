"""The evaluator's masculine and feminine ratings of the 600 gender items, in google/gemma-2-2b-it.

Each item gets two prompts, one per adjective ("On a scale from 1 to 7, how {adj} is the word '{w}'? Answer with
a single digit from 1 to 7."). Each prompt is wrapped in the chat template and the model turn is prefilled with
"Rating: ". From the next-token distribution we record mass = total probability on the digit tokens "1"-"7", and
score = expected value over those seven tokens after renormalising them to sum to 1.

Outputs in --out (default results/validation/): evaluator_ratings.csv (item, adj, score, mass),
evaluator_glasgow.csv (each adjective's correlation with Glasgow GEND).
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / ".hf_cache"))

import pandas as pd  # noqa: E402
import torch  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from scipy import stats  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

sys.path.insert(0, str(ROOT))
from src.device import get_device  # noqa: E402
from src.items import load_items  # noqa: E402

MODEL = "google/gemma-2-2b-it"
ADJS = ["masculine", "feminine"]
TEMPLATE = "On a scale from 1 to 7, how {adj} is the word '{w}'? Answer with a single digit from 1 to 7."
# Gemma has no leading-space digit tokens, so the space after the colon goes into the prefill.
PREFILL = "Rating: "
BATCH = 32
OUT = ROOT / "results" / "validation"


@torch.no_grad()
def rate(words):
    load_dotenv(ROOT / ".env")
    token, device = os.environ["HF_TOKEN"], get_device()
    tok = AutoTokenizer.from_pretrained(MODEL, token=token)
    tok.padding_side = "left"
    digit_ids = [tok.encode(str(k), add_special_tokens=False) for k in range(1, 8)]
    assert all(len(d) == 1 for d in digit_ids), digit_ids
    digit_ids = torch.tensor([d[0] for d in digit_ids], device=device)
    model = AutoModelForCausalLM.from_pretrained(MODEL, token=token, dtype=torch.bfloat16,
                                                 attn_implementation="eager").to(device).eval()
    jobs = [(w, a) for w in words for a in ADJS]
    rows = []
    for start in range(0, len(jobs), BATCH):
        batch = jobs[start:start + BATCH]
        texts = [tok.apply_chat_template([{"role": "user", "content": TEMPLATE.format(adj=a, w=w)}],
                                         tokenize=False, add_generation_prompt=True) + PREFILL for w, a in batch]
        enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(device)
        probs = torch.softmax(model(**enc, logits_to_keep=1).logits[:, -1].float(), -1)[:, digit_ids]
        mass = probs.sum(-1)
        score = (probs / mass[:, None] * torch.arange(1, 8, device=device)).sum(-1)
        rows += [dict(item=w, adj=a, score=s, mass=m)
                 for (w, a), s, m in zip(batch, score.tolist(), mass.tolist())]
        if (start // BATCH) % 25 == 0:
            print(f"{start + len(batch)}/{len(jobs)}", flush=True)
    return pd.DataFrame(rows)


def summarize(r):
    glas = load_items().set_index("item")["glasgow_gender"]
    rows = []
    for a, g in r.groupby("adj", sort=False):
        s = g.set_index("item").loc[glas.index]
        rows.append(dict(adj=a, n=len(s), pearson_r=stats.pearsonr(s["score"], glas)[0],
                         spearman_rho=stats.spearmanr(s["score"], glas)[0],
                         mean_mass=s["mass"].mean(), min_mass=s["mass"].min()))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    if not (a.out / "evaluator_ratings.csv").exists():
        rate(sorted(load_items()["item"])).to_csv(a.out / "evaluator_ratings.csv", index=False)
    corr = summarize(pd.read_csv(a.out / "evaluator_ratings.csv"))
    corr.to_csv(a.out / "evaluator_glasgow.csv", index=False)
    print(corr.to_string(index=False))
