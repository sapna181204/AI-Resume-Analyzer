from backend.core.database import engine, Base

Base.metadata.create_all(bind=engine)


# Existing model
from backend.models.user import User

# ⭐ Model version tracking
from backend.models.model_metadata import ModelMetadata

# ⭐ Batch analysis sessions
from backend.models.analysis_session import AnalysisSession

# ⭐ File upload metadata
from backend.models.file_metadata import FileMetadata

# ⭐ Individual resumes
from backend.models.resume import Resume

# ⭐ AI scoring results
from backend.models.analysis_result import AnalysisResult

# ⭐ Explainability outputs
from backend.models.explainability import Explainability

# ⭐ Fairness tracking
from backend.models.fairness_metrics import FairnessMetrics

# ⭐ Processing performance metrics
from backend.models.processing_metrics import ProcessingMetrics

# ⭐ Audit logs
from backend.models.audit_log import AuditLog

# ⭐ Company model
from backend.models.company import Company

# ⭐ Employee details
from backend.models.employee import Employee

# ⭐ Performance details of Employees
from backend.models.performance import Performance

# ⭐ Salary History 
from backend.models.salary import SalaryHistory

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ All tables created successfully!")