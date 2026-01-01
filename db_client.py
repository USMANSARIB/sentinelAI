import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import json
import time
from datetime import datetime
import config

class SentinelDB:
    def __init__(self):
        # 1. Initialize Redis
        try:
            self.redis = redis.Redis(
                host=config.REDIS_HOST, 
                port=config.REDIS_PORT, 
                db=config.REDIS_DB, 
                decode_responses=True
            )
            self.redis.ping() # Check connection
            print("[OK] Connected to Redis (The Nerve Center)")
        except redis.ConnectionError:
            print("[ERROR] Redis Connection Failed! Ensure Docker/Redis is running on port 6379.")
            raise

        # 2. Initialize PostgreSQL
        try:
            self.conn = psycopg2.connect(
                host=config.PG_HOST,
                port=config.PG_PORT,
                dbname=config.PG_DB,
                user=config.PG_USER,
                password=config.PG_PASS
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            self._init_postgres_tables()
            print(f"[OK] Connected to PostgreSQL ({config.PG_DB})")
        except Exception as e:
            print(f"[ERROR] PostgreSQL Connection Failed: {e}")
            raise

    def _init_postgres_tables(self):
        # Enable pgvector extension
        self.cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Table: Raw Tweets (The Archive)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tweets (
                tweet_id TEXT PRIMARY KEY,
                handle TEXT,
                text_raw TEXT,
                timestamp_absolute TIMESTAMP,
                ingest_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                embedding vector(384) -- Future proofing for MiniLM-L6-v2
            );
        ''')
        
        # Table: Alerts/Incidents
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                alert_type TEXT,
                description TEXT,
                severity TEXT
            );
        ''')

    # --- REDIS OPERATIONS (HOT PATH) ---
    
    def is_duplicate(self, tweet_id):
        """Checks Redis Set for instant duplicate detection."""
        return self.redis.sismember(config.REDIS_DUPE_SET_KEY, tweet_id)

    def push_to_stream(self, tweet_data):
        """Pushes a fresh tweet to the processing stream."""
        # 1. Add to Dupe Set
        self.redis.sadd(config.REDIS_DUPE_SET_KEY, tweet_data['tweet_id'])
        
        # 2. Add to Stream
        self.redis.xadd(config.REDIS_STREAM_KEY, tweet_data)

    # --- POSTGRES OPERATIONS (COLD PATH) ---

    def archive_tweet(self, tweet_data):
        """Moves data from processing to long-term storage."""
        try:
            # Handle potential None for timestamp
            ts_abs = tweet_data.get('timestamp_absolute')
            
            self.cursor.execute('''
                INSERT INTO tweets (tweet_id, handle, text_raw, timestamp_absolute)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (tweet_id) DO NOTHING
            ''', (
                tweet_data['tweet_id'],
                tweet_data['handle'],
                tweet_data['text_raw'],
                ts_abs
            ))
        except Exception as e:
            print(f"[WARN] Postgres Error: {e}")
            
    def log_alert(self, timestamp, alert_type, description, severity):
        try:
            self.cursor.execute('''
                INSERT INTO alerts (timestamp, alert_type, description, severity)
                VALUES (%s, %s, %s, %s)
            ''', (timestamp, alert_type, description, severity))
        except Exception as e:
            print(f"[WARN] Postgres Alert Error: {e}")

if __name__ == "__main__":
    # Test the connection
    db = SentinelDB()