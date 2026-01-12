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





# # app/database.py
# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from dotenv import load_dotenv

# # Load from .env file if it exists (for local development)
# load_dotenv(override=False)

# Base = declarative_base()

# _engine = None
# SessionLocal = None


# def get_engine():
#     """Lazy initialization of database engine"""
#     global _engine
    
#     if _engine is None:
#         DATABASE_URL = os.getenv("DATABASE_URL")
        
#         if not DATABASE_URL:
#             raise RuntimeError(
#                 "DATABASE_URL is not set in environment variables. "
#                 "Please set it in Railway's environment variables or in a .env file for local development."
#             )
        
#         _engine = create_engine(
#             DATABASE_URL,
#             pool_pre_ping=True,
#             pool_size=5,
#             max_overflow=10,
#         )
    
#     return _engine


# def get_session_local():
#     """Get sessionmaker, initializing engine if needed"""
#     global SessionLocal
    
#     if SessionLocal is None:
#         engine = get_engine()
#         SessionLocal = sessionmaker(
#             bind=engine,
#             autocommit=False,
#             autoflush=False,
#         )
    
#     return SessionLocal


# # For backwards compatibility with existing imports
# @property
# def engine():
#     return get_engine()

# # This makes engine accessible as a module-level variable
# engine = property(lambda self: get_engine())
