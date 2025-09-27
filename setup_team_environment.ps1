# Geospatial Information Operations - Team Setup Script (PowerShell)
# This script automates the complete setup process for new team members on Windows

param(
    [switch]$SkipPrereqs = $false
)

# Colors for output
$ErrorActionPreference = "Stop"

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

Write-Host "🚀 Setting up Geospatial Information Operations Development Environment" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

if (-not $SkipPrereqs) {
    Write-Host ""
    Write-Info "Checking prerequisites..."

    # Check Python
    try {
        $pythonVersion = & python --version 2>&1
        Write-Success "Python $pythonVersion found"
    } catch {
        Write-Error "Python is not installed. Please install Python 3.8+ and try again."
        exit 1
    }

    # Check Node.js
    try {
        $nodeVersion = & node --version
        Write-Success "Node.js $nodeVersion found"
    } catch {
        Write-Error "Node.js is not installed. Please install Node.js 16+ and try again."
        exit 1
    }

    # Check npm
    try {
        $npmVersion = & npm --version
        Write-Success "npm v$npmVersion found"
    } catch {
        Write-Error "npm is not installed. Please install npm and try again."
        exit 1
    }
}

Write-Host ""
Write-Info "Setting up backend services..."

# Backend Setup
Set-Location services

# Create virtual environment
Write-Info "Creating Python virtual environment..."
& python -m venv .venv

# Activate virtual environment
Write-Info "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# Install Python dependencies
Write-Info "Installing Python dependencies..."
& pip install --upgrade pip
& pip install -r requirements.txt
Write-Success "Backend dependencies installed"

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Info "Creating backend environment configuration..."
    
    $envContent = @"
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/geospatial_ops
DB_HOST=localhost
DB_PORT=5432
DB_NAME=geospatial_ops
DB_USER=postgres
DB_PASSWORD=password

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173

# Redis Configuration (Optional - for token blacklisting)
REDIS_URL=redis://localhost:6379/0
USE_REDIS=false

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
"@

    $envContent | Out-File -FilePath .env -Encoding UTF8
    Write-Success "Backend environment configuration created"
} else {
    Write-Warning "Backend .env file already exists, skipping creation"
}

# Initialize database
Write-Info "Initializing database..."
try {
    & python init_db.py
    Write-Success "Database initialized successfully"
} catch {
    Write-Warning "Database initialization failed (may already exist)"
}

# Create admin user
Write-Info "Creating admin user..."
try {
    & python create_admin.py
    Write-Success "Admin user created (username: admin, password: password123)"
} catch {
    Write-Warning "Admin user creation failed (may already exist)"
}

# Go back to root directory
Set-Location ..

Write-Host ""
Write-Info "Setting up frontend application..."

# Frontend Setup
Set-Location frontend

# Install Node.js dependencies
Write-Info "Installing Node.js dependencies..."
& npm install
Write-Success "Frontend dependencies installed"

# Create frontend .env file
if (-not (Test-Path .env)) {
    Write-Info "Creating frontend environment configuration..."
    "VITE_API_BASE_URL=http://localhost:8000" | Out-File -FilePath .env -Encoding UTF8
    Write-Success "Frontend environment configuration created"
} else {
    Write-Warning "Frontend .env file already exists, skipping creation"
}

# Go back to root directory
Set-Location ..

Write-Host ""
Write-Info "Running integration tests..."

# Test the setup
try {
    & python test_integration.py
    Write-Success "Integration tests passed!"
} catch {
    Write-Warning "Some integration tests failed, but setup is complete"
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Success "Setup Complete! 🎉"
Write-Host ""
Write-Info "Next steps:"
Write-Host "1. Start the backend server:"
Write-Host "   cd services"
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "   python main.py"
Write-Host ""
Write-Host "2. In a new PowerShell window, start the frontend:"
Write-Host "   cd frontend"
Write-Host "   npm run dev"
Write-Host ""
Write-Host "3. Open your browser to: http://localhost:5173"
Write-Host "4. Login with: admin / password123"
Write-Host ""
Write-Success "Happy coding! 🚀"