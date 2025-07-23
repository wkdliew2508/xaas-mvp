# File: app.py

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
    edgar_list = get_withdrawn_ipos(start_date, end_date)
    edgar_df = pd.DataFrame(edgar_list)
    stock_df = get_stockanalysis_df()
    combined = combine_sources(edgar_df, stock_df)
    
    st.markdown("## Combined Withdrawn IPOs")
    for country in combined['Country'].unique():
        df_country = combined[combined['Country'] == country].reset_index(drop=True)
        st.markdown(f"### {country}")
        st.dataframe(df_country)
        
    with st.status("Fetching withdrawn IPOs from EDGAR and StockAnalysis...", expanded=True):
        edgar_results = get_withdrawn_ipos(start_date, end_date)
        formatted_edgar = format_filing_data(edgar_results)

        stockanalysis_df = fetch_stockanalysis_data()
        combined_df = combine_sources(formatted_edgar, stockanalysis_df)

        st.success("Data fetched and processed successfully!")

    st.markdown("## 📊 Withdrawn IPOs by Country")
    countries = combined_df['Country'].unique()

    for country in countries:
        st.markdown(f"### {country}")
        st.dataframe(combined_df[combined_df['Country'] == country].reset_index(drop=True), use_container_width=True)
