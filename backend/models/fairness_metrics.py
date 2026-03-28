from sqlalchemy import Column, Integer, Float, Boolean
from backend.core.database import Base


class FairnessMetrics(Base):
    __tablename__ = "fairness_metrics"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(Integer, nullable=False)

    bias_detected = Column(Boolean, default=False)
    adjustment_applied = Column(Boolean, default=False)

    adjustment_magnitude = Column(Float, nullable=True)