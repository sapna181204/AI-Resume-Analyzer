from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from datetime import datetime
from backend.core.database import Base

class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))

    rating = Column(Float)
    feedback = Column(String)
    reviewer = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)