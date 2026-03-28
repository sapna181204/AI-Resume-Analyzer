from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    action = Column(String, nullable=False)
    target_resource = Column(String, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)