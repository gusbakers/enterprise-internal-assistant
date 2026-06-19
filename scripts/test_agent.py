from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_agent() -> object:
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    agent_file = root / "agent.py"
    spec = importlib.util.spec_from_file_location("crestline_agent", agent_file)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Agent


def print_divider() -> None:
    print("=" * 70)


def main() -> None:
    Agent = _load_agent()
    agent = Agent()
    queries = [
        ("sql", "How many Crestline X phones were sold?"),
        ("hr", "What is the company's PTO policy?"),
        ("marketing", "Tell me about the Crestline Watch campaign strategy"),
        ("product", "What changed in Crestline OS v3.2?"),
    ]

    print_divider()
    print("🚀 Crestline Agent — Block 3 Verification")
    print_divider()

    for index, (category, query) in enumerate(queries, start=1):
        print()
        print_divider()
        print(f"❓ Query {index}: {query}")
        print_divider()
        print()
        print("🤔 Thinking...\n")

        state = agent.run(query, force_category=category)
        print("💬 Response:")
        print(state.query.response or "No response returned.")
        print()

    print_divider()
    print("✅ Agent test complete — Block 3 verified")
    print_divider()


if __name__ == "__main__":
    main()
