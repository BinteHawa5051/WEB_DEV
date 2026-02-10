"""
Test Login from Frontend Perspective
"""

import requests

BASE_URL = "http://localhost:8000/api"

print("\n" + "="*60)
print("  TESTING LOGIN")
print("="*60)

# Test login
print("\nTesting login with admin@court.gov...")
try:
    # This is how the frontend sends the login request
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={
            "username": "admin@court.gov",
            "password": "password123"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://localhost:3001"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Login successful!")
        print(f"✓ Token received: {data['access_token'][:50]}...")
        
        # Test getting current user
        print("\nTesting get current user...")
        me_response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {data['access_token']}",
                "Origin": "http://localhost:3001"
            }
        )
        
        if me_response.status_code == 200:
            user = me_response.json()
            print(f"✓ User: {user['full_name']}")
            print(f"✓ Email: {user['email']}")
            print(f"✓ Role: {user['role']}")
        else:
            print(f"✗ Failed to get user: {me_response.status_code}")
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*60)
print("  CORS TEST")
print("="*60)

# Test CORS preflight
print("\nTesting CORS preflight (OPTIONS request)...")
try:
    response = requests.options(
        f"{BASE_URL}/auth/token",
        headers={
            "Origin": "http://localhost:3001",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"CORS Headers:")
    for header, value in response.headers.items():
        if 'access-control' in header.lower():
            print(f"  {header}: {value}")
    
    if response.status_code == 200:
        print("✓ CORS is configured correctly")
    else:
        print("✗ CORS preflight failed")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*60)
print("  RESULT")
print("="*60)
print("\nIf you see '✓ Login successful!' above,")
print("then the login should work in the browser.")
print("\nTry logging in again at: http://localhost:3001")
print("Email: admin@court.gov")
print("Password: password123")
print("="*60 + "\n")
