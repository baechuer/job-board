#!/usr/bin/env python3
"""
Manual test script for recruiter request functionality
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_recruiter_request_flow():
    """Test the complete recruiter request flow manually"""
    
    print("🚀 Testing Recruiter Request Functionality")
    print("=" * 50)
    
    # Test data
    test_user = {
        "email": "testuser3@example.com",
        "password": "TestPassword123!",
        "username": "testuser3"
    }
    
    admin_user = {
        "email": "admin3@example.com", 
        "password": "AdminPassword123!",
        "username": "admin3"
    }
    
    try:
        # 1. Register test user
        print("1. Registering test user...")
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        if response.status_code == 201:
            print("✅ User registered successfully")
            user_data = response.json()
            print(f"   User ID: {user_data['id']}")
        else:
            print(f"❌ User registration failed: {response.text}")
            return False
        
        # 2. Register admin user
        print("\n2. Registering admin user...")
        response = requests.post(f"{BASE_URL}/api/auth/register", json=admin_user)
        if response.status_code == 201:
            print("✅ Admin user registered successfully")
            admin_data = response.json()
            print(f"   Admin ID: {admin_data['id']}")
        else:
            print(f"❌ Admin registration failed: {response.text}")
            return False
        
        # 3. Login as test user
        print("\n3. Logging in as test user...")
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        if response.status_code == 200:
            print("✅ User login successful")
            user_token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {user_token}"}
        else:
            print(f"❌ User login failed: {response.text}")
            return False
        
        # 4. Try to submit recruiter request (should fail - email not verified)
        print("\n4. Attempting to submit recruiter request (should fail - email not verified)...")
        response = requests.post(f"{BASE_URL}/api/recruiter-requests/", 
                               json={"reason": "I want to become a recruiter"}, 
                               headers=headers)
        if response.status_code == 400:
            print("✅ Correctly blocked unverified user")
            print(f"   Error: {response.json()['error']}")
        else:
            print(f"❌ Should have been blocked: {response.text}")
            return False
        
        # 5. Check request status
        print("\n5. Checking request status...")
        response = requests.get(f"{BASE_URL}/api/recruiter-requests/my-status", headers=headers)
        if response.status_code == 200:
            print("✅ Status check successful")
            status_data = response.json()
            print(f"   Status: {status_data['status']}")
            print(f"   Message: {status_data['message']}")
        else:
            print(f"❌ Status check failed: {response.text}")
            return False
        
        # 6. Login as admin
        print("\n6. Logging in as admin...")
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": admin_user["email"],
            "password": admin_user["password"]
        })
        if response.status_code == 200:
            print("✅ Admin login successful")
            admin_token = response.json()["access_token"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
        else:
            print(f"❌ Admin login failed: {response.text}")
            return False
        
        # 7. Try to access admin endpoints (should fail - no admin role)
        print("\n7. Attempting to access admin endpoints (should fail - no admin role)...")
        response = requests.get(f"{BASE_URL}/api/admin/recruiter-requests", headers=admin_headers)
        if response.status_code == 403:
            print("✅ Correctly blocked non-admin user")
            print(f"   Error: {response.json()['error']}")
        else:
            print(f"❌ Should have been blocked: {response.text}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 Basic functionality test completed!")
        print("\nNote: To test the full flow, you would need to:")
        print("1. Verify the user's email in the database")
        print("2. Add admin role to the admin user in the database")
        print("3. Test request submission and approval/rejection")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_server_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the Flask app first.")
        return False

if __name__ == "__main__":
    print("Testing Recruiter Request System")
    print("=" * 40)
    
    # First check if server is running
    if not test_server_health():
        print("\nPlease start the Flask app with: python run.py")
        sys.exit(1)
    
    # Run the main test
    success = test_recruiter_request_flow()
    
    if success:
        print("\n✅ All basic tests passed!")
        print("\nTo test the complete workflow:")
        print("1. Start the Flask app: python run.py")
        print("2. Run this script: python manual_test_recruiter_requests.py")
        print("3. Manually verify email and add admin role in database")
        print("4. Test the full approval/rejection workflow")
    else:
        print("\n❌ Some tests failed. Check the output above.")
        sys.exit(1)
