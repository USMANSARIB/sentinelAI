
import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertTriangle, TrendingUp, Users, Activity } from 'lucide-react';

interface VolumeData {
    time: string;
    volume: number;
}

interface Narrative {
    risk_level: string;
    is_spike: boolean;
}

export const DashboardConnected: React.FC = () => {
    const [chartData, setChartData] = useState<VolumeData[]>([]);
    const [narrativeCount, setNarrativeCount] = useState(0);
    const [highRiskCount, setHighRiskCount] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch Stats for Volume Chart
                const statsRes = await fetch('/api/stats');
                const statsJson = await statsRes.json();

                if (statsJson.timeline_data) {
                    setChartData(statsJson.timeline_data);
                } else if (statsJson.volume_chart) {
                    const labels = statsJson.volume_chart.labels;
                    const values = statsJson.volume_chart.data;
                    const formatted = labels.map((l: string, i: number) => ({
                        time: l,
                        volume: values[i]
                    }));
                    setChartData(formatted);
                }

                // Fetch Narratives for Counts
                const narrRes = await fetch('/api/narratives');
                const narrJson = await narrRes.json();
                if (Array.isArray(narrJson)) {
                    setNarrativeCount(narrJson.length);
                    const highRisk = narrJson.filter((n: Narrative) => n.risk_level === 'HIGH' || n.risk_level === 'CRITICAL').length;
                    setHighRiskCount(highRisk);
                }

            } catch (e) {
                console.error("Failed to fetch dashboard data", e);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="container mx-auto px-6 py-12">
            <div className="relative p-1 bg-gradient-to-br from-slate-800 via-cyan-500/20 to-slate-800 rounded-3xl overflow-hidden shadow-2xl">
                <div className="bg-slate-950 rounded-[22px] overflow-hidden flex flex-col md:flex-row h-[600px]">
                    {/* Sidebar */}
                    <div className="w-full md:w-64 bg-slate-900 border-r border-slate-800 p-6 flex flex-col gap-6">
                        <div className="flex items-center gap-3 text-cyan-400 font-bold mb-4">
                            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                                <Activity size={18} />
                            </div>
                            LIVE MONITOR
                        </div>
                        <div className="space-y-4">
                            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Analysis Pipelines</div>
                            <div className="space-y-2">
                                <div className="p-2 bg-slate-800 rounded-lg text-sm flex justify-between items-center text-white">
                                    <span>Narrative Cluster</span>
                                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                </div>
                                <div className="p-2 bg-slate-900 text-slate-400 rounded-lg text-sm flex justify-between items-center">
                                    <span>Bot Scoring</span>
                                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                </div>
                                <div className="p-2 bg-slate-900 text-slate-400 rounded-lg text-sm flex justify-between items-center">
                                    <span>Network Graph</span>
                                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                </div>
                            </div>
                        </div>
                        <div className="mt-auto p-4 bg-cyan-500/10 border border-cyan-500/20 rounded-xl">
                            <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold mb-1">
                                <AlertTriangle size={14} /> HIGH ANOMALY
                            </div>
                            <div className="text-white text-sm font-medium">Cluster #824 exhibiting 120% velocity spike.</div>
                        </div>
                    </div>

                    {/* Main Console */}
                    <div className="flex-1 p-8 overflow-y-auto custom-scrollbar">
                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                            <div>
                                <h2 className="text-2xl font-bold text-white">Threat Landscape</h2>
                                <p className="text-slate-500 text-sm">Real-time aggregate data from global scrapers.</p>
                            </div>
                            <div className="flex gap-2">
                                <div className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs font-medium text-slate-400">Past 24 Hours</div>
                                <button className="px-4 py-2 bg-cyan-500 rounded-xl text-xs font-bold text-slate-950 hover:bg-cyan-400 transition">Export Report</button>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                            <div className="p-6 bg-slate-900 rounded-2xl border border-slate-800">
                                <div className="flex justify-between items-center mb-4">
                                    <TrendingUp className="text-cyan-400" size={20} />
                                    <span className="text-[10px] font-bold text-green-400 bg-green-400/10 px-2 py-0.5 rounded-full">+12%</span>
                                </div>
                                <div className="text-3xl font-bold text-white">{loading ? '...' : narrativeCount}</div>
                                <div className="text-slate-500 text-xs mt-1">Total Narratives Detected</div>
                            </div>
                            <div className="p-6 bg-slate-900 rounded-2xl border border-slate-800">
                                <div className="flex justify-between items-center mb-4">
                                    <Users className="text-blue-400" size={20} />
                                    <span className="text-[10px] font-bold text-red-400 bg-red-400/10 px-2 py-0.5 rounded-full">Alert</span>
                                </div>
                                <div className="text-3xl font-bold text-white">{loading ? '...' : highRiskCount}</div>
                                <div className="text-slate-500 text-xs mt-1">High-Risk Clusters</div>
                            </div>
                            <div className="p-6 bg-slate-900 rounded-2xl border border-slate-800">
                                <div className="flex justify-between items-center mb-4">
                                    <Activity className="text-purple-400" size={20} />
                                    <span className="text-[10px] font-bold text-slate-400 bg-slate-400/10 px-2 py-0.5 rounded-full">Stable</span>
                                </div>
                                <div className="text-3xl font-bold text-white">92ms</div>
                                <div className="text-slate-500 text-xs mt-1">Mean Processing Latency</div>
                            </div>
                        </div>

                        <div className="h-64 w-full bg-slate-900/50 rounded-2xl border border-slate-800 p-4">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData.length > 0 ? chartData : [{ time: '00:00', volume: 0 }]}>
                                    <defs>
                                        <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                    <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                                    <YAxis hide />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', fontSize: '12px' }}
                                        itemStyle={{ color: '#06b6d4' }}
                                    />
                                    <Area type="monotone" dataKey="volume" stroke="#06b6d4" fillOpacity={1} fill="url(#colorVolume)" strokeWidth={3} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
