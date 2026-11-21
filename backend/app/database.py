import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

# Engine configuration with high-concurrency connection pooling & SQLite optimizations
connect_args = {}
engine_kwargs = {"echo": False}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    connect_args["timeout"] = 30.0  # Prevent immediate timeouts under concurrency
else:
    # High-concurrency PostgreSQL connection pooling
    engine_kwargs.update({
        "pool_size": 50,
        "max_overflow": 100,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True
    })

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

# Apply SQLite high-performance WAL (Write-Ahead Logging) and memory pragma settings
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")  # 64MB RAM page cache
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB Memory-mapped I/O
            cursor.close()
        except Exception:
            cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
