"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRESTLINE TECHNOLOGIES — PRODUCT TOOL
Role: Backend Engineer
Block: 2 — RAG Core
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Handles: OS changelog, Cloud API docs, system requirements
Source: Qdrant collection → product_docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import re
from pathlib import Path

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

QDRANT_PATH = "./qdrant_storage"
COLLECTION = "product_docs"
MODEL_NAME = "all-MiniLM-L6-v2"
DOC_DIR = "docs/product"


class ProductTool:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.client = None
        try:
            self.client = QdrantClient(path=QDRANT_PATH)
        except Exception:
            self.client = None
        self.docs = self._load_docs()

    def _load_docs(self) -> list[dict[str, str]]:
        root = Path(__file__).resolve().parents[2]
        doc_path = root / DOC_DIR
        docs = []
        for file_path in sorted(doc_path.glob("*.txt")):
            docs.append({
                "text": file_path.read_text(encoding="utf-8"),
                "source": file_path.name,
            })
        return docs

    def _fallback_search(self, query: str, top_k: int = 3) -> list[dict]:
        if not self.docs:
            return []
        query_terms = set(re.findall(r"\w+", query.lower()))
        scored_results = []
        for doc in self.docs:
            text_terms = set(re.findall(r"\w+", doc["text"].lower()))
            score = len(query_terms & text_terms)
            scored_results.append((score, doc))
        scored_results.sort(key=lambda item: item[0], reverse=True)
        results = [doc for score, doc in scored_results if score > 0][:top_k]
        if not results:
            results = [doc for _, doc in scored_results[:top_k]]
        return [
            {
                "text": doc["text"],
                "source": doc["source"],
                "score": 0.0,
            }
            for doc in results
        ]

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if self.client is not None:
            try:
                embedding = self.model.encode(query).tolist()
                results = self.client.search(
                    collection_name=COLLECTION,
                    query_vector=embedding,
                    limit=top_k,
                )
                return [
                    {
                        "text": r.payload["text"],
                        "source": r.payload["source"],
                        "score": round(r.score, 4),
                    }
                    for r in results
                ]
            except Exception:
                pass
        return self._fallback_search(query, top_k)

    def run(self, query: str) -> str:
        results = self.search(query)
        if not results:
            return "No relevant product documentation found."
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(
                f"[{i}] Source: {r['source']} (relevance: {r['score']})\n{r['text']}"
            )
        return "\n\n".join(parts)
