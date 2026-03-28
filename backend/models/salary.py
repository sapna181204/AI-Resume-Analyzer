from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from datetime import datetime
from backend.core.database import Base

class SalaryHistory(Base):
    __tablename__ = "salary_history"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))

    salary = Column(Float)
    bonus = Column(Float, default=0)

    effective_date = Column(DateTime, default=datetime.utcnow)