"""Diagnostics after the editing pilot: natural effects, direct steering, matched-magnitude edit.

Natural effects: at layers 8 and 13, the projection of the mean extreme-minus-moderate difference onto c (profile
  tokens), and of the mean (profile + sentence) - (profile + neutral sentence) onto L and -M (sentence tokens).
  Profile tokens come before the sentence, so appending a sentence cannot change them.
Direct steering: add alpha * L or alpha * (-M) at the profile tokens of every profile, at layer 8 or layer 13, with
  alpha = k * the held-out natural effect, k in {0.5, 1, 2}.
Matched-magnitude edit: at layer 8, h' = h + beta * ((h - mu).c) * a at the profile tokens, with a = L, -M or the sham
  direction. beta sets the mean extreme-minus-moderate difference along a, over all 20 pairs, to k * the natural effect
  (24.02 for L and sham, 27.26 for -M), k in {0.25, 0.5, 1}.

Commands:
  effects          writes natural_effects.csv
  steer-check      checks the steering hook on the held-out profiles; writes steering_check.csv
  steer-rate       neutral condition, 40 profiles x 4 questions; appends to CSV every 100 prompts, resumes by batch
  steer-summary    writes steering_change.csv, steering_noise.csv, steering_mass.csv
  matched-test     unit test of the matched edits through the hook; writes matched_unit_test.csv
  matched-rate     matched ratings, in the same batches as the unedited run; writes matched_ratings.csv
  matched-summary  writes matched_mass.csv, matched_penalty.csv, matched_vs_sham.csv, matched_noise.csv
  crossover EDIT   information conditions for one edit; writes matched_crossover_{ratings,mass,penalty}_EDIT.csv
  matched-short    two pairs of matched_LEAVE_k0.5 and matched_SHAM_k0.5 in the batches of the full run, compared with
                   the committed run

Every condition uses batch size 8. All conditions but the shuffle_* runs use the same batches, so padding is the
same when two of them are compared; shuffle_* reorders the prompts to measure the effect of batch composition.
Outputs: results/capcom/natural_effects.csv, steering_*.csv, matched_*.csv.
"""
import gc
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / ".hf_cache"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from baseline_ratings import INSTRUCTION, PREFILL, QUESTIONS  # noqa: E402
from edit_pilot import encode, load_model  # noqa: E402
from profile_directions import CACHE, DIRS, RES, SEED, STIM, extract, splits, unit, user_text  # noqa: E402

STEER_LAYERS, LAYER_MATCHED = [8, 13], 8
KS = [0.5, 1, 2]
RATE_QUESTIONS = ["offer", "stay_if_offer", "goals_aligned", "commitment_org"]
BATCH, FLUSH, N_SHUFFLES = 8, 100, 3
KEY = ["edit", "pair_id", "level", "question"]
CROSS_CONDITIONS = ["mission", "pay", "rejected_options", "open_options"]
MATCHED_KS, NATURAL = [0.25, 0.5, 1], dict(LEAVE=24.02, MISSION=27.26, SHAM=24.02)


def gs_dirs(cap, dL, dM, mu):
    l_hat, m_hat = unit(dL), unit(dM)
    L, M, c = unit(dL - (dL @ m_hat) * m_hat), unit(dM - (dM @ l_hat) * l_hat), unit(cap)
    q, _ = np.linalg.qr(np.stack([c, L, M], 1))
    v = np.random.default_rng(SEED).standard_normal(c.shape)
    return dict(c=c, L=L, M=M, l_hat=l_hat, m_hat=m_hat, sham=unit(v - q @ (q.T @ v)), mu=mu)


def cached_dirs(layer):
    D = np.load(DIRS / f"profile_it_estimation_L{layer}.npz")
    mu = np.load(CACHE / f"profiles_L{layer}.npy").mean(0)
    return gs_dirs(D["capability"], D["leaving"], D["mission"], mu)


def effects():
    idx = pd.read_csv(CACHE / "profiles_index.csv")
    sidx = pd.read_csv(CACHE / "sentences_index.csv")
    rows = []
    for layer in STEER_LAYERS:
        d = cached_dirs(layer)
        P, S = np.load(CACHE / f"profiles_L{layer}.npy"), np.load(CACHE / f"sentences_L{layer}.npy")
        for split, pairs in (("estimation", splits()["estimation"]), ("heldout", splits()["heldout"]), ("all", list(range(1, 21)))):
            get = lambda lv: P[[idx.index[(idx.pair_id == p) & (idx.level == lv)][0] for p in pairs]]
            keep = sidx["pair_id"].isin(pairs).to_numpy()
            sent = lambda s: S[keep & (sidx["set"] == s).to_numpy()].mean(0)
            cap, leave, mission = (get("extreme") - get("moderate")).mean(0), sent("leaving") - sent("neutral"), sent("mission") - sent("neutral")
            for name, diff, axis, a in (("capability", cap, "c", d["c"]), ("leaving", leave, "L", d["L"]), ("mission", mission, "-M", -d["M"])):
                rows.append(dict(layer=layer, split=split, effect=name, axis=axis, projection=float(diff @ a),
                                 magnitude=abs(float(diff @ a)), full_vector_norm=float(np.linalg.norm(diff)),
                                 mean_profile_norm=float(np.linalg.norm(P, axis=1).mean())))
    df = pd.DataFrame(rows)
    df.to_csv(RES / "natural_effects.csv", index=False)
    return df


def alphas():
    df = pd.read_csv(RES / "natural_effects.csv")
    df = df[df["split"] == "heldout"].set_index(["layer", "effect"])["magnitude"]
    return {f"steer_L{layer}_{name}_k{k}": (layer, a, k * float(df[(layer, eff)]))
            for layer in STEER_LAYERS for name, eff, a in (("LEAVE", "leaving", "L"), ("MISSION", "mission", "-M")) for k in KS}


def steer_hook(mask, vec):
    vec = torch.tensor(vec, device=mask.device, dtype=torch.float32)

    def hook(_module, _inputs, output):
        h = output[0] if isinstance(output, tuple) else output
        h = h.clone()
        h[mask] = (h[mask].float() + vec).to(h.dtype)
        return (h, *output[1:]) if isinstance(output, tuple) else h
    return hook


def push_hook(mask, mu, c, a, beta):
    mu, c, a = (torch.tensor(x, device=mask.device, dtype=torch.float32) for x in (mu, c, a))

    def hook(_module, _inputs, output):
        h = output[0] if isinstance(output, tuple) else output
        x = h[mask].float()
        h = h.clone()
        h[mask] = (x + beta * ((x - mu) @ c)[:, None] * a).to(h.dtype)
        return (h, *output[1:]) if isinstance(output, tuple) else h
    return hook


def matched_params():
    """{label: (a, beta)}, with beta from the mean differences over all 20 pairs."""
    d = cached_dirs(LAYER_MATCHED)
    P, idx = np.load(CACHE / f"profiles_L{LAYER_MATCHED}.npy"), pd.read_csv(CACHE / "profiles_index.csv")
    diff = P[(idx.level == "extreme").to_numpy()].mean(0) - P[(idx.level == "moderate").to_numpy()].mean(0)
    out = {}
    for name, a in (("LEAVE", d["L"]), ("MISSION", -d["M"]), ("SHAM", d["sham"])):
        for k in MATCHED_KS:
            out[f"matched_{name}_k{k}"] = (a, (k * NATURAL[name] - diff @ a) / (diff @ d["c"]))
    return out


def hooks_for(label, mask, model, ctx):
    if label.startswith("matched_"):
        a, beta = ctx["matched"][label]
        d = ctx["steer"][LAYER_MATCHED]
        return [(model.model.layers[LAYER_MATCHED], push_hook(mask, d["mu"], d["c"], a, beta))]
    if label in ctx["alphas"]:
        layer, a, alpha = ctx["alphas"][label]
        d = ctx["steer"][layer]
        vec = alpha * (d["L"] if a == "L" else -d["M"])
        return [(model.model.layers[layer], steer_hook(mask, vec))]
    return []


def context():
    return dict(matched=matched_params(), alphas=alphas(), steer={x: cached_dirs(x) for x in STEER_LAYERS})


def base_jobs(condition="neutral"):
    system = (STIM / "system_prompt.txt").read_text().strip()
    prof, cond = pd.read_csv(STIM / "profiles.csv"), pd.read_csv(STIM / "conditions.csv").set_index("condition")
    return [dict(condition=condition, pair_id=p.pair_id, level=p.level, question=q, profile=p.text, prefill=PREFILL,
                 user=f"{system}\n\n{p.text}\n\n{cond.loc[condition, 'text']}\n\n{QUESTIONS[q]} {INSTRUCTION}")
            for p in prof.itertuples() for q in RATE_QUESTIONS]


@torch.no_grad()
def rate(labels=None, out=RES / "steering_ratings.csv", conditions=None, pairs=None):
    ctx = context()
    key = KEY + ["condition"] if conditions else KEY
    done = set(map(tuple, pd.read_csv(out)[key].to_numpy().tolist())) if out.exists() else set()
    base = [j for c in conditions or ["neutral"] for j in base_jobs(c) if pairs is None or j["pair_id"] in pairs]
    labels = labels or (["unedited"] + list(ctx["alphas"]) + [f"shuffle_{s}" for s in range(N_SHUFFLES)] + ["repeat"])
    tok, model, device = load_model()
    digit_ids = torch.tensor([tok.encode(str(k), add_special_tokens=False)[0] for k in range(1, 8)], device=device)
    values = torch.arange(1, 8, device=device)
    buf, n = [], 0
    for label in labels:
        order = np.arange(len(base))
        if label.startswith("shuffle_"):
            order = np.random.default_rng(int(label.split("_")[1])).permutation(len(base))
        for s in range(0, len(order), BATCH):
            batch = [{**base[i], "edit": label} for i in order[s:s + BATCH]]
            if all(tuple(j[k] for k in key) in done for j in batch):
                continue
            enc, mask = encode(tok, batch, device)
            handles = [b.register_forward_hook(h) for b, h in hooks_for(label, mask, model, ctx)]
            p = torch.softmax(model(**enc, logits_to_keep=1).logits[:, -1].float(), -1)[:, digit_ids]
            for h in handles:
                h.remove()
            mass = p.sum(-1)
            score = (p / mass[:, None] * values).sum(-1)
            buf += [{**{k: j[k] for k in key}, "mass": m, "score": sc} for j, m, sc in zip(batch, mass.tolist(), score.tolist())]
            n += len(batch)
            if len(buf) >= FLUSH:
                pd.DataFrame(buf).to_csv(out, mode="a", header=not out.exists(), index=False)
                buf = []
                if device.type == "mps":
                    torch.mps.empty_cache()
                print(f"{n} prompts, now {label}", flush=True)
    if buf:
        pd.DataFrame(buf).to_csv(out, mode="a", header=not out.exists(), index=False)
    print(f"{n} prompts finished", flush=True)


@torch.no_grad()
def check():
    """Held-out profiles: the shift along the axis at the steered layer, against alpha."""
    ctx = context()
    tok, model, device = load_model()
    system = (STIM / "system_prompt.txt").read_text().strip()
    prof = pd.read_csv(STIM / "profiles.csv")
    prof = prof[prof["pair_id"].isin(splits()["heldout"])]
    jobs = [dict(user=user_text(system, r.text), profile=r.text) for r in prof.itertuples()]

    def run(label):
        """{layer: [n, d]} token means after any edit at that layer."""
        store = {x: [] for x in STEER_LAYERS}
        for s in range(0, len(jobs), BATCH):
            batch = jobs[s:s + BATCH]
            enc, mask = encode(tok, batch, device)
            handles = [b.register_forward_hook(h) for b, h in hooks_for(label, mask, model, ctx)]

            def capture(x):
                def fn(_m, _i, out):
                    h = (out[0] if isinstance(out, tuple) else out).float()
                    store[x].append(torch.stack([h[b][mask[b]].mean(0) for b in range(len(batch))]).cpu().numpy())
                return fn
            handles += [model.model.layers[x].register_forward_hook(capture(x)) for x in STEER_LAYERS]
            model(**enc, logits_to_keep=1)
            for h in handles:
                h.remove()
        return {x: np.concatenate(v) for x, v in store.items()}

    base = run("unedited")
    rows = []
    for label, (layer, a, alpha) in ctx["alphas"].items():
        d = ctx["steer"][layer]
        got = run(label)[layer]
        vec = d["L"] if a == "L" else -d["M"]
        moved = float(((got - base[layer]) @ vec).mean())
        rows.append(dict(edit=label, layer=layer, alpha=alpha, moved_along_axis=moved, ratio=moved / alpha,
                         off_axis_rel=float(np.linalg.norm((got - base[layer]).mean(0) - moved * vec) / alpha)))
    steer = pd.DataFrame(rows)
    steer.to_csv(RES / "steering_check.csv", index=False)
    print(steer.to_string(index=False))


def summary():
    r = pd.read_csv(RES / "steering_ratings.csv")
    assert not r.duplicated(KEY).any()
    print(r.groupby("edit").size().value_counts().to_string())
    base = r[r.edit == "unedited"].set_index(KEY[1:])["score"]
    r["change"] = r["score"] - r.set_index(KEY[1:]).index.map(base)
    a = alphas()
    g = r.groupby(["edit", "question"])["change"]
    tab = pd.DataFrame(dict(mean_change=g.mean(), sd=g.std(), mean_abs=g.apply(lambda x: x.abs().mean()),
                            max_abs=g.apply(lambda x: x.abs().max()))).reset_index()
    tab["alpha"] = tab["edit"].map(lambda e: a[e][2] if e in a else np.nan)
    tab.to_csv(RES / "steering_change.csv", index=False)
    noise = tab[tab.edit.isin(["repeat"] + [f"shuffle_{s}" for s in range(N_SHUFFLES)])]
    noise.to_csv(RES / "steering_noise.csv", index=False)
    mass = r.groupby("edit")["mass"].agg(["mean", "min"])
    mass.to_csv(RES / "steering_mass.csv")
    pd.set_option("display.width", 240, "display.max_rows", 300, "display.max_columns", 30, "display.precision", 4)
    print(mass.round(4).to_string())
    print(tab.pivot(index="edit", columns="question", values="mean_change")[RATE_QUESTIONS].round(4).to_string())
    print(tab.pivot(index="edit", columns="question", values="sd")[RATE_QUESTIONS].round(4).to_string())
    print(noise.to_string(index=False))


@torch.no_grad()
def matched_test():
    """All 40 profiles through the hook at layer 8; pair differences by split and the size of the per-token push."""
    ctx = context()
    d = ctx["steer"][LAYER_MATCHED]
    tok, model, device = load_model()
    system = (STIM / "system_prompt.txt").read_text().strip()
    prof = pd.read_csv(STIM / "profiles.csv")
    jobs = [dict(user=user_text(system, r.text), profile=r.text, level=r.level, pair_id=r.pair_id) for r in prof.itertuples()]
    ext, pid = np.array([j["level"] == "extreme" for j in jobs]), np.array([j["pair_id"] for j in jobs])
    sp = splits()
    axes = dict(c=d["c"], L=d["L"], minus_M=-d["M"], l_hat=d["l_hat"], minus_m_hat=-d["m_hat"], sham=d["sham"])
    rows, base_x = [], []
    for label in ["unedited"] + list(ctx["matched"]):
        means, push, norm = [], [], []
        for s in range(0, len(jobs), BATCH):
            batch = jobs[s:s + BATCH]
            enc, mask = encode(tok, batch, device)
            seen = {}

            def capture(_m, _i, out):
                seen["h"] = (out[0] if isinstance(out, tuple) else out).float()
            handles = [b.register_forward_hook(h) for b, h in hooks_for(label, mask, model, ctx)]
            handles.append(model.model.layers[LAYER_MATCHED].register_forward_hook(capture))
            model(**enc, logits_to_keep=1)
            for h in handles:
                h.remove()
            h = seen["h"]
            means.append(torch.stack([h[b][mask[b]].mean(0) for b in range(len(batch))]).cpu().numpy())
            x = h[mask].cpu().numpy()
            norm.append(np.linalg.norm(x, axis=1))
            if label == "unedited":
                base_x.append(x)
            else:
                # Size of the push at each token: |beta * (h - mu).c|, from the unedited activations of the same batch.
                beta = ctx["matched"][label][1]
                push.append(np.abs(beta * (base_x[s // BATCH] - d["mu"]) @ d["c"]))
        H = np.concatenate(means)
        norm = np.concatenate(norm)
        row = dict(edit=label, beta=np.nan if label == "unedited" else ctx["matched"][label][1],
                   a_dot_c=np.nan if label == "unedited" else float(ctx["matched"][label][0] @ d["c"]),
                   token_norm_mean=float(norm.mean()))
        if push:
            push = np.concatenate(push)
            row.update(token_push_mean=float(push.mean()), token_push_rms=float(np.sqrt((push ** 2).mean())), token_push_max=float(push.max()))
        for split, pairs in (("all", list(range(1, 21))), ("estimation", sp["estimation"]), ("heldout", sp["heldout"])):
            keep = np.isin(pid, pairs)
            diff = H[keep & ext].mean(0) - H[keep & ~ext].mean(0)
            row.update({f"{split}_proj_{k}": float(diff @ v) for k, v in axes.items()})
        pc = H[ext] @ d["c"] - H[~ext] @ d["c"]
        row["pairs_ext_gt_mod_on_c"] = float((pc[np.argsort(pid[ext])] > 0).mean())
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(RES / "matched_unit_test.csv", index=False)
    print(df.T.round(3).to_string())


def tag(label):
    return label.removeprefix("matched_")


def crossover(label):
    out = RES / f"matched_crossover_ratings_{tag(label)}.csv"
    rate([label], out, CROSS_CONDITIONS)
    r = pd.read_csv(out)
    assert len(r) == len(CROSS_CONDITIONS) * 160 and not r.duplicated(KEY + ["condition"]).any()
    base = pd.read_csv(RES / "baseline_ratings.csv")
    base = base[base["condition"].isin(CROSS_CONDITIONS) & base["question"].isin(RATE_QUESTIONS)].assign(edit="unedited_baseline")
    r.groupby("condition")["mass"].agg(["mean", "min"]).to_csv(RES / f"matched_crossover_mass_{tag(label)}.csv")
    both = pd.concat([r, base[r.columns.intersection(base.columns)]])
    w = both.pivot_table(index=["edit", "condition", "pair_id", "question"], columns="level", values="score").reset_index()
    w["penalty"] = w["extreme"] - w["moderate"]
    pen = w.groupby(["edit", "condition", "question"]).agg(mean=("penalty", "mean"), std=("penalty", "std"), count=("penalty", "count"),
                                                           moderate=("moderate", "mean"), extreme=("extreme", "mean")).reset_index()
    pen.to_csv(RES / f"matched_crossover_penalty_{tag(label)}.csv", index=False)
    pd.set_option("display.width", 240, "display.max_rows", 300, "display.max_columns", 30, "display.precision", 3)
    print(r.groupby("condition")["mass"].agg(["mean", "min"]).round(4).to_string())
    print(pen.to_string(index=False))


def matched_short():
    """Reuses the full run's first batches, so scores should match the committed ratings closely."""
    out = ROOT / "results" / "quickstart" / "d_short.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    if not (CACHE / "profiles_L8.npy").exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        tok, model, device = load_model()
        system = (STIM / "system_prompt.txt").read_text().strip()
        prof = pd.read_csv(STIM / "profiles.csv")
        acts = extract([(user_text(system, t), t) for t in prof["text"]], tok, model, device)
        for layer, a in acts.items():
            np.save(CACHE / f"profiles_L{layer}.npy", a)
        prof[["pair_id", "level"]].to_csv(CACHE / "profiles_index.csv", index=False)
        del model
        gc.collect()
        if device.type == "mps":
            torch.mps.empty_cache()
    rate(["unedited", "matched_LEAVE_k0.5", "matched_SHAM_k0.5"], out, pairs=[1, 2])
    ref = pd.concat([pd.read_csv(RES / "matched_ratings.csv"), pd.read_csv(RES / "steering_ratings.csv")])
    r = pd.read_csv(out).merge(ref, on=KEY, suffixes=("", "_ref"))
    assert len(r) == 48
    diff = (r["score"] - r["score_ref"]).abs()
    print(r.groupby("edit").apply(lambda g: (g["score"] - g["score_ref"]).abs().agg(["mean", "max"]), include_groups=False).round(5).to_string())
    print(f"mean abs {diff.mean():.5f}, max abs {diff.max():.5f}, mass mean {r['mass'].mean():.4f}, min {r['mass'].min():.4f}")
    assert diff.max() < 0.05


def penalties(r):
    w = r.pivot_table(index=["edit", "pair_id", "question"], columns="level", values="score").reset_index()
    w["penalty"] = w["extreme"] - w["moderate"]
    return w


def matched_summary():
    d = pd.read_csv(RES / "steering_ratings.csv")
    m = pd.read_csv(RES / "matched_ratings.csv")
    assert not m.duplicated(KEY).any()
    print(m.groupby("edit").size().value_counts().to_string())
    mass = m.groupby("edit")["mass"].agg(["mean", "min"])
    mass.to_csv(RES / "matched_mass.csv")
    w = penalties(pd.concat([m, d[d["edit"].isin(["unedited", "repeat"] + [f"shuffle_{s}" for s in range(N_SHUFFLES)])]]))
    pen = w.groupby(["edit", "question"]).agg(mean=("penalty", "mean"), std=("penalty", "std"), count=("penalty", "count"),
                                              moderate=("moderate", "mean"), extreme=("extreme", "mean")).reset_index()
    pen.to_csv(RES / "matched_penalty.csv", index=False)
    means = pen.set_index(["edit", "question"])["mean"]
    rows = []
    for name in ("LEAVE", "MISSION"):
        for k in MATCHED_KS:
            for q in RATE_QUESTIONS:
                rows.append(dict(edit=f"matched_{name}_k{k}", question=q, penalty=means[(f"matched_{name}_k{k}", q)], sham=means[(f"matched_SHAM_k{k}", q)],
                                 minus_sham=means[(f"matched_{name}_k{k}", q)] - means[(f"matched_SHAM_k{k}", q)]))
    vs = pd.DataFrame(rows)
    vs.to_csv(RES / "matched_vs_sham.csv", index=False)
    noise = pen[pen["edit"].isin(["repeat"] + [f"shuffle_{s}" for s in range(N_SHUFFLES)])].copy()
    noise["minus_unedited"] = noise["mean"] - noise["question"].map(lambda q: means[("unedited", q)])
    noise.to_csv(RES / "matched_noise.csv", index=False)
    pd.set_option("display.width", 240, "display.max_rows", 300, "display.max_columns", 30, "display.precision", 4)
    print(mass.round(4).to_string())
    pen["cell"] = pen["mean"].map("{:+.3f}".format) + " (" + pen["std"].map("{:.3f}".format) + ")"
    print(pen.pivot(index="edit", columns="question", values="cell")[RATE_QUESTIONS].to_string())
    print(vs.pivot(index="edit", columns="question", values="minus_sham")[RATE_QUESTIONS].round(3).to_string())
    print(noise.pivot(index="edit", columns="question", values="minus_unedited")[RATE_QUESTIONS].round(4).to_string())


if __name__ == "__main__":
    pd.set_option("display.width", 240, "display.max_columns", 30, "display.precision", 4)
    {"effects": lambda: print(effects().to_string(index=False)), "steer-check": check, "steer-rate": rate, "steer-summary": summary,
     "matched-test": matched_test, "matched-rate": lambda: rate(list(matched_params()), RES / "matched_ratings.csv"),
     "matched-summary": matched_summary, "crossover": lambda: crossover(sys.argv[2]), "matched-short": matched_short}[sys.argv[1]]()
