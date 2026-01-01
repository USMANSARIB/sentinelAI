from datetime import timedelta
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class CoordinationDetector:
    def __init__(self, time_window_minutes=10, similarity_threshold=0.85):
        self.time_window = timedelta(minutes=time_window_minutes)
        self.similarity_threshold = similarity_threshold

    def detect_coordination(self, tweets):
        """
        Detects groups of accounts posting similar content in tight time windows.
        tweets: List of Tweet objects (SQLAlchemy)
        """
        clusters = []
        
        # 1. Exact Duplicates (Hash Groups)
        hash_groups = {}
        for t in tweets:
            if not t.text_hash: continue
            if t.text_hash not in hash_groups:
                hash_groups[t.text_hash] = []
            hash_groups[t.text_hash].append(t)
            
        for h, group in hash_groups.items():
            if len(group) < 3: continue # Need at least 3 accounts
            
            # Sort by time
            sorted_group = sorted(group, key=lambda x: x.timestamp_absolute or datetime.min)
            
            # Check time span of the group
            start_time = sorted_group[0].timestamp_absolute
            end_time = sorted_group[-1].timestamp_absolute
            
            if start_time and end_time and (end_time - start_time) <= self.time_window:
                # Check unique users
                users = set(t.user_id for t in sorted_group)
                if len(users) >= 3:
                    clusters.append({
                        'type': 'EXACT_MATCH',
                        'text_hash': h,
                        'users': list(users),
                        'tweet_ids': [t.tweet_id for t in sorted_group],
                        'tweet_count': len(sorted_group),
                        'time_span_seconds': (end_time - start_time).total_seconds(),
                        'sample_text': sorted_group[0].text_clean
                    })

        # 2. Semantic Similarity (Paraphrased)
        # Only check tweets that weren't already clustered? Or check all?
        # For performance, maybe subset.
        
        semantic_clusters = self.find_semantic_similarity(tweets)
        clusters.extend(semantic_clusters)
        
        return clusters

    def find_semantic_similarity(self, tweets):
        # Filter tweets with embeddings
        valid_tweets = [t for t in tweets if t.embedding is not None]
        if len(valid_tweets) < 3: return []
        
        embeddings = np.array([t.embedding for t in valid_tweets])
        sim_matrix = cosine_similarity(embeddings)
        
        clusters = []
        processed = set()
        
        for i in range(len(valid_tweets)):
            if i in processed: continue
            
            # Find similar
            similar_indices = np.where(sim_matrix[i] > self.similarity_threshold)[0]
            
            if len(similar_indices) >= 3:
                # Check time window
                group = [valid_tweets[j] for j in similar_indices]
                times = [t.timestamp_absolute for t in group if t.timestamp_absolute]
                
                if not times: continue
                
                time_span = max(times) - min(times)
                
                if time_span <= self.time_window:
                    users = set(t.user_id for t in group)
                    if len(users) >= 3:
                        clusters.append({
                            'type': 'SEMANTIC_SIMILARITY',
                            'users': list(users),
                            'tweet_ids': [t.tweet_id for t in group],
                            'avg_similarity': float(np.mean(sim_matrix[i][similar_indices])),
                            'time_span_seconds': time_span.total_seconds()
                        })
                        processed.update(similar_indices)
                        
        return clusters
