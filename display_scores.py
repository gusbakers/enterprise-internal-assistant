"""Display evaluation scores in a human-friendly format.

Loads `results/scores.json` produced by `evaluate_agent.py` and prints a
summary table grouped by domain. If `tabulate` is installed it will be used
for prettier output; otherwise a simple formatted table is printed.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


POSSIBLE_RESULTS_PATHS = [
    Path("eval_results/ragas_scores.json"),
    Path("results/scores.json"),
    Path("eval_results/scores.json"),
]


def load_results() -> Dict[str, Any]:
    results_file = None
    for p in POSSIBLE_RESULTS_PATHS:
        if p.exists():
            results_file = p
            break
    if not results_file:
        raise FileNotFoundError(f"No results file found in any of: {POSSIBLE_RESULTS_PATHS}")
    with results_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # If file contains 'summary', return it directly
    if isinstance(data, dict) and "summary" in data:
        return data

    # If RAGAS-style output (metrics + responses), compute per-domain summary
    if isinstance(data, dict) and "responses" in data:
        responses = data.get("responses", [])
        domain_stats = {}
        for r in responses:
            d = r.get("domain", "general")
            resp = r.get("response") or ""
            stats = domain_stats.setdefault(d, {"count": 0, "total_len": 0})
            stats["count"] += 1
            stats["total_len"] += len(resp)

        summary = {}
        for d, s in domain_stats.items():
            summary[d] = {"num_questions": s["count"], "avg_response_length": s["total_len"] / s["count"]}
        return {"summary": summary}

    raise ValueError("Unrecognized results file format")


def print_table(rows, headers):
    try:
        from tabulate import tabulate

        print(tabulate(rows, headers=headers, tablefmt="github"))
    except Exception:
        # Simple fallback
        col_widths = [max(len(str(c)) for c in col) for col in zip(*([headers] + rows))]
        fmt = "  ".join("{:<%d}" % w for w in col_widths)
        print(fmt.format(*headers))
        for r in rows:
            print(fmt.format(*r))


def main():
    data = load_results()
    summary = data.get("summary", {})

    rows = []
    total_q = 0
    total_len = 0
    for domain, stats in sorted(summary.items()):
        nq = stats.get("num_questions", 0)
        al = stats.get("avg_response_length", 0)
        rows.append([domain, nq, f"{al:.1f}"])
        total_q += nq
        total_len += al * nq

    # totals
    avg_overall = (total_len / total_q) if total_q else 0
    rows.append(["TOTAL", total_q, f"{avg_overall:.1f}"])

    headers = ["Domain", "Num Questions", "Avg Response Length"]
    print_table(rows, headers)


if __name__ == "__main__":
    main()
