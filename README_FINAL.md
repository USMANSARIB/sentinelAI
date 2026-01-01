# SentinelGraph - Final MVP

This project is a real-time narrative detection and analysis system for X (Twitter).
It detects bots, clusters similar narratives, and visualizes data in a dashboard.

## 🏁 How to Run

### 1. Prerequisites
*   Docker Desktop installed and running.
*   Python 3.10+ installed.

### 2. Setup Infrastructure
Start Redis and PostgreSQL:
```bash
docker-compose up -d
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the System
Double-click **`start_system.bat`** (Windows) or run:
```batch
start_system.bat
```
This will launch 3 windows:
1.  **Worker**: Consumes tweets, cleans them, and saves to DB.
2.  **Analyzer**: Runs periodic jobs (Clustering, Bot Detection, Graph).
3.  **Dashboard**: Opens the web UI.

### 5. Feed Data (Simulation)
To test the system without waiting for live scrapes:
```bash
python scripts/simulate_traffic.py
```
This will push synthetic "organic" and "bot attack" tweets into the pipeline.
Watch the Dashboard "Live Feed" and "Narrative Analysis" tabs update!

## 🧩 Architecture

*   **Ingestion**: `scrp*.py` -> Redis Stream `tweets:micro`.
*   **Processing**: `app/worker.py` -> Cleans text -> Generates Embeddings -> Postgres.
*   **Analysis**: `app/services/analyzer.py` -> Runs every 1-5 mins:
    *   **Clustering**: HDBSCAN on vector embeddings.
    *   **Bot Detection**: Heuristic scoring (Age, Ratio, Repetition).
    *   **Coordination**: Detects identical text/time patterns.
*   **Visualization**: Streamlit Dashboard querying Postgres.

## 📂 Key Files
*   `dashboard.py`: The frontend.
*   `app/worker.py`: The data processor.
*   `app/services/analyzer.py`: The intelligence brain.
*   `scripts/simulate_traffic.py`: Test data generator.
