import os
import json
import redis
import config

r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)
path = os.path.join('data', 'raw_json')

for filename in os.listdir(path):
    if filename.endswith('.json'):
        filepath = os.path.join(path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                # Determine the correct stream based on filename
                if 'micro' in filename.lower():
                    stream_key = config.REDIS_STREAM_MICRO
                    layer = "MICRO"
                elif 'minute' in filename.lower():
                    stream_key = config.REDIS_STREAM_MINUTE
                    layer = "MINUTE"
                elif 'hourly' in filename.lower():
                    stream_key = config.REDIS_STREAM_HOURLY
                    layer = "HOURLY"
                else:
                    stream_key = config.REDIS_STREAM_KEY
                    layer = "DEFAULT"
                
                for item in data:
                    item['layer'] = layer
                    payload = {k: str(v) for k, v in item.items()}
                    r.xadd(stream_key, payload)
                print(f"Ingested {len(data)} items from {filename} -> {stream_key}")
