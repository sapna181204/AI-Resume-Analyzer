from fastapi import APIRouter, Form, Depends
from backend.core.database import SessionLocal
from backend.models.user import User
from backend.models.company import Company
from backend.models.analysis_session import AnalysisSession
from backend.models.file_metadata import FileMetadata
from backend.models.resume import Resume
from backend.models.analysis_result import AnalysisResult
from backend.models.explainability import Explainability
from backend.models.fairness_metrics import FairnessMetrics
from backend.models.audit_log import AuditLog

from backend.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter()

# ============================================================
# 🟢 REGISTER
# ============================================================

@router.post("/register")
def register(
    hr_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    company_name: str = Form(""),
    department: str = Form("")
):

    if not hr_name.strip() or not email.strip() or not password.strip():
        return {"error": "Name, email and password are required"}

    if not company_name.strip():
        return {"error": "Company name is required"}

    db = SessionLocal()

    existing = db.query(User).filter(User.email == email.strip().lower()).first()

    if existing:
        db.close()
        return {"error": "User already exists"}

    company_clean = company_name.strip().lower()

    company = db.query(Company).filter(
        Company.name == company_clean
    ).first()

    if not company:
        company = Company(name=company_clean)
        db.add(company)
        db.commit()
        db.refresh(company)

    hashed = hash_password(password)

    existing_admin = db.query(User).filter(
        User.company_id == company.id,
        User.role == "admin"
    ).first()

    role = "admin" if not existing_admin else "recruiter"

    user = User(
        hr_name=hr_name.strip(),
        email=email.strip().lower(),
        password_hash=hashed,
        company_id=company.id,
        department=department.strip(),
        role=role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.close()

    return {
        "message": "User registered successfully",
        "assigned_role": role
    }


# ============================================================
# 🟢 LOGIN
# ============================================================

@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...)
):

    if not email.strip() or not password.strip():
        return {"error": "Email and password required"}

    db = SessionLocal()

    user = db.query(User).filter(
        User.email == email.strip().lower()
    ).first()

    if not user:
        db.close()
        return {"error": "User not found"}

    if not verify_password(password, user.password_hash):
        db.close()
        return {"error": "Incorrect password"}

    # CREATE JWT TOKEN
    token = create_access_token({"user_id": user.id})

    db.close()

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.hr_name,
            "email": user.email,
            "role": user.role
        }
    }


# ============================================================
# 🟢 DELETE USER (ADMIN ONLY)
# ============================================================

@router.post("/delete_user")
def delete_user(
    target_email: str = Form(...),
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    requester = current_user

    if requester.role != "admin":
        try:
            db.close()
            return {"error": "Only Admin HR can delete accounts"}
        finally:
            db.close()

    user = db.query(User).filter(
        User.email == target_email.strip().lower()
    ).first()

    if not user:
        db.close()
        return {"error": "User not found"}

    if user.company_id != requester.company_id:
        db.close()
        return {"error": "Cannot delete users from another company"}

    if user.id == requester.id:
        db.close()
        return {"error": "Admin cannot delete own account"}

    if user.role == "admin":
        admin_count = db.query(User).filter(
            User.company_id == user.company_id,
            User.role == "admin"
        ).count()

        if admin_count <= 1:
            db.close()
            return {"error": "Cannot delete the only admin of the company"}

    # ===== DELETE RELATED DATA =====

    db.query(AuditLog).filter(
        AuditLog.user_id == user.id
    ).delete()

    sessions = db.query(AnalysisSession).filter(
        AnalysisSession.user_id == user.id
    ).all()

    for session in sessions:
        
        resumes = db.query(Resume).filter(
            Resume.session_id == session.id
        ).all()
        
        for r in resumes:
            db.query(AnalysisResult).filter(
                AnalysisResult.resume_id == r.id
            ).delete()
            
            db.query(Explainability).filter(
                Explainability.resume_id == r.id
            ).delete()
            
            db.query(FairnessMetrics).filter(
                FairnessMetrics.resume_id == r.id
            ).delete()
            
            db.query(Resume).filter(
                Resume.session_id == session.id
            ).delete()
            
            db.query(FileMetadata).filter(
                FileMetadata.session_id == session.id
            ).delete()
            
            db.delete(session)

    db.delete(user)

    db.commit()
    db.close()

    return {"message": "User account deleted successfully"}


# ============================================================
# 🟢 CHANGE ROLE (ADMIN ONLY)
# ============================================================

@router.post("/change_role")
def change_role(
    target_email: str = Form(...),
    new_role: str = Form(...),
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    requester = current_user

    if requester.role != "admin":
        try:
            db.close()
            return {"error": "Only Admin can change roles"}
        finally:
            db.close()

    user = db.query(User).filter(
        User.email == target_email.strip().lower()
    ).first()

    if not user:
        db.close()
        return {"error": "User not found"}

    if user.company_id != requester.company_id:
        db.close()
        return {"error": "Cannot modify users from another company"}

    if new_role not in ["admin", "recruiter"]:
        db.close()
        return {"error": "Invalid role (use admin or recruiter)"}

    if user.id == requester.id:
        db.close()
        return {"error": "Admin cannot change own role"}

    user.role = new_role

    db.commit()
    db.close()

    return {"message": f"Role updated to {new_role}"}


# ============================================================
# 🟢 GET COMPANY USERS (ADMIN ONLY)
# ============================================================

@router.post("/get_company_users")
def get_company_users(
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    requester = current_user

    if requester.role != "admin":
        db.close()
        return {"error": "Only admin can view users"}

    users = db.query(User).filter(
        User.company_id == requester.company_id
    ).all()

    result = []

    for u in users:
        result.append({
            "id": u.id,
            "name": u.hr_name,
            "email": u.email,
            "department": u.department,
            "role": u.role
        })

    db.close()

    return {"users": result}