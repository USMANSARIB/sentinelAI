
export enum RiskLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export enum NarrativeType {
  SCAM = 'SCAM',
  PANIC = 'PANIC',
  DEFAMATION = 'DEFAMATION',
  CRITICISM = 'CRITICISM',
  COORDINATED_BOT = 'COORDINATED_BOT'
}

export interface MetricBreakdown {
  bot_ratio: { value: number; contribution: number; interpretation: string };
  spike_velocity: { value: number; normalized: number; contribution: number };
  coordination: { value: number; contribution: number };
  suspicious_urls: { count: number; normalized: number; contribution: number };
}

export interface Narrative {
  id: string;
  title: string;
  summary: string;
  tweet_count: number;
  time_range: string;
  risk_score: number;
  risk_level: RiskLevel;
  urgency: string;
  type: NarrativeType;
  metrics: MetricBreakdown;
  origin_tweet_id?: string;
  first_seen: string;
  suggested_reply?: string;
  bot_ratio: number;
}

export interface BotAccount {
  user_id: string;
  handle: string;
  bot_score: number;
  label: 'BOT' | 'SUSPICIOUS' | 'ORGANIC';
  posting_frequency: number;
  account_age_days: number;
  follower_ratio: number;
  repeat_text_ratio: number;
}

export interface GraphNode {
  id: string;
  handle: string;
  group: string;
  bot_score: number;
}

export interface GraphLink {
  source: string;
  target: string;
  type: 'RETWEET' | 'REPLY' | 'MENTION' | 'SIMILAR';
  weight: number;
}
