
import { Narrative, BotAccount, GraphNode, GraphLink } from './types';

const API_BASE = '/api';

export const fetchNarratives = async (): Promise<Narrative[]> => {
    const response = await fetch(`${API_BASE}/narratives`);
    if (!response.ok) throw new Error('Failed to fetch narratives');
    return response.json();
};

export const fetchBots = async (): Promise<BotAccount[]> => {
    const response = await fetch(`${API_BASE}/bots`);
    if (!response.ok) throw new Error('Failed to fetch bots');
    return response.json();
};

export const fetchGraph = async (): Promise<{ nodes: GraphNode[], links: GraphLink[] }> => {
    const response = await fetch(`${API_BASE}/communities`);
    if (!response.ok) throw new Error('Failed to fetch graph');
    return response.json();
};

export const fetchStats = async () => {
    const response = await fetch(`${API_BASE}/stats`);
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
}
