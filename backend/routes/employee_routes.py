import os
import re
from fastapi import APIRouter, Depends, Form, UploadFile, File
from backend.core.database import SessionLocal

from docx import Document
from reportlab.pdfgen import canvas
from io import BytesIO

from backend.models.employee import Employee
from backend.models.performance import Performance
from backend.models.salary import SalaryHistory

from backend.auth.security import get_current_user

from fastapi.responses import FileResponse

from fastapi.responses import Response

from backend.models.resume import Resume

from backend.main import ANALYSIS_NAME_MAP

router = APIRouter()

def convert_docx_to_pdf(docx_bytes):

    doc = Document(BytesIO(docx_bytes))
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer)

    y = 800

    for para in doc.paragraphs:
        text = para.text.strip()

        if not text:
            continue

        c.drawString(40, y, text[:100])

        y -= 20

        if y < 40:
            c.showPage()
            y = 800

    c.save()
    buffer.seek(0)

    return buffer.read()

# =========================================================
# ✅ ADD EMPLOYEE
# =========================================================
@router.post("/add_employee")
async def add_employee(
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    department: str = Form(...),
    salary: float = Form(...),
    resume: UploadFile = File(None),
    current_user = Depends(get_current_user)
):
    db = SessionLocal()

    try:

        resume_id = None

        # HANDLE RESUME FILE
        if resume:
            file_bytes = await resume.read()

            resume_record = Resume(
                session_id=0,
                file_id=0,
                extracted_text=None,
                processing_status="manual_upload",
                file_data=file_bytes,
                file_name=resume.filename,
                real_name=name,
                email=email
            )

            db.add(resume_record)
            db.flush()
            db.refresh(resume_record)

            resume_id = resume_record.id

        emp = Employee(
            company_id=current_user.company_id,
            name=name,
            email=email,
            role=role,
            department=department,
            salary=salary,
            resume_id=resume_id
        )
        
        db.add(emp)
        db.commit()

        db.close()
        
        return {"message": "Employee added successfully"}
    
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    
    finally:
        db.close()

# =========================================================
# ✅ HIRE CANDIDATE (FROM ANALYSIS)
# =========================================================
@router.post("/hire_candidate")
def hire_candidate(
    resume_id: int = Form(...),
    role: str = Form(...),
    department: str = Form(...),
    salary: float = Form(...),
    current_user = Depends(get_current_user)
):
    db = SessionLocal()

    try:

        resume = db.query(Resume).filter(Resume.id == resume_id).first()

        if not resume:
            return {"error": "Resume not found"}

        real_name = resume.real_name or f"Candidate_{resume_id}"
        email = resume.email or real_name.replace(" ", "").lower() + "@company.com"

        # ✅ Use real email if available
        email = resume.email if resume.email else (
            (resume.real_name or f"candidate{resume_id}")
            .replace(" ", "")
            .lower() + "@company.com"
        )

        emp = Employee(
            company_id=current_user.company_id,
            name=real_name,
            email=email,
            role=role,
            department=department,
            salary=salary,
            resume_id=resume_id
        )

        db.add(emp)
        db.commit()

        return {"message": "✅ Candidate hired successfully"}

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()


# =========================================================
# ✅ GET EMPLOYEES
# =========================================================
@router.post("/get_employees")
def get_employees(current_user = Depends(get_current_user)):

    db = SessionLocal()

    employees = db.query(Employee)\
        .filter(Employee.company_id == current_user.company_id)\
        .order_by(Employee.id.desc())\
        .all()

    result = []
    for idx, e in enumerate(employees):
        result.append({
            "serial": len(employees) - idx,
            "id": e.id,
            "name": e.name,
            "role": e.role,
            "salary": e.salary,
            "department": e.department
        })

    db.close()

    return {"employees": result}


# =========================================================
# ✅ ADD PERFORMANCE
# =========================================================
@router.post("/add_performance")
def add_performance(
    employee_id: int = Form(...),
    rating: float = Form(...),
    feedback: str = Form(...),
    current_user = Depends(get_current_user)
):
    db = SessionLocal()

    if rating < 1 or rating > 5:
        return {"error": "Rating must be between 1 and 5"}
    
    # ✅ FEEDBACK VALIDATION
    feedback = feedback.strip()

    # ✅ RATING VALIDATION
    if not feedback:
        return {"error": "Feedback is required"}

    # ❌ Only numbers not allowed
    if feedback.isdigit():
        return {"error": "Feedback cannot be only numbers"}

    # ❌ Too short feedback
    if len(feedback) < 5:
        return {"error": "Feedback too short (min 5 characters)"}

    # ❌ No alphabets (like ### or 123)
    if not re.search(r"[a-zA-Z]", feedback):
        return {"error": "Feedback must contain meaningful text"}
    
    # ❌ Too long
    if len(feedback) > 300:
        return {"error": "Feedback too long (max 300 characters allowed)"}

    p = Performance(
        employee_id=employee_id,
        rating=rating,
        feedback=feedback,
        reviewer=str(current_user.id)
    )

    db.add(p)

    emp = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.company_id == current_user.company_id
    ).first()
    
    if not emp:
        db.close()
        return {"error": "Unauthorized"}

    db.commit()

    db.close()

    return {"message": "Performance added"}


# =========================================================
# ✅ UPDATE SALARY
# =========================================================
@router.post("/update_salary")
def update_salary(
    employee_id: int = Form(...),
    salary: float = Form(...),
    bonus: float = Form(0),
    current_user = Depends(get_current_user)
):
    db = SessionLocal()

    # Save history
    s = SalaryHistory(
        employee_id=employee_id,
        salary=salary,
        bonus=bonus
    )
    db.add(s)

    # Update main employee salary
    emp = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.company_id == current_user.company_id
        ).first()
    
    if not emp:
        db.close()
        return {"error": "Unauthorized"}

    if emp:
        emp.salary = salary

    db.commit()
    db.close()

    return {"message": "Salary updated"}

@router.post("/employee_details")
def employee_details(
    employee_id: int = Form(...),
    current_user = Depends(get_current_user)
):
    db = SessionLocal()

    emp = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.company_id == current_user.company_id
    ).first()

    if not emp:
        db.close()
        return {"error": "Unauthorized"}

    perf = db.query(Performance).filter(
        Performance.employee_id == employee_id
    ).all()

    salary = db.query(SalaryHistory).filter(
        SalaryHistory.employee_id == employee_id
    ).all()

    db.close()

    return {
        "name": emp.name,
        "email": emp.email,
        "role": emp.role,
        "department": emp.department,
        "salary": emp.salary,
        "performance": [
            {"rating": p.rating, "feedback": p.feedback}
            for p in perf
        ],
        "salary_history": [
            {"salary": s.salary, "bonus": s.bonus}
            for s in salary
        ],
        "resume_url": f"/download_resume/{employee_id}"
    }

@router.get("/download_resume/{employee_id}")
def download_resume(employee_id: int, current_user = Depends(get_current_user)):

    db = SessionLocal()

    emp = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.company_id == current_user.company_id
    ).first()

    if not emp or not emp.resume_id:
        db.close()
        return {"error": "Resume not found"}

    resume = db.query(Resume).filter(
        Resume.id == emp.resume_id
    ).first()

    if not resume or not resume.file_data:
        db.close()
        return {"error": "File missing"}

    file_name = f"{emp.name.replace(' ', '_')}.pdf"

    # detect file type
    if file_name.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        media_type = "application/pdf"

    db.close()

    return Response(
        content=resume.file_data,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={file_name}"
        }
    )

@router.get("/preview_resume/{employee_id}")
def preview_resume(employee_id: int):

    db = SessionLocal()

    emp = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.id == employee_id
    ).first()

    if not emp or not emp.resume_id:
        db.close()
        return {"error": "Resume not found"}

    resume = db.query(Resume).filter(
        Resume.id == emp.resume_id
    ).first()

    if not resume or not resume.file_data:
        db.close()
        return {"error": "File missing"}

    file_name = resume.file_name or "resume.pdf"

    # ✅ CASE 1: PDF → DIRECT PREVIEW
    if file_name.lower().endswith(".pdf"):

        db.close()

        return Response(
            content=resume.file_data,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline"}
        )

    # ✅ CASE 2: DOCX → CONVERT TO PDF
    elif file_name.lower().endswith(".docx"):

        pdf_bytes = convert_docx_to_pdf(resume.file_data)

        db.close()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline"}
        )

    db.close()
    return {"error": "Unsupported format"}