# SentinelGraph Integration Map & Testing Plan

## System Architecture Flow (Steps 2-10)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION LAYER                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │   STEP 2: Data Collection     │
                    │   • scrp1.py, scrp2.py        │
                    │   • Playwright scrapers       │
                    │   • Output: raw_json/*.json   │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │   scripts/ingest.py           │
                    │   • Watches raw_json/         │
                    │   • Routes to Redis streams   │
                    │   • MICRO/MINUTE/HOURLY       │
                    └───────────────┬───────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                       PREPROCESSING LAYER                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │   STEP 3: Worker Processing   │
                    │   • app/worker.py             │
                    │   • Consumes Redis streams    │
                    │   • Cleaning (cleaner.py)     │
                    │   • Embeddings (SentenceT.)   │
                    │   • Upserts to PostgreSQL     │
                    └───────────────┬───────────────┘
                                    │
                            [PostgreSQL DB]
                            • tweets table
                            • users table
                            • pgvector embeddings
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                        ANALYTICAL LAYER                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼────────┐      ┌───────────▼────────┐      ┌──────────▼─────────┐
│ STEP 4:        │      │ STEP 5:            │      │ STEP 6:            │
│ Narratives     │      │ Bot Detection      │      │ Coordination       │
│ clustering.py  │      │ bot_detector.py    │      │ coordination.py    │
│                │      │                    │      │                    │
│ • HDBSCAN      │      │ • Heuristic scores │      │ • Sliding window   │
│ • Spike detect │      │ • Updates users    │      │ • Exact match      │
│ • narrative_id │      │   .bot_score       │      │ • Semantic similar │
└────────┬───────┘      └──────────┬─────────┘      └──────────┬─────────┘
         │                         │                           │
         │              ┌──────────▼──────────┐                │
         │              │ STEP 7:             │                │
         │              │ URL Expansion       │                │
         │              │ url_expander.py     │                │
         │              │                     │                │
         │              │ • Async HTTP        │                │
         │              │ • Redis cache       │                │
         │              │ • Suspicious flags  │                │
         │              └──────────┬──────────┘                │
         │                         │                           │
         └─────────────────────────┼───────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │ STEP 8:                     │
                    │ Community Detection         │
                    │ community.py                │
                    │                             │
                    │ • NetworkX graph            │
                    │ • Louvain algorithm         │
                    │ • Similarity edges          │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │ STEP 9:                     │
                    │ Origin Identification       │
                    │ origin.py                   │
                    │                             │
                    │ • Timeline reconstruction   │
                    │ • Patient Zero detection    │
                    │ • Velocity metrics          │
                    └──────────────┬──────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────────────┐
│                         ADVISORY LAYER                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │ STEP 10:                    │
                    │ Advisory Countermeasures    │
                    │ advisor.py                  │
                    │                             │
                    │ • RiskScorer                │
                    │ • ResponseAdvisor (timing)  │
                    │ • ReplyStrategySelector     │
                    │ • EvidenceGenerator         │
                    └──────────────┬──────────────┘
                                   │
                            [API Endpoints]
                            • /api/narratives
                            • /api/users/{handle}
                            • /api/communities
                            • /api/narratives/{id}/origin
                            • /api/narratives/{id}/advice
```

---

## Data Flow Dependencies

### Step 2 → Step 3
**Connection**: File-based → Redis Stream → Database
- **Output of Step 2**: `data/raw_json/*.json` files
- **Input to Step 3**: Redis streams (`MICRO`, `MINUTE`, `HOURLY`)
- **Bridge**: `scripts/ingest.py` (file watcher)

### Step 3 → Steps 4-10
**Connection**: PostgreSQL Database (shared state)
- **Output of Step 3**: 
  - `tweets` table with `embedding`, `text_clean`, `text_hash`
  - `users` table with account metadata
- **Consumed by**:
  - Step 4: Reads `tweets.embedding` for clustering
  - Step 5: Reads `users` + `tweets` for bot scoring
  - Step 6: Reads `tweets.text_hash`, `tweets.embedding`, `tweets.timestamp_absolute`
  - Step 7: Reads `tweets.urls`
  - Step 8: Reads `tweets` + `users` for graph construction
  - Step 9: Reads `tweets` filtered by `narrative_id`
  - Step 10: Aggregates data from all previous steps

### Step 4 → Step 9
**Connection**: `narrative_id` assignment
- **Output of Step 4**: Updates `tweets.narrative_id` (cluster assignment)
- **Input to Step 9**: Filters tweets by `narrative_id` to trace origin

### Step 5 → Step 8, Step 10
**Connection**: `bot_score` enrichment
- **Output of Step 5**: Updates `users.bot_score`, `users.bot_label`
- **Input to Step 8**: Uses `bot_score` for community classification
- **Input to Step 10**: Uses `bot_ratio` for risk scoring

### Step 6 → Step 10
**Connection**: Coordination detection results
- **Output of Step 6**: Coordination clusters (currently logged, not persisted)
- **Input to Step 10**: `coordination_score` (percentage of coordinated tweets)

### Step 7 → Step 10
**Connection**: URL analysis
- **Output of Step 7**: Updates `tweets.expanded_urls`, flags suspicious domains
- **Input to Step 10**: `suspicious_url_count` for risk scoring

### Steps 4-9 → Step 10
**Connection**: Aggregated intelligence
- Step 10 combines:
  - Narrative velocity (Step 4)
  - Bot ratio (Step 5)
  - Coordination score (Step 6)
  - Suspicious URLs (Step 7)
  - Community data (Step 8)
  - Origin timeline (Step 9)

---

## Integration Testing Plan

### Test 1: End-to-End Pipeline (Steps 2→3→4)
**Objective**: Verify data flows from scraper to clustered narratives

**Setup**:
1. Create synthetic tweet JSON file in `data/raw_json/`
2. Start infrastructure (Redis, PostgreSQL)
3. Start `scripts/ingest.py`
4. Start `app/worker.py`
5. Run `app/detection/clustering.py`

**Test Data**:
```json
{
  "tweet_id": "test_001",
  "handle": "testuser1",
  "text_raw": "Breaking: New crypto investment opportunity! #Bitcoin",
  "timestamp_absolute": "2025-12-30T20:00:00Z"
}
```

**Expected Results**:
- ✅ File appears in `data/processed_json/`
- ✅ Redis stream contains message
- ✅ PostgreSQL `tweets` table has record with `embedding`
- ✅ `narrative_id` is assigned (not -1)

**Validation Query**:
```sql
SELECT tweet_id, text_clean, narrative_id, embedding IS NOT NULL 
FROM tweets WHERE tweet_id = 'test_001';
```

---

### Test 2: Bot Detection Integration (Steps 3→5)
**Objective**: Verify bot scoring updates user records

**Setup**:
1. Insert test user with suspicious patterns
2. Run `app/services/analyzer.py` (job_bot_scoring)

**Test Data**:
```python
# Create user with bot indicators
user = User(
    user_id="bot_test_001",
    handle="bot_account",
    followers_count=10,
    following_count=5000,  # High ratio
    tweet_count=10000,     # High volume
    account_created_at=datetime.now() - timedelta(days=5)  # New account
)
```

**Expected Results**:
- ✅ `users.bot_score` > 0.7
- ✅ `users.bot_label` = 'BOT'

**Validation**:
```python
user = session.query(User).filter(User.user_id == "bot_test_001").first()
assert user.bot_score > 0.7
```

---

### Test 3: Coordination Detection (Steps 3→6)
**Objective**: Verify sliding window detects coordinated posting

**Setup**:
1. Insert 3+ tweets with identical `text_hash` within 10 minutes
2. Run `app/detection/coordination.py`

**Test Data**:
```python
base_time = datetime.now()
tweets = [
    Tweet(tweet_id=f"coord_{i}", user_id=f"user_{i}", 
          text_hash="abc123", timestamp_absolute=base_time + timedelta(minutes=i))
    for i in range(3)
]
```

**Expected Results**:
- ✅ Coordination cluster detected
- ✅ Cluster contains 3 users
- ✅ Time window < 10 minutes

**Validation**:
```python
detector = CoordinationDetector()
clusters = detector.detect_coordination(tweets)
assert len(clusters) > 0
assert clusters[0]['type'] == 'EXACT_MATCH'
```

---

### Test 4: URL Expansion (Steps 3→7)
**Objective**: Verify URL unshortening and caching

**Setup**:
1. Insert tweet with shortened URL
2. Run `app/services/analyzer.py` (job_url_expansion)

**Test Data**:
```python
tweet = Tweet(
    tweet_id="url_test_001",
    urls=["https://bit.ly/test123"]
)
```

**Expected Results**:
- ✅ `tweets.expanded_urls` populated
- ✅ Redis cache contains entry
- ✅ Suspicious domain flagged if applicable

**Validation**:
```python
tweet = session.query(Tweet).filter(Tweet.tweet_id == "url_test_001").first()
assert tweet.expanded_urls is not None
assert len(tweet.expanded_urls) > 0
```

---

### Test 5: Community Graph (Steps 3→5→8)
**Objective**: Verify graph construction and Louvain clustering

**Setup**:
1. Insert users with mention relationships
2. Ensure bot scores are calculated
3. Run `app/detection/community.py`

**Test Data**:
```python
# User A mentions B, B mentions C, C mentions A (triangle)
tweets = [
    Tweet(user_id="A", mentions=["@B"]),
    Tweet(user_id="B", mentions=["@C"]),
    Tweet(user_id="C", mentions=["@A"])
]
```

**Expected Results**:
- ✅ Graph has 3 nodes, 3 edges
- ✅ Community detected (size 3)
- ✅ Community type classified (ORGANIC/BOT_CLUSTER)

**Validation**:
```python
results = build_graph_and_detect()
assert len(results) > 0
assert results[0]['size'] >= 3
```

---

### Test 6: Origin Tracing (Steps 3→4→9)
**Objective**: Verify Patient Zero identification

**Setup**:
1. Insert tweets with same `narrative_id` at different times
2. Run `app/detection/origin.py`

**Test Data**:
```python
base_time = datetime.now() - timedelta(hours=2)
tweets = [
    Tweet(narrative_id=1, timestamp_absolute=base_time),  # Origin
    Tweet(narrative_id=1, timestamp_absolute=base_time + timedelta(minutes=30)),
    Tweet(narrative_id=1, timestamp_absolute=base_time + timedelta(hours=1))
]
```

**Expected Results**:
- ✅ First tweet identified as origin seed
- ✅ Timeline has 5-minute buckets
- ✅ Velocity calculated correctly

**Validation**:
```python
analyzer = NarrativeAnalyzer(session)
result = analyzer.find_narrative_origin(narrative_id=1)
assert result['first_seen'] == base_time
assert len(result['timeline']) > 0
```

---

### Test 7: Risk Scoring (Steps 4→5→6→7→10)
**Objective**: Verify weighted risk aggregation

**Setup**:
1. Create narrative with known risk factors
2. Run `app/services/advisor.py`

**Test Data**:
```python
narrative_data = {
    'bot_ratio': 0.8,              # 30% * 0.8 = 0.24
    'velocity': 5.0,               # (5-1)/4 = 1.0 * 25% = 0.25
    'coordination_score': 0.9,     # 25% * 0.9 = 0.225
    'suspicious_url_count': 10     # min(10/5, 1) * 20% = 0.20
    # Total = 0.915 -> HIGH
}
```

**Expected Results**:
- ✅ `risk_score` ≈ 0.915
- ✅ `risk_level` = 'HIGH'
- ✅ `urgency` = 'CRITICAL'
- ✅ Timing recommendation = 'IMMEDIATE' (if velocity >= 3.0)

**Validation**:
```python
advisor = Advisor()
advice = advisor.generate_advice(narrative_data)
assert advice['risk_report']['risk_level'] == 'HIGH'
assert advice['timing_recommendation']['priority'] == 'P0'
```

---

### Test 8: API Integration (All Steps)
**Objective**: Verify all API endpoints return correct data

**Test Endpoints**:
1. `GET /api/stats` - Dashboard KPIs
2. `GET /api/narratives` - Narrative list with spike flags
3. `GET /api/users/{handle}` - Bot score for user
4. `GET /api/communities` - Graph communities
5. `GET /api/narratives/{id}/origin` - Origin analysis
6. `GET /api/narratives/{id}/advice` - Risk + strategy

**Setup**:
1. Populate database with test data
2. Start FastAPI server (`uvicorn app.main:app`)
3. Make HTTP requests

**Expected Results**:
```bash
curl http://localhost:8000/api/narratives
# Should return JSON array with narratives

curl http://localhost:8000/api/users/testuser
# Should return bot_score, label, details

curl http://localhost:8000/api/narratives/1/advice
# Should return risk_report, timing, strategy, draft_reply
```

---

## Integration Test Execution (Implemented)

**Test Suite**: `tests/integration_test_*.py`

**Coverage**:
*   `integration_test_01_ingestion_pipeline.py`: Ingestion (Redis → DB)
*   `integration_test_02_bot_detection.py`: Bot Detection Logic
*   `integration_test_03_coordination.py`: Coordination & Semantic Clustering
*   `integration_test_04_url_expansion.py`: URL Expansion & Threat Intel
*   `integration_test_05_community_graph.py`: Community Graph Detection
*   `integration_test_06_origin_tracing.py`: Origin Tracing
*   `integration_test_07_risk_scoring.py`: Risk Scoring & Advisory
*   `integration_test_08_api_endpoints.py`: API Endpoints

**Run All Tests**:
```powershell
python -m unittest discover tests "integration_test_*.py"
```

---

## Critical Integration Points

### 1. **Redis → PostgreSQL** (Step 2→3)
- **Risk**: Message loss if worker crashes
- **Mitigation**: Redis persistence, consumer groups

### 2. **Embedding Consistency** (Step 3→4,6,8)
- **Risk**: Model version mismatch
- **Mitigation**: Pin `sentence-transformers==2.2.2`, `all-MiniLM-L6-v2`

### 3. **Narrative ID Propagation** (Step 4→9)
- **Risk**: Tweets without `narrative_id` break origin tracing
- **Mitigation**: Default to `-1`, filter in queries

### 4. **Bot Score Availability** (Step 5→8,10)
- **Risk**: Null `bot_score` breaks calculations
- **Mitigation**: Default to `0.0` in queries

### 5. **Coordination Storage** (Step 6→10)
- **Risk**: Coordination results not persisted
- **Mitigation**: Add `coordination_clusters` table (future)

### 6. **API Response Time** (Step 10)
- **Risk**: On-demand graph analysis slow
- **Mitigation**: Cache results, background jobs

---

## Success Criteria

✅ **Pipeline Completeness**: Data flows from scraper to advisory without manual intervention  
✅ **Data Integrity**: No null embeddings, all foreign keys valid  
✅ **Performance**: Worker processes 100 tweets/minute  
✅ **Accuracy**: Bot detection >80% precision on test set  
✅ **API Latency**: All endpoints respond <2 seconds  
✅ **Test Coverage**: All integration tests pass

---

## Next Steps

1. **Create Master Integration Test** (`tests/test_integration_full.py`)
2. **Run Full Pipeline Test** with synthetic data
3. **Measure Performance** (throughput, latency)
4. **Document Edge Cases** (empty narratives, single-user clusters)
5. **Build Dashboard** (Streamlit visualization)
