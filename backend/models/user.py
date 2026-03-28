from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # ===== HR DETAILS =====
    hr_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)

    company_id = Column(Integer)

    # company_name = Column(String, nullable=True)
    department = Column(String, nullable=True)
    

    # Optional system fields
    role = Column(String, default="recruiter")

    password_hash = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)