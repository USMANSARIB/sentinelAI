import unittest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.advisor import Advisor

class TestAdvisor(unittest.TestCase):
    def setUp(self):
        self.advisor = Advisor()

    def test_high_risk_bot_campaign(self):
        """Test risk aggregation and transparent strategy selection."""
        narrative = {
            'title': 'Crypto Scam',
            'bot_ratio': 0.8,         # 30% * 0.8 = 0.24
            'velocity': 6.0,          # (6-1)/4 = 1.25 -> 1.0 * 25% = 0.25
            'coordination_score': 0.9,# 0.9 * 25% = 0.225
            'suspicious_url_count': 10,# 1.0 * 20% = 0.20
            'keywords': ['crypto', 'guarantee']
        }
        # Expected Total: 0.24 + 0.25 + 0.225 + 0.20 = 0.915 -> HIGH Risk
        
        advice = self.advisor.generate_advice(narrative)
        report = advice['risk_report']
        strategy = advice['recommended_strategy']
        
        self.assertEqual(report['risk_level'], 'HIGH')
        self.assertGreater(report['risk_score'], 0.9)
        
        # Strategy should be SCAM oriented
        self.assertEqual(strategy['tone'], 'FIRM')
        self.assertIn('fraudulent', strategy['template'])

    def test_panic_narrative(self):
        """Test logic for panic mitigation strategy."""
        narrative = {
            'title': 'Bank Run',
            'bot_ratio': 0.1,
            'velocity': 2.0,
            'keywords': ['collapse', 'danger']
        }
        
        advice = self.advisor.generate_advice(narrative)
        strategy = advice['recommended_strategy']
        
        self.assertEqual(strategy['tone'], 'CALM')
        self.assertIn('Official Update', strategy['template'])

if __name__ == "__main__":
    unittest.main()
