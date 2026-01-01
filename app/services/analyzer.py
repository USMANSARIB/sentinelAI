import time
import schedule
import sys
import os
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from app.models import engine, User, Tweet
from app.detection.clustering import detect_narratives
from app.detection.bot_detector import BotDetector
from app.detection.coordination import CoordinationDetector
from app.detection.community import build_graph_and_detect
from app.detection.origin import NarrativeAnalyzer
from app.services.url_expander import expand_urls_sync

Session = sessionmaker(bind=engine)

def job_clustering():
    print("\n[ANALYZER] Running Clustering Job...")
    try:
        detect_narratives()
    except Exception as e:
        print(f"[ERROR] Clustering failed: {e}")

def job_bot_scoring():
    print("\n[ANALYZER] Running Bot Scoring Job...")
    session = Session()
    detector = BotDetector()
    
    # Score users with no label (indicates unscored)
    users = session.query(User).filter(User.bot_label == None).limit(100).all()
    print(f"[ANALYZER] Scoring {len(users)} new users...")
    
    for user in users:
        try:
            score, label, details = detector.score_user(user, session)
            user.bot_score = score
            user.bot_label = label 
            # user.bot_details = details # If we add JSON column
            session.add(user)
        except Exception as e:
            print(f"[ERROR] Failed to score user {user.user_id}: {e}")
            
    session.commit()
    session.close()

def job_url_expansion():
    print("\n[ANALYZER] Running URL Expansion Job...")
    session = Session()
    try:
        # Fetch tweets with URLs but no expanded_urls
        # Note: Postgres Array check might need specific syntax, using simple non-empty check
        tweets = session.query(Tweet).filter(Tweet.urls != None).filter(Tweet.expanded_urls == None).limit(50).all()
        
        if not tweets:
            print("[ANALYZER] No URLs to expand.")
            session.close()
            return

        all_urls = []
        for t in tweets:
            if t.urls:
                all_urls.extend(t.urls)
        
        # Deduplicate
        unique_urls = list(set(all_urls))
        if not unique_urls:
             session.close()
             return

        print(f"[ANALYZER] Expanding {len(unique_urls)} URLs...")
        results = expand_urls_sync(unique_urls)
        
        # Map back
        url_map = {res['final_url']: res for res in results} # Logic error in key? 
        # Result key logic in expander was: 'final_url' is the expanded. 
        # The expander returns list of dicts. 
        # I need to know which short url maps to which result.
        # Check expander logic: 
        # cache_key = f"url:{short_url}" ... 
        # return result (which contains final_url). 
        # Wait, the result dict doesn't explicitly have 'original_url' if successful. 
        # Error result DOES have 'final_url': short_url.
        # Actually expander returns result dict. 
        # I should assume order is preserved in `process_batch` (asyncio.gather preserves order).
        
        url_results_map = dict(zip(unique_urls, results))

        count = 0
        for t in tweets:
            if t.urls:
                expanded_list = []
                for u in t.urls:
                    res = url_results_map.get(u)
                    if res and 'final_url' in res:
                        expanded_list.append(res['final_url'])
                    else:
                        expanded_list.append(u) # Fallback
                t.expanded_urls = expanded_list
                
                # --- LAYER 3 FEEDER (Fake URL) ---
                # Simple check for illustration
                for url in expanded_list:
                    if "fake" in url or "scam" in url or "phishing" in url: # Mock logic
                        try:
                            import redis
                            r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
                            r.zincrby(config.REDIS_SUSPECT_QUEUE_KEY, 40, t.handle)
                            print(f"      [L3] Flagged {t.handle} for suspicious URL: {url}")
                        except: pass

                count += 1
        
        session.commit()
        print(f"[ANALYZER] Updated {count} tweets with expanded URLs.")

    except Exception as e:
        print(f"[ERROR] URL Expansion failed: {e}")
    finally:
        session.close()

def job_coordination():
    print("\n[ANALYZER] Running Coordination Detection...")
    session = Session()
    detector = CoordinationDetector(time_window_minutes=15)
    
    # Fetch recent tweets
    # recent_tweets = session.query(Tweet).filter(Tweet.created_at > ...).all()
    # For MVP, just last 1000
    tweets = session.query(Tweet).order_by(Tweet.timestamp_absolute.desc()).limit(1000).all()
    
    try:
        clusters = detector.detect_coordination(tweets)
        print(f"[ANALYZER] Detected {len(clusters)} coordination clusters.")
        # Store clusters in DB? 
        # For now just log
        for c in clusters:
            print(f"   - Type: {c['type']}, Users: {len(c['users'])}, Span: {c['time_span_seconds']}s")
            
    except Exception as e:
        print(f"[ERROR] Coordination detection failed: {e}")
    session.close()

def job_graph():
    print("\n[ANALYZER] Running Community Graph Detection...")
    try:
        results = build_graph_and_detect()
        if results:
            print(f"[ANALYZER] Stored {len(results)} community records (simulated).")
    except Exception as e:
        print(f"[ERROR] Graph analysis failed: {e}")

def run_analyzer():
    print("[SYSTEM] SentinelGraph Analyzer Service Started.")
    
    # Schedule jobs
    schedule.every(1).minutes.do(job_clustering)
    schedule.every(2).minutes.do(job_bot_scoring)
    schedule.every(3).minutes.do(job_url_expansion)
    schedule.every(5).minutes.do(job_coordination)
    schedule.every(10).minutes.do(job_graph)
    
    # Run once on startup
    job_clustering()
    job_bot_scoring()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_analyzer()

