import os
from typing import Any, Dict, List

from dotenv import load_dotenv

from memory.embedder import Embedder
from memory.extractor import MemoryExtractor
from memory.schema import Memory
from memory.store import VectorStore
from runtime.logger import log_step

load_dotenv()


class MemoryService:
    def __init__(self):
        self.embedder = Embedder()
        self.store = VectorStore()
        self.extractor = MemoryExtractor()

        self.top_k = int(os.getenv("MEMORY_TOP_K", 5))
        self.similarity_threshold = float(
            os.getenv("MEMORY_SIMILARITY_THRESHOLD", 0.15)
        )
        self.min_confidence = float(os.getenv("MEMORY_MIN_CONFIDENCE", 0.7))

    def search(self, query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        try:
            query_embedding = self.embedder.embed(query)
            memories = self.store.search(
                query_embedding,
                top_k=top_k or self.top_k,
            )

            log_step("MEMORY_RETRIEVED", memories)
            return memories

        except Exception as e:
            log_step("MEMORY_SEARCH_ERROR", str(e))
            return []

    def process_interaction(
        self,
        user_input: str,
        assistant_response: str,
        history: List[Dict[str, Any]] | None = None,
    ) -> None:
        try:
            candidates = self.extractor.extract(
                user_input=user_input,
                assistant_response=assistant_response,
                history=history or [],
            )

            log_step("MEMORY_CANDIDATES", candidates)

            for candidate in candidates:
                if self._should_store(candidate):
                    self._store_candidate(candidate)

        except Exception as e:
            log_step("MEMORY_PROCESS_ERROR", str(e))

    def _store_candidate(self, candidate: Dict[str, Any]) -> None:
        memory = Memory.create(
            content=candidate["content"],
            type=candidate.get("type", "fact"),
            confidence=float(candidate.get("confidence", 0.8)),
            metadata={
                "source": "conversation",
            },
        )

        embedding = self.embedder.embed(memory.content)

        if self.store.exists_similar(
            embedding,
            threshold=self.similarity_threshold,
        ):
            log_step("MEMORY_SKIPPED_DUPLICATE", memory.to_dict())
            return

        self.store.insert(memory.to_dict(), embedding)
        log_step("MEMORY_STORED", memory.to_dict())

    def _should_store(self, candidate: Dict[str, Any]) -> bool:
        content = str(candidate.get("content", "")).strip()

        try:
            confidence = float(candidate.get("confidence", 0))
        except (TypeError, ValueError):
            confidence = 0

        if not content:
            return False

        if len(content) < 15:
            return False

        if confidence < self.min_confidence:
            return False

        return True
