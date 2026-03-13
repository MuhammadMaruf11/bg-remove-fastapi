import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Render/Heroku compatibility (postgres:// -> postgresql://)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite fallback for local testing (optional)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./test.db"

# Engine create kora
engine = create_engine(DATABASE_URL)

# Session create kora
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class create kora model-er jonno
Base = declarative_base()

# Dependency (Node Middleware er moto)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()