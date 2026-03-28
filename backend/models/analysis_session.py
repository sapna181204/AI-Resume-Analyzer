from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from backend.core.database import Base


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # Link to users table
    user_id = Column(Integer, nullable=True)

    company_id = Column(Integer)

    # Company session number
    session_number = Column(Integer, default=1)

    # Analysis input
    job_description = Column(Text, nullable=False)

    # Session status
    status = Column(String, default="pending")

    total_resumes = Column(Integer, default=0)
    processing_time = Column(Integer, nullable=True)

    model_version = Column(String, nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)