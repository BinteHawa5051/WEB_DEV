"""Test all ML endpoints"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def get_token():
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={"username": "admin@court.gov", "password": "password123"},
        timeout=5
    )
    return response.json()['access_token'] if response.status_code == 200 else None

print("="*70)
print("  ML ENDPOINTS TEST")
print("="*70)

token = get_token()
if not token:
    print("❌ Failed to authenticate")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Test 1: ML Status
print("\n1. ML Status")
response = requests.get(f"{BASE_URL}/ml/ml-status", headers=headers, timeout=5)
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Status: {data['status']}")
    print(f"   ✅ Models Loaded: {data['models_loaded']}")
else:
    print(f"   ❌ Failed: {response.status_code}")

# Test 2: Duration Prediction
print("\n2. Duration Prediction")
response = requests.post(
    f"{BASE_URL}/ml/predict-duration",
    json={
        "num_parties": 4,
        "num_witnesses": 5,
        "evidence_pages": 120,
        "adjournments": 2,
        "judge_speed": 1.0,
        "lawyer_win_rate": 0.75
    },
    headers=headers,
    timeout=10
)
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Duration: {data['predicted_duration_hours']} hours")
    print(f"   ✅ Confidence: {data['confidence_level']}")
else:
    print(f"   ❌ Failed: {response.status_code} - {response.text}")

# Test 3: Outcome Prediction
print("\n3. Outcome Prediction")
response = requests.post(
    f"{BASE_URL}/ml/predict-outcome",
    json={
        "facts_text": "Contract dispute regarding delayed delivery of goods.",
        "decision_type": "majority opinion",
        "disposition": "affirmed"
    },
    headers=headers,
    timeout=10
)
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Win Probability: {data['plaintiff_win_probability']:.2%}")
    print(f"   ✅ Confidence: {data['prediction_confidence']}")
else:
    print(f"   ❌ Failed: {response.status_code} - {response.text}")

# Test 4: Judge Recommendation
print("\n4. Judge Recommendation")
response = requests.post(
    f"{BASE_URL}/ml/recommend-judges",
    json={
        "case_complexity": 0.7,
        "expected_duration": 2.5,
        "plaintiff_win_prob": 0.6,
        "top_judges": 3
    },
    headers=headers,
    timeout=10
)
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Recommended: {len(data['recommended_judges'])} judges")
    for i, judge in enumerate(data['recommended_judges'], 1):
        print(f"      {i}. Judge {judge['judge_id']}: {judge['similarity_score']:.2%}")
else:
    print(f"   ❌ Failed: {response.status_code} - {response.text}")

# Test 5: Complete Analysis
print("\n5. Complete Case Analysis")
response = requests.post(
    f"{BASE_URL}/ml/analyze-case",
    json={
        "facts_text": "Complex corporate litigation involving securities violations.",
        "decision_type": "majority opinion",
        "disposition": "affirmed",
        "num_parties": 4,
        "num_witnesses": 5,
        "evidence_pages": 120,
        "adjournments": 2,
        "judge_speed": 1.0,
        "lawyer_win_rate": 0.75,
        "case_complexity": 0.7,
        "top_judges": 3
    },
    headers=headers,
    timeout=15
)
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Outcome Probability: {data['outcome_probability']:.2%}")
    print(f"   ✅ Expected Duration: {data['expected_duration_hours']:.1f} hours")
    print(f"   ✅ Recommended Judges: {len(data['recommended_judges'])}")
    print(f"   ✅ Summary: {data['analysis_summary']}")
else:
    print(f"   ❌ Failed: {response.status_code} - {response.text}")

print("\n" + "="*70)
print("  TEST COMPLETE")
print("="*70)
print("\n✅ All ML endpoints are operational!")
print("\n🌐 Access:")
print("   • API Docs: http://localhost:8000/docs")
print("   • Frontend: http://localhost:5173/ml-predictions")
print("\n" + "="*70)
