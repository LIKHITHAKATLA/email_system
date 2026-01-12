
# email_generator.py
import requests
from requests.exceptions import RequestException, Timeout
# from config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from config import get_openrouter_config
cfg = get_openrouter_config()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TIMEOUT_SECONDS = 25


class EmailGenerationError(Exception):
    pass


def _call_openrouter(prompt: str, temperature: float):
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": cfg["model"],
                "messages": [
                    {"role": "system", "content": "You generate structured emails."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
            },
            timeout=TIMEOUT_SECONDS,
        )

        if response.status_code != 200:
            raise EmailGenerationError(
                f"OpenRouter HTTP {response.status_code}: {response.text}"
            )

        data = response.json()
        choices = data.get("choices")

        if not choices:
            raise EmailGenerationError("OpenRouter response missing choices")

        content = (
            choices[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not content:
            raise EmailGenerationError("Empty LLM response")

        return content

    except Timeout:
        raise EmailGenerationError("OpenRouter request timed out")
    except RequestException as e:
        raise EmailGenerationError(f"Network error: {e}")
    except Exception as e:
        raise EmailGenerationError(f"Unexpected error: {e}")


def _parse_subject_body(content: str):
    """
    Enforces strict SUBJECT/BODY extraction.
    """
    upper = content.upper()

    if "SUBJECT:" not in upper or "BODY:" not in upper:
        raise EmailGenerationError("LLM output missing SUBJECT or BODY")

    try:
        subject = content.split("SUBJECT:", 1)[1].split("BODY:", 1)[0].strip()
        body = content.split("BODY:", 1)[1].strip()
    except Exception:
        raise EmailGenerationError("Failed to parse SUBJECT/BODY")

    if not subject or not body:
        raise EmailGenerationError("Empty subject or body")

    return subject, body


# ------------------------------------------------------------------------------
# Initial / Follow-up Email Generator
# ------------------------------------------------------------------------------
def generate_email(lead, followup=False, previous_emails=""):
    try:
        if not followup:
            # prompt = f"""
            #     You are a senior B2B outreach copywriter writing on behalf of Hexanova MediaTech.

            #     STRICT OUTPUT CONTRACT:
            #     Return ONLY in this format:

            #     SUBJECT:
            #     <subject>

            #     BODY:
            #     <body>

            #     Rules:
            #     - 60–80 words
            #     - Calm, human, non-salesy
            #     - One subtle situational tension
            #     - No service listing
            #     - End exactly with:

            #     Best regards,
            #     Hexanova MediaTech

            #     Lead:
            #     Name: {lead.name}
            #     Company: {lead.company}
            #     Industry: {lead.industry}

            #     Internal context (do not quote):
            #     {lead.pain_points}
            # """
            

            prompt = f"""
You are a senior B2B outreach copywriter writing on behalf of Hexanova MediaTech.

GOAL:
Write a calm, thoughtful cold email (60–80 words) as a 1-to-1 relevance check — not a pitch.

TONE:
- Professional, human, grounded
- Neutral and non-salesy
- No hype, no marketing language

ABOUT HEXANOVA MEDIATEK (INTERNAL CONTEXT – DO NOT QUOTE):
Hexanova MediaTech builds practical and immersive digital systems across web, mobile, AI, 3D, and AR/VR. 
The team works with growing organizations to design scalable platforms and interactive experiences, often where execution speed, clarity, and long-term maintainability matter.

TENSION RULES:
- Imply ONLY ONE situational tension
- Derive it ONLY from internal context below
- Never assume it applies to the recipient
- Frame as something teams in similar environments often think about
- If context is weak or empty, use a neutral, widely applicable tension
- Mention the tension subtly in ONE short sentence

COMPANY CONTEXT USAGE RULE:
- Use company context only to sound credible and relevant
- NEVER list services or technologies
- NEVER position Hexanova as a vendor or provider
- At most one subtle capability may be implied, only if it naturally aligns with the lead’s industry
- It is acceptable to not reference the company’s work at all

FORMAT (STRICT):
Return output in EXACTLY this format:

SUBJECT:
<3–5 word curiosity-driven subject reflecting the tension>

BODY:
<email body>

STRUCTURE RULES:
- Include a brief neutral greeting (e.g., “Hi <Name>,” or “Hope you’re having a good week at <Company>.”)
- Greeting does NOT count as the opening line
- Opening line: max 1 sentence, observational, neutral
- Short paragraphs (1–2 lines)
- Short, clear sentences

STYLE CONSTRAINTS:
- 60–80 words total
- No flattery, metrics, bold claims, service lists
- Do NOT use these words: pain, problem, challenge, issue, struggle, need, solution

CTA:
- Optional, max 1 sentence
- Low-pressure (e.g., “If you’re open, we could schedule a quick 10-minute chat.”)

NAMING & SIGNATURE:
- Mention Hexanova MediaTech at most once
- End exactly with:

Best regards,
Hexanova MediaTech

Lead:
Name: {lead.name}
Company: {lead.company}
Industry: {lead.industry}

Internal context (do not quote, may be empty):
{lead.pain_points}
Additional internal guidance (DO NOT QUOTE OR PARAPHRASE DIRECTLY):
- Conversation opener (tone reference only):
{lead.conversation_opener}

- Negotiation angle (strategic framing only):
{lead.negotiation_angle}
IMPORTANT:
Never reuse or closely paraphrase the conversation opener text.
Use it only to understand the lead’s role, context, and sensitivity.
"""

            temperature = 0.35

        else:
            prompt = f"""
You are a senior B2B outreach copywriter writing on behalf of Hexanova MediaTech.

GOAL:
Write a calm, thoughtful cold email (60–80 words) as a 1-to-1 relevance check — not a pitch.

TONE:
- Professional, human, grounded
- Neutral and non-salesy
- No hype, no marketing language

ABOUT HEXANOVA MEDIATEK (INTERNAL CONTEXT – DO NOT QUOTE):
Hexanova MediaTech builds practical and immersive digital systems across web, mobile, AI, 3D, and AR/VR. 
The team works with growing organizations to design scalable platforms and interactive experiences, often where execution speed, clarity, and long-term maintainability matter.

TENSION RULES:
- Imply ONLY ONE situational tension
- Derive it ONLY from internal context below
- Never assume it applies to the recipient
- Frame as something teams in similar environments often think about
- If context is weak or empty, use a neutral, widely applicable tension
- Mention the tension subtly in ONE short sentence

COMPANY CONTEXT USAGE RULE:
- Use company context only to sound credible and relevant
- NEVER list services or technologies
- NEVER position Hexanova as a vendor or provider
- At most one subtle capability may be implied, only if it naturally aligns with the lead’s industry
- It is acceptable to not reference the company’s work at all

FORMAT (STRICT):
Return output in EXACTLY this format:

SUBJECT:
<3–5 word curiosity-driven subject reflecting the tension>

BODY:
<email body>

STRUCTURE RULES:
- Include a brief neutral greeting (e.g., “Hi <Name>,” or “Hope you’re having a good week at <Company>.”)
- Greeting does NOT count as the opening line
- Opening line: max 1 sentence, observational, neutral
- Short paragraphs (1–2 lines)
- Short, clear sentences

STYLE CONSTRAINTS:
- 60–80 words total
- No flattery, metrics, bold claims, service lists
- Do NOT use these words: pain, problem, challenge, issue, struggle, need, solution

CTA:
- Optional, max 1 sentence
- Low-pressure (e.g., “If you’re open, we could schedule a quick 10-minute chat.”)

NAMING & SIGNATURE:
- Mention Hexanova MediaTech at most once
- End exactly with:

Best regards,
Hexanova MediaTech

Lead:
Name: {lead.name}
Company: {lead.company}
Industry: {lead.industry}

Internal context (do not quote, may be empty):
{lead.pain_points}
Additional internal guidance (DO NOT QUOTE OR PARAPHRASE DIRECTLY):
- Conversation opener (tone reference only):
{lead.conversation_opener}

- Negotiation angle (strategic framing only):
{lead.negotiation_angle}
IMPORTANT:
Never reuse or closely paraphrase the conversation opener text.
Use it only to understand the lead’s role, context, and sensitivity.
"""

            temperature = 0.3

        content = _call_openrouter(prompt, temperature)
        return _parse_subject_body(content)

    except EmailGenerationError as e:
        # 🔒 graceful fallback
        print(f"❌ Email generation failed: {e}")

        fallback_subject = "Quick note"
        fallback_body = (
            f"Hi {lead.name},\n\n"
            "Just wanted to briefly follow up and see if this is relevant at all.\n\n"
            "Best regards,\n"
            "Hexanova MediaTech"
        )

        return fallback_subject, fallback_body


# ------------------------------------------------------------------------------
# Reply Email Generator
# ------------------------------------------------------------------------------
def generate_reply_email(lead, reply_text):
    try:
        prompt = f"""
You are replying to an inbound email.

STRICT OUTPUT CONTRACT:
Return ONLY in this format:

SUBJECT:
<subject>

BODY:
<body>

Rules:
- Under 90 words
- Respect intent
- No selling
- Start with: Hi {lead.name},
- End exactly with:

Best regards,
Hexanova MediaTech

Lead:
Name: {lead.name}
Company: {lead.company}

Reply:
\"\"\"
{reply_text}
\"\"\"
"""
        content = _call_openrouter(prompt, temperature=0.2)
        return _parse_subject_body(content)

    except EmailGenerationError as e:
        print(f"❌ Reply generation failed: {e}")

        fallback_subject = "Re: Thanks for your note"
        fallback_body = (
            f"Hi {lead.name},\n\n"
            "Thanks for getting back. I appreciate you sharing your thoughts.\n\n"
            "Best regards,\n"
            "Hexanova MediaTech"
        )

        return fallback_subject, fallback_body
