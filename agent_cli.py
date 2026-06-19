from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_agent() -> object:
    agent_path = Path(__file__).resolve().parent / "agent.py"
    spec = importlib.util.spec_from_file_location("crestline_agent", agent_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load agent.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Agent


def main() -> None:
    print("Crestline Internal Assistant CLI")
    print("Type 'exit' or 'quit' to end the session.")

    Agent = _load_agent()
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
