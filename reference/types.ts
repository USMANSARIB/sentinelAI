
export interface SystemMetric {
  label: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export interface Narrative {
  id: string;
  title: string;
  velocity: number;
  riskScore: number;
  type: 'Organic' | 'Bot Cluster' | 'Hybrid';
  firstSeen: string;
}

export interface AnalysisResponse {
  riskScore: number;
  assessment: string;
  strategy: string;
  entities: string[];
}
