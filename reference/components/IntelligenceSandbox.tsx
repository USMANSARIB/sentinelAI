
import React, { useState } from 'react';
import { GoogleGenAI, Type } from "@google/genai";
import { Zap, Send, Brain, ShieldAlert, Loader2, Sparkles } from 'lucide-react';

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export const IntelligenceSandbox: React.FC = () => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const analyzeThreat = async () => {
    if (!input) return;
    setLoading(true);
    try {
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: `Analyze this potential influence operation scenario and provide strategic advice based on SentinelGraph principles: ${input}`,
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              riskLevel: { type: Type.NUMBER, description: "Risk score from 0-100" },
              assessment: { type: Type.STRING, description: "Detailed summary of the threat" },
              classification: { type: Type.STRING, description: "Type of threat (e.g., Scam, State-sponsored, Organic)" },
              recommendedAction: { type: Type.STRING, description: "Tactical response strategy" },
              tacticalNotes: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Specific insights" }
            }
          }
        }
      });
      
      const data = JSON.parse(response.text);
      setResult(data);
    } catch (error) {
      console.error("Analysis failed", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center space-y-4">
        <h2 className="text-3xl font-bold text-white flex items-center justify-center gap-2">
          <Brain className="text-cyan-400" /> Intelligence Sandbox
        </h2>
        <p className="text-slate-400 max-w-2xl mx-auto">
          Test the SentinelGraph Strategic Advisory engine. Describe a narrative anomaly or observed social 
          media behavior to receive a risk assessment and mitigation strategy.
        </p>
      </div>

      <div className="space-y-6">
        <div className="relative group">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe a scenario (e.g., 'Sudden surge of 200 accounts with zero followers posting identical text about the new policy change...')"
            className="w-full h-40 bg-slate-900/50 border border-slate-800 focus:border-cyan-500/50 rounded-2xl p-6 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-4 focus:ring-cyan-500/10 transition-all resize-none"
          />
          <button
            onClick={analyzeThreat}
            disabled={loading || !input}
            className="absolute bottom-4 right-4 px-6 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-bold rounded-xl transition-all flex items-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" size={20} /> : <Sparkles size={20} />}
            Generate Intelligence
          </button>
        </div>

        {result && (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 animate-in zoom-in-95 duration-500">
            {/* Main Assessment */}
            <div className="md:col-span-8 p-8 bg-slate-900 border border-slate-800 rounded-3xl space-y-6">
              <div className="flex items-center justify-between">
                <span className="px-3 py-1 bg-cyan-500/10 text-cyan-400 text-xs font-bold rounded-full uppercase tracking-widest border border-cyan-500/20">
                  {result.classification}
                </span>
                <div className="flex items-center gap-2 text-slate-500 text-xs">
                  <ShieldAlert size={14} /> ADVISORY ENGINE v4.2
                </div>
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold text-white">Scenario Assessment</h3>
                <p className="text-slate-400 leading-relaxed">{result.assessment}</p>
              </div>
              <div className="pt-6 border-t border-slate-800 space-y-4">
                <h4 className="text-sm font-bold text-white uppercase tracking-wider">Tactical Recommendations</h4>
                <div className="grid grid-cols-1 gap-3">
                  {result.tacticalNotes.map((note: string, i: number) => (
                    <div key={i} className="flex gap-3 text-sm text-slate-400">
                      <Zap size={16} className="text-cyan-500 shrink-0" />
                      <span>{note}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Sidebar Metrics */}
            <div className="md:col-span-4 space-y-6">
              <div className="p-8 bg-slate-900 border border-slate-800 rounded-3xl flex flex-col items-center justify-center text-center space-y-2">
                <div className="text-sm text-slate-500 font-bold uppercase tracking-wider">Risk Score</div>
                <div className={`text-6xl font-black ${result.riskLevel > 70 ? 'text-red-500' : 'text-cyan-400'}`}>
                  {result.riskLevel}
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-1000 ${result.riskLevel > 70 ? 'bg-red-500' : 'bg-cyan-500'}`}
                    style={{ width: `${result.riskLevel}%` }}
                  ></div>
                </div>
              </div>

              <div className="p-6 bg-cyan-600 text-slate-950 rounded-3xl space-y-2">
                <h4 className="font-bold">Recommended Response</h4>
                <p className="text-sm font-medium leading-tight">
                  {result.recommendedAction}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
