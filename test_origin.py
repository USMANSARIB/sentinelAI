
import sys
import os
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models import Tweet, engine
from app.detection.origin import NarrativeAnalyzer

def test_narrative_origin():
    Session = sessionmaker(bind=engine)
    session = Session()
    analyzer = NarrativeAnalyzer(session)
    
    from sqlalchemy import text
    
    # 1. Fetch most active narrative
    narrative_query = text("SELECT narrative_id, COUNT(*) as c FROM tweets WHERE narrative_id IS NOT NULL GROUP BY narrative_id ORDER BY c DESC LIMIT 1")
    res = session.execute(narrative_query).fetchone()
    
    if not res:
        print("No narratives found in DB. Run Step 4 (Clustering) first.")
        return

    target_id = res[0]
    print(f"[*] Analyzing Origin of Narrative ID: {target_id} ({res[1]} tweets)")
    
    # 2. Run Identification Logic
    origin_data = analyzer.find_narrative_origin(target_id)
    
    if not origin_data:
        print("[FAIL] Could not generate origin report.")
        return

    print("\n[ORIGIN IDENTIFIED]:")
    print(f"  - First Seen: {origin_data['first_seen']}")
    print(f"  - Origin Seeds Found: {origin_data['origin_seed_count']} tweets")
    print(f"  - Total Volume: {origin_data['total_volume']} tweets")
    
    print("\n[VELOCITY METRICS]:")
    metrics = origin_data['velocity']
    print(f"  - Average Velocity: {metrics['avg_velocity_per_hour']} tweets/hr")
    print(f"  - Peak Volume: {metrics['peak_volume']} (at {metrics['peak_time']})")
    print(f"  - Duration: {metrics['duration_hours']} hours")

    print("\n[TIMELINE SNIPPET] (First 3 Intervals):")
    for bucket in origin_data['timeline'][:3]:
        print(f"  - {bucket['time']}: {bucket['count']} tweets")

    # 3. List the culprit (Seed accounts)
    print("\n[SEED ACCOUNTS] (Potential Originators):")
    seed_ids = origin_data['origin_seeds'][:5]
    for tid in seed_ids:
        t = session.query(Tweet).filter(Tweet.tweet_id == tid).first()
        if t:
            print(f"  - @{t.handle} (Tweet: {t.tweet_id})")

    session.close()

if __name__ == "__main__":
    test_narrative_origin()
