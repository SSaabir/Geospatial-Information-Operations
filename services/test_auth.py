"""
Authentication System Test Script

This script tests the JWT authentication system by making API calls
to verify registration, login, logout, and protected routes.

Usage:
    python test_auth.py

Author: Saabir
"""

import requests
import json
import sys
import os
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "confirm_password": "testpassword123",
    "full_name": "Test User"
}

class AuthTester:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
        self.session = requests.Session()
    
    def make_request(self, method, endpoint, data=None, headers=None, use_auth=False):
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        
        if use_auth and self.access_token:
            request_headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=request_headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=request_headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=request_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def test_health(self):
        """Test health endpoint"""
        print("🔍 Testing health endpoint...")
        response = self.make_request("GET", "/health")
        
        if response and response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code if response else 'No response'}")
            return False
    
    def test_register(self):
        """Test user registration"""
        print(f"🔍 Testing user registration...")
        response = self.make_request("POST", "/auth/register", TEST_USER)
        
        if response:
            if response.status_code == 201:
                user_data = response.json()
                print(f"✅ User registered successfully: {user_data['username']}")
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                print("ℹ️  User already exists (expected if running multiple times)")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
        else:
            print("❌ Registration request failed")
        
        return False
    
    def test_login(self):
        """Test user login"""
        print("🔍 Testing user login...")
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            
            print(f"✅ Login successful: {data['user']['username']}")
            print(f"   Access Token: {self.access_token[:20]}...")
            return True
        else:
            print(f"❌ Login failed: {response.status_code if response else 'No response'}")
            if response:
                print(f"   Error: {response.text}")
        
        return False
    
    def test_protected_route(self):
        """Test accessing protected route"""
        print("🔍 Testing protected route...")
        response = self.make_request("GET", "/protected", use_auth=True)
        
        if response and response.status_code == 200:
            data = response.json()
            print(f"✅ Protected route accessed successfully")
            print(f"   Message: {data['message']}")
            return True
        else:
            print(f"❌ Protected route access failed: {response.status_code if response else 'No response'}")
            if response:
                print(f"   Error: {response.text}")
        
        return False
    
    def test_user_info(self):
        """Test getting current user info"""
        print("🔍 Testing user info endpoint...")
        response = self.make_request("GET", "/auth/me", use_auth=True)
        
        if response and response.status_code == 200:
            user_data = response.json()
            print(f"✅ User info retrieved successfully")
            print(f"   User: {user_data['username']} ({user_data['email']})")
            return True
        else:
            print(f"❌ User info request failed: {response.status_code if response else 'No response'}")
        
        return False
    
    def test_token_verification(self):
        """Test token verification"""
        print("🔍 Testing token verification...")
        response = self.make_request("GET", "/auth/verify-token", use_auth=True)
        
        if response and response.status_code == 200:
            data = response.json()
            print(f"✅ Token verification successful")
            print(f"   Valid: {data['valid']}")
            return True
        else:
            print(f"❌ Token verification failed: {response.status_code if response else 'No response'}")
        
        return False
    
    def test_logout(self):
        """Test user logout"""
        print("🔍 Testing user logout...")
        response = self.make_request("POST", "/auth/logout", use_auth=True)
        
        if response and response.status_code == 200:
            data = response.json()
            print(f"✅ Logout successful: {data['message']}")
            self.access_token = None
            self.refresh_token = None
            return True
        else:
            print(f"❌ Logout failed: {response.status_code if response else 'No response'}")
        
        return False
    
    def test_access_after_logout(self):
        """Test that protected routes are inaccessible after logout"""
        print("🔍 Testing access after logout...")
        response = self.make_request("GET", "/protected", use_auth=True)
        
        if response and response.status_code == 401:
            print("✅ Protected route correctly denied after logout")
            return True
        else:
            print(f"❌ Expected 401, got: {response.status_code if response else 'No response'}")
        
        return False

def main():
    """Main test function"""
    print("🚀 Starting JWT Authentication System Tests")
    print("=" * 60)
    
    tester = AuthTester()
    
    tests = [
        ("Health Check", tester.test_health),
        ("User Registration", tester.test_register),
        ("User Login", tester.test_login),
        ("Protected Route Access", tester.test_protected_route),
        ("User Info Retrieval", tester.test_user_info),
        ("Token Verification", tester.test_token_verification),
        ("User Logout", tester.test_logout),
        ("Access After Logout", tester.test_access_after_logout),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! JWT authentication system is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the API server and configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()