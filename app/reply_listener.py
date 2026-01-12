# reply_listener.py
import imaplib
import email
from email.utils import parseaddr
from datetime import datetime, timezone

from database import SessionLocal
from models import Lead, EmailLog
from intent_analyzer import analyze_reply
from email_generator import generate_reply_email
from config import get_imap_config

IMAP_SERVER = "imap.gmail.com"
IMAP_FOLDER = "INBOX"


def extract_body(msg):
    body = ""

    try:
        if msg.is_multipart():
            for part in msg.walk():
                if (
                    part.get_content_type() == "text/plain"
                    and "attachment" not in str(part.get("Content-Disposition"))
                ):
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
    except Exception:
        return ""

    for sep in ["\nOn ", "\n>"]:
        if sep in body:
            body = body.split(sep)[0]

    return body.strip()


def listen_replies():
    print("🔍 Checking for new replies...")

    # ✅ GET IMAP CONFIG (FIX)
    try:
        IMAP_EMAIL, IMAP_PASSWORD = get_imap_config()
    except Exception as e:
        print(f"⚠️ IMAP config error: {e}")
        return

    if not IMAP_EMAIL or not IMAP_PASSWORD:
        print("⚠️ IMAP not configured, skipping reply listener")
        return

    session = SessionLocal()
    mail = None

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(IMAP_EMAIL, IMAP_PASSWORD)
        mail.select(IMAP_FOLDER)

        status, data = mail.search(None, "(UNSEEN)")
        if status != "OK" or not data or not data[0]:
            return

        for num in data[0].split():
            try:
                _, msg_data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                from_email = parseaddr(msg.get("From"))[1]
                reply_text = extract_body(msg)

                if not from_email or not reply_text:
                    continue

                lead = (
                    session.query(Lead)
                    .filter_by(email=from_email)
                    .with_for_update()
                    .first()
                )

                if not lead:
                    print(f"⚠️ No lead found for {from_email}")
                    continue

                print(f"📩 Reply from {from_email}")

                # 📥 Log inbound reply
                session.add(
                    EmailLog(
                        lead_id=lead.id,
                        subject=msg.get("Subject", ""),
                        body=reply_text,
                        type="reply",
                    )
                )

                intent = analyze_reply(reply_text)
                lead.intent = intent
                lead.awaiting_reply = False
                lead.last_email_sent = datetime.now(timezone.utc)

                # 🎯 sentiment & state
                if intent == "Not Interested":
                    lead.sentiment = "negative"
                    lead.status = "CLOSED"
                elif intent in ("Interested", "Call Request"):
                    lead.sentiment = "positive"
                    lead.status = "QUALIFIED"
                else:
                    lead.sentiment = "neutral"
                    lead.status = "QUALIFIED"

                # ✍️ Generate AI REPLY DRAFT (NO AUTO-SEND)
                if intent != "Not Interested" and not lead.draft_ready:
                    subject, body = generate_reply_email(lead, reply_text)

                    lead.draft_subject = subject
                    lead.draft_body = body
                    lead.draft_type = "reply"
                    lead.draft_ready = True
                    lead.status = "DRAFT_READY"

                session.commit()

                # ✅ mark email as seen
                mail.store(num, "+FLAGS", "\\Seen")

            except Exception as e:
                session.rollback()
                print(f"❌ Failed processing reply: {e}")
                continue

    except Exception as e:
        print(f"❌ IMAP listener error: {e}")

    finally:
        session.close()
        if mail:
            try:
                mail.logout()
            except Exception:
                pass

        print("✅ Reply check completed")
