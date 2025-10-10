# ⚡ Services - FastAPI Backend

> High-performance FastAPI backend with JWT authentication, AI agents, and geospatial analysis capabilities

## 📋 Overview

This is the backend services layer for the Geospatial Information Operations platform. Built with FastAPI, it provides a robust API with JWT authentication, AI-powered agents, database integration, and geospatial analysis capabilities.

## 🎯 Key Features

- **🔐 Complete JWT Authentication**: Token-based auth with access/refresh tokens, password hashing, and secure middleware
- **🤖 AI Agent System**: Multi-agent architecture for data collection, analysis, and reporting
- **🗄️ Database Integration**: PostgreSQL with SQLAlchemy ORM and user management
- **🛡️ Security Middleware**: Request authentication, CORS handling, and input validation
- **📊 Geospatial Analysis**: Weather data processing and trend analysis
- **🌐 RESTful API**: Well-documented endpoints with automatic OpenAPI generation

## 🛠️ Technology Stack

### Core Framework
- **FastAPI 0.104+** - High-performance async web framework
- **Python 3.10+** - Modern Python with type hints
- **Uvicorn** - ASGI server for production deployment
- **Pydantic** - Data validation and serialization

### Authentication & Security
- **JWT (JSON Web Tokens)** - Stateless authentication
- **bcrypt** - Password hashing
- **python-jose** - JWT token handling
- **passlib** - Password validation and hashing

### Database
- **PostgreSQL** - Primary database
- **SQLAlchemy 2.0** - Modern ORM with async support
- **psycopg2-binary** - PostgreSQL adapter
- **Alembic** - Database migrations

### AI & Data Processing
- **LangChain** - AI/LLM framework integration
- **LangGraph** - Multi-agent workflow orchestration
- **Groq API** - Language model services
- **pandas** - Data manipulation
- **scikit-learn** - Machine learning algorithms

## 📁 Project Structure

```
services/
├── agents/                    # AI Agent System
│   ├── collector.py          # Data collection agent
│   ├── orchestrator.py       # Agent coordination
│   ├── trend.py              # Trend analysis agent
│   ├── TrendAgent.py         # Enhanced trend agent class
│   ├── report.py             # Report generation agent
│   ├── collector.ipynb       # Jupyter notebook for development
│   ├── predict/              # Prediction models
│   │   ├── predict_too.py    # Weather prediction logic
│   │   └── train.py          # Model training scripts
│   └── preprocessed_climate_dataset5.csv # Training data
├── api/                      # API Endpoints
│   └── auth.py              # Authentication routes
├── models/                   # Database Models
│   └── user.py              # User model definitions
├── security/                 # Security Components
│   ├── auth_middleware.py   # JWT middleware
│   └── jwt_handler.py       # JWT token operations
├── data/                     # Data Files
│   ├── history_colombo.csv  # Historical weather data
│   └── PstDB.sql           # Database schema
├── main.py                   # FastAPI application entry point
├── db_config.py             # Database configuration
├── init_db.py               # Database initialization
├── create_admin.py          # Admin user creation
├── test_auth.py             # Authentication tests
├── test_environment.py      # Environment testing
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── .env                    # Environment configuration (local)
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** installed
- **PostgreSQL 14+** running
- **Git** for version control

### Setup & Run

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python init_db.py

# Create admin user
python create_admin.py

# Run server
python main.py
```

➡️ **API Server:** http://localhost:8000  
➡️ **API Docs:** http://localhost:8000/docs  
➡️ **ReDoc:** http://localhost:8000/redoc

## 🔐 Authentication System

### JWT Implementation

The authentication system provides:

#### Token Types
- **Access Tokens**: Short-lived (30 minutes) for API requests
- **Refresh Tokens**: Long-lived (7 days) for token renewal

#### Security Features
- **bcrypt Hashing**: Secure password storage
- **Token Blacklisting**: Optional Redis integration for logout
- **Automatic Expiry**: Time-based token invalidation
- **Role-Based Access**: Admin and user permission levels

### Key Components

#### JWT Handler (`security/jwt_handler.py`)
```python
# Token creation and validation
create_access_token(user_id: int) -> str
verify_token(token: str) -> dict
hash_password(password: str) -> str
verify_password(plain: str, hashed: str) -> bool
```

#### Auth Middleware (`security/auth_middleware.py`)
```python
# Request authentication
@app.middleware("http")
async def auth_middleware(request: Request, call_next)
```

#### User Model (`models/user.py`)
```python
class UserDB(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
```

## 🌐 API Endpoints

### Authentication Routes (`/auth`)

```python
POST /auth/login          # User authentication
POST /auth/refresh        # Token renewal
POST /auth/logout         # User logout
GET  /auth/verify         # Token verification
```

### Protected Routes

```python
GET  /protected          # Test protected access
GET  /health            # Health check
POST /orchestrator/preview    # Preview analysis workflow
POST /orchestrator/execute    # Execute analysis tasks
```

### Example Usage

#### Login Request
```python
import requests

response = requests.post("http://localhost:8000/auth/login", json={
    "username": "admin",
    "password": "password123"
})

data = response.json()
access_token = data["access_token"]
```

#### Protected Request
```python
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("http://localhost:8000/protected", headers=headers)
```

## 🤖 AI Agent System

### Agent Architecture

The backend implements a sophisticated multi-agent system:

#### Collector Agent (`agents/collector.py`)
- **Purpose**: Gather weather data from APIs and databases
- **Features**: Multi-source data collection, data validation
- **Output**: Structured weather datasets

#### Orchestrator Agent (`agents/orchestrator.py`)
- **Purpose**: Coordinate agent workflows and task distribution
- **Features**: Workflow management, agent communication
- **Output**: Coordinated analysis results

#### Trend Agent (`agents/trend.py`, `agents/TrendAgent.py`)
- **Purpose**: Analyze patterns and generate predictive insights
- **Features**: Statistical analysis, trend identification
- **Output**: Trend reports and predictions

#### Report Agent (`agents/report.py`)
- **Purpose**: Generate comprehensive analysis reports
- **Features**: PDF generation, data visualization
- **Output**: Formatted reports and summaries

### Agent Communication

```python
# Example agent workflow
from agents.orchestrator import OrchestratorAgent

orchestrator = OrchestratorAgent()
result = await orchestrator.execute_workflow({
    "query": "Analyze weather trends for Colombo",
    "include_predictions": True,
    "output_format": "detailed"
})
```

## 🗄️ Database Configuration

### Models

#### User Management
```python
class UserDB(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime
```

### Database Operations

#### Initialization (`init_db.py`)
- Creates database tables
- Sets up indexes and constraints
- Initializes default data

#### Admin Creation (`create_admin.py`)
- Creates default admin user
- Sets up initial permissions
- Configures system defaults

### Connection Management

```python
# Database configuration (db_config.py)
DATABASE_URL = "postgresql://user:pass@localhost/geospatial_ops"
engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine)
```

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/geospatial_ops
DB_HOST=localhost
DB_PORT=5432
DB_NAME=geospatial_ops
DB_USER=postgres
DB_PASSWORD=password

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# External APIs
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Security Settings
BCRYPT_ROUNDS=12
PASSWORD_MIN_LENGTH=8
```

## 🧪 Testing

### Test Suite

The backend includes comprehensive tests:

#### Authentication Tests (`test_auth.py`)
- Login/logout functionality
- Token validation
- Password hashing
- Protected route access

#### Environment Tests (`test_environment.py`)
- Configuration validation
- Database connectivity
- API key verification

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python test_auth.py

# Run with verbose output
python -m pytest -v

# Integration testing
python ../test_integration.py
```

### Test Coverage

Current test coverage includes:
- ✅ JWT token generation/validation (7/8 tests passing)
- ✅ User authentication flow
- ✅ Protected route access
- ✅ Password hashing/verification
- ✅ Database operations
- ✅ API endpoint responses

## 🚀 Deployment

### Production Setup

#### Using Gunicorn
```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Using Docker
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### Environment Configuration

For production, update:
- **JWT_SECRET_KEY**: Use a strong, random key
- **DATABASE_URL**: Production database connection
- **DEBUG**: Set to `False`
- **ALLOWED_ORIGINS**: Restrict to your domain
- **API Keys**: Use production API credentials

### Performance Optimization

- **Connection Pooling**: Configure database connection pools
- **Caching**: Implement Redis for token blacklisting
- **Rate Limiting**: Add request rate limiting
- **Monitoring**: Set up application monitoring

## 🔍 Monitoring & Logging

### Health Checks

```python
GET /health
{
    "status": "healthy",
    "timestamp": "2025-09-27T12:00:00Z",
    "database": "connected",
    "agents": "operational"
}
```

### Logging Configuration

The application logs:
- **Authentication events**: Login attempts, token validation
- **API requests**: Endpoint access, response times
- **Agent activities**: Workflow executions, data processing
- **Database operations**: Queries, connection status

## 🔧 Development

### Code Quality

- **Type Hints**: Full Python type annotation
- **Pydantic Models**: Data validation and serialization
- **Async/Await**: Non-blocking operations
- **Error Handling**: Comprehensive exception management

### Development Tools

```bash
# Code formatting
black .

# Linting
flake8 .

# Type checking
mypy .

# Security scanning
bandit -r .
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check PostgreSQL is running
   pg_ctl status
   
   # Test connection
   psql -h localhost -U postgres -d geospatial_ops
   ```

2. **JWT Token Issues**
   ```bash
   # Verify JWT secret in .env
   JWT_SECRET_KEY=your-secret-key
   
   # Check token expiry settings
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   which python  # Should point to .venv
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **API Key Errors**
   ```bash
   # Verify external API keys in .env
   GROQ_API_KEY=gsk_...
   SERPAPI_API_KEY=...
   ```

### Debug Mode

Enable debug logging:
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set in .env
DEBUG=True
LOG_LEVEL=DEBUG
```

## 📞 Support

For backend-specific issues:

1. **Check server logs** for detailed error messages
2. **Verify database connectivity** and credentials
3. **Test API endpoints** using `/docs` interface
4. **Validate environment variables** in `.env` file
5. **Run authentication tests** to verify JWT system

## 🎯 Next Steps

### Enhancements

- **API Versioning**: Implement versioned endpoints
- **Rate Limiting**: Add request throttling
- **Websockets**: Real-time communication features  
- **Caching Layer**: Redis integration for performance
- **Background Tasks**: Celery for long-running operations

### Security Improvements

- **OAuth Integration**: Third-party authentication
- **RBAC System**: Fine-grained permissions
- **API Key Management**: Service-to-service authentication
- **Audit Logging**: Comprehensive security logging

### Monitoring & Operations

- **Health Metrics**: Detailed system health reporting
- **Performance Monitoring**: APM integration
- **Alerting**: Automated issue detection
- **Backup Systems**: Database backup automation

---

**Happy Backend Development! ⚡**

*For frontend setup, see `../frontend/README.md`*