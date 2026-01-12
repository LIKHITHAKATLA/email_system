# # #lead_ingestion.py for pain point is string

import json
from sqlalchemy.exc import IntegrityError
from email_validator import validate_email, EmailNotValidError
from database import SessionLocal
from models import Lead


def ingest_leads(json_path):
    session = SessionLocal()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ✅ THIS IS THE FIX
    leads = data.get("leads", [])

    for l in leads:
        email = (l.get("email") or "").strip().lower()
        if not email:
            print("⚠️ Skipping lead with empty email")
            continue

        try:
            validate_email(email)
        except EmailNotValidError:
            print(f"⚠️ Invalid email skipped: {email}")
            continue

        pain = l.get("pain_points")
        if isinstance(pain, list):
            pain = ", ".join(pain)
        elif isinstance(pain, str):
            pain = pain.strip()
        else:
            pain = None

        lead = Lead(
            name=l.get("name"),
            email=email,
            company=l.get("company"),
            industry=l.get("industry"),
            pain_points=pain,
            conversation_opener=l.get("conversation_opener"),
            negotiation_angle=l.get("negotiation_angle"),
            status="NEW",
            followup_count=0,
        )

        try:
            session.add(lead)
            session.commit()  # 🔒 commit per lead

        except IntegrityError:
            session.rollback()
            print(f"⚠️ Duplicate lead skipped: {email}")
            continue

        except Exception as e:
            session.rollback()
            print(f"❌ Failed to ingest lead {email}: {e}")
            continue

    session.close()
