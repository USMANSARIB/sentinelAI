
import React from 'react';

interface CyberCardProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
  headerAction?: React.ReactNode;
}

export const CyberCard: React.FC<CyberCardProps> = ({ children, title, className = '', headerAction }) => {
  return (
    <div className={`cyber-card rounded-lg p-5 border border-cyan-500/20 bg-black/60 shadow-lg shadow-cyan-500/5 ${className}`}>
      {(title || headerAction) && (
        <div className="flex justify-between items-center mb-4 border-b border-cyan-500/10 pb-2">
          {title && (
            <h3 className="mono text-cyan-400 font-bold uppercase tracking-wider text-sm flex items-center">
              <span className="w-2 h-2 bg-cyan-500 mr-2 animate-pulse"></span>
              {title}
            </h3>
          )}
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
