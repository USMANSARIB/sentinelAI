import networkx as nx
import numpy as np
from networkx.algorithms import community
import matplotlib.pyplot as plt
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from app.models import Tweet, User, engine

Session = sessionmaker(bind=engine)

def build_graph_and_detect():
    session = Session()
    print("[GRAPH] Building interaction graph...")
    
    # 1. Fetch recent tweets with embeddings
    # Limit to interact with manageable graph size for MVP
    tweets = session.query(Tweet).filter(Tweet.embedding != None).limit(2000).all()
    if not tweets:
        print("[GRAPH] No tweets with embeddings found.")
        session.close()
        return []
        
    users = session.query(User).all()
    user_map = {u.user_id: u for u in users}
    
    G = nx.Graph()
    
    # Add Nodes
    for u in users:
        G.add_node(u.user_id, bot_score=u.bot_score or 0.0, handle=u.handle)
        
    # Add Interaction Edges (Mentions)
    print("   Adding interaction edges...")
    for t in tweets:
        sender = t.user_id
        if not sender: continue
        
        # MENTION Edges (weight=0.5)
        if t.mentions:
            for mention_handle in t.mentions:
                target_handle = mention_handle.replace('@', '')
                # Find target user ID (assuming handle match for MVP)
                target_user = session.query(User).filter(User.handle == target_handle).first()
                
                if target_user:
                    target_id = target_user.user_id
                    if G.has_edge(sender, target_id):
                        G[sender][target_id]['weight'] += 0.5
                    else:
                        G.add_edge(sender, target_id, weight=0.5, type='MENTION')

    # Add Similarity Edges (Content-based)
    print("   Adding similarity edges...")
    similarity_pairs = find_similar_content_pairs(tweets)
    for user_a, user_b, similarity in similarity_pairs:
        # Ensure nodes exist (might be from tweets where user fetch missed?)
        if not G.has_node(user_a): G.add_node(user_a, bot_score=0)
        if not G.has_node(user_b): G.add_node(user_b, bot_score=0)
        
        if G.has_edge(user_a, user_b):
            G[user_a][user_b]['weight'] += similarity
        else:
            G.add_edge(user_a, user_b, weight=similarity, type='SIMILAR')
            
    print(f"[GRAPH] Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    
    if G.number_of_edges() == 0:
        print("[GRAPH] No edges found. Skipping community detection.")
        session.close()
        return []

    # 2. Detect Communities (Louvain)
    # Using 'weight' to determine strenght of connection
    try:
        communities = community.louvain_communities(G, weight='weight')
    except AttributeError:
        # Fallback if networkx version old (should be fine standard env)
        print("[WARN] Louvain not available, skipping.")
        session.close()
        return []
    
    results = []
    print(f"[GRAPH] Detected {len(communities)} communities.")
    
    for idx, members in enumerate(communities):
        members = list(members)
        if len(members) < 3: continue # Ignore tiny clusters
        
        # Calculate stats
        bot_scores = [G.nodes[n].get('bot_score', 0) for n in members]
        avg_bot_score = np.mean(bot_scores) if bot_scores else 0
        
        # Internal vs External Edges
        subgraph = G.subgraph(members)
        internal_edges = subgraph.number_of_edges()
        
        # Classification Logic
        comm_type = 'ORGANIC'
        if avg_bot_score > 0.6:
            comm_type = 'BOT_CLUSTER'
        elif len(members) > 10 and internal_edges / len(members) > 2.0:
            comm_type = 'COORDINATED_GROUP'
            
        if comm_type in ['BOT_CLUSTER', 'COORDINATED_GROUP']:
            print(f"      [L3] Flagging {len(members)} members of {comm_type} for profiling...")
            try:
                import redis
                import config
                r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
                for member_id in members:
                    # 'member_id' here is user_id (which is handle in our MVP logic for now, or mapped)
                    # Graph nodes were added as u.user_id. User ID in model is handle? 
                    # Let's check model definition... 
                    # Assuming u.user_id is the handle or something we can profile. 
                    # If it's internal ID, we need handle. 
                    # G.nodes[n] has 'handle'.
                    handle = G.nodes[member_id].get('handle')
                    if handle:
                        r.zincrby(config.REDIS_SUSPECT_QUEUE_KEY, 25, handle)
            except Exception as e:
                print(f"      [WARN] Redis Flagging Failed: {e}")

        results.append({
            'community_id': idx,
            'size': len(members),
            'avg_bot_score': round(avg_bot_score, 2),
            'type': comm_type,
            'density': nx.density(subgraph),
            'members_sample': members[:10] # Return first 10 IDs
        })
        
        print(f"   Community {idx}: {comm_type} (Size: {len(members)}, BotScore: {avg_bot_score:.2f})")
        
    session.close()
    return results

def find_similar_content_pairs(tweets):
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Group embeddings by User
    user_embeddings = {}
    for t in tweets:
        if not t.user_id or t.embedding is None: continue
        if t.user_id not in user_embeddings:
            user_embeddings[t.user_id] = []
        # Ensure embedding is numpy array (pgvector might return string or list)
        emb = np.array(t.embedding)
        user_embeddings[t.user_id].append(emb)
        
    # Average embedding per user
    user_avg = {}
    for uid, embs in user_embeddings.items():
        if embs:
            user_avg[uid] = np.mean(embs, axis=0)
            
    users = list(user_avg.keys())
    if len(users) < 2: return []
    
    matrix = np.array([user_avg[u] for u in users])
    sim_matrix = cosine_similarity(matrix)
    
    pairs = []
    # Upper triangle
    for i in range(len(users)):
        for j in range(i+1, len(users)):
            score = sim_matrix[i][j]
            if score > 0.85: # High similarity threshold
                pairs.append((users[i], users[j], float(score)))
                
    return pairs

if __name__ == "__main__":
    build_graph_and_detect()
