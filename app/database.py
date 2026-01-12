# # database.py
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy.exc import OperationalError, SQLAlchemyError
# from urllib.parse import quote_plus
# from config import POSTGRES_CONFIG

# Base = declarative_base()

# try:
#     password = quote_plus(POSTGRES_CONFIG["password"])
# except Exception:
#     raise RuntimeError("Invalid PostgreSQL password encoding")


# # -------------------- Root Connection --------------------
# ROOT_DB_URL = (
#     f"postgresql+psycopg2://{POSTGRES_CONFIG['user']}:"
#     f"{password}@{POSTGRES_CONFIG['host']}:"
#     f"{POSTGRES_CONFIG['port']}/postgres"
# )

# try:
#     engine_root = create_engine(ROOT_DB_URL, isolation_level="AUTOCOMMIT")

#     with engine_root.connect() as conn:
#         result = conn.execute(
#             text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
#             {"dbname": POSTGRES_CONFIG["database"]},
#         )

#         if not result.scalar():
#             conn.execute(
#                 text(f'CREATE DATABASE "{POSTGRES_CONFIG["database"]}"')
#             )

# except OperationalError as e:
#     raise RuntimeError(f"PostgreSQL connection failed: {e}")
# except SQLAlchemyError as e:
#     raise RuntimeError(f"Database initialization error: {e}")


# # -------------------- App Database --------------------
# DB_URL = (
#     f"postgresql+psycopg2://{POSTGRES_CONFIG['user']}:"
#     f"{password}@{POSTGRES_CONFIG['host']}:"
#     f"{POSTGRES_CONFIG['port']}/"
#     f"{POSTGRES_CONFIG['database']}"
# )

# try:
#     engine = create_engine(DB_URL, pool_pre_ping=True)
#     SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# except SQLAlchemyError as e:
#     raise RuntimeError(f"Failed to create DB engine: {e}")




# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
from config import get_postgres_config

Base = declarative_base()


def create_db_engine():
    cfg = get_postgres_config()

    if not all(cfg.values()):
        raise RuntimeError("PostgreSQL environment variables are missing")

    password = quote_plus(cfg["password"])

    DATABASE_URL = (
        f"postgresql+psycopg2://{cfg['user']}:{password}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
        "?sslmode=require"
    )

    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


engine = create_db_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
