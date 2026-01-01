
import React from 'react';
import { Terminal, Shield, ArrowRight, Activity, Cpu } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <div className="relative overflow-hidden pt-20 pb-16 md:pt-32 md:pb-32">
      {/* Background Decor */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-cyan-900/10 blur-[120px] rounded-full -z-10"></div>
      <div className="absolute top-40 right-0 w-[400px] h-[400px] bg-blue-900/10 blur-[100px] rounded-full -z-10"></div>
      
      <div className="container mx-auto px-6">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-slate-900/50 border border-slate-800 rounded-full text-cyan-400 text-sm font-mono mb-4">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
            </span>
            SYSTEM STATUS: OPERATIONAL
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white leading-tight">
            Neutralize Coordinated <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Inauthentic Behavior</span>
          </h1>
          
          <p className="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            SentinelGraph is a hybrid event-driven pipeline combining real-time stream processing with 
            advanced heuristic engines to detect, track, and expose digital influence operations.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button className="w-full sm:w-auto px-8 py-4 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold rounded-xl transition-all flex items-center justify-center gap-2 shadow-xl shadow-cyan-900/30">
              Launch Intelligence Console <ArrowRight size={20} />
            </button>
            <button className="w-full sm:w-auto px-8 py-4 bg-slate-900 border border-slate-800 hover:bg-slate-800 font-medium rounded-xl transition-all flex items-center justify-center gap-2">
              <Terminal size={20} /> View Technical Specs
            </button>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-8 pt-16">
            <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col items-center">
              <Activity className="text-cyan-500 mb-2" size={24} />
              <div className="text-2xl font-bold text-white">4.2M</div>
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Events/Day</div>
            </div>
            <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col items-center">
              <Cpu className="text-cyan-500 mb-2" size={24} />
              <div className="text-2xl font-bold text-white">120ms</div>
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Latent Risk Scoring</div>
            </div>
            <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col items-center">
              <Shield className="text-cyan-500 mb-2" size={24} />
              <div className="text-2xl font-bold text-white">99.8%</div>
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Detection Accuracy</div>
            </div>
            <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col items-center">
              <div className="flex -space-x-2 mb-2">
                {[1,2,3].map(i => (
                  <img key={i} src={`https://picsum.photos/seed/${i*10}/32/32`} className="w-6 h-6 rounded-full border-2 border-slate-950" alt="avatar" />
                ))}
              </div>
              <div className="text-2xl font-bold text-white">12k+</div>
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Bot Accounts Identified</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
