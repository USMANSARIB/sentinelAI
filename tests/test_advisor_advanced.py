import unittest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.advisor import Advisor

class TestAdvisorAdvanced(unittest.TestCase):
    def setUp(self):
        self.advisor = Advisor()

    def test_response_timing_immediate(self):
        """Test HIGH risk + HIGH velocity -> IMMEDIATE response."""
        data = {
            'title': 'Viral Scam',
            'bot_ratio': 0.8,         # 0.24
            'velocity': 6.0,          # 0.25
            'coordination_score': 0.8, # 0.20
            'suspicious_url_count': 5, # 0.20
            # Total ~0.89 -> HIGH
            'keywords': ['scam', 'urgent']
        }
        advice = self.advisor.generate_advice(data)
        
        timing = advice['timing_recommendation']
        self.assertEqual(timing['timing'], 'IMMEDIATE')
        self.assertEqual(timing['priority'], 'P0')

    def test_response_strategy_defamation(self):
        """Test classification and strategy for defamation."""
        data = {
            'title': 'CEO Accusations',
            'bot_ratio': 0.1,
            'keywords': ['fraud', 'criminal', 'ceo'],
            'summary': 'Claims the CEO is a criminal'
        }
        advice = self.advisor.generate_advice(data)
        
        strategy = advice['recommended_strategy']
        self.assertEqual(strategy['type'], 'DEFAMATION')
        self.assertEqual(strategy['tone'], 'EVIDENCE_BASED')

    def test_evidence_packet_structure(self):
        """Test evidence extraction."""
        data = {'title': 'Test', 'bot_ratio': 0.5, 'velocity': 1.0}
        advice = self.advisor.generate_advice(data)
        
        evidence = advice['evidence_package']
        self.assertIn('report_id', evidence)
        self.assertIn('response_plan', evidence)

if __name__ == "__main__":
    unittest.main()
