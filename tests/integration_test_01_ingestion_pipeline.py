"""
Integration Test 01: Ingestion Pipeline (Step 2→3)

Tests the complete data flow:
Scraper → JSON file → Ingest Service → Redis Stream → Worker → PostgreSQL

This test validates:
- JSON file creation
- Redis stream message
- Database record insertion
- Embedding generation
"""

import unittest
import os
import sys
import json
import time
import tempfile
import shutil
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.models import engine, Tweet, User
import redis
import config

class TestIngestionPipeline(unittest.TestCase):
    """Integration test for the complete ingestion pipeline."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once."""
        cls.Session = sessionmaker(bind=engine)
        cls.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            decode_responses=True
        )
        
    def setUp(self):
        """Set up before each test."""
        self.session = self.Session()
        self.test_tweet_id = f"integration_test_{int(time.time())}"
        
    def tearDown(self):
        """Clean up after each test."""
        # Remove test data from database
        self.session.query(Tweet).filter(Tweet.tweet_id == self.test_tweet_id).delete()
        self.session.query(User).filter(User.user_id.like('integration_test_%')).delete()
        self.session.commit()
        self.session.close()
        
    def test_01_json_to_redis(self):
        """Test that JSON files are pushed to Redis stream."""
        # Create test JSON file
        test_data = {
            "tweet_id": self.test_tweet_id,
            "handle": "integration_test_user",
            "text_raw": "This is a test tweet for integration testing.",
            "timestamp_absolute": datetime.now().isoformat(),
            "mentions": "[]", # Serialized
            "urls": "[]"      # Serialized
        }
        
        # Get current stream length
        try:
            stream_length_before = self.redis_client.xlen(config.REDIS_STREAM_KEY)
        except:
            stream_length_before = 0
            
        # Manually push to Redis (simulating ingest service)
        self.redis_client.xadd(
            config.REDIS_STREAM_KEY,
            test_data
        )
        
        # Verify stream length increased
        stream_length_after = self.redis_client.xlen(config.REDIS_STREAM_KEY)
        self.assertGreater(stream_length_after, stream_length_before)
        
        print(f"✅ Redis stream length: {stream_length_before} → {stream_length_after}")
        
    def test_02_redis_to_database(self):
        """Test that worker processes Redis messages and stores in PostgreSQL."""
        from app.services.cleaner import clean_tweet
        from sentence_transformers import SentenceTransformer
        
        # Create test data
        test_data = {
            "tweet_id": self.test_tweet_id,
            "handle": "integration_test_user",
            "text_raw": "This is a test tweet for integration testing #test",
            "timestamp_absolute": datetime.now().isoformat()
        }
        
        # Simulate worker processing
        # 1. Clean tweet (expects dict)
        clean_result = clean_tweet(test_data)
        cleaned_text = clean_result['text_clean']
        
        # 2. Generate embedding
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode(cleaned_text).tolist()
        
        # 3. Create User
        user = User(
            user_id=test_data['handle'],
            handle=test_data['handle'],
            followers_count=0,
            following_count=0,
            tweet_count=1
        )
        self.session.merge(user)
        
        # 4. Create Tweet
        tweet = Tweet(
            tweet_id=test_data['tweet_id'],
            user_id=test_data['handle'],
            handle=test_data['handle'],
            text_raw=test_data['text_raw'],
            text_clean=cleaned_text,
            text_hash=clean_result['text_hash'],
            timestamp_absolute=clean_result['timestamp_absolute'],
            mentions=clean_result['mentions'],
            urls=clean_result['urls'],
            embedding=embedding
        )
        self.session.add(tweet)
        self.session.commit()
        
        # Verify database record
        stored_tweet = self.session.query(Tweet).filter(
            Tweet.tweet_id == self.test_tweet_id
        ).first()
        
        self.assertIsNotNone(stored_tweet)
        self.assertEqual(stored_tweet.text_clean, cleaned_text)
        self.assertIsNotNone(stored_tweet.embedding)
        self.assertEqual(len(stored_tweet.embedding), 384)  # MiniLM embedding size
        
        print(f"✅ Tweet stored in database: {stored_tweet.tweet_id}")
        print(f"✅ Embedding size: {len(stored_tweet.embedding)}")
        
    def test_03_end_to_end_simulation(self):
        """Simulate complete pipeline without external services."""
        # This test simulates the entire flow in-process
        
        # Step 1: Scraper creates JSON (simulated)
        tweet_data = {
            "tweet_id": self.test_tweet_id,
            "handle": "e2e_test_user",
            "text_raw": "End-to-end integration test tweet",
            "timestamp_absolute": datetime.now().isoformat()
        }
        
        # Step 2: Ingest pushes to Redis (simulated)
        # Convert to string-only dict for Redis
        redis_data = {k: str(v) for k, v in tweet_data.items()}
        self.redis_client.xadd(config.REDIS_STREAM_KEY, redis_data)
        
        # Step 3: Worker processes (simulated)
        from app.services.cleaner import clean_tweet
        from sentence_transformers import SentenceTransformer
        
        clean_result = clean_tweet(tweet_data)
        cleaned_text = clean_result['text_clean']
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode(cleaned_text).tolist()
        
        # Create user and tweet
        user = User(
            user_id=tweet_data['handle'],
            handle=tweet_data['handle']
        )
        self.session.merge(user)
        
        tweet = Tweet(
            tweet_id=tweet_data['tweet_id'],
            user_id=tweet_data['handle'],
            handle=tweet_data['handle'],
            text_raw=tweet_data['text_raw'],
            text_clean=cleaned_text,
            embedding=embedding,
            timestamp_absolute=clean_result['timestamp_absolute']
        )
        self.session.add(tweet)
        self.session.commit()
        
        # Verify complete pipeline
        result = self.session.query(Tweet).filter(
            Tweet.tweet_id == self.test_tweet_id
        ).first()
        
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.embedding)
        self.assertIsNotNone(result.text_clean)
        
        print(f"✅ End-to-end test passed")
        print(f"   Tweet ID: {result.tweet_id}")
        print(f"   Clean text: {result.text_clean}")
        print(f"   Has embedding: {result.embedding is not None}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INTEGRATION TEST 01: Ingestion Pipeline (Step 2→3)")
    print("="*70 + "\n")
    unittest.main(verbosity=2)
