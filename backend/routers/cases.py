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


@router.post("/calculate-complexity")
async def calculate_case_complexity(
    num_parties: int,
    num_witnesses: int,
    evidence_pages: int,
    case_type: str,
    current_user: User = Depends(get_current_user)
):
    """
    Auto-calculate case complexity score based on case parameters
    Returns a score from 1-10
    """
    # Base complexity score
    complexity = 0.0
    
    # Factor 1: Number of parties (more parties = more complex)
    if num_parties <= 2:
        complexity += 1
    elif num_parties <= 4:
        complexity += 2
    elif num_parties <= 6:
        complexity += 3
    else:
        complexity += 4
    
    # Factor 2: Number of witnesses
    if num_witnesses == 0:
        complexity += 0.5
    elif num_witnesses <= 3:
        complexity += 1
    elif num_witnesses <= 6:
        complexity += 1.5
    elif num_witnesses <= 10:
        complexity += 2
    else:
        complexity += 2.5
    
    # Factor 3: Evidence volume
    if evidence_pages < 50:
        complexity += 0.5
    elif evidence_pages < 100:
        complexity += 1
    elif evidence_pages < 300:
        complexity += 1.5
    elif evidence_pages < 500:
        complexity += 2
    else:
        complexity += 2.5
    
    # Factor 4: Case type complexity
    case_type_weights = {
        'civil': 1.0,
        'criminal': 1.5,
        'family': 1.0,
        'tax': 2.0,
        'constitutional': 2.5
    }
    complexity += case_type_weights.get(case_type.lower(), 1.0)
    
    # Normalize to 1-10 scale
    complexity_score = min(10, max(1, round(complexity)))
    
    return {
        "complexity_score": complexity_score,
        "factors": {
            "num_parties": num_parties,
            "num_witnesses": num_witnesses,
            "evidence_pages": evidence_pages,
            "case_type": case_type
        },
        "recommendation": (
            "Simple case" if complexity_score <= 3 else
            "Moderate complexity" if complexity_score <= 6 else
            "Complex case" if complexity_score <= 8 else
            "Highly complex case"
        )
    }


@router.get("/{case_id}/delays")
async def get_case_delays(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get delay analysis for a case"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Calculate delays
    filing_date = case.filing_date
    current_date = datetime.now()
    days_pending = (current_date - filing_date).days
    
    # Get status history to track delays
    history = db.query(CaseStatusHistory).filter(
        CaseStatusHistory.case_id == case_id
    ).order_by(CaseStatusHistory.change_date).all()
    
    delays = []
    expected_days = {
        "filed": 7,  # Should move to admitted in 7 days
        "admitted": 30,  # Should be listed in 30 days
        "listed": 14,  # Should start hearing in 14 days
        "hearing": 60,  # Should complete in 60 days
        "reserved": 30  # Judgment in 30 days
    }
    
    for i, event in enumerate(history):
        if i < len(history) - 1:
            next_event = history[i + 1]
            days_in_status = (next_event.change_date - event.change_date).days
            expected = expected_days.get(event.new_status, 30)
            
            if days_in_status > expected:
                delays.append({
                    "status": event.new_status,
                    "expected_days": expected,
                    "actual_days": days_in_status,
                    "delay_days": days_in_status - expected,
                    "reason": event.notes or "No reason provided"
                })
    
    # Calculate total delay
    total_expected = sum(expected_days.values())
    total_delay = max(0, days_pending - total_expected)
    
    return {
        "case_id": case_id,
        "case_number": case.case_number,
        "filing_date": filing_date.isoformat(),
        "days_pending": days_pending,
        "expected_completion_days": total_expected,
        "total_delay_days": total_delay,
        "delay_percentage": round((total_delay / total_expected) * 100, 1) if total_expected > 0 else 0,
        "delays": delays,
        "is_delayed": total_delay > 0,
        "urgency_level": case.urgency_level.value if case.urgency_level else None
    }

@router.get("/delayed")
async def get_delayed_cases(
    threshold_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all cases delayed beyond threshold"""
    cases = db.query(Case).filter(
        Case.status.in_(["filed", "admitted", "listed", "hearing", "reserved"])
    ).all()
    
    delayed_cases = []
    current_date = datetime.now()
    
    for case in cases:
        days_pending = (current_date - case.filing_date).days
        
        # Simple delay calculation
        expected_days = {
            "filed": 7,
            "admitted": 37,  # 7 + 30
            "listed": 51,  # 7 + 30 + 14
            "hearing": 111,  # 7 + 30 + 14 + 60
            "reserved": 141  # 7 + 30 + 14 + 60 + 30
        }
        
        expected = expected_days.get(case.status, 30)
        delay = days_pending - expected
        
        if delay > threshold_days:
            delayed_cases.append({
                "case_id": case.id,
                "case_number": case.case_number,
                "title": case.title,
                "status": case.status,
                "urgency_level": case.urgency_level.value if case.urgency_level else None,
                "filing_date": case.filing_date.isoformat(),
                "days_pending": days_pending,
                "expected_days": expected,
                "delay_days": delay,
                "delay_severity": "critical" if delay > 90 else "high" if delay > 60 else "moderate"
            })
    
    # Sort by delay (most delayed first)
    delayed_cases.sort(key=lambda x: x["delay_days"], reverse=True)
    
    return {
        "total_delayed": len(delayed_cases),
        "threshold_days": threshold_days,
        "delayed_cases": delayed_cases,
        "severity_breakdown": {
            "critical": len([c for c in delayed_cases if c["delay_severity"] == "critical"]),
            "high": len([c for c in delayed_cases if c["delay_severity"] == "high"]),
            "moderate": len([c for c in delayed_cases if c["delay_severity"] == "moderate"])
        }
    }


@router.post("/{case_id}/transfer")
async def transfer_case(
    case_id: int,
    target_court_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Transfer case to another court (appeals, jurisdiction change)"""
    from models import Court
    
    # Check permissions
    if current_user.role not in ["chief_justice", "court_administrator", "judge"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Get case
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get target court
    target_court = db.query(Court).filter(Court.id == target_court_id).first()
    if not target_court:
        raise HTTPException(status_code=404, detail="Target court not found")
    
    # Store old court info
    old_court_id = case.court_id
    old_court = db.query(Court).filter(Court.id == old_court_id).first()
    
    # Update case
    case.court_id = target_court_id
    case.assigned_judge_id = None  # Unassign judge when transferring
    
    # Create status history entry
    status_history = CaseStatusHistory(
        case_id=case.id,
        old_status=case.status,
        new_status=case.status,
        changed_by=current_user.id,
        reason=f"Case transferred from {old_court.name if old_court else 'Unknown'} to {target_court.name}. Reason: {reason}"
    )
    
    db.add(status_history)
    db.commit()
    
    return {
        "message": "Case transferred successfully",
        "case_id": case_id,
        "from_court": old_court.name if old_court else None,
        "to_court": target_court.name,
        "reason": reason
    }

@router.get("/{case_id}/transfer-history")
async def get_transfer_history(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transfer history for a case"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get status history entries related to transfers
    history = db.query(CaseStatusHistory).filter(
        CaseStatusHistory.case_id == case_id,
        CaseStatusHistory.reason.like('%transferred%')
    ).order_by(CaseStatusHistory.changed_at.desc()).all()
    
    transfers = []
    for entry in history:
        transfers.append({
            "date": entry.changed_at.isoformat(),
            "reason": entry.reason,
            "changed_by": entry.changed_by
        })
    
    return {
        "case_id": case_id,
        "case_number": case.case_number,
        "current_court_id": case.court_id,
        "transfers": transfers
    }
