#!/usr/bin/env python3
"""
Test script for job title dropdown functionality
"""

import requests
import json

# Assuming the server is running on localhost:5000
BASE_URL = "http://localhost:5000"

def test_job_titles_api():
    """Test GET /api/admin/job-titles"""
    print("Testing GET /api/admin/job-titles...")

    # First, we need to login to get JWT token
    login_data = {
        "username": "admin",
        "password": "admin123"  # Assuming default password
    }

    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return None

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test job titles endpoint
        response = requests.get(f"{BASE_URL}/api/admin/job-titles", headers=headers)
        if response.status_code == 200:
            job_titles = response.json()
            print(f"✅ Got {len(job_titles)} job titles:")
            for jt in job_titles[:3]:  # Show first 3
                print(f"   - {jt['code']}: {jt['name']} (level {jt['level_no']})")
            return headers
        else:
            print(f"❌ Job titles API failed: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return None

def test_update_user_with_job_title(headers):
    """Test PUT /api/admin/users/<id> with job_title_id"""
    print("\nTesting PUT /api/admin/users/<id> with job_title_id...")

    # First get a user
    response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
    if response.status_code != 200:
        print(f"❌ Cannot get users: {response.status_code}")
        return

    users = response.json()
    if not users:
        print("❌ No users found")
        return

    user = users[0]
    user_id = user["id"]
    print(f"Updating user: {user['username']} (ID: {user_id})")

    # Update with job_title_id (assuming TP - Trưởng phòng exists)
    update_data = {
        "job_title_id": 5,  # TP - Trưởng phòng
        "full_name": user.get("full_name", "Updated Name")
    }

    response = requests.put(f"{BASE_URL}/api/admin/users/{user_id}", json=update_data, headers=headers)
    if response.status_code == 200:
        print("✅ User updated successfully")

        # Verify the update
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        if response.status_code == 200:
            updated_users = response.json()
            updated_user = next((u for u in updated_users if u["id"] == user_id), None)
            if updated_user:
                print(f"✅ Verified: job_title_id={updated_user['job_title_id']}, job_title_name='{updated_user['job_title_name']}'")
    else:
        print(f"❌ Update failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("🧪 Testing Job Title Dropdown Functionality\n")

    headers = test_job_titles_api()
    if headers:
        test_update_user_with_job_title(headers)

    print("\n✨ Test completed!")