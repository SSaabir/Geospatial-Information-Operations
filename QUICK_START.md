# Quick Start Commands for Team Members

## Windows Users (Recommended)
```powershell
# Open PowerShell as Administrator and run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_team_environment.ps1
```

## Linux/Mac Users
```bash
chmod +x setup_team_environment.sh
./setup_team_environment.sh
```

## Manual Setup (If scripts fail)

### 1. Backend Setup
```bash
cd services
python -m venv .venv

# Windows:
.\.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
python init_db.py
python create_admin.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

### 3. Run Servers
```bash
# Terminal 1 - Backend
cd services && .\.venv\Scripts\activate && python main.py

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

## Login Credentials
- Username: `admin`
- Password: `password123`

## URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000