### Updated README.md (20072025)
# 🏛️ IPO Revival Watchlist – SEC RW Filings App

This Streamlit app helps uncover strategic outreach opportunities by identifying companies that **withdrew IPO filings (Form RW)** from the SEC and are **based in ASEAN cities or financial hubs like Hong Kong and China**.

It scrapes the [SEC EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), filters based on location, date, and scoring logic, and provides **outreach message suggestions** to revive discussions.

---

## 🚀 Features

✅ Scrapes live **Form RW (Registration Withdrawal)** filings from the SEC  
✅ Filters by **location**, **score threshold**, and **date range**  
✅ Scores filings based on **industry keywords**  
✅ Generates ready-to-send **outreach messages**  
✅ Tracks outreach history (coming soon)  
✅ Runs as a **Streamlit web app** (zero install needed)

---

## 📦 Project Structure
├── app.py                      # Streamlit app UI
├── requirements.txt
├── README.md
└── core/
├── scraper.py              # SEC EDGAR data logic
├── scorer.py               # Simple keyword-based scoring
├── outreach.py             # Outreach message generator
└── utils.py                # API connection + location filter

---

## 🧪 Try It Locally

### 1. Clone the Repo

```bash
git clone https://github.com/wkdliew2508/ipo-revival-app.git
cd ipo-revival-app

### 2. Create and Activate a Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run Streamlit App
streamlit run app.py


### Configuration
#	•	Default date range: last 1 year
#	•	Editable filters in sidebar:
#	•	Date Range
#	•	ASEAN & Asian Cities
#	•	Industry Keywords (for scoring)
#	•	Minimum Score Threshold


# Outreach Logic

#You can customize the scoring (core/scorer.py) and message style (core/#outreach.py) to suit your industry or sales tone.


Contact

Built by David Liew.
Open to collaborators and feedback!


Disclaimer

This tool uses publicly available data from the SEC. It is intended for informational and exploratory purposes only and does not constitute investment advice.



#### ORIG README ####
## 💹 IPO Revival Radar

#A modular outreach engine that identifies and tracks companies that withdrew #IPO plans in APAC, scores revival likelihood, finds executive contacts, and #automates intelligent email campaigns.

## 📦 Features

#- Scrapes and scores withdrawn IPO candidates
#- Tracks daily score changes and activity
#- Outreach history with outcomes
#- Editable messaging UI
#- Modular and reusable for other campaigns

## 🧪 Run Locally

#```bash
#pip install -r requirements.txt
#streamlit run app.py