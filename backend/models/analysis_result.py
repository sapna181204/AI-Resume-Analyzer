from sqlalchemy import Column, Integer, Float
from backend.core.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(Integer, nullable=False)

    semantic_score = Column(Float, nullable=True)
    skill_match_score = Column(Float, nullable=True)
    ats_score = Column(Float, nullable=True)

    hiring_probability = Column(Float, nullable=True)
    fairness_adjusted_score = Column(Float, nullable=True)

    confidence_score = Column(Float, nullable=True)
    ranking_position = Column(Integer, nullable=True)