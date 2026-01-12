# initial_sender.py

from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from models import Lead, EmailLog
from email_generator import generate_email
from email_sender import send_email

def generate_initial_drafts():
    session = SessionLocal()

    leads = (
        session.query(Lead)
        .filter(
            Lead.status == "NEW",
            Lead.draft_ready == False
        )
        .with_for_update(skip_locked=True)
        .all()
    )

    for lead in leads:
        subject, body = generate_email(lead, followup=False)

        lead.draft_subject = subject
        lead.draft_body = body
        lead.draft_type = "initial"
        lead.draft_ready = True
        lead.status = "DRAFT_READY"

    session.commit()
    session.close()

# def send_initial_emails():
#     session = SessionLocal()
#     now_utc = datetime.now(timezone.utc)

#     try:
#         leads = (
#             session.query(Lead)
#             .filter(
#                 Lead.status == "NEW",
#                 Lead.intent.is_(None),          # ❌ block replied leads
#                 Lead.awaiting_reply == False,   # ❌ block conversation in progress
#             )
#             .with_for_update(skip_locked=True)
#             .all()
#         )
        

#         for lead in leads:
#             try:
#                 subject, body = generate_email(lead, followup=False)

#                 sent = send_email(
#                     to=lead.email,
#                     subject=subject,
#                     body=body,
#                     raise_on_failure=False,
#                 )

#                 if not sent:
#                     print(f"❌ Initial email failed for {lead.email}")
#                     continue  # do NOT update DB

#                 lead.status = "EMAIL_SENT"
#                 lead.last_email_sent = now_utc
#                 lead.followup_count = 0

#                 log = EmailLog(
#                     lead_id=lead.id,
#                     subject=subject,
#                     body=body,
#                     type="initial",
#                 )

#                 session.add(log)

#             except Exception as e:
#                 # isolate per-lead failure
#                 session.rollback()
#                 print(f"❌ Lead send failed ({lead.email}): {e}")
#                 continue

#         session.commit()

#     except SQLAlchemyError as e:
#         session.rollback()
#         print(f"❌ Database error in initial sender: {e}")

#     except Exception as e:
#         session.rollback()
#         print(f"❌ Unexpected error in initial sender: {e}")

#     finally:
#         session.close()
