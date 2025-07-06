def run_campaign_ui():
    import streamlit as st
    import pandas as pd
    from core.scraper import WithdrawnIPOScraper
    from core.enricher import ContactEnricher
    from core.outreach import OutreachGenerator
    from core.scorer import IPORevivalScorer
    from core.utils import compute_signal_deltas, load_outreach_log, update_outreach_log, update_outcome

    st.sidebar.header("🔍 IPO Filter Options")
    run_button = st.sidebar.button("Run Campaign")

    if run_button:
        st.info("Scraping withdrawn IPO data...")
        scraper = WithdrawnIPOScraper()
        leads = scraper.scrape()

        scorer = IPORevivalScorer()
        scored_leads = []
        for lead in leads:
            score, signal_breakdown = scorer.score(lead)
            lead.update({"score": score, "signals": signal_breakdown})
            scored_leads.append(lead)

        deltas = compute_signal_deltas(scored_leads)

        enricher = ContactEnricher()
        enriched = [lead | {"contact": enricher.find_contact(lead)} for lead in scored_leads]

        generator = OutreachGenerator(campaign="ipo_revival")
        st.success(f"🎯 {len(enriched)} leads enriched and scored")

        log = load_outreach_log()

        table_data = []
        for lead in enriched:
            contact = lead.get("contact", {})
            company = lead["company"]
            st.markdown("---")
            st.subheader(f"🏢 {company} ({lead['country']})")
            st.metric("Score", lead["score"])
            st.text(f"Contact: {contact.get('name', 'N/A')} | {contact.get('email', 'N/A')}")

            with st.expander("📊 Score Breakdown"):
                for k, v in lead["signals"].items():
                    st.write(f"{k}: {v}")
                delta = deltas.get(company)
                if delta:
                    st.info(f"📈 Daily Movement: {delta:+} pts")

            with st.expander("✉️ Outreach Preview & Send"):
                message = generator.generate(lead)
                editable_msg = st.text_area("Edit Message:", value=message, key=company)
                if st.button("Send Outreach", key=f"send_{company}"):
                    update_outreach_log(company)
                    st.success("Outreach sent and logged.")

                outcome = st.selectbox(
                    "Update Outcome:", ["", "Interested", "No Reply", "Rejected"], key=f"outcome_{company}"
                )
                if outcome:
                    update_outcome(company, outcome)
                    st.info(f"Outcome for {company} set to '{outcome}'.")

            entry = log.get(company, {"count": 0, "last_contacted": "Never", "outcome": "-"})
            table_data.append({
                "Company": company,
                "Contact Email": contact.get("email", "N/A"),
                "Outreach Count": entry["count"],
                "Last Contacted": entry["last_contacted"],
                "Outcome": entry.get("outcome", "-")
            })

        st.markdown("## 📬 Outreach Log")
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)