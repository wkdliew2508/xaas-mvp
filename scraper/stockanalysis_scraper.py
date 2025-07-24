# stockanalysis_scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd

TARGET_COUNTRIES = ["Singapore", "China", "Hong Kong"]

def fetch_stockanalysis_withdrawn():
    url = "https://stockanalysis.com/ipos/withdrawn/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table")
    rows = table.find("tbody").find_all("tr")

    data = []
    for tr in rows:
        cols = tr.find_all("td")
        if len(cols) < 6:
            continue
        symbol = cols[0].text.strip()
        company = cols[1].text.strip()
        price_range = cols[2].text.strip()
        shares = cols[3].text.strip()
        country = cols[4].text.strip()
        exchange = cols[5].text.strip()
        if country in TARGET_COUNTRIES and exchange.upper() == "NASDAQ":
            data.append({
                "Source": "StockAnalysis",
                "Company": company,
                "Symbol": symbol,
                "Country": country,
                "Price Range": price_range,
                "Shares": shares,
                "Exchange": exchange
            })

    return pd.DataFrame(data)
