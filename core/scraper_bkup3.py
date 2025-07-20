import requests
from datetime import datetime, timedelta
from core.utils import is_asean_location

class WithdrawnIPOScraper:
    def __init__(self, days_back=365):
        self.base_url = "https://efts.sec.gov/LATEST/search-index"
        self.days_back = days_back

    def get_withdrawn_ipos(self, start_date, end_date, selected_locations):
        query = {
            "keys": ["rw"],
            "startdt": start_date.strftime("%Y-%m-%d"),
            "enddt": end_date.strftime("%Y-%m-%d"),
            "category": "custom",
            "forms": ["RW"]
        }

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            # ✅ Proper User-Agent required by SEC
            "User-Agent": "XaaS-MVP/0.1 (contact: david@example.com)"
        }

        try:
            response = requests.post(self.base_url, json=query, headers=headers, timeout=10)
            response.raise_for_status()
            results = response.json().get("hits", {}).get("hits", [])
            return self.filter_asean(results, selected_locations)
        except requests.RequestException as e:
            print(f"Error fetching EDGAR data: {e}")
            return []

    def filter_asean(self, results, selected_locations):
        filtered = []
        for result in results:
            try:
                source = result["_source"]
                location = (
                    source.get("filing_entity_city", "") + " " +
                    source.get("filing_entity_state", "") + " " +
                    source.get("filing_entity_country", "")
                )

                if is_asean_location(location, selected_locations):
                    filtered.append({
                        "company_name": source.get("companyName", "N/A"),
                        "form": source.get("formType", "RW"),
                        "location": location.strip(),
                        "filing_date": source.get("filedAt", ""),
                        "industry": source.get("business", "N/A"),
                        "filing_url": f"https://www.sec.gov/Archives/edgar/data/{source.get('cik', '')}/{result['_id']}.txt"
                    })
            except Exception as e:
                print(f"Error processing record: {e}")
        return filtered