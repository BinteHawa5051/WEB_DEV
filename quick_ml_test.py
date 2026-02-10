"""Quick ML endpoint test"""
import requests

BASE_URL = "http://localhost:8000/api"

# Get token
response = requests.post(
    f"{BASE_URL}/auth/token",
    data={"username": "admin@court.gov", "password": "password123"},
    timeout=5
)
print(f"Auth: {response.status_code}")

if response.status_code == 200:
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test ML status
    print("\nTesting ML Status...")
    response = requests.get(f"{BASE_URL}/ml/ml-status", headers=headers, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test duration prediction
    print("\nTesting Duration Prediction...")
    response = requests.post(
        f"{BASE_URL}/ml/predict-duration",
        json={
            "num_parties": 2,
            "num_witnesses": 3,
            "evidence_pages": 50,
            "adjournments": 0,
            "judge_speed": 1.0,
            "lawyer_win_rate": 0.65
        },
        headers=headers,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Duration: {response.json()}")
    else:
        print(f"❌ Error: {response.text}")
