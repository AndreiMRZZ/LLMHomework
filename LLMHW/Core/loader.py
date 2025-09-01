from pathlib import Path
from typing import List, Dict, Tuple
import json

def load_book_summaries(json_path: str) -> Tuple[List[str], List[str], List[Dict]]:
    path = Path(json_path)

    if not path.exists():
        raise FileNotFoundError(f"Nu gasesc fisierul: {path.resolve()}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    documents: List[str] = []
    ids: List[str] = []
    metadata: List[Dict] = []

    seen = set()

    for entry in data:
        title = (entry.get("title") or "").strip()
        summary = (entry.get("summary") or "").strip()
        themes = entry.get("themes", [])

        if not title or not summary:
            continue
        if title in seen:
            continue
        seen.add(title)

        documents.append(summary)
        ids.append(title)
        metadata.append({"title": title, "themes": themes})

    if not documents:
        raise ValueError(f"{path.name} nu contine intrari valide (title+summary).")

    return documents, ids, metadata
