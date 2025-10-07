import requests, sys
BASE='http://127.0.0.1:8000'
# login
r=requests.post(f"{BASE}/auth/login", json={"username":"testuser","password":"testpassword123"}, timeout=10)
print('login status', r.status_code)
if r.status_code!=200:
    print(r.text); sys.exit(1)
access=r.json().get('access_token')
print('token len', len(access))
headers={'Authorization':f'Bearer {access}','Content-Type':'application/json'}
# send a frontend-like request body (mixed-case tier)
payload={'tier':'Researcher'}
r2=requests.post(f"{BASE}/billing/change-tier", json=payload, headers=headers)
print('/billing/change-tier', r2.status_code, r2.text)
# call the compat endpoint too
r3=requests.post(f"{BASE}/billing/create-checkout-session", json={'plan_id':'professional'}, headers=headers)
print('/billing/create-checkout-session', r3.status_code, r3.text)
