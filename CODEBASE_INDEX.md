# SentinelGraph Codebase Index
*Generated on 2025-12-30*

This document provides an index of the current codebase state, mapping implemented components to the project roadmap.

## 1. System Overview
**SentinelGraph** is a real-time narrative detection system for X (Twitter). It currently features a complete data ingestion pipeline, storage layer, and initial analytical modules for clustering and bot detection.

| Component | Status | Description |
| :--- | :---: | :--- |
| **Scrapers** | ✅ Active | Playwright-based scrapers for Pulse (`scrp1`), Narrative (`scrp2`), and Profiles (`scrp3`). |
| **Ingestion** | ✅ Active | File watcher (`scripts/ingest.py`) pushes JSON to Redis Streams. |
| **Processing** | ✅ Active | Worker (`app/worker.py`) consumes Redis, generates embeddings, and saves to Postgres. |
| **Storage** | ✅ Active | PostgreSQL (Metadata + Vectors) and Redis (Hot Cache/Streams). |
| **Analysis** | ⚠️ Partial | Bot detection and clustering implemented; Graph/Community detection in early stages. |
| **Dashboard** | ⚠️ Pending | Basic Streamlit setup; needs integration with new Postgres schema. |

## 2. Component Details

### A. Data Collection & Ingestion
*   **`scrp1.py`**: "Pulse" scraper. Runs continuous search queries to fetch latest tweets.
*   **`scrp2.py`**: "Narrative" scraper. Deep dives into specific queries.
*   **`scrp3.py`**: "Profile" scraper. Fetches user details (followers, bio, join date).
*   **`scripts/ingest.py`**: Uses `watchdog` to monitor `data/raw_json/`. Parses new files and pushes them to the `tweets:micro` Redis stream.

### B. Core Processing (Worker)
*   **`app/worker.py`**:
    *   **Role**: The central nervous system.
    *   **Logic**:
        1.  Connects to Redis Stream (`tweets:micro`).
        2.  Consumes batches (default 50).
        3.  Cleans text using `app/services/cleaner.py`.
        4.  Generates semantic embeddings using `sentence-transformers` (`all-MiniLM-L6-v2`).
        5.  Upserts `User` and `Tweet` records to PostgreSQL.
    *   **Status**: Fully functional logic.

### C. Analytical Modules (`app/detection/`)
*   **`bot_detector.py`**:
    *   **Logic**: Calculates a 0.0-1.0 "Bot Score" based on:
        *   Posting Frequency (30%)
        *   Account Age (25%)
        *   Follower Ratio (20%)
        *   Text Repetition (25%)
    *   **Status**: Logic implemented.
*   **`clustering.py`**:
    *   **Logic**:
        *   Fetches recent tweets (e.g., last 6h) from Postgres.
        *   Uses `HDBSCAN` on vector embeddings to find narrative clusters.
        *   Updates `Tweet.narrative_id`.
        *   Detects volume spikes (>3x velocity).
    *   **Status**: Logic implemented.
*   **`community.py`**: Structure for graph-based community detection (Louvain algorithm).
*   **`coordination.py`**: Structure for detecting coordinated behavior (same text, same time).
*   **`origin.py`**: Structure for tracing narrative origins (time-bucketed analysis).

### D. Services (`app/services/`)
*   **`cleaner.py`**: Text normalization, emoji removal, and feature extraction (hashtags/mentions).
*   **`url_expander.py`**: Async URL expansion to resolve shortlinks (e.g., `bit.ly` -> real domain).
*   **`advisor.py`**: Rule-based system for recommending response strategies (Firm, Calm, Polite, Transparent).

## 3. Database Schema
*   **PostgreSQL**:
    *   `users`: `user_id`, `handle`, `stats` (followers/following), `bot_score`.
    *   `tweets`: `tweet_id`, `text`, `embedding` (vector), `narrative_id`.
    *   `narratives`: (Planned) Metadata about detected clusters.
*   **Redis**:
    *   Stream: `tweets:micro` (Ingestion buffer).

## 4. Next Steps (Gap Analysis)
1.  **Dashboard Integration**: Update `dashboard.py` to pull real-time data from PostgreSQL instead of local logs/JSON.
2.  **Orchestration**: Create a "Master Loop" that runs the Scrapers -> Worker -> Clustering -> Dashboard continuously.
3.  **Graph Analysis**: Fully implement the NetworkX logic in `community.py` and visualize it.
