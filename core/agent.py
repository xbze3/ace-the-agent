import os
import json
from pathlib import Path

from core.state import AgentState
from core.harness import build_messages
from llm.client import call_llm
from runtime.logger import log_step
from llm.parser import parse_llm_response
from runtime.executor import execute_tool
from runtime.spinner import spinner
from memory.service import MemoryService
from skills.core.registry import SkillRegistry
from skills.core.router import SkillRouter

from dotenv import load_dotenv  # type: ignore

load_dotenv()

MAX_STEPS = int(os.getenv("MAX_STEPS", 30))

# Default: clean mode.
# To show detailed logs, set:
# ACE_SHOW_LOGS=true
ACE_SHOW_LOGS = os.getenv("ACE_SHOW_LOGS", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def resolve_skill_dirs() -> list[str]:
    """
    Resolve skill directories for ACE.

    Priority:
    1. ACE_SKILLS_DIR from .env
       - supports multiple paths separated by semicolon
    2. ./agents/skills relative to the current working directory
    3. ./.agents/skills relative to the current working directory
    4. ~/.agents/skills for globally installed skills
    """

    dirs: list[Path] = []

    env_dir = os.getenv("ACE_SKILLS_DIR")

    if env_dir:
        for part in env_dir.split(";"):
            part = part.strip()

            if part:
                dirs.append(Path(part).expanduser())

    dirs.extend(
        [
            Path.cwd() / "agents" / "skills",
            Path.cwd() / ".agents" / "skills",
            Path.home() / ".agents" / "skills",
        ]
    )

    resolved_dirs: list[str] = []
    seen = set()

    for path in dirs:
        resolved = path.resolve()

        if resolved in seen:
            continue

        seen.add(resolved)
        resolved_dirs.append(str(resolved))

    return resolved_dirs


class ACEAgent:
    def __init__(
        self,
        max_steps: int = MAX_STEPS,
        show_logs: bool = ACE_SHOW_LOGS,
    ):
        self.max_steps = max_steps
        self.show_logs = show_logs

        self.state = AgentState()
        self.memory = MemoryService()

        self.skill_dirs = resolve_skill_dirs()
        self.skill_registry = SkillRegistry(self.skill_dirs)
        self.skill_router = SkillRouter(self.skill_registry)

        log_step(
            "SKILL_DIRS",
            {
                "skill_dirs": self.skill_dirs,
                "loaded_skills": [
                    skill.name for skill in self.skill_registry.list_skills()
                ],
            },
        )

        if self.show_logs:
            print("\nLoaded skills:")
            for skill in self.skill_registry.list_skills():
                print(f" - {skill.name}: {skill.description}")

    def _line(self):
        print("─" * 72)

    def _section(self, title: str):
        print("\n" + "─" * 72)
        print(f" ACE :: {title}")
        print("─" * 72)

    def _status(self, label: str, value: str | None = None):
        if value:
            print(f" ◉ {label:<14} {value}")
        else:
            print(f" ◉ {label}")

    def _debug(self, label: str, value):
        """
        Prints detailed logs only when show_logs=True.
        Runtime logger still records logs either way.
        """
        if not self.show_logs:
            return

        print(f"\n ◆ {label}")
        print("─" * 72)

        if isinstance(value, (dict, list)):
            print(json.dumps(value, indent=2, ensure_ascii=False))
        else:
            print(value)

    def _is_llm_error(self, raw_response) -> bool:
        """
        Detects provider/client errors that should not be treated
        as invalid JSON from the model.

        Important:
        Do not search for generic words like "timeout" anywhere in the response.
        Generated code can contain words like setTimeout().
        """

        if not isinstance(raw_response, str):
            return False

        stripped = raw_response.strip()
        lowered = stripped.lower()

        provider_error_prefixes = (
            "error:",
            "ollama error:",
            "openai error:",
            "llm error:",
            "request error:",
            "connection error:",
        )

        if lowered.startswith(provider_error_prefixes):
            return True

        exact_provider_errors = {
            "error: ollama request timed out after retries",
            "error: openai request timed out after retries",
            "error: llm request timed out after retries",
            "error: request failed after retries",
            "ollama request timed out after retries",
            "openai request timed out after retries",
            "llm request timed out after retries",
            "request failed after retries",
        }

        return lowered in exact_provider_errors

    def _resolve_allowed_tools(self, active_skill):
        """
        Resolves tool permissions for the active skill.

        Anthropic-style skills may not include ACE-specific allowed-tools.
        For those, ACE can apply safe defaults by skill name.
        """

        if not active_skill:
            return None

        if active_skill.allowed_tools:
            return active_skill.allowed_tools

        default_skill_tools = {
            "frontend-design": [
                "create_file",
                "read_file",
                "update_file",
                "replace_in_file",
                "append_file",
                "list_files",
                "get_file_info",
                "create_directory",
                "list_directory",
                "tree",
                "download_file",
            ],
            "nodejs-express-server": [
                "create_file",
                "read_file",
                "update_file",
                "replace_in_file",
                "append_file",
                "list_files",
                "get_file_info",
                "create_directory",
                "list_directory",
                "tree",
                "run_node_file",
                "run_npm_install",
                "run_npm_script",
                "install_npm_package",
                "start_background_command",
                "list_background_processes",
                "stop_background_process",
                "http_get",
                "http_post",
                "http_put",
                "http_delete",
            ],
            "python-script-builder": [
                "create_file",
                "read_file",
                "update_file",
                "replace_in_file",
                "append_file",
                "list_files",
                "get_file_info",
                "create_directory",
                "list_directory",
                "tree",
                "run_python_file",
                "install_python_package",
            ],
            "code-review-debugger": [
                "create_file",
                "read_file",
                "update_file",
                "replace_in_file",
                "append_file",
                "list_files",
                "get_file_info",
                "create_directory",
                "list_directory",
                "tree",
                "run_python_file",
                "run_node_file",
                "run_npm_install",
                "run_npm_script",
                "install_python_package",
                "install_npm_package",
            ],
            "api-client-tester": [
                "create_file",
                "read_file",
                "update_file",
                "replace_in_file",
                "append_file",
                "list_files",
                "get_file_info",
                "create_directory",
                "list_directory",
                "tree",
                "http_get",
                "http_post",
                "http_put",
                "http_delete",
                "start_background_command",
                "list_background_processes",
                "stop_background_process",
            ],
            "project-scaffolder": [
                "create_file",
                "read_file",
                "update_file",
                "replace_in_file",
                "append_file",
                "list_files",
                "get_file_info",
                "create_directory",
                "list_directory",
                "tree",
            ],
            "web-researcher": [
                "create_file",
                "read_file",
                "update_file",
                "append_file",
                "list_files",
                "get_file_info",
                "create_directory",
                "list_directory",
                "tree",
                "web_search",
                "http_get",
                "download_file",
            ],
            "file-manager": [
                "create_file",
                "read_file",
                "update_file",
                "delete_file",
                "append_file",
                "replace_in_file",
                "list_files",
                "get_file_info",
                "create_directory",
                "list_directory",
                "delete_directory",
                "delete_directory_recursive",
                "tree",
                "download_file",
            ],
        }

        return default_skill_tools.get(active_skill.name)

    def run(self, user_input: str):
        self._section("START")

        self._debug("Skill Directories", self.skill_dirs)
        self._debug(
            "Loaded Skills",
            [skill.name for skill in self.skill_registry.list_skills()],
        )

        with spinner("Selecting skill"):
            active_skill, routed_input = self.skill_router.route(user_input)

        allowed_tools = self._resolve_allowed_tools(active_skill)

        self.state.add_user_message(routed_input)

        if active_skill:
            self._status("Skill", active_skill.name)
            log_step(
                "ACTIVE_SKILL",
                {
                    "name": active_skill.name,
                    "path": str(active_skill.path),
                    "allowed_tools": allowed_tools,
                },
            )
        else:
            self._status("Skill", "none")
            log_step("ACTIVE_SKILL", None)

        self._debug("Routed Input", routed_input)
        self._debug("Resolved Allowed Tools", allowed_tools)

        with spinner("Checking memory"):
            memories = self.memory.search(routed_input)

        self._debug("Relevant Memories", memories)

        for step in range(self.max_steps):
            self._section(f"STEP {step + 1}/{self.max_steps}")

            try:
                with spinner("Preparing context"):
                    messages = build_messages(
                        self.state,
                        memories=memories,
                        active_skill=active_skill,
                        allowed_tools=allowed_tools,
                    )

                self._debug("LLM Messages", messages)

                with spinner("Thinking"):
                    raw_response = call_llm(messages)

                log_step("LLM_RAW_RESPONSE", raw_response)
                self._debug("LLM Raw Response", raw_response)

                with spinner("Parsing response"):
                    parsed = parse_llm_response(raw_response)

                log_step("LLM_PARSED_RESPONSE", parsed)
                self._debug("LLM Parsed Response", parsed)

                if not parsed and self._is_llm_error(raw_response):
                    self._status("LLM", "request failed")
                    log_step("AGENT_ERROR", raw_response)
                    return raw_response

                if not parsed:
                    error_msg = "Failed to parse LLM response"
                    self._status("Parse", "failed")
                    log_step("AGENT_ERROR", error_msg)

                    repair_messages = messages + [
                        {
                            "role": "system",
                            "content": (
                                "Your previous response was invalid JSON. "
                                "Return ONLY valid JSON in the required format. "
                                "Do not include any extra text."
                            ),
                        }
                    ]

                    self._debug("Repair Messages", repair_messages)

                    with spinner("Repairing response"):
                        raw_response = call_llm(repair_messages)

                    log_step("LLM_RETRY_RESPONSE", raw_response)
                    self._debug("LLM Retry Response", raw_response)

                    with spinner("Parsing repaired response"):
                        parsed = parse_llm_response(raw_response)

                    log_step("LLM_RETRY_PARSED", parsed)
                    self._debug("LLM Retry Parsed", parsed)

                    if not parsed and self._is_llm_error(raw_response):
                        self._status("LLM", "repair request failed")
                        log_step("AGENT_ERROR", raw_response)
                        return raw_response

                    if not parsed:
                        log_step("AGENT_ERROR", "Failed to parse after retry")
                        return raw_response

                self.state.add_assistant_message(raw_response)

                if "final_answer" in parsed:
                    final = parsed["final_answer"]

                    self._status("Result", "final answer ready")

                    with spinner("Saving memory"):
                        self.memory.process_interaction(
                            user_input=routed_input,
                            assistant_response=final,
                            history=self.state.get_messages(),
                        )

                    self._section("DONE")
                    return final

                action = parsed.get("action")
                arguments = parsed.get("arguments", {})

                if not action:
                    error_msg = (
                        "Parsed response did not include an action or final_answer"
                    )
                    self._status("Error", "missing action")
                    log_step("AGENT_ERROR", error_msg)
                    return error_msg

                self._status("Action", action)
                self._debug("Action Arguments", arguments)

                with spinner(f"Running {action}"):
                    result = execute_tool(
                        action,
                        arguments,
                        allowed_tools=allowed_tools,
                    )

                log_step("TOOL_RESULT", result)
                self._debug("Tool Result", result)

                if self.show_logs:
                    print("\n ◉ Tool Result")
                    self._line()
                    print(result)
                else:
                    self._status("Tool", "completed")

                self.state.add_tool_result(result)

            except KeyboardInterrupt:
                print("\n\n[INTERRUPTED] ACE stopped by user.")
                log_step("AGENT_INTERRUPTED", "Stopped by Ctrl+C")
                raise

            except Exception as e:
                error_msg = f"Agent loop failed: {str(e)}"
                print(f"\n[EXCEPTION] {error_msg}")
                log_step("AGENT_EXCEPTION", error_msg)
                return error_msg

        max_step_msg = "Reached max steps without completion"

        print("\n" + "═" * 72)
        print(" ACE :: STOP")
        print("═" * 72)
        print(max_step_msg)
        print("═" * 72)

        log_step("AGENT_STOP", max_step_msg)
        return max_step_msg
