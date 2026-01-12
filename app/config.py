# # config.py
# import os
# from dotenv import load_dotenv

# try:
#     load_dotenv()
# except Exception as e:
#     raise RuntimeError(f"Failed to load environment variables: {e}")

# def get_env(key, default=None, required=False):
#     value = os.getenv(key, default)

#     if isinstance(value, str):
#         value = value.strip()
#         if value == "":
#             value = None

#     if required and value is None:
#         raise RuntimeError(f"Missing required environment variable: {key}")

#     return value


# # -------------------- OpenRouter --------------------
# OPENROUTER_API_KEY = get_env("OPENROUTER_API_KEY", required=True)
# OPENROUTER_MODEL = get_env("OPENROUTER_MODEL", required=True)


# # -------------------- PostgreSQL --------------------
# try:
#     POSTGRES_CONFIG = {
#         "host": get_env("POSTGRES_HOST", required=True),
#         "port": int(get_env("POSTGRES_PORT", 5432)),
#         "user": get_env("POSTGRES_USER", required=True),
#         "password": get_env("POSTGRES_PASSWORD", required=True),
#         "database": get_env("POSTGRES_DB", required=True),
#     }
# except ValueError:
#     raise RuntimeError("POSTGRES_PORT must be a valid integer")


# # -------------------- SMTP --------------------
# SMTP_EMAIL = get_env("SMTP_EMAIL")
# SMTP_PASSWORD = get_env("SMTP_PASSWORD")

# if bool(SMTP_EMAIL) ^ bool(SMTP_PASSWORD):
#     raise RuntimeError("SMTP_EMAIL and SMTP_PASSWORD must be set together")


# # -------------------- IMAP --------------------
# IMAP_EMAIL = get_env("IMAP_EMAIL")
# IMAP_PASSWORD = get_env("IMAP_PASSWORD")

# if bool(IMAP_EMAIL) ^ bool(IMAP_PASSWORD):
#     raise RuntimeError("IMAP_EMAIL and IMAP_PASSWORD must be set together")




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
        raise RuntimeError("OpenRouter environment variables are missing")

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
