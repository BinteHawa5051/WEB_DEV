"""
Populate Sample Data for Courtroom Scheduling System
This script creates realistic test data for demonstration and testing
"""

import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000/api"

# Sample data
COURTS = [
    {
        "name": "Supreme Court of Justice",
        "level": "supreme_court",
        "jurisdiction": "constitutional",
        "location": "Capital City, Main Building"
    },
    {
        "name": "High Court - Civil Division",
        "level": "high_court",
        "jurisdiction": "civil",
        "location": "Downtown, Court Complex"
    },
    {
        "name": "District Court Central",
        "level": "district_court",
        "jurisdiction": "criminal",
        "location": "Central District, Justice Plaza"
    },
    {
        "name": "District Court North",
        "level": "district_court",
        "jurisdiction": "family",
        "location": "North District, Family Court Building"
    }
]

USERS = [
    {
        "email": "admin@court.gov",
        "password": "password123",
        "full_name": "Admin User",
        "role": "court_administrator"
    },
    {
        "email": "chief.justice@court.gov",
        "password": "password123",
        "full_name": "Chief Justice Williams",
        "role": "chief_justice"
    },
    {
        "email": "judge.smith@court.gov",
        "password": "password123",
        "full_name": "Judge Robert Smith",
        "role": "presiding_judge"
    },
    {
        "email": "judge.johnson@court.gov",
        "password": "password123",
        "full_name": "Judge Sarah Johnson",
        "role": "presiding_judge"
    },
    {
        "email": "judge.davis@court.gov",
        "password": "password123",
        "full_name": "Judge Michael Davis",
        "role": "presiding_judge"
    },
    {
        "email": "lawyer.brown@lawfirm.com",
        "password": "password123",
        "full_name": "Attorney Jennifer Brown",
        "role": "lawyer"
    },
    {
        "email": "lawyer.wilson@lawfirm.com",
        "password": "password123",
        "full_name": "Attorney David Wilson",
        "role": "lawyer"
    },
    {
        "email": "prosecutor@court.gov",
        "password": "password123",
        "full_name": "Public Prosecutor Anderson",
        "role": "public_prosecutor"
    },
    {
        "email": "scheduler@court.gov",
        "password": "password123",
        "full_name": "Court Scheduler Martinez",
        "role": "scheduler"
    }
]

JUDGES_DATA = [
    {
        "user_email": "judge.smith@court.gov",
        "court_id": 2,
        "specializations": ["civil", "criminal"],
        "experience_years": 15
    },
    {
        "user_email": "judge.johnson@court.gov",
        "court_id": 2,
        "specializations": ["civil", "tax"],
        "experience_years": 12
    },
    {
        "user_email": "judge.davis@court.gov",
        "court_id": 3,
        "specializations": ["criminal", "constitutional"],
        "experience_years": 20
    }
]

LAWYERS_DATA = [
    {
        "user_email": "lawyer.brown@lawfirm.com",
        "bar_registration": "BAR-2010-12345",
        "firm_name": "Brown & Associates",
        "specializations": ["civil", "family"]
    },
    {
        "user_email": "lawyer.wilson@lawfirm.com",
        "bar_registration": "BAR-2012-67890",
        "firm_name": "Wilson Legal Group",
        "specializations": ["criminal", "civil"]
    }
]

CASES = [
    {
        "title": "Smith vs. Johnson - Property Dispute",
        "court_id": 2,
        "jurisdiction": "civil",
        "case_type": "Property Dispute",
        "urgency_level": "regular",
        "complexity_score": 7,
        "public_interest_score": 4,
        "estimated_duration_hours": 3.5,
        "description": "Dispute over property boundaries and ownership rights between neighboring landowners"
    },
    {
        "title": "State vs. Anderson - Theft Case",
        "court_id": 3,
        "jurisdiction": "criminal",
        "case_type": "Theft",
        "urgency_level": "bail",
        "complexity_score": 5,
        "public_interest_score": 6,
        "estimated_duration_hours": 2.0,
        "description": "Criminal case involving alleged theft of valuable property"
    },
    {
        "title": "Martinez vs. City Council - Administrative Appeal",
        "court_id": 2,
        "jurisdiction": "civil",
        "case_type": "Administrative Law",
        "urgency_level": "injunction",
        "complexity_score": 8,
        "public_interest_score": 9,
        "estimated_duration_hours": 4.0,
        "description": "Appeal against city council decision regarding zoning regulations"
    },
    {
        "title": "Thompson Family Custody Case",
        "court_id": 4,
        "jurisdiction": "family",
        "case_type": "Child Custody",
        "urgency_level": "regular",
        "complexity_score": 6,
        "public_interest_score": 3,
        "estimated_duration_hours": 2.5,
        "description": "Child custody dispute between divorced parents"
    },
    {
        "title": "Corporate Tax Dispute - ABC Corp",
        "court_id": 2,
        "jurisdiction": "tax",
        "case_type": "Tax Dispute",
        "urgency_level": "regular",
        "complexity_score": 9,
        "public_interest_score": 7,
        "estimated_duration_hours": 5.0,
        "description": "Complex tax dispute involving corporate tax calculations and deductions"
    },
    {
        "title": "Habeas Corpus Petition - Doe",
        "court_id": 1,
        "jurisdiction": "constitutional",
        "case_type": "Habeas Corpus",
        "urgency_level": "habeas_corpus",
        "complexity_score": 8,
        "public_interest_score": 10,
        "estimated_duration_hours": 3.0,
        "description": "Urgent habeas corpus petition challenging detention legality"
    },
    {
        "title": "Contract Breach - Tech Solutions Inc",
        "court_id": 2,
        "jurisdiction": "civil",
        "case_type": "Contract Dispute",
        "urgency_level": "regular",
        "complexity_score": 7,
        "public_interest_score": 5,
        "estimated_duration_hours": 3.0,
        "description": "Breach of contract case involving software development agreement"
    },
    {
        "title": "State vs. Roberts - Assault Case",
        "court_id": 3,
        "jurisdiction": "criminal",
        "case_type": "Assault",
        "urgency_level": "regular",
        "complexity_score": 6,
        "public_interest_score": 5,
        "estimated_duration_hours": 2.5,
        "description": "Criminal assault case with multiple witnesses"
    }
]

COURTROOMS = [
    {"court_id": 1, "name": "Supreme Court Chamber 1", "capacity": 100},
    {"court_id": 2, "name": "High Court Room A", "capacity": 80},
    {"court_id": 2, "name": "High Court Room B", "capacity": 80},
    {"court_id": 3, "name": "District Court Room 1", "capacity": 60},
    {"court_id": 3, "name": "District Court Room 2", "capacity": 60},
    {"court_id": 4, "name": "Family Court Room", "capacity": 40}
]

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def create_courts_directly():
    """Create courts directly in database"""
    print_section("Creating Courts")
    import psycopg2
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="tooba@123",
            database="DEV_WEB"
        )
        cursor = conn.cursor()
        
        court_ids = {}
        for idx, court in enumerate(COURTS, 1):
            cursor.execute("""
                INSERT INTO courts (name, level, jurisdiction, location, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (court['name'], court['level'], court['jurisdiction'], court['location'], True))
            
            result = cursor.fetchone()
            if result:
                court_id = result[0]
            else:
                # Court already exists, get its ID
                cursor.execute("SELECT id FROM courts WHERE name = %s", (court['name'],))
                court_id = cursor.fetchone()[0]
            
            court_ids[court['name']] = court_id
            print(f"   Court created: {court['name']} (ID: {court_id})")
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"\n   Total courts created: {len(COURTS)}")
        return court_ids
    except Exception as e:
        print(f"   Error creating courts: {e}")
        return {}

def create_courtrooms_directly(court_ids):
    """Create courtrooms directly in database"""
    print_section("Creating Courtrooms")
    import psycopg2
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="tooba@123",
            database="DEV_WEB"
        )
        cursor = conn.cursor()
        
        for courtroom in COURTROOMS:
            cursor.execute("""
                INSERT INTO courtrooms (court_id, name, capacity, equipment, is_available)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (courtroom['court_id'], courtroom['name'], courtroom['capacity'], 
                  json.dumps(["Projector", "Microphone", "Recording System"]), True))
            print(f"   Courtroom created: {courtroom['name']}")
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"\n   Total courtrooms created: {len(COURTROOMS)}")
    except Exception as e:
        print(f"   Error creating courtrooms: {e}")

def register_users():
    """Register all users"""
    print_section("Registering Users")
    
    user_ids = {}
    for user in USERS:
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user)
            if response.status_code == 200:
                data = response.json()
                user_ids[user['email']] = data['id']
                print(f"   User registered: {user['full_name']} ({user['email']})")
            elif response.status_code == 400:
                print(f"   User already exists: {user['email']}")
                # Try to get user ID by logging in
                login_response = requests.post(
                    f"{BASE_URL}/auth/token",
                    data={"username": user['email'], "password": user['password']}
                )
                if login_response.status_code == 200:
                    token = login_response.json()['access_token']
                    me_response = requests.get(
                        f"{BASE_URL}/auth/me",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    if me_response.status_code == 200:
                        user_ids[user['email']] = me_response.json()['id']
        except Exception as e:
            print(f"   Error registering {user['email']}: {e}")
    
    print(f"\n   Total users: {len(user_ids)}")
    return user_ids

def get_admin_token():
    """Get admin token for authenticated requests"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={"username": "admin@court.gov", "password": "password123"}
        )
        if response.status_code == 200:
            return response.json()['access_token']
    except Exception as e:
        print(f"   Error getting admin token: {e}")
    return None

def create_judges(user_ids, token):
    """Create judge profiles"""
    print_section("Creating Judge Profiles")
    
    headers = {"Authorization": f"Bearer {token}"}
    judge_ids = {}
    
    for judge_data in JUDGES_DATA:
        user_id = user_ids.get(judge_data['user_email'])
        if not user_id:
            print(f"   User not found: {judge_data['user_email']}")
            continue
        
        data = {
            "user_id": user_id,
            "court_id": judge_data['court_id'],
            "specializations": judge_data['specializations'],
            "experience_years": judge_data['experience_years']
        }
        
        try:
            response = requests.post(f"{BASE_URL}/judges", json=data, headers=headers)
            if response.status_code == 200:
                judge = response.json()
                judge_ids[judge_data['user_email']] = judge['id']
                print(f"   Judge created: {judge_data['user_email']} (ID: {judge['id']})")
            else:
                print(f"   Failed to create judge: {judge_data['user_email']} - {response.status_code}")
        except Exception as e:
            print(f"   Error creating judge {judge_data['user_email']}: {e}")
    
    print(f"\n   Total judges created: {len(judge_ids)}")
    return judge_ids

def create_lawyers(user_ids, token):
    """Create lawyer profiles"""
    print_section("Creating Lawyer Profiles")
    
    headers = {"Authorization": f"Bearer {token}"}
    lawyer_ids = {}
    
    for lawyer_data in LAWYERS_DATA:
        user_id = user_ids.get(lawyer_data['user_email'])
        if not user_id:
            print(f"   User not found: {lawyer_data['user_email']}")
            continue
        
        data = {
            "user_id": user_id,
            "bar_registration": lawyer_data['bar_registration'],
            "firm_name": lawyer_data['firm_name'],
            "specializations": lawyer_data['specializations']
        }
        
        try:
            response = requests.post(f"{BASE_URL}/lawyers", json=data, headers=headers)
            if response.status_code == 200:
                lawyer = response.json()
                lawyer_ids[lawyer_data['user_email']] = lawyer['id']
                print(f"   Lawyer created: {lawyer_data['user_email']} (ID: {lawyer['id']})")
            else:
                print(f"   Failed to create lawyer: {lawyer_data['user_email']} - {response.status_code}")
        except Exception as e:
            print(f"   Error creating lawyer {lawyer_data['user_email']}: {e}")
    
    print(f"\n   Total lawyers created: {len(lawyer_ids)}")
    return lawyer_ids

def create_cases(judge_ids, token):
    """Create cases"""
    print_section("Creating Cases")
    
    headers = {"Authorization": f"Bearer {token}"}
    case_ids = []
    
    for case_data in CASES:
        try:
            response = requests.post(f"{BASE_URL}/cases", json=case_data, headers=headers)
            if response.status_code == 200:
                case = response.json()
                case_ids.append(case['id'])
                print(f"   Case created: {case['case_number']} - {case['title']}")
                
                # Assign judge to case if available
                if judge_ids:
                    judge_id = random.choice(list(judge_ids.values()))
                    assign_response = requests.put(
                        f"{BASE_URL}/cases/{case['id']}/assign-judge",
                        params={"judge_id": judge_id},
                        headers=headers
                    )
                    if assign_response.status_code == 200:
                        print(f"      Judge assigned to case")
            else:
                print(f"   Failed to create case: {case_data['title']} - {response.status_code}")
        except Exception as e:
            print(f"   Error creating case {case_data['title']}: {e}")
    
    print(f"\n   Total cases created: {len(case_ids)}")
    return case_ids

def create_hearings(case_ids, token):
    """Create sample hearings"""
    print_section("Creating Sample Hearings")
    
    headers = {"Authorization": f"Bearer {token}"}
    hearing_count = 0
    
    # Create hearings for first few cases
    for case_id in case_ids[:4]:
        # Schedule hearing 7-14 days from now
        days_ahead = random.randint(7, 14)
        hearing_date = datetime.now() + timedelta(days=days_ahead)
        hearing_date = hearing_date.replace(hour=random.choice([9, 10, 11, 14, 15]), minute=0, second=0, microsecond=0)
        
        hearing_data = {
            "case_id": case_id,
            "courtroom_id": random.randint(1, 6),
            "scheduled_date": hearing_date.isoformat(),
            "scheduled_duration_hours": random.choice([1.5, 2.0, 2.5, 3.0])
        }
        
        try:
            response = requests.post(f"{BASE_URL}/scheduling/schedule-hearing", json=hearing_data, headers=headers)
            if response.status_code == 200:
                hearing_count += 1
                print(f"   Hearing scheduled for case {case_id} on {hearing_date.strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"   Failed to schedule hearing for case {case_id}")
        except Exception as e:
            print(f"   Error scheduling hearing: {e}")
    
    print(f"\n   Total hearings scheduled: {hearing_count}")

def main():
    print("\n" + "="*60)
    print("  POPULATING SAMPLE DATA FOR COURTROOM SCHEDULING SYSTEM")
    print("="*60)
    
    # Step 1: Create courts
    court_ids = create_courts_directly()
    
    # Step 2: Create courtrooms
    create_courtrooms_directly(court_ids)
    
    # Step 3: Register users
    user_ids = register_users()
    
    # Step 4: Get admin token
    print_section("Getting Admin Token")
    token = get_admin_token()
    if not token:
        print("   ERROR: Could not get admin token. Stopping.")
        return
    print("   Admin token obtained successfully")
    
    # Step 5: Create judges
    judge_ids = create_judges(user_ids, token)
    
    # Step 6: Create lawyers
    lawyer_ids = create_lawyers(user_ids, token)
    
    # Step 7: Create cases
    case_ids = create_cases(judge_ids, token)
    
    # Step 8: Create hearings
    create_hearings(case_ids, token)
    
    # Summary
    print_section("SUMMARY")
    print(f"   Courts: {len(COURTS)}")
    print(f"   Courtrooms: {len(COURTROOMS)}")
    print(f"   Users: {len(user_ids)}")
    print(f"   Judges: {len(judge_ids)}")
    print(f"   Lawyers: {len(lawyer_ids)}")
    print(f"   Cases: {len(case_ids)}")
    print(f"\n   Sample data population complete!")
    print(f"\n   You can now login with any of these accounts:")
    print(f"   - admin@court.gov / password123 (Administrator)")
    print(f"   - judge.smith@court.gov / password123 (Judge)")
    print(f"   - lawyer.brown@lawfirm.com / password123 (Lawyer)")
    print(f"\n   Access the application at: http://localhost:3001")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
