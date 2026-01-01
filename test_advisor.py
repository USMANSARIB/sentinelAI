
import sys
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models import Tweet, User, engine
from app.detection.origin import NarrativeAnalyzer
from app.services.advisor import Advisor

def test_advisor_logic():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 1. Get a Real Narrative (e.g. Narrative 0 which we know exists)
    narrative_query = text("SELECT narrative_id FROM tweets WHERE narrative_id IS NOT NULL GROUP BY narrative_id ORDER BY COUNT(*) DESC LIMIT 1")
    res = session.execute(narrative_query).fetchone()
    
    if not res:
        print("[FAIL] No narratives found in DB.")
        return
        
    narrative_id = res[0]
    print(f"[*] Analyzing Risk & Response for Narrative ID: {narrative_id}")
    
    # 2. Reconstruct Data Packet (Mirroring app/main.py logic)
    analyzer = NarrativeAnalyzer(session=session)
    origin_data = analyzer.find_narrative_origin(narrative_id)
    
    if not origin_data:
        print("[FAIL] Could not analyze origin.")
        return

    # Calculate mock signals for testing the scorer
    # In a real run, these come from their respective tables/microservices
    
    # Bot Ratio (from origin seeds)
    tweet_ids = origin_data['origin_seeds']
    if tweet_ids:
        users = session.query(User).join(Tweet, User.user_id == Tweet.user_id).filter(Tweet.tweet_id.in_(tweet_ids)).all()
        bot_count = sum(1 for u in users if (u.bot_score or 0) > 0.7)
        bot_ratio = bot_count / len(users) if users else 0.0
    else:
        bot_ratio = 0.0
        
    velocity = origin_data['velocity'].get('avg_velocity_per_hour', 0.0)
    
    # Construct input packet
    narrative_packet = {
        'title': f"Narrative #{narrative_id} (Viral Event)",
        'summary': "High velocity event detected involving multiple bot accounts.",
        'bot_ratio': bot_ratio,
        'velocity': velocity,
        'coordination_score': 0.8, # Mocked High Coordination for testing
        'suspicious_url_count': 2, # Mocked
        'keywords': ['crisis', 'urgent', 'scam'], # Mocked to trigger SCAM/PANIC logic
        'tweet_count': origin_data['total_volume']
    }
    
    print("\n[INPUT DATA]:")
    print(json.dumps(narrative_packet, indent=2))
    
    # 3. Generate Advice
    advisor = Advisor()
    advice = advisor.generate_advice(narrative_packet)
    
    # 4. Display Results
    print("\n" + "="*50)
    print("   ADVISORY COUNTERMEASURES REPORT")
    print("="*50)
    
    risk = advice['risk_report']
    print(f"\n[RISK ASSESSMENT]: Level {risk['risk_level']} ({risk['risk_score']})")
    print(f"Urgency: {risk['urgency']}")
    print("Breakdown:")
    for key, val in risk['breakdown'].items():
        if 'contribution' in val:
            print(f"  - {key}: {val['contribution']} (Value: {val.get('value') or val.get('count')})")

    timing = advice['timing_recommendation']
    print(f"\n[TIMING]: {timing['timing']} ({timing['priority']})")
    print(f"Window: {timing['timeframe']}")
    print(f"Rationale: {timing['rationale']}")
    
    strat = advice['recommended_strategy']
    print(f"\n[STRATEGY]: {strat['type']}")
    print(f"Tone: {strat['tone']}")
    print(f"Approach: {strat['approach']}")
    
    print(f"\n[DRAFT REPLY]:\n{advice['draft_reply']}")
    
    session.close()

if __name__ == "__main__":
    test_advisor_logic()
