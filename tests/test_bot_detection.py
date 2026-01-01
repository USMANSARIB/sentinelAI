import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta, timezone
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.models import User
from app.detection.bot_detector import BotDetector

class TestBotDetection(unittest.TestCase):
    def setUp(self):
        self.detector = BotDetector()
        self.mock_session = MagicMock()

    def test_organic_user(self):
        """Test a normal organic user."""
        # 3 year old account, 1000 followers, 500 following, 3 tweets/day, low repeat
        user = User(
            user_id="user1",
            tweet_count=3000,
            account_created_at=datetime.now(timezone.utc) - timedelta(days=1000),
            followers_count=1000,
            following_count=500
        )
        
        # Mock repeat ratio to 0.0
        self.detector.calculate_repeat_ratio = MagicMock(return_value=0.0)
        
        score, label, details = self.detector.score_user(user, self.mock_session)
        
        # Expected:
        # Freq: 3/day -> score 0.03 * 0.30 = 0.009
        # Age: 1000 days -> score 0.0 * 0.25 = 0.0
        # Ratio: 2.0 -> score 0.0 * 0.20 = 0.0
        # Repeat: 0.0 -> score 0.0 * 0.25 = 0.0
        # Total < 0.1
        
        self.assertEqual(label, 'ORGANIC')
        self.assertLess(score, 0.4)

    def test_obvious_bot(self):
        """Test a clear bot profile."""
        # New account (1 day), 1000 tweets (1000/day), 0 followers, 1000 following
        user = User(
            user_id="bot1",
            tweet_count=1000,
            account_created_at=datetime.now(timezone.utc) - timedelta(days=1),
            followers_count=0,
            following_count=1000
        )
        
        self.detector.calculate_repeat_ratio = MagicMock(return_value=0.8) # High repeat
        
        score, label, details = self.detector.score_user(user, self.mock_session)
        
        # Expected:
        # Freq: 1000/day -> cap 1.0 * 0.30 = 0.30
        # Age: 1 day -> 1.0 * 0.25 = 0.25
        # Ratio: 0.0 -> <0.1 -> 0.8 * 0.20 = 0.16
        # Repeat: 0.8 -> cap 1.0 * 0.25 = 0.25
        # Total: 0.30 + 0.25 + 0.16 + 0.25 = 0.96 (BOT)
        
        self.assertEqual(label, 'BOT')
        self.assertGreater(score, 0.7)

if __name__ == "__main__":
    unittest.main()
