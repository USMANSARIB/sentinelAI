import time
import sys
import os
import glob
import redis
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrp1 import run_simple_scraper_once
from scrp2 import analyze_narrative
from scrp3 import profile_user
from db_client import SentinelDB
import config

def cleanup_old_json_files(max_age_hours=1):
    """Remove processed JSON files older than max_age_hours"""
    json_dir = os.path.join("data", "raw_json")
    if not os.path.exists(json_dir):
        return 0
    
    removed = 0
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    
    for filepath in glob.glob(os.path.join(json_dir, "*.json")):
        try:
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_mtime < cutoff:
                os.remove(filepath)
                removed += 1
        except Exception as e:
            print(f"[CLEANUP] Error removing {filepath}: {e}")
    
    if removed > 0:
        print(f"[CLEANUP] Removed {removed} old JSON files")
    return removed

def cleanup_redis_duplicates():
    """Trim the Redis duplicate set to prevent memory bloat"""
    try:
        r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
        dupe_count = r.scard(config.REDIS_DUPE_SET_KEY)
        
        # If we have too many tracked IDs, keep only the most recent ones
        # (Note: Sets don't have order, so this is a rough cleanup)
        if dupe_count > 10000:
            # For simplicity, we clear old entries by removing the set 
            # and letting it rebuild with fresh scrapes
            r.delete(config.REDIS_DUPE_SET_KEY)
            print(f"[CLEANUP] Reset duplicate tracking set (was {dupe_count} entries)")
    except Exception as e:
        print(f"[CLEANUP] Redis cleanup error: {e}")

def main():
    print("==================================================")
    print("   SENTINEL SQUAD ORCHESTRATOR (End-to-End)")
    print("==================================================")
    
    # Pre-emptive cleanup of browser locks to prevent launch failures
    lock_file = os.path.join(config.SESSION_DIR, "lockfile")
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            print("[SQUAD] Removed stale browser lockfile.")
        except:
            pass

    db = SentinelDB()
    
    # Configuration
    LAST_DEEP_DIVE = 0
    DEEP_DIVE_INTERVAL = 600 # 10 mins
    
    LAST_PROFILE = 0
    PROFILE_INTERVAL = 3600 # 1 hour
    
    PROFILE_TARGETS = ["imVkohli", "elonmusk", "narendramodi"]
    profile_idx = 0

    while True:
        try:
            # 1. Micro Scout (scrp1)
            print("\n[*] [SQUAD] Triggering Micro Scout (Scraper 1)...")
            run_simple_scraper_once(config.DEFAULT_SEARCH_QUERY)
            
            # 2. Minute Analyst (scrp2) - Check every 10 mins
            now = time.time()
            if now - LAST_DEEP_DIVE > DEEP_DIVE_INTERVAL:
                print("\n[*] [SQUAD] Triggering Minute Analyst Deep Dive (Scraper 2)...")
                analyze_narrative(config.DEFAULT_SEARCH_QUERY, db)
                LAST_DEEP_DIVE = time.time()
            
            # 3. Hourly Profiler (scrp3) - Check every hour
            if now - LAST_PROFILE > PROFILE_INTERVAL:
                target = PROFILE_TARGETS[profile_idx % len(PROFILE_TARGETS)]
                print(f"\n[*] [SQUAD] Triggering Hourly Profile for {target} (Scraper 3)...")
                profile_user(target, db)
                profile_idx += 1
                LAST_PROFILE = time.time()

            # 4. Periodic Cleanup (every cycle)
            cleanup_old_json_files(max_age_hours=1)
            cleanup_redis_duplicates()

            print("\n[OK] Squad cycle complete. Sleeping for 60s...")
            time.sleep(60)

        except Exception as e:
            print(f"\n[CRITICAL ERROR] Squad Orchestrator Error: {e}")
            print("[*] Retrying in 30s...")
            time.sleep(30)

if __name__ == "__main__":
    main()
