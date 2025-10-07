import requests
import os

BASE = os.getenv("BASE_URL", "http://127.0.0.1:8000")

# test user credentials - adjust as needed
USERNAME = "testuser"
PASSWORD = "password"

s = requests.Session()

# 1. login
# Ensure test user exists by attempting to register (ignore failure if exists)
reg_payload = {
    "username": USERNAME,
    "email": f"{USERNAME}@example.com",
    "full_name": "Test User",
    "password": PASSWORD,
    "confirm_password": PASSWORD,
}
r = s.post(f"{BASE}/auth/register", json=reg_payload)
print("register", r.status_code, r.text)

# Now login
r = s.post(f"{BASE}/auth/login", json={"username": USERNAME, "password": PASSWORD})
print("login", r.status_code, r.text)
if r.status_code != 200:
    raise SystemExit("login failed")

token = r.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# 2. create session
r = s.post(f"{BASE}/payments/create-session", json={"plan": "researcher", "recurring": False}, headers=headers)
print("create-session", r.status_code, r.text)
if r.status_code != 200:
    raise SystemExit("create-session failed")

session_id = r.json().get("session_id")

# 3. pay session with test card
card = {
    "card_number": "4242424242424242",
    "exp_month": "12",
    "exp_year": "2028",
    "cvc": "123",
}

r = s.post(f"{BASE}/payments/session/{session_id}/pay", json=card, headers=headers)
print("pay-session", r.status_code, r.text)
if r.status_code != 200:
    raise SystemExit("pay-session failed")

# 4. list payments
r = s.get(f"{BASE}/payments/", headers=headers)
print("list-payments", r.status_code, r.text)

# 5. check /auth/me
r = s.get(f"{BASE}/auth/me", headers=headers)
print("me", r.status_code, r.text)
