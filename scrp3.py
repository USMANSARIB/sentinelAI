import time
import json
import os
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import config
from db_client import SentinelDB



def profile_user(target_handle: str, db: SentinelDB):
    from browser_lock import BrowserLock
    print(f"[*] SentinelGraph Layer 3 -- Hourly Profiler (Triggered for: '{target_handle}')")

    try:
        with BrowserLock(timeout=120) as lock:
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=config.SESSION_DIR,
                    headless=False,
                    slow_mo=80,
                    viewport={'width': 1280, 'height': 800},
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                try:
                    data = _internal_profile_logic(context, target_handle, db)
                finally:
                    context.close()
                return data

    except Exception as e:
        print(f"[ERROR] Profiler Lock/Launch failed: {e}")
        return None

def _internal_profile_logic(context, target_handle, db):
    start_time = time.time()
    page = context.pages[0] if context.pages else context.new_page()

    # Block heavy assets
    page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["font", "media"] else r.continue_())

    # ------------------------------
    # GO TO USER PROFILE PAGE
    # ------------------------------
    profile_url = f"https://x.com/{target_handle.replace('@','')}"
    print(f"[*] Visiting: {profile_url}")
    page.goto(profile_url)

    try:
        page.wait_for_selector("div[data-testid='UserProfileHeader_Items']", timeout=15000)
    except:
        print(f"[ERROR] Could not load profile header for {target_handle}.")
        return None

    # ------------------------------
    # Extract Profile Header Section
    header_items = page.query_selector("div[data-testid='UserProfileHeader_Items']")
    
    # Bio
    try:
        bio_el = page.query_selector("div[data-testid='UserDescription']")
        bio = bio_el.inner_text() if bio_el else None
    except:
        bio = None

    # Location + URL in bio
    location = None
    url_in_bio = None

    if header_items:
        parts = header_items.inner_text().split("\n")
        for part in parts:
            if "Joined" in part:
                join_date_str = part
            elif part.startswith("http"):
                url_in_bio = part
            else:
                if location is None and not part.startswith("@"):
                    location = part

    # Join Date
    join_date_str = None
    try:
        join_el = page.query_selector("span:has-text('Joined')")
        join_date_str = join_el.inner_text() if join_el else None
    except:
        join_date_str = None

    # Stats
    stats = {"followers": None, "following": None, "tweet_count": None}
    try:
        stat_items = page.query_selector_all("a[href$='/following'], a[href$='/followers']")
        for item in stat_items:
            txt = item.inner_text()
            if "Followers" in txt:
                stats["followers"] = txt.split(" ")[0].replace(",", "")
            elif "Following" in txt:
                stats["following"] = txt.split(" ")[0].replace(",", "")
    except: pass

    # Tweet count
    try:
        count_el = page.query_selector("div[data-testid='primaryColumn'] h2 + div span")
        if count_el:
            count_text = count_el.inner_text()
            if "posts" in count_text or "Tweets" in count_text:
                stats["tweet_count"] = count_text.split(" ")[0].replace(",", "")
    except:
        stats["tweet_count"] = None
        
    # Verified?
    is_verified = bool(page.query_selector("svg[data-testid='icon-verified']"))

    # Default profile image?
    has_default_pfp = False
    try:
        img_el = page.query_selector("img[src*='profile_images']")
        if img_el:
            src = img_el.get_attribute("src")
            if src and "default_profile" in src:
                has_default_pfp = True
    except: pass

    # ------------------------------
    # BUILD REPORT OBJECT
    # ------------------------------
    profile_data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "target_handle": f"@{target_handle.replace('@','')}",
        "scan_duration_ms": int((time.time() - start_time) * 1000),
        "bio": bio,
        "location": location,
        "url_in_bio": url_in_bio,
        "join_date_str": join_date_str,
        "followers": stats["followers"],
        "following": stats["following"],
        "tweet_count": stats["tweet_count"],
        "is_verified": is_verified,
        "has_default_profile_image": has_default_pfp
    }

    # Log Alert
    alert_description = f"Profiled user {profile_data['target_handle']}: Followers: {profile_data['followers']}, Following: {profile_data['following']}, Tweets: {profile_data['tweet_count']}."
    db.log_alert(datetime.now(timezone.utc).isoformat(), "PROFILE_ANALYSIS", alert_description, "INFO")

    # SAVE TO JSON
    if profile_data:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hourly_{timestamp_str}.json"
        save_dir = os.path.join("data", "raw_json")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        ingest_ready = {
            "tweet_id": f"profile_{profile_data['target_handle'].replace('@','')}_{timestamp_str}",
            "handle": profile_data['target_handle'],
            "text_raw": profile_data['bio'] or f"Profile refresh for {profile_data['target_handle']}",
            "timestamp_absolute": profile_data['timestamp_utc']
        }
        
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([ingest_ready], f, indent=2)
        
        print(f"[OK] Saved profile snapshot for {profile_data['target_handle']} to {filepath}")

    print(f"\n[OK] Layer 3 Profile for '{target_handle}' logged to alerts.")
    return profile_data

def run_continuous_scraper_l3():
    print("--------------------------------------------------")
    print("   SENTINEL GRAPH - HOURLY PROFILER ONLINE")
    print("--------------------------------------------------")
    db_client = SentinelDB()
    interval = 3600  # 1 hour
    
    # In a real scenario, we might pull recent influential users from DB
    # targets = ["imVkohli", "narendramodi", "elonmusk"] # DEPRECATED: Static List
    
    while True:
        try:
            # 1. Pop highest priority suspect from Redis
            # zpopmax returns list of tuples: [(member, score), ...]
            suspect = db_client.redis.zpopmax(config.REDIS_SUSPECT_QUEUE_KEY)
            
            if not suspect:
                print(f"[*] Queue empty. Sentinel Watchlist is clean. Sleeping for {interval}s...")
                time.sleep(interval)
                continue
            
            target_handle, score = suspect[0]
            print(f"\n[NEXT TARGET] Discovered Suspect: {target_handle} (Risk Score: {score})")

            # 2. Profile User
            profile_user(target_handle, db_client)
            
            # 3. Dynamic Sleep? 
            # If queue is full, maybe sleep less?
            # For now, let's sleep 2 minutes between profiles to be safe but faster than hourly
            time.sleep(120) 

        except Exception as e:
            print(f"[ERROR] Profiler L3 loop failed: {e}")
            time.sleep(60)

# This part is for standalone testing if needed
if __name__ == "__main__":
    run_continuous_scraper_l3()
