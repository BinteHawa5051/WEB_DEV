from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date

from database import get_db
from models import Hearing, Case, Judge, Courtroom, User
from schemas import CalendarHeatmap, CalendarSlot
from routers.auth import get_current_user

router = APIRouter()

@router.get("/heatmap")
async def get_calendar_heatmap(
    start_date: date = Query(..., description="Start date for heatmap"),
    end_date: date = Query(..., description="End date for heatmap"),
    court_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate calendar heatmap data for visualization"""
    
    # Convert dates to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Get all hearings in the date range
    query = db.query(Hearing).filter(
        Hearing.scheduled_date >= start_datetime,
        Hearing.scheduled_date <= end_datetime
    )
    
    if court_id:
        query = query.join(Case).filter(Case.court_id == court_id)
    
    hearings = query.all()
    
    # Get all courtrooms for capacity calculation
    courtroom_query = db.query(Courtroom)
    if court_id:
        courtroom_query = courtroom_query.filter(Courtroom.court_id == court_id)
    
    courtrooms = courtroom_query.all()
    total_courtrooms = len(courtrooms)
    
    # Generate calendar slots
    slots = []
    current_date = start_datetime
    
    while current_date <= end_datetime:
        # Skip weekends
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            
            # Calculate daily metrics
            daily_hearings = [h for h in hearings if h.scheduled_date.date() == current_date.date()]
            
            # Calculate capacity utilization
            total_daily_hours = 0
            for hearing in daily_hearings:
                total_daily_hours += hearing.scheduled_duration_hours
            
            # Assuming 8 working hours per day per courtroom
            max_daily_capacity = total_courtrooms * 8
            capacity_percentage = (total_daily_hours / max_daily_capacity * 100) if max_daily_capacity > 0 else 0
            
            # Determine status based on capacity
            if capacity_percentage < 50:
                status = "available"
            elif capacity_percentage < 80:
                status = "moderate"
            elif capacity_percentage < 100:
                status = "busy"
            else:
                status = "overloaded"
            
            # Create slots for each courtroom
            for courtroom in courtrooms:
                courtroom_hearings = [h for h in daily_hearings if h.courtroom_id == courtroom.id]
                courtroom_hours = sum(h.scheduled_duration_hours for h in courtroom_hearings)
                courtroom_capacity = (courtroom_hours / 8 * 100) if courtroom_hours <= 8 else 100
                
                slot = CalendarSlot(
                    date=current_date,
                    courtroom_id=courtroom.id,
                    judge_id=courtroom_hearings[0].case.assigned_judge_id if courtroom_hearings else None,
                    case_id=courtroom_hearings[0].case_id if courtroom_hearings else None,
                    status=status,
                    capacity_percentage=courtroom_capacity
                )
                slots.append(slot)
        
        current_date += timedelta(days=1)
    
    # Calculate judge workload distribution
    judges = db.query(Judge).all()
    workload_distribution = {}
    
    for judge in judges:
        judge_hearings = [h for h in hearings if h.case.assigned_judge_id == judge.id]
        total_hours = sum(h.scheduled_duration_hours for h in judge_hearings)
        # Assuming 40 hours per week capacity
        weeks_in_period = (end_date - start_date).days / 7
        max_capacity = weeks_in_period * 40
        workload_percentage = (total_hours / max_capacity * 100) if max_capacity > 0 else 0
        workload_distribution[judge.id] = min(workload_percentage, 100)
    
    return CalendarHeatmap(
        date_range={"start": start_datetime, "end": end_datetime},
        slots=slots,
        workload_distribution=workload_distribution
    )

@router.get("/day-view")
async def get_day_view(
    target_date: date = Query(..., description="Date to view"),
    court_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed day view with courtroom-wise schedule"""
    
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())
    
    # Get hearings for the day
    query = db.query(Hearing).filter(
        Hearing.scheduled_date >= start_datetime,
        Hearing.scheduled_date <= end_datetime
    ).join(Case)
    
    if court_id:
        query = query.filter(Case.court_id == court_id)
    
    hearings = query.all()
    
    # Get courtrooms
    courtroom_query = db.query(Courtroom)
    if court_id:
        courtroom_query = courtroom_query.filter(Courtroom.court_id == court_id)
    
    courtrooms = courtroom_query.all()
    
    # Organize by courtroom and time
    schedule = {}
    
    for courtroom in courtrooms:
        courtroom_hearings = [h for h in hearings if h.courtroom_id == courtroom.id]
        courtroom_hearings.sort(key=lambda x: x.scheduled_date)
        
        schedule[courtroom.id] = {
            "courtroom_name": courtroom.name,
            "hearings": []
        }
        
        for hearing in courtroom_hearings:
            case = hearing.case
            judge = case.assigned_judge
            
            hearing_info = {
                "hearing_id": hearing.id,
                "case_number": case.case_number,
                "case_title": case.title,
                "scheduled_time": hearing.scheduled_date,
                "duration_hours": hearing.scheduled_duration_hours,
                "judge_name": judge.user.full_name if judge and judge.user else "Unassigned",
                "status": hearing.status,
                "urgency_level": case.urgency_level.value,
                "case_type": case.case_type
            }
            
            schedule[courtroom.id]["hearings"].append(hearing_info)
    
    return {
        "date": target_date,
        "court_id": court_id,
        "schedule": schedule,
        "total_hearings": len(hearings),
        "summary": {
            "total_courtrooms": len(courtrooms),
            "active_courtrooms": len([cr for cr in schedule.values() if cr["hearings"]]),
            "total_hours_scheduled": sum(h.scheduled_duration_hours for h in hearings)
        }
    }

@router.get("/week-view")
async def get_week_view(
    week_start: date = Query(..., description="Start of week (Monday)"),
    court_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get week view with detailed time slots"""
    
    # Ensure week_start is a Monday
    days_since_monday = week_start.weekday()
    actual_monday = week_start - timedelta(days=days_since_monday)
    week_end = actual_monday + timedelta(days=6)
    
    start_datetime = datetime.combine(actual_monday, datetime.min.time())
    end_datetime = datetime.combine(week_end, datetime.max.time())
    
    # Get hearings for the week
    query = db.query(Hearing).filter(
        Hearing.scheduled_date >= start_datetime,
        Hearing.scheduled_date <= end_datetime
    ).join(Case)
    
    if court_id:
        query = query.filter(Case.court_id == court_id)
    
    hearings = query.all()
    
    # Organize by day
    week_schedule = {}
    
    for day_offset in range(7):
        current_date = actual_monday + timedelta(days=day_offset)
        day_name = current_date.strftime("%A")
        
        # Skip weekends for court schedule
        if day_offset >= 5:
            week_schedule[day_name] = {
                "date": current_date,
                "is_working_day": False,
                "hearings": []
            }
            continue
        
        day_hearings = [
            h for h in hearings 
            if h.scheduled_date.date() == current_date
        ]
        
        # Create time slots (9 AM to 5 PM)
        time_slots = []
        for hour in range(9, 17):
            slot_time = datetime.combine(current_date, datetime.min.time()).replace(hour=hour, minute=0, second=0, microsecond=0)
            slot_hearings = [
                h for h in day_hearings
                if h.scheduled_date.hour == hour
            ]
            
            time_slots.append({
                "time": slot_time,
                "hearings": [
                    {
                        "hearing_id": h.id,
                        "case_number": h.case.case_number,
                        "case_title": h.case.title,
                        "courtroom": h.courtroom.name,
                        "duration": h.scheduled_duration_hours,
                        "judge": h.case.assigned_judge.user.full_name if h.case.assigned_judge and h.case.assigned_judge.user else "Unassigned"
                    }
                    for h in slot_hearings
                ]
            })
        
        week_schedule[day_name] = {
            "date": current_date,
            "is_working_day": True,
            "total_hearings": len(day_hearings),
            "time_slots": time_slots
        }
    
    return {
        "week_start": actual_monday,
        "week_end": week_end,
        "court_id": court_id,
        "schedule": week_schedule,
        "summary": {
            "total_hearings": len(hearings),
            "busiest_day": max(
                [(day, data["total_hearings"]) for day, data in week_schedule.items() if data["is_working_day"]],
                key=lambda x: x[1],
                default=("None", 0)
            )[0]
        }
    }

@router.get("/upcoming-hearings")
async def get_upcoming_hearings(
    days_ahead: int = Query(7, description="Number of days to look ahead"),
    judge_id: Optional[int] = None,
    courtroom_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming hearings for quick view"""
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=days_ahead)
    
    query = db.query(Hearing).filter(
        Hearing.scheduled_date >= start_date,
        Hearing.scheduled_date <= end_date,
        Hearing.status.in_(["scheduled", "hearing"])
    ).join(Case)
    
    if judge_id:
        query = query.filter(Case.assigned_judge_id == judge_id)
    
    if courtroom_id:
        query = query.filter(Hearing.courtroom_id == courtroom_id)
    
    # Filter by user's court if not admin
    if current_user.role not in ["chief_justice", "court_administrator"]:
        query = query.filter(Case.court_id == current_user.court_id)
    
    hearings = query.order_by(Hearing.scheduled_date).all()
    
    upcoming = []
    for hearing in hearings:
        case = hearing.case
        judge = case.assigned_judge
        
        upcoming.append({
            "hearing_id": hearing.id,
            "case_number": case.case_number,
            "case_title": case.title,
            "scheduled_date": hearing.scheduled_date,
            "duration_hours": hearing.scheduled_duration_hours,
            "courtroom": hearing.courtroom.name,
            "judge": judge.user.full_name if judge and judge.user else "Unassigned",
            "urgency": case.urgency_level.value,
            "days_until": (hearing.scheduled_date.date() - datetime.now().date()).days
        })
    
    return {
        "upcoming_hearings": upcoming,
        "total_count": len(upcoming),
        "date_range": {
            "start": start_date,
            "end": end_date
        }
    }

@router.post("/drag-drop-reschedule")
async def drag_drop_reschedule(
    hearing_id: int,
    new_datetime: datetime,
    new_courtroom_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Handle drag-and-drop rescheduling with conflict checking"""
    
    if current_user.role not in ["chief_justice", "court_administrator", "scheduler"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    hearing = db.query(Hearing).filter(Hearing.id == hearing_id).first()
    if not hearing:
        raise HTTPException(status_code=404, detail="Hearing not found")
    
    # Use existing courtroom if not specified
    target_courtroom_id = new_courtroom_id or hearing.courtroom_id
    
    # Check for conflicts at new time
    end_time = new_datetime + timedelta(hours=hearing.scheduled_duration_hours)
    
    conflicts = db.query(Hearing).filter(
        Hearing.courtroom_id == target_courtroom_id,
        Hearing.scheduled_date < end_time,
        Hearing.scheduled_date + timedelta(hours=Hearing.scheduled_duration_hours) > new_datetime,
        Hearing.id != hearing_id,
        Hearing.status.in_(["scheduled", "hearing"])
    ).all()
    
    if conflicts:
        conflict_details = [
            {
                "hearing_id": c.id,
                "case_number": c.case.case_number,
                "scheduled_time": c.scheduled_date,
                "duration": c.scheduled_duration_hours
            }
            for c in conflicts
        ]
        
        return {
            "success": False,
            "conflicts": conflict_details,
            "message": f"Cannot reschedule: {len(conflicts)} conflicting hearings found"
        }
    
    # Update hearing
    hearing.scheduled_date = new_datetime
    if new_courtroom_id:
        hearing.courtroom_id = new_courtroom_id
    
    hearing.notes = f"Rescheduled via drag-drop by {current_user.full_name} at {datetime.now()}"
    
    db.commit()
    
    return {
        "success": True,
        "message": "Hearing rescheduled successfully",
        "new_datetime": new_datetime,
        "courtroom_id": target_courtroom_id
    }