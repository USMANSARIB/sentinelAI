import config
from datetime import datetime

class RiskScorer:
    def __init__(self):
        self.weights = {
            'bot_ratio': 0.30,
            'spike_velocity': 0.25,
            'coordination': 0.25,
            'suspicious_urls': 0.20
        }

    def calculate_risk(self, narrative_data):
        score = 0.0
        details = {}
        
        # 1. Bot Ratio (0-1)
        bot_ratio = narrative_data.get('bot_ratio', 0.0)
        bot_contribution = bot_ratio * self.weights['bot_ratio']
        score += bot_contribution
        
        details['bot_ratio'] = {
            'value': bot_ratio,
            'contribution': round(bot_contribution, 3),
            'interpretation': self.interpret_bot_ratio(bot_ratio)
        }
        
        # 2. Spike Velocity (Normalized)
        velocity = narrative_data.get('velocity', 1.0)
        # Normalize: 1x=0.0, 5x=1.0
        vel_norm = min(max((velocity - 1) / 4.0, 0), 1.0)
        velocity_contribution = vel_norm * self.weights['spike_velocity']
        score += velocity_contribution
        
        details['spike_velocity'] = {
            'value': velocity,
            'normalized': round(vel_norm, 2),
            'contribution': round(velocity_contribution, 3)
        }
        
        # 3. Coordination (0-1)
        coord_score = narrative_data.get('coordination_score', 0.0)
        coord_contribution = coord_score * self.weights['coordination']
        score += coord_contribution
        
        details['coordination'] = {
            'value': coord_score,
            'contribution': round(coord_contribution, 3)
        }
        
        # 4. URLs
        url_count = narrative_data.get('suspicious_url_count', 0)
        url_norm = min(url_count / 5.0, 1.0)
        url_contribution = url_norm * self.weights['suspicious_urls']
        score += url_contribution
        
        details['suspicious_urls'] = {
            'count': url_count,
            'normalized': round(url_norm, 2),
            'contribution': round(url_contribution, 3)
        }
        
        # Classify
        level = 'LOW'
        urgency = 'ROUTINE'
        if score >= 0.7:
            level = 'HIGH'
            urgency = 'CRITICAL'
        elif score >= 0.4:
            level = 'MEDIUM'
            urgency = 'MODERATE'
            
        return {
            'risk_score': round(score, 3),
            'risk_level': level,
            'urgency': urgency,
            'breakdown': details
        }
        
    def interpret_bot_ratio(self, ratio):
        if ratio >= 0.7:
            return "SEVERE: Highly automated campaign"
        elif ratio >= 0.4:
            return "MODERATE: Significant bot activity"
        else:
            return "LOW: Mostly organic accounts"

class ResponseAdvisor:
    def recommend_timing(self, risk_report, narrative_data):
        risk_level = risk_report['risk_level']
        velocity = narrative_data.get('velocity', 0)
        
        if risk_level == 'HIGH':
            if velocity >= 3.0:
                return {
                    'timing': 'IMMEDIATE',
                    'timeframe': '< 30 minutes',
                    'rationale': 'High-risk fast-spreading narrative requires immediate containment',
                    'priority': 'P0'
                }
            else:
                 return {
                    'timing': 'URGENT',
                    'timeframe': '< 2 hours',
                    'rationale': 'High-risk but slower spread allows brief preparation',
                    'priority': 'P1'
                }
        elif risk_level == 'MEDIUM':
            if velocity >= 2.0:
                return {
                    'timing': 'DELAY',
                    'timeframe': '2-4 hours',
                    'rationale': 'Moderate risk, gather more data before responding',
                    'priority': 'P2'
                }
            else:
                 return {
                    'timing': 'MONITOR',
                    'timeframe': '6-12 hours',
                    'rationale': 'Watch for escalation before committing response',
                    'priority': 'P3'
                }
        else:
             return {
                'timing': 'MONITOR',
                'timeframe': '24 hours',
                'rationale': 'Low risk, continue monitoring without response',
                'priority': 'P4'
            }

class ReplyStrategySelector:
    def select_strategy(self, narrative_data, risk_report):
        narrative_type = self.classify_type(narrative_data)
        bot_ratio = narrative_data.get('bot_ratio', 0.0)
        risk_level = risk_report['risk_level']
        
        # Default Strategy
        strategy = {
            'type': narrative_type,
            'tone': 'POLITE',
            'approach': 'Acknowledge concern and provide context',
            'template': "[TEMPLATE] We hear you. Here's what we're doing: [Action]..."
        }
        
        if narrative_type == 'SCAM':
            strategy = {
                'type': 'SCAM',
                'tone': 'FIRM',
                'approach': 'Call out fraud directly with evidence',
                'template': "[TEMPLATE] WARNING: This is a known scam. Do not engage. Verified Evidence: {evidence_link}"
            }
        elif narrative_type == 'PANIC':
             strategy = {
                'type': 'PANIC',
                'tone': 'CALM',
                'approach': 'Reassure with facts and authoritative sources',
                'template': "[TEMPLATE] We understand concerns. Official Data: {fact_link}"
            }
        elif narrative_type == 'DEFAMATION':
            strategy = {
                'type': 'DEFAMATION',
                'tone': 'EVIDENCE_BASED',
                'approach': 'Correct with verifiable data and sources',
                'template': "[TEMPLATE] The facts: [Data]. Sources: {fact_link}"
            }
        elif narrative_type == 'COORDINATED_BOT' or bot_ratio > 0.6:
            strategy = {
                'type': 'COORDINATED_BOT',
                'tone': 'TRANSPARENT',
                'approach': 'Expose coordination evidence',
                'template': "[TEMPLATE] Detection Alert: We've detected inauthentic activity driving this trend. Analysis: {dashboard_link}"
            }
            
        return strategy

    def classify_type(self, narrative_data):
        keywords = narrative_data.get('keywords', [])
        summary = narrative_data.get('summary', '')
        text_source = (" ".join(keywords) + " " + summary).lower()
        
        scam_ind = ['invest', 'guarantee', 'double your', 'limited time', 'crypto', 'free']
        panic_ind = ['collapse', 'crisis', 'shutdown', 'failing', 'danger', 'hack']
        defam_ind = ['fraud', 'illegal', 'scandal', 'corrupt', 'criminal']
        
        if any(w in text_source for w in scam_ind): return 'SCAM'
        if any(w in text_source for w in panic_ind): return 'PANIC'
        if any(w in text_source for w in defam_ind): return 'DEFAMATION'
        
        if narrative_data.get('bot_ratio', 0) > 0.6: return 'COORDINATED_BOT'
        
        return 'CRITICISM'

class EvidenceGenerator:
    def prepare_evidence_package(self, narrative_data, risk_report, strategy, timing):
        """
        Prepares a structured dictionary that can be rendered into an HTML report.
        """
        return {
            'report_id': f"RPT-{datetime.now().strftime('%Y%m%d%H%M')}",
            'generated_at': datetime.now().isoformat(),
            'narrative': {
                'title': narrative_data.get('title'),
                'summary': narrative_data.get('summary'),
                'metrics': {
                    'bot_ratio': narrative_data.get('bot_ratio'),
                    'velocity': narrative_data.get('velocity'),
                    'volume': narrative_data.get('tweet_count')
                }
            },
            'risk_assessment': risk_report,
            'response_plan': {
                'strategy': strategy,
                'timing': timing
            }
        }

class Advisor:
    def __init__(self):
        self.scorer = RiskScorer()
        self.response_advisor = ResponseAdvisor()
        self.selector = ReplyStrategySelector()
        self.evidence_gen = EvidenceGenerator()
        
    def generate_advice(self, narrative_data):
        # 1. Risk Calculation
        risk = self.scorer.calculate_risk(narrative_data)
        
        # 2. Timing Recommendation
        timing = self.response_advisor.recommend_timing(risk, narrative_data)
        
        # 3. Strategy Selection
        strategy = self.selector.select_strategy(narrative_data, risk)
        
        # 4. Draft Reply (Mockup for MVP)
        topic = narrative_data.get('title', 'this topic')
        draft = strategy['template'].format(
            evidence_link="sentinel.io/report",
            fact_link="official.com/facts",
            dashboard_link="sentinel.io/dash",
            topic=topic
        )
        
        # 5. Evidence Package
        evidence = self.evidence_gen.prepare_evidence_package(narrative_data, risk, strategy, timing)

        return {
            'risk_report': risk,
            'timing_recommendation': timing,
            'recommended_strategy': strategy,
            'draft_reply': draft,
            'evidence_package': evidence
        }
