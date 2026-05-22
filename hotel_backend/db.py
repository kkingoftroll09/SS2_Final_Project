from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import pymysql
from config import settings

# Create SQLAlchemy Database URL for MySQL
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

# Setup SQLAlchemy Engine (MySQL only)
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
# The functions below use the SQLAlchemy engine's underlying DBAPI connection
# to allow existing raw SQL queries with `%s` parameters to continue working
# during the transition to SQLAlchemy ORM models.

def fetch_one(query, params=None):
    with engine.connect() as conn:
        cursor = conn.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        cursor.close()
        return row

def fetch_all(query, params=None):
    with engine.connect() as conn:
        cursor = conn.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return rows

def execute_query(query, params=None):
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        cursor.execute(query, params or ())
        conn.connection.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id if last_id else True
