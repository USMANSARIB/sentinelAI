"""
Integration Test 04: URL Expansion (Step 3→7)

Tests the integration between stored database records and the URL expansion service.

This test validates:
- Detection of shortened URLs in tweets
- Resolution of expanded URLs (mocked network)
- Redis caching of expanded URLs
- Database update of expanded_urls field
"""

import unittest
import os
import sys
import asyncio
import time
import json
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.models import engine, Tweet
from app.services.url_expander import URLExpander
import redis
import config

class TestURLExpansionIntegration(unittest.TestCase):
    """Integration test for URL expansion logic."""
    
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
        self.test_tweet_id = f"url_test_{int(time.time())}"
        
    def tearDown(self):
        """Clean up after each test."""
        self.session.query(Tweet).filter(Tweet.tweet_id == self.test_tweet_id).delete()
        self.session.commit()
        self.session.close()

    @patch('httpx.AsyncClient.head')
    def test_url_expansion_logic(self, mock_head):
        """Test the URLExpander service directly with mocked network."""
        short_url = "https://bit.ly/fake-news-123"
        self.redis_client.delete(f"url:{short_url}")
        
        # Setup mock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = MagicMock()
        # MagicMock.__str__ needs to be the URL string
        mock_resp.url.__str__.return_value = "https://legit-site.com/real-article"
        mock_head.return_value = mock_resp        
        expander = URLExpander()
        
        # Test expansion
        result = asyncio.run(expander.expand_url(short_url))
        
        print(f"✅ Expanded: {short_url} → {result['final_url']}")
        
        self.assertEqual(result['final_url'], "https://legit-site.com/real-article")
        self.assertIn('is_suspicious', result)
        
        # Verify Redis cache
        cache_val = self.redis_client.get(f"url:{short_url}")
        self.assertIsNotNone(cache_val)
        cache_data = json.loads(cache_val)
        self.assertEqual(cache_data['final_url'], "https://legit-site.com/real-article")
        print("✅ Redis cache verified (as JSON)")

    @patch('httpx.AsyncClient.head')
    def test_analyzer_job_integration(self, mock_head):
        """Test that the analyzer job updates the database with expanded URLs."""
        short_url = "https://t.co/abc123short"
        self.redis_client.delete(f"url:{short_url}")
        
        # Setup mock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = MagicMock()
        mock_resp.url.__str__.return_value = "https://expanded-destination.com"
        mock_head.return_value = mock_resp
        
        # Setup tweet in DB
        tweet = Tweet(
            tweet_id=self.test_tweet_id,
            handle="url_bot",
            text_raw=f"Check this out {short_url}",
            urls=[short_url]
        )
        self.session.add(tweet)
        self.session.commit()
        
        # Verify initial state
        self.assertIsNone(tweet.expanded_urls)
        
        # Run job
        from app.services.analyzer import job_url_expansion
        job_url_expansion()
        
        # Refresh and verify
        self.session.refresh(tweet)
        self.assertIsNotNone(tweet.expanded_urls)
        self.assertIn("https://expanded-destination.com", tweet.expanded_urls)
        print(f"✅ Database updated with expanded URL: {tweet.expanded_urls}")

    @patch('httpx.AsyncClient.head')
    def test_suspicious_domain_detection(self, mock_head):
        """Test that suspicious domains (e.g. .tk) are flagged."""
        expander = URLExpander()
        
        # .tk is a common malicious TLD
        bad_url = "http://scam-site.tk/login"
        self.redis_client.delete(f"url:{bad_url}")
        
        # Setup mock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = MagicMock()
        mock_resp.url.__str__.return_value = bad_url
        mock_head.return_value = mock_resp
        
        result = asyncio.run(expander.expand_url(bad_url))
            
        print(f"✅ Suspicious URL detected: {bad_url} -> {result['is_suspicious']}")
        self.assertTrue(result['is_suspicious'])

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INTEGRATION TEST 04: URL Expansion (Step 3→7)")
    print("="*70 + "\n")
    unittest.main(verbosity=2)
