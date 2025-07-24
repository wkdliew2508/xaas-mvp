# File: app.py

import os
import sys
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import pandas as pd

from scraper.scraper import get_withdrawn_ipos
from utils.formatter import format_filing_data
from utils.helpers import get_stockanalysis_df, combine_sources

st.set_page_config(page_title="Withdrawn IPO Intelligence", layout="wide")

st.title("📉 Withdrawn IPO Intelligence Dashboard")

st.markdown("""
This dashboard aggregates and analyzes withdrawn IPO filings from SEC's EDGAR system and StockAnalysis,
focusing on Singapore, Hong Kong, and China.
""")

with st.sidebar:
    st.header("🔍 Search Parameters")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    run_search = st.button("Run Search")

if run_search:
    with st.status("Fetching withdrawn IPOs from EDGAR and StockAnalysis...", expanded=True):
        edgar_list = get_withdrawn_ipos(start_date, end_date)
        formatted_edgar = format_filing_data(edgar_list)

        stockanalysis_df = get_stockanalysis_df()

        combined_df = combine_sources(formatted_edgar, stockanalysis_df)

        st.success("Data fetched and processed successfully!")

    if 'Country' in combined_df.columns and not combined_df.empty:
        st.markdown("## Combined Withdrawn IPOs")
        for country in combined_df['Country'].unique():
            df_country = combined_df[combined_df['Country'] == country].reset_index(drop=True)
            st.markdown(f"### {country}")
            st.dataframe(df_country, use_container_width=True)
    else:
        st.warning("No country data found to display IPOs by country.")
