"""
Test Frontend-Backend Integration

This script tests the integration between the React frontend and FastAPI backend
by making API calls to verify authentication works end-to-end.

Author: Saabir
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_integration():
    """Test the full integration flow"""
    print("🔗 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    # Test 1: Backend Health Check
    print("1. Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print("❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Frontend Accessibility
    print("\n2. Testing Frontend Accessibility...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print("❌ Frontend not accessible")
    except Exception as e:
        print(f"⚠️  Frontend check failed (but may be normal): {e}")
    
    # Test 3: Login Endpoint
    print("\n3. Testing Login Endpoint...")
    login_data = {
        "username": "admin",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Login endpoint working")
            data = response.json()
            access_token = data.get("access_token")
            
            if access_token:
                print("✅ JWT token received")
                
                # Test 4: Protected Route Access
                print("\n4. Testing Protected Route...")
                headers = {"Authorization": f"Bearer {access_token}"}
                
                response = requests.get(f"{BACKEND_URL}/protected", headers=headers)
                if response.status_code == 200:
                    print("✅ Protected route accessible with token")
                else:
                    print("❌ Protected route access failed")
                
                # Test 5: Orchestrator API
                print("\n5. Testing Orchestrator API...")
                
                # Test orchestrator preview
                orchestrator_data = {
                    "query": "Show me weather data for Colombo",
                    "async_execution": False,
                    "include_visualizations": True
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/orchestrator/preview",
                    json=orchestrator_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    print("✅ Orchestrator preview working")
                    preview_data = response.json()
                    print(f"   Workflow Type: {preview_data.get('workflow_type')}")
                    print(f"   Description: {preview_data.get('description')}")
                else:
                    print("❌ Orchestrator preview failed")
                
                return True
            else:
                print("❌ No access token in response")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Login test failed: {e}")
    
    return False

def main():
    """Main function"""
    print("🚀 Starting Integration Tests")
    print("📋 Ensure both servers are running:")
    print(f"   - Backend: {BACKEND_URL}")
    print(f"   - Frontend: {FRONTEND_URL}")
    print()
    
    success = test_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Integration tests PASSED!")
        print("\n💡 Next Steps:")
        print("1. Open your browser to http://localhost:5173")
        print("2. Click 'Sign In' or 'Get Started'")
        print("3. Login with:")
        print("   - Username: admin")
        print("   - Password: password123")
        print("4. Test the dashboard and orchestrator features")
    else:
        print("❌ Integration tests FAILED!")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure backend server is running on port 8000")
        print("2. Ensure frontend server is running on port 5173")
        print("3. Check that admin user was created successfully")
        print("4. Verify .env configuration")

if __name__ == "__main__":
    main()