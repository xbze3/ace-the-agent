from core.agent import ACEAgent
from runtime.logger import set_console_logging, get_console_logging

APP_NAME = "ACE"
APP_FULL_NAME = "Autonomous Cognitive Engine"


def line(char="-", width=72):
    return char * width


def print_banner(show_logs: bool = False):
    print("\n" + line("═"))
    print("  █████╗  ██████╗███████╗")
    print(" ██╔══██╗██╔════╝██╔════╝")
    print(" ███████║██║     █████╗  ")
    print(" ██╔══██║██║     ██╔══╝  ")
    print(" ██║  ██║╚██████╗███████╗")
    print(" ╚═╝  ╚═╝ ╚═════╝╚══════╝")
    print(line("═"))
    print(f" {APP_NAME} :: {APP_FULL_NAME}")
    print(" Mode    :: Interactive Agent Console")
    print(" Runtime :: Tool-augmented reasoning")
    print(" Memory  :: Long-term vector recall enabled")
    print(f" Display :: {'Detailed logs' if show_logs else 'Clean status mode'}")
    print(line("-"))
    print(" Commands:")
    print("   /help       Show commands")
    print("   /logs       Show log display mode")
    print("   /logs on    Show detailed runtime logs")
    print("   /logs off   Show clean spinner/status view")
    print("   /clear      Clear terminal")
    print("   /exit       End session")
    print(line("═") + "\n")


def print_help():
    print("\n" + line("-"))
    print(" ACE COMMANDS")
    print(line("-"))
    print(" /help       Show this help menu")
    print(" /logs       Show current log display mode")
    print(
        " /logs on    Show detailed logs, raw responses, parsed JSON, args, and tool results"
    )
    print(
        " /logs off   Show only clean states like checking memory, thinking, and running tools"
    )
    print(" /clear      Clear the terminal screen")
    print(" /exit       End the current session")
    print(" /quit       End the current session")
    print("")
    print(" Keyboard:")
    print(" Ctrl+C              Gracefully stop ACE")
    print(" Ctrl+Z then Enter   Gracefully stop ACE on Windows")
    print(line("-") + "\n")


def clear_screen():
    import os

    os.system("cls" if os.name == "nt" else "clear")


def print_processing(show_logs: bool):
    print("\n" + line("-"))

    if show_logs:
        print(" ◉ ACE is running with detailed logs enabled.")
    else:
        print(" ◉ ACE is active. Showing clean runtime states.")

    print(line("-"))


def print_result(result: str):
    print("\n" + line("═"))
    print(" RESPONSE")
    print(line("═"))
    print(result)
    print(line("═") + "\n")


def print_exit():
    print("\n" + line("-"))
    print(" ACE session terminated gracefully.")
    print(" Goodbye.")
    print(line("-"))


def print_error(error: Exception):
    print("\n" + line("-"))
    print(" SYSTEM ERROR")
    print(line("-"))
    print(str(error))
    print(line("-"))


def print_logs_status(agent: ACEAgent):
    print("\n" + line("-"))
    print(" ACE LOG DISPLAY")
    print(line("-"))

    agent_logs_enabled = getattr(agent, "show_logs", False)
    console_logs_enabled = get_console_logging()

    if agent_logs_enabled and console_logs_enabled:
        print(" Mode :: Detailed logs enabled")
        print(
            " View :: terminal logs, raw responses, parsed JSON, action args, memories, and tool results"
        )
    else:
        print(" Mode :: Clean status enabled")
        print(
            " View :: checking memory, thinking, parsing, running tools, saving memory"
        )
        print(" Logs :: still saved silently to logs/ace.log")

    print(line("-") + "\n")


def set_logs(agent: ACEAgent, enabled: bool):
    agent.show_logs = enabled
    set_console_logging(enabled)

    print("\n" + line("-"))
    print(" ACE LOG DISPLAY UPDATED")
    print(line("-"))

    if enabled:
        print(" Mode :: Detailed logs enabled")
        print(
            " View :: terminal logs, raw responses, parsed JSON, args, memories, and tool results"
        )
    else:
        print(" Mode :: Clean status enabled")
        print(" View :: spinner states only; logs are still saved to logs/ace.log")

    print(line("-") + "\n")


def handle_command(user_input: str, agent: ACEAgent) -> bool:
    """
    Handles CLI commands.

    Returns True if the command was handled.
    Returns False if the input should be sent to ACE.
    """

    command = user_input.lower().strip()

    if command in ["/exit", "/quit", "exit", "quit", "q"]:
        print_exit()
        raise SystemExit

    if command == "/help":
        print_help()
        return True

    if command == "/clear":
        clear_screen()
        print_banner(getattr(agent, "show_logs", False))
        return True

    if command == "/logs":
        print_logs_status(agent)
        return True

    if command in ["/logs on", "/log on", "/verbose on"]:
        set_logs(agent, True)
        return True

    if command in ["/logs off", "/log off", "/verbose off"]:
        set_logs(agent, False)
        return True

    return False


def main():
    agent = ACEAgent()

    # Keep the CLI display mode and runtime.logger console output synced.
    set_console_logging(getattr(agent, "show_logs", False))

    print_banner(getattr(agent, "show_logs", False))

    while True:
        try:
            try:
                user_input = input("ace › ").strip()

            except EOFError:
                print_exit()
                break

            if not user_input:
                continue

            try:
                if handle_command(user_input, agent):
                    continue

            except SystemExit:
                break

            print_processing(getattr(agent, "show_logs", False))

            result = agent.run(user_input)

            if result:
                print_result(result)

        except KeyboardInterrupt:
            # Ctrl+C
            print_exit()
            break

        except Exception as e:
            print_error(e)


if __name__ == "__main__":
    main()
