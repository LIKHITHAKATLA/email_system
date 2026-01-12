from datetime import datetime, timedelta, timezone
from database import SessionLocal
from models import Lead
from email_generator import generate_email
from email_sender import send_email

WAIT_TIME = timedelta(hours=24)
# WAIT_TIME = timedelta(minutes=2)

def check_post_reply_followups():
    session = SessionLocal()
    now = datetime.now(timezone.utc)

    try:
        leads = (
            session.query(Lead)
            .filter(
                Lead.awaiting_reply == True,
                Lead.last_ai_reply_sent.isnot(None),
                Lead.status == "QUALIFIED"
            )
            .with_for_update(skip_locked=True)
            .all()
        )

        for lead in leads:
            sent_time = lead.last_ai_reply_sent
            if sent_time.tzinfo is None:
                sent_time = sent_time.replace(tzinfo=timezone.utc)

            if now - sent_time < WAIT_TIME:
                continue

            subject, body = generate_email(lead, followup=True)

            sent = send_email(
                lead.email,
                subject,
                body,
                raise_on_failure=False
            )

            # if sent:
            #     lead.awaiting_reply = False
            #     lead.last_email_sent = now
            #     lead.followup_count += 1
            if sent:
                lead.awaiting_reply = False
                lead.last_email_sent = now
                lead.followup_count += 1

                # ✅ MARK FOLLOW-UP STATE
                lead.status = "FOLLOWED_UP"


        session.commit()

    except Exception as e:
        session.rollback()
        print(f"❌ Post-reply follow-up error: {e}")

    finally:
        session.close()
