# 🎯 Team Deployment Instructions

## Files Your Team Needs to Run

Your team members need to run these **3 simple commands** to get started:

### Option 1: Automated Setup (Recommended) ⚡

**Windows PowerShell (Run as Administrator):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_team_environment.ps1
```

**Linux/Mac Terminal:**
```bash
chmod +x setup_team_environment.sh
./setup_team_environment.sh
```

### Option 2: Manual Setup 🔧

If automated setup fails, follow these steps:

1. **Backend Setup:**
```bash
cd services
python -m venv .venv
.\.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
cp .env.example .env             # Then edit .env with actual values
python init_db.py
python create_admin.py
```

2. **Frontend Setup:**
```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

3. **Start Both Servers:**
```bash
# Terminal 1 - Backend
cd services && .\.venv\Scripts\activate && python main.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## 📋 Required Files Checklist

Ensure these files are in your repository:

### Setup Files ✅
- [ ] `setup_team_environment.ps1` - Windows automated setup
- [ ] `setup_team_environment.sh` - Linux/Mac automated setup
- [ ] `TEAM_SETUP_GUIDE.md` - Detailed setup guide
- [ ] `QUICK_START.md` - Quick reference commands
- [ ] `test_integration.py` - Integration testing

### Backend Files ✅
- [ ] `services/requirements.txt` - Python dependencies
- [ ] `services/.env.example` - Environment template
- [ ] `services/main.py` - FastAPI server
- [ ] `services/init_db.py` - Database initialization
- [ ] `services/create_admin.py` - Admin user creation

### Frontend Files ✅
- [ ] `frontend/package.json` - Node.js dependencies
- [ ] `frontend/src/App.jsx` - React application
- [ ] `frontend/src/contexts/AuthContext.jsx` - Auth state

## 🚀 What Happens After Setup

1. **Backend Server**: `http://localhost:8000`
   - JWT Authentication API
   - Orchestrator endpoints
   - Protected routes

2. **Frontend App**: `http://localhost:5173`
   - React interface
   - Authentication pages
   - Dashboard and tools

3. **Default Login**:
   - Username: `admin`
   - Password: `password123`

## 🔧 Troubleshooting Guide

### Common Issues:

**1. "Python not found"**
```bash
# Install Python 3.8+ from python.org
# Restart terminal/command prompt
python --version
```

**2. "Node.js not found"** 
```bash
# Install Node.js 16+ from nodejs.org
# Restart terminal/command prompt
node --version
```

**3. "Port already in use"**
```bash
# Windows: Kill process on port
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/Mac: Kill process on port
lsof -ti:8000 | xargs kill -9
```

**4. "Database connection error"**
- Install PostgreSQL
- Create database: `geospatial_ops`
- Update `services/.env` with correct credentials

**5. "Permission denied"**
```bash
# Windows: Run PowerShell as Administrator
# Linux/Mac: Add execute permission
chmod +x setup_team_environment.sh
```

## 📞 Team Support

**Before asking for help:**
1. Run `python test_integration.py` to identify issues
2. Check the setup logs for error messages
3. Verify all prerequisites are installed

**Quick Test Command:**
```bash
python test_integration.py
```
This will verify that everything is working correctly.

## 🎯 Summary for Team Leaders

**To onboard a new team member:**

1. **Send them this repository**
2. **Tell them to run the appropriate setup script**
3. **They'll have a working system in ~5 minutes**

**Key files to maintain:**
- Keep `requirements.txt` updated with Python dependencies
- Keep `package.json` updated with Node.js dependencies
- Update `.env.example` when new configuration is needed
- Test setup scripts periodically

---

**🎉 Your team will have a complete JWT-authenticated geospatial analysis system running locally!**

*Last Updated: September 27, 2025 by Saabir*