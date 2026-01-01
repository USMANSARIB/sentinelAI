@echo off
echo ========================================
echo   TESTING SENTINELGRAPH INGESTION
echo ========================================
echo.

echo [Step 1/3] Checking if Docker is running...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running!
    echo.
    echo Please start Docker Desktop and run this again.
    echo Then run: docker-compose up -d
    pause
    exit /b 1
)
echo ✓ Docker is running

echo.
echo [Step 2/3] Checking if infrastructure is up...
docker-compose ps | findstr "sentinel_db" >nul
if errorlevel 1 (
    echo ⚠ Infrastructure not running
    echo Starting PostgreSQL and Redis...
    docker-compose up -d
    timeout /t 5 >nul
)
echo ✓ Infrastructure is ready

echo.
echo [Step 3/3] Verifying database ingestion...
python verify_ingestion.py

echo.
echo ========================================
echo.
echo Next steps:
echo   1. Run: start_system.bat  (to start all services)
echo   2. Run: python scripts/simulate_traffic.py  (to test)
echo.
pause
