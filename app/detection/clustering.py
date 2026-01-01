import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
from sklearn.cluster import HDBSCAN
from datetime import datetime, timedelta, timezone
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from app.models import Tweet, engine

Session = sessionmaker(bind=engine)

def detect_narratives():
    session = Session()
    print("[CLUSTERING] Starting narrative detection cycle...")
    
    # 1. Fetch recent tweets (All for now to ensure we capture the batch)
    # cutoff = datetime.now() - timedelta(hours=6)
    tweets = session.query(Tweet).filter(Tweet.embedding != None).limit(500).all()
    print(f"[CLUSTERING] Fetched {len(tweets)} tweets with embeddings from DB.")
    
    if len(tweets) < 5: # Lower threshold for demo
        print("[CLUSTERING] Not enough tweets to cluster (Need 5+).")
        session.close()
        return

    # 2. Extract Embeddings
    # Assuming embeddings are stored as list/vector in DB. 
    # pgvector returns numpy array or string depending on driver, but SQLAlchemy model should handle it?
    # Actually, we might need to cast or ensure they are lists.
    
    embeddings = [np.array(t.embedding) for t in tweets if t.embedding is not None]
    tweet_ids = [t.tweet_id for t in tweets if t.embedding is not None]
    
    if not embeddings:
        session.close()
        return

    data_matrix = np.vstack(embeddings).astype(np.float64)
    print(f"[CLUSTERING] Data Shape: {data_matrix.shape}")
    
    # 3. Cluster using HDBSCAN
    print(f"[CLUSTERING] Clustering {len(data_matrix)} tweets...")
    clusterer = HDBSCAN(min_cluster_size=5, min_samples=3, metric='euclidean')
    labels = clusterer.fit_predict(data_matrix)
    
    # 4. Update Database
    # Map label back to tweet
    # Label -1 is noise
    
    updates = 0
    unique_labels = set(labels)
    print(f"[CLUSTERING] Found {len(unique_labels) - (1 if -1 in unique_labels else 0)} clusters.")

    # We can do bulk update or iterate. 
    # For MVP, iterate is fine or batch update by ID.
    
    for t_id, label in zip(tweet_ids, labels):
        if label != -1:
            # Update tweet object
            # Ideally we'd do session.query(Tweet).filter...update
            # But we have the objects in memory if we kept them map-able
            # Optimization: filter query
            pass
            # session.query(Tweet).filter(Tweet.tweet_id == t_id).update({"narrative_id": int(label)})
            # updates += 1
            
    # Efficient update
    # Construct mappings
    mappings = []
    for t_id, label in zip(tweet_ids, labels):
        if label != -1:
            mappings.append({'tweet_id': t_id, 'narrative_id': int(label)})
            
    if mappings:
        session.bulk_update_mappings(Tweet, mappings)
        session.commit()
        print(f"[CLUSTERING] Updated {len(mappings)} tweets with narrative IDs.")
    
    # 5. Spike Detection (Volume Anomalies)
    # Group by narrative_id and check velocity
    detect_spikes(tweets, labels, session)
    
    session.close()

def detect_spikes(tweets, labels, session):
    # Convert to DataFrame for easier time grouping
    data = []
    for t, label in zip(tweets, labels):
        if label == -1: continue
        if not t.timestamp_absolute: continue
        data.append({
            'tweet_id': t.tweet_id,
            'narrative_id': label,
            'created_at': t.timestamp_absolute
        })
    
    if not data: return
    
    df = pd.DataFrame(data)
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # Iterate through narratives
    for narrative_id in df['narrative_id'].unique():
        narrative_df = df[df['narrative_id'] == narrative_id]
        
        # Calculate rates
        now = datetime.now(timezone.utc)
        last_hour = narrative_df[narrative_df['created_at'] >= (now - timedelta(hours=1))]
        current_rate = len(last_hour)
        
        # Simple baseline (avg per hour over full window, e.g. 6h)
        duration_hours = (narrative_df['created_at'].max() - narrative_df['created_at'].min()).total_seconds() / 3600
        duration_hours = max(duration_hours, 1) # Avoid div by zero
        baseline_rate = len(narrative_df) / duration_hours
        
        velocity = current_rate / max(baseline_rate, 0.1)
        print(f"   [DEBUG] Narrative {narrative_id}: Rate={current_rate}/hr, Baseline={baseline_rate:.2f}/hr, Velocity={velocity:.2f}x")
        
        if velocity >= 3.0 and current_rate > 5:
            print(f"[SPIKE DETECTED] Narrative {narrative_id}: Velocity {velocity:.1f}x (Rate: {current_rate}/hr)")
            # Log this spike? Create a 'Narrative' record?
            # PDF Step 4 Deliverables: "Spike detector flags 3x+ volume increases"
            # For now, just print. Ideally store in 'narratives' table.

if __name__ == "__main__":
    detect_narratives()
