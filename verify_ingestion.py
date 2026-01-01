"""
Quick verification script to check if SentinelGraph database has ingested tweets.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.models import Tweet, User, engine, init_db

def check_database():
    print("=" * 60)
    print("SENTINELGRAPH DATABASE VERIFICATION")
    print("=" * 60)
    
    try:
        # Initialize database (ensures tables exist)
        init_db()
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Count tweets
        tweet_count = session.query(Tweet).count()
        user_count = session.query(User).count()
        
        print(f"\n✓ Database connection successful!")
        print(f"✓ Total tweets in database: {tweet_count}")
        print(f"✓ Total users in database: {user_count}")
        
        if tweet_count > 0:
            # Show sample tweets
            recent_tweets = session.query(Tweet).order_by(Tweet.created_at.desc()).limit(5).all()
            print(f"\n📊 Latest {min(5, tweet_count)} tweets:")
            print("-" * 60)
            for t in recent_tweets:
                print(f"  @{t.handle}: {t.text_raw[:60]}...")
                print(f"  ID: {t.tweet_id}, Narrative: {t.narrative_id}")
                print()
        else:
            print("\n⚠ No tweets found in database yet.")
            print("   Make sure to:")
            print("   1. Start Docker (docker-compose up -d)")
            print("   2. Run scrapers OR simulate traffic")
            print("   3. Start the ingestion pipeline (start_system.bat)")
        
        session.close()
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error connecting to database:")
        print(f"   {e}")
        print("\n💡 Make sure Docker is running:")
        print("   > docker-compose up -d")
        print("=" * 60)
        return False

if __name__ == "__main__":
    check_database()
