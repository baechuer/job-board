#!/usr/bin/env python3
"""
Test script for recruiter request functionality
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_recruiter_request_flow():
    """Test the complete recruiter request flow"""
    
    # Test data
    test_user = {
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "username": "testuser"
    }
    
    admin_user = {
        "email": "admin@example.com", 
        "password": "AdminPassword123!",
        "username": "admin"
    }
    
    print("🚀 Testing Recruiter Request Functionality")
    print("=" * 50)
    
    # 1. Register test user
    print("1. Registering test user...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user, timeout=2)
    except requests.exceptions.ConnectionError:
        import pytest
        pytest.skip("Server not running on localhost:5000; skipping manual E2E test")
    if response.status_code == 201:
        print("✅ User registered successfully")
        user_data = response.json()
        print(f"   User ID: {user_data['id']}")
    else:
        print(f"❌ User registration failed: {response.text}")
        return
    
    # 2. Register admin user
    print("\n2. Registering admin user...")
    response = requests.post(f"{BASE_URL}/api/auth/register", json=admin_user)
    if response.status_code == 201:
        print("✅ Admin user registered successfully")
        admin_data = response.json()
        print(f"   Admin ID: {admin_data['id']}")
    else:
        print(f"❌ Admin registration failed: {response.text}")
        return
    
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
        return
    
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
    
    print("\n" + "=" * 50)
    print("🎉 Basic functionality test completed!")
    print("\nNote: To test the full flow, you would need to:")
    print("1. Verify the user's email")
    print("2. Add admin role to the admin user")
    print("3. Test request submission and approval/rejection")

if __name__ == "__main__":
    try:
        test_recruiter_request_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
