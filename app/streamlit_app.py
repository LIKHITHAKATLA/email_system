import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import datetime, timezone

from database import SessionLocal, engine
from models import Lead, EmailLog
from email_sender import send_email

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Hexanova Email Dashboard",
    layout="wide"
)

st.title("📊 Hexanova AI Email System")

# -------------------------------------------------
# Sidebar Navigation
# -------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    [
        "📧 Email Preview & Send",
        "📌 Leads Table",
        "📨 Mail Chats"
    ]
)

# =================================================
# PAGE 1: EMAIL PREVIEW & SEND
# =================================================
if page == "📧 Email Preview & Send":

    st.subheader("📧 Pending Email Drafts")

    session = SessionLocal()

    drafts = (
        session.query(Lead)
        .filter(Lead.draft_ready == True)
        .order_by(Lead.id.desc())
        .all()
    )

    if not drafts:
        st.info("No emails pending preview.")
    else:
        for lead in drafts:
            with st.expander(
                f"{lead.draft_type.upper()} | {lead.name} | {lead.email}",
                expanded=True
            ):

                subject = st.text_input(
                    "Subject",
                    lead.draft_subject,
                    key=f"sub_{lead.id}"
                )

                body = st.text_area(
                    "Email Body",
                    lead.draft_body,
                    height=240,
                    key=f"body_{lead.id}"
                )

                col1, col2 = st.columns(2)

                # ✅ SEND EMAIL
                with col1:
                    if st.button("✅ Send Email", key=f"send_{lead.id}"):

                        sent = send_email(
                            to=lead.email,
                            subject=subject,
                            body=body
                        )

                        if sent:
                            lead.draft_ready = False
                            lead.sent_by_human = True
                            lead.last_email_sent = datetime.now(timezone.utc)

                            if lead.draft_type == "initial":
                                lead.status = "EMAIL_SENT"
                                lead.followup_count = 0

                            elif lead.draft_type == "followup":
                                lead.status = "FOLLOWUP_SENT"
                                lead.followup_count += 1

                            elif lead.draft_type == "reply":
                                lead.awaiting_reply = True
                                lead.last_ai_reply_sent = datetime.now(timezone.utc)

                            session.add(
                                EmailLog(
                                    lead_id=lead.id,
                                    subject=subject,
                                    body=body,
                                    type=lead.draft_type
                                )
                            )

                            session.commit()
                            st.success("Email sent successfully ✅")

                # ❌ DISCARD DRAFT
                with col2:
                    if st.button("❌ Discard Draft", key=f"discard_{lead.id}"):
                        lead.draft_ready = False
                        lead.draft_subject = None
                        lead.draft_body = None
                        lead.draft_type = None
                        session.commit()
                        st.warning("Draft discarded")

    session.close()

# =================================================
# PAGE 2: LEADS TABLE


elif page == "📌 Leads Table":

    st.subheader("📌 Leads Overview")

    # -------------------------------------------------
    # FETCH ALL LEAD DATA
    # -------------------------------------------------
    query = """
    SELECT
        id,
        name,
        email,
        company,
        industry,
        pain_points,
        conversation_opener,
        negotiation_angle,

        draft_subject,
        draft_body,
        draft_type,
        draft_ready,
        sent_by_human,

        status,
        followup_count,
        awaiting_reply,
        intent,
        sentiment,

        last_email_sent,
        last_ai_reply_sent
    FROM leads
    ORDER BY id ASC
    """

    df = pd.read_sql(text(query), engine)

    # -------------------------------------------------
    # TOP: TABLE VIEW (FULL DATA)
    # -------------------------------------------------
    st.markdown("### 📋 Leads Table (All Fields)")
    # st.dataframe(df, use_container_width=True)
    st.dataframe(df, width="stretch")


    if df.empty:
        st.info("No leads available.")
        st.stop()

    # -------------------------------------------------
    # BOTTOM: DETAILED LEAD VIEW
    # -------------------------------------------------
    st.markdown("---")
    st.markdown("### 🔍 Lead Details")

    selected_email = st.selectbox(
        "Select a lead to view details",
        df["email"].tolist()
    )

    lead = df[df["email"] == selected_email].iloc[0]

    # -------------------------------------------------
    # BASIC INFO
    # -------------------------------------------------
    st.markdown("#### 👤 Basic Information")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        **Name:** {lead['name'] or '-'}  
        **Email:** {lead['email']}  
        **Company:** {lead['company'] or '-'}  
        **Industry:** {lead['industry'] or '-'}  
        """)

    with col2:
        st.markdown(f"""
        **Status:** `{lead['status']}`  
        **Intent:** {lead['intent'] or '-'}  
        **Sentiment:** {lead['sentiment'] or '-'}  
        **Follow-ups Sent:** {lead['followup_count']}  
        """)

    # -------------------------------------------------
    # COMMUNICATION CONTEXT
    # -------------------------------------------------
    st.markdown("#### 🧠 Communication Context")

    st.markdown(f"""
    **Pain Points:**  
    {lead['pain_points'] or '—'}

    **Conversation Opener:**  
    {lead['conversation_opener'] or '—'}

    **Negotiation Angle:**  
    {lead['negotiation_angle'] or '—'}
    """)

    # -------------------------------------------------
    # DRAFT / AI STATE
    # -------------------------------------------------
    st.markdown("#### ✍️ Draft / AI State")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown(f"""

        **Draft Type:** {lead['draft_type'] or '-'}    
        """)

    with col4:
        st.markdown(f"""
         
        **Last Email Sent:** {lead['last_email_sent'] or '—'}  
        **Last AI Reply Sent:** {lead['last_ai_reply_sent'] or '—'}  
        """)

    # -------------------------------------------------
    # DRAFT CONTENT (READ-ONLY)
    # -------------------------------------------------
    st.markdown("#### 📄 Draft Content (Read-only)")

    st.text_area(
        "Draft Subject",
        lead["draft_subject"] or "",
        height=50,
        disabled=True
    )

    st.text_area(
        "Draft Body",
        lead["draft_body"] or "",
        height=200,
        disabled=True
    )


# =================================================
# PAGE 3: MAIL CHATS / CONVERSATION
# =================================================
elif page == "📨 Mail Chats":

    st.subheader("📨 Conversation Timeline")

    emails_df = pd.read_sql(
        text("SELECT DISTINCT email FROM leads ORDER BY email"),
        engine
    )

    if emails_df.empty:
        st.info("No leads available.")
    else:
        selected_email = st.selectbox(
            "Select a person",
            emails_df["email"].tolist()
        )

        logs_query = """
        SELECT
            email_logs.type,
            email_logs.subject,
            email_logs.body,
            email_logs.timestamp
        FROM email_logs
        JOIN leads ON leads.id = email_logs.lead_id
        WHERE leads.email = :email
        ORDER BY email_logs.timestamp ASC
        """

        logs = pd.read_sql(
            text(logs_query),
            engine,
            params={"email": selected_email}
        )

        if logs.empty:
            st.info("No conversation found.")
        else:
            for _, row in logs.iterrows():
                icon = {
                    "initial": "📤 Initial",
                    "reply": "📩 Reply",
                    "ai_reply": "🤖 AI Reply",
                    "followup": "⏰ Follow-up"
                }.get(row["type"], "✉️ Email")

                with st.expander(f"{icon} | {row['timestamp']}"):
                    st.markdown(f"**Subject:** {row['subject']}")
                    st.markdown("---")
                    st.text(row["body"])

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.caption("✅ Human-in-the-loop · Safe · Production-ready")

