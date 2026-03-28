from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os
from dotenv import load_dotenv

# ⚠️ CHANGE PASSWORD HERE
load_dotenv()  # load values from .env

DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_URL = f"postgresql://postgres:{DATABASE_PASSWORD}@localhost:5432/resume_ai_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

from backend.models.analysis_session import AnalysisSession

Base.metadata.create_all(bind=engine)
