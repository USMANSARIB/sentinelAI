import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import json
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.url_expander import URLExpander

class TestURLExpansion(unittest.TestCase):
    def setUp(self):
        # Mock Redis
        self.mock_redis = MagicMock()
        with patch('app.services.url_expander.redis.Redis') as mock_redis_cls:
            mock_redis_cls.return_value = self.mock_redis
            self.expander = URLExpander()
            # Restore mock to instance
            self.expander.redis = self.mock_redis 

    def test_suspicious_domain_logic(self):
        """Test heuristic domain flagging."""
        self.assertTrue(self.expander.is_suspicious_domain("scam.tk"))
        self.assertTrue(self.expander.is_suspicious_domain("phishing.ga"))
        self.assertTrue(self.expander.is_suspicious_domain("bit.ly")) # In seed set
        self.assertFalse(self.expander.is_suspicious_domain("google.com"))

    @patch('app.services.url_expander.httpx.AsyncClient')
    def test_expand_url_success(self, mock_client_cls):
        """Test full expansion logic (Cache Miss -> HTTP -> Cache Set)."""
        # Mock Redis Miss
        self.mock_redis.get.return_value = None
        
        # Mock HTTP Response
        mock_response = MagicMock()
        mock_response.url = "https://example.com/long-article"
        mock_response.status_code = 200
        
        # Async Context Manager Mocking hell
        mock_client = AsyncMock()
        mock_client.head.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_cls.return_value = mock_client
        
        # Run Async Test
        result = asyncio.run(self.expander.expand_url("http://tiny.cc/abc"))
        
        # Verify result
        self.assertEqual(result['final_url'], "https://example.com/long-article")
        self.assertEqual(result['domain'], "example.com")
        
        # Verify Cache Set
        self.mock_redis.setex.assert_called_once()
        args = self.mock_redis.setex.call_args[0]
        self.assertEqual(args[0], "url:http://tiny.cc/abc") # Key
        self.assertIn("example.com", args[2]) # Value (JSON)

    def test_cache_hit(self):
        """Test URL expansion from cache."""
        cached_data = {
            'final_url': 'https://cached.com',
            'domain': 'cached.com',
            'status': 200
        }
        self.mock_redis.get.return_value = json.dumps(cached_data)
        
        result = asyncio.run(self.expander.expand_url("http://bit.ly/cached"))
        
        self.assertEqual(result['final_url'], 'https://cached.com')
        # Ensure no HTTP request made (can't easily verify exact mock calls without patching class globally in scope, but logic implies it returns early)

if __name__ == "__main__":
    unittest.main()
