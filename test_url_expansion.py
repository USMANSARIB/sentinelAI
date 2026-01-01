
import sys
import os
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models import Tweet, engine
from app.services.url_expander import expand_urls_sync

def test_url_expansion():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 1. Inject a REAL resolvable short URL for testing
    test_id = "url_test_123"
    real_short_url = "https://bit.ly/40K8XzN" # Example (usually redirects to google or something safe)
    
    # Cleanup previous test if exists
    session.query(Tweet).filter(Tweet.tweet_id == test_id).delete()
    
    test_tweet = Tweet(
        tweet_id=test_id,
        handle="url_tester",
        user_id="url_tester",
        text_raw=f"Check this out: {real_short_url}",
        urls=[real_short_url],
        expanded_urls=None
    )
    session.add(test_tweet)
    session.commit()
    
    print(f"[*] Injected test tweet with URL: {real_short_url}")

    # 2. Run Expansion Logic (Targeting ONLY our test tweet)
    tweets_to_expand = session.query(Tweet).filter(Tweet.tweet_id == test_id).all()
    
    if not tweets_to_expand:
        print("No URLs found to expand.")
        return

    all_urls = []
    for t in tweets_to_expand:
        all_urls.extend(t.urls)
    
    unique_urls = list(set(all_urls))
    print(f"[*] Expanding {len(unique_urls)} unique URLs...")
    
    results = expand_urls_sync(unique_urls)
    print(f"[*] Debug Results: {results}")
    url_map = {unique_urls[i]: results[i]['final_url'] for i in range(len(unique_urls))}
    
    # 3. Apply updates
    for t in tweets_to_expand:
        t.expanded_urls = [url_map.get(u, u) for u in t.urls]
    
    session.commit()
    
    # 4. Verify results
    updated = session.query(Tweet).filter(Tweet.tweet_id == test_id).first()
    print("\n[VERIFICATION RESULTS]:")
    print(f"  Original: {updated.urls}")
    print(f"  Expanded: {updated.expanded_urls}")
    
    # Check suspicious flagging in the model (via results)
    for res in results:
        if res.get('is_suspicious'):
            print(f"  [!] Flagged Suspicious Domain: {res['domain']}")

    session.close()

if __name__ == "__main__":
    test_url_expansion()
