
import sys
import os
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models import Tweet, User, engine
from app.detection.coordination import CoordinationDetector

def test_coordination_detection():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Fetch recent tweets (last 24 hours)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    tweets = session.query(Tweet).filter(Tweet.timestamp_absolute > cutoff).limit(2000).all()
    
    print(f"[*] Analyzing {len(tweets)} recent tweets for coordination...")
    
    # 1. Run Coordination Detector on ACTUAL Data
    detector = CoordinationDetector(time_window_minutes=30, similarity_threshold=0.90)
    clusters = detector.detect_coordination(tweets)
    
    if clusters:
        print(f"\n[!] DETECTED {len(clusters)} COORDINATION CLUSTERS IN ACTUAL DATA:")
        for i, c in enumerate(clusters):
            print(f"Cluster {i+1} ({c['type']}):")
            print(f"  - Users Involved: {len(c['users'])} accounts ({', '.join(c['users'][:3])}...)")
            print(f"  - Time Span: {c['time_span_seconds']} seconds")
            if c['type'] == 'EXACT_MATCH':
                print(f"  - Sample Text: {c['sample_text']}")
            else:
                print(f"  - Avg Similarity: {c['avg_similarity']:.2f}")
    else:
        print("\n[OK] No coordination clusters found in actual data (Normal for organic traffic).")

    # 2. SIMULATION to prove the SLIDING WINDOW and LOGIC work
    print("\n" + "="*50)
    print("[*] SIMULATING COORDINATED ATTACK (Sliding Window Test)...")
    
    # Create 5 fake tweets from 5 different users with same text hash and tight timestamps
    fake_hash = "fake_attack_hash_123"
    fake_text = "🚨 COORDINATED ATTACK SIMULATION 🚨 Detect me!"
    base_time = datetime.now(timezone.utc)
    
    fake_tweets = []
    for i in range(5):
        t = Tweet(
            tweet_id=f"sim_attack_{i}",
            handle=f"bot_account_{i}",
            user_id=f"bot_account_{i}",
            text_raw=fake_text,
            text_clean=fake_text,
            text_hash=fake_hash,
            timestamp_absolute=base_time + timedelta(seconds=i*10), # Every 10 seconds (Total 40s)
            embedding=[0.1] * 384 # Dummy embedding
        )
        fake_tweets.append(t)
    
    # Run detector on simulated data
    sim_clusters = detector.detect_coordination(fake_tweets)
    
    if sim_clusters:
        print(f"\n[OK] SIMULATION SUCCESS: Logic detected the coordinated attack!")
        for c in sim_clusters:
            print(f"   Detected {c['type']} with {len(c['users'])} accounts across {c['time_span_seconds']}s window.")
    else:
        print("\n[FAIL] Simulation failed to detect coordination.")

    session.close()

if __name__ == "__main__":
    test_coordination_detection()
