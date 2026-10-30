"""Download the Warriner et al. (2013, BRM) valence norms (ESM 1) and extract BRM-emot-submit.csv."""
import hashlib
import urllib.request
import zipfile
from pathlib import Path

URL = ("https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-012-0314-x/"
       "MediaObjects/13428_2012_314_MOESM1_ESM.zip")
SHA256 = "5a0db0437ef234219fb899caced5eb3195dbf9f84396637ab4db74c50ca441aa"
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "warriner" / "13428_2012_314_MOESM1_ESM.zip"

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUT.exists():
        urllib.request.urlretrieve(URL, OUT)
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    assert digest == SHA256, f"checksum mismatch: {digest}"
    with zipfile.ZipFile(OUT) as z:
        names = [n for n in z.namelist() if n.endswith("BRM-emot-submit.csv")]
        assert names, z.namelist()
        (OUT.parent / "extracted").mkdir(exist_ok=True)
        (OUT.parent / "extracted" / "BRM-emot-submit.csv").write_bytes(z.read(names[0]))
    print(f"OK {OUT}")
