# File: utils/formatter.py

import pandas as pd

def format_filing_data(filings):
    """
    Convert list of dicts (filings) into a clean DataFrame.
    Standardizes column names and formatting.
    """
    if not filings:
        return pd.DataFrame(columns=["Company Name", "CIK", "Filing Date", "Country", "Details", "URL"])

    df = pd.DataFrame(filings)
    
    # Ensure all expected columns are present
    for col in ["Company Name", "CIK", "Filing Date", "Country", "Details", "URL"]:
        if col not in df.columns:
            df[col] = ""

    df["Filing Date"] = pd.to_datetime(df["Filing Date"], errors='coerce')
    df.sort_values("Filing Date", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
