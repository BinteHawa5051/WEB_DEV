"""
ML Service Module for Court Case Analysis
Integrates three AI components:
1. Case Outcome Prediction (XGBoost)
2. Hearing Duration Prediction (XGBoost Regression)
3. Judge Recommendation (Similarity-based Ranking)
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import os
from pathlib import Path

class MLService:
    """
    ML Service for court case predictions and judge recommendations
    """
    
    def __init__(self, models_path: str = "../model_related_things"):
        """
        Initialize ML Service and load all models
        
        Args:
            models_path: Path to directory containing model files
        """
        self.models_path = Path(models_path)
        self.models_loaded = False
        
        # Model placeholders
        self.model_duration = None
        self.model_outcome = None
        self.model_settlement = None
        self.settlement_encoder = None
        self.vectorizer = None
        self.lda = None
        self.categorical_cols = None
        self.judge_vectors = None
        self.judges_df = None
        
        # Load models
        self.load_models()
    
    def load_models(self):
        """Load all ML models and preprocessing objects"""
        try:
            print("Loading ML models...")
            
            # Load duration prediction model
            duration_path = self.models_path / "xgb_model_hearing_duration.pkl"
            self.model_duration = joblib.load(duration_path)
            print(f"✓ Loaded duration prediction model from {duration_path}")
            
            # Load outcome prediction model
            outcome_path = self.models_path / "xgboost_model.joblib"
            self.model_outcome = joblib.load(outcome_path)
            print(f"✓ Loaded outcome prediction model from {outcome_path}")
            
            # Load preprocessing objects
            vectorizer_path = self.models_path / "vectorizer.pkl"
            self.vectorizer = joblib.load(vectorizer_path)
            print(f"✓ Loaded vectorizer from {vectorizer_path}")
            
            lda_path = self.models_path / "lda_model.pkl"
            self.lda = joblib.load(lda_path)
            print(f"✓ Loaded LDA model from {lda_path}")
            
            cat_cols_path = self.models_path / "categorical_columns.pkl"
            self.categorical_cols = joblib.load(cat_cols_path)
            print(f"✓ Loaded categorical columns from {cat_cols_path}")
            
            # Load judge data
            judge_vectors_path = self.models_path / "judge_vectors.npy"
            self.judge_vectors = np.load(judge_vectors_path)
            print(f"✓ Loaded judge vectors from {judge_vectors_path}")
            
            judges_csv_path = self.models_path / "judges_dataset.csv"
            self.judges_df = pd.read_csv(judges_csv_path)
            print(f"✓ Loaded judges dataset from {judges_csv_path}")
            
            # Load settlement prediction model
            settlement_path = self.models_path / "settlement_model.pkl"
            self.model_settlement = joblib.load(settlement_path)
            print(f"✓ Loaded settlement prediction model from {settlement_path}")
            
            settlement_encoder_path = self.models_path / "encoder.pkl"
            self.settlement_encoder = joblib.load(settlement_encoder_path)
            print(f"✓ Loaded settlement encoder from {settlement_encoder_path}")
            
            self.models_loaded = True
            print("✅ All ML models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading ML models: {e}")
            raise
    
    def simple_preprocess(self, text: str) -> str:
        """
        Simple text preprocessing
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        return text.lower().strip()
    
    def predict_hearing_duration(self, features_dict: dict) -> float:
        """
        Predict hearing duration based on case features
        
        Args:
            features_dict: Dictionary containing:
                - num_parties: Number of parties involved
                - num_witnesses: Number of witnesses
                - evidence_pages: Number of evidence pages
                - adjournments: Number of previous adjournments
                - judge_speed: Judge's average speed (1.0 = normal)
                - lawyer_win_rate: Lawyer's historical win rate (0-1)
        
        Returns:
            Predicted hearing duration in hours
        """
        if not self.models_loaded:
            raise RuntimeError("ML models not loaded")
        
        try:
            # Convert to DataFrame
            input_df = pd.DataFrame([features_dict])
            
            # Predict
            duration = self.model_duration.predict(input_df)[0]
            
            return float(duration)
            
        except Exception as e:
            print(f"Error predicting hearing duration: {e}")
            raise
    
    def predict_judgment(self, facts_text: str, decision_type: str, disposition: str) -> float:
        """
        Predict case outcome (probability that first party/plaintiff wins)
        
        Args:
            facts_text: Case facts description
            decision_type: Type of decision (e.g., "majority opinion")
            disposition: Case disposition (e.g., "affirmed", "reversed")
        
        Returns:
            Probability that first party wins (0-1)
        """
        if not self.models_loaded:
            raise RuntimeError("ML models not loaded")
        
        try:
            # Preprocess text
            cleaned = self.simple_preprocess(facts_text)
            
            # Vectorize text
            facts_vec = self.vectorizer.transform([cleaned]).toarray()
            
            # Create categorical features DataFrame
            cat_df = pd.DataFrame(
                0,
                index=[0],
                columns=[c for c in self.categorical_cols if c != 'first_party_winner']
            )
            
            # Set categorical features
            if decision_type in cat_df.columns:
                cat_df.loc[0, decision_type] = 1
            
            if disposition in cat_df.columns:
                cat_df.loc[0, disposition] = 1
            
            # Combine features
            combined = np.hstack((facts_vec, cat_df.to_numpy()))
            
            # Apply LDA transformation
            lda_input = self.lda.transform(combined)
            
            # Predict
            pred = self.model_outcome.predict(lda_input)[0]
            
            return float(pred)
            
        except Exception as e:
            print(f"Error predicting judgment: {e}")
            raise
    
    def predict_best_judges(
        self, 
        case_complexity: float, 
        expected_duration: float, 
        plaintiff_win_prob: float, 
        top_n: int = 3
    ) -> pd.DataFrame:
        """
        Recommend best judges for a case based on similarity matching
        
        Args:
            case_complexity: Case complexity score (0-1)
            expected_duration: Expected hearing duration in hours
            plaintiff_win_prob: Predicted plaintiff win probability (0-1)
            top_n: Number of top judges to return
        
        Returns:
            DataFrame with judge_id and similarity scores
        """
        if not self.models_loaded:
            raise RuntimeError("ML models not loaded")
        
        try:
            # Create case feature vector
            case_vec = np.array([[
                case_complexity,
                expected_duration / 50.0,  # Normalize duration
                plaintiff_win_prob
            ]])
            
            # Calculate cosine similarity with all judges
            similarities = cosine_similarity(case_vec, self.judge_vectors)
            
            # Add scores to judges dataframe
            judges_copy = self.judges_df.copy()
            judges_copy["score"] = similarities[0]
            
            # Sort by score and get top N
            ranked = judges_copy.sort_values("score", ascending=False)
            
            return ranked.head(top_n)[["judge_id", "score"]]
            
        except Exception as e:
            print(f"Error predicting best judges: {e}")
            raise
    
    def analyze_case(
        self,
        facts_text: str,
        decision_type: str,
        disposition: str,
        num_parties: int,
        num_witnesses: int,
        evidence_pages: int,
        adjournments: int,
        judge_speed: float,
        lawyer_win_rate: float,
        case_complexity: float,
        top_judges: int = 3
    ) -> dict:
        """
        Complete case analysis pipeline
        
        Args:
            facts_text: Case facts description
            decision_type: Type of decision
            disposition: Case disposition
            num_parties: Number of parties
            num_witnesses: Number of witnesses
            evidence_pages: Number of evidence pages
            adjournments: Number of adjournments
            judge_speed: Judge speed factor
            lawyer_win_rate: Lawyer win rate
            case_complexity: Case complexity score
            top_judges: Number of judges to recommend
        
        Returns:
            Dictionary containing:
                - outcome_probability: Predicted plaintiff win probability
                - expected_duration: Predicted hearing duration
                - recommended_judges: List of recommended judges with scores
        """
        # Step 1: Predict outcome
        outcome_prob = self.predict_judgment(facts_text, decision_type, disposition)
        
        # Step 2: Predict duration
        duration_features = {
            'num_parties': num_parties,
            'num_witnesses': num_witnesses,
            'evidence_pages': evidence_pages,
            'adjournments': adjournments,
            'judge_speed': judge_speed,
            'lawyer_win_rate': lawyer_win_rate
        }
        expected_duration = self.predict_hearing_duration(duration_features)
        
        # Step 3: Recommend judges
        judges_ranked = self.predict_best_judges(
            case_complexity,
            expected_duration,
            outcome_prob,
            top_judges
        )
        
        # Format results
        return {
            "outcome_probability": round(outcome_prob, 4),
            "expected_duration_hours": round(expected_duration, 2),
            "recommended_judges": [
                {
                    "judge_id": int(row["judge_id"]),
                    "similarity_score": round(row["score"], 4)
                }
                for _, row in judges_ranked.iterrows()
            ]
        }
    
    def predict_settlement_probability(
        self,
        case_type: str,
        district: str,
        days_to_resolution: int = None
    ) -> dict:
        """
        Predict settlement probability using trained ML model
        
        Args:
            case_type: Type of case (e.g., 'Civil', 'Criminal')
            district: District name (e.g., 'Northern District', 'Southern District')
            days_to_resolution: Days to resolution (optional, defaults to 120)
            
        Returns:
            dict: Settlement analysis with probability and prediction
        """
        if not self.models_loaded:
            raise RuntimeError("ML models not loaded")
        
        try:
            # Default days_to_resolution if not provided
            if days_to_resolution is None:
                days_to_resolution = 120
            
            # Create case data DataFrame
            case_data = {
                'Case_Type': case_type,
                'District': district,
                'Days_to_Resolution': days_to_resolution
            }
            df = pd.DataFrame([case_data])
            
            # Encode categorical features
            cat_cols = ['Case_Type', 'District']
            encoded_cat = self.settlement_encoder.transform(df[cat_cols])
            
            # Create numeric features
            df['num_parties'] = 2  # Default value
            df['complexity'] = df['Days_to_Resolution'].fillna(0)
            df['case_age_days'] = df['Days_to_Resolution'].fillna(0)
            num_features = df[['num_parties', 'complexity', 'case_age_days']].values
            
            # Combine features
            X = np.hstack([encoded_cat, num_features])
            
            # Predict
            settlement_prob = self.model_settlement.predict_proba(X)[0][1]
            settlement_pred = self.model_settlement.predict(X)[0]
            
            # Generate recommendations based on probability
            recommend_mediation = settlement_prob > 0.6
            recommend_early_settlement = settlement_prob > 0.7
            
            # Calculate confidence
            if settlement_prob < 0.3 or settlement_prob > 0.7:
                confidence = "High"
            elif 0.35 < settlement_prob < 0.65:
                confidence = "Medium"
            else:
                confidence = "Low"
            
            # Estimate settlement timeline
            if settlement_prob > 0.7:
                estimated_days = 30 + int(days_to_resolution * 0.2)
            elif settlement_prob > 0.5:
                estimated_days = 45 + int(days_to_resolution * 0.3)
            else:
                estimated_days = 60 + int(days_to_resolution * 0.4)
            
            # Generate action items
            action_items = []
            if recommend_mediation:
                action_items.append("Schedule mediation session")
                action_items.append("Prepare settlement proposal")
            if recommend_early_settlement:
                action_items.append("Consider early settlement conference")
                action_items.append("Evaluate cost-benefit of trial vs settlement")
            if settlement_prob < 0.4:
                action_items.append("Prepare for trial")
                action_items.append("Focus on evidence gathering")
            
            # Generate reasoning
            reasons = []
            if settlement_prob > 0.7:
                reasons.append("High settlement probability based on case characteristics")
            elif settlement_prob > 0.5:
                reasons.append("Moderate settlement likelihood")
            else:
                reasons.append("Low settlement probability, trial likely")
            
            reasons.append(f"Case type: {case_type}")
            reasons.append(f"District: {district}")
            
            return {
                "settlement_probability": round(float(settlement_prob), 4),
                "settlement_prediction": int(settlement_pred),
                "recommend_mediation": recommend_mediation,
                "recommend_early_settlement": recommend_early_settlement,
                "confidence": confidence,
                "reasoning": "; ".join(reasons),
                "estimated_settlement_days": estimated_days,
                "action_items": action_items,
                "settlement_category": (
                    "Highly Likely" if settlement_prob > 0.7 else
                    "Likely" if settlement_prob > 0.55 else
                    "Possible" if settlement_prob > 0.4 else
                    "Unlikely"
                )
            }
            
        except Exception as e:
            print(f"Error in settlement prediction: {e}")
            raise


# Global ML service instance
ml_service = None

def get_ml_service() -> MLService:
    """
    Get or create ML service instance (singleton pattern)
    
    Returns:
        MLService instance
    """
    global ml_service
    if ml_service is None:
        ml_service = MLService()
    return ml_service


# Test function
if __name__ == "__main__":
    print("Testing ML Service...")
    
    # Initialize service
    service = MLService()
    
    # Test data
    case_data = {
        'num_parties': 4,
        'num_witnesses': 5,
        'evidence_pages': 120,
        'adjournments': 2,
        'judge_speed': 1.0,
        'lawyer_win_rate': 0.75
    }
    
    facts = "Contract dispute regarding delayed delivery of goods."
    
    # Test predictions
    duration = service.predict_hearing_duration(case_data)
    outcome = service.predict_judgment(facts, "majority opinion", "affirmed")
    judges_ranked = service.predict_best_judges(0.7, duration, outcome)
    
    print(f"\nDuration: {duration:.2f} hours")
    print(f"Outcome Probability: {outcome:.4f}")
    print(f"Recommended Judges:")
    print(judges_ranked)
    
    # Test complete pipeline
    print("\n" + "="*60)
    print("Testing Complete Pipeline:")
    print("="*60)
    
    result = service.analyze_case(
        facts_text=facts,
        decision_type="majority opinion",
        disposition="affirmed",
        num_parties=4,
        num_witnesses=5,
        evidence_pages=120,
        adjournments=2,
        judge_speed=1.0,
        lawyer_win_rate=0.75,
        case_complexity=0.7,
        top_judges=3
    )
    
    print(f"\nComplete Analysis Result:")
    print(f"  Outcome Probability: {result['outcome_probability']}")
    print(f"  Expected Duration: {result['expected_duration_hours']} hours")
    print(f"  Recommended Judges: {result['recommended_judges']}")
    
    print("\n✅ ML Service test completed successfully!")
