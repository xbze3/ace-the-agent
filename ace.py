from core.agent import ACEAgent


def print_banner():
    print("═" * 70)
    print(" ACE (Autonomous Cognitive Engine)")
    print(" Interactive Agent Console")
    print("═" * 70)
    print(" Type your request below.")
    print(" Type 'exit' or 'quit' to end the session.")
    print("═" * 70 + "\n")


def main():
    agent = ACEAgent()

    print_banner()

    while True:
        try:
            user_input = input("➤ ")

            if user_input.lower().strip() in ["exit", "quit", "q"]:
                print("\n" + "-" * 70)
                print(" Session ended. Goodbye.")
                print("-" * 70)
                break

            if not user_input.strip():
                continue

            print("\n" + "-" * 70)
            print(" Processing request...")
            print("-" * 70)

            result = agent.run(user_input)

            if result:
                print("\n" + "═" * 70)
                print(" RESULT")
                print("═" * 70)
                print(result)
                print("═" * 70 + "\n")

        except KeyboardInterrupt:
            print("\n" + "-" * 70)
            print(" Interrupted. Exiting...")
            print("-" * 70)
            break

        except Exception as e:
            print("\n" + "-" * 70)
            print(f"[ERROR] {str(e)}")
            print("-" * 70)
