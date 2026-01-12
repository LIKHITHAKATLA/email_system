# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime, timezone
from database import Base

try:

    class Lead(Base):
        __tablename__ = "leads"

        id = Column(Integer, primary_key=True)
        name = Column(String(100))
        email = Column(String(150), unique=True, index=True, nullable=False)
        company = Column(String(150))
        industry = Column(String(100))
        pain_points = Column(Text)
        conversation_opener = Column(Text)      # ✅ NEW
        negotiation_angle = Column(Text) 

        draft_subject = Column(Text)
        draft_body = Column(Text)
        draft_type = Column(String(50))   # initial | followup | reply
        draft_ready = Column(Boolean, default=False)
    
        sent_by_human = Column(Boolean, default=False)

        status = Column(String(50), default="NEW", nullable=False)
        last_email_sent = Column(DateTime(timezone=True))
        followup_count = Column(Integer, default=0)
        awaiting_reply = Column(Boolean, default=False)
        last_ai_reply_sent = Column(DateTime(timezone=True))

        intent = Column(String(50))
        sentiment = Column(String(50))


    class EmailLog(Base):
        __tablename__ = "email_logs"

        id = Column(Integer, primary_key=True)
        lead_id = Column(Integer, nullable=False)
        subject = Column(Text, nullable=False)
        body = Column(Text, nullable=False)
        type = Column(String(50), nullable=False)
        timestamp = Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )

except Exception as e:
    raise RuntimeError(f"Model definition error: {e}")
