
import sys
import os
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models import User, engine, Tweet
from app.detection.bot_detector import BotDetector

def test_bot_scoring():
    Session = sessionmaker(bind=engine)
    session = Session()
    detector = BotDetector()
    
    # 1. Fetch some users
    users = session.query(User).limit(10).all()
    if not users:
        print("No users found in database.")
        return

    print(f"{'Handle':<20} | {'Score':<6} | {'Label':<10} | {'Details'}")
    print("-" * 80)

    for user in users:
        try:
            score, label, details = detector.score_user(user, session)
            print(f"{user.handle:<20} | {score:<6} | {label:<10} | {details}")
            
            # Update DB to prove it works
            user.bot_score = score
            user.bot_label = label
            session.add(user)
        except Exception as e:
            print(f"Error scoring {user.handle}: {e}")
            import traceback
            traceback.print_exc()

    session.commit()
    print("-" * 80)
    print("Bot scoring simulation complete and saved to DB.")
    session.close()

if __name__ == "__main__":
    test_bot_scoring()
