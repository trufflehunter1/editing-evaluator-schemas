"""Build the hiring stimuli (DRAFT): candidate profiles and assessment conditions.

profiles.csv has 20 pairs x 2 levels (moderate, extreme). Pair 1 is fixed. For pairs 2-20, school,
bank, title, opportunity/model, reports and deals are drawn independently with a fixed seed, and
every pair is a unique combination. Within a pair only the reports and deals differ.
conditions.csv holds the six assessment texts verbatim, and system_prompt.txt the rating context.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "stimuli"
SEED, N_PAIRS = 0, 20

TEMPLATE = ("Candidate profile (name removed). Education: B.A. in Economics, {school}. "
            "Experience: {title} at {bank}. Managed a team of {reports} to assess and pitch "
            "{opp} opportunities. Created {model} models to support closed deals worth {deals}.")

PAIR_1 = dict(school="a top-ranked private university", title="Associate", bank="an elite investment bank",
              opp="investment", model="LBO financing", reports=(2, 10), deals=("$15 million", "$1.5 billion"))
SCHOOLS = ["a highly selective liberal arts college", "an elite research university",
           "a top-five undergraduate business program"]
BANKS = ["a bulge-bracket investment bank", "a top-tier global investment bank", "a leading Wall Street investment bank"]
TITLES = ["Associate", "Senior Associate"]
OPP_MODEL = [("acquisition", "M&A valuation"), ("financing", "debt financing"), ("equity", "equity offering"),
             ("restructuring", "restructuring")]
REPORTS = [(1, 5), (2, 10), (3, 15), (4, 20)]
DEALS = [("$10 million", "$1 billion"), ("$12 million", "$1.2 billion"), ("$15 million", "$1.5 billion"),
         ("$20 million", "$2 billion"), ("$25 million", "$2.5 billion")]

BASE = ("As part of the application process, the candidate completed an assessment delivered by your firm's HR "
        "department. The candidate scored 75; candidates that have scored at least 60 points have skills that "
        "match the requirements of the job. ")
ABILITY = "This assessment was able to predict the candidate's ability to do the job in your firm."
COMMITMENT = ("This assessment was able to predict the candidate's likely commitment to your organization (e.g., "
              "likelihood to stay with your firm, be motivated and work well with others).")
TRUSTED = " You have received an additional piece of information about the candidate from a trusted source: "
NEUTRAL = BASE + ABILITY
CONDITIONS = {
    "neutral": NEUTRAL,
    "commitment_info": BASE + COMMITMENT,
    "mission": NEUTRAL + TRUSTED + "this candidate is excited about the firm's mission.",
    "pay": NEUTRAL + TRUSTED + "this candidate is excited about the firm's pay package.",
    "rejected_options": NEUTRAL + TRUSTED + ("this candidate has turned down other offers in investment banking "
                                             "and other health care companies."),
    "open_options": NEUTRAL + TRUSTED + ("there has been an industry downturn and your firm is the only one "
                                         "hiring right now."),
}
SYSTEM_PROMPT = ("You are a line manager hiring for a corporate finance position in a medium-sized health care "
                 "company. Do not concern yourself with negotiating the offer; consider only this candidate's "
                 "performance on the job.")


def direct_reports(n):
    return f"{n} direct report" + ("" if n == 1 else "s")


def draw_pairs(rng):
    pairs, seen = [PAIR_1], set()
    while len(pairs) < N_PAIRS:
        opp, model = OPP_MODEL[rng.integers(len(OPP_MODEL))]
        p = dict(school=SCHOOLS[rng.integers(len(SCHOOLS))], title=TITLES[rng.integers(len(TITLES))],
                 bank=BANKS[rng.integers(len(BANKS))], opp=opp, model=model,
                 reports=REPORTS[rng.integers(len(REPORTS))], deals=DEALS[rng.integers(len(DEALS))])
        key = tuple((k, str(v)) for k, v in p.items())
        if key not in seen:
            seen.add(key)
            pairs.append(p)
    return pairs


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for pid, p in enumerate(draw_pairs(np.random.default_rng(SEED)), start=1):
        for j, level in enumerate(("moderate", "extreme")):
            fields = {k: v for k, v in p.items() if k not in ("reports", "deals")}
            rows.append(dict(pair_id=pid, level=level, **fields, reports=p["reports"][j], deals=p["deals"][j],
                             text=TEMPLATE.format(**fields, reports=direct_reports(p["reports"][j]), deals=p["deals"][j])))
    prof = pd.DataFrame(rows)
    prof[["pair_id", "level", "text"]].to_csv(OUT / "profiles.csv", index=False)
    prof.drop(columns="text").to_csv(OUT / "profiles_factors.csv", index=False)
    pd.DataFrame(dict(condition=list(CONDITIONS), text=list(CONDITIONS.values()))).to_csv(OUT / "conditions.csv",
                                                                                           index=False)
    (OUT / "system_prompt.txt").write_text(SYSTEM_PROMPT + "\n")
    print(prof.drop(columns="text").to_string(index=False))


if __name__ == "__main__":
    main()
