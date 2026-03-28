from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from backend.core.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String)
    email = Column(String)
    role = Column(String)
    department = Column(String)
    
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)

    salary = Column(Float)
    joining_date = Column(DateTime, default=datetime.utcnow)

    status = Column(String, default="active")  # active / resigned