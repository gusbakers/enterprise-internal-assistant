# Assistant architecture

[Project overview](../README.md)

## Request processing


```mermaid
flowchart TD
    U["User question"] --> UI["Streamlit: input and session history"]
    UI --> PY["Python: resolve follow-up and classify domain"]
    PY --> KIND{"Supported request?"}
    KIND -->|Business analytics| SQL["Python: validate filters and SQL template"]
    SQL --> DB["PostgreSQL: parameterized read-only query"]
    KIND -->|HR, Marketing, Product| EMB["FastEmbed: multilingual query embedding"]
    EMB --> VEC["pgvector: exact cosine search"]
    EMB --> TXT["PostgreSQL: full-text search"]
    VEC --> RANK["Python: rank fusion and relevance filter"]
    TXT --> RANK
    DB --> E["Evidence: computed rows or source passages"]
    RANK --> E
    KIND -->|Unsupported or ambiguous| STOP["Clarify or acknowledge missing information"]
    E --> CHECK{"Evidence available?"}
    CHECK -->|No| STOP
    CHECK -->|Yes| LLM{"Gemini configured and available?"}
    LLM -->|Yes| GEN["Gemini: grounded answer in JSON"]
    GEN --> VALID{"Valid citations and numbers?"}
    VALID -->|Yes| ANSWER["Answer with source references"]
    VALID -->|No| FALL["Python: concise rows or cited fact selection"]
    LLM -->|No| FALL
    ANSWER --> OUT["Streamlit: answer, sources, data and query"]
    FALL --> OUT
    STOP --> OUT
    OUT --> HISTORY["Session-local conversation history"]
```

| Stack | What happens |
|---|---|
| **Streamlit** | Collects the question, keeps the last turns in that browser session, displays evidence and optional SQL details. Shared resources are cached; conversation state is not shared between users. |
| **Python** | Resolves explicit follow-ups such as “And Q2?”, routes to one domain, validates supported filters and handles unsupported requests. Routing is deterministic, not an autonomous multi-agent system. |
| **PostgreSQL** | Stores sales, employee aggregates, campaign metrics and company metrics. SQL templates use bound parameters and read-only transactions with a five-second statement timeout. |
| **FastEmbed / ONNX** | Encodes document passages and questions using `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions), without PyTorch or a paid embedding API. |
| **pgvector + full-text search** | Combines exact cosine search and lexical ranking using reciprocal rank fusion. Source restrictions and a similarity gate remove some irrelevant results. Thresholds remain an evaluation choice, not a correctness guarantee. |
| **Gemini** | Optionally rewrites the retrieved evidence into a concise answer. JSON output includes source IDs; invalid references or unsupported numeric values fall back to concise cited evidence. Answers are instructed to stay within 80 words. No LLM-generated SQL is executed. |
| **Docker / Hugging Face** | Starts PostgreSQL on a private Unix socket, loads the reproducible dataset, then starts Streamlit on port 7860. An external PostgreSQL connection can be supplied instead. |
| **GitHub Actions / pytest** | Checks SQL ground truth, routing, unsupported questions, retrieval against actual pgvector and container startup before syncing the Space. |

## Document indexing

```mermaid
flowchart TD
    DOC["Versioned HR, Marketing and Product documents"] --> CHUNK["Python: section-aware chunks with source IDs"]
    CHUNK --> ENCODE["FastEmbed: multilingual vectors"]
    ENCODE --> STORE["PostgreSQL: content, metadata and vector columns"]
    FIX["Versioned business fixture"] --> TABLES["PostgreSQL: business tables"]
    STORE --> HASH["Dataset fingerprint: reuse matching data"]
    TABLES --> HASH
    HASH --> READY["Assistant ready"]
```

The loader preserves short sections, attaches document headings, and checks a dataset fingerprint. Matching data is reused on restart; a changed dataset requires a fresh demo database instead of silently overwriting an existing one. This small corpus uses exact vector search; an HNSW index is not necessary at this size.
