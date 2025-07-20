import json
import requests #(for test edgar api connection)
import os
from datetime import datetime

LOG_PATH = "data/outreach_log.json"

def load_outreach_log():
    if not os.path.exists(LOG_PATH):
        return {}
    with open(LOG_PATH, "r") as f:
        return json.load(f)

def update_outreach_log(company):
    log = load_outreach_log()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if company in log:
        log[company]["count"] += 1
        log[company]["last_contacted"] = now
    else:
        log[company] = {"count": 1, "last_contacted": now, "outcome": "-"}
    os.makedirs("data", exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

def update_outcome(company, outcome):
    log = load_outreach_log()
    if company not in log:
        log[company] = {"count": 0, "last_contacted": "Never", "outcome": outcome}
    else:
        log[company]["outcome"] = outcome
    os.makedirs("data", exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

def compute_signal_deltas(leads):
    # Dummy baseline for delta computation -- remove in demo/prod
    previous_scores = {
        "Fictional Tech Co.": 65,
        "Future AI Ltd.": 58
    }
    return {
        lead["company"]: lead["score"] - previous_scores.get(lead["company"], lead["score"])
        for lead in leads
    }

### function: asean_location -- for scraper.py #######
def is_asean_location(location):
    asean_keywords = [
        "Singapore", "Kuala Lumpur", "Jakarta", "Ho Chi Minh", "Hanoi", 
        "Bangkok", "Manila", "Phnom Penh", "Vientiane", "Naypyidaw", 
        "Bandar Seri Begawan", "Kwai Chung", "Wan Chai", "Hong Kong", "China"
    ]
    return any(keyword.lower() in location.lower() for keyword in asean_keywords)

#### function: test_edgar_api_connection ####
def test_edgar_api_connection():
    try:
        response = requests.get("https://data.sec.gov/submissions/CIK0000320193.json", headers={"User-Agent": "YourApp/0.1"})
        return response.status_code == 200
    except Exception as e:
        return False