
import React, { useState, useEffect } from 'react';
import {
  Activity,
  Shield,
  Database,
  Terminal as TerminalIcon,
  AlertTriangle,
  BarChart3,
  Users,
  Share2,
  ChevronRight,
  RefreshCw,
  Search,
  Bell,
  Cpu,
  Globe,
  Lock,
  Zap,
  Download,
  Settings,
  ArrowRight,
  Monitor,
  Command,
  MessageSquare,
  Loader2
} from 'lucide-react';
import { fetchNarratives, fetchBots, fetchGraph, fetchStats } from './api';
import { Narrative, RiskLevel, BotAccount, GraphNode, GraphLink } from './types';
import { Narrative, RiskLevel } from './types';
import { CyberCard } from './components/CyberCard';
import { Terminal } from './components/Terminal';
import { NetworkGraph } from './components/NetworkGraph';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell, PieChart, Pie
} from 'recharts';

const TIMELINE_DATA = [
  { time: '14:00', volume: 120 },
  { time: '14:30', volume: 210 },
  { time: '15:00', volume: 450 },
  { time: '15:30', volume: 1800 },
  { time: '16:00', volume: 2400 },
  { time: '16:30', volume: 3200 },
  { time: '17:00', volume: 2900 },
];

const SidebarItem = ({ icon: Icon, label, active, onClick }: { icon: any, label: string, active?: boolean, onClick: () => void }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center px-4 py-3 mb-2 rounded-r-full transition-all duration-300 group ${active
        ? 'bg-cyan-500/10 border-l-4 border-cyan-500 text-cyan-400'
        : 'text-slate-500 hover:text-cyan-400 hover:bg-cyan-500/5 border-l-4 border-transparent'
      }`}
  >
    <Icon className={`w-5 h-5 mr-3 group-hover:scale-110 transition-transform`} />
    <span className="text-sm font-semibold tracking-wide uppercase">{label}</span>
  </button>
);

const LandingPage = ({ onEnter }: { onEnter: () => void }) => {
  return (
    <div className="min-h-screen bg-black relative overflow-hidden flex flex-col items-center justify-center p-6">
      {/* Background Decorative Elements */}
      <div className="absolute inset-0 z-0 opacity-20">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/30 blur-[150px] animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 blur-[150px]"></div>
      </div>

      <div className="z-10 text-center max-w-4xl space-y-8">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-cyan-500 rounded-2xl shadow-[0_0_50px_rgba(0,242,255,0.4)] animate-bounce">
            <Shield className="w-12 h-12 text-black" />
          </div>
        </div>

        <h1 className="text-6xl md:text-8xl font-black mono tracking-tighter text-white uppercase italic">
          Narrative<span className="text-cyan-400">Sentry</span>
        </h1>

        <p className="text-xl md:text-2xl text-slate-400 mono max-w-2xl mx-auto leading-relaxed">
          The industry's first <span className="text-cyan-400">coordinated inauthentic behavior</span> (CIB) detection platform.
          Powered by LLM-driven heuristics and community graph analysis.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12">
          {[
            { icon: Activity, title: 'Live Detection', desc: 'Identify disinformation spikes in real-time across X, Telegram & Discord.' },
            { icon: Users, title: 'Bot Clustering', desc: 'Auto-cluster bot accounts using Louvain modularity & behavioral fingerprinting.' },
            { icon: MessageSquare, title: 'AI Advisory', desc: 'Generate high-impact counter-narratives with local LLM integration.' }
          ].map((feature, i) => (
            <div key={i} className="p-6 rounded-xl border border-white/5 bg-white/5 backdrop-blur hover:border-cyan-500/30 transition-all text-left">
              <feature.icon className="w-8 h-8 text-cyan-500 mb-4" />
              <h3 className="text-lg font-bold text-white mb-2 uppercase mono">{feature.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>

        <div className="pt-12">
          <button
            onClick={onEnter}
            className="group relative inline-flex items-center justify-center px-10 py-4 font-bold text-white transition-all duration-200 bg-cyan-600 font-pj rounded-xl focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-600 hover:bg-cyan-500 shadow-[0_0_30px_rgba(0,242,255,0.4)]"
          >
            <span className="mono mr-2">INITIALIZE TERMINAL</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>

      <div className="absolute bottom-8 left-0 w-full flex justify-center space-x-8 text-[10px] mono text-slate-600 uppercase tracking-widest">
        <span>v2.4.0-Stable</span>
        <span>Secure Ingest: Active</span>
        <span>Encryption: 4096-bit AES</span>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  const [view, setView] = useState<'landing' | 'app'>('landing');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedNarrative, setSelectedNarrative] = useState<Narrative | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [narratives, setNarratives] = useState<Narrative[]>([]);
  const [bots, setBots] = useState<BotAccount[]>([]);
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[], links: GraphLink[] }>({ nodes: [], links: [] });
  const [stats, setStats] = useState<any>(null);

  const loadData = async () => {
    try {
      const [n, b, g, s] = await Promise.all([
        fetchNarratives(),
        fetchBots(),
        fetchGraph(),
        fetchStats()
      ]);
      setNarratives(n);
      setBots(b);
      setGraphData(g);
      setStats(s);
      if (n.length > 0 && !selectedNarrative) setSelectedNarrative(n[0]);
    } catch (e) {
      console.error("Failed to load data", e);
    }
  };

  useEffect(() => {
    if (view === 'app') {
      loadData();
    }
  }, [view]);

  const refreshData = () => {
    setIsRefreshing(true);
    loadData().finally(() => setTimeout(() => setIsRefreshing(false), 500));
  };

  const renderDashboard = () => (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <CyberCard className="!p-4 border-l-4 border-l-cyan-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-500 text-xs mono uppercase">Active Narratives</p>
              <h4 className="text-2xl font-bold mono mt-1">{narratives.length}</h4>
            </div>
            <div className="p-2 bg-cyan-500/10 rounded">
              <Activity className="text-cyan-500 w-5 h-5" />
            </div>
          </div>
          <p className="text-[10px] text-green-500 mt-2 flex items-center">
            <ChevronRight className="w-3 h-3 rotate-[-90deg]" /> +{narratives.filter(n => new Date(n.first_seen).getTime() > Date.now() - 3600000).length} in last hour
          </p>
        </CyberCard>

        <CyberCard className="!p-4 border-l-4 border-l-red-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-500 text-xs mono uppercase">High Risk Alerts</p>
              <h4 className="text-2xl font-bold mono mt-1">{narratives.filter(n => n.risk_level === 'HIGH' || n.risk_level === 'CRITICAL').length}</h4>
            </div>
            <div className="p-2 bg-red-500/10 rounded">
              <AlertTriangle className="text-red-500 w-5 h-5" />
            </div>
          </div>
          <p className="text-[10px] text-red-400 mt-2">Requires immediate response</p>
        </CyberCard>

        <CyberCard className="!p-4 border-l-4 border-l-purple-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-500 text-xs mono uppercase">Bots Detected</p>
              <h4 className="text-2xl font-bold mono mt-1">{stats?.kpi?.bots || 0}</h4>
            </div>
            <div className="p-2 bg-purple-500/10 rounded">
              <Users className="text-purple-500 w-5 h-5" />
            </div>
          </div>
          <p className="text-[10px] text-purple-400 mt-2">Avg bot ratio: 24.5%</p>
        </CyberCard>

        <CyberCard className="!p-4 border-l-4 border-l-green-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-500 text-xs mono uppercase">Tweets Ingested</p>
              <h4 className="text-2xl font-bold mono mt-1">{stats?.kpi?.tweets || 0}</h4>
            </div>
            <div className="p-2 bg-green-500/10 rounded">
              <RefreshCw className="text-green-500 w-5 h-5" />
            </div>
          </div>
          <p className="text-[10px] text-green-400 mt-2">Health: Nominal (99.8%)</p>
        </CyberCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <CyberCard title="Active Narrative Monitor">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm border-collapse">
                <thead className="text-slate-500 border-b border-cyan-500/10">
                  <tr>
                    <th className="py-3 px-2">Narrative</th>
                    <th className="py-3 px-2">Volume</th>
                    <th className="py-3 px-2">Risk</th>
                    <th className="py-3 px-2">Urgency</th>
                    <th className="py-3 px-2">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-cyan-500/5">
                  {narratives.map((n) => (
                    <tr
                      key={n.id}
                      className={`hover:bg-cyan-500/5 transition-colors cursor-pointer ${selectedNarrative?.id === n.id ? 'bg-cyan-500/10' : ''}`}
                      onClick={() => setSelectedNarrative(n)}
                    >
                      <td className="py-3 px-2">
                        <div className="font-semibold text-cyan-100">{n.title}</div>
                        <div className="text-[10px] text-slate-500 uppercase">{n.type}</div>
                      </td>
                      <td className="py-3 px-2 mono text-slate-400">{n.tweet_count}</td>
                      <td className="py-3 px-2">
                        <div className="w-24 h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${n.risk_score > 0.7 ? 'bg-red-500' : 'bg-cyan-500'}`}
                            style={{ width: `${n.risk_score * 100}%` }}
                          ></div>
                        </div>
                      </td>
                      <td className="py-3 px-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${n.urgency === 'IMMEDIATE' ? 'bg-red-500/20 text-red-500' : 'bg-slate-500/20 text-slate-400'
                          }`}>
                          {n.urgency}
                        </span>
                      </td>
                      <td className="py-3 px-2">
                        <ChevronRight className="w-4 h-4 text-slate-500" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CyberCard>

          <CyberCard title="Spike Detection & Timeline">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stats?.timeline_data || []}>
                  <defs>
                    <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00f2ff" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#00f2ff" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#00f2ff', color: '#fff' }}
                    itemStyle={{ color: '#00f2ff' }}
                  />
                  <Area type="monotone" dataKey="volume" stroke="#00f2ff" fillOpacity={1} fill="url(#colorVolume)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CyberCard>
        </div>

        <div className="space-y-6">
          <CyberCard title="Risk Advisory Engine" className="border-t-2 border-t-cyan-500">
            {selectedNarrative ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500 uppercase mono">Assessment for:</span>
                  <span className="text-xs font-bold text-cyan-400 uppercase mono truncate max-w-[150px]">{selectedNarrative.title}</span>
                </div>

                <Terminal text={selectedNarrative.suggested_reply || "No reply suggestion available."} />

                <div className="space-y-2 mt-4">
                  <h5 className="text-[10px] font-bold uppercase text-slate-400 mono">Risk Breakdown</h5>
                  {Object.entries(selectedNarrative.metrics).map(([key, m]: [string, any]) => (
                    <div key={key} className="flex flex-col gap-1">
                      <div className="flex justify-between items-center text-[10px] mono">
                        <span className="text-slate-500">{key.replace('_', ' ')}</span>
                        <span className="text-cyan-400">{(m.contribution * 100).toFixed(0)}% weight</span>
                      </div>
                      <div className="h-1 bg-slate-800 rounded-full">
                        <div
                          className="h-full bg-cyan-500 shadow-[0_0_8px_rgba(0,242,255,0.4)]"
                          style={{ width: `${(m.value || m.normalized || 0) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>

                <button className="w-full mt-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold uppercase text-xs mono rounded transition-all shadow-[0_0_15px_rgba(0,242,255,0.3)]">
                  Approve Countermeasure
                </button>
              </div>
            ) : (
              <div className="text-center py-10 text-slate-500 mono text-xs">
                Select a narrative to see AI analysis.
              </div>
            )}
          </CyberCard>

          <CyberCard title="Infrastructure Health">
            <div className="space-y-3">
              {[
                { name: 'PostgreSQL + pgvector', status: 'Healthy', latency: '4ms' },
                { name: 'Redis Streams', status: 'Healthy', latency: '2ms' },
                { name: 'Ollama-Llama3:3b', status: 'Idle', latency: 'N/A' },
                { name: 'HDBSCAN Worker', status: 'Processing', latency: '12ms' },
              ].map((service, idx) => (
                <div key={idx} className="flex justify-between items-center border-b border-cyan-500/5 pb-2 last:border-0">
                  <div>
                    <div className="text-xs font-semibold">{service.name}</div>
                    <div className="text-[10px] text-green-500">{service.status}</div>
                  </div>
                  <div className="text-[10px] mono text-slate-500">{service.latency}</div>
                </div>
              ))}
            </div>
          </CyberCard>
        </div>
      </div>
    </div>
  );

  const renderBots = () => (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
      <CyberCard title="Identified Bot Network Assets">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Real-time heuristic analysis identifies automated behavior based on posting frequency, follower ratio, account age, and textual repetition.
            </p>
            <div className="max-h-[600px] overflow-y-auto space-y-3 pr-2 custom-scrollbar">
              {bots.map((bot) => (
                <div key={bot.user_id} className="p-3 bg-slate-900/50 rounded border border-cyan-500/10 hover:border-cyan-500/40 transition-all">
                  <div className="flex justify-between items-center mb-2">
                    <span className="mono text-cyan-400 text-sm font-bold">{bot.handle}</span>
                    <span className={`px-2 py-0.5 rounded text-[8px] font-bold ${bot.label === 'BOT' ? 'bg-red-500/20 text-red-500' : 'bg-yellow-500/20 text-yellow-500'
                      }`}>
                      {bot.label}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[9px] uppercase text-slate-500 mono">
                    <div>Posts/Day: <span className="text-slate-300">{bot.posting_frequency.toFixed(0)}</span></div>
                    <div>Account Age: <span className="text-slate-300">{bot.account_age_days}d</span></div>
                    <div>Follow Ratio: <span className="text-slate-300">{bot.follower_ratio.toFixed(2)}</span></div>
                    <div>Bot Score: <span className="text-red-400 font-bold">{(bot.bot_score * 100).toFixed(0)}%</span></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div className="mb-4">
              <h4 className="text-xs font-bold uppercase text-slate-400 mono flex items-center">
                <Share2 className="w-3 h-3 mr-1" /> Community Graph Visualization
              </h4>
            </div>
            <NetworkGraph data={graphData} />
            <div className="mt-4 p-4 bg-black/40 rounded border border-cyan-500/10">
              <h5 className="text-[10px] font-bold uppercase text-cyan-400 mb-2 mono">Louvain Algorithm Analysis</h5>
              <p className="text-[10px] text-slate-400 leading-relaxed">
                Detected 3 distinct clusters. Cluster 0 (Bot Cluster) exhibits high modularity (0.42) and extreme internal interconnectivity.
                Common nodes are linked via identical text hashes and shared suspicious domains.
              </p>
            </div>
          </div>
        </div>
      </CyberCard>
    </div>
  );

  const renderIngest = () => (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <CyberCard title="Data Sources" className="md:col-span-2">
          <div className="space-y-4">
            {[
              { name: 'X (Twitter)', icon: Globe, status: 'Active', load: '640 req/min', iconColor: 'text-blue-400' },
              { name: 'Telegram Monitoring', icon: MessageSquare, status: 'Active', load: '120 req/min', iconColor: 'text-sky-400' },
              { name: 'Discord Scrapers', icon: MessageSquare, status: 'Warning', load: '12 req/min', iconColor: 'text-indigo-400' },
              { name: 'Dark Web Feeds', icon: Lock, status: 'Disabled', load: '0 req/min', iconColor: 'text-slate-500' },
            ].map((source, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/5">
                <div className="flex items-center">
                  <source.icon className={`w-6 h-6 mr-4 ${source.iconColor}`} />
                  <div>
                    <h4 className="font-bold text-sm uppercase mono">{source.name}</h4>
                    <p className="text-[10px] text-slate-500 mono">{source.load}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${source.status === 'Active' ? 'bg-green-500/20 text-green-500' : source.status === 'Warning' ? 'bg-yellow-500/20 text-yellow-500' : 'bg-slate-500/20 text-slate-500'}`}>
                    {source.status}
                  </span>
                  <Settings className="w-4 h-4 text-slate-500 cursor-pointer hover:text-white" />
                </div>
              </div>
            ))}
          </div>
        </CyberCard>

        <CyberCard title="Queue Health">
          <div className="space-y-6">
            <div>
              <div className="flex justify-between text-[10px] mono text-slate-400 mb-1">
                <span>BUFFER CAPACITY</span>
                <span>82%</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full">
                <div className="h-full bg-yellow-500 w-[82%]"></div>
              </div>
            </div>
            <div className="p-4 bg-black/40 rounded border border-cyan-500/5 mono text-[10px] leading-relaxed">
              <p className="text-cyan-500"># tail -f /var/log/ingest.log</p>
              <p className="text-slate-500">[14:32:01] Ingested 42 tweets from @amplifier_1</p>
              <p className="text-slate-500">[14:32:05] New cluster detected (ID: cl-92)</p>
              <p className="text-red-400">[14:32:08] Rate limit hit for Discord API</p>
              <p className="text-slate-500">[14:32:12] Heartbeat nominal</p>
            </div>
          </div>
        </CyberCard>
      </div>
    </div>
  );

  const renderLLM = () => (
    <div className="space-y-6 animate-in zoom-in-95 duration-500">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <CyberCard title="Advisory Engine Configuration">
          <div className="space-y-4">
            <div>
              <label className="text-xs mono text-slate-500 uppercase block mb-2">Base Model</label>
              <select className="w-full bg-slate-900 border border-cyan-500/20 rounded px-3 py-2 text-sm mono focus:outline-none">
                <option>Llama-3-8B-Instruct (GGUF)</option>
                <option>Mistral-7B-v0.2</option>
                <option>Gemma-7B-IT</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs mono text-slate-500 uppercase block mb-2">Temperature</label>
                <input type="range" className="w-full accent-cyan-500" min="0" max="1" step="0.1" />
              </div>
              <div>
                <label className="text-xs mono text-slate-500 uppercase block mb-2">Max Tokens</label>
                <input type="number" className="w-full bg-slate-900 border border-cyan-500/20 rounded px-2 py-1 text-sm mono" defaultValue={512} />
              </div>
            </div>
            <div>
              <label className="text-xs mono text-slate-500 uppercase block mb-2">System Instruction Prompt</label>
              <textarea
                className="w-full h-32 bg-slate-900 border border-cyan-500/20 rounded p-3 text-xs mono focus:outline-none focus:border-cyan-500"
                defaultValue="You are a cyber-threat intelligence specialist. Generate counter-narratives that are professional, factual, and de-escalating. Focus on identifying and neutralizing logical fallacies..."
              />
            </div>
            <button className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold uppercase text-xs mono rounded">
              Update Weights & Prompts
            </button>
          </div>
        </CyberCard>

        <CyberCard title="Performance Benchmarks">
          <div className="space-y-6">
            <div className="flex items-center justify-center h-48">
              <div className="relative">
                <div className="w-32 h-32 rounded-full border-4 border-cyan-500/20 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-3xl font-bold mono">42</div>
                    <div className="text-[8px] text-slate-500 uppercase">Tokens/sec</div>
                  </div>
                </div>
                <div className="absolute inset-0 border-t-4 border-cyan-500 rounded-full animate-spin"></div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-center mono uppercase text-[10px]">
              <div className="p-3 bg-white/5 rounded">
                <div className="text-slate-500 mb-1">Inference Latency</div>
                <div className="text-cyan-400 font-bold">120ms</div>
              </div>
              <div className="p-3 bg-white/5 rounded">
                <div className="text-slate-500 mb-1">GPU VRAM Usage</div>
                <div className="text-purple-400 font-bold">6.2GB / 8GB</div>
              </div>
            </div>
          </div>
        </CyberCard>
      </div>
    </div>
  );

  const renderReports = () => (
    <div className="space-y-6 animate-in fade-in duration-500">
      <CyberCard title="Intelligence Reports">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Weekly Summary', type: 'PDF', date: 'Oct 24, 2023', size: '2.4MB' },
            { label: 'Bot Network Audit', type: 'JSON', date: 'Oct 23, 2023', size: '1.8MB' },
            { label: 'Threat Landscape', type: 'CSV', date: 'Oct 22, 2023', size: '4.2MB' },
            { label: 'Incident Timeline', type: 'PDF', date: 'Oct 21, 2023', size: '1.2MB' },
          ].map((report, i) => (
            <div key={i} className="p-4 bg-white/5 rounded border border-white/5 hover:border-cyan-500/30 transition-all group cursor-pointer">
              <Download className="w-6 h-6 text-cyan-500 mb-3 group-hover:animate-bounce" />
              <div className="text-xs font-bold uppercase mono mb-1">{report.label}</div>
              <div className="flex justify-between text-[10px] text-slate-500 mono">
                <span>{report.date}</span>
                <span>{report.type}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats?.timeline_data || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#00f2ff', color: '#fff' }}
                cursor={{ fill: 'rgba(0, 242, 255, 0.05)' }}
              />
              <Bar dataKey="volume" fill="#00f2ff">
                {TIMELINE_DATA.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index === 5 ? '#ff0055' : '#00f2ff'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <p className="text-center text-[10px] mono text-slate-500 mt-4 uppercase">Figure 1.1: Historical Hourly Ingest Volume (Red indicates spike detection)</p>
        </div>
      </CyberCard>
    </div>
  );

  if (view === 'landing') {
    return <LandingPage onEnter={() => setView('app')} />;
  }

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-[#050505] text-slate-200">
      {/* Sidebar Navigation */}
      <aside className="w-full lg:w-64 bg-black/40 border-r border-cyan-500/10 z-50">
        <div className="p-6">
          <div className="flex items-center mb-8 cursor-pointer" onClick={() => setView('landing')}>
            <div className="p-2 bg-cyan-500 rounded mr-3 shadow-[0_0_15px_rgba(0,242,255,0.6)]">
              <Shield className="w-6 h-6 text-black" />
            </div>
            <h1 className="text-xl font-bold mono tracking-tighter text-cyan-400">
              NARRATIVE<span className="text-white">SENTRY</span>
            </h1>
          </div>

          <nav className="space-y-1">
            <SidebarItem icon={Activity} label="Dashboard" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
            <SidebarItem icon={Users} label="Bot Clusters" active={activeTab === 'bots'} onClick={() => setActiveTab('bots')} />
            <SidebarItem icon={Database} label="Data Ingest" active={activeTab === 'ingest'} onClick={() => setActiveTab('ingest')} />
            <SidebarItem icon={TerminalIcon} label="Advisory LLM" active={activeTab === 'llm'} onClick={() => setActiveTab('llm')} />
            <SidebarItem icon={BarChart3} label="Intelligence" active={activeTab === 'reports'} onClick={() => setActiveTab('reports')} />
          </nav>
        </div>

        <div className="absolute bottom-0 left-0 w-full p-4 hidden lg:block">
          <div className="p-3 rounded bg-cyan-500/5 border border-cyan-500/10">
            <div className="text-[10px] text-slate-500 uppercase mono mb-1">System Load</div>
            <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-cyan-500 w-[12%] animate-pulse"></div>
            </div>
            <div className="text-[10px] text-cyan-500 mt-2 mono">CPU: 12% | RAM: 4.2GB</div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-4 lg:p-8 overflow-y-auto max-h-screen relative z-10">
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] mono text-cyan-500 bg-cyan-500/10 px-1 rounded uppercase tracking-widest">Live Surveillance</span>
              <span className="flex h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white uppercase mono">
              {activeTab.replace('_', ' ')} <span className="text-cyan-400">Environment</span>
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="SEARCH THREATS..."
                className="bg-slate-900 border border-cyan-500/20 rounded pl-10 pr-4 py-2 text-xs mono focus:outline-none focus:border-cyan-500 transition-all w-64"
              />
            </div>
            <button className="p-2 bg-slate-900 border border-cyan-500/20 rounded hover:border-cyan-500 transition-colors relative">
              <Bell className="w-5 h-5 text-slate-400" />
              <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full animate-ping"></span>
            </button>
            <button
              onClick={refreshData}
              className={`p-2 bg-slate-900 border border-cyan-500/20 rounded hover:border-cyan-500 transition-colors ${isRefreshing ? 'animate-spin' : ''}`}
            >
              <RefreshCw className="w-5 h-5 text-slate-400" />
            </button>
          </div>
        </header>

        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'bots' && renderBots()}
        {activeTab === 'ingest' && renderIngest()}
        {activeTab === 'llm' && renderLLM()}
        {activeTab === 'reports' && renderReports()}
      </main>

      {/* Visual background elements */}
      <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-cyan-500/5 blur-[120px] pointer-events-none"></div>
      <div className="fixed bottom-0 left-0 w-[400px] h-[400px] bg-purple-500/5 blur-[100px] pointer-events-none"></div>
    </div>
  );
};

export default App;
