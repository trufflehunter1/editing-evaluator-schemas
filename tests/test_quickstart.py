"""End-to-end quickstart test. Run from the repo root: python -m unittest tests.test_quickstart -v"""
import subprocess
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "quickstart"


class Quickstart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "scripts" / "quickstart.py")], check=True, cwd=ROOT)

    def test_measurement(self):
        cos = pd.read_csv(OUT / "cosines.csv")
        self.assertEqual(len(cos), 6)
        self.assertTrue(cos["cosine"].between(-1, 1).all())

    def test_baseline_readout(self):
        r = pd.read_csv(OUT / "baseline_ratings.csv")
        self.assertEqual(len(r), 240)
        self.assertGreater(r["mass"].min(), 0.9)
        self.assertTrue(r["score"].between(1, 7).all())

    def test_baseline_matches_committed_run(self):
        keys = ["pair_id", "level", "condition", "question"]
        r = pd.read_csv(OUT / "baseline_ratings.csv").merge(pd.read_csv(ROOT / "results" / "capcom" / "baseline_ratings.csv"),
                                                            on=keys, suffixes=("", "_ref"))
        self.assertEqual(len(r), 240)
        # Batch composition changes the padding, which moves scores: mean absolute 0.019 and maximum 0.14 between full runs.
        diff = (r["score"] - r["score_ref"]).abs()
        self.assertLess(diff.mean(), 0.05)
        self.assertLess(diff.max(), 0.25)


if __name__ == "__main__":
    unittest.main()
