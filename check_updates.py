import config
from db_client import SentinelDB
import redis

def main():
    db = SentinelDB()
    # Check PostgreSQL tweet count
    try:
        db.cursor.execute('SELECT COUNT(*) as cnt, MAX(timestamp_absolute) as latest FROM tweets')
        res = db.cursor.fetchone()
        print(f"[POSTGRES] Row Count: {res['cnt']}")
        print(f"[POSTGRES] Latest Tweet Time: {res['latest']}")
    except Exception as e:
        print(f"[POSTGRES] Error querying tweets: {e}")

    # Check Redis stream lengths
    try:
        r = db.redis
        stream_keys = [config.REDIS_STREAM_KEY, config.REDIS_STREAM_MICRO, config.REDIS_STREAM_MINUTE, config.REDIS_STREAM_HOURLY]
        for key in stream_keys:
            try:
                length = r.xlen(key)
                print(f"[REDIS] Stream {key} length: {length}")
            except Exception:
                print(f"[REDIS] Stream {key} does not exist or error.")
    except Exception as e:
        print(f"[REDIS] Error accessing Redis: {e}")

if __name__ == '__main__':
    main()
