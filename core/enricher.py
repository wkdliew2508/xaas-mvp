class ContactEnricher:
    def find_contact(self, lead):
        return {
            "name": "Jane Doe",
            "email": f"ceo@{lead['company'].replace(' ', '').lower()}.com"
        }