from __future__ import annotations

import os
import re
from typing import Literal

try:
    from langchain_groq import Groq
except ImportError:  # pragma: no cover
    Groq = None

Category = Literal["hr", "marketing", "product", "sql", "unknown"]


class GroqRouter:
    """Route user questions to a tool category using Groq classification.

    If the Groq client is unavailable, the router falls back to a
    keyword-based heuristic classifier.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None

        if Groq is not None and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception:
                self.client = None

    def classify(self, question: str) -> Category:
        normalized = question.strip()
        if not normalized:
            return "unknown"

        if self._is_strong_sql_query(normalized):
            return "sql"

        if self.client:
            try:
                prompt = self._build_prompt(normalized)
                result = self._call_groq(prompt)
                label = self._normalize_label(result)
                if label != "unknown":
                    return label
            except Exception:
                pass

        return self._heuristic_classify(normalized)

    def _build_prompt(self, question: str) -> str:
        return (
            "Classify the following Crestline internal assistant question into exactly one of "
            "these categories: hr, marketing, product, sql. Return only the category name.\n\n"
            f"Question: {question}\n"
        )

    def _call_groq(self, prompt: str) -> str:
        if hasattr(self.client, "predict"):
            return str(self.client.predict(prompt)).strip()
        if hasattr(self.client, "complete"):
            return str(self.client.complete(prompt)).strip()
        if hasattr(self.client, "generate"):
            return str(self.client.generate(prompt)).strip()
        raise RuntimeError("Groq client does not expose a compatible completion method.")

    def _normalize_label(self, label: str) -> Category:
        label = label.lower().strip()
        if label in {"hr", "human resources"}:
            return "hr"
        if label in {"marketing", "mar"}:
            return "marketing"
        if label in {"product", "prod"}:
            return "product"
        if label in {"sql", "data", "database"}:
            return "sql"
        return "unknown"

    def _is_strong_sql_query(self, question: str) -> bool:
        q = question.lower()
        if "how many" in q and ("employees" in q or "employee" in q):
            return True

        department_names = [
            "engineering", "product", "marketing", "sales",
            "finance", "hr", "human resources",
        ]
        if "how many" in q and any(dept in q for dept in department_names):
            return True

        if "headcount" in q or "count of" in q:
            return True

        return False

    def _heuristic_classify(self, question: str) -> Category:
        q = question.lower()

        patterns: dict[Category, list[str]] = {
            "hr": [
                "pto",
                "vacation",
                "remote work",
                "onboarding",
                "employee",
                "employees",
                "salary",
                "benefits",
                "hiring",
                "termination",
                "policy",
            ],
            "marketing": [
                "campaign",
                "launch",
                "channel",
                "ads",
                "target audience",
                "brand",
                "impression",
                "conversion",
                "instagram",
                "linkedin",
                "youtube",
            ],
            "product": [
                "api",
                "changelog",
                "system requirements",
                "release",
                "feature",
                "cloud",
                "os",
                "device",
                "update",
            ],
            "sql": [
                "sales",
                "revenue",
                "headcount",
                "count",
                "how many",
                "employees",
                "database",
                "query",
                "metric",
                "mrr",
                "churn",
                "kpi",
            ],
        }

        scores: dict[Category, int] = {category: 0 for category in patterns}
        for category, keywords in patterns.items():
            for keyword in keywords:
                if re.search(rf"\b{re.escape(keyword)}\b", q):
                    scores[category] += 1

        winner = max(scores, key=scores.get)
        if scores[winner] == 0:
            return "unknown"
        return winner
