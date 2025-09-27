# JWT Authentication System Documentation

## Overview

This document describes the comprehensive JWT (JSON Web Token) authentication system implemented for the Geospatial Information Operations project. The system provides secure user authentication with registration, login, logout, token refresh, and user management capabilities.

## 🏗️ System Architecture

### Backend Components

1. **User Models** (`/models/user.py`)
   - `UserDB`: SQLAlchemy ORM model for database operations
   - `UserCreate`, `UserLogin`, `UserResponse`: Pydantic models for API validation
   - Password hashing and verification methods

2. **JWT Handler** (`/security/jwt_handler.py`)
   - Token creation and validation
   - Token blacklisting with Redis (optional)
   - Refresh token functionality
   - Password hashing utilities

3. **Authentication Middleware** (`/security/auth_middleware.py`)
   - JWT token verification
   - User authentication dependencies
   - Admin privilege checking
   - Optional authentication support

4. **API Endpoints** (`/api/auth.py`)
   - User registration and login
   - Token refresh and logout
   - User profile management
   - Password change functionality

5. **Database Configuration** (`/db_config.py`)
   - PostgreSQL connection management
   - Session handling
   - Connection pooling

### Frontend Components

1. **AuthContext** (`/frontend/src/contexts/AuthContext.jsx`)
   - React context for authentication state
   - API integration for auth operations
   - Token management and automatic refresh
   - User session persistence

## 🚀 Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
cd services
source .venv/bin/activate
pip install -r requirements.txt
```

#### Configure Environment Variables
Ensure your `.env` file contains:
```bash
# Database Configuration
DATABASE_URL=postgresql+psycopg2://postgres:ElDiabloX32@localhost:5432/GISDb

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration (optional, for token blacklisting)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### Initialize Database
```bash
python init_db.py --create-admin
```

#### Start the API Server
```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

#### Configure Environment
Create `/frontend/.env`:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Start Development Server
```bash
npm run dev
```

## 🔐 Authentication Flow

### Registration Flow
1. User submits registration form
2. Frontend calls `/auth/register` endpoint
3. Backend validates data and creates user
4. Password is hashed using bcrypt
5. User record is stored in database
6. Success response returned

### Login Flow
1. User submits login credentials
2. Frontend calls `/auth/login` endpoint
3. Backend verifies credentials
4. JWT access and refresh tokens generated
5. Tokens and user data returned to frontend
6. Tokens stored in localStorage
7. User authenticated in React context

### Token Refresh Flow
1. Access token expires
2. Frontend automatically uses refresh token
3. Backend validates refresh token
4. New access token generated and returned
5. Frontend updates stored token

### Logout Flow
1. User initiates logout
2. Frontend calls `/auth/logout` endpoint
3. Backend blacklists current token (if Redis available)
4. Frontend clears stored tokens and user data
5. User redirected to login page

## 📡 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/auth/register` | Register new user | None |
| POST | `/auth/login` | User login | None |
| POST | `/auth/logout` | User logout | Required |
| POST | `/auth/refresh` | Refresh access token | None |
| GET | `/auth/me` | Get current user info | Required |
| PUT | `/auth/me` | Update user profile | Required |
| POST | `/auth/change-password` | Change password | Required |
| GET | `/auth/verify-token` | Verify token validity | Required |

### Example Requests

#### Registration
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword123",
    "confirm_password": "securepassword123",
    "full_name": "New User"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword123"
  }'
```

#### Access Protected Route
```bash
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🛡️ Security Features

### Password Security
- Bcrypt hashing with salt
- Minimum 8-character requirement
- Password confirmation validation

### Token Security
- JWT with HMAC SHA-256 signing
- Configurable expiration times
- Refresh token rotation
- Optional token blacklisting with Redis

### API Security
- CORS configuration
- Rate limiting (can be added)
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy

## 🧪 Testing

### Manual Testing
Run the authentication test script:
```bash
cd services
python test_auth.py
```

### API Documentation
Access interactive API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Testing
1. Start both backend and frontend servers
2. Test registration at frontend login page
3. Test login/logout functionality
4. Test protected routes

## 🔧 Configuration Options

### JWT Settings
```bash
JWT_SECRET_KEY=your-secret-key          # Secret for signing tokens
JWT_ALGORITHM=HS256                     # Signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=30          # Access token lifetime
REFRESH_TOKEN_EXPIRE_DAYS=7             # Refresh token lifetime
```

### Database Settings
```bash
DATABASE_URL=postgresql+psycopg2://user:pass@host:port/db
DB_POOL_SIZE=5                          # Connection pool size
DB_MAX_OVERFLOW=10                      # Max overflow connections
```

### Redis Settings (Optional)
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=                         # Optional password
```

## 🚨 Troubleshooting

### Common Issues

#### "Import errors" in TrendAgent.py
- Ensure virtual environment is activated
- Verify VS Code is using the correct Python interpreter
- Check that all packages are installed

#### Database connection errors
- Verify PostgreSQL is running
- Check DATABASE_URL configuration
- Ensure database exists and user has permissions

#### CORS errors in frontend
- Verify CORS_ORIGINS includes frontend URL
- Check that API server is running
- Ensure VITE_API_BASE_URL is correctly set

#### Token validation failures
- Check JWT_SECRET_KEY matches between environments
- Verify token hasn't expired
- Ensure Authorization header format: "Bearer <token>"

### Debug Commands

```bash
# Check database connection
python -c "from db_config import DatabaseConfig; db = DatabaseConfig(); print('DB OK' if db.test_connection() else 'DB Failed')"

# Verify environment variables
python -c "import os; print('JWT Key:', bool(os.getenv('JWT_SECRET_KEY')))"

# Test API health
curl http://localhost:8000/health
```

## 📝 Development Notes

### Adding New Protected Routes
```python
from security.auth_middleware import get_current_user

@app.get("/my-protected-route")
async def protected_route(current_user: UserDB = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

### Adding Admin-Only Routes
```python
from security.auth_middleware import get_current_admin_user

@app.get("/admin-only")
async def admin_route(admin_user: UserDB = Depends(get_current_admin_user)):
    return {"message": "Admin access granted"}
```

### Using Authentication in Frontend
```jsx
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, apiCall, isAuthenticated } = useAuth();
  
  const fetchProtectedData = async () => {
    try {
      const data = await apiCall('/protected-endpoint');
      console.log(data);
    } catch (error) {
      console.error('API call failed:', error);
    }
  };
  
  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }
  
  return <div>Welcome {user.username}!</div>;
}
```

## 📋 Next Steps

1. **Add Password Reset**: Implement email-based password reset
2. **Email Verification**: Add email verification for new accounts
3. **Rate Limiting**: Implement API rate limiting
4. **Audit Logging**: Add authentication event logging
5. **Two-Factor Authentication**: Implement 2FA support
6. **OAuth Integration**: Add Google/GitHub login options

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation at `/docs`
3. Run the test script to verify system health
4. Check logs for detailed error messages