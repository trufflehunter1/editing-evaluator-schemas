"""Editing pilot: strengthening edits at layer 8, at the profile token positions, in gemma-2-2b-it.

Directions come from the neutral-referenced estimation directions of scripts/profile_directions.py. With m = dM/|dM| and
l = dL/|dL|: L = dL - (dL.m)m and M = dM - (dM.l)l, both normalised. c is the unit capability direction.

Edit for a unit path direction a: e1 = a, e2 = unit(c - (a.c)a), and in the (e1, e2) basis
T = [[1, (cos t' - cos t)/sin t], [0, sin t'/sin t]], which leaves a fixed and sends c to
cos t' e1 + sin t' e2. For h at a profile token, p = [(h-mu).e1, (h-mu).e2] and
h' = h + (Tp - p)[0] e1 + (Tp - p)[1] e2, where mu is the mean layer-8 activation over all 40 profiles.
LEAVE uses a = L, MISSION a = -M, SHAM a random unit vector orthogonal to c, L and M (seed 0).

Commands:
  tests             unit tests and decoding probe on the held-out profiles, plus a hook check
  rate              neutral condition, 40 profiles x 5 questions x 10 edit conditions
  followup EDIT     one edit (e.g. LEAVE_0.6) under mission, pay, rejected_options, open_options

Ratings use the readout of scripts/baseline_ratings.py and are appended to CSV every 100 prompts, so a stopped job resumes.
Outputs: directions/path_gs_L8.npz, results/capcom/edit_*.csv.
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
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from baseline_ratings import INSTRUCTION, MODEL, PREFILL, QUESTIONS  # noqa: E402
from profile_directions import CACHE, DIRS, RES, SEED, STIM, splits, unit, user_text  # noqa: E402
from src.device import get_device  # noqa: E402

LAYER, BATCH, FLUSH = 8, 8, 100
TARGETS = [0.2, 0.4, 0.6]
RATING_QUESTIONS = ["offer", "capabilities", "commitment_org", "goals_aligned", "stay_if_offer"]
FOLLOWUP_CONDITIONS = ["mission", "pay", "rejected_options", "open_options"]


def build_dirs():
    D = np.load(DIRS / f"profile_it_estimation_L{LAYER}.npz")
    dL, dM = D["leaving"], D["mission"]
    l_hat, m_hat = unit(dL), unit(dM)
    L, M, c = unit(dL - (dL @ m_hat) * m_hat), unit(dM - (dM @ l_hat) * l_hat), unit(D["capability"])
    q, _ = np.linalg.qr(np.stack([c, L, M], 1))
    v = np.random.default_rng(SEED).standard_normal(c.shape)
    sham = unit(v - q @ (q.T @ v))
    mu = np.load(CACHE / f"profiles_L{LAYER}.npy").mean(0)
    np.savez(DIRS / f"path_gs_L{LAYER}.npz", c=c, L=L, M=M, l_hat=l_hat, m_hat=m_hat, sham=sham, mu=mu)
    return dict(c=c, L=L, M=M, l_hat=l_hat, m_hat=m_hat, sham=sham, mu=mu)


def edit_params(d):
    """{label: (E [dim, 2], T [2, 2])} for the nine edits."""
    paths = dict(LEAVE=d["L"], MISSION=-d["M"], SHAM=d["sham"])
    params = {}
    for name, a in paths.items():
        ac = float(a @ d["c"])
        theta = np.arccos(ac)
        e2 = unit(d["c"] - ac * a)
        for t in TARGETS:
            th = np.arccos(t)
            T = np.array([[1.0, (np.cos(th) - np.cos(theta)) / np.sin(theta)], [0.0, np.sin(th) / np.sin(theta)]])
            params[f"{name}_{t}"] = (np.stack([a, e2], 1), T)
    return params


def apply_edit(h, mu, E, T):
    p = (h - mu) @ E
    return h + (p @ (T - np.eye(2)).T) @ E.T


def heldout_means():
    P = np.load(CACHE / f"profiles_L{LAYER}.npy")
    idx = pd.read_csv(CACHE / "profiles_index.csv")
    held = splits()["heldout"]
    get = lambda lv: P[[idx.index[(idx.pair_id == p) & (idx.level == lv)][0] for p in held]]
    return get("moderate"), get("extreme")


def probe_scores(train_x, train_y, test_x, test_y):
    sc = StandardScaler().fit(train_x)
    clf = LogisticRegression(C=0.01, max_iter=5000).fit(sc.transform(train_x), train_y)
    return clf.decision_function(sc.transform(test_x)), test_y


def unit_tests(d, params):
    mod, ext = heldout_means()
    n = len(mod)
    X0, y = np.concatenate([mod, ext]), np.array([0] * n + [1] * n)
    pair = np.concatenate([np.arange(n)] * 2)
    rows, probe = [], []
    for label in ["unedited"] + list(params):
        if label == "unedited":
            m, e, a = mod, ext, None
        else:
            E, T = params[label]
            m, e, a = apply_edit(mod, d["mu"], E, T), apply_edit(ext, d["mu"], E, T), E[:, 0]
        diff = (e - m).mean(0)
        row = dict(edit=label, diff_norm=np.linalg.norm(diff))
        row.update({f"proj_{k}": float(diff @ d[k]) for k in ("c", "L", "M", "l_hat", "m_hat", "sham")})
        row.update({f"cos_{k}": float(unit(diff) @ d[k]) for k in ("c", "L", "M", "l_hat", "m_hat", "sham")})
        row["cos_a"] = np.nan if a is None else float(unit(diff) @ a)
        pc = (e - m) @ d["c"]
        row.update(c_mod=float((m - d["mu"]).mean(0) @ d["c"]), c_ext=float((e - d["mu"]).mean(0) @ d["c"]),
                   c_pair_diff_sd=float(pc.std(ddof=1)), c_pairs_ext_gt_mod=float((pc > 0).mean()))
        rows.append(row)
        # Leave-one-pair-out: train on nine unedited pairs, test on the left-out pair under this edit.
        Xt = np.concatenate([m, e])
        scores, labels = [], []
        for p in range(n):
            tr, te = pair != p, pair == p
            s, l = probe_scores(X0[tr], y[tr], Xt[te], y[te])
            scores.append(s)
            labels.append(l)
        s, l = np.concatenate(scores), np.concatenate(labels)
        probe.append(dict(edit=label, n=len(l), accuracy=float(((s > 0) == l).mean()), auc=float(roc_auc_score(l, s))))
    probe = pd.DataFrame(probe)
    probe["drop_points"] = 100 * (probe["accuracy"].iloc[0] - probe["accuracy"])
    probe["flag_over_5"] = probe["drop_points"] > 5
    return pd.DataFrame(rows), probe


def load_model():
    load_dotenv(ROOT / ".env")
    token, device = os.environ["HF_TOKEN"], get_device()
    tok = AutoTokenizer.from_pretrained(MODEL, token=token)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(MODEL, token=token, dtype=torch.bfloat16,
                                                 attn_implementation="eager").to(device).eval()
    return tok, model, device


def encode(tok, batch, device):
    """Tokenise; mask marks tokens overlapping the profile span."""
    texts = [tok.apply_chat_template([{"role": "user", "content": j["user"]}], tokenize=False,
                                     add_generation_prompt=True) + j.get("prefill", "") for j in batch]
    enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False, return_offsets_mapping=True)
    offs = enc.pop("offset_mapping")
    mask = torch.zeros(enc["input_ids"].shape, dtype=torch.bool)
    for b, (j, text) in enumerate(zip(batch, texts)):
        c0 = text.rindex(j["profile"])
        c1 = c0 + len(j["profile"])
        mask[b] = (offs[b, :, 0] < c1) & (offs[b, :, 1] > c0)
        assert mask[b].any()
    return enc.to(device), mask.to(device)


def make_hook(mask, mu, E, T):
    I = torch.eye(2, device=mask.device, dtype=torch.float32)
    E, T, mu = (torch.tensor(x, device=mask.device, dtype=torch.float32) for x in (E, T, mu))

    def hook(_module, _inputs, output):
        h = output[0] if isinstance(output, tuple) else output
        x = h[mask].float()
        new = x + ((x - mu) @ E @ (T - I).T) @ E.T
        h = h.clone()
        h[mask] = new.to(h.dtype)
        return (h, *output[1:]) if isinstance(output, tuple) else h
    return hook


@torch.no_grad()
def hook_check(d, params):
    """Run one held-out pair through the hook; compare profile-token means with the analytic edit."""
    tok, model, device = load_model()
    block = model.model.layers[LAYER]
    system = (STIM / "system_prompt.txt").read_text().strip()
    prof = pd.read_csv(STIM / "profiles.csv")
    pid = splits()["heldout"][0]
    batch = [dict(user=user_text(system, r.text), profile=r.text) for r in prof[prof.pair_id == pid].itertuples()]
    enc, mask = encode(tok, batch, device)
    seen = {}

    def capture(_m, _i, out):
        seen["h"] = (out[0] if isinstance(out, tuple) else out).float()

    def run(extra=None):
        hs = [block.register_forward_hook(extra)] if extra else []
        hs.append(block.register_forward_hook(capture))
        model(**enc, logits_to_keep=1)
        for x in hs:
            x.remove()
        return torch.stack([seen["h"][b][mask[b]].mean(0) for b in range(2)]).cpu().numpy()

    base = run()
    cached = np.load(CACHE / f"profiles_L{LAYER}.npy")
    idx = pd.read_csv(CACHE / "profiles_index.csv")
    cached = cached[[idx.index[(idx.pair_id == pid) & (idx.level == lv)][0] for lv in ("moderate", "extreme")]]
    rows = [dict(edit="unedited_vs_cache", max_abs_error=float(np.abs(base - cached).max()),
                 rel_error=float(np.linalg.norm(base - cached) / np.linalg.norm(cached)))]
    for label, (E, T) in params.items():
        got = run(make_hook(mask, d["mu"], E, T))
        want = apply_edit(base, d["mu"], E, T)
        rows.append(dict(edit=label, max_abs_error=float(np.abs(got - want).max()),
                         rel_error=float(np.linalg.norm(got - want) / np.linalg.norm(want - base))))
    return pd.DataFrame(rows)


def build_jobs(conditions, labels):
    system = (STIM / "system_prompt.txt").read_text().strip()
    prof, cond = pd.read_csv(STIM / "profiles.csv"), pd.read_csv(STIM / "conditions.csv").set_index("condition")
    return [dict(edit=e, condition=c, pair_id=p.pair_id, level=p.level, question=q, profile=p.text, prefill=PREFILL,
                 user=f"{system}\n\n{p.text}\n\n{cond.loc[c, 'text']}\n\n{QUESTIONS[q]} {INSTRUCTION}")
            for e in labels for c in conditions for p in prof.itertuples() for q in RATING_QUESTIONS]


KEY = ["edit", "condition", "pair_id", "level", "question"]


@torch.no_grad()
def rate(jobs, params, d, out):
    done = set()
    if out.exists():
        done = set(map(tuple, pd.read_csv(out)[KEY].to_numpy().tolist()))
    jobs = [j for j in jobs if tuple(j[k] for k in KEY) not in done]
    print(f"{len(done)} done, {len(jobs)} to run", flush=True)
    if not jobs:
        return
    tok, model, device = load_model()
    block = model.model.layers[LAYER]
    digit_ids = torch.tensor([tok.encode(str(k), add_special_tokens=False)[0] for k in range(1, 8)], device=device)
    values = torch.arange(1, 8, device=device)
    buf, n = [], 0
    for label in dict.fromkeys(j["edit"] for j in jobs):
        group = [j for j in jobs if j["edit"] == label]
        for s in range(0, len(group), BATCH):
            batch = group[s:s + BATCH]
            enc, mask = encode(tok, batch, device)
            handle = None
            if label != "unedited":
                handle = block.register_forward_hook(make_hook(mask, d["mu"], *params[label]))
            p = torch.softmax(model(**enc, logits_to_keep=1).logits[:, -1].float(), -1)[:, digit_ids]
            if handle:
                handle.remove()
            mass = p.sum(-1)
            score = (p / mass[:, None] * values).sum(-1)
            for j, m, sc in zip(batch, mass.tolist(), score.tolist()):
                buf.append({**{k: j[k] for k in KEY}, "mass": m, "score": sc})
            n += len(batch)
            if len(buf) >= FLUSH:
                pd.DataFrame(buf).to_csv(out, mode="a", header=not out.exists(), index=False)
                buf = []
                if device.type == "mps":
                    torch.mps.empty_cache()
                print(f"{n}/{len(jobs)} {label}", flush=True)
    if buf:
        pd.DataFrame(buf).to_csv(out, mode="a", header=not out.exists(), index=False)
    print(f"{n}/{len(jobs)} finished", flush=True)


def summarize(path, tag):
    r = pd.read_csv(path)
    mass = r.groupby(["condition", "edit"])["mass"].agg(["mean", "min"]).reset_index()
    w = r.pivot_table(index=["edit", "condition", "pair_id", "question"], columns="level", values="score").reset_index()
    w["penalty"] = w["extreme"] - w["moderate"]
    pen = w.groupby(["condition", "edit", "question"]).agg(mean=("penalty", "mean"), std=("penalty", "std"),
                                                           count=("penalty", "count"), moderate=("moderate", "mean"),
                                                           extreme=("extreme", "mean")).reset_index()
    mass.to_csv(RES / f"edit_mass{tag}.csv", index=False)
    pen.to_csv(RES / f"edit_penalty{tag}.csv", index=False)
    pen["cell"] = pen["mean"].map("{:+.2f}".format) + " (" + pen["std"].map("{:.2f}".format) + ")"
    pd.set_option("display.width", 220, "display.max_rows", 200, "display.max_columns", 30, "display.precision", 3)
    print(mass.to_string(index=False))
    print(pen.pivot_table(index=["condition", "edit"], columns="question", values="cell", aggfunc="first")
          [RATING_QUESTIONS].to_string())
    return pen


if __name__ == "__main__":
    d = build_dirs()
    params = edit_params(d)
    cmd = sys.argv[1]
    RES.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 240, "display.max_columns", 40, "display.precision", 4)
    if cmd == "tests":
        print(f"cos(c,L)={d['c'] @ d['L']:.4f} cos(c,M)={d['c'] @ d['M']:.4f} cos(L,M)={d['L'] @ d['M']:.4f} "
              f"cos(L,m_hat)={d['L'] @ d['m_hat']:.2e} cos(M,l_hat)={d['M'] @ d['l_hat']:.2e} "
              f"cos(sham,c)={d['sham'] @ d['c']:.2e} cos(sham,L)={d['sham'] @ d['L']:.2e} cos(sham,M)={d['sham'] @ d['M']:.2e}")
        tests, probe = unit_tests(d, params)
        tests.to_csv(RES / "edit_unit_tests.csv", index=False)
        probe.to_csv(RES / "edit_probe.csv", index=False)
        print(tests[["edit", "cos_a", "cos_c", "proj_c", "c_mod", "c_ext", "c_pairs_ext_gt_mod", "diff_norm"]].to_string(index=False))
        print(tests[["edit", "proj_L", "proj_M", "proj_l_hat", "proj_m_hat", "proj_sham"]].to_string(index=False))
        print(probe.to_string(index=False))
        check = hook_check(d, params)
        check.to_csv(RES / "edit_hook_check.csv", index=False)
        print(check.to_string(index=False))
    elif cmd == "rate":
        out = RES / "edit_ratings.csv"
        rate(build_jobs(["neutral"], ["unedited"] + list(params)), params, d, out)
        summarize(out, "")
    elif cmd == "followup":
        label = sys.argv[2]
        out = RES / f"edit_ratings_followup_{label}.csv"
        rate(build_jobs(FOLLOWUP_CONDITIONS, [label]), params, d, out)
        summarize(out, f"_followup_{label}")
