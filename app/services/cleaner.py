import re
import hashlib
from datetime import datetime
from dateutil import parser

def clean_tweet(tweet_data):
    """
    Implements the Cleaning Pipeline from Step 3.
    """
    text = tweet_data.get('text_raw', '')
    
    # 1. Remove extra whitespace
    text = ' '.join(text.split())
    
    # 2. Remove/normalize emojis
    # PDF Method: text.encode('ascii', 'ignore').decode()
    # This removes them. Alternative is 'emoji' lib but PDF suggests this for MVP.
    text_clean = text.encode('ascii', 'ignore').decode()
    
    # 3. Extract features
    hashtags = re.findall(r'#\w+', text)
    mentions = re.findall(r'@\w+', text)
    # Simple regex for URLs
    urls = re.findall(r'https?://[^\s]+', text)
    
    # 4. Generate text hash (for duplicate detection)
    # Normalize: lowercase + remove punctuation/spaces for hashing
    normalized = ''.join(c.lower() for c in text if c.isalnum())
    text_hash = hashlib.md5(normalized.encode()).hexdigest()
    
    # 5. Parse Timestamp
    ts_str = tweet_data.get('timestamp_absolute')
    ts_obj = None
    if ts_str:
        try:
            ts_obj = parser.parse(ts_str)
        except:
            ts_obj = datetime.now() # Fallback

    return {
        'tweet_id': tweet_data['tweet_id'],
        'handle': tweet_data['handle'],
        'text_raw': text,
        'text_clean': text_clean,
        'hashtags': hashtags,
        'mentions': mentions,
        'urls': urls,
        'text_hash': text_hash,
        'timestamp_absolute': ts_obj
    }
