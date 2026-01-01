import unittest
from datetime import datetime, timedelta, timezone
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.detection.coordination import CoordinationDetector

# Mock Tweet Object
class MockTweet:
    def __init__(self, tweet_id, user_id, text_hash, timestamp, embedding=None):
        self.tweet_id = tweet_id
        self.user_id = user_id
        self.text_hash = text_hash
        self.timestamp_absolute = timestamp
        self.text_clean = "sample text"
        self.embedding = embedding

class TestCoordination(unittest.TestCase):
    def test_exact_hash_coordination(self):
        """Test detection of exact text duplication within time window."""
        detector = CoordinationDetector(time_window_minutes=10)
        
        # 3 users posting same hash within 5 mins
        base_time = datetime.now()
        tweets = [
            MockTweet("t1", "u1", "hash_abc", base_time),
            MockTweet("t2", "u2", "hash_abc", base_time + timedelta(minutes=2)),
            MockTweet("t3", "u3", "hash_abc", base_time + timedelta(minutes=4)),
            # Unrelated tweet
            MockTweet("t4", "u4", "hash_xyz", base_time)
        ]
        
        clusters = detector.detect_coordination(tweets)
        
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]['type'], 'EXACT_HASH')
        self.assertEqual(len(clusters[0]['users']), 3)

    def test_exact_hash_no_coordination(self):
        """Test that spread out tweets are NOT flagged."""
        detector = CoordinationDetector(time_window_minutes=10)
        
        base_time = datetime.now()
        tweets = [
            MockTweet("t1", "u1", "hash_abc", base_time),
            MockTweet("t2", "u2", "hash_abc", base_time + timedelta(minutes=30)), # Gap > 10
            MockTweet("t3", "u3", "hash_abc", base_time + timedelta(minutes=60))
        ]
        
        clusters = detector.detect_coordination(tweets)
        self.assertEqual(len(clusters), 0)

if __name__ == "__main__":
    unittest.main()
