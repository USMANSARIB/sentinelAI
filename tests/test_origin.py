import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.detection.origin import NarrativeAnalyzer

class MockTweet:
    def __init__(self, tweet_id, timestamp):
        self.tweet_id = tweet_id
        self.timestamp_absolute = timestamp
        self.narrative_id = 1

class TestOriginDetection(unittest.TestCase):
    def test_spread_metrics(self):
        """Test calculation of peak and velocity."""
        analyzer = NarrativeAnalyzer(session=MagicMock())
        
        # Scenario: 
        # T0: 10 tweets
        # T+1hr: 100 tweets (Peak)
        # T+2hr: 10 tweets
        
        base = datetime(2025,1,1,10,0,0)
        timeline = [
            {'time': base.isoformat(), 'count': 10},
            {'time': (base + timedelta(hours=1)).isoformat(), 'count': 100},
            {'time': (base + timedelta(hours=2)).isoformat(), 'count': 10},
        ]
        
        metrics = analyzer.calculate_spread_metrics(timeline)
        
        self.assertEqual(metrics['peak_volume'], 100)
        self.assertEqual(metrics['peak_time'], (base + timedelta(hours=1)).isoformat())
        self.assertEqual(metrics['duration_hours'], 2.0)
        
        # Velocity = 120 tweets / 2 hours = 60/hr
        self.assertEqual(metrics['avg_velocity_per_hour'], 60.0)

if __name__ == "__main__":
    unittest.main()
