# /mnt/c/xaas-mvp/app.py

import streamlit as st
from campaigns.ipo_revival.run import run_campaign_ui

st.set_page_config(page_title="IPO Revival Radar", layout="wide")
st.title("📡 IPO Revival Radar")

run_campaign_ui()
