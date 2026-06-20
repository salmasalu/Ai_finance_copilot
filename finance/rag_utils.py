import os
import chromadb
from pathlib import Path

CHROMA_PATH = Path(__file__).resolve().parent.parent / "datasets" / "chroma_db"

chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))

collection = chroma_client.get_or_create_collection(
    name="financial_tips2"
)


def load_knowledge_base():
    if collection.count() > 0:
        return

    tips_path = Path(__file__).resolve().parent.parent / "datasets" / "financial_tips.txt"

    if not tips_path.exists():
        return

    with open(tips_path, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if not lines:
        return

    collection.add(
        documents=lines,
        ids=[f"tip_{i}" for i in range(len(lines))]
    )
    print(f"Loaded {len(lines)} financial tips into ChromaDB")


def retrieve_financial_tips(query: str, top_k: int = 3) -> list:
    load_knowledge_base()

    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count())
    )

    return results["documents"][0] if results["documents"] else []