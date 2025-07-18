import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 