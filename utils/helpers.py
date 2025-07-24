# File: utils/helpers.py

import pandas as pd
import requests
from bs4 import BeautifulSoup

def extract_filing_details(filing_url: str) -> dict:
    """
    Given a filing URL from EDGAR, extract relevant details such as
    reason for withdrawal, undersigned name/title, and possible contact info.
    """
    details = {
        "Reason": "",
        "Undersigned": "",
        "Contact": ""
    }

    try:
        response = requests.get(filing_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n")

        # Extract Reason for Withdrawal
        reason_keywords = ["reason for withdrawal", "withdraw its registration", "has determined not to proceed"]
        for line in text.splitlines():
            if any(kw.lower() in line.lower() for kw in reason_keywords):
                details["Reason"] = line.strip()
                break

        # Extract Undersigned name and title
        sig_block = []
        for line in reversed(text.splitlines()):
            if "By:" in line or "Name:" in line or "Title:" in line:
                sig_block.insert(0, line.strip())
            if len(sig_block) > 3:
                break
        details["Undersigned"] = " / ".join(sig_block)

        # Attempt to find email or LinkedIn (less common)
        if "@" in text:
            contact_lines = [line.strip() for line in text.splitlines() if "@" in line]
            details["Contact"] = contact_lines[0] if contact_lines else ""
        elif "linkedin.com/in/" in text:
            contact_lines = [line.strip() for line in text.splitlines() if "linkedin.com/in/" in line]
            details["Contact"] = contact_lines[0] if contact_lines else ""

    except Exception as e:
        details["Reason"] = f"[Error parsing filing: {e}]"

    return details

def fetch_stockanalysis_data():
    """
    Scrapes withdrawn IPOs from stockanalysis.com using requests + BeautifulSoup
    and returns a cleaned pandas DataFrame.
    """
    url = "https://stockanalysis.com/ipos/withdrawn/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table")
        if not table:
            raise ValueError("No table found on the page")

        rows = table.find_all("tr")
        data = []
        headers = [th.text.strip() for th in rows[0].find_all("th")]

        for row in rows[1:]:
            cols = [td.text.strip() for td in row.find_all("td")]
            if len(cols) == len(headers):
                data.append(dict(zip(headers, cols)))

        df = pd.DataFrame(data)
        df.rename(columns={
            "Company": "Company Name",
            "Symbol": "Ticker",
            "Country": "Country",
            "Withdrawn": "Withdrawn Date"
        }, inplace=True)

        df["Status"] = "Withdrawn"
        return df

    except Exception as e:
        print(f"Error scraping StockAnalysis: {e}")
        return pd.DataFrame(columns=["Company Name", "Country", "Status"])

def get_stockanalysis_df():
    return fetch_stockanalysis_data()


def combine_sources(edgar_df, stock_df):
    """
    Merge or concatenate EDGAR and StockAnalysis datasets.
    Assumes both are already formatted DataFrames.
    """
    edgar_df["Source"] = "EDGAR"
    stock_df["Source"] = "StockAnalysis"

    combined = pd.concat([edgar_df, stock_df], ignore_index=True)
    
    # Sort by filing or expected date if available
    date_col = "Filing Date" if "Filing Date" in combined.columns else "Expected Date"
    if date_col in combined.columns:
        combined[date_col] = pd.to_datetime(combined[date_col], errors='coerce')
        combined.sort_values(date_col, ascending=False, inplace=True)

    # Standardize column order
    columns = [col for col in ["Company Name", "CIK", "Filing Date", "Expected Date",
                               "Country", "Details", "URL", "Source"]
               if col in combined.columns]
    
    combined = combined[columns]
    combined.reset_index(drop=True, inplace=True)
    return combined
