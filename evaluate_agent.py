"""Run a simple RAGAS-style evaluation on the local agent.

This script loads questions from `data/test_questions.json`, attempts to invoke
the local agent (from `agent` or `agent_cli`) to produce answers, and writes a
results file to `results/scores.json`.

If a full RAGAS evaluation package is available in the environment, you can
replace the evaluation logic inside `evaluate_responses()` with a proper
RAGAS call.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from typing import List, Dict, Any


POSSIBLE_QUESTION_PATHS = [
    Path("eval_results/test_questions_by_domain.json"),
    Path("eval_results/test_questions.json"),
    Path("data/test_questions.json"),
]
RESULTS_PATH = Path("results/scores.json")


def load_questions() -> List[Dict[str, Any]]:
    # Pick the first existing questions file from known locations
    questions_file = None
    for p in POSSIBLE_QUESTION_PATHS:
        if p.exists():
            questions_file = p
            break
    if not questions_file:
        raise FileNotFoundError(f"No questions file found in any of: {POSSIBLE_QUESTION_PATHS}")

    with questions_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Normalize formats:
    # - If list of dicts: assume already in expected format
    # - If list of strings: convert to dicts with domain 'general'
    # - If dict mapping domains -> list(strings): expand per-domain
    if isinstance(data, list):
        if data and isinstance(data[0], dict):
            return data
        # list of strings
        return [
            {"id": idx + 1, "domain": "general", "question": q}
            for idx, q in enumerate(data)
        ]

    if isinstance(data, dict):
        # If only 'all' provided, use it as general questions
        if set(data.keys()) == {"all"}:
            all_qs = data["all"]
            return [
                {"id": idx + 1, "domain": "general", "question": q}
                for idx, q in enumerate(all_qs)
            ]

        questions = []
        cur_id = 1
        for domain in sorted(data.keys()):
            if domain == "all":
                continue
            items = data[domain] or []
            for item in items:
                if isinstance(item, dict):
                    qtext = item.get("question") or item.get("q") or str(item)
                else:
                    qtext = str(item)
                questions.append({"id": cur_id, "domain": domain, "question": qtext})
                cur_id += 1
        return questions

    raise ValueError("Unrecognized questions file format")


def _load_agent_class() -> type:
    root = Path(__file__).resolve().parent
    agent_path = root / "agent.py"
    spec = importlib.util.spec_from_file_location("crestline_agent", agent_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "Agent"):
        raise ImportError("agent.py does not define Agent")
    return getattr(module, "Agent")


def try_invoke_agent(question: str) -> str:
    # Attempt to load the local Agent class and ask the question.
    try:
        Agent = _load_agent_class()
        inst = Agent()
        state = inst.run(question)
        if hasattr(state, "query") and getattr(state.query, "response", None) is not None:
            return state.query.response
        if hasattr(state, "response") and state.response is not None:
            return state.response
    except Exception:
        pass

    try:
        import agent_cli

        if hasattr(agent_cli, "run"):
            return agent_cli.run(question)
    except Exception:
        pass

    # Fallback simulated response
    return "[NO_AGENT_AVAILABLE]"


def evaluate_responses(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = {"questions": [], "summary": {}}
    domain_stats = {}

    for q in questions:
        qid = q.get("id")
        domain = q.get("domain", "general")
        text = q.get("question", "")
        resp = try_invoke_agent(text)

        entry = {"id": qid, "domain": domain, "question": text, "response": resp}
        results["questions"].append(entry)

        stats = domain_stats.setdefault(domain, {"count": 0, "total_len": 0})
        stats["count"] += 1
        stats["total_len"] += len(resp or "")

    # compute per-domain averages
    summary = {}
    for d, s in domain_stats.items():
        summary[d] = {"num_questions": s["count"], "avg_response_length": s["total_len"] / s["count"]}

    results["summary"] = summary
    return results


def main():
    questions = load_questions()
    results = evaluate_responses(questions)

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Wrote evaluation results to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
