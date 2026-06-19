from __future__ import annotations

from agent import Agent


def main() -> None:
    print("Crestline Internal Assistant CLI")
    print("Type 'exit' or 'quit' to end the session.")

    agent = Agent()

    while True:
        try:
            prompt = input("\nAsk a question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        state = agent.run(prompt)
        print("\n" + (state.query.response or "No response returned."))


if __name__ == "__main__":
    main()
