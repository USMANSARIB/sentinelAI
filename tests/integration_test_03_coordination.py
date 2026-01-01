"""
Integration Test 03: Coordination Detection (Step 3→6)

Tests the integration between stored database records and the coordination detection service.

This test validates:
- Exact text match detection within time windows
- Semantic similarity detection (pgvector)
- Handling of multiple coordination clusters
"""

import unittest
import os
import sys
from datetime import datetime, timedelta
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.models import engine, Tweet, User
from app.detection.coordination import CoordinationDetector

class TestCoordinationIntegration(unittest.TestCase):
    """Integration test for coordination detection."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once."""
        cls.Session = sessionmaker(bind=engine)
        cls.detector = CoordinationDetector(time_window_minutes=15)
        
    def setUp(self):
        """Set up before each test."""
        self.session = self.Session()
        self.test_prefix = f"coord_test_{int(datetime.now().timestamp())}"
        
    def tearDown(self):
        """Clean up after each test."""
        # Clean up database
        self.session.query(Tweet).filter(Tweet.tweet_id.like(f"{self.test_prefix}%")).delete()
        self.session.query(User).filter(User.user_id.like(f"{self.test_prefix}%")).delete()
        self.session.commit()
        self.session.close()

    def test_exact_match_coordination(self):
        """Test detection of 3+ accounts posting exact same text within 15 minutes."""
        base_time = datetime.now()
        text = "This is a coordinated exact match message!"
        text_hash = "exact_match_hash_123"
        
        test_tweets = []
        for i in range(4):
            uid = f"{self.test_prefix}_u{i}"
            user = User(user_id=uid, handle=f"user_{i}")
            self.session.merge(user)
            
            tweet = Tweet(
                tweet_id=f"{self.test_prefix}_t{i}",
                user_id=uid,
                handle=f"user_{i}",
                text_raw=text,
                text_clean=text.lower(),
                text_hash=text_hash,
                timestamp_absolute=base_time + timedelta(minutes=i*2) # 0, 2, 4, 6 mins
            )
            test_tweets.append(tweet)
            self.session.add(tweet)
            
        self.session.commit()
        
        # Run detection on these tweets
        clusters = self.detector.detect_coordination(test_tweets)
        
        print(f"✅ Exact Match Clusters: {len(clusters)}")
        for i, c in enumerate(clusters):
             print(f"   Cluster {i}: Type={c['type']}, Users={len(c['users'])}")
             
        self.assertGreaterEqual(len(clusters), 1)
        # Find the exact match cluster
        exact_clusters = [c for c in clusters if c['type'] == 'EXACT_MATCH']
        self.assertGreaterEqual(len(exact_clusters), 1)
        self.assertEqual(len(exact_clusters[0]['users']), 4)

    def test_semantic_similarity_coordination(self):
        """Test detection of similar (but not exact) text via embeddings."""
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        base_time = datetime.now()
        # Very similar messages
        messages = [
            "ALARM: Market crash imminent! Sell all assets immediately!",
            "ALARM: Market crash imminent! Sell all your assets now!",
            "ALARM: Market crash imminent! Time to sell all assets!",
            "ALARM: Market crash imminent! Selling all assets today!"
        ]
        
        test_tweets = []
        for i, msg in enumerate(messages):
            uid = f"{self.test_prefix}_sem_u{i}"
            user = User(user_id=uid, handle=f"sem_user_{i}")
            self.session.merge(user)
            
            embedding = model.encode(msg).tolist()
            
            tweet = Tweet(
                tweet_id=f"{self.test_prefix}_sem_t{i}",
                user_id=uid,
                handle=f"sem_user_{i}",
                text_raw=msg,
                text_clean=msg.lower(),
                text_hash=f"sem_hash_{i}",
                embedding=embedding,
                timestamp_absolute=base_time + timedelta(minutes=i)
            )
            test_tweets.append(tweet)
            self.session.add(tweet)
            
        self.session.commit()
        
        # Run detection
        clusters = self.detector.detect_coordination(test_tweets)
        
        print(f"✅ Semantic Clusters: {len(clusters)}")
        for i, c in enumerate(clusters):
             print(f"   Cluster {i}: Type={c['type']}, Users={len(c['users'])}")
             
        # Should detect at least one semantic cluster
        # Note: Depending on threshold, some might be clustered together
        sem_clusters = [c for c in clusters if c['type'] == 'SEMANTIC_SIMILARITY']
        self.assertGreaterEqual(len(sem_clusters), 1)
        self.assertGreaterEqual(len(sem_clusters[0]['users']), 3)

    def test_analyzer_job_integration(self):
        """Test that the analyzer job runs coordination detection without error."""
        # Setup: Create some data
        base_time = datetime.now()
        for i in range(5):
             t = Tweet(
                tweet_id=f"{self.test_prefix}_job_t{i}",
                handle="job_user",
                text_raw="Coordinated job test",
                text_hash="job_hash",
                timestamp_absolute=base_time + timedelta(minutes=i)
            )
             self.session.add(t)
        self.session.commit()
        
        # Run job
        from app.services.analyzer import job_coordination
        
        # This job currently just logs to stdout. We verify it doesn't crash.
        try:
            job_coordination()
            print("✅ Analyzer job_coordination executed successfully.")
        except Exception as e:
            self.fail(f"job_coordination crashed: {e}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INTEGRATION TEST 03: Coordination Detection (Step 3→6)")
    print("="*70 + "\n")
    unittest.main(verbosity=2)
