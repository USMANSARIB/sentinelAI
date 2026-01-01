import time
import json
import redis
import os
import sys
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from app.models import Tweet, User, engine, init_db
from app.services.cleaner import clean_tweet
from sentence_transformers import SentenceTransformer

# Initialize DB tables
init_db()
Session = sessionmaker(bind=engine)

# Load ML Model (Global to avoid reload)
print("[WORKER] Loading Embedding Model (all-MiniLM-L6-v2)...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("[WORKER] Model Loaded.")

def run_worker():
    # 1. Connect to Redis
    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)
    try:
        r.ping()
        print("[WORKER] Connected to Redis.")
    except Exception as e:
        print(f"[WORKER] Redis Connection Failed: {e}")
        return

    # 2. Worker Loop Setup
    print("[WORKER] Multi-stream consumer starting (MICRO, MINUTE, HOURLY)...")
    
    # We'll listen to all three vision-defined streams + the default one
    # Use '0-0' to start from the beginning of the stream (process backlog)
    streams = {
        config.REDIS_STREAM_MICRO: '0-0',
        config.REDIS_STREAM_MINUTE: '0-0',
        config.REDIS_STREAM_HOURLY: '0-0',
        config.REDIS_STREAM_KEY: '0-0'
    }
    
    BATCH_SIZE = 100 # Target throughput as per Step 3
    
    while True:
        try:
            # Read from all streams
            response = r.xread(streams, count=BATCH_SIZE, block=2000)
            
            if not response:
                continue
                
            session = Session()
            processed_tweets = []
            
            # Temporary storage to deduplicate within the current batch
            unique_items = {}

            # Response structure: [[stream, [entries]], ...]
            for stream_key, entries in response:
                # Update the stream ID to the last processed message ID to avoid reprocessing
                # and to ensure we get the next batch correctly
                if entries:
                    streams[stream_key] = entries[-1][0]

                for msg_id, data in entries:
                    try:
                        # 1. Clean and process (Step 3 Cleaning Pipeline)
                        processed = clean_tweet(data)
                        
                        # Add layer info if not present
                        if 'layer' not in processed:
                            processed['layer'] = stream_key.split(':')[-1].upper()

                        # Keep the latest version of a tweet if they appear multiple times in the batch
                        unique_items[processed['tweet_id']] = processed
                        
                    except Exception as e:
                        print(f"[ERROR] processing msg {msg_id} from {stream_key}: {e}")


            if not unique_items:
                session.close()
                continue

            # 2. Generate Embeddings (Batch)
            temp_data_list = list(unique_items.values())
            batch_texts = [p['text_clean'] or "" for p in temp_data_list]
            embeddings = embedding_model.encode(batch_texts)
            
            # 3. Save to PostgreSQL (Step 3 Database Operations)
            for idx, processed in enumerate(temp_data_list):
                try:
                    # UPSERT USER
                    user_stub = User(
                        user_id=processed['handle'], 
                        handle=processed['handle']
                    )
                    session.merge(user_stub)

                    # CREATE TWEET
                    tweet = Tweet(
                        tweet_id=processed['tweet_id'],
                        handle=processed['handle'],
                        user_id=processed['handle'], 
                        text_raw=processed['text_raw'],
                        text_clean=processed['text_clean'],
                        text_hash=processed['text_hash'],
                        hashtags=processed['hashtags'],
                        mentions=processed['mentions'],
                        urls=processed['urls'],
                        timestamp_absolute=processed['timestamp_absolute'],
                        embedding=embeddings[idx].tolist() if len(embeddings) > idx else None
                    )
                    session.merge(tweet)
                    processed_tweets.append(tweet)
                except Exception as e:
                    print(f"[ERROR] Failed to merge tweet {processed['tweet_id']}: {e}")

            if processed_tweets:
                try:
                    session.commit()
                    print(f"[WORKER] Batched {len(processed_tweets)} tweets to Postgres.")
                except Exception as e:
                    session.rollback()
                    print(f"[ERROR] Batch commit failed for {len(processed_tweets)} tweets: {e}")
                    import traceback
                    traceback.print_exc()
            
            session.close()
            
        except Exception as e:
            print(f"[CRITICAL] Worker Loop Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_worker()
