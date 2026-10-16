"""Fetch citations, h-index and i10-index from Google Scholar and save them to data/scholar.json.

If Google Scholar blocks the request (it sometimes does for automated traffic),
the script leaves the existing file unchanged, so the website keeps the last good numbers.
"""
import datetime
import json
import pathlib
import sys

from scholarly import scholarly

SCHOLAR_ID = "CiLrxdcAAAAJ"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "scholar.json"

try:
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["indices"])
except Exception as exc:  # network error or blocked by Google
    print(f"Could not reach Google Scholar, keeping existing numbers: {exc}")
    sys.exit(0)

data = {
    "citations": int(author.get("citedby", 0)),
    "hindex": int(author.get("hindex", 0)),
    "i10index": int(author.get("i10index", 0)),
    "updated": datetime.date.today().isoformat(),
}

if data["citations"] <= 0:
    print("Got empty numbers from Google Scholar, keeping existing file.")
    sys.exit(0)

old = {}
if OUT.exists():
    old = json.loads(OUT.read_text(encoding="utf-8"))
if all(old.get(k) == data[k] for k in ("citations", "hindex", "i10index")):
    print("No change in metrics.")
    sys.exit(0)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print("Updated:", data)
