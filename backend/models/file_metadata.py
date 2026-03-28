from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.core.database import Base


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)
    session_id = Column(Integer, nullable=False)

    original_filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)

    file_size = Column(Integer, nullable=True)
    file_hash = Column(String, nullable=True)

    uploaded_at = Column(DateTime, default=datetime.utcnow)