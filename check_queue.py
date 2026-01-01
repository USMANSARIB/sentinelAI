import redis
import config

try:
    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)
    
    print("\n--- SENTINEL WATCHLIST (Suspect Queue) ---")
    
    # Get top 10 suspects
    suspects = r.zrange(config.REDIS_SUSPECT_QUEUE_KEY, 0, -1, desc=True, withscores=True)
    
    if not suspects:
        print("[!] Queue is empty. Scraper 1 might not have found anyone yet.")
    else:
        for i, (handle, score) in enumerate(suspects[:10]):
            print(f"{i+1}. {handle} - Score: {score}")

    print(f"\n[INFO] Total Suspects in Queue: {r.zcard(config.REDIS_SUSPECT_QUEUE_KEY)}")

except Exception as e:
    print(f"[ERROR] Verification failed: {e}")
