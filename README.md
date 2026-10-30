# Measuring and editing an AI evaluator's associations

This repository measures how a language model acting as an evaluator represents social concepts, then edits those
associations directly and observes how its ratings change. The case is adapted from a published hiring experiment on
capability and commitment (Galperin, Hahl, Sterling & Guo, 2020, *Administrative Science Quarterly*). In
`google/gemma-2-2b-it` we estimate a capability direction and commitment, mission and leaving directions, obtain
baseline ratings of candidate profiles, and change the capability direction at the profile tokens during the forward
pass. Only public data and open models are used.

## What's here

- **Core pipeline:** `stimuli/` and `items_capcom.csv` (inputs); the scripts listed under "Which script makes which
  file" (directions, baseline ratings, editing pilot, direct steering, matched-magnitude edit, information crossover).
- **Minimal validation:** `items.csv` and `scripts/validate_gender.py`. It checks a gender direction and the
  evaluator's ratings against the Glasgow Norms, and compares the direction across the base and instruction-tuned models.
- **Results:** `RESULTS.md` gives every reported number with its value, script and file. Tables are in
  `results/capcom/` (core) and `results/validation/` (validation); direction vectors are in `directions/`.
- **Tests:** `tests/test_quickstart.py`. Sources and licenses are in `DATA.md`.

## Setup

**Gemma license and Hugging Face access.** The models are gated. Accept the Gemma Terms of Use on the Hugging Face pages
of `google/gemma-2-2b-it` and `google/gemma-2-2b` (terms: <https://ai.google.dev/gemma/terms>), then create a read token.

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
cp .env.example .env   # then add your Hugging Face token
```

`requirements.lock` pins the exact versions; `requirements.txt` lists the direct dependencies.

**Hardware used.** Apple M2 Pro laptop with 16 GB of memory, using MPS, with Python 3.11. About 10 GB of disk is enough.
`src/device.py` falls back to CPU when MPS is not available; only MPS was used for the results.

## Runtime

Measured on that machine; the first three rows ran together from a fresh clone. Other rating prompts took about 0.8 s each, which gives the approximate times.

| Job | Prompts | Time |
|---|---|---|
| Quickstart test, cold (fresh clone, install, model download) | 564 | 9 min 33 s |
| `scripts/validate_gender.py`, after the quickstart (includes the base model download) | 6,000 | 7 min 40 s |
| `scripts/steering_diagnostics.py matched-short` | 88 | 84 s |
| `scripts/profile_directions.py` | 3,240 | about 40 min |
| `scripts/baseline_ratings.py` | 2,400 | about 30 min |
| `scripts/edit_pilot.py tests`, `rate` | about 2,000 | about 30 min |
| `scripts/steering_diagnostics.py steer-rate` | 2,720 | about 40 min |
| `matched-rate`, `crossover` | 2,080 | about 30 min |

## Seeds

Every seed is 0 unless noted.

| Script | Used for |
|---|---|
| `scripts/build_items.py` | Selecting the 600 items |
| `scripts/build_stimuli.py` | Drawing the profile pairs |
| `scripts/profile_directions.py` | Estimation, held-out and half splits of the pairs |
| `scripts/path_directions.py` | 20/20 sentence splits |
| `scripts/edit_pilot.py`, `scripts/steering_diagnostics.py` | Sham direction |
| `scripts/steering_diagnostics.py` | Shuffled batch runs, seeds 0, 1, 2 |

Model outputs also depend on batch composition, because it changes the padding. For the same 200 unedited prompts in
different batches, two runs differ by 0.019 on average (maximum 0.14). Repeating a run in the same batches gave identical
scores. All comparisons between edits use the same batches, at batch size 8.

## Quickstart

Runs the direction measurement and the baseline on 2 profile pairs. It downloads the model on first use and writes to
`results/quickstart/`, leaving committed results unchanged.

```bash
python -m unittest tests.test_quickstart -v
```

To run the validation, then a short check of the matched-magnitude edit against the committed ratings:

```bash
python scripts/download_glasgow.py
python scripts/validate_gender.py --out results/validation_rerun
python scripts/steering_diagnostics.py matched-short
```

`items.csv` is committed, so `download_glasgow.py` is needed only to rebuild it with `scripts/build_items.py`.

## Which script makes which file

Paths are relative to the repo root. `data/` holds gitignored activation caches. Run `scripts/download_warriner.py` before
`scripts/profile_directions.py` or `scripts/path_directions.py`, which attach valence at run time.

| Script | Produces |
|---|---|
| `scripts/download_glasgow.py`, `scripts/download_warriner.py` | `data/raw/glasgow/`, `data/raw/warriner/` |
| `scripts/build_stimuli.py` | `stimuli/profiles.csv`, `profiles_factors.csv`, `conditions.csv`, `system_prompt.txt` |
| `scripts/build_sentences.py` | `stimuli/sentences.csv` |
| `scripts/extract_activations.py --model it --words stimuli/capcom_words.txt --out data/activations_it_capcom` | `data/activations_it_capcom/` |
| `scripts/profile_directions.py` | `data/profile_acts/`, `directions/profile_it_{estimation,heldout,est_half_a,est_half_b}_L{8,13}.npz`, `results/capcom/{cosines,stability,word_projections,valence_correlation,sentence_spread,sentence_overlap,splits}.csv` |
| `scripts/path_directions.py` | `directions/profile_it_pathspecific_L{8,13}.npz`, `results/capcom/path_*.csv` |
| `scripts/baseline_ratings.py` | `results/capcom/baseline_{ratings,mass,penalty}.csv` |
| `scripts/edit_pilot.py tests` | `directions/path_gs_L8.npz`, `results/capcom/edit_{unit_tests,probe,hook_check}.csv` |
| `scripts/edit_pilot.py rate` | `results/capcom/edit_{ratings,mass,penalty}.csv` |
| `scripts/steering_diagnostics.py effects` | `results/capcom/natural_effects.csv` |
| `scripts/steering_diagnostics.py steer-check`, `steer-rate`, `steer-summary` | `results/capcom/steering_{check,ratings,change,noise,mass}.csv` |
| `scripts/steering_diagnostics.py matched-test`, `matched-rate`, `matched-summary` | `results/capcom/matched_{unit_test,ratings,mass,penalty,vs_sham,noise}.csv` |
| `scripts/steering_diagnostics.py crossover EDIT` | `results/capcom/matched_crossover_{ratings,mass,penalty}_*.csv` |
| `scripts/build_items.py` | `items.csv` |
| `scripts/validate_gender.py`, with `extract_activations.py`, `behavioral_ratings.py`, `compare_models.py` | `data/activations/`, `data/activations_it/`, `directions/{base,it}_meanpool_gender_L{4,8,13,18}.npz`, `results/validation/` |
| `scripts/quickstart.py` | `results/quickstart/` (gitignored) |

`items_capcom.csv` and `stimuli/capcom_words.txt` are curated by hand and have no build script.

Of the `profile_it_*` direction files, only `estimation` is committed, because the edits read it. The `heldout`,
`est_half_a`, `est_half_b` and `pathspecific` files are gitignored outputs that no reported number reads; the two scripts
above regenerate them.

## Adding a new case

To test a different association, such as motherhood and commitment, edit the data files below and run the scripts in the
order of the table above. This was checked by replacing the profiles with motherhood profiles and running
`scripts/quickstart.py` with no code edits. The direction measurement and the baseline ran. The later steps read the same
files but were not run on a new case.

| File | Change |
|---|---|
| `stimuli/profiles.csv` | One row per profile: `pair_id`, `level`, `text`. Use the new attribute in place of the capability difference |
| `stimuli/sentences.csv` | Sentences for each path, if the paths change in content |
| `stimuli/conditions.csv` | Text of the information conditions |
| `stimuli/system_prompt.txt` | The evaluator's context |
| `items_capcom.csv`, `stimuli/capcom_words.txt` | Word lists for the word projections |

Edit these CSV files directly: `scripts/build_stimuli.py` and `scripts/build_sentences.py` overwrite them.

The code currently fixes these, so keep them or edit the scripts:

- **Levels:** must be named `moderate` and `extreme`, with `extreme` as the level holding the attribute.
- **Pairs:** 20 pairs numbered 1 to 20 (`splits()` in `scripts/profile_directions.py`).
- **Sentence sets:** must be named `commitment`, `mission`, `leaving` and `neutral`, with 40 in each for `scripts/path_directions.py`.
- **Conditions:** a `neutral` condition is required. The crossover also needs `mission`, `pay`, `rejected_options` and `open_options`.

These need code edits:

- **Questions:** `QUESTIONS` in `scripts/baseline_ratings.py`, and the question lists in `scripts/edit_pilot.py` and `scripts/steering_diagnostics.py`.
- **Matched-magnitude targets:** `NATURAL` in `scripts/steering_diagnostics.py` holds this case's natural effects (24.02, 27.26).
- **Output location:** scripts write to `results/capcom/` and `directions/`, replacing this case's results. Work in a copy of the repo.
- **Quickstart test:** it compares with the committed baseline ratings, so its match check fails on a new case. Use `scripts/quickstart.py`.

## Method notes

**Directions.** Gemma 2's chat template has no system role, so the system context goes first in the user turn, followed by
the profile and any sentence. Layer L is the residual stream after block L (HF `hidden_states[L + 1]`). Capability is the
mean extreme-minus-moderate difference over profile tokens. Commitment, mission and leaving are the mean difference between
pole and neutral sentences over sentence tokens, on moderate profiles.

**Readout.** The prompt ends "Answer with a single digit from 1 to 7." and the model turn is prefilled with `Rating: `, with the
trailing space. The score is the expected value over the digit tokens 1 to 7, and digit mass is their total probability.

**Editing pilot.** `scripts/edit_pilot.py` edits layer 8 at the profile tokens. L is the leaving direction with the mission
direction removed, and M is the mission direction with the leaving direction removed. For a unit path direction a, the edit
centres on the mean profile activation and applies, in the plane of a and capability, the linear map that sends capability
to a target cosine with a. LEAVE uses a = L, MISSION uses a = -M, and SHAM uses a random unit vector orthogonal to c, L and M.
The model runs in bfloat16, so edited activations are rounded when written back; `results/capcom/edit_hook_check.csv`
compares the hook's output with the exact edit.

**Diagnostics.** `scripts/steering_diagnostics.py` measures natural effects, adds a fixed vector at the profile tokens (direct
steering at layer 8 or 13), and applies a capability-dependent push at layer 8, h' = h + beta * ((h - mu).c) * a. Ratings are
appended to CSV every 100 prompts, so a stopped job resumes where it left off.

**Validation.** Word activations use the prompts of Kozlowski & Boutyline (2026), mean-pooled over tokens except BOS, then
averaged across the four prompts. Each prompt is wrapped in the chat template for the instruction-tuned model.

## Data sources and licenses

Details are in [DATA.md](DATA.md). Code is under the MIT license ([LICENSE](LICENSE)).

| Source | Used for | Access | License |
|---|---|---|---|
| Glasgow Norms (Scott et al., 2019) | Gender ratings | `scripts/download_glasgow.py` | CC BY 4.0 |
| Warriner et al. (2013) norms | Valence ratings | `scripts/download_warriner.py` | No open license stated by the publisher |
| Hiring stimuli | Profiles, conditions, sentences | `stimuli/` | Pair 1 and the condition texts adapted from Galperin et al. (2020, *Administrative Science Quarterly*); pairs 2 to 20 and the 160 sentences written for this project |
| `google/gemma-2-2b-it`, `google/gemma-2-2b` | Models | Hugging Face | Gemma Terms of Use |
