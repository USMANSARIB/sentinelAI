# 🦅 SentinelGraph
> **Real-Time Narrative Detection & Anti-Disinformation System**

SentinelGraph is an advanced OSINT and analytics platform designed to detect coordinated inauthentic behavior (CIB), track narrative origins, and identify bot networks on X (Twitter) in real-time.

## 🚀 Key Features

*   **Ingestion Pipeline**: Multi-layer Redis streams (Micro/Minute/Hourly) handling high-throughput tweet data from distributed Playwright scrapers.
*   **Bot Detection**: Heuristic-based scoring engine analyzing account age, post frequency, follower ratios, and username entropy.
*   **Coordination Analysis**: Sliding-window detection of exact text matches (copypasta) and semantic similarity clusters using vector embeddings.
*   **Community Graph**: Graph-based detection of bot clusters using the Louvain algorithm on interaction (retweet/mention) and content similarity edges.
*   **Origin Tracing**: "Patient Zero" identification to pinpoint the exact start time and author of a viral narrative.
*   **Risk Advisory**: Automated risk scoring and strategic response generation (e.g., "Ignore," "Monitor," "Debunk") based on attack velocity and bot composition.
*   **Dashboard**: Real-time FastAPI web interface for monitoring narratives and threats.

---

## 🛠️ Architecture

The system follows a microservices-like architecture:

1.  **Scrapers (`scrp*.py`)**: Headless browsers collecting tweets and pushing to `tweets:micro` Redis stream.
2.  **Ingestion Worker (`app/worker.py`)**: Consumes streams, cleans text, generates embeddings (SentenceTransformers), and persists to PostgreSQL.
3.  **Analyzer Service (`app/services/analyzer.py`)**: Background job runner performing:
    *   Bot Scoring
    *   Coordination Detection
    *   URL Unshortening & Threat Checking
    *   Community Graph Analysis
4.  **API Layer (`app/main.py`)**: FastAPI server exposing analytics endpoints.
5.  **Storage**:
    *   **PostgreSQL**: Relational data + `pgvector` for semantic search.
    *   **Redis**: Hot caching and stream buffering.

---

## 🏁 Quick Start

### 1. Prerequisites
*   **Docker Desktop** (for Redis & PostgreSQL)
*   **Python 3.10+** (with `pip`)
*   **Google Chrome** (for Playwright)

### 2. Setup Infrastructure
Start the database and cache layers:
```powershell
docker-compose up -d
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
playwright install chromium
```

### 4. Initialize Database
Ensure the database schema is created:
```powershell
python -c "from app.models import init_db; init_db()"
```

### 5. Run the System
Use the automated startup script to launch all components (API, Worker, Scrapers):

**Windows:**
```batch
start_system.bat
```

**Manual Start:**
1.  **API**: `uvicorn app.main:app --reload`
2.  **Worker**: `python app/worker.py`
3.  **Analyzer**: `python app/services/analyzer.py`

---

## 🧪 Testing

The system includes a comprehensive integration test suite validating every step of the pipeline.

**Run All Integration Tests:**
```powershell
python -m unittest discover tests "integration_test_*.py"
```

### Test Coverage:
*   `integration_test_01`: Ingestion Pipeline (Redis → DB)
*   `integration_test_02`: Bot Detection Logic
*   `integration_test_03`: Coordination & Semantic Clustering
*   `integration_test_04`: URL Expansion & Threat Intel
*   `integration_test_05`: Community Graph Detection
*   `integration_test_06`: Origin Tracing
*   `integration_test_07`: Risk Scoring & Advisory
*   `integration_test_08`: API Endpoints

---

## 📚 API Documentation

Once the system is running, access the interactive API docs at:
**`http://localhost:8000/docs`**

### Key Endpoints:
*   `GET /api/narratives`: List active narratives with spike velocity.
*   `GET /api/narratives/{id}/origin`: Trace a narrative to its source.
*   `GET /api/narratives/{id}/advice`: Get strategic risk assessment.
*   `GET /api/users/{handle}`: Get bot score and account analysis.
*   `GET /api/communities`: View detected bot clusters and groups.

---

## 🛡️ License
Private & Confidential - SentinelGraph Team
