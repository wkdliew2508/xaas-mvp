class OutreachGenerator:
    def __init__(self, campaign):
        self.campaign = campaign

    def generate(self, lead):
        company = lead["company"]
        country = lead["country"]
        contact = lead.get("contact", {})
        name = contact.get("name", "there")

        return f"""
Hi {name},

We noticed that {company} had previously explored a listing and withdrew. We're working with select high-growth firms in {country} to re-engage capital markets with stronger positioning.

We offer end-to-end listing services including structuring, financing, and underwriting — with terms that outperform traditional routes.

Would you be open to a short exploratory call?

Best regards,  
[Your Name]  
CrossBorder Listings Team
        """