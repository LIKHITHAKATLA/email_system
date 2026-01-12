# app/config.py
import os
from dotenv import load_dotenv

# Load .env locally (Railway ignores this)
load_dotenv()


def get_env(key: str, default=None) -> str | None:
    value = os.getenv(key, default)
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
    return value


# -------------------- OpenRouter --------------------
def get_openrouter_config():
    api_key = get_env("OPENROUTER_API_KEY")
    model = get_env("OPENROUTER_MODEL")

    if not api_key or not model:
        raise RuntimeError(
            "OPENROUTER_API_KEY and OPENROUTER_MODEL are required. "
            "Please set them in Railway's environment variables or in a .env file for local development."
        )
    return {
        "api_key": api_key,
        "model": model,
    }


# -------------------- PostgreSQL --------------------
def get_postgres_config():
    try:
        port_raw = get_env("POSTGRES_PORT", 5432)

        port = int(port_raw) if port_raw else 5432

        return {
            "host": get_env("POSTGRES_HOST"),
            "port": port,
            "user": get_env("POSTGRES_USER"),
            "password": get_env("POSTGRES_PASSWORD"),
            "database": get_env("POSTGRES_DB"),
        }
    except Exception as e:
        raise RuntimeError(f"Invalid PostgreSQL configuration: {e}")


# -------------------- SMTP --------------------
def get_smtp_config():
    email = get_env("SMTP_EMAIL")
    password = get_env("SMTP_PASSWORD")

    if bool(email) ^ bool(password):
        raise RuntimeError("SMTP_EMAIL and SMTP_PASSWORD must be set together")

    return email, password


# -------------------- IMAP --------------------
def get_imap_config():
    email = get_env("IMAP_EMAIL")
    password = get_env("IMAP_PASSWORD")

    if bool(email) ^ bool(password):
        raise RuntimeError("IMAP_EMAIL and IMAP_PASSWORD must be set together")

    return email, password
