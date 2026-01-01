# 🛡️ SentinelGraph: Narrative Detection MVP - Vision & Rules

## 1. Project Objective
To build a real-time intelligence system that detects narratives, coordinated attacks, bot networks, and astroturfing on X (Twitter). The system ingests data via Playwright scrapers, processes it through an analysis pipeline, and visualizes threats on a dashboard.

## 2. 🏗️ Tech Stack (Strict)

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Collector** | Playwright (Python) | `scrp1` (Pulse), `scrp2` (Narrative), `scrp3` (Profile) |
| **Message Queue** | **Redis** | Buffers high-velocity tweets from scrapers. |
| **Primary DB** | **PostgreSQL + pgvector** | **REPLACES SQLITE.** Stores tweets, users, alerts, and vector embeddings. |
| **Analysis** | `sentence-transformers` | CPU-optimized embeddings (e.g., `all-MiniLM-L6-v2`). |
| **Clustering** | `HDBSCAN` / `scikit-learn` | Groups tweets into narratives. |
| **Graph** | `NetworkX` | Community detection and coordination graphing. |
| **Frontend** | Streamlit | Real-time dashboard for analysts. |

> **❌ EXCLUDED:** Ollama / Local LLMs (Due to hardware constraints).
> **❌ DEPRECATED:** SQLite (Migrating to PostgreSQL for scale/vector support).

## 3. 📜 Core Rules (The "Anti-Hallucination" Protocols)

1.  **NO OLLAMA / GEN-AI GENERATION:**
    *   **Rule:** Do not suggest, import, or implement code requiring Ollama, Llama, or heavy local LLMs.
    *   **Alternative:** Use deterministic rule-based classifiers, keyword matching, and static response templates instead of generative replies.

2.  **POSTGRESQL SUPREMACY:**
    *   **Rule:** All new code must use `psycopg2` or `SQLAlchemy` connecting to PostgreSQL.
    *   **Action:** Ignore/Refactor any legacy SQLite code. Ensure `pgvector` extension is enabled for embeddings.

3.  **REALITY CHECK IMPORTS:**
    *   **Rule:** Never import a library without verifying it is in `requirements.txt` or standard library.
    *   **Action:** If a new library is needed (e.g., `sentence-transformers`), explicitly ask to add it to requirements first.

4.  **HARDWARE OPTIMIZATION:**
    *   **Rule:** Assume the system runs on a standard laptop.
    *   **Action:** Use lightweight models (`all-MiniLM-L6-v2`). Avoid heavy batch processing that blocks the main thread. Use `asyncio` where appropriate.

## 4. 🗺️ Implementation Roadmap

### Phase 1: Infrastructure Switch (Current Focus)
- [ ] spin up PostgreSQL container with `pgvector` enabled.
- [ ] Refactor `db_client.py` to connect to Postgres instead of SQLite.
- [ ] Create initial Schema (Tweets, Users, Narratives).

### Phase 2: Ingestion & Pipeline
- [ ] Create `worker.py` to consume Redis streams.
- [ ] Implement Text Cleaning & Feature Extraction (Hashtags, URLs).
- [ ] Store clean data into Postgres.

### Phase 3: Analytical Engines
- [ ] **Bot Detector:** Implement heuristic scoring (Account age, post freq, etc.).
- [ ] **Narrative Clustering:** Integrate `sentence-transformers` + `HDBSCAN`.
- [ ] **Coordination Detector:** Find simultaneous posting patterns.

### Phase 4: Visualization
- [ ] Update `dashboard.py` to query Postgres.
- [ ] Visualize "Risk Score" and "Bot Probability".

## 5. 🧠 Memory Context (For Gemini)
*   **User:** UsmanSarib.
*   **OS:** Windows (win32).
*   **Session:** Persistent Playwright session in `E:\scrp\session_data`.
*   **Current Status:** Scrapers are working (Redis feed active). Database is currently empty/SQLite (needs migration).
