
import React, { useState, useEffect } from 'react';

interface TerminalProps {
  text: string;
  speed?: number;
}

export const Terminal: React.FC<TerminalProps> = ({ text, speed = 20 }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text, speed]);

  return (
    <div className="mono bg-black text-green-500 p-4 rounded border border-green-500/30 text-xs h-32 overflow-y-auto leading-relaxed">
      <div className="flex items-center mb-2">
        <span className="w-3 h-3 rounded-full bg-red-500 mr-1"></span>
        <span className="w-3 h-3 rounded-full bg-yellow-500 mr-1"></span>
        <span className="w-3 h-3 rounded-full bg-green-500"></span>
        <span className="ml-2 text-green-800">Ollama-Llama3-Core.session</span>
      </div>
      <p>
        <span className="text-cyan-500">$ advisory_engine --generate-reply</span>
        <br />
        {displayedText}
        <span className="inline-block w-2 h-4 bg-green-500 ml-1 animate-pulse align-middle"></span>
      </p>
    </div>
  );
};
