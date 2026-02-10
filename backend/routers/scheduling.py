from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from database import get_db
from models import Case, Judge, Courtroom, Hearing, User
from schemas import SchedulingRequest, SchedulingResponse, HearingCreate, HearingResponse
from routers.auth import get_current_user

router = APIRouter()

class SchedulingEngine:
    """
    Constraint-based scheduling engine
    AI/ML PLACEHOLDER: This will be enhanced with ML optimization algorithms
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_available_slots(self, case_id: int, constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find available time slots for a case based on constraints"""
        case = self.db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return []
        
        # Get eligible judges based on specialization
        eligible_judges = self.db.query(Judge).filter(
            Judge.specializations.contains([case.jurisdiction]),
            Judge.is_available == True,
            Judge.court_id == case.court_id
        ).all()
        
        # Get available courtrooms
        available_courtrooms = self.db.query(Courtroom).filter(
            Courtroom.court_id == case.court_id,
            Courtroom.is_available == True
        ).all()
        
        # Generate time slots for next 30 days (excluding weekends)
        slots = []
        start_date = datetime.now() + timedelta(days=constraints.get('min_advance_days', 7))
        
        for day_offset in range(30):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            # Generate time slots (9 AM to 5 PM)
            for hour in range(9, 17):
                slot_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                for judge in eligible_judges:
                    for courtroom in available_courtrooms:
                        # Check for conflicts
                        conflicts = self._check_conflicts(judge.id, courtroom.id, slot_time, case.estimated_duration_hours)
                        
                        if not conflicts:
                            slots.append({
                                'datetime': slot_time,
                                'judge_id': judge.id,
                                'judge_name': judge.user.full_name if judge.user else f"Judge {judge.id}",
                                'courtroom_id': courtroom.id,
                                'courtroom_name': courtroom.name,
                                'estimated_duration': case.estimated_duration_hours,
                                'priority_score': self._calculate_priority_score(case, judge, slot_time)
                            })
        
        # Sort by priority score (higher is better)
        slots.sort(key=lambda x: x['priority_score'], reverse=True)
        return slots[:10]  # Return top 10 slots
    
    def _check_conflicts(self, judge_id: int, courtroom_id: int, start_time: datetime, duration_hours: float) -> List[str]:
        """Check for scheduling conflicts"""
        conflicts = []
        end_time = start_time + timedelta(hours=duration_hours)
        
        # Check judge conflicts
        judge_hearings = self.db.query(Hearing).join(Case).filter(
            Case.assigned_judge_id == judge_id,
            Hearing.scheduled_date >= start_time,
            Hearing.scheduled_date < end_time,
            Hearing.status.in_(['scheduled', 'hearing'])
        ).all()
        
        if judge_hearings:
            conflicts.append(f"Judge has {len(judge_hearings)} conflicting hearings")
        
        # Check courtroom conflicts
        courtroom_hearings = self.db.query(Hearing).filter(
            Hearing.courtroom_id == courtroom_id,
            Hearing.scheduled_date >= start_time,
            Hearing.scheduled_date < end_time,
            Hearing.status.in_(['scheduled', 'hearing'])
        ).all()
        
        if courtroom_hearings:
            conflicts.append(f"Courtroom has {len(courtroom_hearings)} conflicting hearings")
        
        return conflicts
    
    def _calculate_priority_score(self, case: Case, judge: Judge, slot_time: datetime) -> float:
        """Calculate priority score for a slot"""
        score = 0.0
        
        # Urgency factor
        urgency_weights = {
            'habeas_corpus': 10.0,
            'bail': 8.0,
            'injunction': 6.0,
            'regular': 1.0
        }
        score += urgency_weights.get(case.urgency_level.value, 1.0)
        
        # Age factor (older cases get higher priority)
        days_since_filing = (datetime.now() - case.filing_date).days
        score += min(days_since_filing * 0.1, 5.0)
        
        # Public interest factor
        score += case.public_interest_score * 0.5
        
        # Judge workload factor (prefer judges with lower workload)
        score += max(0, 10 - judge.current_workload) * 0.3
        
        # Time slot preference (morning slots for high-priority cases)
        if slot_time.hour < 12 and case.public_interest_score > 7:
            score += 2.0
        
        return score

@router.post("/find-slots", response_model=SchedulingResponse)
async def find_available_slots(
    request: SchedulingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find available time slots for a case"""
    if current_user.role not in ["chief_justice", "court_administrator", "scheduler"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    case = db.query(Case).filter(Case.id == request.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    engine = SchedulingEngine(db)
    constraints_dict = request.constraints.dict()
    
    suggested_slots = engine.find_available_slots(request.case_id, constraints_dict)
    
    # Generate explanation
    explanation = f"Found {len(suggested_slots)} available slots for case {case.case_number}. "
    explanation += f"Prioritized based on urgency ({case.urgency_level.value}), "
    explanation += f"case age ({(datetime.now() - case.filing_date).days} days), "
    explanation += f"and public interest score ({case.public_interest_score})."
    
    return SchedulingResponse(
        case_id=request.case_id,
        suggested_slots=suggested_slots,
        conflicts=[],
        explanation=explanation
    )

@router.post("/schedule-hearing", response_model=HearingResponse)
async def schedule_hearing(
    hearing: HearingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Schedule a hearing for a case"""
    if current_user.role not in ["chief_justice", "court_administrator", "scheduler"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    case = db.query(Case).filter(Case.id == hearing.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    courtroom = db.query(Courtroom).filter(Courtroom.id == hearing.courtroom_id).first()
    if not courtroom:
        raise HTTPException(status_code=404, detail="Courtroom not found")
    
    # Check for conflicts
    engine = SchedulingEngine(db)
    conflicts = engine._check_conflicts(
        case.assigned_judge_id or 0,
        hearing.courtroom_id,
        hearing.scheduled_date,
        hearing.scheduled_duration_hours
    )
    
    if conflicts:
        raise HTTPException(
            status_code=400,
            detail=f"Scheduling conflicts detected: {', '.join(conflicts)}"
        )
    
    db_hearing = Hearing(
        case_id=hearing.case_id,
        courtroom_id=hearing.courtroom_id,
        scheduled_date=hearing.scheduled_date,
        scheduled_duration_hours=hearing.scheduled_duration_hours,
        status="scheduled"
    )
    
    db.add(db_hearing)
    
    # Update case status if needed
    if case.status.value == "admitted":
        case.status = "listed"
    
    db.commit()
    db.refresh(db_hearing)
    
    return db_hearing

@router.get("/conflicts/{case_id}")
async def get_scheduling_conflicts(
    case_id: int,
    proposed_date: datetime,
    duration_hours: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed conflict information for a proposed hearing time"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    engine = SchedulingEngine(db)
    
    # Check conflicts for all possible judges and courtrooms
    conflicts = []
    
    # Get eligible judges
    eligible_judges = db.query(Judge).filter(
        Judge.specializations.contains([case.jurisdiction]),
        Judge.court_id == case.court_id
    ).all()
    
    for judge in eligible_judges:
        judge_conflicts = engine._check_conflicts(
            judge.id, 0, proposed_date, duration_hours
        )
        if judge_conflicts:
            conflicts.append({
                'type': 'judge',
                'judge_id': judge.id,
                'judge_name': judge.user.full_name if judge.user else f"Judge {judge.id}",
                'conflicts': judge_conflicts
            })
    
    # Check courtroom conflicts
    courtrooms = db.query(Courtroom).filter(Courtroom.court_id == case.court_id).all()
    
    for courtroom in courtrooms:
        courtroom_conflicts = engine._check_conflicts(
            0, courtroom.id, proposed_date, duration_hours
        )
        if courtroom_conflicts:
            conflicts.append({
                'type': 'courtroom',
                'courtroom_id': courtroom.id,
                'courtroom_name': courtroom.name,
                'conflicts': courtroom_conflicts
            })
    
    return {
        'case_id': case_id,
        'proposed_datetime': proposed_date,
        'duration_hours': duration_hours,
        'conflicts': conflicts,
        'has_conflicts': len(conflicts) > 0
    }

@router.post("/reschedule/{hearing_id}")
async def reschedule_hearing(
    hearing_id: int,
    new_date: datetime,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reschedule an existing hearing"""
    if current_user.role not in ["chief_justice", "court_administrator", "scheduler"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    hearing = db.query(Hearing).filter(Hearing.id == hearing_id).first()
    if not hearing:
        raise HTTPException(status_code=404, detail="Hearing not found")
    
    # Check for conflicts at new time
    engine = SchedulingEngine(db)
    case = hearing.case
    conflicts = engine._check_conflicts(
        case.assigned_judge_id or 0,
        hearing.courtroom_id,
        new_date,
        hearing.scheduled_duration_hours
    )
    
    if conflicts:
        raise HTTPException(
            status_code=400,
            detail=f"Conflicts at new time: {', '.join(conflicts)}"
        )
    
    # Update hearing
    hearing.scheduled_date = new_date
    hearing.adjournment_reason = reason
    hearing.notes = f"Rescheduled by {current_user.full_name} on {datetime.now()}"
    
    db.commit()
    
    return {"message": "Hearing rescheduled successfully"}

@router.get("/optimization-report")
async def get_scheduling_optimization_report(
    court_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get scheduling optimization metrics and suggestions
    AI/ML PLACEHOLDER: This will use ML models for optimization insights
    """
    
    # Basic metrics for now - will be enhanced with ML
    query = db.query(Case)
    if court_id:
        query = query.filter(Case.court_id == court_id)
    
    total_cases = query.count()
    pending_cases = query.filter(Case.status.in_(["filed", "admitted", "listed"])).count()
    
    # Calculate average delay
    filed_cases = query.filter(Case.status != "filed").all()
    total_delay_days = sum(
        (datetime.now() - case.filing_date).days for case in filed_cases
    ) if filed_cases else 0
    avg_delay_days = total_delay_days / len(filed_cases) if filed_cases else 0
    
    return {
        "court_id": court_id,
        "total_cases": total_cases,
        "pending_cases": pending_cases,
        "average_delay_days": avg_delay_days,
        "optimization_suggestions": [
            "AI/ML PLACEHOLDER: ML-based optimization suggestions will be implemented",
            "Current basic metrics show system status",
            "Advanced scheduling algorithms pending implementation"
        ],
        "workload_distribution": "AI/ML PLACEHOLDER: Judge workload optimization pending",
        "predicted_improvements": "AI/ML PLACEHOLDER: ML predictions pending"
    }