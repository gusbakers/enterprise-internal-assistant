"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRESTLINE TECHNOLOGIES — TOOL TESTS
Role: ML Engineer
Block: 2 — RAG Core
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tests all 4 tools with real Crestline questions
Run: python scripts/test_tools.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
sys.path.append(".")

from agent.tools.sql_tool       import SQLTool
from agent.tools.hr_tool        import HRTool
from agent.tools.marketing_tool import MarketingTool
from agent.tools.product_tool   import ProductTool

DIVIDER = "=" * 60

def test_tool(name: str, tool, questions: list[str]) -> None:
    print(f"\n{DIVIDER}")
    print(f"🧪 Testing: {name}")
    print(DIVIDER)
    for q in questions:
        print(f"\n❓ Query: {q}")
        print("-" * 40)
        result = tool.run(q)
        print(result)


def main() -> None:
    print(f"\n{DIVIDER}")
    print("🚀 Crestline Tool Tests — Block 2 Verification")
    print(DIVIDER)

    # ── SQL Tool ───────────────────────────────────────────────────
    test_tool(
        "SQL Tool",
        SQLTool(),
        [
            "How many Crestline X phones were sold?",
            "How many employees work in Engineering?",
            "What was the marketing budget for Crestline Pro?",
            "What is the latest MRR?",
        ],
    )

    # ── HR Tool ────────────────────────────────────────────────────
    test_tool(
        "HR Tool",
        HRTool(),
        [
            "How many vacation days do employees get?",
            "What is the remote work policy?",
            "What happens on Day 1 for new employees?",
        ],
    )

    # ── Marketing Tool ─────────────────────────────────────────────
    test_tool(
        "Marketing Tool",
        MarketingTool(),
        [
            "What was the launch strategy for Crestline X?",
            "What channels did we use for the Watch campaign?",
            "Who is the target audience for Crestline Pro?",
        ],
    )

    # ── Product Tool ───────────────────────────────────────────────
    test_tool(
        "Product Tool",
        ProductTool(),
        [
            "What changed in Crestline OS v3.2?",
            "What are the API rate limits for Crestline Cloud?",
            "What are the system requirements for Crestline Pro?",
        ],
    )

    print(f"\n{DIVIDER}")
    print("✅ All tools tested — Block 2 complete")
    print(DIVIDER)


if __name__ == "__main__":
    main()
