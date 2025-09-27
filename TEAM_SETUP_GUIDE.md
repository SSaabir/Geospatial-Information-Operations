# Team Setup Guide 🚀
## Geospatial Information Operations - Complete Development Environment

This guide will help your team get the complete system running locally with JWT authentication, backend services, and frontend interface.

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.8+** installed
- **Node.js 16+** and npm installed  
- **PostgreSQL** installed and running
- **Git** installed
- **Code editor** (VS Code recommended)

## 🏗️ Quick Start (5 Minutes)

### 1. Clone and Setup Repository
```bash
# Clone the repository
git clone https://github.com/SSaabir/Geospatial-Information-Operations.git
cd Geospatial-Information-Operations

# Make setup script executable (Linux/Mac)
chmod +x setup_team_environment.sh

# Run automated setup
./setup_team_environment.sh
```

### 2. Manual Setup (If automated fails)

#### Backend Setup
```bash
# Navigate to services directory
cd services

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment configuration
cp .env.example .env

# Initialize database and create admin user
python init_db.py
python create_admin.py
```

#### Frontend Setup  
```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Create frontend environment configuration
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

## 🚀 Running the Application

### Start Backend Server
```bash
cd services
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

python main.py
```
**Backend will run on:** `http://localhost:8000`

### Start Frontend Server
```bash
cd frontend
npm run dev
```
**Frontend will run on:** `http://localhost:5173`

## 🔐 Default Login Credentials

- **Username:** `admin`
- **Password:** `password123`

## 🧪 Verify Setup

Run the integration test to ensure everything works:
```bash
python test_integration.py
```

## 📁 Key Files Overview

### Essential Backend Files:
- `services/main.py` - FastAPI server entry point
- `services/requirements.txt` - Python dependencies
- `services/.env` - Environment configuration
- `services/init_db.py` - Database initialization
- `services/create_admin.py` - Creates admin user

### Essential Frontend Files:
- `frontend/package.json` - Node.js dependencies  
- `frontend/.env` - Frontend environment variables
- `frontend/src/App.jsx` - Main React application
- `frontend/src/contexts/AuthContext.jsx` - Authentication state

### Configuration Files:
- `.env.example` - Template for environment variables
- `setup_team_environment.sh` - Automated setup script
- `test_integration.py` - Integration testing

## 🔧 Troubleshooting

### Common Issues:

1. **Port already in use:**
   ```bash
   # Kill process on port 8000
   netstat -ano | findstr :8000
   taskkill /PID <process_id> /F
   ```

2. **Database connection error:**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Run `python init_db.py` again

3. **Module not found errors:**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

4. **Frontend build errors:**
   - Delete `node_modules` and run `npm install`
   - Check Node.js version (16+ required)

## 🛡️ Security Notes

- Change default admin password in production
- Update JWT secret keys in `.env`
- Configure proper CORS settings
- Use environment-specific configurations

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run `python test_integration.py` to identify problems
3. Check server logs for detailed error messages
4. Contact the development team

## 🎯 Next Steps After Setup

1. **Test Login:** Go to `http://localhost:5173` and login
2. **Explore Dashboard:** Access protected routes and features
3. **Test Orchestrator:** Try the geospatial analysis tools
4. **Review Documentation:** Check component READMEs for details

---

**Happy Coding! 🎉**

*Last Updated: September 27, 2025*