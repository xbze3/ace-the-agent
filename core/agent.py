import os
from core.state import AgentState
from core.harness import build_messages
from llm.client import call_llm
from runtime.logger import log_step
from llm.parser import parse_llm_response
from runtime.executor import execute_tool
from memory.service import MemoryService

from dotenv import load_dotenv  # type: ignore

load_dotenv()

MAX_STEPS = int(os.getenv("MAX_STEPS", 30))


class ACEAgent:
    def __init__(self, max_steps: int = MAX_STEPS):
        self.max_steps = max_steps
        self.state = AgentState()
        self.memory = MemoryService()

    def run(self, user_input: str):
        self.state.add_user_message(user_input)

        memories = self.memory.search(user_input)

        for step in range(self.max_steps):
            print("\n" + "─" * 72)
            print(f" ACE :: Step {step + 1}/{self.max_steps}")
            print("─" * 72)

            try:
                messages = build_messages(self.state, memories=memories)
                raw_response = call_llm(messages)
                log_step("LLM_RAW_RESPONSE", raw_response)

                parsed = parse_llm_response(raw_response)
                log_step("LLM_PARSED_RESPONSE", parsed)

                if not parsed:
                    error_msg = "Failed to parse LLM response"
                    print(f"\n[ERROR] {error_msg}")
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

                    raw_response = call_llm(repair_messages)
                    log_step("LLM_RETRY_RESPONSE", raw_response)

                    parsed = parse_llm_response(raw_response)
                    log_step("LLM_RETRY_PARSED", parsed)

                    if not parsed:
                        log_step("AGENT_ERROR", "Failed to parse after retry")
                        return raw_response

                self.state.add_assistant_message(raw_response)

                if "final_answer" in parsed:
                    final = parsed["final_answer"]

                    self.memory.process_interaction(
                        user_input=user_input,
                        assistant_response=final,
                        history=self.state.get_messages(),
                    )

                    return final

                action = parsed.get("action")
                arguments = parsed.get("arguments", {})

                if not action:
                    error_msg = (
                        "Parsed response did not include an action or final_answer"
                    )
                    print(f"\n[ERROR] {error_msg}")
                    log_step("AGENT_ERROR", error_msg)
                    return error_msg

                print(f"\n ◉ Action :: {action}")
                print(f" ◌ Args   :: {arguments}")

                result = execute_tool(action, arguments)
                log_step("TOOL_RESULT", result)

                print("\n ◉ Tool Result")
                print("─" * 72)
                print(result)

                self.state.add_tool_result(result)

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
