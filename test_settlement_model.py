"""
Test script for Settlement Probability Model
Tests the newly integrated settlement_model.pkl
"""

import requests
import json

# API Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/token"
SETTLEMENT_URL = f"{BASE_URL}/api/ml/predict-settlement"

def login():
    """Login and get access token"""
    print("🔐 Logging in...")
    response = requests.post(
        LOGIN_URL,
        data={
            "username": "admin@court.gov",
            "password": "password123"
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_settlement_prediction(token):
    """Test settlement probability prediction"""
    print("\n" + "="*60)
    print("Testing Settlement Probability Prediction")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "name": "Civil Case - Northern District",
            "data": {
                "case_type": "Civil",
                "district": "Northern District",
                "days_to_resolution": 120
            }
        },
        {
            "name": "Criminal Case - Southern District",
            "data": {
                "case_type": "Criminal",
                "district": "Southern District",
                "days_to_resolution": 180
            }
        },
        {
            "name": "Family Case - Eastern District",
            "data": {
                "case_type": "Family",
                "district": "Eastern District",
                "days_to_resolution": 90
            }
        },
        {
            "name": "Tax Case - Western District",
            "data": {
                "case_type": "Tax",
                "district": "Western District",
                "days_to_resolution": 150
            }
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        print(f"   Input: {test_case['data']}")
        
        try:
            response = requests.post(
                SETTLEMENT_URL,
                headers=headers,
                json=test_case['data']
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"   Settlement Probability: {result['settlement_probability']:.2%}")
                print(f"   Settlement Prediction: {result['settlement_prediction']}")
                print(f"   Category: {result['settlement_category']}")
                print(f"   Confidence: {result['confidence']}")
                print(f"   Recommend Mediation: {result['recommend_mediation']}")
                print(f"   Recommend Early Settlement: {result['recommend_early_settlement']}")
                print(f"   Estimated Days: {result['estimated_settlement_days']}")
                print(f"   Reasoning: {result['reasoning']}")
                if result['action_items']:
                    print(f"   Action Items:")
                    for item in result['action_items']:
                        print(f"     - {item}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

def main():
    """Main test function"""
    print("="*60)
    print("Settlement Model Integration Test")
    print("="*60)
    
    # Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Test settlement prediction
    test_settlement_prediction(token)
    
    print("\n" + "="*60)
    print("✅ Settlement Model Test Complete!")
    print("="*60)

if __name__ == "__main__":
    main()
