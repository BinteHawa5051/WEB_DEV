import requests
import json

BASE_URL = "http://localhost:8000/api"

print("\n" + "="*60)
print("  TESTING COURTROOM SCHEDULING ENDPOINTS")
print("="*60 + "\n")

# Test 1: Health Check
print("1. Testing Health Check...")
try:
    response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
    if response.status_code == 200:
        print(f"   PASS - Health check: {response.json()}")
    else:
        print(f"   FAIL - Status: {response.status_code}")
except Exception as e:
    print(f"   ERROR - {e}")

# Test 2: Register User
print("\n2. Testing User Registration...")
user_data = {
    "email": "admin@court.gov",
    "password": "password123",
    "full_name": "Admin User",
    "role": "court_administrator"
}
try:
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code == 200:
        print(f"   PASS - User registered: {response.json()['email']}")
    elif response.status_code == 400:
        print(f"   INFO - User already exists")
    else:
        print(f"   FAIL - Status: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ERROR - {e}")

# Test 3: Login
print("\n3. Testing Login...")
try:
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={"username": "admin@court.gov", "password": "password123"}
    )
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"   PASS - Login successful, token: {token[:20]}...")
    else:
        print(f"   FAIL - Status: {response.status_code}")
        print(f"   Response: {response.text}")
        token = None
except Exception as e:
    print(f"   ERROR - {e}")
    token = None

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 4: Get Current User
    print("\n4. Testing Get Current User...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"   PASS - User: {user['full_name']} ({user['role']})")
        else:
            print(f"   FAIL - Status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR - {e}")
    
    # Test 4.5: Create Court (needed for cases)
    print("\n4.5 Creating Court...")
    court_data = {
        "name": "District Court Central",
        "level": "district_court",
        "jurisdiction": "civil",
        "location": "Downtown"
    }
    try:
        # Note: We need to add a court creation endpoint or use SQL
        # For now, let's create it directly via SQL
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="tooba@123",
            database="DEV_WEB"
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO courts (name, level, jurisdiction, location, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON CONFLICT DO NOTHING
            RETURNING id
        """, (court_data['name'], court_data['level'], court_data['jurisdiction'], court_data['location'], True))
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        print(f"   PASS - Court created")
    except Exception as e:
        print(f"   INFO - Court may already exist: {e}")
    
    # Test 5: Create Case
    print("\n5. Testing Create Case...")
    case_data = {
        "title": "Test Case - Property Dispute",
        "court_id": 1,
        "jurisdiction": "civil",
        "case_type": "Property",
        "urgency_level": "regular",
        "complexity_score": 5,
        "public_interest_score": 3,
        "estimated_duration_hours": 2.5,
        "description": "Test case for endpoint testing"
    }
    try:
        response = requests.post(f"{BASE_URL}/cases", json=case_data, headers=headers)
        if response.status_code == 200:
            case = response.json()
            print(f"   PASS - Case created: {case['case_number']}")
            case_id = case['id']
        else:
            print(f"   FAIL - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            case_id = None
    except Exception as e:
        print(f"   ERROR - {e}")
        case_id = None
    
    # Test 6: Get Cases
    print("\n6. Testing Get Cases...")
    try:
        response = requests.get(f"{BASE_URL}/cases", headers=headers)
        if response.status_code == 200:
            cases = response.json()
            print(f"   PASS - Retrieved {len(cases)} cases")
        else:
            print(f"   FAIL - Status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR - {e}")
    
    # Test 7: Get Judges
    print("\n7. Testing Get Judges...")
    try:
        response = requests.get(f"{BASE_URL}/judges", headers=headers)
        if response.status_code == 200:
            judges = response.json()
            print(f"   PASS - Retrieved {len(judges)} judges")
        else:
            print(f"   FAIL - Status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR - {e}")
    
    # Test 8: Calendar Week View
    print("\n8. Testing Calendar Week View...")
    try:
        from datetime import datetime, timedelta
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start_str = week_start.strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{BASE_URL}/calendar/week-view",
            params={"week_start": week_start_str},
            headers=headers
        )
        if response.status_code == 200:
            print(f"   PASS - Calendar week view retrieved")
        else:
            print(f"   FAIL - Status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR - {e}")
    
    # Test 9: Upcoming Hearings
    print("\n9. Testing Upcoming Hearings...")
    try:
        response = requests.get(
            f"{BASE_URL}/calendar/upcoming-hearings",
            params={"days_ahead": 7},
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   PASS - Retrieved {len(data.get('upcoming_hearings', []))} upcoming hearings")
        else:
            print(f"   FAIL - Status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR - {e}")

print("\n" + "="*60)
print("  TESTING COMPLETE")
print("="*60 + "\n")
