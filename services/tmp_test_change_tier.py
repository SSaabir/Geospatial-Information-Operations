import requests
import sys

BASE = "http://127.0.0.1:8000"
creds = {"username": "testuser", "password": "testpassword123"}

s = requests.Session()
try:
    r = s.post(f"{BASE}/auth/login", json=creds, timeout=10)
except Exception as e:
    print(f"Login request failed: {e}")
    sys.exit(2)

if r.status_code != 200:
    print(f"Login failed: {r.status_code} {r.text}")
    sys.exit(1)

data = r.json()
access_token = data.get("access_token")
print(f"Got access token: {access_token[:30]}...")

headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

# Use frontend-expecting endpoint
payload = {"tier": "professional"}

r2 = s.post(f"{BASE}/auth/me/tier", json=payload, headers=headers)
print("Change-tier (frontend path) status:", r2.status_code)
try:
    print("Response:", r2.json())
except Exception:
    print("Response text:", r2.text)

# fetch user info
r3 = s.get(f"{BASE}/auth/me", headers=headers)
print("/auth/me status:", r3.status_code)
try:
    print("User:", r3.json())
except Exception:
    print("User text:", r3.text)

sys.exit(0)