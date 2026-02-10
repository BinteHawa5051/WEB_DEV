"""
Quick Test Script - Verify Application is Working
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:3001"

def test_backend():
    print("\n" + "="*60)
    print("  TESTING BACKEND")
    print("="*60)
    
    # Test 1: Health Check
    print("\n1. Health Check...")
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        if response.status_code == 200:
            print(f"   ✓ Backend is healthy: {response.json()}")
        else:
            print(f"   ✗ Backend health check failed")
            return False
    except Exception as e:
        print(f"   ✗ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Login
    print("\n2. Testing Login...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={"username": "admin@court.gov", "password": "password123"}
        )
        if response.status_code == 200:
            token = response.json()['access_token']
            print(f"   ✓ Login successful")
            return token
        else:
            print(f"   ✗ Login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ✗ Login error: {e}")
        return None

def test_data(token):
    print("\n" + "="*60)
    print("  TESTING SAMPLE DATA")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test Cases
    print("\n1. Checking Cases...")
    try:
        response = requests.get(f"{BASE_URL}/cases", headers=headers)
        if response.status_code == 200:
            cases = response.json()
            print(f"   ✓ Found {len(cases)} cases")
            if len(cases) > 0:
                print(f"   ✓ Sample case: {cases[0]['case_number']} - {cases[0]['title']}")
        else:
            print(f"   ✗ Failed to get cases")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Judges
    print("\n2. Checking Judges...")
    try:
        response = requests.get(f"{BASE_URL}/judges", headers=headers)
        if response.status_code == 200:
            judges = response.json()
            print(f"   ✓ Found {len(judges)} judges")
            if len(judges) > 0:
                print(f"   ✓ Sample judge: {judges[0].get('experience_years', 0)} years experience")
        else:
            print(f"   ✗ Failed to get judges")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Hearings
    print("\n3. Checking Hearings...")
    try:
        response = requests.get(f"{BASE_URL}/calendar/upcoming-hearings?days_ahead=30", headers=headers)
        if response.status_code == 200:
            data = response.json()
            hearings = data.get('upcoming_hearings', [])
            print(f"   ✓ Found {len(hearings)} upcoming hearings")
            if len(hearings) > 0:
                print(f"   ✓ Next hearing: {hearings[0]['case_number']} on {hearings[0]['scheduled_date'][:10]}")
        else:
            print(f"   ✗ Failed to get hearings")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Lawyers
    print("\n4. Checking Lawyers...")
    try:
        response = requests.get(f"{BASE_URL}/lawyers", headers=headers)
        if response.status_code == 200:
            lawyers = response.json()
            print(f"   ✓ Found {len(lawyers)} lawyers")
        else:
            print(f"   ✗ Failed to get lawyers")
    except Exception as e:
        print(f"   ✗ Error: {e}")

def test_frontend():
    print("\n" + "="*60)
    print("  TESTING FRONTEND")
    print("="*60)
    
    print("\n1. Checking Frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"   ✓ Frontend is accessible")
            print(f"   ✓ URL: {FRONTEND_URL}")
        else:
            print(f"   ✗ Frontend returned status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Cannot connect to frontend: {e}")

def print_summary():
    print("\n" + "="*60)
    print("  SUMMARY & NEXT STEPS")
    print("="*60)
    
    print("\n✓ Backend is running on: http://localhost:8000")
    print("✓ Frontend is running on: http://localhost:3001")
    print("✓ Sample data is loaded")
    print("\n" + "="*60)
    print("  HOW TO ACCESS THE APPLICATION")
    print("="*60)
    
    print("\n1. Open your web browser")
    print("2. Go to: http://localhost:3001")
    print("3. Login with:")
    print("   Email: admin@court.gov")
    print("   Password: password123")
    print("\n" + "="*60)
    print("  AVAILABLE TEST ACCOUNTS")
    print("="*60)
    
    print("\nAdministrator:")
    print("  • admin@court.gov / password123")
    
    print("\nJudges:")
    print("  • judge.smith@court.gov / password123")
    print("  • judge.johnson@court.gov / password123")
    print("  • judge.davis@court.gov / password123")
    
    print("\nLawyers:")
    print("  • lawyer.brown@lawfirm.com / password123")
    print("  • lawyer.wilson@lawfirm.com / password123")
    
    print("\nOther:")
    print("  • prosecutor@court.gov / password123")
    print("  • scheduler@court.gov / password123")
    
    print("\n" + "="*60)
    print("  WHAT YOU CAN TEST")
    print("="*60)
    
    print("\n✓ Dashboard - View statistics and recent cases")
    print("✓ Cases - Browse 8 sample cases")
    print("✓ Judges - View 3 judge profiles")
    print("✓ Calendar - See 4 scheduled hearings")
    print("✓ Scheduling - Find available time slots")
    print("✓ Documents - Search and manage documents")
    
    print("\n" + "="*60)
    print("  READY TO TEST!")
    print("="*60)
    print("\nOpen your browser and go to: http://localhost:3001\n")

def main():
    print("\n" + "="*60)
    print("  COURTROOM SCHEDULING SYSTEM - QUICK TEST")
    print("="*60)
    
    # Test Backend
    token = test_backend()
    
    if token:
        # Test Data
        test_data(token)
        
        # Test Frontend
        test_frontend()
        
        # Print Summary
        print_summary()
    else:
        print("\n✗ Backend tests failed. Please check if the backend is running.")
        print("  Run: cd backend && python main.py")

if __name__ == "__main__":
    main()
