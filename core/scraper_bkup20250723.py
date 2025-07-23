import requests
from datetime import datetime, timedelta
from core.utils import is_asean_location

class WithdrawnIPOScraper:
    def __init__(self, days_back=365):
        self.base_url = "https://efts.sec.gov/LATEST/search-index"
        self.days_back = days_back

    def fetch_data(self):
        query = {
            "keys": ["rw"],
            "startdt": (datetime.today() - timedelta(days=self.days_back)).strftime("%Y-%m-%d"),
            "enddt": datetime.today().strftime("%Y-%m-%d"),
            "category": "custom",
            "forms": ["RW"]
        }

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "XaaS-MVP/0.1 (contact: david@example.com)"
        }

        try:
            response = requests.post(self.base_url, json=query, headers=headers, timeout=10)
            response.raise_for_status()
            results = response.json().get("hits", {}).get("hits", [])
            print(f"✅ Total filings fetched from EDGAR: {len(results)}")
            filtered = self.filter_asean(results)
            print(f"🌏 ASEAN-related filings: {len(filtered)}")
            return filtered

        except requests.RequestException as e:
            print(f"❌ Error fetching EDGAR data: {e}")
            return []

    def filter_asean(self, results):
        filtered = []
        for result in results:
            try:
                location = result["_source"].get("filing_entity_city", "") + " " + \
                           result["_source"].get("filing_entity_state", "") + " " + \
                           result["_source"].get("filing_entity_country", "")
                if is_asean_location(location):
                    filtered.append({
                        "company": result["_source"].get("companyName", "N/A"),
                        "form": result["_source"].get("formType", "RW"),
                        "location": location,
                        "filed": result["_source"].get("filedAt", ""),
                        "cik": result["_source"].get("cik", ""),
                        "accession_no": result["_id"]
                    })
            except Exception as e:
                print(f"⚠️ Error processing record: {e}")
        return filtered

    def get_withdrawn_ipos(self, start_date, end_date, selected_locations):
        all_filings = self.fetch_data()
        print(f"📆 Filtering filings between {start_date} and {end_date} in locations: {selected_locations}")
        results = []
        for f in all_filings:
            try:
                filed_date = datetime.strptime(f["filed"][:10], "%Y-%m-%d").date()
                if start_date <= filed_date <= end_date:
                    if any(loc.lower() in f["location"].lower() for loc in selected_locations):
                        results.append(f)
            except Exception as e:
                print(f"⚠️ Date/location filter error: {e}")
        print(f"✅ Final matching results: {len(results)}")
        return results