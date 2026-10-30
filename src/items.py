from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_items() -> pd.DataFrame:
    return pd.read_csv(ROOT / "items.csv")


def pole_sets(n: int = 100) -> tuple[list[str], list[str]]:
    """Top-n masculine and feminine words from items.csv (Glasgow GEND: 7 = masculine, 1 = feminine).

    Ties are broken by the word, so the sets do not depend on row order.
    """
    ranked = load_items().sort_values(["glasgow_gender", "item"])
    return ranked["item"].tail(n).tolist(), ranked["item"].head(n).tolist()


def attach_valence(df, word_col="word"):
    """Add warriner_valence from the downloaded norms (scripts/download_warriner.py); blank if unrated."""
    path = ROOT / "data" / "raw" / "warriner" / "extracted" / "BRM-emot-submit.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing; run scripts/download_warriner.py first")
    w = pd.read_csv(path, keep_default_na=False, low_memory=False)
    return df.assign(warriner_valence=df[word_col].map(w.set_index("Word")["V.Mean.Sum"]))
