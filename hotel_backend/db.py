from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def _build_database_url() -> str:
    if settings.database_url:
        return _normalize_database_url(settings.database_url)

    return (
        f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )


SQLALCHEMY_DATABASE_URL = _build_database_url()

# Setup SQLAlchemy Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Setup SessionLocal factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy Models
Base = declarative_base()

# FastAPI Dependency for injecting the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# BACKWARD COMPATIBILITY FOR LEGACY CODE
# ==========================================
# The functions below use SQLAlchemy text queries so they work with PostgreSQL.

def _param_dict(params=None):
    if params is None:
        return {}
    if isinstance(params, dict):
        return params
    raise TypeError("SQL helper params must be passed as a dict")

def fetch_one(query, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(query), _param_dict(params))
        row = result.mappings().first()
        return dict(row) if row else None

def fetch_all(query, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(query), _param_dict(params))
        return [dict(row) for row in result.mappings().all()]

def execute_query(query, params=None):
    with engine.begin() as conn:
        result = conn.execute(text(query), _param_dict(params))
        last_id = getattr(result, "lastrowid", None)
        if last_id:
            return last_id

        inserted_primary_key = getattr(result, "inserted_primary_key", None)
        if inserted_primary_key and inserted_primary_key[0] is not None:
            return inserted_primary_key[0]

        return True
