"""
Integration Test 02: Bot Detection (Step 3→5)

Tests the integration between stored database records and the bot detector service.

This test validates:
- Bot score calculation for organic accounts
- Bot score calculation for bot-like accounts
- Database update of bot scores via the analyzer job logic
"""

import unittest
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.models import engine, User, Tweet
from app.detection.bot_detector import BotDetector

class TestBotDetectionIntegration(unittest.TestCase):
    """Integration test for bot detection logic."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once."""
        cls.Session = sessionmaker(bind=engine)
        cls.detector = BotDetector()
        
    def setUp(self):
        """Set up before each test."""
        self.session = self.Session()
        self.test_user_id = f"bot_test_{int(datetime.now().timestamp())}"
        
    def tearDown(self):
        """Clean up after each test."""
        # Clean up database
        self.session.query(Tweet).filter(Tweet.user_id == self.test_user_id).delete()
        self.session.query(User).filter(User.user_id == self.test_user_id).delete()
        self.session.commit()
        self.session.close()

    def test_organic_user_scoring(self):
        """Test that an organic user gets a low bot score."""
        # Setup: Organic-looking user
        user = User(
            user_id=self.test_user_id,
            handle="organic_tester",
            followers_count=500,
            following_count=450,
            tweet_count=1000,
            account_created_at=datetime.now() - timedelta(days=365) # 1 year old
        )
        self.session.add(user)
        
        # Add some tweets
        for i in range(5):
            t = Tweet(
                tweet_id=f"{self.test_user_id}_t{i}",
                user_id=self.test_user_id,
                handle="organic_tester",
                text_raw=f"Organic tweet number {i}",
                text_clean=f"organic tweet number {i}",
                text_hash=f"hash_o_{i}",
                timestamp_absolute=datetime.now() - timedelta(hours=i)
            )
            self.session.add(t)
        
        self.session.commit()
        
        # Run detection
        score, label, details = self.detector.score_user(user, self.session)
        
        print(f"✅ Organic Score: {score} ({label})")
        print(f"   Details: {details}")
        
        self.assertLess(score, 0.4)
        self.assertEqual(label, "ORGANIC")

    def test_bot_user_scoring(self):
        """Test that a bot-like user gets a high bot score."""
        # Setup: Bot-looking user
        user = User(
            user_id=self.test_user_id,
            handle="bot_tester",
            followers_count=10,
            following_count=5000, # Extreme ratio
            tweet_count=20000,
            account_created_at=datetime.now() - timedelta(days=2) # New account
        )
        self.session.add(user)
        
        # Add some tweets with repetitive text
        for i in range(10):
            t = Tweet(
                tweet_id=f"{self.test_user_id}_t{i}",
                user_id=self.test_user_id,
                handle="bot_tester",
                text_raw="REPETITIVE Content! Visit my spam site.",
                text_clean="repetitive content visit my spam site",
                text_hash="spam_hash", # Same hash for all
                timestamp_absolute=datetime.now() - timedelta(minutes=i)
            )
            self.session.add(t)
        
        self.session.commit()
        
        # Run detection
        score, label, details = self.detector.score_user(user, self.session)
        
        print(f"✅ Bot Score: {score} ({label})")
        print(f"   Details: {details}")
        
        self.assertGreaterEqual(score, 0.7)
        self.assertEqual(label, "BOT")

    def test_analyzer_job_integration(self):
        """Test that the analyzer job correctly updates users in the database."""
        # Create a user without a score
        user = User(
            user_id=self.test_user_id,
            handle="pending_score",
            followers_count=100,
            following_count=100,
            account_created_at=datetime.now() - timedelta(days=10)
        )
        self.session.add(user)
        self.session.commit()
        
        # Verify initial state
        self.assertIsNone(user.bot_label)
        
        # Run job (imported from analyzer)
        from app.services.analyzer import job_bot_scoring
        
        # The job picks up users with no score. 
        # Since we just added one, it should pick it up.
        job_bot_scoring()
        
        # Refresh and verify
        self.session.refresh(user)
        self.assertIsNotNone(user.bot_score)
        print(f"✅ Database updated by analyzer job. Score: {user.bot_score}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INTEGRATION TEST 02: Bot Detection (Step 3→5)")
    print("="*70 + "\n")
    unittest.main(verbosity=2)
