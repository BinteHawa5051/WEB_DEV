from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class UserRoleEnum(str, Enum):
    CHIEF_JUSTICE = "chief_justice"
    PRESIDING_JUDGE = "presiding_judge"
    COURT_ADMINISTRATOR = "court_administrator"
    SCHEDULER = "scheduler"
    LAWYER = "lawyer"
    PUBLIC_PROSECUTOR = "public_prosecutor"
    LITIGANT = "litigant"
    PUBLIC = "public"

class CourtLevelEnum(str, Enum):
    SUPREME_COURT = "supreme_court"
    HIGH_COURT = "high_court"
    DISTRICT_COURT = "district_court"

class JurisdictionEnum(str, Enum):
    CIVIL = "civil"
    CRIMINAL = "criminal"
    FAMILY = "family"
    TAX = "tax"
    CONSTITUTIONAL = "constitutional"

class CaseStatusEnum(str, Enum):
    FILED = "filed"
    ADMITTED = "admitted"
    LISTED = "listed"
    HEARING = "hearing"
    RESERVED = "reserved"
    JUDGMENT = "judgment"
    ARCHIVED = "archived"

class UrgencyLevelEnum(str, Enum):
    HABEAS_CORPUS = "habeas_corpus"
    BAIL = "bail"
    INJUNCTION = "injunction"
    REGULAR = "regular"

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRoleEnum
    court_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CourtBase(BaseModel):
    name: str
    level: CourtLevelEnum
    jurisdiction: JurisdictionEnum
    location: str
    parent_court_id: Optional[int] = None

class CourtCreate(CourtBase):
    pass

class CourtResponse(CourtBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class JudgeBase(BaseModel):
    specializations: List[JurisdictionEnum]
    experience_years: int
    court_id: int

class JudgeCreate(JudgeBase):
    user_id: int

class JudgeResponse(JudgeBase):
    id: int
    disposal_rate: Optional[float]
    current_workload: int
    performance_score: Optional[float]
    is_available: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LawyerBase(BaseModel):
    bar_registration: str
    firm_name: Optional[str] = None
    specializations: List[JurisdictionEnum]

class LawyerCreate(LawyerBase):
    user_id: int

class LawyerResponse(LawyerBase):
    id: int
    win_rate: Optional[float]
    is_available: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CaseBase(BaseModel):
    title: str
    court_id: int
    jurisdiction: JurisdictionEnum
    case_type: str
    urgency_level: UrgencyLevelEnum = UrgencyLevelEnum.REGULAR
    complexity_score: int  # 1-10
    public_interest_score: int  # 1-10
    estimated_duration_hours: float
    description: Optional[str] = None
    connected_cases: Optional[List[int]] = []

class CaseCreate(CaseBase):
    pass

class CaseResponse(CaseBase):
    id: int
    case_number: str
    status: CaseStatusEnum
    filing_date: datetime
    assigned_judge_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class HearingBase(BaseModel):
    case_id: int
    courtroom_id: int
    scheduled_date: datetime
    scheduled_duration_hours: float

class HearingCreate(HearingBase):
    pass

class HearingResponse(HearingBase):
    id: int
    actual_duration_hours: Optional[float]
    status: str
    adjournment_reason: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str
    document_type: str
    is_public: bool = False

class DocumentCreate(DocumentBase):
    case_id: int

class DocumentResponse(DocumentBase):
    id: int
    case_id: int
    file_path: str
    file_hash: str
    digital_signature: Optional[str]
    version: int
    uploaded_by: int
    upload_date: datetime
    
    class Config:
        from_attributes = True

# Scheduling schemas
class SchedulingConstraints(BaseModel):
    judge_expertise_required: List[JurisdictionEnum]
    min_advance_days: int = 7
    max_daily_hours: float = 6.0
    preferred_time_slots: Optional[List[str]] = None
    avoid_conflicts_with: Optional[List[int]] = None

class SchedulingRequest(BaseModel):
    case_id: int
    constraints: SchedulingConstraints
    priority_weight: float = 1.0

class SchedulingResponse(BaseModel):
    case_id: int
    suggested_slots: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    explanation: str

# Calendar schemas
class CalendarSlot(BaseModel):
    date: datetime
    courtroom_id: int
    judge_id: Optional[int]
    case_id: Optional[int]
    status: str  # available, booked, blocked
    capacity_percentage: float

class CalendarHeatmap(BaseModel):
    date_range: Dict[str, datetime]
    slots: List[CalendarSlot]
    workload_distribution: Dict[int, float]  # judge_id -> workload percentage

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# AI/ML Placeholder schemas
class CasePredictionResponse(BaseModel):
    case_id: int
    predicted_duration_hours: float
    predicted_hearings_count: int
    settlement_probability: float
    outcome_probability: Dict[str, float]
    confidence_score: float
    
    # AI/ML PLACEHOLDER: These will be populated by ML models