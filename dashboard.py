import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import time
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
from app.models import engine, Tweet, User

st.set_page_config(page_title="SentinelGraph Dashboard", layout="wide", page_icon="🛡️")

Session = sessionmaker(bind=engine)

@st.cache_resource
def get_db_session():
    return Session()

def load_data():
    session = get_db_session()
    
    # 1. Total Stats
    total_tweets = session.query(func.count(Tweet.tweet_id)).scalar()
    total_users = session.query(func.count(User.user_id)).scalar()
    identified_bots = session.query(func.count(User.user_id)).filter(User.bot_score > 0.7).scalar()
    active_narratives = session.query(func.count(func.distinct(Tweet.narrative_id))).filter(Tweet.narrative_id != -1).scalar()
    
    # 2. Recent Tweets
    recent_tweets = pd.read_sql(
        session.query(Tweet.handle, Tweet.text_clean, Tweet.narrative_id, Tweet.timestamp_absolute)
        .order_by(Tweet.timestamp_absolute.desc())
        .limit(100)
        .statement,
        session.bind
    )
    
    # 3. Narratives
    narrative_stats = pd.read_sql(
        session.query(Tweet.narrative_id, func.count(Tweet.tweet_id).label('count'))
        .filter(Tweet.narrative_id != None)
        .filter(Tweet.narrative_id != -1)
        .group_by(Tweet.narrative_id)
        .order_by(func.count(Tweet.tweet_id).desc())
        .limit(20)
        .statement,
        session.bind
    )
    
    session.close()
    return {
        "total_tweets": total_tweets,
        "total_users": total_users,
        "bots": identified_bots,
        "narratives": active_narratives,
        "recent_df": recent_tweets,
        "narrative_df": narrative_stats
    }

# Sidebar
st.sidebar.title("SentinelGraph 🛡️")
st.sidebar.markdown("---")
refresh = st.sidebar.button("Refresh Data")
auto_refresh = st.sidebar.checkbox("Auto-Refresh (5s)", value=False)

if auto_refresh:
    time.sleep(5)
    st.rerun()

# Main Layout
st.title("Narrative Detection & Analysis System")

# Load Data
try:
    data = load_data()
    
    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tweets", data["total_tweets"])
    c2.metric("Tracked Users", data["total_users"])
    c3.metric("High-Conf Bots", data["bots"])
    c4.metric("Active Narratives", data["narratives"])
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🚀 Live Feed", "🧬 Narrative Analysis", "🤖 Bot Detection"])
    
    with tab1:
        st.subheader("Real-time Ingestion Stream")
        if not data["recent_df"].empty:
            st.dataframe(
                data["recent_df"][['handle', 'text_clean', 'narrative_id', 'timestamp_absolute']],
                use_container_width=True,
                height=400
            )
        else:
            st.info("No tweets found in database yet. Run the mock generator or scrapers.")

    with tab2:
        st.subheader("Top Detected Narratives (Clusters)")
        col_chart, col_details = st.columns([2, 1])
        
        with col_chart:
            if not data["narrative_df"].empty:
                fig = px.bar(data["narrative_df"], x='narrative_id', y='count', title="Tweets per Narrative Cluster")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No narratives clustered yet.")
                
        with col_details:
            st.markdown("### Deep Dive")
            if not data["narrative_df"].empty:
                selected_id = st.selectbox("Select Narrative ID", data["narrative_df"]['narrative_id'])
                
                # Fetch samples for this narrative
                session = get_db_session()
                samples = session.query(Tweet.text_clean).filter(Tweet.narrative_id == int(selected_id)).limit(3).all()
                session.close()
                
                st.markdown(f"**Sample Content for ID {selected_id}:**")
                for s in samples:
                    st.info(f"\"{s[0]}\"")

    with tab3:
        st.subheader("Bot Network Analysis")
        # Fetch top bot scores
        session = get_db_session()
        bots = pd.read_sql(
            session.query(User.handle, User.bot_score, User.tweet_count, User.followers_count)
            .filter(User.bot_score > 0.5)
            .order_by(User.bot_score.desc())
            .limit(50)
            .statement,
            session.bind
        )
        session.close()
        
        if not bots.empty:
            st.dataframe(bots, use_container_width=True)
            
            fig_bot = px.scatter(bots, x='tweet_count', y='bot_score', size='followers_count', hover_name='handle',
                                 title="Bot Score vs Activity")
            st.plotly_chart(fig_bot)
        else:
            st.success("No high-probability bots detected yet.")

except Exception as e:
    st.error(f"Database Connection Error: {e}")
    st.markdown("Ensure PostgreSQL is running and `config.py` is correct.")