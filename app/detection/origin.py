from datetime import timedelta
import pandas as pd
from sqlalchemy.orm import Session
from app.models import Tweet

class NarrativeAnalyzer:
    def __init__(self, session: Session):
        self.session = session

    def find_narrative_origin(self, narrative_id):
        # 1. Get Tweets
        tweets = self.session.query(Tweet).filter(Tweet.narrative_id == narrative_id).order_by(Tweet.timestamp_absolute.asc()).all()
        
        if not tweets:
            return None
            
        # 2. Origin Seeds (First 30 mins or First 10 tweets)
        first_tweet_time = tweets[0].timestamp_absolute
        cutoff_time = first_tweet_time + timedelta(minutes=30)
        
        origin_seeds = [t for t in tweets if t.timestamp_absolute <= cutoff_time]
        
        # 3. Spread Timeline
        timeline = self.build_spread_timeline(tweets)
        
        # 4. Velocity
        velocity_metrics = self.calculate_spread_metrics(timeline)
        
        # --- LAYER 3 FEEDER (Patient Zero) ---
        if origin_seeds:
            try:
                import redis
                import config
                r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
                print(f"   [L3] Flagging {len(origin_seeds)} origin seeds for profiling...")
                for t in origin_seeds:
                    if t.handle:
                        r.zincrby(config.REDIS_SUSPECT_QUEUE_KEY, 30, t.handle)
            except Exception as e:
                print(f"   [WARN] Redis Flagging Failed: {e}")
        
        return {
            'narrative_id': narrative_id,
            'first_seen': first_tweet_time,
            'origin_seed_count': len(origin_seeds),
            'origin_seeds': [t.tweet_id for t in origin_seeds],
            'total_volume': len(tweets),
            'timeline': timeline,
            'velocity': velocity_metrics
        }

    def build_spread_timeline(self, tweets):
        data = [{'timestamp': t.timestamp_absolute} for t in tweets if t.timestamp_absolute]
        if not data: return []
        
        df = pd.DataFrame(data)
        # Group by 5 min buckets
        df['time_bucket'] = df['timestamp'].dt.floor('5min')
        counts = df.groupby('time_bucket').size().to_dict()
        
        # Convert to list for JSON serialization
        timeline = [{'time': k.isoformat(), 'count': v} for k, v in sorted(counts.items())]
        return timeline

    def calculate_spread_metrics(self, timeline):
        if len(timeline) < 2: return {}
        
        # Find peak
        peak_bucket = max(timeline, key=lambda x: x['count'])
        
        # Simple velocity: total tweets / duration hours
        first = pd.to_datetime(timeline[0]['time'])
        last = pd.to_datetime(timeline[-1]['time'])
        duration = (last - first).total_seconds() / 3600
        
        total_tweets = sum(t['count'] for t in timeline)
        velocity = total_tweets / max(duration, 0.1)
        
        return {
            'peak_time': peak_bucket['time'],
            'peak_volume': peak_bucket['count'],
            'avg_velocity_per_hour': round(velocity, 2),
            'duration_hours': round(duration, 2)
        }
