from core.agent import ACEAgent


APP_NAME = "ACE"
APP_FULL_NAME = "Autonomous Cognitive Engine"


def line(char="─", width=72):
    return char * width


def print_banner():
    print("\n" + line("═"))
    print("  █████╗  ██████╗███████╗")
    print(" ██╔══██╗██╔════╝██╔════╝")
    print(" ███████║██║     █████╗  ")
    print(" ██╔══██║██║     ██╔══╝  ")
    print(" ██║  ██║╚██████╗███████╗")
    print(" ╚═╝  ╚═╝ ╚═════╝╚══════╝")
    print(line("═"))
    print(f" {APP_NAME} :: {APP_FULL_NAME}")
    print(" Mode :: Interactive Agent Console")
    print(" Runtime :: Tool-augmented reasoning")
    print(" Memory :: Long-term vector recall enabled")
    print(line("─"))
    print(" Commands:")
    print("   /exit   End session")
    print("   /clear  Clear screen")
    print("   /help   Show commands")
    print(line("═") + "\n")


def print_help():
    print("\n" + line("─"))
    print(" ACE COMMANDS")
    print(line("─"))
    print(" /help   Show this help menu")
    print(" /exit   End the current session")
    print(" /quit   End the current session")
    print(" /clear  Clear the terminal screen")
    print(line("─") + "\n")


def clear_screen():
    import os

    os.system("cls" if os.name == "nt" else "clear")


def print_processing():
    print("\n" + line("─"))
    print(" ◉ ACE is thinking...")
    print(line("─"))


def print_result(result: str):
    print("\n" + line("═"))
    print(" RESPONSE")
    print(line("═"))
    print(result)
    print(line("═") + "\n")


def print_exit():
    print("\n" + line("─"))
    print(" ACE session terminated.")
    print(" Goodbye.")
    print(line("─"))


def print_error(error: Exception):
    print("\n" + line("─"))
    print(" SYSTEM ERROR")
    print(line("─"))
    print(str(error))
    print(line("─"))


def main():
    agent = ACEAgent()

    print_banner()

    while True:
        try:
            user_input = input("ace › ").strip()

            if user_input.lower() in ["/exit", "/quit", "exit", "quit", "q"]:
                print_exit()
                break

            if user_input.lower() == "/help":
                print_help()
                continue

            if user_input.lower() == "/clear":
                clear_screen()
                print_banner()
                continue

            if not user_input:
                continue

            print_processing()

            result = agent.run(user_input)

            if result:
                print_result(result)

        except KeyboardInterrupt:
            print_exit()
            break

        except Exception as e:
            print_error(e)


if __name__ == "__main__":
    main()
