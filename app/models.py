from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, Integer, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import os
import sys

# Add project root to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

Base = declarative_base()

class Tweet(Base):
    __tablename__ = 'tweets'

    tweet_id = Column(String, primary_key=True)
    handle = Column(String, nullable=False)
    text_raw = Column(Text, nullable=False)
    text_clean = Column(Text)
    text_hash = Column(String, index=True) # For duplicate detection
    
    # Features
    hashtags = Column(ARRAY(String))
    mentions = Column(ARRAY(String))
    urls = Column(ARRAY(String))
    expanded_urls = Column(ARRAY(String)) # Populated later
    
    # Metadata
    timestamp_absolute = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Embeddings (384 dim for all-MiniLM-L6-v2)
    embedding = Column(Vector(384))
    
    # Narrative Clustering (Step 4)
    narrative_id = Column(Integer, nullable=True)
    
    # Foreign Key (Loose)
    user_id = Column(String, index=True)

    def __repr__(self):
        return f"<Tweet(id={self.tweet_id}, handle={self.handle})>"

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True)
    handle = Column(String)
    display_name = Column(String)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    tweet_count = Column(Integer, default=0)
    account_created_at = Column(DateTime(timezone=True))
    
    # Bot Detection (Step 5)
    bot_score = Column(Float, default=0.0)
    bot_label = Column(String) # ORGANIC, SUSPICIOUS, BOT
    last_scraped_at = Column(DateTime(timezone=True), server_default=func.now())

# Database Connection
# Construct DB URL from config
DATABASE_URL = f"postgresql://{config.PG_USER}:{config.PG_PASS}@{config.PG_HOST}:{config.PG_PORT}/{config.PG_DB}"

engine = create_engine(DATABASE_URL)

def init_db():
    Base.metadata.create_all(engine)
