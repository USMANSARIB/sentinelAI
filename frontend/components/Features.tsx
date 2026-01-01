
import React from 'react';
import { 
  ShieldCheck, 
  Network, 
  BarChart3, 
  Search, 
  MessageSquare, 
  Zap, 
  Globe, 
  Database 
} from 'lucide-react';

export const Features: React.FC = () => {
  const features = [
    {
      title: "CIB Detection",
      desc: "Real-time identification of Coordinated Inauthentic Behavior using sliding window text matching.",
      icon: <ShieldCheck className="text-cyan-500" />
    },
    {
      title: "Community Graphing",
      desc: "NetworkX-powered graph analysis classifying clusters as Organic, Bot, or Hybrid.",
      icon: <Network className="text-blue-500" />
    },
    {
      title: "Narrative Clustering",
      desc: "HDBSCAN groups semantically similar tweets to track the propagation of specific talking points.",
      icon: <Layers className="text-purple-500" />
    },
    {
      title: "Patient Zero Tracking",
      desc: "Trace narratives back to their precise origin to identify initial seeds and velocity spikes.",
      icon: <Fingerprint className="text-emerald-500" />
    },
    {
      title: "Bot Scoring",
      desc: "Heuristic and entropy-based scoring to flag suspicious handles with surgical precision.",
      icon: <BarChart3 className="text-orange-500" />
    },
    {
      title: "Threat Intel Integration",
      desc: "Automatic URL unshortening and verification against global threat intelligence feeds.",
      icon: <Globe className="text-indigo-500" />
    }
  ];

  return (
    <section className="py-24 bg-slate-950">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-4xl font-bold text-white">Full-Spectrum Intelligence</h2>
          <p className="text-slate-400 max-w-2xl mx-auto">
            SentinelGraph provides the most comprehensive suite of tools for tracking state-sponsored 
            influence operations and bot-driven narrative shifts.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((f, i) => (
            <div key={i} className="p-8 bg-slate-900/50 border border-slate-800 rounded-3xl hover:bg-slate-900 hover:border-slate-700 transition-all group">
              <div className="p-3 bg-slate-950 rounded-2xl w-fit mb-6 group-hover:scale-110 transition-transform">
                {f.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{f.title}</h3>
              <p className="text-slate-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

import { Layers, Fingerprint } from 'lucide-react';
