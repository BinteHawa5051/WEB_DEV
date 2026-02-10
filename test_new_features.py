"""
Test script for newly implemented features
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def login():
    """Login and get token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/auth/token",
        data={"username": "admin@court.gov", "password": "password123"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful!\n")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

def test_complexity_calculation(token):
    """Test case complexity auto-calculation"""
    print("="*60)
    print("Testing Case Complexity Auto-calculation")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    test_cases = [
        {
            "name": "Simple Civil Case",
            "params": {
                "num_parties": 2,
                "num_witnesses": 2,
                "evidence_pages": 30,
                "case_type": "civil"
            }
        },
        {
            "name": "Complex Criminal Case",
            "params": {
                "num_parties": 8,
                "num_witnesses": 15,
                "evidence_pages": 800,
                "case_type": "criminal"
            }
        },
        {
            "name": "Constitutional Case",
            "params": {
                "num_parties": 5,
                "num_witnesses": 10,
                "evidence_pages": 500,
                "case_type": "constitutional"
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n📋 {test['name']}")
        print(f"   Input: {test['params']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/cases/calculate-complexity",
                headers=headers,
                params=test['params']
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Complexity Score: {result['complexity_score']}/10")
                print(f"   Recommendation: {result['recommendation']}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

def test_workload_analysis(token):
    """Test judge workload analysis"""
    print("\n" + "="*60)
    print("Testing Judge Workload Analysis")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/judges/workload-analysis",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Analysis Complete!")
            print(f"   Total Judges: {result['total_judges']}")
            print(f"   Available: {result['available_judges']}")
            print(f"   Average Workload: {result['workload_stats']['average']}%")
            print(f"   Balance Score: {result['balance_score']}/100")
            print(f"   Overloaded Judges: {len(result['overloaded_judges'])}")
            print(f"   Needs Rebalancing: {result['needs_rebalancing']}")
            
            if result['suggestions']:
                print(f"\n   📊 Rebalancing Suggestions:")
                for i, sug in enumerate(result['suggestions'][:3], 1):
                    print(f"      {i}. Transfer {sug['suggested_cases_count']} cases")
                    print(f"         From: {sug['from_judge']}")
                    print(f"         To: {sug['to_judge']}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_settlement_prediction(token):
    """Test settlement probability prediction"""
    print("\n" + "="*60)
    print("Testing Settlement Probability (Quick Test)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    test_data = {
        "case_type": "Civil",
        "district": "Northern District",
        "days_to_resolution": 120
    }
    
    print(f"\n📋 Input: {test_data}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ml/predict-settlement",
            headers=headers,
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Settlement Probability: {result['settlement_probability']:.2%}")
            print(f"   Category: {result['settlement_category']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Recommend Mediation: {result['recommend_mediation']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

def test_ml_status(token):
    """Test ML service status"""
    print("\n" + "="*60)
    print("Testing ML Service Status")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/ml/ml-status",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ ML Service Status: {result['status']}")
            print(f"   Models Loaded: {result['models_loaded']}")
            print(f"\n   Available Models:")
            for model, desc in result['model_info'].items():
                print(f"      • {model}: {desc}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def main():
    """Main test function"""
    print("="*60)
    print("NEW FEATURES TEST SUITE")
    print("="*60)
    print()
    
    # Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Run tests
    test_complexity_calculation(token)
    test_workload_analysis(token)
    test_settlement_prediction(token)
    test_ml_status(token)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETE!")
    print("="*60)
    print("\n📱 Frontend is running at: http://localhost:3000")
    print("🔧 Backend is running at: http://localhost:8000")
    print("\n🎯 You can now test the UI features:")
    print("   1. Login with: admin@court.gov / password123")
    print("   2. Check Dashboard - AI/ML section updated")
    print("   3. Check Cases - Public Interest Score column")
    print("   4. Check Calendar - Capacity indicators & filters")
    print("   5. Check Judges - Workload analysis section")
    print("   6. Check ML Predictions - Settlement prediction form")
    print("   7. Check Case Detail - Connected cases section")

if __name__ == "__main__":
    main()
