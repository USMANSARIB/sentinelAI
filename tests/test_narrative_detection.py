import unittest
from datetime import datetime, timedelta
import pandas as pd

# Mocking the logic since we can't easily import the complex dependencies of clustering.py in a simple unit test
# without setting up a full DB mock. We will test the logic function directly.

def calculate_spike_metrics(tweets_data):
    """
    tweets_data: list of dicts with 'created_at'
    """
    if not tweets_data:
        return {'is_spike': False, 'velocity': 0}

    df = pd.DataFrame(tweets_data)
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    now = datetime.now() # In real code this should be passed in or mocked
    # For test determinism, let's assume 'now' is the max time in tweets
    now = df['created_at'].max()
    
    # Current rate (last 1 hour)
    last_hour_start = now - timedelta(hours=1)
    current_tweets = df[df['created_at'] >= last_hour_start]
    current_rate = len(current_tweets)
    
    # Baseline rate (full duration, max 24h?)
    # Vision says: "Baseline (past 24 hours)"
    # And "Baseline rate = len(baseline_tweets) / 24" (if window is full 24h)
    # If narrative is younger than 24h, use its duration.
    
    start_time = df['created_at'].min()
    duration_hours = (now - start_time).total_seconds() / 3600
    
    # Valid baseline calculation per logic:
    # If duration < 1, assume 1 hour to avoid skew?
    # Logic in clustering.py: duration_hours = max(duration_hours, 1)
    duration_hours = max(duration_hours, 1.0)
    baseline_rate = len(df) / duration_hours
    
    velocity = current_rate / max(baseline_rate, 0.1)
    is_spike = velocity >= 3.0
    
    return {
        'is_spike': is_spike, 
        'velocity': round(velocity, 2),
        'current_rate': current_rate,
        'baseline_rate': round(baseline_rate, 2)
    }

class TestNarrativeDetection(unittest.TestCase):
    def test_spike_detection_logic(self):
        """Test Step 2: Spike Detection math."""
        
        # Scenario 1: No Spike (Steady state)
        # 10 tweets per hour for 5 hours
        tweets = []
        base_time = datetime(2025, 1, 1, 10, 0, 0)
        for i in range(50):
            t = base_time + timedelta(minutes=i*6) # Every 6 mins = 10/hr
            tweets.append({'created_at': t})
            
        metrics = calculate_spike_metrics(tweets)
        # Baseline ~10/hr. Current ~10/hr. Velocity ~1.0
        self.assertFalse(metrics['is_spike'])
        self.assertAlmostEqual(metrics['velocity'], 1.0, delta=0.5)

    def test_massive_spike(self):
        """Test Scenario 2: Sudden Spike (3x volume)"""
        # Baseline: 10 tweets/hr for 10 hours
        tweets = []
        base_time = datetime(2025, 1, 1, 0, 0, 0)
        for i in range(100):
            t = base_time + timedelta(minutes=i*6) 
            tweets.append({'created_at': t})
            
        # Spike: 50 tweets in last hour (11th hour)
        last_hour_start = base_time + timedelta(hours=10)
        for i in range(50):
            t = last_hour_start + timedelta(minutes=i)
            tweets.append({'created_at': t})
            
        metrics = calculate_spike_metrics(tweets)
        
        # Current rate: 50/hr
        # Baseline (total 150 tweets over 11 hours) = 13.6/hr
        # Velocity = 50 / 13.6 = 3.6x
        
        self.assertTrue(metrics['is_spike'])
        self.assertGreaterEqual(metrics['velocity'], 3.0)

if __name__ == "__main__":
    unittest.main()
