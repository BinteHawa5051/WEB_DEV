from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Case, User, CaseStatusHistory
from schemas import CaseCreate, CaseResponse, CaseStatusEnum
from routers.auth import get_current_user
import uuid

router = APIRouter()

def generate_case_number(court_id: int, case_type: str) -> str:
    """Generate unique case number"""
    year = datetime.now().year
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"{court_id}/{case_type}/{year}/{unique_id}"

@router.post("/", response_model=CaseResponse)
async def create_case(
    case: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Generate unique case number
    case_number = generate_case_number(case.court_id, case.case_type)
    
    db_case = Case(
        case_number=case_number,
        title=case.title,
        court_id=case.court_id,
        jurisdiction=case.jurisdiction,
        case_type=case.case_type,
        urgency_level=case.urgency_level,
        complexity_score=case.complexity_score,
        public_interest_score=case.public_interest_score,
        estimated_duration_hours=case.estimated_duration_hours,
        description=case.description,
        connected_cases=case.connected_cases or []
    )
    
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    
    # Create status history entry
    status_history = CaseStatusHistory(
        case_id=db_case.id,
        old_status=None,
        new_status=CaseStatusEnum.FILED,
        changed_by=current_user.id,
        notes="Case filed"
    )
    db.add(status_history)
    db.commit()
    
    return db_case

@router.get("/", response_model=List[CaseResponse])
async def get_cases(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CaseStatusEnum] = None,
    jurisdiction: Optional[str] = None,
    urgency: Optional[str] = None,
    court_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Case)
    
    # Apply filters
    if status:
        query = query.filter(Case.status == status)
    if jurisdiction:
        query = query.filter(Case.jurisdiction == jurisdiction)
    if urgency:
        query = query.filter(Case.urgency_level == urgency)
    if court_id:
        query = query.filter(Case.court_id == court_id)
    
    # For non-admin users, filter by their court
    if current_user.role not in ["chief_justice", "court_administrator"]:
        query = query.filter(Case.court_id == current_user.court_id)
    
    cases = query.offset(skip).limit(limit).all()
    return cases

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check access permissions
    if (current_user.role not in ["chief_justice", "court_administrator"] and 
        case.court_id != current_user.court_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return case

@router.put("/{case_id}/status")
async def update_case_status(
    case_id: int,
    new_status: CaseStatusEnum,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check permissions
    if current_user.role not in ["chief_justice", "presiding_judge", "court_administrator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    old_status = case.status
    case.status = new_status
    
    # Create status history entry
    status_history = CaseStatusHistory(
        case_id=case_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=current_user.id,
        notes=notes
    )
    
    db.add(status_history)
    db.commit()
    
    return {"message": "Case status updated successfully"}

@router.get("/{case_id}/history")
async def get_case_history(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    history = db.query(CaseStatusHistory).filter(
        CaseStatusHistory.case_id == case_id
    ).order_by(CaseStatusHistory.change_date.desc()).all()
    
    return history

@router.get("/search/{case_number}")
async def search_case_by_number(
    case_number: str,
    db: Session = Depends(get_db)
):
    """Public endpoint for case number search"""
    case = db.query(Case).filter(Case.case_number == case_number).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Return limited public information
    return {
        "case_number": case.case_number,
        "title": case.title,
        "status": case.status,
        "filing_date": case.filing_date,
        "jurisdiction": case.jurisdiction,
        "urgency_level": case.urgency_level
    }

@router.put("/{case_id}/assign-judge")
async def assign_judge_to_case(
    case_id: int,
    judge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["chief_justice", "court_administrator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.assigned_judge_id = judge_id
    db.commit()
    
    return {"message": "Judge assigned successfully"}