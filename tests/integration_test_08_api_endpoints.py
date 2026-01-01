"""
Integration Test 08: API Endpoints (All Steps → API Layer)

Tests the final delivery layer: the FastAPI REST API.
This test validates that all defined endpoints return the expected data structures.

Ensures:
- Narrative aggregation works
- User bot score lookup works
- Community graph data is served
- Origin and Advice endpoints correctly aggregate nested analytics
"""

import unittest
import os
import sys
from fastapi.testclient import TestClient
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.models import engine, User, Tweet
from sqlalchemy.orm import sessionmaker

class TestAPIEndpointsIntegration(unittest.TestCase):
    """Integration test for all API endpoints."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once."""
        cls.client = TestClient(app)
        cls.Session = sessionmaker(bind=engine)
        
    def setUp(self):
        """Set up before each test."""
        self.session = self.Session()
        self.test_prefix = f"api_test_{int(datetime.now().timestamp())}"
        
    def tearDown(self):
        """Clean up after each test."""
        self.session.query(Tweet).filter(Tweet.tweet_id.like(f"{self.test_prefix}%")).delete()
        self.session.query(User).filter(User.user_id.like(f"{self.test_prefix}%")).delete()
        self.session.commit()
        self.session.close()

    def test_narratives_endpoint(self):
        """Test GET /api/narratives"""
        # Create a narrative
        t = Tweet(
            tweet_id=f"{self.test_prefix}_t1",
            handle="n_user",
            text_raw="Narrative tweet",
            narrative_id=888,
            timestamp_absolute=datetime.now()
        )
        self.session.add(t)
        self.session.commit()
        
        response = self.client.get("/api/narratives")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        print(f"✅ /api/narratives: Found {len(data)} narratives")
        self.assertIsInstance(data, list)
        
        # Check if 888 is in the narrative_ids
        n_ids = [n['narrative_id'] for n in data]
        self.assertIn(888, n_ids)

    def test_user_bot_score_endpoint(self):
        """Test GET /api/users/{handle}"""
        user = User(
            user_id=f"{self.test_prefix}_u1",
            handle="test_api_bot",
            bot_score=0.95,
            bot_label="BOT"
        )
        self.session.add(user)
        self.session.commit()
        
        response = self.client.get("/api/users/test_api_bot")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        print(f"✅ /api/users/test_api_bot: Score={data['bot_score']}")
        self.assertEqual(data['handle'], "test_api_bot")
        self.assertEqual(data['bot_score'], 0.95)

    def test_communities_endpoint(self):
        """Test GET /api/communities"""
        # This endpoint relies on data in DB and graph analysis
        # Even if empty, it should return 200 and a 'communities' list
        response = self.client.get("/api/communities")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        print(f"✅ /api/communities: Size={len(data)}")
        self.assertIsInstance(data, list)

    def test_narrative_advice_endpoint(self):
        """Test GET /api/narratives/{id}/advice"""
        # Create narrative data
        nid = 777
        for i in range(5):
             t = Tweet(
                tweet_id=f"{self.test_prefix}_adv_t{i}",
                handle=f"adv_u{i}",
                text_raw="Coordinated narrative content",
                narrative_id=nid,
                timestamp_absolute=datetime.now()
            )
             user = User(user_id=f"{self.test_prefix}_adv_u{i}", handle=f"adv_u{i}", bot_score=0.8)
             self.session.merge(user)
             self.session.add(t)
        self.session.commit()
        
        response = self.client.get(f"/api/narratives/{nid}/advice")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        print(f"✅ /api/narratives/{nid}/advice: Risk={data['risk_report']['risk_level']}")
        self.assertIn('risk_report', data)
        self.assertIn('recommended_strategy', data)
        self.assertIn('timing_recommendation', data)

    def test_narrative_origin_endpoint(self):
        """Test GET /api/narratives/{id}/origin"""
        nid = 666
        t = Tweet(
            tweet_id=f"{self.test_prefix}_orig_t1",
            handle="orig_user",
            text_raw="Origin tweet",
            narrative_id=nid,
            timestamp_absolute=datetime.now()
        )
        self.session.add(t)
        self.session.commit()
        
        response = self.client.get(f"/api/narratives/{nid}/origin")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        print(f"✅ /api/narratives/{nid}/origin: SeedCount={data['origin_seed_count']}")
        self.assertEqual(data['narrative_id'], nid)
        self.assertIn('timeline', data)
        self.assertIn('velocity', data)

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INTEGRATION TEST 08: API Endpoints (All Steps → API Layer)")
    print("="*70 + "\n")
    unittest.main(verbosity=2)
