"""
Integration Test 05: Community Graph Detection (Step 3→5→8)

Tests the integration between stored database records (Tweets, Users + Bot Scores)
and the community detection graph analysis.

This test validates:
- Node creation from User records
- Edge creation from mentions in Tweets
- Edge creation from content similarity (Embeddings)
- Louvain community detection and classification (BOT_CLUSTER vs ORGANIC)
"""

import unittest
import os
import sys
import numpy as np
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.models import engine, Tweet, User
from app.detection.community import build_graph_and_detect

class TestCommunityGraphIntegration(unittest.TestCase):
    """Integration test for graph analysis logic."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once."""
        cls.Session = sessionmaker(bind=engine)
        
    def setUp(self):
        """Set up before each test."""
        self.session = self.Session()
        self.test_prefix = f"graph_test_{int(datetime.now().timestamp())}"
        
    def tearDown(self):
        """Clean up after each test."""
        # Clean up database
        self.session.query(Tweet).filter(Tweet.tweet_id.like(f"{self.test_prefix}%")).delete()
        self.session.query(User).filter(User.user_id.like(f"{self.test_prefix}%")).delete()
        self.session.commit()
        self.session.close()

    def test_community_detection_logic(self):
        """Test building a graph and detecting communities with mixed signals."""
        # Setup: 4 users
        # 3 users are in a tight community (mentions + similar content)
        # 1 user is isolated
        
        # We'll make the 3 users high bot scores to test classification
        user_ids = [f"{self.test_prefix}_u{i}" for i in range(4)]
        handles = [f"g_user_{i}" for i in range(4)]
        
        for i in range(4):
            user = User(
                user_id=user_ids[i],
                handle=handles[i],
                bot_score=0.8 if i < 3 else 0.1 # Community of bots vs 1 organic
            )
            self.session.add(user)
            
        self.session.commit()
        
        # Add Mentions: u0 -> u1, u1 -> u2, u2 -> u0
        mentions_data = [
            (user_ids[0], [f"@{handles[1]}"]),
            (user_ids[1], [f"@{handles[2]}"]),
            (user_ids[2], [f"@{handles[0]}"])
        ]
        
        # Add similar embeddings to force similarity edges
        # Base vector
        base_emb = np.zeros(384)
        base_emb[0] = 1.0 # Simple distinct vector
        
        for i, (uid, mentions) in enumerate(mentions_data):
            # Create a few tweets per user to ensure they are found
            t = Tweet(
                tweet_id=f"{self.test_prefix}_t{i}",
                user_id=uid,
                handle=handles[i],
                text_raw=f"Bot content from {handles[i]} with {mentions[0]}",
                mentions=mentions,
                embedding=(base_emb + np.random.normal(0, 0.01, 384)).tolist() # Highly similar
            )
            self.session.add(t)
            
        # Add isolated user tweet with different embedding
        other_emb = np.zeros(384)
        other_emb[10] = 1.0 # Orthogonal
        t_iso = Tweet(
            tweet_id=f"{self.test_prefix}_t_iso",
            user_id=user_ids[3],
            handle=handles[3],
            text_raw="Organic isolated content",
            embedding=other_emb.tolist()
        )
        self.session.add(t_iso)
        self.session.commit()
        
        # Run Detection
        results = build_graph_and_detect()
        
        print(f"✅ Detection Results: {len(results)} communities found.")
        for r in results:
            print(f"   - ID: {r['community_id']}, Size: {r['size']}, Type: {r['type']}, BotScore: {r['avg_bot_score']}")
            
        # We expect at least one community containing the 3 bots
        # (It ignores tiny clusters < 3, so isolated users won't show)
        bot_communities = [r for r in results if r['type'] == 'BOT_CLUSTER']
        self.assertGreaterEqual(len(bot_communities), 1)
        self.assertEqual(bot_communities[0]['size'], 3)
        self.assertGreater(bot_communities[0]['avg_bot_score'], 0.7)

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INTEGRATION TEST 05: Community Graph Detection (Step 3→5→8)")
    print("="*70 + "\n")
    unittest.main(verbosity=2)
