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
