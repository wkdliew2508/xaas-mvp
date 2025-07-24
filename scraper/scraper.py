# File: scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from utils.helpers import extract_filing_details

location_codes = {
    "Singapore": "U0",
    "Hong Kong": "K3",
    "China": "F4"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; MyAppName/1.0; +https://example.com/info)'
}

def get_withdrawn_ipos(start_date, end_date):
    base_url = "https://data.sec.gov/submissions/CIK{}.json"
    results = []

    for country, code in location_codes.items():
        search_url = f"https://efts.sec.gov/LATEST/search-index"
        payload = {
            "keys": ["RW"],
            "category": "custom",
            "forms": ["RW", "RW WD"],
            "startdt": str(start_date),
            "enddt": str(end_date),
            "location": code
        }

        res = requests.post(search_url, headers=headers, json=payload)
        if res.status_code != 200:
            print(f"Failed search for {country}")
            continue

        filings = res.json().get("hits", [])

        for filing in filings:
            accession = filing['adsh']
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{filing['cik']}/{accession.replace('-', '')}/{accession}-index.htm"
            details = extract_filing_details(filing_url)
            details.update({
                "Country": country,
                "Company Name": filing['name'],
                "CIK": filing['cik'],
                "Filing Date": filing['filed']
            })
            results.append(details)
            time.sleep(0.5)

    return results
