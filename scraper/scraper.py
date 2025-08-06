# File: scraper/scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

from utils.helpers import extract_filing_details

# Location codes used by EDGAR for targeted geographic searches
location_codes = {
    "Singapore": "U0",
    "Hong Kong": "K3",
    "China": "F4"
}

# Required user-agent format for SEC.gov per their fair access policy
headers = {
    'User-Agent': 'AtasSuccess-XaaS-MVP/1.0 (wkdliew@gmail.com)'
}

def get_withdrawn_ipos(start_date, end_date):
    """
    Search for withdrawn IPO filings (Form RW, RW WD) on EDGAR using EFTS search.
    Filters by country using SEC location codes and date range.
    Extracts additional detail text for each filing.
    """
    search_url = "https://efts.sec.gov/LATEST/search-index"
    results = []

    for country, location_code in location_codes.items():
        payload = {
            "keys": ["RW"],  # Withdrawn forms
            "category": "custom",
            "forms": ["RW", "RW WD"],
            "startdt": str(start_date),
            "enddt": str(end_date),
            "location": location_code
        }

        try:
            response = requests.post(search_url, headers=headers, json=payload)
            response.raise_for_status()
            filings = response.json().get("hits", [])

            print(f"[✓] {len(filings)} filings found for {country}")

            for filing in filings:
                cik = filing.get("cik", "")
                name = filing.get("name", "")
                filed = filing.get("filed", "")
                accession = filing.get("adsh", "")

                if not (cik and accession):
                    continue  # Skip incomplete records

                accession_nodash = accession.replace("-", "")
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodash}/{accession}-index.htm"

                print(f"CIK: {cik}, Accession: {accession}, Filing URL: {filing_url}")

                filing_details = extract_filing_details(filing_url)

                filing_details.update({
                    "Company Name": name,
                    "CIK": cik,
                    "Filing Date": filed,
                    "Country": country,
                    "URL": filing_url
                })

                results.append(filing_details)
                time.sleep(0.5)  # Be respectful to SEC servers

        except Exception as e:
            print(f"[!] Error fetching for {country}: {e}")
            continue

    print(f"[✓] Total EDGAR filings fetched: {len(results)}")
    return results
