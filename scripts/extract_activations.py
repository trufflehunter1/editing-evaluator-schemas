"""Residual-stream activations for a word list (default: the items of items.csv).

Prompts follow Kozlowski & Boutyline (2026). For each prompt, activations are mean-pooled over all prompt
tokens except the BOS token. "Layer L" is the residual stream after block L (HF hidden_states[L + 1]).

With --model it (google/gemma-2-2b-it), each prompt is wrapped in the chat template. The USER text becomes the
user turn, and prompt 4's ASSISTANT text is a prefix to the model turn. Pooling still covers every token except
BOS, including the chat-template tokens.

Outputs (gitignored): words.txt, acts_L{4,8,13,18}.npy [n_items, 4 prompts, d_model].
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / ".hf_cache"))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

sys.path.insert(0, str(ROOT))
from src.device import get_device  # noqa: E402
from src.items import load_items  # noqa: E402

MODELS = {"base": "google/gemma-2-2b", "it": "google/gemma-2-2b-it"}
LAYERS = [4, 8, 13, 18]
PROMPTS = [
    "USER: Tell me about {w}.",
    "USER: Tell me your associations with the word {w}.",
    "USER: What do you think of when you hear the word {w}?",
    "USER: Define the word {w}. ASSISTANT: The word {w} means",
]
BATCH = 32
OUT_DIRS = {"base": ROOT / "data" / "activations", "it": ROOT / "data" / "activations_it"}


def chat_templates(tok):
    """Prompts wrapped in the chat template. The USER text becomes the user turn, and the ASSISTANT text in
    prompt 4 becomes a prefix to the model turn. The template supplies BOS."""
    out = []
    for p in PROMPTS:
        user, _, assistant = p.removeprefix("USER: ").partition(" ASSISTANT: ")
        out.append(tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False,
                                           add_generation_prompt=True) + assistant)
    return out


@torch.no_grad()
def main(model_key, words, out):
    load_dotenv(ROOT / ".env")
    token = os.environ["HF_TOKEN"]
    device = get_device()
    print(f"{len(words)} items, model {MODELS[model_key]}, device {device}")

    tok = AutoTokenizer.from_pretrained(MODELS[model_key], token=token)
    tok.padding_side = "right"
    templates = chat_templates(tok) if model_key == "it" else PROMPTS
    model = AutoModelForCausalLM.from_pretrained(MODELS[model_key], token=token, dtype=torch.bfloat16,
                                                 attn_implementation="eager").to(device).eval()
    d_model = model.config.hidden_size
    acts = {L: np.zeros((len(words), len(PROMPTS), d_model), np.float32) for L in LAYERS}

    jobs = [(i, p) for i in range(len(words)) for p in range(len(PROMPTS))]
    for start in range(0, len(jobs), BATCH):
        batch = jobs[start:start + BATCH]
        texts = [templates[p].replace("{w}", words[i]) for i, p in batch]
        enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=model_key == "base").to(device)
        assert (enc["input_ids"][:, 0] == tok.bos_token_id).all()
        hs = model(**enc, output_hidden_states=True, logits_to_keep=1).hidden_states
        mask = enc["attention_mask"].clone()
        mask[:, 0] = 0  # drop BOS
        m = mask.unsqueeze(-1).float()
        for L in LAYERS:
            pooled = ((hs[L + 1].float() * m).sum(1) / m.sum(1)).cpu().numpy()
            for (i, p), v in zip(batch, pooled):
                acts[L][i, p] = v
        if (start // BATCH) % 20 == 0:
            print(f"{start + len(batch)}/{len(jobs)} prompts", flush=True)

    out.mkdir(parents=True, exist_ok=True)
    (out / "words.txt").write_text("\n".join(words) + "\n")
    for L in LAYERS:
        np.save(out / f"acts_L{L}.npy", acts[L])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=list(MODELS), default="base")
    ap.add_argument("--words", type=Path, help="one word per line; default = the items of items.csv")
    ap.add_argument("--out", type=Path, help="output dir; default depends on --model")
    a = ap.parse_args()
    words = sorted(set(a.words.read_text().split())) if a.words else sorted(set(load_items()["item"]))
    main(a.model, words, a.out or OUT_DIRS[a.model])
