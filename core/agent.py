from core.state import AgentState
from core.harness import build_messages
from llm.client import call_llm
from runtime.logger import log_step
from llm.parser import parse_llm_response
from runtime.executor import execute_tool


class ACEAgent:
    def __init__(self, max_steps: int = 30):
        self.max_steps = max_steps
        self.state = AgentState()

    def run(self, user_input: str):
        self.state.add_user_message(user_input)

        for step in range(self.max_steps):
            print("\n" + "─" * 70)
            print(f" ACE AGENT  |  Step {step + 1}/{self.max_steps}")
            print("─" * 70)

            try:
                messages = build_messages(self.state)
                raw_response = call_llm(messages)
                log_step("LLM_RAW_RESPONSE", raw_response)

                parsed = parse_llm_response(raw_response)
                log_step("LLM_PARSED_RESPONSE", parsed)

                if not parsed:
                    error_msg = "Failed to parse LLM response"
                    print(f"\n[ERROR] {error_msg}")
                    log_step("AGENT_ERROR", error_msg)
                    return error_msg

                self.state.add_assistant_message(raw_response)

                if "final_answer" in parsed:
                    final = parsed["final_answer"]
                    # print("\n" + "═" * 70)
                    # print(" FINAL ANSWER")
                    # print("═" * 70)
                    # print(final)
                    # print("═" * 70)
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

                print(f"\n[ACTION] {action}")
                print(f"[ARGS]   {arguments}")

                result = execute_tool(action, arguments)
                log_step("TOOL_RESULT", result)

                print("\n[RESULT]")
                print(result)

                self.state.add_tool_result(result)

            except Exception as e:
                error_msg = f"Agent loop failed: {str(e)}"
                print(f"\n[EXCEPTION] {error_msg}")
                log_step("AGENT_EXCEPTION", error_msg)
                return error_msg

        max_step_msg = "Reached max steps without completion"
        print("\n" + "═" * 70)
        print(f"[STOP] {max_step_msg}")
        print("═" * 70)
        log_step("AGENT_STOP", max_step_msg)
        return max_step_msg
