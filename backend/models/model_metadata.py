from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.core.database import Base


class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    id = Column(Integer, primary_key=True, index=True)

    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False)

    embedding_model = Column(String, nullable=True)
    scoring_model = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)