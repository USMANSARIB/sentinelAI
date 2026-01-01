@echo off
echo ==========================================
echo       STARTING SENTINEL GRAPH
echo ==========================================

echo [1/4] Launching Ingest Service (JSON to Redis)...
start "SG Ingest" cmd /k python scripts/ingest.py

echo [2/4] Launching Data Worker (Redis to Postgres)...
start "SG Worker" cmd /k python app/worker.py

echo [3/4] Launching Analyzer Service...
start "SG Analyzer" cmd /k python app/services/analyzer.py

echo [4/4] Launching Web Dashboard (FastAPI)...
start "SG WebServer" cmd /k python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo ==========================================
echo System is running!
echo.
echo ACCESS DASHBOARD AT: http://localhost:8000
echo.
echo To feed data (if no scrapers running):
echo   python scripts/simulate_traffic.py
echo.
echo To stop: Close the opened windows.
echo ==========================================
pause