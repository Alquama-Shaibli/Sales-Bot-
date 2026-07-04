"""
database.py — PostgreSQL Connection & Session Management
Handles SQLAlchemy engine, connection pooling, and session lifecycle.
"""
import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
from config import settings

logger = logging.getLogger(__name__)

# ── Engine ──────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,          # Verify connections before use
    pool_recycle=3600,           # Recycle connections every hour
    echo=settings.debug,         # Log SQL in debug mode
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"   # 30s query timeout
    } if "postgresql" in settings.database_url else {},
)

# ── Session Factory ──────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ── Base Class ───────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependency ───────────────────────────────────────────────────────────────
def get_db():
    """FastAPI dependency: yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all tables defined in models.py. Called on app startup."""
    from models import Base as ModelBase  # noqa: F401 — triggers model registration
    ModelBase.metadata.create_all(bind=engine)
    logger.info("✅ Database tables verified/created")


def check_db_health() -> bool:
    """Returns True if database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"DB health check failed: {e}")
        return False
