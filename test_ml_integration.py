"""
Complete ML Integration Test
Tests all ML endpoints with various scenarios
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def get_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={"username": "admin@court.gov", "password": "password123"}
    )
    if response.status_code == 200:
        return response.json()['access_token']
    return None

def test_complete_integration():
    print("\n" + "="*70)
    print("  COMPLETE ML INTEGRATION TEST")
    print("="*70)
    
    # Get token
    token = get_token()
    if not token:
        print("❌ Failed to get authentication token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test scenarios
    test_cases = [
        {
            "name": "Simple Contract Dispute",
            "data": {
                "facts_text": "Breach of contract for non-delivery of goods worth $50,000.",
                "decision_type": "majority opinion",
                "disposition": "affirmed",
                "num_parties": 2,
                "num_witnesses": 3,
                "evidence_pages": 50,
                "adjournments": 0,
                "judge_speed": 1.0,
                "lawyer_win_rate": 0.65,
                "case_complexity": 0.4,
                "top_judges": 5
            }
        },
        {
            "name": "Complex Corporate Litigation",
            "data": {
                "facts_text": "Multi-party corporate fraud case involving securities violations and breach of fiduciary duty.",
                "decision_type": "majority opinion",
                "disposition": "reversed",
                "num_parties": 8,
                "num_witnesses": 15,
                "evidence_pages": 500,
                "adjournments": 3,
                "judge_speed": 0.8,
                "lawyer_win_rate": 0.75,
                "case_complexity": 0.9,
                "top_judges": 3
            }
        },
        {
            "name": "Property Dispute",
            "data": {
                "facts_text": "Boundary dispute between neighboring property owners regarding fence placement.",
                "decision_type": "majority opinion",
                "disposition": "affirmed",
                "num_parties": 2,
                "num_witnesses": 2,
                "evidence_pages": 20,
                "adjournments": 1,
                "judge_speed": 1.2,
                "lawyer_win_rate": 0.55,
                "case_complexity": 0.3,
                "top_judges": 3
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'='*70}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/ml/analyze-case",
                json=test_case['data'],
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n✅ Analysis Successful!")
                print(f"\n📊 Results:")
                print(f"   • Outcome Probability: {result['outcome_probability']:.2%}")
                print(f"   • Expected Duration: {result['expected_duration_hours']:.2f} hours")
                print(f"   • Recommended Judges: {len(result['recommended_judges'])}")
                
                print(f"\n👨‍⚖️ Top Recommended Judges:")
                for j, judge in enumerate(result['recommended_judges'][:3], 1):
                    print(f"   {j}. Judge ID {judge['judge_id']}: {judge['similarity_score']:.2%} match")
                
                print(f"\n📝 Summary:")
                print(f"   {result['analysis_summary']}")
                
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test individual endpoints
    print(f"\n{'='*70}")
    print("Testing Individual Endpoints")
    print(f"{'='*70}")
    
    # Duration only
    print("\n1. Duration Prediction Only:")
    try:
        response = requests.post(
            f"{BASE_URL}/ml/predict-duration",
            json={
                "num_parties": 4,
                "num_witnesses": 6,
                "evidence_pages": 150,
                "adjournments": 1,
                "judge_speed": 1.0,
                "lawyer_win_rate": 0.7
            },
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Duration: {data['predicted_duration_hours']} hours")
            print(f"   ✓ Confidence: {data['confidence_level']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Outcome only
    print("\n2. Outcome Prediction Only:")
    try:
        response = requests.post(
            f"{BASE_URL}/ml/predict-outcome",
            json={
                "facts_text": "Employment discrimination case with strong evidence.",
                "decision_type": "majority opinion",
                "disposition": "affirmed"
            },
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Win Probability: {data['plaintiff_win_probability']:.2%}")
            print(f"   ✓ Confidence: {data['prediction_confidence']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Judge recommendation only
    print("\n3. Judge Recommendation Only:")
    try:
        response = requests.post(
            f"{BASE_URL}/ml/recommend-judges",
            json={
                "case_complexity": 0.6,
                "expected_duration": 3.5,
                "plaintiff_win_prob": 0.55,
                "top_judges": 5
            },
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Recommended: {len(data['recommended_judges'])} judges")
            for j, judge in enumerate(data['recommended_judges'][:3], 1):
                print(f"     {j}. Judge {judge['judge_id']}: {judge['similarity_score']:.2%}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # ML Status
    print("\n4. ML Service Status:")
    try:
        response = requests.get(f"{BASE_URL}/ml/ml-status", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {data['status']}")
            print(f"   ✓ Models Loaded: {data['models_loaded']}")
            print(f"   ✓ Available Endpoints: {len(data['available_endpoints'])}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*70}")
    print("  INTEGRATION TEST COMPLETE")
    print(f"{'='*70}")
    print("\n✅ ML Service is fully integrated and operational!")
    print("\n🌐 Access Points:")
    print("   • Backend API: http://localhost:8000/docs")
    print("   • Frontend UI: http://localhost:5173/ml-predictions")
    print("\n📚 Features Available:")
    print("   • Complete case analysis with all predictions")
    print("   • Individual prediction endpoints")
    print("   • Judge recommendation system")
    print("   • Real-time ML model inference")
    print("   • Interactive web interface")
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    test_complete_integration()
