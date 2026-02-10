from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    CHIEF_JUSTICE = "chief_justice"
    PRESIDING_JUDGE = "presiding_judge"
    COURT_ADMINISTRATOR = "court_administrator"
    SCHEDULER = "scheduler"
    LAWYER = "lawyer"
    PUBLIC_PROSECUTOR = "public_prosecutor"
    LITIGANT = "litigant"
    PUBLIC = "public"

class CourtLevel(str, enum.Enum):
    SUPREME_COURT = "supreme_court"
    HIGH_COURT = "high_court"
    DISTRICT_COURT = "district_court"

class Jurisdiction(str, enum.Enum):
    CIVIL = "civil"
    CRIMINAL = "criminal"
    FAMILY = "family"
    TAX = "tax"
    CONSTITUTIONAL = "constitutional"

class CaseStatus(str, enum.Enum):
    FILED = "filed"
    ADMITTED = "admitted"
    LISTED = "listed"
    HEARING = "hearing"
    RESERVED = "reserved"
    JUDGMENT = "judgment"
    ARCHIVED = "archived"

class UrgencyLevel(str, enum.Enum):
    HABEAS_CORPUS = "habeas_corpus"
    BAIL = "bail"
    INJUNCTION = "injunction"
    REGULAR = "regular"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]))
    court_id = Column(Integer, ForeignKey("courts.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    court = relationship("Court", back_populates="users")

class Court(Base):
    __tablename__ = "courts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    level = Column(SQLEnum(CourtLevel, values_callable=lambda x: [e.value for e in x]))
    jurisdiction = Column(SQLEnum(Jurisdiction, values_callable=lambda x: [e.value for e in x]))
    location = Column(String)
    parent_court_id = Column(Integer, ForeignKey("courts.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    users = relationship("User", back_populates="court")
    cases = relationship("Case", back_populates="court")
    judges = relationship("Judge", back_populates="court")
    courtrooms = relationship("Courtroom", back_populates="court")

class Judge(Base):
    __tablename__ = "judges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    court_id = Column(Integer, ForeignKey("courts.id"))
    specializations = Column(JSON)  # List of jurisdictions
    experience_years = Column(Integer)
    disposal_rate = Column(Float)
    current_workload = Column(Integer, default=0)
    performance_score = Column(Float)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    court = relationship("Court", back_populates="judges")
    cases = relationship("Case", back_populates="assigned_judge")
    recusals = relationship("JudgeRecusal", back_populates="judge")

class Lawyer(Base):
    __tablename__ = "lawyers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bar_registration = Column(String, unique=True)
    firm_name = Column(String)
    specializations = Column(JSON)
    win_rate = Column(Float)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    case_lawyers = relationship("CaseLawyer", back_populates="lawyer")

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, index=True)
    title = Column(String)
    court_id = Column(Integer, ForeignKey("courts.id"))
    jurisdiction = Column(SQLEnum(Jurisdiction, values_callable=lambda x: [e.value for e in x]))
    case_type = Column(String)
    status = Column(SQLEnum(CaseStatus, values_callable=lambda x: [e.value for e in x]), default=CaseStatus.FILED)
    urgency_level = Column(SQLEnum(UrgencyLevel, values_callable=lambda x: [e.value for e in x]), default=UrgencyLevel.REGULAR)
    complexity_score = Column(Integer)  # 1-10
    public_interest_score = Column(Integer)  # 1-10
    estimated_duration_hours = Column(Float)
    filing_date = Column(DateTime, default=datetime.utcnow)
    assigned_judge_id = Column(Integer, ForeignKey("judges.id"))
    description = Column(Text)
    connected_cases = Column(JSON)  # List of connected case IDs
    
    court = relationship("Court", back_populates="cases")
    assigned_judge = relationship("Judge", back_populates="cases")
    case_lawyers = relationship("CaseLawyer", back_populates="case")
    hearings = relationship("Hearing", back_populates="case")
    documents = relationship("Document", back_populates="case")
    status_history = relationship("CaseStatusHistory", back_populates="case")

class CaseLawyer(Base):
    __tablename__ = "case_lawyers"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"))
    party_type = Column(String)  # plaintiff, defendant, etc.
    is_lead = Column(Boolean, default=False)
    
    case = relationship("Case", back_populates="case_lawyers")
    lawyer = relationship("Lawyer", back_populates="case_lawyers")

class Courtroom(Base):
    __tablename__ = "courtrooms"
    
    id = Column(Integer, primary_key=True, index=True)
    court_id = Column(Integer, ForeignKey("courts.id"))
    name = Column(String)
    capacity = Column(Integer)
    equipment = Column(JSON)  # List of available equipment
    is_available = Column(Boolean, default=True)
    
    court = relationship("Court", back_populates="courtrooms")
    hearings = relationship("Hearing", back_populates="courtroom")

class Hearing(Base):
    __tablename__ = "hearings"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    courtroom_id = Column(Integer, ForeignKey("courtrooms.id"))
    scheduled_date = Column(DateTime)
    scheduled_duration_hours = Column(Float)
    actual_duration_hours = Column(Float)
    status = Column(String)  # scheduled, completed, adjourned, cancelled
    adjournment_reason = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="hearings")
    courtroom = relationship("Courtroom", back_populates="hearings")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    title = Column(String)
    document_type = Column(String)  # pleading, evidence, order, judgment
    file_path = Column(String)
    file_hash = Column(String)
    digital_signature = Column(Text)
    version = Column(Integer, default=1)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    upload_date = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    
    case = relationship("Case", back_populates="documents")
    uploader = relationship("User")

class JudgeRecusal(Base):
    __tablename__ = "judge_recusals"
    
    id = Column(Integer, primary_key=True, index=True)
    judge_id = Column(Integer, ForeignKey("judges.id"))
    case_id = Column(Integer, ForeignKey("cases.id"))
    reason = Column(String)
    recusal_date = Column(DateTime, default=datetime.utcnow)
    
    judge = relationship("Judge", back_populates="recusals")

class CaseStatusHistory(Base):
    __tablename__ = "case_status_history"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    old_status = Column(SQLEnum(CaseStatus, values_callable=lambda x: [e.value for e in x]))
    new_status = Column(SQLEnum(CaseStatus, values_callable=lambda x: [e.value for e in x]))
    changed_by = Column(Integer, ForeignKey("users.id"))
    change_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    case = relationship("Case", back_populates="status_history")
    changed_by_user = relationship("User")

# AI/ML Placeholder Models
class CasePrediction(Base):
    __tablename__ = "case_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    predicted_duration_hours = Column(Float)
    predicted_hearings_count = Column(Integer)
    settlement_probability = Column(Float)
    outcome_probability = Column(JSON)  # Probabilities for different outcomes
    confidence_score = Column(Float)
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # AI/ML PLACEHOLDER: This will store ML model predictions