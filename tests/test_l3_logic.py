
import unittest
from unittest.mock import MagicMock, patch
import networkx as nx
from datetime import datetime, timedelta

# Import the functions to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.detection.community import build_graph_and_detect
from app.detection.origin import NarrativeAnalyzer
from app.services.analyzer import job_url_expansion

class TestL3Logic(unittest.TestCase):

    @patch('app.detection.community.Session')
    @patch('redis.Redis')
    def test_community_flagging(self, mock_redis_cls, mock_session_cls):
        """Test if BOT_CLUSTER members are flagged to Redis"""
        print("\n[TEST] Verifying Community Detection Flagging...")
        
        # Mock Redis
        mock_redis = MagicMock()
        mock_redis_cls.return_value = mock_redis
        
        # Mock Session & DB Data
        mock_sess = MagicMock()
        mock_session_cls.return_value = mock_sess
        
        # Create Mock Users (Mock handle logic: G.nodes[id].get('handle'))
        # The build_graph function queries all users.
        u1 = MagicMock(user_id='u1', handle='bot1', bot_score=0.9)
        u2 = MagicMock(user_id='u2', handle='bot2', bot_score=0.9)
        u3 = MagicMock(user_id='u3', handle='bot3', bot_score=0.9)
        mock_sess.query().all.return_value = [u1, u2, u3]
        
        # Create Mock Tweets (Mentions to form a clique)
        # Mock return for query(Tweet)
        t1 = MagicMock(user_id='u1', mentions=['@bot2'], embedding=[0.1]*384)
        t2 = MagicMock(user_id='u2', mentions=['@bot3'], embedding=[0.1]*384)
        t3 = MagicMock(user_id='u3', mentions=['@bot1'], embedding=[0.1]*384)
        mock_sess.query().filter().limit().all.return_value = [t1, t2, t3]
        
        # Mock generic query().filter().first() for user lookup in graph
        def side_effect_filter(*args, **kwargs):
            mock_res = MagicMock()
            mock_res.first.return_value = u1 # Simplification: always find u1 so edges form
            return mock_res
        
        # It's hard to mock SQLAlchemy chaining perfectly.
        # Instead, we will Mock `community.louvain_communities` to return our fake community
        
        with patch('networkx.algorithms.community.louvain_communities') as mock_louvain:
            # Return one community with u1, u2, u3
            mock_louvain.return_value = [{'u1', 'u2', 'u3'}]
            
            # Run
            build_graph_and_detect()
            
            # Verify Redis Calls - Should flag 'bot1', 'bot2', 'bot3' (score 25)
            # Since we mocked user query to return objects with handles, the code G.nodes[n].get('handle') should work
            # because build_graph populates G nodes from u.
            
            calls = mock_redis.zincrby.call_args_list
            print(f"   Redis calls detected: {len(calls)}")
            
            handles_flagged = []
            for c in calls:
                args = c[0] # (key, score, value)
                if args[1] == 25:
                    handles_flagged.append(args[2])
            
            self.assertIn('bot1', handles_flagged)
            self.assertIn('bot2', handles_flagged)
            self.assertIn('bot3', handles_flagged)
            print("   [PASS] Community Flagging logic works.")

    @patch('app.detection.origin.Session')
    @patch('redis.Redis')
    def test_origin_flagging(self, mock_redis_cls, mock_session_cls):
        """Test if Narrative Origin seeds are flagged"""
        print("\n[TEST] Verifying Narrative Origin Flagging...")
        
        mock_redis = MagicMock()
        mock_redis_cls.return_value = mock_redis
        
        # Mock Tweets sorted by time
        base_time = datetime.now()
        t1 = MagicMock(tweet_id='t1', handle='patient_zero', timestamp_absolute=base_time)
        t2 = MagicMock(tweet_id='t2', handle='follower_1', timestamp_absolute=base_time + timedelta(minutes=5))
        # t3 is later
        t3 = MagicMock(tweet_id='t3', handle='late_comer', timestamp_absolute=base_time + timedelta(hours=2))
        
        analyzer = NarrativeAnalyzer(MagicMock())
        # Mock the query return
        analyzer.session.query().filter().order_by().all.return_value = [t1, t2, t3]
        
        analyzer.find_narrative_origin('n1')
        
        # Verify Redis (Score 30)
        calls = mock_redis.zincrby.call_args_list
        flagged = []
        for c in calls:
            if c[0][1] == 30:
                flagged.append(c[0][2])
        
        self.assertIn('patient_zero', flagged)
        self.assertIn('follower_1', flagged)
        self.assertNotIn('late_comer', flagged)
        print("   [PASS] Origin Flagging logic works.")

    @patch('app.services.analyzer.Session')
    @patch('redis.Redis')
    def test_fake_url_flagging(self, mock_redis_cls, mock_session_cls):
        """Test if Fake URLs trigger flagging"""
        print("\n[TEST] Verifying Fake URL Flagging...")
        
        mock_redis = MagicMock()
        mock_redis_cls.return_value = mock_redis
        
        mock_sess = MagicMock()
        mock_session_cls.return_value = mock_sess
        
        # Mock Tweet with URL
        t1 = MagicMock(tweet_id='t1', handle='scammer', urls=['http://short.ly/xyz'], expanded_urls=None)
        mock_sess.query().filter().filter().limit().all.return_value = [t1]
        
        # Mock Expansion Result
        with patch('app.services.analyzer.expand_urls_sync') as mock_expand:
            # Result format from expander
            mock_expand.return_value = [{'initial_url': 'http://short.ly/xyz', 'final_url': 'http://phishing-site.com/login'}]
            
            job_url_expansion()
            
            # Verify Redis (Score 40)
            mock_redis.zincrby.assert_called_with('queue:suspects', 40, 'scammer')
            print("   [PASS] Fake URL Flagging logic works.")

if __name__ == '__main__':
    unittest.main()
