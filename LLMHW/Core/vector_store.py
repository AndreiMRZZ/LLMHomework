# Core/vector_store.py
from api.conf import settings

# Embeddings (noua cale recomandată)
try:
    from langchain_openai import OpenAIEmbeddings
except Exception:
    from langchain.embeddings.openai import OpenAIEmbeddings  # fallback

# VectorStore Chroma – pachet nou
from langchain_chroma import Chroma

from Core.loader import load_book_summaries
from pathlib import Path
import os

OPENAI_API_KEY = settings.OPENAI_API_KEY
EMBEDDING_MODEL = settings.OPENAI_EMBEDDING_MODEL
CHROMA_DB_DIR = settings.CHROMA_DB_DIR

# -------- Embeddings --------
embedding_function = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    openai_api_key=OPENAI_API_KEY,
)

# -------- Încarcă rezumatele --------
SUMMARIES_PATH = "summaries.json"
if not Path(SUMMARIES_PATH).exists():
    raise FileNotFoundError(f"Nu gasesc {SUMMARIES_PATH} (pune-l în radacina proiectului).")

documents, ids, metadata = load_book_summaries(SUMMARIES_PATH)

metadata_clean = []
for m in metadata:
    m2 = dict(m)
    if isinstance(m2.get("themes"), list):
        m2["themes"] = ", ".join(map(str, m2["themes"]))
    metadata_clean.append(m2)

vector_store = Chroma(
    collection_name="book_summaries",
    embedding_function=embedding_function,
    persist_directory=CHROMA_DB_DIR,  # folder pe disc
)

try:
    current = vector_store.get()
    existing_ids = set(current.get("ids", []))
except Exception:
    existing_ids = set()

if not existing_ids:
    vector_store.add_texts(
        texts=documents,
        metadatas=metadata_clean,
        ids=ids,
    )
    print("Vector store populat")
else:
    print("Vector store deja populat")

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},
)

def get_retriever():
    return retriever
