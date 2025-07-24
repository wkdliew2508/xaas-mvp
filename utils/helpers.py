# File: utils/helpers.py

import pandas as pd

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
