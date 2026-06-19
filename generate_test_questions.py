"""Generate test questions for evaluation.

Creates 20 test questions (5 per domain). Domains are discovered from the
`docs/` subdirectories. If fewer domains are present, a fallback "general"
domain is added to reach 20 questions.

Writes output to `data/test_questions.json`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict


OUTPUT_PATH = Path("eval_results/test_questions.json")
DOCS_DIR = Path("docs")
QUESTIONS_PER_DOMAIN = 5
TARGET_TOTAL = 20


def make_questions_for_domain(domain: str, files: List[str], start_id: int) -> List[Dict]:
    questions = []
    for i in range(QUESTIONS_PER_DOMAIN):
        file_hint = files[i] if i < len(files) else None
        if file_hint:
            q_text = f"Summarize the document '{file_hint}' in the {domain} domain."
        else:
            q_text = f"Give a concise test question about {domain} policies or procedures."
        questions.append({"id": start_id + i, "domain": domain, "question": q_text})
    return questions


def discover_domains() -> Dict[str, List[str]]:
    domains = {}
    if not DOCS_DIR.exists():
        return domains
    for entry in sorted(DOCS_DIR.iterdir()):
        if entry.is_dir():
            files = [f.name for f in sorted(entry.iterdir()) if f.is_file()]
            domains[entry.name] = files
    return domains


def main():
    domains = discover_domains()
    # Ensure we have at least one domain
    if not domains:
        domains = {"general": []}

    questions = []
    current_id = 1
    for domain, files in domains.items():
        questions.extend(make_questions_for_domain(domain, files, current_id))
        current_id += QUESTIONS_PER_DOMAIN

    # If we produced fewer than TARGET_TOTAL, add a fallback domain
    while len(questions) < TARGET_TOTAL:
        domain = "general"
        questions.extend(make_questions_for_domain(domain, [], current_id))
        current_id += QUESTIONS_PER_DOMAIN

    # Trim to exact target
    questions = questions[:TARGET_TOTAL]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print("📝 Crestline Test Questions Generator")
    print("=" * 60)
    print(f"✅ Saved {len(questions)} test questions to {OUTPUT_PATH}")
    print()
    print("✅ Test questions ready for RAGAS evaluation")


if __name__ == "__main__":
    main()
