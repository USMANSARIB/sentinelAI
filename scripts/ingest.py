import time
import json
import os
import sys
import redis
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add project root to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class JSONHandler(FileSystemEventHandler):
    def __init__(self, r):
        self.redis = r

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.json'):
            print(f"[WATCHER] New file detected: {event.src_path}")
            # Give a small delay for file write to complete
            time.sleep(0.5)
            self.ingest_json_file(event.src_path)

    def ingest_json_file(self, file_path):
        filename = os.path.basename(file_path).lower()
        # Project root should be one level up from the scripts folder
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        processed_dir = os.path.join(project_root, 'data', 'processed_json')
        error_dir = os.path.join(project_root, 'data', 'errors')

        # Ensure folders exist
        os.makedirs(processed_dir, exist_ok=True)
        os.makedirs(error_dir, exist_ok=True)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle both single object or list of objects
            if isinstance(data, dict):
                items = [data]
            elif isinstance(data, list):
                items = data
            else:
                print(f"[ERROR] Invalid JSON format in {file_path}")
                os.rename(file_path, os.path.join(error_dir, filename))
                return

            # Determine Layer Stream
            if 'micro' in filename:
                stream_key = config.REDIS_STREAM_MICRO
                layer = "MICRO"
            elif 'minute' in filename:
                stream_key = config.REDIS_STREAM_MINUTE
                layer = "MINUTE"
            elif 'hourly' in filename:
                stream_key = config.REDIS_STREAM_HOURLY
                layer = "HOURLY"
            else:
                stream_key = config.REDIS_STREAM_KEY
                layer = "DEFAULT"

            count = 0
            for item in items:
                # Basic Validation & Default Values
                if 'tweet_id' not in item or 'text_raw' not in item:
                    print(f"[WARN] Skipping invalid item in {file_path}")
                    continue

                # Ensure required fields exist even if NULL (for worker consistency)
                item['layer'] = layer
                item['handle'] = item.get('handle', 'unknown')
                item['timestamp_absolute'] = item.get('timestamp_absolute') or time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

                # Push to Redis Stream
                payload = {k: str(v) for k, v in item.items()}
                self.redis.xadd(stream_key, payload)
                count += 1

            print(f"[INGEST] ({layer}) Pushed {count} tweets from {filename} to Redis.")
            
            # Move to processed
            os.rename(file_path, os.path.join(processed_dir, filename))
            
        except Exception as e:
            print(f"[ERROR] Failed to ingest {file_path}: {e}")
            try:
                os.rename(file_path, os.path.join(error_dir, filename))
            except Exception as move_err:
                print(f"[CRITICAL] Could not move failed file: {move_err}")

def start_ingester():
    # Connect to Redis
    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)
    try:
        r.ping()
        print(f"[OK] Connected to Redis at {config.REDIS_HOST}:{config.REDIS_PORT}")
    except redis.ConnectionError:
        print("[ERROR] Could not connect to Redis. Is it running?")
        return

    # Setup Watcher
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'raw_json')
    if not os.path.exists(path):
        os.makedirs(path)
        
    event_handler = JSONHandler(r)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    
    print(f"[SYSTEM] Ingest Service watching: {path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_ingester()
