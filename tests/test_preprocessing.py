import unittest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.cleaner import clean_tweet

class TestFeatureExtraction(unittest.TestCase):
    def test_cleaning_logic(self):
        """Test Step 3 cleaning pipeline: whitespace, emojis, extraction."""
        sample_tweet = {
            "tweet_id": "999",
            "handle": "tester",
            "text_raw": "  Hello World! 🚀 Join us at #SentinelGraph. CC: @elonmusk https://google.com  ",
            "timestamp_absolute": "2023-01-01T12:00:00Z"
        }
        
        processed = clean_tweet(sample_tweet)
        
        # 1. Whitespace removal
        self.assertEqual(processed['text_raw'], "Hello World! 🚀 Join us at #SentinelGraph. CC: @elonmusk https://google.com")
        
        # 2. Emoji removal (normalize to ascii)
        self.assertNotIn("🚀", processed['text_clean'])
        
        # 3. Hashtag extraction
        self.assertIn("#SentinelGraph", processed['hashtags'])
        
        # 4. Mention extraction
        self.assertIn("@elonmusk", processed['mentions'])
        
        # 5. URL extraction
        self.assertIn("https://google.com", processed['urls'])
        
        # 6. Text Hash (MD5 of alphanumeric lower)
        # "helloworldjoinusatsentinelgraphccelonmuskhttpsgooglecom"
        self.assertTrue(len(processed['text_hash']) == 32)
        
    def test_duplicate_hashes(self):
        """Test that same content with different spacing/casing results in same hash."""
        tweet1 = {"tweet_id": "1", "handle": "a", "text_raw": "Check this #News!"}
        tweet2 = {"tweet_id": "2", "handle": "b", "text_raw": "  CHECK THIS #NEWS!  "}
        
        p1 = clean_tweet(tweet1)
        p2 = clean_tweet(tweet2)
        
        self.assertEqual(p1['text_hash'], p2['text_hash'])

if __name__ == "__main__":
    unittest.main()
