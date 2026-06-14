"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRESTLINE TECHNOLOGIES — MARKETING TOOL
Role: Backend Engineer
Block: 2 — RAG Core
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Handles: campaign strategy, launch plans, channels
Source: Qdrant collection → marketing_docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

QDRANT_PATH = "./qdrant_storage"
COLLECTION  = "marketing_docs"
MODEL_NAME  = "all-MiniLM-L6-v2"


class MarketingTool:
    def __init__(self):
        self.model  = SentenceTransformer(MODEL_NAME)
        self.client = QdrantClient(path=QDRANT_PATH)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        embedding = self.model.encode(query).tolist()
        results   = self.client.search(
            collection_name=COLLECTION,
            query_vector=embedding,
            limit=top_k,
        )
        return [
            {
                "text":   r.payload["text"],
                "source": r.payload["source"],
                "score":  round(r.score, 4),
            }
            for r in results
        ]

    def run(self, query: str) -> str:
        results = self.search(query)
        if not results:
            return "No relevant marketing information found."
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(
                f"[{i}] Source: {r['source']} (relevance: {r['score']})\n{r['text']}"
            )
        return "\n\n".join(parts)
