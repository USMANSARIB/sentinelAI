import os

# --- REDIS CONFIG ---
REDIS_HOST = "localhost"
REDIS_PORT = 6380
REDIS_DB = 0
REDIS_STREAM_KEY = "stream:tweets"
REDIS_STREAM_MICRO = "tweets:micro"
REDIS_STREAM_MINUTE = "tweets:minute"
REDIS_STREAM_HOURLY = "tweets:hourly"
REDIS_DUPE_SET_KEY = "set:seen_tweet_ids"
REDIS_SUSPECT_QUEUE_KEY = "queue:suspects"

# --- POSTGRES CONFIG ---
PG_HOST = "localhost"
PG_PORT = "5433"
PG_DB = "sentinel_core"
PG_USER = "admin"
PG_PASS = "sentinel_pass"

# --- SCRAPER CONFIG ---
SESSION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session_data")
DEFAULT_SEARCH_QUERY = "Virat Kohli"

# --- THRESHOLDS ---
VELOCITY_ALERT_THRESHOLD = 10 # tweets per minute to trigger alert
SENTIMENT_ALERT_THRESHOLD = -0.5 # significantly negative

# --- SMART SCHEDULE BUCKETS ---
KEYWORD_BUCKETS = {
    "Entity: Jio": {
        "priority": 5, 
        "terms": ["jio", "jio down", "jio scam", "jio fiber", "jio risk", "jio outage"]
    },
    "Entity: Virat": {
        "priority": 3,
        "terms": ["virat kohli", "virat rcb", "virat out"]
    },
    "Risk: High": {
        "priority": 10,
        "terms": ["riot", "protest", "attack", "scam alert", "fraud"]
    }
}