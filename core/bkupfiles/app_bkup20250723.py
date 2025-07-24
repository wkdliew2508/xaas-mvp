import streamlit as st
from datetime import datetime, timedelta
from core.scraper import WithdrawnIPOScraper
from core.outreach import generate_outreach_message
from core.scorer import score_filing
from core.utils import test_edgar_api_connection

# ------------------------- Sidebar Inputs ------------------------- #
st.sidebar.header("Search Criteria")

start_date = st.sidebar.date_input(
    "Start Date", datetime.today() - timedelta(days=365)
)
end_date = st.sidebar.date_input("End Date", datetime.today())

ASEAN_CITIES = [
    "Singapore", "Kuala Lumpur", "Jakarta", "Ho Chi Minh", "Hanoi",
    "Bangkok", "Manila", "Phnom Penh", "Vientiane", "Naypyidaw",
    "Bandar Seri Begawan", "Kwai Chung", "Wan Chai", "Hong Kong", "China"
]
selected_locations = st.sidebar.multiselect(
    "Filter by Locations", ASEAN_CITIES, default=["Singapore", "Hong Kong"]
)

min_score = st.sidebar.slider("Minimum Score", 0, 100, 50)
industry_keywords = st.sidebar.text_input("Industry Keywords", "fintech, ai")
custom_tags = st.sidebar.text_input("Custom Tags", "IPO Revival")

# ------------------------- API Check ------------------------- #
st.markdown("## EDGAR API Status")
connected, status_msg = test_edgar_api_connection()
st.info(status_msg)

# ------------------------- Run Search ------------------------- #
if st.button("🔍 Run Search"):
    with st.spinner("Fetching filings from EDGAR..."):
        scraper = WithdrawnIPOScraper()
        filings = scraper.get_withdrawn_ipos(start_date, end_date, selected_locations)

    results = []
    for filing in filings:
        filing["score"] = score_filing(filing, industry_keywords)
        if filing["score"] >= min_score:
            filing["tags"] = custom_tags
            filing["outreach"] = generate_outreach_message(filing)
            results.append(filing)

    if results:
        st.markdown("## 🎯 Filtered IPO Revival Targets")
        for r in results:
            with st.expander(f"{r['company']} ({r['filed']}) - Score: {r['score']}"):
                st.write(f"**Location:** {r['location']}")
                st.write(f"**Form Type:** {r['form']}")
                st.write(f"**Tags:** {r['tags']}")
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{r['cik']}/{r['accession_no'].replace('-', '')}/{r['accession_no']}-index.htm"
                st.write(f"**Filing URL:** [{filing_url}]({filing_url})")
                st.text_area("✉️ Outreach Message", r['outreach'])
                if st.button("📤 Send Outreach", key=r['company']):
                    st.success("Outreach sent and logged.")
    else:
        st.warning("No IPO withdrawal filings matched your filters.")

# ------------------------- Outreach Tracker ------------------------- #
st.markdown("## 📈 Outreach Tracker")
# Placeholder — to be replaced with actual outreach history log
dummy_tracker = {
    "Company": ["ABC Corp", "XYZ Ltd"],
    "Last Outreach": ["2025-07-01", "2025-07-10"],
    "Response": ["No reply", "Interested"],
    "Attempts": [1, 2],
    "Next Action": ["Follow-up", "Send deck"]
}
st.dataframe(dummy_tracker)