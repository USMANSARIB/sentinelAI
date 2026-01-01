import time
import json
import random
import os
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import config
from db_client import SentinelDB

# --- CONFIGURATION ---
SEARCH_QUERY = config.DEFAULT_SEARCH_QUERY
SESSION_DIR = config.SESSION_DIR
LOOP_INTERVAL_SECONDS = 60  # Check every 60 seconds

from app.services.smart_scheduler import SmartOrchestrator

def run_simple_scraper_once(query):
    print(f"[*] SentinelGraph Micro Scout (Pulse Check)...")
    print(f"[*] Target: '{query}'")
    
    # Initialize DB Connection
    try:
        db = SentinelDB()
    except Exception as e:
        print(f"[ERROR] DB Init Failed: {e}")
        return 0

    from browser_lock import BrowserLock
    
    try:
        with BrowserLock(timeout=30) as lock:
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=SESSION_DIR,
                    headless=False,
                    slow_mo=100,
                    viewport={'width': 1280, 'height': 800},
                    args=["--disable-blink-features=AutomationControlled", "--disable-infobars"]
                )
                
                try:
                    count = _internal_scrape_logic(context, query, db)
                finally:
                    context.close()
                return count

    except TimeoutError:
        print("[LOCK] Micro Scout yielded lock to other agents.")
        return 0
    except Exception as e:
        print(f"[ERROR] Micro Scout failed: {e}")
        return 0

def _internal_scrape_logic(context, query, db):
    page = context.pages[0] if context.pages else context.new_page()

    # 2. Turbo Mode (block images, fonts, media)
    page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font"] else r.continue_())

    # 3. Go directly to search
    page.goto(f"https://x.com/search?q={query}&src=typed_query&f=live")
    
    try:
        page.wait_for_selector("article", timeout=15000)
    except:
        print("[WARN] No results found.")
        return 0

    # Scroll once (micro scroll)
    page.mouse.wheel(0, 2000)
    time.sleep(2)
    
    tweets = page.query_selector_all("article[data-testid='tweet']")

    # Extract
    count_new = 0
    extracted_sparks = []
    
    for tweet in tweets[:15]: 
        try:
            # --- Extract Timestamp & ID First to check Dupe ---
            tweet_id = f"gen_{random.randint(1000,9999)}"
            absolute_timestamp = None
            
            time_el = tweet.query_selector("time")
            if time_el:
                link = tweet.query_selector("a[href*='/status/']")
                if link:
                    url = link.get_attribute("href")
                    tweet_id = url.split("/status/")[-1]
                    absolute_timestamp = time_el.get_attribute("datetime")

            # --- DUPLICATE CHECK ---
            if db.is_duplicate(tweet_id):
                continue

            # --- Extract Rest ---
            text_el = tweet.query_selector("div[data-testid='tweetText']")
            if not text_el: continue
            text = text_el.inner_text()

            user_el = tweet.query_selector("div[data-testid='User-Name']")
            user_text = user_el.inner_text().split('\n')
            handle = user_text[1] if len(user_text) > 1 else "Unknown"

            relative_timestamp = time_el.inner_text() if time_el else "Unknown"

            # --- COLLECT FOR BATCH SAVE ---
            spark = {
                "tweet_id": tweet_id,
                "handle": handle,
                "text_raw": text,
                "timestamp_relative": relative_timestamp,
                "timestamp_absolute": absolute_timestamp or datetime.now(timezone.utc).isoformat(),
                "query_source": query
            }

            extracted_sparks.append(spark)
            print(f"   -> [EXTRACTED]: {handle} ({tweet_id})")

            count_new += 1

        except Exception as e:
            continue
    
    # --- BATCH SAVE TO JSON ---
    if extracted_sparks:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"micro_{timestamp_str}.json"
        save_dir = os.path.join("data", "raw_json")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(extracted_sparks, f, indent=2)
        
        print(f"[OK] Saved {len(extracted_sparks)} tweets to {filepath}")
    else:
        print("[OK] Pass Complete. No new tweets to save.")

    return count_new


def run_continuous_scraper():
    print("--------------------------------------------------")
    print("   SENTINEL GRAPH - SMART ORCHESTRATOR ONLINE")
    print("--------------------------------------------------")
    
    scheduler = SmartOrchestrator()

    while True:
        found_count = 0
        try:
            target = scheduler.get_next_target()
            if not target:
                print("[!] No targets available. Check config. Sleeping...")
                time.sleep(10)
                continue

            print(f"\n[NEXT MISSION] Target: {target.term} | Bucket: {target.bucket} | Priority: {target.current_multiplier:.2f}x")
            
            # Execute Scrape
            found_count = run_simple_scraper_once(target.term)
            
            # Feedback Loop
            scheduler.feedback(target.term, found_count)

        except Exception as e:
            print(f"[CRITICAL ERROR] Orchestrator crashed: {e}")
            import traceback
            traceback.print_exc()
        
        # Dynamic sleep based on urgency? 
        # For now, stick to interval but maybe slightly randomized or reduced if hot?
        # Let's keep a base interval but allow it to speed up.
        
        sleep_time = LOOP_INTERVAL_SECONDS
        if found_count > 5:
            sleep_time = LOOP_INTERVAL_SECONDS / 2 # Speed up if we found stuff
            print(f"[*] High Velocity Detected. Accelerating next cycle.")

        print(f"[*] Cooling down for {sleep_time}s...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    run_continuous_scraper()