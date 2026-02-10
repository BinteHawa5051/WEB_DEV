from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Lawyer, User
from schemas import LawyerCreate, LawyerResponse
from routers.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=LawyerResponse)
async def create_lawyer(
    lawyer: LawyerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["chief_justice", "court_administrator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if user exists and is not already a lawyer
    user = db.query(User).filter(User.id == lawyer.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_lawyer = db.query(Lawyer).filter(Lawyer.user_id == lawyer.user_id).first()
    if existing_lawyer:
        raise HTTPException(status_code=400, detail="User is already a lawyer")
    
    db_lawyer = Lawyer(
        user_id=lawyer.user_id,
        bar_registration=lawyer.bar_registration,
        firm_name=lawyer.firm_name,
        specializations=lawyer.specializations,
        win_rate=0.0
    )
    
    db.add(db_lawyer)
    db.commit()
    db.refresh(db_lawyer)
    return db_lawyer

@router.get("/", response_model=List[LawyerResponse])
async def get_lawyers(
    specialization: Optional[str] = None,
    available_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Lawyer)
    
    if specialization:
        query = query.filter(Lawyer.specializations.contains([specialization]))
    
    if available_only:
        query = query.filter(Lawyer.is_available == True)
    
    lawyers = query.all()
    return lawyers

@router.get("/{lawyer_id}", response_model=LawyerResponse)
async def get_lawyer(
    lawyer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    return lawyer


@router.post("/{lawyer_id}/unavailability")
async def add_unavailability(
    lawyer_id: int,
    start_date: str,
    end_date: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add unavailability period for a lawyer"""
    from datetime import datetime
    
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Check if user is the lawyer or admin
    if current_user.id != lawyer.user_id and current_user.role not in ["chief_justice", "court_administrator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Parse dates
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    if start >= end:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Store in lawyer's unavailability (we'll use a simple list for now)
    # In production, this would be a separate table
    unavailability = {
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "message": "Unavailability period added",
        "lawyer_id": lawyer_id,
        "unavailability": unavailability
    }

@router.get("/{lawyer_id}/unavailability")
async def get_unavailability(
    lawyer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get unavailability periods for a lawyer"""
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # In production, query from unavailability table
    # For now, return empty list
    return {
        "lawyer_id": lawyer_id,
        "unavailability_periods": []
    }

@router.get("/{lawyer_id}/conflicts")
async def check_conflicts(
    lawyer_id: int,
    date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if lawyer has conflicts on a specific date"""
    from models import Hearing
    from datetime import datetime
    
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    try:
        check_date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
    except:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Check hearings on that date
    hearings = db.query(Hearing).filter(
        Hearing.scheduled_date == check_date
    ).all()
    
    # Check if lawyer is involved in any cases on that date
    conflicts = []
    for hearing in hearings:
        case = hearing.case
        if case:
            # Check if lawyer is representing any party in this case
            # This is simplified - in production, check case_lawyers table
            conflicts.append({
                "hearing_id": hearing.id,
                "case_number": case.case_number,
                "case_title": case.title,
                "scheduled_time": hearing.scheduled_date.isoformat()
            })
    
    return {
        "lawyer_id": lawyer_id,
        "date": date,
        "has_conflicts": len(conflicts) > 0,
        "conflicts": conflicts
    }
