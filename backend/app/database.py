from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Migration: Add meaning column to words table if it doesn't exist
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(words)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'meaning' not in columns:
                conn.execute(text("ALTER TABLE words ADD COLUMN meaning VARCHAR(500)"))
                conn.commit()
                print("Migration: Added 'meaning' column to words table")
    except Exception as e:
        print(f"Migration check: {e}")
