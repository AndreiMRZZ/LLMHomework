# Core/summary_tool.py
from functools import lru_cache
from pathlib import Path
import unicodedata
import re
import json

CANDIDATE_PATHS = [
    Path("summaries.json"),
    Path(__file__).resolve().parents[1] / "summaries.json",
    Path(__file__).resolve().parent / "summaries.json",
]

def _normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def _find_summaries_path() -> Path:
    for p in CANDIDATE_PATHS:
        if p.exists():
            return p
    raise FileNotFoundError(
        "Nu am gasit summaries.json. Plaseaza-l in radacina proiectului sau langa summary_tool.py."
    )

@lru_cache(maxsize=1)
def _load_dict() -> dict:
    path = _find_summaries_path()
    with path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    d = {
        _normalize(entry["title"]): entry["summary"]
        for entry in raw_data
        if entry.get("title") and entry.get("summary")
    }
    if not d:
        raise ValueError(f"{path.name} nu contine perechi title/summary valide.")
    return d

def get_summary_by_title(title: str) -> str:
    d = _load_dict()
    key = _normalize(title)
    if key in d:
        return d[key]
    raise KeyError(f"Titlul '{title}' nu a fost gasit in baza locala.")
