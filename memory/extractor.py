import json
from typing import Any, Dict, List

from llm.client import call_llm


MEMORY_EXTRACTION_PROMPT = """
You extract useful long-term memories for ACE, an AI agent.

Only extract information that is likely to be useful in future conversations.

Store:
- user preferences
- stable project facts
- important technical decisions
- repeated constraints
- long-term goals
- lessons from debugging

Do NOT store:
- greetings
- temporary requests
- generic explanations
- one-time details
- information about the assistant
- anything uncertain or guessed

Return raw JSON only.

Format:
{
  "memories": [
    {
      "type": "preference | project | fact | constraint | lesson",
      "content": "short standalone memory",
      "confidence": 0.0
    }
  ]
}

If nothing should be remembered, return:
{
  "memories": []
}
"""


class MemoryExtractor:
    def extract(
        self,
        user_input: str,
        assistant_response: str,
        history: List[Dict[str, Any]] | None = None,
    ) -> List[Dict[str, Any]]:
        messages = [
            {
                "role": "system",
                "content": MEMORY_EXTRACTION_PROMPT,
            },
            {
                "role": "user",
                "content": self._build_extraction_input(
                    user_input=user_input,
                    assistant_response=assistant_response,
                    history=history or [],
                ),
            },
        ]

        raw = call_llm(messages)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []

        memories = data.get("memories", [])

        if not isinstance(memories, list):
            return []

        clean_memories = []

        for memory in memories:
            if not isinstance(memory, dict):
                continue

            content = str(memory.get("content", "")).strip()
            memory_type = str(memory.get("type", "fact")).strip()
            confidence = memory.get("confidence", 0)

            try:
                confidence = float(confidence)
            except (TypeError, ValueError):
                confidence = 0

            if content:
                clean_memories.append(
                    {
                        "type": memory_type,
                        "content": content,
                        "confidence": confidence,
                    }
                )

        return clean_memories

    def _build_extraction_input(
        self,
        user_input: str,
        assistant_response: str,
        history: List[Dict[str, Any]],
    ) -> str:
        recent_history = history[-8:] if history else []

        return f"""
User input:
{user_input}

Assistant response:
{assistant_response}

Recent conversation history:
{json.dumps(recent_history, indent=2)}

Extract useful long-term memories from this interaction.
"""
