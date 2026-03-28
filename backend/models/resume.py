from sqlalchemy import Column, Integer, String, DateTime, Text, LargeBinary
from datetime import datetime
from backend.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(Integer, nullable=False)
    file_id = Column(Integer, nullable=False)

    extracted_text = Column(Text, nullable=True)

    processing_status = Column(String, default="pending")

    real_name = Column(String, nullable=True)
    email = Column(String, nullable=True)

    file_data = Column(LargeBinary, nullable=True) 
    file_name = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)