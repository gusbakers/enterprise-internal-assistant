# Crestline Internal Assistant 🤖

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/Groq-Llama%203.1%208B%20Instant-green?style=flat-square" />
  <img src="https://img.shields.io/badge/Qdrant-Vector%20DB-red?style=flat-square" />
  <img src="https://img.shields.io/badge/Streamlit-UI-ff4b4b?style=flat-square&logo=streamlit" />
  <img src="https://img.shields.io/badge/🤗%20HuggingFace-Spaces-yellow?style=flat-square" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" />
</p>

<p align="center">
  <b>An enterprise internal AI agent for Crestline Technologies — a fictional B2B SaaS company.</b><br>
  A Groq-powered router sends employee questions to four domain tools (HR, Marketing, Product RAG + SQL), backed by a Streamlit UI and an evaluation harness.
</p>

<p align="center">
  <a href="https://huggingface.co/spaces/gustavoscience/crestline-internal-assistant">
    <img src="https://img.shields.io/badge/🚀%20Live%20Demo-HuggingFace%20Spaces-yellow?style=for-the-badge" />
  </a>
</p>

---

## 📌 What It Does

Employees can ask natural-language questions and get routed automatically to the right data source — no need to know whether the answer lives in a spreadsheet or a policy doc.

| Domain | Example Question |
|---|---|
| 💰 SQL | *"How many Crestline X phones were sold?"* |
| 👥 HR | *"What's the PTO policy after 3 years?"* |
| 📣 Marketing | *"What was the Crestline Watch campaign strategy?"* |
| 🛠️ Product | *"What changed in Crestline OS v3.2?"* |

---

## 🏗️ Architecture

```
                    ┌──────────┐
                    │   User   │
                    └────┬─────┘
                         ▼
                    ┌──────────┐
                    │ Streamlit│
                    └────┬─────┘
                         ▼
                    ┌──────────┐
                    │  Agent   │
                    └────┬─────┘
                         ▼
                    ┌──────────┐
                    │  Router  │  ← Groq (ChatGroq.invoke)
                    └────┬─────┘
        ┌────────┬───────┼────────┬────────┐
        ▼        ▼       ▼        ▼
   ┌────────┐┌────────┐┌────────┐┌────────┐
   │ HRTool ││MktTool ││ProdTool││ SQLTool│
   └───┬────┘└───┬────┘└───┬────┘└───┬────┘
       └─────────┴─────────┘         │
                 ▼                   ▼
            ┌─────────┐         ┌─────────┐
            │ Qdrant  │         │ SQLite  │
            └────┬────┘         └────┬────┘
                 └─────────┬─────────┘
                           ▼
                 ┌───────────────────┐
                 │ ResponseGenerator │
                 └────────┬──────────┘
                          ▼
                     Final Answer
```

**Flow:** Streamlit collects the question → the `Agent` hands it to the `Router`, which classifies it via Groq → the matching tool queries Qdrant (HR/Marketing/Product) or SQLite (SQL) → `ResponseGenerator` formats the final answer for the UI.

---

## 💭 Why I Built This

Most portfolio agent projects I see do one thing — RAG over a folder of PDFs. I wanted something closer to what an internal assistant at an actual company would need: routing between **structured data (SQL)** and **unstructured documents (RAG)** across multiple domains, not just one.



---

## 🧭 Project Status

I ran this through a real debugging pass with Cursor after the first build, and I'd rather be upfront here about what's solid and what's still rough than pretend it's all finished. If you're reviewing this as a hiring manager or fellow engineer, that's probably more useful to you anyway.

### ✅ Currently Working

- End-to-end routing: question → correct tool → answer, **100% success rate** on the 20-question test set
- Groq-based router using `ChatGroq.invoke()` with `llama-3.1-8b-instant`
- Heuristic keyword fallback when `GROQ_API_KEY` isn't set — the agent still runs, just without LLM-based routing
- RAG tools (HR/Marketing/Product) fall back to keyword search if Qdrant is unavailable
- Streamlit app bootstraps docs, SQLite, and Qdrant on startup and caches the agent (no rebuild per click)
- HuggingFace Space deploy builds Qdrant fresh at runtime from a clean snapshot

### ⚠️ Next Engineering Improvements

| Limitation | Detail |
|---|---|
| **No LLM answer synthesis** | Responses are raw RAG chunks / SQL rows, not summarized prose. `ResponseGenerator` formats, it doesn't yet rewrite. |
| **SQL tool is keyword-driven** | Not true text-to-SQL — it pattern-matches question phrasing to pre-built queries rather than generating SQL from scratch. |
| **RAGAS scores ** | `evaluate_agent.py` does not yet call the real `ragas` library — current scores are not trustworthy as RAG quality metrics. |
| **Duplicated tool code** | `HRTool`, `MarketingTool`, and `ProductTool` are ~90% identical — a shared base class hasn't been factored out yet. |
| **Imperfect routing on edge cases** | General-domain questions can mis-route to HR because broad terms like "policies" overlap with HR keywords. |

---

## 🛠️ Engineering Log — What Was Broken, What Got Fixed

The first version of this looked complete but quietly wasn't — the eval script was returning placeholder errors for every single question. Here's what was actually wrong and how I fixed it:

| Issue | Impact | Fix |
|---|---|---|
| `evaluate_agent.py` / `test_agent.py` imported a non-existent `agent.py` interface | All 20 eval responses returned `[NO_AGENT_AVAILABLE]` | Switched to `from agent import Agent` |
| Groq router called the wrong API (`predict`/`complete`) | LLM routing silently failed without surfacing an error | Switched to `ChatGroq.invoke()` |
| Router missed "hr", "policies", doc filenames, and "X domain" phrasing | Meta-style test questions routed to `unknown` | Added explicit domain detection, filename mapping, expanded keyword lists |
| `app.py` rebuilt the agent on every click; no docs/DB bootstrap | Slow UI, HF Space cold start could fail outright | App now bootstraps data once on startup and caches the agent |
| Response generator duplicated category metadata in every answer | Noisy, repetitive UI output | Returns tool output directly, no metadata wrapping |

---

## 📊 Post-Fix Validation Results


| Domain | Questions | Avg. response length |
|---|---|---|
| HR | 5 | 676 chars |
| Marketing | 5 | 5,216 chars |
| Product | 5 | 8,380 chars |
| General | 5 | 700 chars |

Qdrant ingestion verified: **95 vector points across 3 collections** (hr_docs, marketing_docs, product_docs). Agent unit tests pass.

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **Orchestration** | `Agent` + `Router` classes | Question classification and dispatch to tools |
| **LLM** | Groq — `llama-3.1-8b-instant` | Query routing (heuristic fallback if no API key) |
| **Vector DB** | Qdrant | Semantic search over HR, marketing, product docs |
| **SQL DB** | SQLite | Sales, employees, campaigns, metrics |
| **UI** | Streamlit | Chat interface, bootstraps data on startup |
| **Eval harness** | Custom script (RAGAS integration pending) | Success rate, routed category, response length tracking |
| **Deploy** | HuggingFace Spaces | Public demo, builds Qdrant fresh at runtime |
| **Language** | Python 3.12 | Everything |

---

## 🚀 Getting Started

```bash
# 1. Set up environment
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Generate data and ingest into Qdrant
python scripts/generate_docs.py
python scripts/generate_db.py
python scripts/ingest_docs.py

# 3. Run the app
streamlit run app.py

# Or run the evaluation harness instead:
python evaluate_agent.py
python display_scores.py
```

Set `GROQ_API_KEY` in `.env` to enable LLM-based routing. Without it, the agent still works using the heuristic keyword fallback.

---

## 🗺️ What's Next

In priority order, here's what I'd tackle next if I kept going on this:

1. **LLM answer synthesis** — have Groq summarize raw tool output into natural prose instead of returning chunks/rows directly
2. **Real RAGAS evaluation** — replace the simulated scoring in `evaluate_agent.py` with actual `ragas` library calls (faithfulness, answer relevancy, context precision)
3. **Deduplicate RAG tools** — factor `HRTool`, `MarketingTool`, and `ProductTool` into one shared base class with a `collection_name` parameter

---

## 💡 Crestline Technologies (Fictional Company Context)

The agent simulates an internal assistant for a fictional B2B SaaS company selling:

| Product | Category |
|---|---|
| Crestline Pro | 💻 Business laptop |
| Crestline X | 📱 Smartphone |
| Crestline Watch | ⌚ Smartwatch |
| Crestline OS | 💾 Operating system |
| Crestline Cloud | ☁️ Cloud storage for business |

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

## 👤 Author

Built by **Gustavo** — Data professional  | Master's in Data Science 
Data Engineer · ML Engineer · AI Engineer



[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/gustavo-f-a27066145)
[![GitHub](https://img.shields.io/badge/GitHub-@gusbakers-black?style=flat-square&logo=github)](https://github.com/gusbakers)
