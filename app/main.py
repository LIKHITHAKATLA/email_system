import time
import sys

from database import engine, Base

from lead_ingestion import ingest_leads
from initial_sender import generate_initial_drafts
from followup_scheduler import start_scheduler
from reply_listener import listen_replies
from post_reply_followup import check_post_reply_followups


def bootstrap_database():
    try:
        Base.metadata.create_all(engine)
        print("✅ Database schema ready")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)


def bootstrap_ingestion():
    try:
        ingest_leads("data/leads.json")
        print("✅ Lead ingestion completed")
    except FileNotFoundError:
        print("⚠️ Leads file not found, skipping ingestion")
    except Exception as e:
        print(f"❌ Lead ingestion failed: {e}")


def bootstrap_initial_drafts():
    try:
        generate_initial_drafts()
        print("✅ Initial email drafts generated")
    except Exception as e:
        print(f"❌ Initial draft generation failed: {e}")


def bootstrap_scheduler():
    scheduler = start_scheduler()

    # ✍️ Generate initial email drafts periodically
    scheduler.add_job(
        generate_initial_drafts,
        trigger="interval",
        minutes=10,
        max_instances=1,
        coalesce=True,
        id="initial_draft_generator",
        replace_existing=True,
    )

    # 🔁 Listen for incoming replies (draft replies only)
    scheduler.add_job(
        listen_replies,
        trigger="interval",
        minutes=2,
        max_instances=1,
        coalesce=True,
        id="reply_listener",
        replace_existing=True,
    )

    # ⏰ Generate post-reply follow-up drafts
    scheduler.add_job(
        check_post_reply_followups,
        trigger="interval",
        minutes=1,
        max_instances=1,
        coalesce=True,
        id="post_reply_followup",
        replace_existing=True,
    )

    print("✅ Scheduler started")
    return scheduler


def main():
    print("🚀 Starting Hexanova AI Marketing Email Agent")

    bootstrap_database()
    bootstrap_ingestion()

    # 🔥 Generate initial drafts ONCE at startup
    bootstrap_initial_drafts()

    scheduler = bootstrap_scheduler()

    try:
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        print("🛑 Shutdown requested")

    finally:
        print("🧹 Stopping scheduler...")
        scheduler.shutdown(wait=False)
        print("✅ Clean shutdown complete")


if __name__ == "__main__":
    main()



