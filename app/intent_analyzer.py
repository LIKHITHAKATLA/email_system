# # intent_analyzer.py
import requests
from requests.exceptions import RequestException, Timeout
# from config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from config import get_openrouter_config

cfg = get_openrouter_config() 


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TIMEOUT_SECONDS = 20

ALLOWED_INTENTS = {
    "interested": "Interested",
    "pricing": "Pricing",
    "call request": "Call Request",
    "question": "Question",
    "not interested": "Not Interested",
}


def analyze_reply(text: str) -> str:
    if not text or not text.strip():
        return "Question"

    prompt = f"""
You are an email intent classifier.

Allowed labels (return EXACTLY one):
- Interested
- Pricing
- Call Request
- Question
- Not Interested

Reply text:
{text}

Return only the label.
"""

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
                    {"role": "system", "content": "You classify email intent."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
            },
            timeout=TIMEOUT_SECONDS,
        )

        if response.status_code != 200:
            print(f"❌ OpenRouter error {response.status_code}: {response.text}")
            return "Question"

        data = response.json()
        choices = data.get("choices")

        if not choices:
            print("❌ OpenRouter response missing choices")
            return "Question"

        content = (
            choices[0]
            .get("message", {})
            .get("content", "")
            .strip()
            .lower()
        )

        # 🔒 CRITICAL FIX
        if "not interested" in content:
            return "Not Interested"

        for key in sorted(ALLOWED_INTENTS, key=len, reverse=True):
            if key in content:
                return ALLOWED_INTENTS[key]

        print(f"⚠️ Unknown intent output: {content}")
        return "Question"

    except Timeout:
        print("❌ Intent analysis timed out")
        return "Question"

    except RequestException as e:
        print(f"❌ Network error during intent analysis: {e}")
        return "Question"

    except Exception as e:
        print(f"❌ Unexpected intent analyzer error: {e}")
        return "Question"
