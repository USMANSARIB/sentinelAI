import time
import json
import os
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
from collections import Counter
import config
from db_client import SentinelDB

# SCROLL_ROUNDS is now configurable via config.py if needed, or remain local
SCROLL_ROUNDS = 4  

def analyze_narrative(query: str, db: SentinelDB):
    print(f"[*] SentinelGraph Layer 2 -- Minute Analyst (Triggered for: '{query}')")
    
    from browser_lock import BrowserLock
    
    try:
        with BrowserLock(timeout=60) as lock: # Wait up to 60s
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=config.SESSION_DIR,
                    headless=False,
                    slow_mo=80,
                    viewport={'width': 1280, 'height': 800},
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                try:
                    findings = _internal_analyze_logic(context, query, db)
                finally:
                    context.close()
                return findings
                
    except TimeoutError:
        print("[LOCK] Minute Analyst yielded lock.")
        return None
    except Exception as e:
        print(f"[ERROR] Minute Analyst failed: {e}")
        return None

def _internal_analyze_logic(context, query, db):
    start_time = time.time()
    page = context.pages[0] if context.pages else context.new_page()

    # block heavy assets for speed
    page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "font", "media"] else r.continue_())

    print(f"[*] Opening X for deep dive on '{query}'...")
    page.goto(f"https://x.com/search?q={query}&src=typed_query&f=live")
    page.wait_for_timeout(3000)

    # Wait for initial tweets
    try:
        page.wait_for_selector("article", timeout=10000)
    except:
        print("[WARN] No tweets found for deep analysis.")
        return None

    # ----------------------------
    # SCROLL FOR DEEP DATA
    # ----------------------------
    print(f"[*] Deep scroll ({SCROLL_ROUNDS} rounds)...")

    for _ in range(SCROLL_ROUNDS):
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(1500)

    tweets = page.query_selector_all("article[data-testid='tweet']")
    tweets_gathered = len(tweets)
    print(f"   Gathered {tweets_gathered} tweets for analysis.")

    # -------------------------------------------
    # EXTRACT DATA FROM EACH TWEET
    # -------------------------------------------
    batch_data = []

    for tweet in tweets[:50]:  # cap to 50 for performance
        try:
            # text
            text_el = tweet.query_selector("div[data-testid='tweetText']")
            if not text_el: continue
            text = text_el.inner_text()

            # handle
            user_el = tweet.query_selector("div[data-testid='User-Name']")
            user_parts = user_el.inner_text().split("\n")
            handle = user_parts[1] if len(user_parts) > 1 else "Unknown"

            # Tweet ID
            tweet_id = None
            link = tweet.query_selector("a[href*='/status/']")
            if link:
                url = link.get_attribute("href")
                tweet_id = url.split("/status/")[-1]

            # Metrics (likes, replies, retweets)
            def extract_metric(selector):
                el = tweet.query_selector(selector)
                txt = el.inner_text().strip() if el else "0"
                return int(txt) if txt.isdigit() else 0

            replies = extract_metric("div[data-testid='reply']")
            retweets = extract_metric("div[data-testid='retweet']")
            likes = extract_metric("div[data-testid='like']")

            batch_data.append({
                "tweet_id": tweet_id,
                "handle": handle,
                "text_raw": text,
                "timestamp_absolute": datetime.now(timezone.utc).isoformat(),
                "metrics": {
                    "replies": replies,
                    "retweets": retweets,
                    "likes": likes
                }
            })

        except Exception as e:
            continue

    # -------------------------------------------
    # ANALYTICS — Narrative Derivation
    # -------------------------------------------

    all_hashtags = []
    total_engagement = 0
    suspicious_handles = set()

    for item in batch_data:
        words = item["text_raw"].split()
        tags = [w for w in words if w.startswith("#") and len(w) > 1]
        all_hashtags.extend(tags)
        
        total_engagement += item["metrics"]["likes"] + item["metrics"]["retweets"] + item["metrics"]["replies"]

        # Simple bot coordination heuristic
        if item["metrics"]["retweets"] > 50 and item["metrics"]["likes"] < 5:
            suspicious_handles.add(item["handle"])

    hashtag_counts = Counter(all_hashtags)
    top_hashtags = [tag for tag, _ in hashtag_counts.most_common(5)]

    scan_duration_ms = int((time.time() - start_time) * 1000)

    # Report findings to SQLite
    findings = {
        "keyword_targeted": query,
        "tweets_gathered": tweets_gathered,
        "scan_duration_ms": scan_duration_ms,
        "narrative_velocity": f"{total_engagement} engagements across {tweets_gathered} tweets",
        "coordination_signal": "Detected suspicious patterns" if suspicious_handles else "No strong signals",
        "suspicious_handles": list(suspicious_handles),
        "top_related_hashtags": top_hashtags
    }

    # Store a summary in the alerts table
    alert_description = f"Layer 2 Analysis for '{query}': Top # {', '.join(top_hashtags)}. Coordination: {findings['coordination_signal']}. Suspicious: {len(suspicious_handles)} handles."
    severity = "HIGH" if suspicious_handles else "INFO"
    
    db.log_alert(datetime.now(timezone.utc).isoformat(), "NARRATIVE_ANALYSIS", alert_description, severity)
    
    # SAVE TO JSON
    if batch_data:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"minute_{timestamp_str}.json"
        save_dir = os.path.join("data", "raw_json")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, indent=2)
        
        print(f"[OK] Saved {len(batch_data)} tweets to {filepath}")
    
    print(f"\n[OK] Layer 2 Analysis for '{query}' complete. Findings logged.")
    return findings

def run_continuous_scraper_l2():
    print("--------------------------------------------------")
    print("   SENTINEL GRAPH - MINUTE ANALYST ONLINE")
    print("--------------------------------------------------")
    db_client = SentinelDB()
    interval = 300  # 5 minutes
    
    while True:
        try:
            analyze_narrative(config.DEFAULT_SEARCH_QUERY, db_client)
        except Exception as e:
            print(f"[CRITICAL ERROR] Scraper 2 crashed: {e}")
        
        print(f"[*] Sleeping for {interval} seconds...")
        time.sleep(interval)

# This part is for standalone testing if needed
if __name__ == "__main__":
    run_continuous_scraper_l2()
