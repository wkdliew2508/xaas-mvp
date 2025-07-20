class IPORevivalScorer:
    def score(self, lead):
        signals = {
            "base": 50,
            "country_bonus": 10 if lead['country'] in ["Singapore", "India"] else 5,
            "linkedin_activity": 5 if "hiring" in lead.get("news", "").lower() else 0,
            "peer_ipo": 4 if lead.get("peer_ipo", False) else 0,
            "funding_news": 7 if lead.get("funding", False) else 0,
            "exec_change": 8 if lead.get("ceo_change", False) else 0,
        }
        total = sum(signals.values())
        return total, signals

# core/scorer.py

def score_filing(filing):
    # TODO: implement actual scoring logic
    return {
        "score": 75,
        "notes": "Scored based on placeholder logic. Final logic pending."
    }