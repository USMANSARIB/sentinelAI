"""
Integration Test 06: Origin Tracing (Step 3→4→9)

Tests the integration between narrative-clustered tweets and the origin detection service.

This test validates:
- Correct identification of 'patient zero' (earliest tweet)
- Correct calculation of origin seeds (time-window based)
- Generation of the spread timeline (5-minute buckets)
- Velocity calculation (tweets per hour)
"""

import unittest
import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.models import engine, Tweet
from app.detection.origin import NarrativeAnalyzer

class TestOriginTracingIntegration(unittest.TestCase):
    """Integration test for narrative origin tracking."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once."""
        cls.Session = sessionmaker(bind=engine)
        
    def setUp(self):
        """Set up before each test."""
        self.session = self.Session()
        self.test_narrative_id = 9999 + int(datetime.now().timestamp() % 1000)
        self.test_prefix = f"origin_test_{self.test_narrative_id}"
        
    def tearDown(self):
        """Clean up after each test."""
        # Clean up database
        self.session.query(Tweet).filter(Tweet.narrative_id == self.test_narrative_id).delete()
        self.session.commit()
        self.session.close()

    def test_narrative_origin_and_velocity(self):
        """Test tracing a narrative to its origin and measuring spread speed."""
        # Setup: Narrative with 10 tweets spread over 2 hours
        # T0: Start
        # T+10m: 2 tweets
        # T+60m: 5 tweets (Peak)
        # T+120m: 2 tweets
        
        base_time = datetime.now() - timedelta(hours=5) # 5 hours ago
        
        tweet_timeline = [
            (0, 1),   # 0 min, 1 tweet (Patient Zero)
            (10, 2),  # 10 min, 2 tweets
            (60, 5),  # 60 min, 5 tweets (Peak)
            (120, 2)  # 120 min, 2 tweets
        ]
        
        expected_total = sum(count for _, count in tweet_timeline)
        
        count = 0
        for offset_min, num_tweets in tweet_timeline:
            for _ in range(num_tweets):
                t = Tweet(
                    tweet_id=f"{self.test_prefix}_t{count}",
                    handle=f"user_{count}",
                    text_raw=f"Narrative {self.test_narrative_id} message {count}",
                    timestamp_absolute=base_time + timedelta(minutes=offset_min),
                    narrative_id=self.test_narrative_id
                )
                self.session.add(t)
                count += 1
                
        self.session.commit()
        
        # Run tracing
        analyzer = NarrativeAnalyzer(self.session)
        report = analyzer.find_narrative_origin(self.test_narrative_id)
        
        print(f"✅ Origin Report for Narrative {self.test_narrative_id}:")
        print(f"   Total Volume: {report['total_volume']}")
        print(f"   Origin Seeds: {report['origin_seed_count']}")
        print(f"   Discovery: {report['first_seen']}")
        print(f"   Velocity: {report['velocity']['avg_velocity_per_hour']} tweets/hour")
        print(f"   Timeline Length: {len(report['timeline'])} buckets")
        
        # Validations
        self.assertIsNotNone(report)
        self.assertEqual(report['total_volume'], expected_total)
        # Seeds are within 30 mins: T0 (1) + T10 (2) = 3
        self.assertEqual(report['origin_seed_count'], 3)
        # Velocity for 10 tweets over 2 hours = 5/hour
        self.assertEqual(report['velocity']['avg_velocity_per_hour'], 5.0)
        # Peak should be at T+60
        self.assertEqual(report['velocity']['peak_volume'], 5)

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INTEGRATION TEST 06: Origin Tracing (Step 3→4→9)")
    print("="*70 + "\n")
    unittest.main(verbosity=2)
