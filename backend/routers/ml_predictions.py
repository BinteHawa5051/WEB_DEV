from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field

from database import get_db
from models import User
from routers.auth import get_current_user
from ml_service import get_ml_service

router = APIRouter()

# Request/Response Models
class CaseAnalysisRequest(BaseModel):
    """Request model for complete case analysis"""
    facts_text: str = Field(..., description="Case facts description")
    decision_type: str = Field(default="majority opinion", description="Type of decision")
    disposition: str = Field(default="affirmed", description="Case disposition")
    num_parties: int = Field(..., ge=1, description="Number of parties involved")
    num_witnesses: int = Field(..., ge=0, description="Number of witnesses")
    evidence_pages: int = Field(..., ge=0, description="Number of evidence pages")
    adjournments: int = Field(default=0, ge=0, description="Number of previous adjournments")
    judge_speed: float = Field(default=1.0, ge=0.1, le=3.0, description="Judge speed factor (1.0 = normal)")
    lawyer_win_rate: float = Field(..., ge=0.0, le=1.0, description="Lawyer's historical win rate")
    case_complexity: float = Field(..., ge=0.0, le=1.0, description="Case complexity score")
    top_judges: int = Field(default=3, ge=1, le=10, description="Number of judges to recommend")

class DurationPredictionRequest(BaseModel):
    """Request model for hearing duration prediction"""
    num_parties: int = Field(..., ge=1, description="Number of parties involved")
    num_witnesses: int = Field(..., ge=0, description="Number of witnesses")
    evidence_pages: int = Field(..., ge=0, description="Number of evidence pages")
    adjournments: int = Field(default=0, ge=0, description="Number of previous adjournments")
    judge_speed: float = Field(default=1.0, ge=0.1, le=3.0, description="Judge speed factor")
    lawyer_win_rate: float = Field(..., ge=0.0, le=1.0, description="Lawyer's win rate")

class OutcomePredictionRequest(BaseModel):
    """Request model for case outcome prediction"""
    facts_text: str = Field(..., description="Case facts description")
    decision_type: str = Field(default="majority opinion", description="Type of decision")
    disposition: str = Field(default="affirmed", description="Case disposition")

class JudgeRecommendationRequest(BaseModel):
    """Request model for judge recommendation"""
    case_complexity: float = Field(..., ge=0.0, le=1.0, description="Case complexity score")
    expected_duration: float = Field(..., ge=0.1, description="Expected duration in hours")
    plaintiff_win_prob: float = Field(..., ge=0.0, le=1.0, description="Plaintiff win probability")
    top_judges: int = Field(default=3, ge=1, le=10, description="Number of judges to recommend")

class RecommendedJudge(BaseModel):
    """Model for recommended judge"""
    judge_id: int
    similarity_score: float

class CaseAnalysisResponse(BaseModel):
    """Response model for complete case analysis"""
    outcome_probability: float = Field(..., description="Probability that plaintiff wins (0-1)")
    expected_duration_hours: float = Field(..., description="Expected hearing duration in hours")
    recommended_judges: List[RecommendedJudge] = Field(..., description="List of recommended judges")
    analysis_summary: str = Field(..., description="Human-readable summary")

class DurationPredictionResponse(BaseModel):
    """Response model for duration prediction"""
    predicted_duration_hours: float = Field(..., description="Predicted hearing duration in hours")
    confidence_level: str = Field(..., description="Confidence level of prediction")

class OutcomePredictionResponse(BaseModel):
    """Response model for outcome prediction"""
    plaintiff_win_probability: float = Field(..., description="Probability that plaintiff wins (0-1)")
    prediction_confidence: str = Field(..., description="Confidence level of prediction")

class JudgeRecommendationResponse(BaseModel):
    """Response model for judge recommendations"""
    recommended_judges: List[RecommendedJudge] = Field(..., description="List of recommended judges")
    recommendation_basis: str = Field(..., description="Explanation of recommendation basis")

# Helper functions
def get_confidence_level(score: float) -> str:
    """Convert numerical score to confidence level"""
    if score >= 0.8:
        return "High"
    elif score >= 0.6:
        return "Medium"
    elif score >= 0.4:
        return "Low"
    else:
        return "Very Low"

def generate_analysis_summary(outcome_prob: float, duration: float, num_judges: int) -> str:
    """Generate human-readable analysis summary"""
    outcome_desc = "likely to win" if outcome_prob > 0.6 else "unlikely to win" if outcome_prob < 0.4 else "has moderate chances"
    duration_desc = "long" if duration > 4 else "short" if duration < 2 else "moderate"
    
    return f"The plaintiff {outcome_desc} this case. Expected hearing duration is {duration:.1f} hours ({duration_desc}). {num_judges} judges have been recommended based on case characteristics."

# API Endpoints
@router.post("/analyze-case", response_model=CaseAnalysisResponse)
async def analyze_case(
    request: CaseAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete case analysis using all three ML models
    
    This endpoint provides:
    1. Case outcome prediction (plaintiff win probability)
    2. Hearing duration prediction
    3. Judge recommendations based on case characteristics
    """
    try:
        # Get ML service
        ml_service = get_ml_service()
        
        # Perform complete analysis
        result = ml_service.analyze_case(
            facts_text=request.facts_text,
            decision_type=request.decision_type,
            disposition=request.disposition,
            num_parties=request.num_parties,
            num_witnesses=request.num_witnesses,
            evidence_pages=request.evidence_pages,
            adjournments=request.adjournments,
            judge_speed=request.judge_speed,
            lawyer_win_rate=request.lawyer_win_rate,
            case_complexity=request.case_complexity,
            top_judges=request.top_judges
        )
        
        # Generate summary
        summary = generate_analysis_summary(
            result["outcome_probability"],
            result["expected_duration_hours"],
            len(result["recommended_judges"])
        )
        
        # Format response
        return CaseAnalysisResponse(
            outcome_probability=result["outcome_probability"],
            expected_duration_hours=result["expected_duration_hours"],
            recommended_judges=[
                RecommendedJudge(
                    judge_id=judge["judge_id"],
                    similarity_score=judge["similarity_score"]
                )
                for judge in result["recommended_judges"]
            ],
            analysis_summary=summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing case: {str(e)}"
        )

@router.post("/predict-duration", response_model=DurationPredictionResponse)
async def predict_hearing_duration(
    request: DurationPredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Predict hearing duration based on case characteristics
    """
    try:
        # Get ML service
        ml_service = get_ml_service()
        
        # Prepare features
        features = {
            'num_parties': request.num_parties,
            'num_witnesses': request.num_witnesses,
            'evidence_pages': request.evidence_pages,
            'adjournments': request.adjournments,
            'judge_speed': request.judge_speed,
            'lawyer_win_rate': request.lawyer_win_rate
        }
        
        # Predict duration
        duration = ml_service.predict_hearing_duration(features)
        
        # Determine confidence (simplified)
        confidence = "High" if 1.0 <= duration <= 6.0 else "Medium"
        
        return DurationPredictionResponse(
            predicted_duration_hours=round(duration, 2),
            confidence_level=confidence
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting duration: {str(e)}"
        )

@router.post("/predict-outcome", response_model=OutcomePredictionResponse)
async def predict_case_outcome(
    request: OutcomePredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Predict case outcome (plaintiff win probability)
    """
    try:
        # Get ML service
        ml_service = get_ml_service()
        
        # Predict outcome
        outcome_prob = ml_service.predict_judgment(
            request.facts_text,
            request.decision_type,
            request.disposition
        )
        
        # Determine confidence
        confidence = get_confidence_level(abs(outcome_prob - 0.5) * 2)
        
        return OutcomePredictionResponse(
            plaintiff_win_probability=round(outcome_prob, 4),
            prediction_confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting outcome: {str(e)}"
        )

@router.post("/recommend-judges", response_model=JudgeRecommendationResponse)
async def recommend_judges(
    request: JudgeRecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Recommend judges based on case characteristics
    """
    try:
        # Get ML service
        ml_service = get_ml_service()
        
        # Get judge recommendations
        judges_df = ml_service.predict_best_judges(
            request.case_complexity,
            request.expected_duration,
            request.plaintiff_win_prob,
            request.top_judges
        )
        
        # Format recommendations
        recommendations = [
            RecommendedJudge(
                judge_id=int(row["judge_id"]),
                similarity_score=round(row["score"], 4)
            )
            for _, row in judges_df.iterrows()
        ]
        
        # Generate explanation
        basis = f"Recommendations based on case complexity ({request.case_complexity:.2f}), expected duration ({request.expected_duration:.1f}h), and outcome probability ({request.plaintiff_win_prob:.2f}) using cosine similarity matching."
        
        return JudgeRecommendationResponse(
            recommended_judges=recommendations,
            recommendation_basis=basis
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error recommending judges: {str(e)}"
        )

@router.get("/ml-status")
async def get_ml_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get ML service status and model information
    """
    try:
        ml_service = get_ml_service()
        
        return {
            "status": "operational" if ml_service.models_loaded else "error",
            "models_loaded": ml_service.models_loaded,
            "available_endpoints": [
                "/analyze-case - Complete case analysis",
                "/predict-duration - Hearing duration prediction",
                "/predict-outcome - Case outcome prediction",
                "/recommend-judges - Judge recommendations",
                "/predict-settlement - Settlement probability prediction"
            ],
            "model_info": {
                "outcome_model": "XGBoost Classifier",
                "duration_model": "XGBoost Regressor",
                "judge_recommendation": "Cosine Similarity Matching",
                "settlement_prediction": "Trained ML Model (settlement_model.pkl)",
                "preprocessing": "TF-IDF + LDA + Categorical Encoding"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "models_loaded": False
        }

class SettlementPredictionRequest(BaseModel):
    """Request model for settlement probability prediction"""
    case_type: str = Field(..., description="Type of case (e.g., 'Civil', 'Criminal')")
    district: str = Field(..., description="District name (e.g., 'Northern District', 'Southern District')")
    days_to_resolution: int = Field(default=120, ge=0, description="Days to resolution (optional, defaults to 120)")

class SettlementPredictionResponse(BaseModel):
    """Response model for settlement prediction"""
    settlement_probability: float
    settlement_prediction: int
    recommend_mediation: bool
    recommend_early_settlement: bool
    confidence: str
    reasoning: str
    estimated_settlement_days: int
    action_items: list
    settlement_category: str

@router.post("/predict-settlement", response_model=SettlementPredictionResponse)
async def predict_settlement(
    request: SettlementPredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Predict settlement probability using trained ML model
    """
    try:
        ml_service = get_ml_service()
        
        result = ml_service.predict_settlement_probability(
            case_type=request.case_type,
            district=request.district,
            days_to_resolution=request.days_to_resolution
        )
        
        return SettlementPredictionResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting settlement: {str(e)}"
        )
