import redis
import json
import time
import random
import uuid
import sys
import os
from datetime import datetime

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def generate_tweet(scenario="normal"):
    tweet_id = str(uuid.uuid4())
    
    if scenario == "normal":
        user = f"user_{random.randint(1, 100)}"
        topics = ["Virat Kohli is great!", "Watching the match #cricket", "Kohli stats are insane", "India vs Aus today"]
        text = random.choice(topics) + " " + str(random.randint(1, 1000))
        hashtags = ["cricket", "kohli"]
        
    elif scenario == "bot_attack":
        user = f"bot_{random.randint(500, 600)}"
        text = "URGENT: Crypto collapse imminent! Withdraw now! http://scam.ly/coin"
        hashtags = ["crypto", "scam", "bitcoin"]
    
    return {
        "tweet_id": tweet_id,
        "handle": user,
        "text_raw": text,
        "text_clean": text.lower(), # Simplified for simulation
        "text_hash": str(hash(text)),
        "hashtags": hashtags,
        "mentions": [],
        "urls": [],
        "timestamp_absolute": datetime.now().isoformat()
    }

def simulate():
    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)
    try:
        r.ping()
        print(f"Connected to Redis at {config.REDIS_PORT}")
    except Exception as e:
        print(f"Redis connect failed: {e}")
        return

    print("Starting Traffic Simulation (Ctrl+C to stop)...")
    
    count = 0
    try:
        while True:
            # Generate Batch
            scenario = "bot_attack" if random.random() < 0.3 else "normal"
            tweet = generate_tweet(scenario)
            
            # Redis XADD expects dict of strings
            payload = {k: str(v) for k, v in tweet.items()}
            
            r.xadd(config.REDIS_STREAM_KEY, payload)
            
            count += 1
            if count % 10 == 0:
                print(f"Pushed {count} tweets... (Last: {scenario})")
            
            time.sleep(0.1) # 10 tweets/sec
            
    except KeyboardInterrupt:
        print("Simulation stopped.")

if __name__ == "__main__":
    simulate()
