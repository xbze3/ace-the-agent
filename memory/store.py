import os
from typing import Any, Dict, List
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class VectorStore:
    def __init__(self):
        self.provider = os.getenv("MEMORY_STORE_PROVIDER", "chroma").lower()

        if self.provider != "chroma":
            raise ValueError(f"Unsupported memory store provider: {self.provider}")

        try:
            import chromadb
        except ImportError as exc:
            raise ImportError(
                "chromadb is required for memory storage. Install it with: pip install chromadb"
            ) from exc

        self.collection_name = os.getenv("MEMORY_COLLECTION", "ace_memories")

        base_dir = Path(__file__).resolve().parent

        db_dir_name = os.getenv("MEMORY_DB_DIR", "memory_db")

        self.persist_dir = base_dir / db_dir_name

        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.persist_dir))

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={
                "description": "ACE long-term memory collection",
                "hnsw:space": "cosine",
            },
        )

    def insert(self, memory: Dict[str, Any], embedding: list[float]) -> None:
        metadata = {
            "type": memory.get("type", "fact"),
            "confidence": float(memory.get("confidence", 0.8)),
            "created_at": memory.get("created_at", ""),
        }

        extra_metadata = memory.get("metadata") or {}

        for key, value in extra_metadata.items():
            if isinstance(value, (str, int, float, bool)):
                metadata[key] = value

        self.collection.add(
            ids=[memory["id"]],
            documents=[memory["content"]],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    def search(self, embedding: list[float], top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
        )

        memories = []

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i, memory_id in enumerate(ids):
            memories.append(
                {
                    "id": memory_id,
                    "content": documents[i],
                    "metadata": metadatas[i],
                    "distance": distances[i] if i < len(distances) else None,
                }
            )

        return memories

    def exists_similar(self, embedding: list[float], threshold: float = 0.15) -> bool:
        results = self.search(embedding, top_k=1)

        if not results:
            return False

        distance = results[0].get("distance")

        if distance is None:
            return False

        return distance <= threshold
