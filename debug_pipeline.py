import redis
import sys
import os
from sqlalchemy import create_engine, text
import config

def probe_system():
    print("--- PIPELINE PROBE ---")
    
    # 1. Check Redis
    try:
        r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)
        r.ping()
        stream_len = r.xlen(config.REDIS_STREAM_MICRO)
        print(f"[REDIS] Stream '{config.REDIS_STREAM_MICRO}' Length: {stream_len}")
        
        if stream_len > 0:
            last = r.xrevrange(config.REDIS_STREAM_MICRO, count=1)
            print(f"[REDIS] Last Msg: {last}")
    except Exception as e:
        print(f"[REDIS] Error: {e}")

    # 2. Check Postgres
    try:
        db_url = f"postgresql://{config.PG_USER}:{config.PG_PASS}@{config.PG_HOST}:{config.PG_PORT}/{config.PG_DB}"
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM tweets"))
            count = result.scalar()
            print(f"[DB] Total Tweets: {count}")
            
            if count > 0:
                recent = conn.execute(text("SELECT tweet_id, handle, created_at FROM tweets ORDER BY created_at DESC LIMIT 5"))
                print("\n[DB] Recent Entries:")
                for row in recent:
                    print(f"   - {row[1]}: {row[0]}")
    except Exception as e:
        print(f"[DB] Error: {e}")

if __name__ == "__main__":
    probe_system()
