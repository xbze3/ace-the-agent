import json
from llm.client import call_llm
from llm.parser import parse_llm_response
from runtime.logger import log_step
from skills.core.models import Skill
from skills.core.registry import SkillRegistry


class SkillRouter:
    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    def route(self, user_input: str) -> tuple[Skill | None, str]:
        """
        Returns:
            active_skill, cleaned_user_input
        """

        manual_skill, cleaned_input = self._manual_invocation(user_input)

        if manual_skill:
            log_step(
                "SKILL_ROUTER_SELECTED",
                {
                    "mode": "manual",
                    "skill": manual_skill.name,
                    "confidence": 1.0,
                },
            )
            return manual_skill, cleaned_input

        selected_skill = self._llm_route(user_input)

        if selected_skill:
            return selected_skill, user_input

        return None, user_input

    def _manual_invocation(self, user_input: str) -> tuple[Skill | None, str]:
        if not user_input.startswith("/"):
            return None, user_input

        first, *rest = user_input.split(maxsplit=1)
        command = first.removeprefix("/")

        if command == "skill" and rest:
            parts = rest[0].split(maxsplit=1)
            requested_skill = parts[0]
            cleaned_input = parts[1] if len(parts) > 1 else ""

            return self.registry.get(requested_skill), cleaned_input

        cleaned_input = rest[0] if rest else ""

        return self.registry.get(command), cleaned_input

    def _llm_route(self, user_input: str) -> Skill | None:
        skill_summaries = self._available_skill_summaries()

        if not skill_summaries:
            return None

        valid_skill_names = [skill["name"] for skill in skill_summaries]

        messages = [
            {
                "role": "system",
                "content": (
                    "You are ACE's skill router. "
                    "Your job is to choose the best skill for the user's request. "
                    "Only choose a skill if it clearly helps. "
                    "If no skill is appropriate, return null. "
                    "You must return ONLY valid JSON. "
                    "Do not return markdown. "
                    "Do not use code fences. "
                    "Do not explain outside the JSON."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "user_input": user_input,
                        "available_skills": skill_summaries,
                        "valid_skill_names": valid_skill_names,
                        "required_output_format": {
                            "skill": "Use one exact skill name from valid_skill_names, or null",
                            "confidence": "A number from 0 to 1",
                            "reason": "A short reason",
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ]

        try:
            raw_response = call_llm(messages)
            log_step("SKILL_ROUTER_RAW_RESPONSE", raw_response)

            parsed = self._parse_router_response(raw_response)

            if not parsed:
                log_step("SKILL_ROUTER_ERROR", "Could not parse router response")
                return None

            log_step("SKILL_ROUTER_PARSED_RESPONSE", parsed)

            skill_name = parsed.get("skill")
            confidence = float(parsed.get("confidence", 0))

            if not skill_name or str(skill_name).lower() == "null":
                log_step(
                    "SKILL_ROUTER_SELECTED",
                    {
                        "mode": "llm",
                        "skill": None,
                        "confidence": confidence,
                        "reason": parsed.get("reason"),
                    },
                )
                return None

            if confidence < 0.65:
                log_step(
                    "SKILL_ROUTER_SELECTED",
                    {
                        "mode": "llm",
                        "skill": None,
                        "rejected_skill": skill_name,
                        "confidence": confidence,
                        "reason": "Below confidence threshold",
                    },
                )
                return None

            skill = self.registry.get(skill_name)

            if not skill:
                log_step(
                    "SKILL_ROUTER_ERROR",
                    {
                        "message": "LLM selected unknown skill",
                        "skill": skill_name,
                        "valid_skill_names": valid_skill_names,
                    },
                )
                return None

            log_step(
                "SKILL_ROUTER_SELECTED",
                {
                    "mode": "llm",
                    "skill": skill.name,
                    "confidence": confidence,
                    "reason": parsed.get("reason"),
                },
            )

            return skill

        except Exception as e:
            log_step("SKILL_ROUTER_ERROR", str(e))
            return None

    def _parse_router_response(self, raw_response: str) -> dict | None:
        try:
            parsed = parse_llm_response(raw_response)

            if isinstance(parsed, dict):
                if "final_answer" in parsed:
                    value = parsed["final_answer"]

                    if isinstance(value, dict):
                        return value

                    if isinstance(value, str):
                        return json.loads(value)

                return parsed

        except Exception:
            pass

        try:
            cleaned = raw_response.strip()

            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`").strip()

                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()

            return json.loads(cleaned)

        except Exception:
            return None

    def _available_skill_summaries(self) -> list[dict]:
        summaries = []

        for skill in self.registry.list_skills():
            if getattr(skill, "disable_model_invocation", False):
                continue

            summaries.append(
                {
                    "name": skill.name,
                    "description": skill.description,
                    "tags": skill.metadata.get("tags", []),
                    "routing": skill.metadata.get("routing", {}),
                }
            )

        return summaries
