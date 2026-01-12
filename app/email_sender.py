# email_sender.py
import smtplib
import socket
from email.mime.text import MIMEText
from typing import Optional

# from config import SMTP_EMAIL, SMTP_PASSWORD
from config import get_smtp_config

smtp_email, smtp_password = get_smtp_config()


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_TIMEOUT = 20  # seconds


class EmailSendError(Exception):
    pass


def send_email(
    to: str,
    subject: str,
    body: str,
    *,
    raise_on_failure: bool = False
) -> bool:
    """
    Sends an email safely.
    Returns True if sent, False if failed.
    """

    smtp_email, smtp_password = get_smtp_config()  # ✅ ADD THIS
    if not to or not subject or not body:
        msg = "Invalid email payload (to/subject/body)"
        if raise_on_failure:
            raise EmailSendError(msg)
        print(f"❌ {msg}")
        return False

    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = smtp_email      # ✅ CHANGED
        msg["To"] = to
        msg["Subject"] = subject

        with smtplib.SMTP_SSL(
            SMTP_HOST,
            SMTP_PORT,
            timeout=SMTP_TIMEOUT
        ) as server:
            server.login(smtp_email, smtp_password)  # ✅ CHANGED
            server.send_message(msg)

        print(f"✅ Email sent to {to}")
        return True

    except smtplib.SMTPAuthenticationError:
        error = "SMTP authentication failed (check email/password or app password)"
    except smtplib.SMTPRecipientsRefused:
        error = f"Recipient address rejected: {to}"
    except smtplib.SMTPServerDisconnected:
        error = "SMTP server disconnected unexpectedly"
    except socket.timeout:
        error = "SMTP connection timed out"
    except smtplib.SMTPException as e:
        error = f"SMTP error: {e}"
    except Exception as e:
        error = f"Unexpected error while sending email: {e}"

    print(f"❌ {error}")

    if raise_on_failure:
        raise EmailSendError(error)

    return False
