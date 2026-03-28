import os
import re
import io
import zipfile
import numpy as np

from sqlalchemy.orm import Session
from sqlalchemy import text

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Depends
from typing import Optional

from backend.core.database import Base, engine   # ✅ ADD THIS 

# ================= AI MODULES =================

from backend.parser.resume_parser import extract_text
from backend.anonymizer.anonymizer import anonymize
from backend.semantic.semantic_engine import semantic_match
from backend.skills.skill_engine import extract_skills
from backend.experience.experience_engine import extract_experience
from backend.ats.ats_engine import ats_score
from backend.model.hiring_model import hiring_probability
from backend.fairness.fairness_engine import (
    detect_bias,
    fairness_adjust_scores,
    generate_explanation,
    compute_confidence,
    create_audit_entry,
    generate_detailed_explanation
)
from backend.utils.text_normalizer import normalize_text, normalize_skill
from backend.utils.memory_store import ANALYSIS_NAME_MAP
from backend.fairness.dataset_fairness import dataset_fair_adjustment

# ================= DATABASE =================

from backend.core.database import SessionLocal
from backend.models.analysis_session import AnalysisSession
from backend.models.file_metadata import FileMetadata
from backend.models.resume import Resume
from backend.models.analysis_result import AnalysisResult
from backend.models.explainability import Explainability
from backend.models.fairness_metrics import FairnessMetrics
from backend.models.audit_log import AuditLog
from backend.models.user import User
from backend.models.company import Company
from backend.models.employee import Employee
from backend.models.performance import Performance
from backend.models.salary import SalaryHistory

# ================= AUTH ROUTES =================

from backend.auth.routes import router as auth_router
from backend.auth.security import get_current_user

from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from asyncio import gather 

from backend.routes.employee_routes import router as employee_router

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.include_router(auth_router)
app.include_router(employee_router)

# ================= CORS =================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)


def process_resume_pipeline(text, anon_text, jd_skills, job_description, filename, resume_id):

    semantic = semantic_match(anon_text, job_description)

    normalized_text = normalize_text(text)
    text_canonical = re.sub(r"[^a-z0-9]", "", normalized_text)

    skill_set = set(jd_skills)
    
    matched_skills = [s for s in skill_set if re.sub(r"[^a-z0-9]", "", s) in text_canonical]
    missing_skills = list(skill_set - set(matched_skills))

    skill_match = (
        len(matched_skills) / len(jd_skills) * 100
        if jd_skills else 0
    )

    experience = extract_experience(text) or 0
    ats = ats_score(text)

    probability = hiring_probability(
        semantic,
        skill_match,
        experience,
        ats
    )

    return {
        "resume_id": resume_id,
        "semantic": semantic,
        "skill_match": skill_match,
        "experience": experience,
        "ats": ats,
        "probability": probability,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "filename": filename
    }

# ============================================================
# 🚀 ANALYZE BATCH
# ============================================================

@app.post("/analyze_batch")
async def analyze_batch(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_description: str = Form(""),
    top_k: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    # ================= VALIDATE USER =================

    user = current_user 

    # ================= HANDLE FILE / ZIP =================

    MAX_SIZE = 10 * 1024 * 1024

    contents = await file.read()

    if len(contents) > MAX_SIZE:
        db.close()
        return {"error": "File too large (max 10MB)"}

    file.file.seek(0)

    all_files = []

    if file.filename.lower().endswith(".zip"):

        try:
            z = zipfile.ZipFile(io.BytesIO(contents))
        except zipfile.BadZipFile:
            db.close()
            return {"error": "Invalid ZIP file"}

        for name in z.namelist():

            if ".." in name or name.startswith("/"):
                continue

            if name.endswith("/") or name.startswith("__"):
                continue

            if name.lower().endswith((".pdf", ".docx")):

                file_bytes = z.read(name)

                fake_file = UploadFile(
                    filename=name,
                    file=io.BytesIO(file_bytes)
                )

                all_files.append(fake_file)

    else:
        all_files.append(file)

    if not all_files:
        db.close()
        return {"error": "No valid resumes found"}
    
    if len(all_files) > 200:
        db.close()
        return {"error": "Maximum 200 resumes allowed per batch"}

    # ================= JOB DESCRIPTION =================

    jd_skills = (
        [normalize_skill(s) for s in job_description.split(",") if s.strip()]
        if job_description else []
    )

    jd_empty = not job_description.strip()

    # ================= CREATE SESSION =================
    # get user's company
    
    company = db.query(Company).filter(
        Company.id == user.company_id
    ).first()
    
    if not company:
        db.close()
        return {"error": "Company not found"}
    
    # get last session number for THIS company
    last_session = db.query(AnalysisSession)\
        .filter(AnalysisSession.company_id == company.id)\
        .order_by(AnalysisSession.session_number.desc())\
        .first()
    
    next_session_number = 1 if not last_session else last_session.session_number + 1
    
    # create session
    session_record = AnalysisSession(
        user_id=user.id,
        company_id=company.id,
        session_number=next_session_number,
        job_description=job_description,
        status="processing",
        total_resumes=len(all_files),
        model_version="v1.0"
    )

    db.add(session_record)
    db.commit()
    db.refresh(session_record)

    # ================= PROCESS RESUMES =================
    
    results = []
    resume_ids = []
    resume_data = []
    
    # Step 1: Extract text and store resumes

    texts = await gather(*[extract_text(f) for f in all_files])
     
    for idx, f in enumerate(all_files):

        file_bytes = await f.read()
        file_size = len(file_bytes)
        if not file_bytes:
            f.file.seek(0)
            file_bytes = await f.read()
        
        file_record = FileMetadata(
        user_id=user.id,
        session_id=session_record.id,
        original_filename=f.filename,
        stored_path=f.filename,
        file_size=file_size
    )
        
        db.add(file_record)
        db.flush()
        db.refresh(file_record)
        
        text = texts[idx]
        anon_text = anonymize(text)

        real_name = f"Candidate_{idx}"
        
        lines = text.split("\n")

        for line in lines[:15]:
            line = line.strip()

            if not line:
                continue
            
            # skip unwanted lines
            if any(keyword in line.lower() for keyword in [
                "resume", "cv", "profile", "summary", "objective",
                "email", "phone", "contact", "developer", "engineer"
            ]):
                continue
            
            # skip emails / numbers
            if "@" in line or any(char.isdigit() for char in line):
                continue
            
            words = line.split()
            
            # stricter name condition
            if 2 <= len(words) <= 3 and all(w.isalpha() for w in words):
                real_name = " ".join(w.capitalize() for w in words)
                break

        # Extract email from resume
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        real_email = email_match.group(0) if email_match else None

        if real_name.startswith("Candidate_") and real_email:
            username = real_email.split("@")[0]

            # remove numbers
            username = re.sub(r"\d+", "", username)

            # replace separators
            username = username.replace(".", " ").replace("_", " ")

            username = username.strip()

            if username:
                real_name = username.title()
        
        resume_record = Resume(
            session_id=session_record.id,
            file_id=file_record.id,
            extracted_text=anon_text,
            processing_status="completed",
            file_data=file_bytes,
            file_name=f.filename,
            real_name=real_name,
            email=real_email
       )
        
        db.add(resume_record)
        db.flush()
        db.refresh(resume_record)
        
        resume_ids.append(resume_record.id)
        
        resume_data.append({
            "resume_id": resume_record.id,
            "text": text,
            "anon_text": anon_text,
            "filename": f.filename,
            "real_name": real_name,
            "email": real_email
        })
    
    # ================= PARALLEL AI PROCESSING =================

    max_workers = min(16, os.cpu_count() or 4)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:


        futures = [executor.submit(
            process_resume_pipeline,
            r["text"],
            r["anon_text"],
            jd_skills,
            job_description,
            r["filename"],
            resume_ids[idx]
        )
        for idx, r in enumerate(resume_data)
    ]
        
        for future in as_completed(futures):
            
            try:
                result = future.result()
            except Exception as e:
                print("AI processing error:", e)
                continue
            
            resume_id = result["resume_id"]

            semantic = result["semantic"]
            skill_match = result["skill_match"]
            experience = result["experience"]
            ats = result["ats"]
            probability = result["probability"]
            
            analysis_result = AnalysisResult(
                resume_id=resume_id,
                semantic_score=float(semantic),
                skill_match_score=float(skill_match),
                ats_score=float(ats),
                hiring_probability=float(probability)
            )
            
            db.add(analysis_result)
            
            results.append({
                "resume_id": resume_id,
                "filename": result["filename"],
                "semantic_match": round(semantic, 2),
                "skill_match": round(skill_match, 2),
                "experience_years": experience,
                "ats_score": round(ats, 2),
                "matched_skills": result["matched_skills"],
                "missing_skills": result["missing_skills"],
                "hiring_probability": max(0, min(100, round(probability, 2)))
            })

            # ✅ SAFE MATCHING
            for rdata in resume_data:
                if rdata["resume_id"] == resume_id:
                    ANALYSIS_NAME_MAP[resume_id] = {
                        "real_name": rdata["real_name"],
                        "email": rdata["email"]
                    }
                    break
            
            db.commit()


    # ================= FAIRNESS =================

    scores = [r["hiring_probability"] for r in results]

    bias_report = detect_bias(scores)

    adjusted_scores = fairness_adjust_scores(scores)
    adjusted_scores = dataset_fair_adjustment(adjusted_scores)

    for idx, (r, adj) in enumerate(zip(results, adjusted_scores)):

        r["fairness_adjusted_score"] = round(adj, 2)

        if adj >= 75:
            decision = "Recommended for Interview."
        elif adj >= 60:
            decision = "Shortlisted"
        elif adj >= 40:
            decision = "Hold"
        else:
            decision = "Rejected"
        
        r["decision"] = decision

        r["confidence"] = compute_confidence(r)
        r["explanation"] = generate_explanation(r)
        # r["detailed_explanation"] = generate_detailed_explanation(r)
        details = generate_detailed_explanation(r)
        if isinstance(details, dict):
            r["detailed_explanation"] = details
        else:
            r["detailed_explanation"] = {
                "strength": "-",
                "weakness": "-",
                "recommendation": details
        }

        resume_id = r["resume_id"]

        db.add(Explainability(
            resume_id=resume_id,
            explanation=r["explanation"],
            detailed_explanation=r["detailed_explanation"]
        ))

        db.add(FairnessMetrics(
            resume_id=resume_id,
            bias_detected=bias_report.get("bias_detected", False),
            adjustment_applied=True,
            adjustment_magnitude=float(adj)
        ))

    db.commit()

    # ================= RANKING =================

    if jd_empty:
        ranked = sorted(
            results,
            key=lambda x: (
                x["fairness_adjusted_score"],
                x["confidence"],
                x["skill_match"],
                x["semantic_match"],
                x["experience_years"]
            ),
            reverse=True
        )
    else:
        ranked = sorted(
            results,
            key=lambda x: (
                x["fairness_adjusted_score"],
                x["skill_match"],
                x["semantic_match"],
                x["ats_score"],
                x["experience_years"]
            ),
            reverse=True
        )

    audit_log = []
    
    for r in ranked:
        entry = f"Candidate: {r['filename']} — Score: {r['fairness_adjusted_score']} — Decision: {r['decision']}"
        audit_log.append(entry)

    db.commit()

    # ================= COMPLETE SESSION =================

    from datetime import datetime

    session_record.status = "completed"
    session_record.completed_at = datetime.utcnow()

    db.commit()

    # ⭐ FIX: SAVE SESSION ID BEFORE CLOSING DB
    session_id = session_record.id

    db.close()

    # ================= RESPONSE =================

    top_candidates = ranked[:top_k] if top_k else ranked

    return {
        "session_id": session_id,
        "mode": "experience_ranking" if jd_empty else "ai_ranking",
        "total_resumes_processed": len(ranked),
        "bias_report": bias_report,
        "top_candidates": top_candidates,
        "all_candidates_ranked": ranked,
        "audit_log": audit_log
    }


# ============================================================
# 🧹 CLEAR ANALYSIS DATA (SAFE — KEEP HR ACCOUNTS)
# ============================================================

@app.post("/clear_analysis_data")
def clear_analysis_gdata(
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    if current_user.role != "admin":
        return {"error": "Admin only"}

    try:

        company_id = current_user.company_id

        # Get sessions belonging to this company
        sessions = db.query(AnalysisSession).filter(
            AnalysisSession.company_id == company_id
        ).all()

        session_ids = [s.id for s in sessions]

        # Get resumes for these sessions
        resumes = db.query(Resume).filter(
            Resume.session_id.in_(session_ids)
        ).all()

        resume_ids = [r.id for r in resumes]

        # ================= CORRECT DELETE ORDER =================
        
        # 1. EMPLOYEE CHILD TABLES FIRST
        employees = db.query(Employee).filter(
            Employee.company_id == company_id
        ).all()

        employee_ids = [e.id for e in employees]

        db.query(Performance).filter(
            Performance.employee_id.in_(employee_ids)
        ).delete(synchronize_session=False)

        db.query(SalaryHistory).filter(
            SalaryHistory.employee_id.in_(employee_ids)
        ).delete(synchronize_session=False)


        # 2. ANALYSIS CHILD TABLES
        sessions = db.query(AnalysisSession).filter(
            AnalysisSession.company_id == company_id
        ).all()

        session_ids = [s.id for s in sessions]

        resumes = db.query(Resume).filter(
            Resume.session_id.in_(session_ids)
        ).all()

        resume_ids = [r.id for r in resumes]

        db.query(FairnessMetrics).filter(
            FairnessMetrics.resume_id.in_(resume_ids)
        ).delete(synchronize_session=False)

        db.query(Explainability).filter(
            Explainability.resume_id.in_(resume_ids)
        ).delete(synchronize_session=False)

        db.query(AnalysisResult).filter(
            AnalysisResult.resume_id.in_(resume_ids)
        ).delete(synchronize_session=False)

        # 🔥 BREAK FK LINK FIRST
        db.query(Employee).filter(
            Employee.resume_id.in_(resume_ids)
        ).update(
            {Employee.resume_id: None},
            synchronize_session=False
        )

        # 3. RESUME LEVEL
        db.query(Resume).filter(
            Resume.id.in_(resume_ids)
        ).delete(synchronize_session=False)

        db.query(FileMetadata).filter(
            FileMetadata.session_id.in_(session_ids)
        ).delete(synchronize_session=False)

        # 4. SESSION LEVEL
        db.query(AnalysisSession).filter(
            AnalysisSession.company_id == company_id
        ).delete(synchronize_session=False)

        # 5. EMPLOYEE LAST
        db.query(Employee).filter(
            Employee.company_id == company_id
        ).delete(synchronize_session=False)

        # 6. AUDIT LOG LAST
        db.query(AuditLog).filter(
            AuditLog.user_id.in_(
                db.query(User.id).filter(User.company_id == company_id)
            )
        ).delete(synchronize_session=False)

        try:
            db.query(SalaryHistory).filter(
                SalaryHistory.employee_id.in_(employee_ids)
            ).delete(synchronize_session=False)
        except Exception:
            pass

        db.query(Employee).filter(
            Employee.company_id == company_id
        ).delete(synchronize_session=False)

        db.commit()

        return {
            "message": "Analysis data cleared for this company only"
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()


# ============================================================
# ☠️ DELETE COMPANY DATA (DANGEROUS — EVERYTHING)
# ============================================================

@app.post("/delete_company_data")
def delete_company_data(
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    if current_user.role != "admin":
        return {"error": "Admin only"}

    try:

        company_id = current_user.company_id

        sessions = db.query(AnalysisSession).filter(
            AnalysisSession.company_id == company_id
        ).all()

        session_ids = [s.id for s in sessions]

        resumes = db.query(Resume).filter(
            Resume.session_id.in_(session_ids)
        ).all()

        resume_ids = [r.id for r in resumes]

        # ================= SAFE DELETE =================
         
        # 1. EMPLOYEES FIRST (children first)
        employees = db.query(Employee).filter(
            Employee.company_id == company_id
        ).all()

        employee_ids = [e.id for e in employees]

        db.query(Performance).filter(
            Performance.employee_id.in_(employee_ids)
        ).delete(synchronize_session=False)

        db.query(SalaryHistory).filter(
            SalaryHistory.employee_id.in_(employee_ids)
        ).delete(synchronize_session=False)

        db.query(Employee).filter(
            Employee.company_id == company_id
        ).delete(synchronize_session=False)

        # 2. ANALYSIS DATA
        sessions = db.query(AnalysisSession).filter(
            AnalysisSession.company_id == company_id
        ).all()

        session_ids = [s.id for s in sessions]

        resumes = db.query(Resume).filter(
            Resume.session_id.in_(session_ids)
        ).all()

        resume_ids = [r.id for r in resumes]

        db.query(FairnessMetrics).filter(
            FairnessMetrics.resume_id.in_(resume_ids)
        ).delete(synchronize_session=False)

        db.query(Explainability).filter(
            Explainability.resume_id.in_(resume_ids)
        ).delete(synchronize_session=False)

        db.query(AnalysisResult).filter(
            AnalysisResult.resume_id.in_(resume_ids)
        ).delete(synchronize_session=False)
        
        # 🔥 BREAK FK LINK FIRST
        db.query(Employee).filter(
            Employee.resume_id.in_(resume_ids)
        ).update(
            {Employee.resume_id: None},
            synchronize_session=False
        )

        db.query(Resume).filter(
            Resume.id.in_(resume_ids)
        ).delete(synchronize_session=False)

        db.query(FileMetadata).filter(
            FileMetadata.session_id.in_(session_ids)
        ).delete(synchronize_session=False)

        db.query(AnalysisSession).filter(
            AnalysisSession.company_id == company_id
        ).delete(synchronize_session=False)

        # 3. USERS LAST
        db.query(User).filter(
            User.company_id == company_id
        ).delete(synchronize_session=False)

        db.commit()

        return {"message": "Company data deleted safely"}

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()


# ============================================================
#  GET ANALYSIS DATA
# ============================================================



@app.post("/get_analysis_data")
def get_analysis_data(
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    user = current_user

    sessions = db.query(AnalysisSession)\
        .filter(AnalysisSession.company_id == user.company_id)\
        .order_by(AnalysisSession.id.desc())\
        .all()

    result = []

    for s in sessions:
        result.append({
            # "session_number": len(result) + 1,
            "session_number": s.session_number,
            "session_id": s.id,
            "user_id": s.user_id,
            "total_resumes": s.total_resumes,
            "status": s.status
        })

    db.close()

    return {"sessions": result}

@app.post("/get_history")
def get_history(
    current_user: User =  Depends(get_current_user)
):

    db = SessionLocal()

    user = current_user
    
    company = db.query(Company).filter(Company.id == user.company_id).first()

    sessions = db.query(AnalysisSession)\
        .filter(AnalysisSession.company_id == user.company_id)\
        .order_by(AnalysisSession.session_number.desc())\
        .all()

    result = []

    for s in sessions:

        hr_user = db.query(User).filter(User.id == s.user_id).first()

        result.append({
            "session_number": s.session_number,
            "session_id": s.id,
            "hr_name": hr_user.hr_name if hr_user else "Unknown",
            "company_name": company.name if company else "Unknown",
            "job_description": s.job_description,
            "total_resumes": s.total_resumes,
            "status": s.status,
            "completed_at":
                str(s.completed_at) if s.completed_at else "N/A"
        })

    db.close()

    return {"history": result}

@app.post("/get_session_details")
def get_session_details(
    session_id: int = Form(...), 
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    user = current_user

    session = db.query(AnalysisSession)\
                .filter(AnalysisSession.id == session_id)\
                .first()

    if not session:
        db.close()
        return {"error": "Session not found"}
    
    # ==================== AUTHORIZATION CHECK (Company Security Check) =================

    if session.company_id != user.company_id:
        db.close()
        return {"error": "Unauthorized access."}

    # ================= FILES =================

    files = db.query(FileMetadata)\
              .filter(FileMetadata.session_id == session_id)\
              .all()

    # ================= RESUMES =================

    resumes = db.query(Resume)\
                .filter(Resume.session_id == session_id)\
                .all()

    # ================= ANALYSIS RESULTS =================

    results = []

    for r in resumes:

        analysis = db.query(AnalysisResult)\
                     .filter(AnalysisResult.resume_id == r.id)\
                     .first()

        if analysis:

            file = db.query(FileMetadata)\
                     .filter(FileMetadata.id == r.file_id)\
                     .first()

            results.append({
                "filename": file.original_filename if file else "Unknown",
                "score": analysis.hiring_probability
            })

    # Sort highest score first
    results_sorted = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    top_candidates = results_sorted[:3]

    db.close()

    return {
        "session_id": session.id,
        "session_number": session.session_number,
        "job_description": session.job_description,
        "total_resumes": session.total_resumes,
        "status": session.status,
        "completed_at": str(session.completed_at),
        "files": [f.original_filename for f in files],
        "top_candidates": top_candidates
    }








# Run with: 
# python -m uvicorn backend.main:app --reload 
# OUTPUT 
# http://127.0.0.1:8000/docs