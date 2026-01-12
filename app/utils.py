import json
from email_generator import generate_email


# Lead class matching your generator expectations
class Lead:
    def __init__(self, name, email, company, industry, pain_points):
        self.name = name
        self.email = email
        self.company = company
        self.industry = industry
        self.pain_points = pain_points


# Load leads from JSON
with open("data/leads.json", "r", encoding="utf-8") as f:
    leads_data = json.load(f)


# Generate & print emails
for idx, lead_data in enumerate(leads_data, start=1):
    lead = Lead(
        name=lead_data["name"],
        email=lead_data["email"],
        company=lead_data["company"],
        industry=lead_data["industry"],
        pain_points=lead_data["pain_points"]
    )

    subject, body = generate_email(lead, followup=False)

    print("\n" + "=" * 70)
    print(f"EMAIL #{idx}")
    print("=" * 70)
    print(f"\nTO: {lead.email}")
    print(f"SUBJECT:\n{subject}\n")
    print("BODY:\n" + body)
    print("=" * 70)
