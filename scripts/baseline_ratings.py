"""Baseline hiring ratings in gemma-2-2b-it, with no edits.

Each prompt combines one of 40 profiles, one of 6 conditions and one of 10 questions. The user turn is
the system context (no system role in Gemma 2), the profile, the condition text, then the question
plus "Answer with a single digit from 1 to 7.", separated by blank lines. The model turn is
prefilled with "Rating: ". From the next-token distribution: mass = probability on digit tokens 1-7,
score = expected value over those tokens after renormalising them to sum to 1.

Outputs: results/capcom/baseline_ratings.csv, baseline_mass.csv, baseline_penalty.csv
(extreme - moderate within pair, mean and SD across the 20 pairs, by condition and question).
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / ".hf_cache"))

import pandas as pd  # noqa: E402
import torch  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

sys.path.insert(0, str(ROOT))
from src.device import get_device  # noqa: E402

MODEL = "google/gemma-2-2b-it"
STIM, RES = ROOT / "stimuli", ROOT / "results" / "capcom"
BATCH = 8
INSTRUCTION = "Answer with a single digit from 1 to 7."
PREFILL = "Rating: "
QUESTIONS = {
    "offer": "How likely would you be to offer this candidate the job?",
    "capabilities": "How would you rate the capabilities of this candidate?",
    "competence": "How would you rate the competence of this candidate?",
    "commitment_org": "Rate the candidate's likely commitment to the organization.",
    "commitment_industry": "Rate the candidate's commitment to the industry.",
    "stay": "Rate the candidate's willingness to stay with the company.",
    "extra_hours": "Rate the candidate's willingness to work extra hours.",
    "goals_aligned": "How likely is it that this candidate's goals will be aligned with the organization's goals?",
    "stay_if_offer": ("How willing would this candidate be to stay with the company if they received another offer "
                      "from a competitor?"),
    "turn_down_concern": "How concerned are you that this candidate would turn down an offer?",
}


def build_jobs():
    system = (STIM / "system_prompt.txt").read_text().strip()
    prof, cond = pd.read_csv(STIM / "profiles.csv"), pd.read_csv(STIM / "conditions.csv")
    return [dict(pair_id=p.pair_id, level=p.level, condition=c.condition, question=q,
                 user=f"{system}\n\n{p.text}\n\n{c.text}\n\n{qt} {INSTRUCTION}")
            for p in prof.itertuples() for c in cond.itertuples() for q, qt in QUESTIONS.items()]


@torch.no_grad()
def rate(jobs):
    load_dotenv(ROOT / ".env")
    token, device = os.environ["HF_TOKEN"], get_device()
    tok = AutoTokenizer.from_pretrained(MODEL, token=token)
    tok.padding_side = "left"
    digit_ids = torch.tensor([tok.encode(str(k), add_special_tokens=False)[0] for k in range(1, 8)], device=device)
    model = AutoModelForCausalLM.from_pretrained(MODEL, token=token, dtype=torch.bfloat16,
                                                 attn_implementation="eager").to(device).eval()
    for s in range(0, len(jobs), BATCH):
        batch = jobs[s:s + BATCH]
        texts = [tok.apply_chat_template([{"role": "user", "content": j["user"]}], tokenize=False,
                                         add_generation_prompt=True) + PREFILL for j in batch]
        enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(device)
        # logits_to_keep=1 keeps only the last position; full [batch, seq, vocab] logits fill MPS memory
        p = torch.softmax(model(**enc, logits_to_keep=1).logits[:, -1].float(), -1)[:, digit_ids]
        mass = p.sum(-1)
        score = (p / mass[:, None] * torch.arange(1, 8, device=device)).sum(-1)
        for j, m, sc in zip(batch, mass.tolist(), score.tolist()):
            j["mass"], j["score"] = m, sc
        del enc
        if (s // BATCH) % 25 == 0:
            if device.type == "mps":
                torch.mps.empty_cache()
            print(f"{s + len(batch)}/{len(jobs)}", flush=True)
    return pd.DataFrame(jobs).drop(columns="user")


def summarize(r):
    mass = r.groupby("question")["mass"].agg(["mean", "min"]).reindex(list(QUESTIONS))
    w = r.pivot_table(index=["pair_id", "condition", "question"], columns="level", values="score").reset_index()
    w["penalty"] = w["extreme"] - w["moderate"]
    pen = w.groupby(["condition", "question"])["penalty"].agg(["mean", "std", "count"]).reset_index()
    means = r.groupby(["condition", "question", "level"])["score"].mean().unstack("level").reset_index()
    return mass, pen.merge(means, on=["condition", "question"])


if __name__ == "__main__":
    RES.mkdir(parents=True, exist_ok=True)
    out = RES / "baseline_ratings.csv"
    if not out.exists():
        rate(build_jobs()).to_csv(out, index=False)
    mass, pen = summarize(pd.read_csv(out))
    mass.to_csv(RES / "baseline_mass.csv")
    pen.to_csv(RES / "baseline_penalty.csv", index=False)
    pd.set_option("display.width", 220, "display.precision", 3)
    print(mass)
    print(pen.pivot_table(index="question", columns="condition", values="mean").reindex(list(QUESTIONS)))
    print(pen.pivot_table(index="question", columns="condition", values="std").reindex(list(QUESTIONS)))
