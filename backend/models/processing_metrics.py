from sqlalchemy import Column, Integer, Float
from backend.core.database import Base


class ProcessingMetrics(Base):
    __tablename__ = "processing_metrics"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(Integer, nullable=False)

    total_time_seconds = Column(Float, nullable=True)
    failed_resumes = Column(Integer, default=0)
    skipped_resumes = Column(Integer, default=0)