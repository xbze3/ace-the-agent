from dataclasses import dataclass, asdict
from typing import Any, Dict
from datetime import datetime, timezone
import uuid


@dataclass
class Memory:
    id: str
    content: str
    type: str
    confidence: float
    created_at: str
    metadata: Dict[str, Any]

    @staticmethod
    def create(
        content: str,
        type: str = "fact",
        confidence: float = 0.8,
        metadata: Dict[str, Any] | None = None,
    ) -> "Memory":
        return Memory(
            id=str(uuid.uuid4()),
            content=content.strip(),
            type=type,
            confidence=confidence,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
