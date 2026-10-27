"""Write stimuli/sentences_DRAFT.csv: 40 sentences each for mission, leaving, commitment, neutral.

Every sentence has the form "The candidate ..." and contains no personal, possessive, reflexive or
relative pronouns. One exception is "what" in one mission sentence. The script
checks for pronouns, for any 3-word sequence shared with stimuli/conditions.csv or the system
prompt, and reports length per set.
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "stimuli"

SETS = {
    "mission": """
The candidate cares deeply about what this organization is trying to achieve.
The candidate strongly believes in the purpose behind this organization's work.
The candidate finds real meaning in the goals of this company.
The candidate is inspired by the larger purpose of this organization.
The candidate wants to advance the central aims of this company.
The candidate identifies closely with the values of this organization.
The candidate sees the work of this company as genuinely important.
The candidate is drawn to this organization because of the cause.
The candidate shares the core values guiding this organization.
The candidate wants to contribute to the purpose of this company.
The candidate is passionate about the goals this organization pursues.
The candidate feels a strong personal connection to this company's purpose.
The candidate admires the cause at the heart of this organization.
The candidate is eager to serve the purpose of this company.
The candidate considers this organization's goals worth working toward.
The candidate strongly supports the vision guiding this company.
The candidate hopes to help this organization achieve a lasting impact.
The candidate values the difference this company makes for patients.
The candidate is moved by the work this organization does.
The candidate wants to be part of this company's larger purpose.
The candidate believes in the long-term vision of this organization.
The candidate feels proud to support the aims of this company.
The candidate is devoted to the cause this organization serves.
The candidate sees personal purpose in this company's goals.
The candidate cares about the people this organization aims to help.
The candidate embraces the values at the core of this company.
The candidate is enthusiastic about the purpose behind this organization.
The candidate wants to further the goals this company stands for.
The candidate finds the aims of this organization deeply worthwhile.
The candidate is dedicated to advancing this company's purpose.
The candidate strongly endorses the goals of this organization.
The candidate relates personally to the vision of this company.
The candidate wants to make this organization's vision a reality.
The candidate is energized by the purpose of this company.
The candidate shares a deep belief in this organization's goals.
The candidate is attracted to the meaningful work of this company.
The candidate wants to help this organization reach the central goal.
The candidate feels aligned with the values behind this company's work.
The candidate takes pride in the goals of this organization.
The candidate cares about the outcomes this company works toward.
""",
    "leaving": """
The candidate sees this job as a stepping stone.
The candidate plans to move to another employer within a year.
The candidate treats this role as a short stop on the way elsewhere.
The candidate expects to leave once a better opportunity appears.
The candidate is already looking ahead to the next job.
The candidate views this position as a temporary arrangement.
The candidate will probably switch companies after a short time.
The candidate keeps an eye on openings at other companies.
The candidate intends to move on after gaining some experience.
The candidate sees little reason to remain here for long.
The candidate is likely to leave within the first two years.
The candidate regards this role as a way to build a resume.
The candidate plans to depart once a promotion elsewhere comes up.
The candidate expects to change employers several times.
The candidate treats this company as a brief career stop.
The candidate is likely to jump at the next attractive opening.
The candidate already has plans for the next career move.
The candidate sees this position as a short-term step.
The candidate is ready to leave whenever a better role appears.
The candidate views this job mainly as a launching pad.
The candidate tends to change jobs every year or two.
The candidate considers this role a temporary stage.
The candidate plans to stay only until the next opportunity.
The candidate is open to leaving for a bigger title.
The candidate will likely move to a rival company soon.
The candidate sees no long future at this company.
The candidate expects to outgrow this position quickly.
The candidate is keeping other career options open.
The candidate plans to leave after one or two projects.
The candidate is unlikely to remain here for many years.
The candidate views this company as a place to pass through.
The candidate is already preparing for the next employer.
The candidate treats this job as a brief chapter.
The candidate would leave quickly for a role in a bigger city.
The candidate expects to be gone within eighteen months.
The candidate sees this role as practice for a better job.
The candidate keeps a resume ready for the next move.
The candidate plans a short stay before moving elsewhere.
The candidate regards this company as one stop among many.
The candidate is likely to leave once enough experience is gained.
""",
    "commitment": """
The candidate is fully committed to whichever employer the candidate joins.
The candidate stays loyal to an employer through difficult times.
The candidate gives full effort to every job taken on.
The candidate tends to remain with an employer for many years.
The candidate takes every job obligation very seriously.
The candidate sticks with an employer even when work gets hard.
The candidate is dependable over the long run in any role.
The candidate follows through on every commitment made at work.
The candidate is devoted to any workplace joined.
The candidate shows strong loyalty to every employer.
The candidate puts long hours into any role when needed.
The candidate builds a long career at each workplace.
The candidate stays the course on long and difficult projects.
The candidate is known for steady loyalty to employers.
The candidate remains dedicated regardless of the employer.
The candidate treats each job as a long-term commitment.
The candidate rarely gives up on a role once started.
The candidate is consistently loyal to colleagues and employers.
The candidate sees each role through to the very end.
The candidate shows lasting dedication to every position held.
The candidate stays with each employer through ups and downs.
The candidate is reliably present for the team every day.
The candidate brings steady dedication to any job.
The candidate keeps every promise made to an employer.
The candidate stays engaged with the job over many years.
The candidate is a loyal employee at every workplace.
The candidate invests fully in each organization joined.
The candidate remains steadfast in every role held.
The candidate commits fully to any employer chosen.
The candidate is loyal to the workplace for the long haul.
The candidate tends to stay put once hired.
The candidate holds firm to obligations at work.
The candidate shows deep dedication to any employer.
The candidate stays with a job until the work is done.
The candidate puts the employer first in every role.
The candidate has a record of long tenure at each employer.
The candidate gives every employer full loyalty.
The candidate is equally dedicated to every workplace.
The candidate remains loyal to each company over time.
The candidate treats any job as a lasting commitment.
""",
    "neutral": """
The candidate lives near the office.
The candidate usually drives a small blue car to work.
The candidate enjoys hiking in the hills on most weekends.
The candidate grew up in a small town near the coast.
The candidate prefers a cup of tea over coffee.
The candidate plays the piano at home in the evenings.
The candidate walks a large dog around the block daily.
The candidate reads mystery novels before going to sleep.
The candidate takes the train into the city most mornings.
The candidate owns a small apartment in the downtown area.
The candidate likes to cook Italian food for family dinners.
The candidate wears glasses for reading small print.
The candidate was born in a city in the Midwest.
The candidate speaks a little Spanish learned in high school.
The candidate enjoys watching basketball games on television.
The candidate has visited several national parks over the years.
The candidate grows tomatoes and peppers in the backyard.
The candidate rides a bicycle around town on sunny days.
The candidate collects old postcards from different countries.
The candidate enjoys playing board games with close friends.
The candidate is left-handed and writes with a fountain pen.
The candidate prefers vacations in the mountains over the beach.
The candidate listens to jazz records while cooking dinner.
The candidate has two younger siblings living in another state.
The candidate runs a few miles in the park each morning.
The candidate enjoys painting landscapes in watercolor.
The candidate recently moved to a quiet new neighborhood.
The candidate likes to bake fresh bread on Sunday mornings.
The candidate wears the same silver wristwatch every day.
The candidate enjoys solving crossword puzzles over breakfast.
The candidate keeps a small garden full of spring flowers.
The candidate drinks black coffee without any sugar.
The candidate took a long road trip through Canada last year.
The candidate enjoys photography as a weekend hobby.
The candidate plays tennis at a local club on Saturdays.
The candidate prefers cold winter days to hot summer days.
The candidate owns a large collection of old vinyl records.
The candidate likes to walk in the park during lunch.
The candidate shares a small house with a gray cat.
The candidate enjoys visiting art museums on rainy afternoons.
""",
}
PRONOUNS = r"\b(i|me|my|mine|myself|you|your|yours|yourself|he|him|his|himself|she|her|hers|herself|it|its|itself|" \
           r"we|us|our|ours|ourselves|they|them|their|theirs|themselves|who|whom|whose|which|that|what)\b"
ALLOWED = {("mission", 0)}  # one sentence uses "what"


def trigrams(text):
    w = re.findall(r"[a-z']+", text.lower())
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)}


def main():
    rows = [dict(set=s, idx=i, sentence=x.strip()) for s, block in SETS.items()
            for i, x in enumerate([ln for ln in block.strip().splitlines() if ln.strip()])]
    df = pd.DataFrame(rows)
    df["n_words"] = df["sentence"].str.split().str.len()
    assert (df.groupby("set").size() == 40).all(), df.groupby("set").size()
    assert df["sentence"].str.startswith("The candidate ").all()
    assert not df["sentence"].duplicated().any()
    bad = [(r.set, r.idx, r.sentence) for r in df.itertuples()
           if re.search(PRONOUNS, r.sentence.lower()) and (r.set, r.idx) not in ALLOWED]
    ref = set().union(*[trigrams(t) for t in pd.read_csv(OUT / "conditions.csv")["text"]],
                      trigrams((OUT / "system_prompt.txt").read_text()))
    ref -= {("the", "candidate", w) for w in ("is", "has", "completed", "scored")}
    overlap = [(r.set, r.sentence, sorted(trigrams(r.sentence) & ref)) for r in df.itertuples()
               if trigrams(r.sentence) & ref]
    df.insert(0, "status", "DRAFT")
    df.to_csv(OUT / "sentences_DRAFT.csv", index=False)
    print(df.groupby("set", sort=False)["n_words"].agg(["mean", "std", "min", "max"]).round(2))
    print("pronoun hits:", bad)
    print("3-gram overlaps with conditions/system prompt:", overlap)


if __name__ == "__main__":
    main()
