import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import time
import sys
import os
import redis
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
from app.models import engine, Tweet, User, Alert

st.set_page_config(page_title="SentinelGraph Command Center", layout="wide", page_icon="🛡️")

# --- CSS STYLING ---
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #00FF99;
    }
    .metric-label {
        font-size: 0.9em;
        color: #888;
    }
    .stDataFrame { border: 1px solid #333 !important; }
</style>
""", unsafe_allow_html=True)

Session = sessionmaker(bind=engine)

@st.cache_resource
def get_db_session():
    return Session()

@st.cache_resource
def get_redis_client():
    return redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)

def get_system_health():
    """Check queue sizes"""
    r = get_redis_client()
    try:
        suspect_queue = r.zcard(config.REDIS_SUSPECT_QUEUE_KEY)
        micro_stream = r.xlen(config.REDIS_STREAM_MICRO)
        minute_stream = r.xlen(config.REDIS_STREAM_MINUTE)
        hourly_stream = r.xlen(config.REDIS_STREAM_HOURLY)
        return {
            "suspect_queue": suspect_queue,
            "micro_stream": micro_stream,
            "minute_stream": minute_stream,
            "hourly_stream": hourly_stream,
            "status": "ONLINE"
        }
    except:
        return {"status": "OFFLINE", "suspect_queue": 0, "micro_stream": 0, "minute_stream": 0, "hourly_stream": 0}

def load_data():
    session = get_db_session()
    
    # 1. Core Stats
    total_tweets = session.query(func.count(Tweet.tweet_id)).scalar()
    total_users = session.query(func.count(User.user_id)).scalar()
    identified_bots = session.query(func.count(User.user_id)).filter(User.bot_score > 0.7).scalar()
    
    # 2. Recent Tweets (Live Feed)
    recent_tweets = pd.read_sql(
        session.query(Tweet.handle, Tweet.text_clean, Tweet.narrative_id, Tweet.timestamp_absolute)
        .order_by(Tweet.timestamp_absolute.desc())
        .limit(50)
        .statement,
        session.bind
    )
    
    # 3. Recent Alerts
    alerts = pd.read_sql(
        session.query(Alert.timestamp, Alert.alert_type, Alert.description, Alert.severity)
        .order_by(Alert.timestamp.desc())
        .limit(20)
        .statement,
        session.bind
    )
    
    # 4. Bot Stats
    top_bots = pd.read_sql(
        session.query(User.handle, User.bot_score, User.tweet_count, User.followers_count)
        .filter(User.bot_score > 0.6)
        .order_by(User.bot_score.desc())
        .limit(20)
        .statement,
        session.bind
    )

    session.close()
    
    return {
        "total_tweets": total_tweets,
        "total_users": total_users,
        "bots": identified_bots,
        "recent_df": recent_tweets,
        "alerts_df": alerts,
        "top_bots_df": top_bots
    }

# --- SIDEBAR ---
st.sidebar.title("SentinelGraph 🛡️")
st.sidebar.markdown("Layer 3 Surveillance System")
st.sidebar.markdown("---")
refresh_rate = st.sidebar.slider("Refresh Rate (s)", 2, 60, 5)
auto_refresh = st.sidebar.checkbox("Auto-Refresh", value=True)

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()

# --- HEADER ---
st.title("SentinelGraph Command Center")
health = get_system_health()

# Status Banner
if health["status"] == "ONLINE":
    st.success(f"SYSTEM ONLINE | Suspect Queue: {health['suspect_queue']} | Ingest Backlog: {health['micro_stream'] + health['minute_stream'] + health['hourly_stream']}")
else:
    st.error("SYSTEM OFFLINE - Redis Unreachable")

# --- KEY METRICS ---
data = load_data()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Tweets Analyzed", f"{data['total_tweets']:,}")
c2.metric("Profiles Tracked", f"{data['total_users']:,}")
c3.metric("Confirmed Bots", f"{data['bots']:,}")
c4.metric("Active Alerts", len(data['alerts_df']))

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🔴 Live Suspect Queue", "⚠️ System Alerts", "📉 Bot Analytics", "📥 Data Feed"])

with tab1:
    st.subheader("Layer 3 Priority Queue (Redis)")
    st.markdown("Users flagged by Scraper 1 & 2 for profiling by Scraper 3.")
    
    try:
        r = get_redis_client()
        # Fetch top 50 suspects
        suspects = r.zrevrange(config.REDIS_SUSPECT_QUEUE_KEY, 0, 49, withscores=True)
        if suspects:
            suspect_df = pd.DataFrame(suspects, columns=["Handle", "Risk Score"])
            suspect_df["Profile Url"] = suspect_df["Handle"].apply(lambda x: f"https://x.com/{x.replace('@','')}")
            
            # Display formatted table
            st.dataframe(
                suspect_df,
                column_config={
                    "Profile Url": st.column_config.LinkColumn("X Profile")
                },
                use_container_width=True,
                height=500
            )
        else:
            st.info("Suspect Queue is Empty. Good news?")
    except Exception as e:
        st.error(f"Redis Error: {e}")

with tab2:
    st.subheader("Recent System Alerts")
    if not data['alerts_df'].empty:
        for index, row in data['alerts_df'].iterrows():
            severity_color = "red" if row['severity'] == "CRITICAL" else "orange" if row['severity'] == "HIGH" else "blue"
            st.markdown(f"**[{row['timestamp']}]** <span style='color:{severity_color}'>{row['alert_type']}</span>: {row['description']}", unsafe_allow_html=True)
            st.divider()
    else:
        st.success("No active alerts.")

with tab3:
    st.subheader("Bot Network Detection")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### High Probability Bots")
        st.dataframe(data['top_bots_df'], use_container_width=True)
    
    with col2:
        st.markdown("### Score Distribution")
        if not data['top_bots_df'].empty:
            fig = px.histogram(data['top_bots_df'], x="bot_score", nbins=10, title="Bot Score Distribution")
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Raw Ingestion Stream")
    st.dataframe(data['recent_df'], use_container_width=True)