"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRESTLINE TECHNOLOGIES — DOCUMENT INGESTION
Role: ML Engineer
Block: 2 — RAG Core
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ingests 9 .txt files into Qdrant
Creates 3 collections: hr_docs, marketing_docs, product_docs
Run: python scripts/ingest_docs.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# ── Config ─────────────────────────────────────────────────────────
QDRANT_PATH  = "./qdrant_storage"
DOCS_BASE    = "./docs"
MODEL_NAME   = "all-MiniLM-L6-v2"
VECTOR_SIZE  = 384
CHUNK_MIN    = 40
CHUNK_MAX    = 1200

COLLECTIONS = {
    "hr_docs":        f"{DOCS_BASE}/hr",
    "marketing_docs": f"{DOCS_BASE}/marketing",
    "product_docs":   f"{DOCS_BASE}/product",
}


# ── Chunking ───────────────────────────────────────────────────────

def chunk_text(file_path: str) -> list[dict]:
    """Split a .txt file into paragraph-level chunks."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    paragraphs = content.split("\n\n")
    chunks = []
    for para in paragraphs:
        text = para.strip()
        if CHUNK_MIN <= len(text) <= CHUNK_MAX:
            chunks.append({
                "text":   text,
                "source": Path(file_path).name,
            })
    return chunks


# ── Qdrant helpers ─────────────────────────────────────────────────

def reset_collection(client: QdrantClient, name: str) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if name in existing:
        client.delete_collection(name)
        print(f"   🗑️  Deleted old: {name}")
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"   ✅ Created: {name}")


def ingest_folder(
    client: QdrantClient,
    model: SentenceTransformer,
    collection: str,
    folder: str,
) -> int:
    """Embed and upsert all .txt chunks from a folder."""
    all_chunks = []

    for fname in sorted(os.listdir(folder)):
        if not fname.endswith(".txt"):
            continue
        path   = os.path.join(folder, fname)
        chunks = chunk_text(path)
        all_chunks.extend(chunks)
        print(f"      📄 {fname}: {len(chunks)} chunks")

    if not all_chunks:
        print(f"   ⚠️  No chunks in {folder}")
        return 0

    texts      = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=False)

    points = [
        PointStruct(
            id=idx,
            vector=emb.tolist(),
            payload={"text": chunk["text"], "source": chunk["source"]},
        )
        for idx, (chunk, emb) in enumerate(zip(all_chunks, embeddings))
    ]

    client.upsert(collection_name=collection, points=points)
    return len(points)


# ── Verify ─────────────────────────────────────────────────────────

def verify(client: QdrantClient) -> None:
    print("\n📊 Qdrant Collections:")
    for col in client.get_collections().collections:
        info = client.get_collection(col.name)
        print(f"   {col.name:<22} → {info.points_count} points")


# ── Main ───────────────────────────────────────────────────────────

def main() -> None:
    print("🚀 Crestline ML Engineer — Ingesting Documents into Qdrant")
    print("=" * 60)

    # Load model
    print("\n📦 Loading embedding model (first run downloads ~90MB)...")
    model = SentenceTransformer(MODEL_NAME)
    print(f"✅ Model ready: {MODEL_NAME} | Dimensions: {VECTOR_SIZE}")

    # Connect Qdrant
    os.makedirs(QDRANT_PATH, exist_ok=True)
    client = QdrantClient(path=QDRANT_PATH)
    print(f"✅ Qdrant connected → {QDRANT_PATH}")

    # Ingest each collection
    print("\n📥 Ingesting documents...")
    for collection, folder in COLLECTIONS.items():
        print(f"\n   [{collection}]")
        reset_collection(client, collection)
        count = ingest_folder(client, model, collection, folder)
        print(f"   ✅ {count} chunks ingested")

    verify(client)
    print("\n" + "=" * 60)
    print("✅ Ingestion complete → qdrant_storage/")


if __name__ == "__main__":
    main()

