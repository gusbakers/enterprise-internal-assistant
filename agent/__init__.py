from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path so we can import root-level modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from router import GroqRouter, Category
from response_generator import ResponseGenerator
from state import AgentState, QueryState

TOOL_REGISTRY: dict[Category, tuple[str, str]] = {
    "hr": ("hr_tool", "HRTool"),
    "marketing": ("marketing_tool", "MarketingTool"),
    "product": ("product_tool", "ProductTool"),
    "sql": ("sql_tool", "SQLTool"),
}


def _load_tool_class(module_name: str, class_name: str) -> type:
    current_dir = Path(__file__).resolve().parent
    module_path = current_dir / "tools" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(f"_agent_tools.{module_name}", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load tool module: {module_name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tool_class = getattr(module, class_name, None)
    if tool_class is None:
        raise ImportError(f"Tool class {class_name} not found in {module_name}.py")

    return tool_class


class Agent:
    def __init__(self, tools: dict[Category, Any] | None = None, router: GroqRouter | None = None):
        self.router = router or GroqRouter()
        self.response_generator = ResponseGenerator()
        self.tools = tools or self._build_tool_instances()

    def _build_tool_instances(self) -> dict[Category, Any]:
        instances: dict[Category, Any] = {}
        for category, (module_name, class_name) in TOOL_REGISTRY.items():
            tool_class = _load_tool_class(module_name, class_name)
            instances[category] = tool_class()
        return instances

    def route(self, question: str) -> Category:
        return self.router.classify(question)

    def run(self, question: str, force_category: Category | None = None) -> AgentState:
        state = QueryState(question=question)
        state.category = force_category or self.route(question)
        state.tool_input = question

        tool = self.tools.get(state.category)
        if tool is None:
            state.tool_output = None
            state.error = None
        else:
            try:
                state.tool_output = tool.run(question)
            except Exception as exc:
                state.tool_output = None
                state.error = str(exc)

        state.response = self.response_generator.generate_response(state)
        return AgentState(
            query=state,
            graph={
                "router": self.router.__class__.__name__,
                "response_generator": self.response_generator.__class__.__name__,
            },
            steps=["route", "execute_tool", "generate_response"],
        )


__all__ = ["Agent"]
