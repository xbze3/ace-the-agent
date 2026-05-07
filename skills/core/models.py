from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Skill:
    name: str
    description: str
    body: str
    path: Path
    allowed_tools: list[str] = field(default_factory=list)
    disable_model_invocation: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def prompt_block(self) -> str:
        allowed = (
            ", ".join(self.allowed_tools)
            if self.allowed_tools
            else "No specific tool restriction"
        )

        return f"""
Active skill: {self.name}

Description:
{self.description}

Instructions:
{self.body}

Allowed tools for this skill:
{allowed}

Skill rule:
When this skill is active, follow its workflow carefully. Do not use tools outside its allowed tool list.
""".strip()
