# File: utils.py

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date
from stockanalysis_scraper import fetch_stockanalysis_withdrawn


def extract_filing_details(filing_url):
    res = requests.get(filing_url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(res.text, "html.parser")

    doc_link = None
    for a in soup.find_all('a'):
        if a.text.strip() == "Complete submission text file":
            doc_link = a['href']
            break

    if not doc_link:
        return {"Reason": "", "Undersigned": "", "Title": "", "Contact": ""}

    doc_res = requests.get(f"https://www.sec.gov{doc_link}", headers={'User-Agent': 'Mozilla/5.0'})
    text = doc_res.text

    reason = extract_reason(text)
    signer, title = extract_signer_and_title(text)
    contact = extract_contact(text)

    return {
        "Reason": reason,
        "Undersigned": signer,
        "Title": title,
        "Contact": contact
    }

def extract_reason(text):
    lower = text.lower()
    for line in lower.splitlines():
        if "withdraw" in line and "because" in line:
            return line.strip()
    return ""

def extract_signer_and_title(text):
    lines = text.strip().splitlines()
    signer, title = "", ""
    for i in range(len(lines)-1):
        if lines[i].strip().lower().startswith("by:"):
            signer = lines[i].replace("By:", "").strip()
            title = lines[i+1].strip()
            break
    return signer, title

def extract_contact(text):
    for line in text.splitlines():
        if "@" in line:
            return line.strip()
    return ""

def format_filing_data(data):
    return pd.DataFrame(data)

def fetch_stockanalysis_data():
    # Dummy structure, assumes export from scraped table or internal cache
    data = [
        {"Company Name": "Test Holdings Ltd", "Country": "Singapore", "Status": "Withdrawn"},
        {"Company Name": "Alpha Asia Corp", "Country": "China", "Status": "Withdrawn"}
    ]
    return pd.DataFrame(data)

def get_stockanalysis_df():
    return fetch_stockanalysis_withdrawn()

def combine_sources(edgar_df, stock_df):
    edgar_df['Source'] = 'EDGAR'
    stock_df['Filing Date'] = pd.NaT
    stock_df['Reason'] = ''
    stock_df['Undersigned'] = ''
    stock_df['Title'] = ''
    return pd.concat([edgar_df, stock_df], ignore_index=True)

#def combine_sources(edgar_df, sa_df):
#    return pd.concat([edgar_df, sa_df], ignore_index=True).drop_duplicates()
