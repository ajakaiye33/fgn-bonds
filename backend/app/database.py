"""SQLite database configuration with SQLAlchemy."""

from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import get_settings

settings = get_settings()

# Create engine with SQLite-specific settings
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Required for SQLite with FastAPI
    echo=settings.debug,  # Log SQL queries in debug mode
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Apply recommended PRAGMA settings on every SQLite connection."""
    cursor = dbapi_connection.cursor()
    # WAL mode for better concurrency (readers don't block writers)
    cursor.execute("PRAGMA journal_mode=WAL")
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys=ON")
    # Safe with WAL, faster than FULL
    cursor.execute("PRAGMA synchronous=NORMAL")
    # 64MB page cache
    cursor.execute("PRAGMA cache_size=-64000")
    # Store temp tables in memory
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()


# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields a session that is closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
