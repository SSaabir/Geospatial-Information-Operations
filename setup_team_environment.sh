#!/bin/bash
# Geospatial Information Operations - Team Setup Script
# This script automates the complete setup process for new team members

set -e  # Exit on any error

echo "🚀 Setting up Geospatial Information Operations Development Environment"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
echo ""
print_info "Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "Python is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
print_status "Python $PYTHON_VERSION found"

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status "Node.js $NODE_VERSION found"
else
    print_error "Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_status "npm $NPM_VERSION found"
else
    print_error "npm is not installed. Please install npm and try again."
    exit 1
fi

echo ""
print_info "Setting up backend services..."

# Backend Setup
cd services || exit 1

# Create virtual environment
print_info "Creating Python virtual environment..."
$PYTHON_CMD -m venv .venv

# Activate virtual environment
print_info "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # Linux/Mac
    source .venv/bin/activate
fi

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_status "Backend dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_info "Creating backend environment configuration..."
    cat > .env << EOF
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
EOF
    print_status "Backend environment configuration created"
else
    print_warning "Backend .env file already exists, skipping creation"
fi

# Initialize database
print_info "Initializing database..."
if $PYTHON_CMD init_db.py; then
    print_status "Database initialized successfully"
else
    print_warning "Database initialization failed (may already exist)"
fi

# Create admin user
print_info "Creating admin user..."
if $PYTHON_CMD create_admin.py; then
    print_status "Admin user created (username: admin, password: password123)"
else
    print_warning "Admin user creation failed (may already exist)"
fi

# Go back to root directory
cd ..

echo ""
print_info "Setting up frontend application..."

# Frontend Setup
cd frontend || exit 1

# Install Node.js dependencies
print_info "Installing Node.js dependencies..."
npm install
print_status "Frontend dependencies installed"

# Create frontend .env file
if [ ! -f .env ]; then
    print_info "Creating frontend environment configuration..."
    echo "VITE_API_BASE_URL=http://localhost:8000" > .env
    print_status "Frontend environment configuration created"
else
    print_warning "Frontend .env file already exists, skipping creation"
fi

# Go back to root directory
cd ..

echo ""
print_info "Running integration tests..."

# Test the setup
if $PYTHON_CMD test_integration.py; then
    print_status "Integration tests passed!"
else
    print_warning "Some integration tests failed, but setup is complete"
fi

echo ""
echo "=================================================================="
print_status "Setup Complete! 🎉"
echo ""
print_info "Next steps:"
echo "1. Start the backend server:"
echo "   cd services"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   .venv/Scripts/activate"
else
    echo "   source .venv/bin/activate"
fi
echo "   python main.py"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser to: http://localhost:5173"
echo "4. Login with: admin / password123"
echo ""
print_status "Happy coding! 🚀"