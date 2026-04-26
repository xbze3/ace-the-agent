import os
import requests
from dotenv import load_dotenv

load_dotenv()


class Embedder:
    def __init__(self):
        self.provider = os.getenv("EMBEDDING_PROVIDER", "ollama").lower()
        self.model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.base_url = os.getenv("EMBEDDING_BASE_URL", "http://localhost:11434")
        self.api_key = os.getenv("EMBEDDING_API_KEY", "")
        self.timeout = int(os.getenv("EMBEDDING_TIMEOUT", 60))

    def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        if self.provider == "ollama":
            return self._embed_with_ollama(text)

        raise ValueError(f"Unsupported embedding provider: {self.provider}")

    def _embed_with_ollama(self, text: str) -> list[float]:
        url = f"{self.base_url.rstrip('/')}/api/embeddings"

        headers = {}
        if self.api_key and self.api_key != "your_embedding_api_key":
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "prompt": text,
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )

        response.raise_for_status()
        data = response.json()

        embedding = data.get("embedding")

        if not embedding:
            raise RuntimeError("Embedding response did not contain an embedding")

        return embedding
