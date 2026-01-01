
import { Narrative, RiskLevel, NarrativeType, BotAccount, GraphNode, GraphLink } from './types';

export const MOCK_NARRATIVES: Narrative[] = [
  {
    id: 'nar-001',
    title: 'Bank XYZ Liquidity Rumors',
    summary: 'Viral misinformation suggesting immediate collapse of Bank XYZ, leading to panic withdrawals.',
    tweet_count: 5420,
    time_range: 'Last 6 hours',
    risk_score: 0.892,
    risk_level: RiskLevel.CRITICAL,
    urgency: 'IMMEDIATE',
    type: NarrativeType.PANIC,
    bot_ratio: 0.42,
    first_seen: '2023-10-24T14:30:00Z',
    metrics: {
      bot_ratio: { value: 0.42, contribution: 0.25, interpretation: 'MODERATE: Significant bot activity' },
      spike_velocity: { value: 8.5, normalized: 1.0, contribution: 0.25 },
      coordination: { value: 0.78, contribution: 0.20 },
      suspicious_urls: { count: 12, normalized: 1.0, contribution: 0.20 }
    },
    suggested_reply: 'We understand concerns. Here are the facts regarding Bank XYZ stability: [Liquidity Report Link]. Assets are 110% collateralized.'
  },
  {
    id: 'nar-002',
    title: 'Token-X Investment Scam',
    summary: 'Coordinated bot network promoting a "guaranteed double" crypto scheme.',
    tweet_count: 12400,
    time_range: 'Last 12 hours',
    risk_score: 0.950,
    risk_level: RiskLevel.HIGH,
    urgency: 'URGENT',
    type: NarrativeType.SCAM,
    bot_ratio: 0.88,
    first_seen: '2023-10-24T08:15:00Z',
    metrics: {
      bot_ratio: { value: 0.88, contribution: 0.30, interpretation: 'SEVERE: Highly automated campaign' },
      spike_velocity: { value: 4.2, normalized: 0.8, contribution: 0.20 },
      coordination: { value: 0.95, contribution: 0.25 },
      suspicious_urls: { count: 45, normalized: 1.0, contribution: 0.20 }
    },
    suggested_reply: 'WARNING: This is a known scam. High bot coordination detected. Do not click links.'
  },
  {
    id: 'nar-003',
    title: 'Supply Chain Criticisms',
    summary: 'Legitimate user complaints regarding shipping delays for TechCorp Alpha release.',
    tweet_count: 850,
    time_range: 'Last 24 hours',
    risk_score: 0.210,
    risk_level: RiskLevel.LOW,
    urgency: 'ROUTINE',
    type: NarrativeType.CRITICISM,
    bot_ratio: 0.05,
    first_seen: '2023-10-23T19:00:00Z',
    metrics: {
      bot_ratio: { value: 0.05, contribution: 0.02, interpretation: 'LOW: Mostly organic accounts' },
      spike_velocity: { value: 1.2, normalized: 0.1, contribution: 0.05 },
      coordination: { value: 0.05, contribution: 0.01 },
      suspicious_urls: { count: 0, normalized: 0.0, contribution: 0.0 }
    },
    suggested_reply: 'We hear you. We are working hard to resolve Alpha shipping delays. Thanks for your patience.'
  }
];

export const MOCK_BOTS: BotAccount[] = Array.from({ length: 15 }).map((_, i) => ({
  user_id: `user-${i}`,
  handle: `@bot_detector_${i}`,
  bot_score: 0.4 + Math.random() * 0.6,
  label: i % 3 === 0 ? 'BOT' : 'SUSPICIOUS',
  posting_frequency: 10 + Math.random() * 150,
  account_age_days: Math.floor(Math.random() * 30),
  follower_ratio: Math.random() * 0.2,
  repeat_text_ratio: 0.3 + Math.random() * 0.5
}));

export const GRAPH_DATA = {
  nodes: [
    { id: '1', handle: '@origin_seed', group: 'origin', bot_score: 0.1 },
    { id: '2', handle: '@amplifier_1', group: 'bot', bot_score: 0.9 },
    { id: '3', handle: '@amplifier_2', group: 'bot', bot_score: 0.85 },
    { id: '4', handle: '@legit_user_1', group: 'organic', bot_score: 0.05 },
    { id: '5', handle: '@amplifier_3', group: 'bot', bot_score: 0.92 },
    { id: '6', handle: '@legit_user_2', group: 'organic', bot_score: 0.12 },
    { id: '7', handle: '@suspicious_link', group: 'bot', bot_score: 0.75 },
  ],
  links: [
    { source: '1', target: '2', type: 'RETWEET', weight: 1.0 },
    { source: '1', target: '3', type: 'RETWEET', weight: 1.0 },
    { source: '2', target: '5', type: 'SIMILAR', weight: 0.9 },
    { source: '3', target: '5', type: 'MENTION', weight: 0.5 },
    { source: '4', target: '1', type: 'REPLY', weight: 0.8 },
    { source: '2', target: '7', type: 'SIMILAR', weight: 0.85 },
    { source: '5', target: '7', type: 'SIMILAR', weight: 0.95 },
    { source: '6', target: '1', type: 'REPLY', weight: 0.8 },
  ]
};
