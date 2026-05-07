from pathlib import Path
from typing import Any

import yaml

from skills.core.models import Skill


class SkillLoader:
    def __init__(self, skills_dirs: str | list[str] = "skills"):
        if isinstance(skills_dirs, str):
            skills_dirs = [skills_dirs]

        self.skills_dirs = [Path(path).expanduser() for path in skills_dirs]

    def load_all(self) -> list[Skill]:
        skills: list[Skill] = []
        seen_paths = set()
        seen_names = set()

        skill_patterns = [
            "*/SKILL.md",
            ".agents/skills/*/SKILL.md",
        ]

        for skills_dir in self.skills_dirs:
            if not skills_dir.exists():
                continue

            for pattern in skill_patterns:
                for skill_file in skills_dir.glob(pattern):
                    if "core" in skill_file.parts:
                        continue

                    resolved_path = skill_file.resolve()

                    if resolved_path in seen_paths:
                        continue

                    skill = self.load_skill(skill_file)

                    if skill.name in seen_names:
                        continue

                    seen_paths.add(resolved_path)
                    seen_names.add(skill.name)
                    skills.append(skill)

        return skills

    def load_skill(self, skill_file: Path) -> Skill:
        raw = skill_file.read_text(encoding="utf-8")
        metadata, body = self._parse_frontmatter(raw)

        name = metadata.get("name") or skill_file.parent.name
        description = metadata.get("description", "").strip()

        if not description:
            raise ValueError(f"{skill_file} is missing a description in frontmatter")

        allowed_tools = metadata.get("allowed-tools", [])

        if isinstance(allowed_tools, str):
            allowed_tools = [allowed_tools]

        return Skill(
            name=name,
            description=description,
            body=body.strip(),
            path=skill_file.parent,
            allowed_tools=allowed_tools,
            disable_model_invocation=metadata.get("disable-model-invocation", False),
            metadata=metadata,
        )

    def _parse_frontmatter(self, raw: str) -> tuple[dict[str, Any], str]:
        if not raw.startswith("---"):
            return {}, raw

        parts = raw.split("---", 2)

        if len(parts) < 3:
            return {}, raw

        _, frontmatter, body = parts

        metadata = yaml.safe_load(frontmatter) or {}

        return metadata, body
