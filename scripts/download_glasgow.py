"""Download the official Glasgow Norms supplementary data (Scott et al., 2019, BRM, ESM 2)."""
import hashlib
import urllib.request
from pathlib import Path

URL = ("https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-018-1099-3/"
       "MediaObjects/13428_2018_1099_MOESM2_ESM.csv")
SHA256 = "30d7776eed9219767f8a6aabdf95d7120cd050ddeab431acef13d435807bbc39"
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "glasgow" / "13428_2018_1099_MOESM2_ESM.csv"

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUT.exists():
        urllib.request.urlretrieve(URL, OUT)
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    assert digest == SHA256, f"checksum mismatch: {digest}"
    print(f"OK {OUT}")
