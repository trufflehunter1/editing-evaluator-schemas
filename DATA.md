# Data

## Committed

| Path | Contents | Why it is committed |
|---|---|---|
| `items.csv` | 600 words with Glasgow gender ratings (CC BY 4.0) | Defines the validation; the selection depends on a seed |
| `items_capcom.csv`, `stimuli/capcom_words.txt` | Capability, commitment and neutral words with Zipf frequencies. Warriner valence is not committed; `src/items.py` attaches it at run time | Hand-curated, so they cannot be regenerated |
| `stimuli/` | Profiles, conditions, sentences, system prompt | Exact inputs to the model |
| `directions/` | Direction vectors estimated from model activations | Needed to rerun edits without re-extracting |
| `results/` | Result tables | The reported numbers, listed in `RESULTS.md` |

## Downloaded by script

| Path | Source | Script | Why it is not committed |
|---|---|---|---|
| `data/raw/glasgow/` | Scott et al. (2019), *Behavior Research Methods*, ESM 2. CC BY 4.0 | `scripts/download_glasgow.py` | The publisher hosts the official file; the script checks its SHA-256 |
| `data/raw/warriner/` | Warriner, Kuperman & Brysbaert (2013), *Behavior Research Methods*, ESM 1. The publisher's page states no open license | `scripts/download_warriner.py` | Redistribution terms are unclear; the script checks the SHA-256 |
| `.hf_cache/` | `google/gemma-2-2b-it`, `google/gemma-2-2b` | Downloaded on first use | Large, and governed by the Gemma Terms of Use, which each user accepts |

## Generated locally and not committed

`data/activations/`, `data/activations_it/`, `data/activations_it_capcom/` and `data/profile_acts/` are activation
caches, rebuilt by `scripts/extract_activations.py` and `scripts/profile_directions.py`. `results/quickstart/` is written
by the quickstart.

`directions/profile_it_{heldout,est_half_a,est_half_b}_L{8,13}.npz` and `directions/profile_it_pathspecific_L{8,13}.npz` are
also gitignored. `scripts/profile_directions.py` and `scripts/path_directions.py` regenerate them, and no reported number
reads them.

## Stimuli and third-party text

- Pair 1 of `stimuli/profiles.csv` and the condition texts in `stimuli/conditions.csv` are adapted from Galperin, R. V.,
  Hahl, O., Sterling, A. D., & Guo, J. (2020). Too good to hire? Capability and inferences about commitment in labor
  markets. *Administrative Science Quarterly*, 65(2), 275-313. The profile format follows that article's Online
  Appendix B, and `stimuli/system_prompt.txt` adapts its rating context.
- Profile pairs 2 to 20 and the 160 sentences in `stimuli/sentences.csv` were written for this project.
- The `in_anderson` column of `items_capcom.csv` marks words on the Anderson (1968) trait list.

## Other sources

The Zipf frequencies in `items_capcom.csv` come from the wordfreq package.
