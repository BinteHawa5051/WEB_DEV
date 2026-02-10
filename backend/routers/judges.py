from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Judge, User, JudgeRecusal, Case
from schemas import JudgeCreate, JudgeResponse, JurisdictionEnum
from routers.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=JudgeResponse)
async def create_judge(
    judge: JudgeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["chief_justice", "court_administrator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if user exists and is not already a judge
    user = db.query(User).filter(User.id == judge.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_judge = db.query(Judge).filter(Judge.user_id == judge.user_id).first()
    if existing_judge:
        raise HTTPException(status_code=400, detail="User is already a judge")
    
    db_judge = Judge(
        user_id=judge.user_id,
        court_id=judge.court_id,
        specializations=judge.specializations,
        experience_years=judge.experience_years,
        disposal_rate=0.0,
        performance_score=0.0
    )
    
    db.add(db_judge)
    db.commit()
    db.refresh(db_judge)
    return db_judge

@router.get("/", response_model=List[JudgeResponse])
async def get_judges(
    court_id: Optional[int] = None,
    specialization: Optional[JurisdictionEnum] = None,
    available_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Judge)
    
    if court_id:
        query = query.filter(Judge.court_id == court_id)
    
    if specialization:
        query = query.filter(Judge.specializations.contains([specialization]))
    
    if available_only:
        query = query.filter(Judge.is_available == True)
    
    judges = query.all()
    return judges

@router.get("/workload-analysis")
async def analyze_judge_workload(
    court_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze judge workload distribution and identify imbalances
    Returns workload statistics and rebalancing suggestions
    """
    query = db.query(Judge)
    if court_id:
        query = query.filter(Judge.court_id == court_id)
    
    judges = query.all()
    
    if not judges:
        return {
            "total_judges": 0,
            "workload_stats": {},
            "imbalanced_judges": [],
            "suggestions": []
        }
    
    # Calculate workload statistics
    workloads = [j.current_workload or 0 for j in judges]
    avg_workload = sum(workloads) / len(workloads) if workloads else 0
    max_workload = max(workloads) if workloads else 0
    min_workload = min(workloads) if workloads else 0
    
    # Identify overloaded judges (>2x average or >80%)
    overloaded = []
    underloaded = []
    
    for judge in judges:
        workload = judge.current_workload or 0
        if workload > avg_workload * 2 or workload > 80:
            overloaded.append({
                "judge_id": judge.id,
                "judge_name": judge.user.full_name if judge.user else f"Judge {judge.id}",
                "current_workload": workload,
                "excess": workload - avg_workload,
                "severity": "critical" if workload > 90 else "high" if workload > 80 else "moderate"
            })
        elif workload < avg_workload * 0.5 and judge.is_available:
            underloaded.append({
                "judge_id": judge.id,
                "judge_name": judge.user.full_name if judge.user else f"Judge {judge.id}",
                "current_workload": workload,
                "capacity": avg_workload - workload
            })
    
    # Generate rebalancing suggestions
    suggestions = []
    if overloaded and underloaded:
        for over in overloaded[:3]:  # Top 3 overloaded
            for under in underloaded[:2]:  # Top 2 underloaded
                cases_to_transfer = min(3, int(over["excess"] / 2))
                if cases_to_transfer > 0:
                    suggestions.append({
                        "from_judge_id": over["judge_id"],
                        "from_judge": over["judge_name"],
                        "to_judge_id": under["judge_id"],
                        "to_judge": under["judge_name"],
                        "suggested_cases_count": cases_to_transfer,
                        "reason": f"Reduce workload imbalance ({over['current_workload']}% → {over['current_workload'] - cases_to_transfer*5}%)"
                    })
    
    return {
        "total_judges": len(judges),
        "available_judges": len([j for j in judges if j.is_available]),
        "workload_stats": {
            "average": round(avg_workload, 1),
            "maximum": max_workload,
            "minimum": min_workload,
            "std_deviation": round(
                (sum((w - avg_workload) ** 2 for w in workloads) / len(workloads)) ** 0.5, 1
            ) if len(workloads) > 1 else 0
        },
        "overloaded_judges": overloaded,
        "underloaded_judges": underloaded,
        "balance_score": round(100 - (max_workload - min_workload), 1),  # 100 = perfect balance
        "suggestions": suggestions,
        "needs_rebalancing": len(overloaded) > 0
    }

@router.get("/{judge_id}", response_model=JudgeResponse)
async def get_judge(
    judge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    judge = db.query(Judge).filter(Judge.id == judge_id).first()
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    return judge

@router.put("/{judge_id}/availability")
async def update_judge_availability(
    judge_id: int,
    is_available: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["chief_justice", "court_administrator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    judge = db.query(Judge).filter(Judge.id == judge_id).first()
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    
    judge.is_available = is_available
    db.commit()
    
    return {"message": "Judge availability updated"}

@router.post("/{judge_id}/recusal")
async def create_recusal(
    judge_id: int,
    case_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["chief_justice", "presiding_judge", "court_administrator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if judge and case exist
    judge = db.query(Judge).filter(Judge.id == judge_id).first()
    case = db.query(Case).filter(Case.id == case_id).first()
    
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check if recusal already exists
    existing_recusal = db.query(JudgeRecusal).filter(
        JudgeRecusal.judge_id == judge_id,
        JudgeRecusal.case_id == case_id
    ).first()
    
    if existing_recusal:
        raise HTTPException(status_code=400, detail="Recusal already exists")
    
    recusal = JudgeRecusal(
        judge_id=judge_id,
        case_id=case_id,
        reason=reason
    )
    
    db.add(recusal)
    
    # If this judge was assigned to the case, unassign them
    if case.assigned_judge_id == judge_id:
        case.assigned_judge_id = None
    
    db.commit()
    
    return {"message": "Recusal created successfully"}

@router.get("/{judge_id}/workload")
async def get_judge_workload(
    judge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    judge = db.query(Judge).filter(Judge.id == judge_id).first()
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    
    # Get active cases assigned to judge
    active_cases = db.query(Case).filter(
        Case.assigned_judge_id == judge_id,
        Case.status.in_(["admitted", "listed", "hearing", "reserved"])
    ).all()
    
    # Calculate workload metrics
    total_cases = len(active_cases)
    total_estimated_hours = sum(case.estimated_duration_hours for case in active_cases)
    
    # Group by urgency and complexity
    urgency_breakdown = {}
    complexity_breakdown = {}
    
    for case in active_cases:
        urgency = case.urgency_level.value
        urgency_breakdown[urgency] = urgency_breakdown.get(urgency, 0) + 1
        
        complexity = case.complexity_score
        complexity_range = f"{complexity}-{min(complexity + 1, 10)}"
        complexity_breakdown[complexity_range] = complexity_breakdown.get(complexity_range, 0) + 1
    
    return {
        "judge_id": judge_id,
        "total_active_cases": total_cases,
        "total_estimated_hours": total_estimated_hours,
        "current_workload_percentage": judge.current_workload,
        "urgency_breakdown": urgency_breakdown,
        "complexity_breakdown": complexity_breakdown,
        "performance_score": judge.performance_score,
        "disposal_rate": judge.disposal_rate
    }

@router.get("/{judge_id}/schedule")
async def get_judge_schedule(
    judge_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get judge's hearing schedule"""
    # AI/ML PLACEHOLDER: This will integrate with scheduling optimization
    
    judge = db.query(Judge).filter(Judge.id == judge_id).first()
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    
    # This is a placeholder - actual implementation will come with scheduling engine
    return {
        "judge_id": judge_id,
        "schedule": [],
        "availability": judge.is_available,
        "message": "Schedule integration pending - AI/ML scheduling engine to be implemented"
    }
