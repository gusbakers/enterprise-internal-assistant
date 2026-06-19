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


def test_routing_and_response() -> None:
    Agent = _load_agent()
    agent = Agent()

    question = "What is our remote work policy?"
    state = agent.run(question, force_category="hr")

    assert state.query.category == "hr"
    assert state.query.tool_output is not None
    assert "remote work" in state.query.tool_output.lower() or "policy" in state.query.tool_output.lower()
    assert state.query.response is not None


def test_unknown_question() -> None:
    Agent = _load_agent()
    agent = Agent()

    question = "Tell me the weather in Crestline headquarters."
    state = agent.run(question)

    assert state.query.category in {"hr", "marketing", "product", "sql", "unknown"}
    assert state.query.response is not None


if __name__ == "__main__":
    test_routing_and_response()
    test_unknown_question()
    print("All agent tests passed.")
