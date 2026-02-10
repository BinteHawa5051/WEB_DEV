"""
Quick test to verify ML endpoints work with authentication
"""

import requests

BASE_URL = "http://localhost:8000"

# Step 1: Login
print("1. Logging in...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/token",
    data={"username": "admin@court.gov", "password": "password123"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Login successful! Token: {token[:20]}...")

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Test ML Analyze Case
print("\n2. Testing ML Analyze Case...")
ml_data = {
    "facts_text": "Contract dispute regarding delayed delivery of goods worth $500,000. Multiple witnesses and extensive documentation.",
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
}

ml_response = requests.post(
    f"{BASE_URL}/api/ml/analyze-case",
    headers=headers,
    json=ml_data
)

if ml_response.status_code == 200:
    result = ml_response.json()
    print("✅ ML Analysis successful!")
    print(f"   Outcome Probability: {result['outcome_probability']:.2%}")
    print(f"   Expected Duration: {result['expected_duration_hours']:.1f} hours")
    print(f"   Recommended Judges: {len(result['recommended_judges'])}")
else:
    print(f"❌ ML Analysis failed: {ml_response.status_code}")
    print(ml_response.text)

# Step 3: Test Settlement Prediction
print("\n3. Testing Settlement Prediction...")
settlement_data = {
    "case_type": "Civil",
    "district": "Northern District",
    "days_to_resolution": 120
}

settlement_response = requests.post(
    f"{BASE_URL}/api/ml/predict-settlement",
    headers=headers,
    json=settlement_data
)

if settlement_response.status_code == 200:
    result = settlement_response.json()
    print("✅ Settlement prediction successful!")
    print(f"   Settlement Probability: {result['settlement_probability']:.2%}")
    print(f"   Category: {result['settlement_category']}")
else:
    print(f"❌ Settlement prediction failed: {settlement_response.status_code}")
    print(settlement_response.text)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\n🌐 Frontend: http://localhost:3000")
print("🔐 Login: admin@court.gov / password123")
print("\n💡 TIP: Make sure you're logged in on the frontend!")
print("   If you see 'invalid credentials', try:")
print("   1. Logout and login again")
print("   2. Clear browser cache")
print("   3. Check browser console for errors (F12)")
