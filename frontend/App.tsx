
import React, { useState, useEffect } from 'react';
import {
  Shield,
  Activity,
  Network,
  Cpu,
  Database,
  Lock,
  Terminal,
  ChevronRight,
  BarChart3,
  Search,
  AlertTriangle,
  Zap,
  Github,
  Menu,
  X,
  Layers,
  Fingerprint
} from 'lucide-react';
import { Hero } from './components/Hero';
import { Architecture } from './components/Architecture';
import { Features } from './components/Features';
import { IntelligenceSandbox } from './components/IntelligenceSandbox';
import { DashboardConnected } from './components/DashboardConnected';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'home' | 'docs' | 'sandbox'>('home');
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled ? 'bg-slate-900/80 backdrop-blur-md border-b border-slate-800 py-3' : 'bg-transparent py-6'
        }`}>
        <div className="container mx-auto px-6 flex justify-between items-center">
          <div className="flex items-center gap-2 group cursor-pointer" onClick={() => setActiveTab('home')}>
            <div className="p-2 bg-cyan-500 rounded-lg text-slate-950 group-hover:scale-110 transition-transform">
              <Shield size={24} />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">SentinelGraph</span>
          </div>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            <button
              onClick={() => setActiveTab('home')}
              className={`text-sm font-medium transition-colors ${activeTab === 'home' ? 'text-cyan-400' : 'text-slate-400 hover:text-white'}`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('docs')}
              className={`text-sm font-medium transition-colors ${activeTab === 'docs' ? 'text-cyan-400' : 'text-slate-400 hover:text-white'}`}
            >
              Architecture
            </button>
            <button
              onClick={() => setActiveTab('sandbox')}
              className={`text-sm font-medium transition-colors ${activeTab === 'sandbox' ? 'text-cyan-400' : 'text-slate-400 hover:text-white'}`}
            >
              Intelligence Sandbox
            </button>
            <div className="h-6 w-px bg-slate-800"></div>
            <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-medium transition-all">
              Login
            </button>
            <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 rounded-lg text-sm font-bold shadow-lg shadow-cyan-900/20 transition-all">
              Request Demo
            </button>
          </div>

          {/* Mobile Toggle */}
          <button className="md:hidden text-slate-400" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 right-0 bg-slate-900 border-b border-slate-800 p-6 flex flex-col gap-4 animate-in fade-in slide-in-from-top-4 duration-300">
            <button onClick={() => { setActiveTab('home'); setMobileMenuOpen(false); }} className="text-left py-2 text-slate-300">Overview</button>
            <button onClick={() => { setActiveTab('docs'); setMobileMenuOpen(false); }} className="text-left py-2 text-slate-300">Architecture</button>
            <button onClick={() => { setActiveTab('sandbox'); setMobileMenuOpen(false); }} className="text-left py-2 text-slate-300">Intelligence Sandbox</button>
            <div className="grid grid-cols-2 gap-4 mt-4">
              <button className="px-4 py-3 bg-slate-800 rounded-xl font-medium">Login</button>
              <button className="px-4 py-3 bg-cyan-600 text-slate-950 rounded-xl font-bold">Request Demo</button>
            </div>
          </div>
        )}
      </nav>

      {/* Content */}
      <main className="pt-20">
        {activeTab === 'home' && (
          <>
            <Hero />
            <DashboardConnected />
            <Features />
          </>
        )}

        {activeTab === 'docs' && (
          <div className="container mx-auto px-6 py-12">
            <Architecture />
          </div>
        )}

        {activeTab === 'sandbox' && (
          <div className="container mx-auto px-6 py-12">
            <IntelligenceSandbox />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-12">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-8">
            <div className="flex items-center gap-2">
              <Shield className="text-cyan-500" size={24} />
              <span className="text-xl font-bold text-white">SentinelGraph</span>
            </div>
            <div className="flex gap-8 text-slate-500 text-sm">
              <a href="#" className="hover:text-cyan-400 transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-cyan-400 transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-cyan-400 transition-colors">Documentation</a>
              <a href="#" className="hover:text-cyan-400 transition-colors">API Reference</a>
            </div>
            <div className="flex gap-4">
              <button className="p-2 bg-slate-900 rounded-full hover:bg-slate-800 transition-colors">
                <Github size={20} />
              </button>
            </div>
          </div>
          <div className="mt-8 text-center text-slate-600 text-xs">
            © {new Date().getFullYear()} SentinelGraph System Architecture. All Rights Reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
