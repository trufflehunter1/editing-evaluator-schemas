"""Build the hiring stimuli (DRAFT): candidate profiles and assessment conditions.

profiles.csv has 20 pairs x 2 levels (moderate, extreme), following the social-media profile in
Galperin et al. (2020), Online Appendix B. Pair 1 extreme is verbatim, and pair 1 moderate swaps in
$15 million and 2 direct reports. For pairs 2-20, the current bank, internship firm, school + degree,
model type, reports and deal size are drawn with a fixed seed, and every pair is a unique
combination. Within a pair only the reports and deal size differ. The $1 billion internship bullet,
the dates and all other text stay constant.
conditions.csv holds the six assessment texts verbatim, and system_prompt.txt the rating context.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "stimuli"
SEED, N_PAIRS = 0, 20

# Galperin et al. (2020), Online Appendix B, with pair 1 extreme reproduced verbatim.
TEMPLATE = """Please review the following profile taken from a social media site.

Analyst - Investment Banking Division at {bank}
New York, New York | Financial Services
Previous: {intern}
Education: {school}

Summary
- Created {model} to support {deals} M&A transaction
- Led team of {reports} to assess investment opportunities and build pitch-books supporting North American deals
- Participated in all stages of capital raising process for $1 billion in common stock, preferred stock, and bond offerings

Experience
Analyst - Investment Banking Division, {bank}
August 2011 - Present (4 years 2 months) | New York, NY
- Created {model} to support {deals} M&A transaction
- Developed financial valuation models and analyzed investment opportunities in the healthcare sector
- Led team of {reports} to assess investment opportunities and build pitch-books supporting North American deals

Summer Intern, {intern}
June 2010 - August 2010 (3 months) | New York, NY
- Performed financial analysis via pro forma cash flow models
- Participated in all stages of capital raising process for $1 billion in common stock, preferred stock, and bond offerings

Education
{school}
{degree}
2007 - 2011"""

CORNELL = ("Cornell University", "Bachelor of Science (B.S.), Applied Economics and Management, Concentration: Finance")
PAIR_1 = dict(bank="Merrill Lynch", intern="UBS", school=CORNELL[0], degree=CORNELL[1], model="LBO financing model",
              reports=(2, 10), deals=("$15 million", "$1.5 billion"))
BANKS = ["Goldman Sachs", "Morgan Stanley", "J.P. Morgan", "Citi", "Barclays", "Bank of America"]
INTERNS = ["UBS", "Lazard", "Evercore", "Deutsche Bank"]
SCHOOLS = [CORNELL,
           ("University of Pennsylvania", "Bachelor of Science (B.S.), Economics, Concentration: Finance"),
           ("Columbia University", "Bachelor of Arts (B.A.), Economics"),
           ("Dartmouth College", "Bachelor of Arts (B.A.), Economics"),
           ("Northwestern University", "Bachelor of Arts (B.A.), Economics"),
           ("Duke University", "Bachelor of Arts (B.A.), Economics")]
MODELS = ["LBO financing model", "merger valuation model", "acquisition financing model"]
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
        bank = BANKS[rng.integers(len(BANKS))]
        options = [f for f in INTERNS if f != bank]
        intern = options[rng.integers(len(options))]
        school, degree = SCHOOLS[rng.integers(len(SCHOOLS))]
        p = dict(bank=bank, intern=intern, school=school, degree=degree, model=MODELS[rng.integers(len(MODELS))],
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
