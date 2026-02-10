from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Court, User
from routers.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_courts(
    level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all courts with optional level filter"""
    query = db.query(Court)
    
    if level:
        query = query.filter(Court.level == level)
    
    courts = query.all()
    
    # Build hierarchy
    court_list = []
    for court in courts:
        parent_name = None
        if court.parent_court_id:
            parent = db.query(Court).filter(Court.id == court.parent_court_id).first()
            parent_name = parent.name if parent else None
        
        court_list.append({
            "id": court.id,
            "name": court.name,
            "level": court.level.value if court.level else None,
            "jurisdiction": court.jurisdiction.value if court.jurisdiction else None,
            "location": court.location,
            "parent_court_id": court.parent_court_id,
            "parent_court_name": parent_name,
            "is_active": court.is_active,
            "created_at": court.created_at.isoformat() if court.created_at else None
        })
    
    return court_list

@router.get("/hierarchy")
async def get_court_hierarchy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get court hierarchy tree structure"""
    courts = db.query(Court).all()
    
    # Build tree structure
    court_map = {}
    for court in courts:
        court_map[court.id] = {
            "id": court.id,
            "name": court.name,
            "level": court.level.value if court.level else None,
            "jurisdiction": court.jurisdiction.value if court.jurisdiction else None,
            "location": court.location,
            "parent_court_id": court.parent_court_id,
            "children": []
        }
    
    # Build hierarchy
    root_courts = []
    for court_id, court_data in court_map.items():
        if court_data["parent_court_id"]:
            parent = court_map.get(court_data["parent_court_id"])
            if parent:
                parent["children"].append(court_data)
        else:
            root_courts.append(court_data)
    
    return {
        "hierarchy": root_courts,
        "total_courts": len(courts),
        "levels": {
            "supreme_court": len([c for c in courts if c.level.value == "supreme_court"]),
            "high_court": len([c for c in courts if c.level.value == "high_court"]),
            "district_court": len([c for c in courts if c.level.value == "district_court"])
        }
    }

@router.get("/statistics")
async def get_court_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get court system statistics"""
    from models import Case, Judge
    
    courts = db.query(Court).all()
    total_cases = db.query(Case).count()
    total_judges = db.query(Judge).count()
    
    court_stats = []
    for court in courts:
        cases_count = db.query(Case).filter(Case.court_id == court.id).count()
        judges_count = db.query(Judge).filter(Judge.court_id == court.id).count()
        
        court_stats.append({
            "court_id": court.id,
            "court_name": court.name,
            "level": court.level.value if court.level else None,
            "cases_count": cases_count,
            "judges_count": judges_count,
            "utilization": round((cases_count / max(judges_count * 10, 1)) * 100, 1)
        })
    
    return {
        "total_courts": len(courts),
        "total_cases": total_cases,
        "total_judges": total_judges,
        "court_statistics": court_stats
    }
