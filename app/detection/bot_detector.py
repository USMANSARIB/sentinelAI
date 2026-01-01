from datetime import datetime, timezone
import math
from sqlalchemy.orm import Session
from app.models import User, Tweet

class BotDetector:
    def __init__(self):
        self.weights = {
            'posting_frequency': 0.30,
            'account_age': 0.25,
            'follower_ratio': 0.20,
            'repeat_text': 0.25
        }

    def score_user(self, user: User, db_session: Session):
        score = 0.0
        details = {}
        
        # 1. Posting Frequency (Tweets per day)
        account_age_days = 1
        if user.account_created_at:
            # Handle timezone awareness
            now = datetime.now(timezone.utc)
            if user.account_created_at.tzinfo is None:
                # Fallback if DB returns naive
                age_delta = datetime.utcnow() - user.account_created_at
            else:
                age_delta = now - user.account_created_at
            
            account_age_days = max(age_delta.days, 1)
        
        count = user.tweet_count if user.tweet_count else 0
        posts_per_day = count / account_age_days
        
        # Logic: Suspicious > 50, Bot > 100
        # Score = min(ppd / 100, 1.0)
        freq_score = min(posts_per_day / 100.0, 1.0) 
        score += freq_score * self.weights['posting_frequency']
        details['freq_score'] = round(freq_score, 2)
        details['posts_per_day'] = round(posts_per_day, 1)

        # 2. Account Age
        age_score = 0.0
        if account_age_days < 7:
            age_score = 1.0
        elif account_age_days < 30:
            age_score = 0.7
        elif account_age_days < 90:
            age_score = 0.3
        
        score += age_score * self.weights['account_age']
        details['age_score'] = age_score
        details['account_age_days'] = account_age_days

        # 3. Follower Ratio
        # ratio = followers / following
        following = max(user.following_count, 1)
        ratio = user.followers_count / following
        
        ratio_score = 0.0
        if ratio < 0.1 or ratio > 10:
            ratio_score = 0.8
        elif ratio < 0.3 or ratio > 5:
            ratio_score = 0.5
        
        score += ratio_score * self.weights['follower_ratio']
        details['ratio_score'] = ratio_score
        details['follower_ratio'] = round(ratio, 2)

        # 4. Repeat Text Ratio
        repeat_ratio = self.calculate_repeat_ratio(user.user_id, db_session)
        # Logic: min(ratio/0.5, 1.0)
        repeat_score = min(repeat_ratio / 0.5, 1.0)
        
        score += repeat_score * self.weights['repeat_text']
        details['repeat_score'] = round(repeat_score, 2)
        details['repeat_ratio'] = round(repeat_ratio, 2)
        
        # Classification
        label = 'ORGANIC'
        if score >= 0.7:
            label = 'BOT'
        elif score >= 0.4:
            label = 'SUSPICIOUS'
            
        return round(score, 3), label, details

    def calculate_repeat_ratio(self, user_id, session):
        # PDF: 1 - (unique_hashes / total_tweets)
        # Limit to last 50 tweets for speed
        tweets = session.query(Tweet.text_hash).filter(Tweet.user_id == user_id).limit(50).all()
        if not tweets:
            return 0.0
        
        hashes = [t[0] for t in tweets if t[0]]
        if not hashes: 
            return 0.0
            
        unique_hashes = set(hashes)
        
        return 1.0 - (len(unique_hashes) / len(hashes))
