# File: utils/helpers.py

import pandas as pd
import requests
from bs4 import BeautifulSoup

def extract_filing_details(filing_url: str) -> dict:
    """
    Given an EDGAR filing index URL, follow links to extract the actual
    filing text and parse out the reason for withdrawal and signer info.
    """
    details = {
        "Reason": "",
        "Undersigned": "",
        "Contact": ""
    }

    try:
        index_page = requests.get(filing_url, headers={"User-Agent": "Mozilla/5.0"})
        index_page.raise_for_status()
        soup = BeautifulSoup(index_page.text, "html.parser")

        # Step 1: Find the actual filing document link (.htm or .txt)
        doc_table = soup.find("table", class_="tableFile")
        filing_doc_url = None

        if doc_table:
            for row in doc_table.find_all("tr")[1:]:  # skip header
                cols = row.find_all("td")
                if len(cols) >= 3 and "complete submission text" in cols[2].text.lower():
                    filing_doc_url = "https://www.sec.gov" + cols[2].a['href']
                    break
                elif len(cols) >= 3 and (".htm" in cols[2].text or ".txt" in cols[2].text):
                    filing_doc_url = "https://www.sec.gov" + cols[2].a['href']
                    break

        # Step 2: If found, fetch the full filing document text
        if filing_doc_url:
            filing_resp = requests.get(filing_doc_url, headers={"User-Agent": "Mozilla/5.0"})
            filing_resp.raise_for_status()
            text = BeautifulSoup(filing_resp.text, "html.parser").get_text(separator="\n")

            # Step 3: Try to extract the reason
            reason_keywords = [
                "reason for withdrawal", 
                "has determined not to proceed", 
                "withdraw its registration", 
                "terminated the offering", 
                "request withdrawal", 
                "no longer intends"
            ]
            for line in text.splitlines():
                if any(kw in line.lower() for kw in reason_keywords):
                    details["Reason"] = line.strip()
                    break

            # Step 4: Extract signer info
            sig_block = []
            for line in reversed(text.splitlines()):
                if "By:" in line or "Name:" in line or "Title:" in line:
                    sig_block.insert(0, line.strip())
                if len(sig_block) > 3:
                    break
            if sig_block:
                details["Undersigned"] = " / ".join(sig_block)

            # Step 5: Try to find email or LinkedIn contact
            contact_lines = [line.strip() for line in text.splitlines() if "@" in line or "linkedin.com/in/" in line]
            if contact_lines:
                details["Contact"] = contact_lines[0]

        else:
            details["Reason"] = "[Filing document not found on index page]"

    except Exception as e:
        details["Reason"] = f"[Error extracting filing details: {e}]"

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

        if "Country" not in df.columns:
            df["Country"] = ""

        df.rename(columns={
            "Company": "Company Name",
            "Symbol": "Ticker",
            "Withdrawn": "Withdrawn Date",
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
