"""CLI entrypoint for agent tools."""

import argparse
from typing import Callable

from . import HRTool, MarketingTool, ProductTool, SQLTool

TOOL_CLASSES = {
    "hr": HRTool,
    "marketing": MarketingTool,
    "product": ProductTool,
    "sql": SQLTool,
}

TOOL_HELP = {
    "hr": "Search HR policy docs (hr_docs collection)",
    "marketing": "Search marketing docs (marketing_docs collection)",
    "product": "Search product docs (product_docs collection)",
    "sql": "Run a SQL query against data/crestline.db",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Crestline agent tools from the command line."
    )
    parser.add_argument(
        "tool",
        choices=list(TOOL_CLASSES),
        nargs="?",
        help="Tool to run",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Query text for the selected tool",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of search results to return for vector search tools",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available tools",
    )
    return parser.parse_args()


def list_tools() -> str:
    lines = ["Available tools:"]
    for name, desc in TOOL_HELP.items():
        lines.append(f"  {name}: {desc}")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    if args.list or not args.tool:
        print(list_tools())
        print("\nUsage example: python -m agent.tools hr \"What is the PTO policy?\"")
        return

    query = " ".join(args.query).strip() if args.query else ""
    if not query:
        raise SystemExit("Error: query text is required when a tool is selected.")

    tool_class = TOOL_CLASSES[args.tool]
    tool = tool_class()

    if args.tool in ["hr", "marketing", "product"]:
        if not hasattr(tool, "search"):
            raise SystemExit(f"Tool {args.tool} does not support vector search.")
        output = tool.run(query)
    else:
        output = tool.run(query)

    print(output)


if __name__ == "__main__":
    main()
