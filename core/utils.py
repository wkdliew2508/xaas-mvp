import json
import requests
import os
from datetime import datetime

LOG_PATH = "data/outreach_log.json"

def load_outreach_log():
    if not os.path.exists(LOG_PATH):
        return {}
    try:
        with open(LOG_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

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
    # Dummy baseline for delta computation -- replace or remove in production
    previous_scores = {
        "Fictional Tech Co.": 65,
        "Future AI Ltd.": 58
    }
    deltas = {}
    for lead in leads:
        previous = previous_scores.get(lead["company"], lead["score"])
        deltas[lead["company"]] = lead["score"] - previous
    return deltas

def is_asean_location(location_string, selected_locations=None):
    asean_keywords = [
        "Singapore", "Kuala Lumpur", "Jakarta", "Ho Chi Minh", "Hanoi",
        "Bangkok", "Manila", "Phnom Penh", "Vientiane", "Naypyidaw",
        "Bandar Seri Begawan", "Kwai Chung", "Wan Chai", "Hong Kong", "China"
    ]
    keywords = selected_locations if selected_locations else asean_keywords
    return any(keyword.lower() in location_string.lower() for keyword in keywords)

def test_edgar_api_connection(user_agent="YourApp/0.1 Contact@yourdomain.com"):
    try:
        headers = {"User-Agent": user_agent}
        response = requests.get("https://data.sec.gov/submissions/CIK0000320193.json", headers=headers)
        if response.status_code == 200:
            return True, "Connected successfully to EDGAR API"
        else:
            return False, f"Connection failed with status code {response.status_code}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"