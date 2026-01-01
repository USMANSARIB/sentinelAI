import unittest
import json
import os
import redis
import sys
import time
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from scripts.ingest import JSONHandler

class TestTwitterDataCollector(unittest.TestCase):
    def setUp(self):
        # Mock Redis
        self.mock_redis = MagicMock(spec=redis.Redis)
        self.handler = JSONHandler(self.mock_redis)
        
        # Test paths
        self.test_json = "test_tweet.json"
        
    def tearDown(self):
        if os.path.exists(self.test_json):
            os.remove(self.test_json)

    def test_ingest_json_file_micro_routing(self):
        """Test that a 'micro' file is routed to the MICRO stream and moved to processed."""
        filename = "test_micro_tweet.json"
        sample_data = [{"tweet_id": "1", "text_raw": "test"}]
        
        with open(filename, 'w') as f:
            json.dump(sample_data, f)
            
        self.handler.ingest_json_file(filename)
        
        # Verify stream routing
        self.mock_redis.xadd.assert_called_once()
        args, _ = self.mock_redis.xadd.call_args
        self.assertEqual(args[0], config.REDIS_STREAM_MICRO)
        
        # Verify file moved to processed
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        processed_path = os.path.join(project_root, 'data', 'processed_json', filename)
        
        self.assertTrue(os.path.exists(processed_path), f"File not found at {processed_path}")
        if os.path.exists(processed_path): os.remove(processed_path)

    def test_ingest_invalid_to_error_folder(self):
        """Test that malformed JSON is moved to the error folder."""
        filename = "bad_format.json"
        with open(filename, 'w') as f:
            f.write("not active json")
            
        self.handler.ingest_json_file(filename)
            
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        error_path = os.path.join(project_root, 'data', 'errors', filename)
        
        self.assertTrue(os.path.exists(error_path), f"File not found at {error_path}")
        if os.path.exists(error_path): os.remove(error_path)

    def test_file_watcher_detection(self):
        """Test that the handler's on_created trigger works."""
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "data/raw_json/new_tweet.json"
        
        with patch.object(JSONHandler, 'ingest_json_file') as mock_ingest:
            with patch('time.sleep'): # Skip sleep in tests
                self.handler.on_created(mock_event)
                mock_ingest.assert_called_once_with("data/raw_json/new_tweet.json")

if __name__ == "__main__":
    unittest.main()
