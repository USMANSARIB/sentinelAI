
import React from 'react';
import { Database, Zap, Layers, Cpu, Search, Activity, Terminal, Code2 } from 'lucide-react';

export const Architecture: React.FC = () => {
  return (
    <div className="space-y-16 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center space-y-4">
        <h2 className="text-3xl font-bold text-white">System Architecture</h2>
        <p className="text-slate-400 max-w-2xl mx-auto">
          Built on a modular microservices pattern, SentinelGraph orchestrates distributed scrapers 
          and high-performance analytical engines to process petabytes of social graph data.
        </p>
      </div>

      {/* Visual Pipeline */}
      <div className="relative grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Layer 1: Ingestion */}
        <div className="relative group">
          <div className="absolute inset-0 bg-cyan-500/5 rounded-3xl blur-xl group-hover:bg-cyan-500/10 transition-all"></div>
          <div className="relative p-6 bg-slate-900 border border-slate-800 rounded-2xl h-full flex flex-col">
            <div className="p-3 bg-cyan-500/20 rounded-xl text-cyan-400 w-fit mb-4">
              <Zap size={24} />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Ingestion Layer</h3>
            <p className="text-sm text-slate-400 flex-grow">
              Distributed Playwright scrapers capture raw social signals. Orchestrator manages dynamic scaling and routing.
            </p>
            <div className="mt-4 pt-4 border-t border-slate-800 text-[10px] font-mono text-slate-500 space-y-1">
              <div>> scrapy.py: instance_init()</div>
              <div>> playwright.chromium: headless=True</div>
              <div>> data/raw_json/: landing_zone</div>
            </div>
          </div>
          <div className="hidden lg:block absolute top-1/2 -right-6 -translate-y-1/2 z-10">
             <div className="h-0.5 w-6 bg-slate-800"></div>
          </div>
        </div>

        {/* Layer 2: Event Bus */}
        <div className="relative group">
          <div className="absolute inset-0 bg-blue-500/5 rounded-3xl blur-xl group-hover:bg-blue-500/10 transition-all"></div>
          <div className="relative p-6 bg-slate-900 border border-slate-800 rounded-2xl h-full flex flex-col">
            <div className="p-3 bg-blue-500/20 rounded-xl text-blue-400 w-fit mb-4">
              <Layers size={24} />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Event Bus & Cache</h3>
            <p className="text-sm text-slate-400 flex-grow">
              Redis Streams act as the backbone, routing payloads into micro, minute, and hourly processing queues.
            </p>
            <div className="mt-4 pt-4 border-t border-slate-800 text-[10px] font-mono text-slate-500 space-y-1">
              <div>> redis.xadd(STREAM_KEY)</div>
              <div>> worker.py: consumer_group_read</div>
              <div>> pydantic: schema_validate()</div>
            </div>
          </div>
          <div className="hidden lg:block absolute top-1/2 -right-6 -translate-y-1/2 z-10">
             <div className="h-0.5 w-6 bg-slate-800"></div>
          </div>
        </div>

        {/* Layer 3: Intelligence */}
        <div className="relative group">
          <div className="absolute inset-0 bg-purple-500/5 rounded-3xl blur-xl group-hover:bg-purple-500/10 transition-all"></div>
          <div className="relative p-6 bg-slate-900 border border-slate-800 rounded-2xl h-full flex flex-col">
            <div className="p-3 bg-purple-500/20 rounded-xl text-purple-400 w-fit mb-4">
              <Cpu size={24} />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Intelligence Engine</h3>
            <p className="text-sm text-slate-400 flex-grow">
              HDBSCAN narrative clustering and Louvain community detection run concurrently with pgvector similarity search.
            </p>
            <div className="mt-4 pt-4 border-t border-slate-800 text-[10px] font-mono text-slate-500 space-y-1">
              <div>> sklearn: hdbscan.fit()</div>
              <div>> pgvector: operator(&lt;=&gt;)</div>
              <div>> networkx: louvain_communities()</div>
            </div>
          </div>
          <div className="hidden lg:block absolute top-1/2 -right-6 -translate-y-1/2 z-10">
             <div className="h-0.5 w-6 bg-slate-800"></div>
          </div>
        </div>

        {/* Layer 4: Storage & API */}
        <div className="relative group">
          <div className="absolute inset-0 bg-emerald-500/5 rounded-3xl blur-xl group-hover:bg-emerald-500/10 transition-all"></div>
          <div className="relative p-6 bg-slate-900 border border-slate-800 rounded-2xl h-full flex flex-col">
            <div className="p-3 bg-emerald-500/20 rounded-xl text-emerald-400 w-fit mb-4">
              <Database size={24} />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Persistence & API</h3>
            <p className="text-sm text-slate-400 flex-grow">
              PostgreSQL stores the persistent graph. FastAPI serves clean RESTful endpoints for the frontend dashboard.
            </p>
            <div className="mt-4 pt-4 border-t border-slate-800 text-[10px] font-mono text-slate-500 space-y-1">
              <div>> sqlalchemy: session.commit()</div>
              <div>> fastapi: router.get('/narratives')</div>
              <div>> uvicorn: server_up</div>
            </div>
          </div>
        </div>
      </div>

      {/* Code Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <h3 className="text-2xl font-bold text-white flex items-center gap-2">
            <Code2 className="text-cyan-500" /> Technical Logic
          </h3>
          <div className="space-y-4">
            <div className="p-5 bg-slate-900/50 rounded-xl border border-slate-800">
              <h4 className="text-white font-bold mb-2">Phase 1: Ingestion</h4>
              <p className="text-sm text-slate-400">
                Scrapers navigate X/Twitter using Playwright, extracting structured JSON artifacts. 
                Ingest watcher handles file rotation and pushes to high-velocity Redis streams.
              </p>
            </div>
            <div className="p-5 bg-slate-900/50 rounded-xl border border-slate-800">
              <h4 className="text-white font-bold mb-2">Phase 2: Processing</h4>
              <p className="text-sm text-slate-400">
                Worker services sanitize text and generate 384-dim embeddings using 
                <code className="bg-slate-800 px-1 rounded text-cyan-400">all-MiniLM-L6-v2</code>.
              </p>
            </div>
          </div>
        </div>
        <div className="space-y-6">
          <div className="p-6 bg-slate-900 rounded-2xl border border-slate-800 font-mono text-xs overflow-hidden">
            <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="ml-2 text-slate-500">app/detection/bot_detector.py</span>
            </div>
            <pre className="text-cyan-400 space-y-1">
{`def calculate_bot_score(user_data):
    # Heuristic scoring engine
    score = 0.0
    
    # 1. Frequency Check
    if user_data.tweet_count / user_data.age_days > 72:
        score += 0.4
        
    # 2. Entropy Analysis
    if calculate_entropy(user_data.handle) > 4.5:
        score += 0.3
        
    # 3. Ratio Analysis
    ratio = user_data.following / max(1, user_data.followers)
    if ratio > 50:
        score += 0.3
        
    return min(1.0, score)`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};
