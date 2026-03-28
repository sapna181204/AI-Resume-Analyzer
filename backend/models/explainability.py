from sqlalchemy import Column, Integer, JSON
from backend.core.database import Base


class Explainability(Base):
    __tablename__ = "explainability"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(Integer, nullable=False)

    explanation = Column(JSON, nullable=True)
    detailed_explanation = Column(JSON, nullable=True)