from skills.core.loader import SkillLoader
from skills.core.models import Skill


class SkillRegistry:
    def __init__(self, skills_dirs: str | list[str] = "skills"):
        self.loader = SkillLoader(skills_dirs)
        self.skills: dict[str, Skill] = {}
        self.reload()

    def reload(self) -> None:
        self.skills = {skill.name: skill for skill in self.loader.load_all()}

    def get(self, name: str) -> Skill | None:
        return self.skills.get(name)

    def list_skills(self) -> list[Skill]:
        return list(self.skills.values())

    def summaries(self) -> list[dict]:
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "allowed_tools": skill.allowed_tools,
                "disable_model_invocation": skill.disable_model_invocation,
                "path": str(skill.path),
            }
            for skill in self.skills.values()
        ]
