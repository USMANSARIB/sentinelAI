"""
Integration Test 07: Risk Scoring and Advisory (Steps 4-9→10)

Tests the final analytical layer: the Advisor service.
This service takes inputs from all previous steps to generate a risk report.

This test validates:
- Weight-based risk calculation
- Response timing logic (IMMEDIATE vs MONITOR)
- Strategy selection (COORDINATED_BOT, SCAM, etc.)
- Evidence generation (structured report)
"""

import unittest
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.advisor import Advisor

class TestRiskScoringIntegration(unittest.TestCase):
    """Integration test for risk scoring and advisory logic."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once."""
        cls.advisor = Advisor()
        
    def test_high_risk_bot_attack_scenario(self):
        """Test a high-risk scenario involving bots, coordination, and suspicious URLs."""
        # Scenario: 80% bots, high coordination, high velocity, multiple suspicious URLs
        data = {
            'bot_ratio': 0.85,
            'coordination_score': 0.9,
            'velocity': 150.0, # Corrected key
            'suspicious_url_count': 3,
            'narrative_type': 'COORDINATED_BOT'
        }
        
        report = self.advisor.generate_advice(data)
        
        print("\n✅ High Risk Scenario Results:")
        print(f"   Risk Score: {report['risk_report']['risk_score']}")
        print(f"   Response Timing: {report['timing_recommendation']['timing']}")
        print(f"   Strategy: {report['recommended_strategy']['approach']}")
        
        self.assertGreater(report['risk_report']['risk_score'], 0.7)
        self.assertEqual(report['timing_recommendation']['timing'], 'IMMEDIATE')
        self.assertEqual(report['recommended_strategy']['tone'], 'TRANSPARENT') # Matches COACH_MODE classification

    def test_low_risk_organic_scenario(self):
        """Test a low-risk scenario involving mostly organic users."""
        # Scenario: 10% bots, no coordination, low velocity, no suspicious URLs
        data = {
            'bot_ratio': 0.1,
            'coordination_score': 0.1,
            'velocity': 1.0,
            'suspicious_url_count': 0,
            'narrative_type': 'ORGANIC'
        }
        
        report = self.advisor.generate_advice(data)
        
        print("\n✅ Low Risk Scenario Results:")
        print(f"   Risk Score: {report['risk_report']['risk_score']}")
        print(f"   Response Timing: {report['timing_recommendation']['timing']}")
        
        self.assertLess(report['risk_report']['risk_score'], 0.3)
        self.assertIn(report['timing_recommendation']['timing'], ['MONITOR', 'DELAY'])

    def test_scam_detection_strategy(self):
        """Test that SCAM narrative type triggers the correct strategy template."""
        data = {
            'bot_ratio': 0.5,
            'coordination_score': 0.5,
            'velocity': 20.0,
            'suspicious_url_count': 5,
            'summary': 'Double your investment now with this crypto link!'
        }
        
        report = self.advisor.generate_advice(data)
        
        print("\n✅ Scam Detection Results:")
        print(f"   Strategy approach: {report['recommended_strategy']['approach']}")
        
        self.assertIn("WARNING", report['draft_reply'])
        self.assertIn("known scam", report['draft_reply'])

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INTEGRATION TEST 07: Risk Scoring and Advisory (Steps 4-9→10)")
    print("="*70 + "\n")
    unittest.main(verbosity=2)
