@echo off
echo ==========================================
echo    LAUNCHING SENTINEL SCRAPER SQUAD
echo ==========================================
echo.
echo Running Squad Orchestrator (Sequentially):
echo 1. Micro Scout (Scraper 1) - Every cycle
echo 2. Minute Analyst (Scraper 2) - Every 10 mins
echo 3. Hourly Profiler (Scraper 3) - Every hour
echo.
echo Note: This avoids session lock issues.
echo.

python run_squad.py

pause
