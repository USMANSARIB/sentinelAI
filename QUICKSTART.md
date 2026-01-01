# SentinelGraph - Quick Start Guide

## 🚀 Complete Setup Instructions

### Step 1: Start Infrastructure
```bash
# Make sure Docker Desktop is running, then:
docker-compose up -d
```

This starts:
- PostgreSQL with pgvector (port 5433)
- Redis (port 6380)

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Start the System
```batch
# Windows
start_system.bat
```

This launches 4 services:
1. **Ingest Service** - Watches `data/raw_json/` and pushes to Redis
2. **Worker** - Consumes Redis stream, generates embeddings, saves to PostgreSQL
3. **Analyzer** - Runs clustering, bot detection, etc.
4. **Dashboard** - Web UI at http://localhost:8000

### Step 4: Verify Ingestion
```bash
python verify_ingestion.py
```

### Step 5: Feed Data

**Option A: Run Scrapers** (requires Twitter login session)
```bash
# Terminal 1
python scrp1.py

# Terminal 2  
python scrp2.py
```

**Option B: Simulate Traffic** (no login needed)
```bash
python scripts/simulate_traffic.py
```

## 🔍 Troubleshooting

**Problem**: No tweets in database
- Check Docker is running: `docker ps`
- Verify ingest service is watching folder
- Check worker is consuming Redis: Look for "[WORKER] Saved X tweets"

**Problem**: Database connection error
- Ensure Docker containers are up: `docker-compose up -d`
- Check ports 5433 (Postgres) and 6380 (Redis) are free

## 📊 System Architecture

```
Scrapers (scrp*.py)
  ↓ Save JSON files
data/raw_json/
  ↓ Watched by
Ingest Service (scripts/ingest.py)
  ↓ Push to
Redis Stream (stream:tweets)
  ↓ Consumed by
Worker (app/worker.py)
  ↓ Process & Save to
PostgreSQL
  ↓ Analyzed by
Analyzer (app/services/analyzer.py)
  ↓ Displayed in
Dashboard (http://localhost:8000)
```

## 📁 Key Files

- `config.py` - Configuration (Redis, PostgreSQL, search queries)
- `start_system.bat` - Launch all services
- `verify_ingestion.py` - Check if tweets are in database
- `app/worker.py` - Main ingestion pipeline
- `app/services/analyzer.py` - Intelligence analysis
- `docker-compose.yml` - Infrastructure setup
