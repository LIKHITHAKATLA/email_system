# followup_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, timezone
from database import SessionLocal
from models import Lead
from email_generator import generate_email

scheduler = BackgroundScheduler()

MAX_FOLLOWUPS = 3
FOLLOWUP_DELAY = timedelta(minutes=5)  # change for prod


def check_followups():
    session = SessionLocal()
    now_utc = datetime.now(timezone.utc)

    try:
        leads = (
            session.query(Lead)
            .filter(
                Lead.status.in_(["EMAIL_SENT", "FOLLOWUP_SENT"]),
                Lead.last_email_sent.isnot(None),
                Lead.followup_count < MAX_FOLLOWUPS,
                Lead.draft_ready == False,   # 🔒 prevent duplicate drafts
            )
            .with_for_update(skip_locked=True)
            .all()
        )

        for lead in leads:
            sent_time = lead.last_email_sent
            if sent_time.tzinfo is None:
                sent_time = sent_time.replace(tzinfo=timezone.utc)

            # ⏳ wait before follow-up
            if now_utc - sent_time < FOLLOWUP_DELAY:
                continue

            try:
                subject, body = generate_email(lead, followup=True)

                # ✅ SAVE AS DRAFT (NO SENDING)
                lead.draft_subject = subject
                lead.draft_body = body
                lead.draft_type = "followup"
                lead.draft_ready = True
                lead.status = "DRAFT_READY"

            except Exception as e:
                print(f"❌ Follow-up draft failed for {lead.email}: {e}")
                session.rollback()
                continue

        session.commit()

    except Exception as e:
        session.rollback()
        print(f"❌ Scheduler error: {e}")

    finally:
        session.close()


def start_scheduler():
    scheduler.add_job(
        check_followups,
        trigger="interval",
        seconds=30,
        max_instances=1,   # 🔒 prevents overlap
        coalesce=True,
    )
    scheduler.start()
    return scheduler
