# 🌍 Geospatial Information Operations (GIS)

> **An intelligent climate data platform with 28 years of historical weather data, AI-powered insights, and tier-based access control for comprehensive environmental monitoring.**

## 🔍 Project Overview

The **Geospatial Information Operations** project is a comprehensive platform that combines geospatial data analysis, weather prediction, and intelligent data processing using multi-agent systems. The application provides real-time weather insights, predictive analytics, and interactive dashboards for environmental monitoring and decision-making.

**Key Highlights:**
- 📊 **52,435 Historical Weather Records** (1997-2025) covering 5 major Sri Lankan cities
- 🎯 **Tier-Based Access System** with Free, Researcher, and Professional plans
- 📥 **Historical Data Download** with CSV and JSON export capabilities
- 🛡️ **Comprehensive Security Monitoring** with AI-powered threat detection
- ⚖️ **AI Ethics Dashboard** with bias detection and fairness monitoring
- 📰 **Real-Time Climate News** collection and analysis

### 🎯 Key Features

- **🔐 JWT Authentication System**: Complete token-based authentication with access/refresh tokens, password hashing, and protected routes
- **📥 Historical Data Download**: Export weather data (CSV/JSON) with tier-enforced date ranges
- **🎚️ Tier-Based Access Control**: Free (30 days), Researcher (1 year), Professional (unlimited)
- **🤖 AI-Powered Weather Analysis**: Multi-agent system using LangGraph for intelligent data collection and analysis
- **📊 Interactive Dashboards**: Real-time visualization of weather patterns, trends, and predictions with protected access
- **🌡️ Weather Prediction**: Machine learning models for temperature, humidity, and weather forecasting
- **💬 Intelligent Chat Interface**: Natural language queries for weather data and insights
- **🗄️ Database Integration**: PostgreSQL with geospatial capabilities and comprehensive data model (20 tables)
- **👥 Role-Based Access Control**: Admin dashboard with user management and secure authentication
- **📈 Trend Analysis**: Historical data analysis and future trend predictions
- **🛡️ Security Monitoring**: Real-time threat detection, incident tracking, and audit logging
- **⚖️ AI Ethics Dashboard**: Bias detection, fairness metrics, and ethical AI monitoring
- **💳 Payment Integration**: Stripe-powered subscription management with checkout sessions
- **🌐 RESTful API**: FastAPI backend with JWT-secured endpoints and tier enforcement

### 💎 Tier System

| Feature | 🆓 Free | 🔬 Researcher | 💼 Professional |
|---------|---------|--------------|-----------------|
| **Historical Data Access** | Last 30 days | Last 1 year | Full 28 years (1997-2025) |
| **API Calls per Month** | 5 | 5,000 | Unlimited |
| **Data Downloads per Month** | 10 | 500 | Unlimited |
| **Reports per Month** | 5 | 100 | Unlimited |
| **Export Formats** | CSV only | CSV, JSON | CSV, JSON, Parquet |
| **Price** | $0/month | $29/month | $99/month |

### 🏗️ Architecture

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  React Frontend  │    │  FastAPI Backend │    │  PostgreSQL DB   │
│  (Vite+Tailwind) │◄──►│  (Python + AI)   │◄──►│  (20 Tables)     │
└──────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ User Interface   │    │   AI Agents      │    │  Data Sources    │
│ • Dashboard      │    │ • Collector      │    │ • Historical     │
│ • Weather Form   │    │ • Orchestrator   │    │ • Real-time      │
│ • Chat System    │    │ • Trend Agent    │    │ • Predictions    │
│ • Data Download  │    │ • Report Agent   │    │ • News APIs      │
│ • Analytics      │    │ • Security Agent │    │ • Weather APIs   │
│ • Ethics Monitor │    │ • News Collector │    │ • Stripe API     │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

### 🤖 AI Agent System

The backend employs a sophisticated multi-agent architecture:

- **🔍 Collector Agent**: Gathers weather data from multiple APIs and databases
- **🎯 Orchestrator Agent**: Coordinates data processing and agent communication  
- **📈 Trend Agent**: Analyzes patterns and generates predictive insights
- **📝 Report Agent**: Creates comprehensive weather reports and summaries
- **🛡️ Security Agent**: Monitors threats, detects anomalies, and logs security events
- **⚖️ Responsible AI Agent**: Detects bias, monitors fairness, validates data quality
- **📰 News Collector Agent**: Aggregates climate news from multiple sources

### 🗄️ Database Schema

**20 Tables, 52,435+ Records** (See `services/data/GISDb_schema.sql` for complete schema)

**Core Tables:**
- `users` - User accounts with tier management (Free/Researcher/Professional)
- `weather_data` - 52,435 historical weather records (1997-2025) across 5 cities
- `usage_metrics` - API usage tracking for tier enforcement
- `notifications` - User alerts and system notifications

**Business Tables:**
- `payments` - Subscription payment records
- `checkout_sessions` - Stripe checkout session management
- `news_articles` - Climate news collection with sentiment analysis

**Security Tables:**
- `security_alerts` - Real-time threat detection alerts
- `security_incidents` - Incident tracking and response
- `security_audit_log` - Security action auditing
- `auth_events` - Authentication event logging
- `api_access_log` - API request logging and monitoring
- `network_traffic` - Network activity monitoring
- `system_metrics` - System performance tracking

**AI Ethics Tables:**
- `ai_decision_audit` - AI model decision tracking and explainability
- `bias_detection_log` - Bias detection results and severity
- `fairness_metrics_log` - Fairness score monitoring
- `data_validation_log` - Data quality validation results
- `ethics_reports` - Generated ethics compliance reports

**Environmental Data:**
- `air_quality_data` - Air quality measurements and indices

---

## 🛠️ Technology Stack

### Frontend
- **React 19.1** - Modern UI framework
- **Vite 7.1** - Fast build tool and dev server
- **Tailwind CSS 4.1** - Utility-first CSS framework
- **Recharts 3.2** - Interactive data visualization
- **React Router DOM** - Client-side routing
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI 0.104** - High-performance web framework with JWT authentication
- **Python 3.10+** - Core programming language
- **JWT Authentication** - Token-based security with bcrypt password hashing
- **PostgreSQL** - Primary database with 20 tables and 52,435+ records
- **SQLAlchemy 2.0** - Database ORM with comprehensive models
- **LangGraph** - Multi-agent workflow orchestration
- **LangChain & LangChain-Groq** - AI/LLM integration framework
- **Groq API** - Language model integration
- **Stripe** - Payment processing and subscription management

### Data Science & ML
- **Pandas & NumPy** - Data manipulation and analysis
- **Scikit-learn** - Machine learning algorithms
- **Statsmodels** - Statistical modeling
- **Matplotlib, Seaborn & Plotly** - Data visualization and chart generation

### APIs & External Services
- **NewsAPI.org** - Climate news aggregation
- **Weather APIs** - Real-time weather data
- **OpenAI/Groq** - Language model services
- **Stripe API** - Payment processing

---

## 🚀 Quick Start Guide

### 🎯 For Team Members (Automated Setup)

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

✅ **This will automatically:**
- Create Python virtual environment
- Install all dependencies
- Initialize database with admin user
- Configure environment variables
- Test the complete system

📋 **Default Login:** `admin` / `password123`  
🌐 **Frontend:** http://localhost:5173  
⚡ **Backend API:** http://localhost:8000

---

### 🔧 Manual Setup (Advanced)

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL 14+**
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/SSaabir/Geospatial-Information-Operations.git
cd Geospatial-Information-Operations
```

### 2. Backend Setup (FastAPI + AI Agents)

#### Create & Activate Virtual Environment

```bash
cd services
python -m venv .venv
```

**Activate the virtual environment:**

- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

- **Windows (Command Prompt):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

- **Mac/Linux:**
  ```bash
  source .venv/bin/activate
  ```

#### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Environment Configuration

Create a `.env` file in the `services` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/GISDb

# API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_key_here
NEWS_API_KEY=your_newsapi_key_here

# Stripe Payment Integration
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# JWT Authentication
SECRET_KEY=your_secret_jwt_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server Configuration
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
```

#### Database Setup

```bash
# Create PostgreSQL database
createdb GISDb

# Import the complete schema
psql -U username -d GISDb -f services/data/GISDb_schema.sql

# Or run the database initialization script
cd services
python init_db.py
```

**Database Details:**
- 20 tables with proper indexes and foreign keys
- 52,435 pre-loaded historical weather records (1997-2025)
- Complete schema in `services/data/GISDb_schema.sql`

#### Start Backend Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

➡️ **Backend API:** [http://localhost:8000](http://localhost:8000)  
➡️ **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend Setup (React + Vite)

#### Install Dependencies

```bash
cd ../frontend
npm install
```

#### Start Development Server

```bash
npm run dev
```

➡️ **Frontend Application:** [http://localhost:5173](http://localhost:5173)

---

## 📱 Application Features

### 🏠 **User Dashboard**
- Real-time weather overview with interactive charts
- Usage metrics and tier status display
- Weather alerts and notifications
- **📥 Historical Data Download** with tier-based access:
  - City selection (Colombo, Jaffna, Kandy, Matara, Trincomalee)
  - Date range picker with automatic tier validation
  - Export formats: CSV and JSON
  - Real-time download progress and error handling
  - Upgrade prompts for users exceeding tier limits
- News section with latest climate updates
- Quick access to key metrics and forecasts

### 🌡️ **Weather Predictor**
- Input weather parameters for any of 5 cities
- AI-powered predictions using machine learning models
- Historical data comparison (28 years of data)
- Confidence intervals and accuracy metrics
- Visualization of prediction results
- Batch prediction capabilities

### 💬 **Intelligent Chat**
- Natural language weather queries
- AI agent responses with context awareness
- Data visualization in chat interface
- Multi-turn conversations with memory
- Support for complex queries about trends and patterns

### 📊 **Analytics Dashboard**
- Comprehensive trend analysis and forecasting
- Historical data visualization (1997-2025)
- Performance metrics and model accuracy
- Interactive charts powered by Recharts
- Export capabilities with tier enforcement
- Comparative analysis across cities

### �️ **Security Dashboard** (Admin Only)
- Real-time threat monitoring and alerts
- Security incident tracking and response
- Audit log viewer with filtering
- Network traffic analysis
- System metrics monitoring
- API access logging and rate limiting

### ⚖️ **AI Ethics Dashboard** (Admin Only)
- Bias detection results and severity tracking
- Fairness metrics monitoring across demographics
- Model decision audit trail with explainability
- Data quality validation reports
- Temporal bias analysis (Morning/Afternoon/Evening/Night)
- Ethics compliance reports generation

### 👤 **User Management** (Admin Only)
- Secure JWT-based authentication
- User profiles with tier assignment
- Subscription management and billing
- Role-based access control (User/Admin)
- Usage tracking and tier enforcement
- Account upgrade/downgrade workflows

### 💳 **Billing & Payments**
- Stripe-powered subscription management
- Secure checkout process with session tracking
- Payment history and invoicing
- Automatic tier upgrades after payment
- Subscription renewal reminders
- Multiple payment methods support

---

## 🔧 Development

### Project Structure
```
Geospatial-Information-Operations/
├── frontend/                          # React application
│   ├── src/
│   │   ├── components/               # Reusable UI components
│   │   │   ├── HistoricalDataDownload.jsx  # Data download component
│   │   │   ├── NewsAlerts.jsx        # News display component
│   │   │   ├── WeatherChart.jsx      # Weather visualization
│   │   │   └── ...                   # Other UI components
│   │   ├── pages/                    # Application pages
│   │   │   ├── Dashboard.jsx         # Main user dashboard
│   │   │   ├── WeatherPredictor.jsx  # Prediction interface
│   │   │   ├── Chat.jsx              # AI chat interface
│   │   │   ├── SecurityDashboard.jsx # Security monitoring
│   │   │   ├── AIEthicsDashboard.jsx # Ethics monitoring
│   │   │   └── AdminDashboard.jsx    # Admin panel
│   │   ├── contexts/                 # React contexts
│   │   │   ├── AuthContext.jsx       # Authentication state
│   │   │   └── ThemeContext.jsx      # Theme management
│   │   └── assets/                   # Static assets
│   ├── package.json                  # Frontend dependencies
│   └── vite.config.js               # Vite configuration
│
├── services/                         # FastAPI backend
│   ├── agents/                       # AI agent implementations
│   │   ├── collector.py             # Data collection agent
│   │   ├── orchestrator.py          # Agent orchestration
│   │   ├── trend.py                 # Trend analysis agent
│   │   ├── news_collector.py        # News aggregation agent
│   │   ├── security_agent.py        # Security monitoring agent
│   │   ├── responsible_ai.py        # AI ethics agent
│   │   └── report.py                # Report generation agent
│   │
│   ├── api/                          # API endpoints (20 files)
│   │   ├── auth.py                  # Authentication endpoints
│   │   ├── dashboard_api.py         # Dashboard data (no mock data)
│   │   ├── historical_api.py        # Historical data with tier enforcement
│   │   ├── forecast_api.py          # Weather predictions
│   │   ├── chat_api.py              # AI chat interface
│   │   ├── news_api.py              # News aggregation
│   │   ├── security_api.py          # Security monitoring
│   │   ├── security_dashboard_api.py # Security dashboard data
│   │   ├── ai_ethics_api.py         # AI ethics monitoring
│   │   ├── ai_ethics_dashboard_api.py # Ethics dashboard (no mock data)
│   │   ├── analytics_api.py         # Analytics endpoints
│   │   ├── admin_api.py             # Admin operations
│   │   ├── billing_api.py           # Subscription management
│   │   ├── payments_api.py          # Payment processing
│   │   └── ...                      # Other API modules
│   │
│   ├── models/                       # Database models
│   │   ├── user.py                  # User model with tiers
│   │   ├── news.py                  # News article model
│   │   └── usage.py                 # Usage tracking model
│   │
│   ├── middleware/                   # Middleware components
│   │   ├── error_handlers.py        # Error handling
│   │   └── event_logger.py          # Event logging
│   │
│   ├── security/                     # Security components
│   │   ├── auth_middleware.py       # JWT authentication
│   │   └── jwt_handler.py           # Token management
│   │
│   ├── schedulers/                   # Background tasks
│   │   └── unified_daily_collector.py # Daily data collection
│   │
│   ├── utils/                        # Utility functions
│   │   ├── notification_manager.py  # Notification system
│   │   └── tier.py                  # Tier enforcement logic
│   │
│   ├── data/                         # Data files and schemas
│   │   ├── GISDb_schema.sql         # Complete database schema (20 tables)
│   │   ├── preprocessed/            # Preprocessed datasets
│   │   └── raw/                     # Raw data files
│   │
│   ├── scripts/                      # Utility scripts (moved from root)
│   │   ├── check_news_db.py         # Database inspection tool
│   │   ├── seed_news.py             # Initial data seeding
│   │   ├── get_schema.py            # Schema export utility
│   │   ├── test_historical_access.py # Tier testing
│   │   └── test_real_news.py        # News API testing
│   │
│   ├── visualizations/               # Generated charts (5 recent sessions)
│   │   └── session_*/               # Chart output folders
│   │
│   ├── main.py                       # FastAPI application entry
│   ├── db_config.py                 # Database configuration
│   ├── requirements.txt             # Python dependencies (cleaned, 60 packages)
│   └── .env                         # Environment variables
│
└── README.md                         # Project documentation
```

**Key Directories:**
- `frontend/src/components/` - 20+ reusable React components
- `services/api/` - 20 API modules covering all features
- `services/agents/` - 7 specialized AI agents
- `services/models/` - 3 core database models
- `services/data/` - Complete database schema and datasets
- `services/scripts/` - 5 maintenance and testing utilities

### Available Scripts

#### Frontend
```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

#### Backend
```bash
uvicorn main:app --reload    # Development server
python -m pytest            # Run tests
black .                      # Format code
flake8 .                    # Lint code
```

### API Endpoints

**Base URL:** `http://localhost:8000`  
**API Documentation:** `http://localhost:8000/docs` (Swagger UI)

#### 🔐 Authentication Endpoints (`/auth`)
- `POST /auth/login` - User login with JWT token response
- `POST /auth/register` - New user registration
- `POST /auth/refresh` - Refresh JWT access token
- `POST /auth/logout` - Logout and invalidate token
- `GET /auth/me` - Get current user profile
- `PUT /auth/profile` - Update user profile

#### 📥 Historical Data Endpoints (`/historical`)
- `POST /historical/weather` - Download historical weather data (tier-enforced)
  - **Request Body:**
    ```json
    {
      "city": "Colombo",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "format": "csv"
    }
    ```
  - **Tier Limits:**
    - Free: Last 30 days only
    - Researcher: Last 365 days only
    - Professional: Full 28 years (1997-2025)
  - **Response:** CSV or JSON data with weather records
  
- `GET /historical/access-limits` - Get user's historical access limits
- `GET /historical/cities` - List available cities for download

#### 📊 Dashboard Endpoints (`/dashboard`)
- `GET /dashboard/weather/current` - Current weather for user's default city
- `GET /dashboard/weather/trends` - Weather trends (last 7 days)
- `GET /dashboard/usage` - User's API usage metrics
- `GET /dashboard/notifications` - User notifications
- `GET /dashboard/news` - Latest climate news articles

#### 🌡️ Weather Prediction Endpoints (`/forecast`)
- `POST /forecast/predict` - Generate weather predictions
- `GET /forecast/models` - List available ML models
- `GET /forecast/accuracy` - Model accuracy metrics

#### 💬 Chat Interface Endpoints (`/chat`)
- `POST /chat/query` - Send query to AI agents
- `GET /chat/history` - Get chat conversation history
- `DELETE /chat/history` - Clear chat history

#### 📰 News Endpoints (`/news`)
- `GET /news/articles` - Get climate news articles
- `GET /news/latest` - Get latest news (last 24 hours)
- `POST /news/collect` - Trigger news collection (admin only)

#### 🛡️ Security Endpoints (`/security`)
- `GET /security/alerts` - Get security alerts
- `GET /security/incidents` - Get security incidents
- `GET /security/audit-log` - Get audit log entries
- `GET /security/metrics` - Get system security metrics

#### 🛡️ Security Dashboard Endpoints (`/security-dashboard`)
- `GET /security-dashboard/overview` - Security overview statistics
- `GET /security-dashboard/alerts` - Recent security alerts
- `GET /security-dashboard/incidents` - Security incident tracking
- `GET /security-dashboard/network-traffic` - Network activity analysis

#### ⚖️ AI Ethics Endpoints (`/ai-ethics`)
- `GET /ai-ethics/bias-detection` - Bias detection results
- `GET /ai-ethics/fairness-metrics` - Fairness score monitoring
- `GET /ai-ethics/decisions` - AI decision audit trail
- `POST /ai-ethics/validate-data` - Validate data quality

#### ⚖️ AI Ethics Dashboard Endpoints (`/ai-ethics-dashboard`)
- `GET /ai-ethics-dashboard/overview` - Ethics overview with calculated metrics
- `GET /ai-ethics-dashboard/bias-trends` - Temporal bias analysis (no mock data)
- `GET /ai-ethics-dashboard/fairness-scores` - Real-time fairness metrics

#### 📈 Analytics Endpoints (`/analytics`)
- `GET /analytics/trends` - Weather trend analysis
- `GET /analytics/patterns` - Pattern detection results
- `GET /analytics/reports` - Generated analytics reports

#### 💳 Billing Endpoints (`/billing`)
- `GET /billing/subscription` - Get user's subscription details
- `POST /billing/upgrade` - Upgrade to higher tier
- `GET /billing/usage` - Get billing usage summary

#### 💳 Payment Endpoints (`/payments`)
- `POST /payments/create-checkout` - Create Stripe checkout session
- `POST /payments/webhook` - Handle Stripe webhooks
- `GET /payments/history` - Get payment history

#### 👥 Admin Endpoints (`/admin`)
- `GET /admin/users` - List all users
- `PUT /admin/users/{id}/tier` - Update user tier
- `GET /admin/system-stats` - System statistics
- `POST /admin/run-collector` - Manually trigger data collection

#### 🤖 Orchestrator Endpoints (`/orchestrator`)
- `POST /orchestrator/preview` - Preview orchestrator workflow
- `POST /orchestrator/execute` - Execute orchestrator tasks
- `GET /orchestrator/status` - Get orchestrator status

#### 🏥 Health Check
- `GET /health` - API health check endpoint

---

## 🧪 Testing

### Run Backend Tests
```bash
cd services
pytest tests/ -v
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

---

## � Historical Data Download Feature

### Overview
Users can download historical weather data directly from the dashboard with tier-based access control:

- **Free Tier**: Last 30 days of data
- **Researcher Tier**: Last 1 year of data
- **Professional Tier**: Full 28 years (1997-2025)

### Features
- **City Selection**: Choose from 5 major Sri Lankan cities (Colombo, Jaffna, Kandy, Matara, Trincomalee)
- **Date Range Picker**: Select custom date ranges within tier limits
- **Export Formats**: Download as CSV or JSON
- **Automatic Validation**: System prevents requests exceeding tier limits
- **Real-time Feedback**: Progress indicators and error messages
- **Upgrade Prompts**: Encourages tier upgrades for more data access

### Usage Example

**Frontend Component:**
```jsx
import HistoricalDataDownload from '../components/HistoricalDataDownload';

// In your Dashboard
<HistoricalDataDownload />
```

**API Call:**
```javascript
const response = await fetch('http://localhost:8000/historical/weather', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify({
    city: 'Colombo',
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    format: 'csv'
  })
});

const data = await response.json();
// Trigger browser download
const blob = new Blob([data.csv_data], { type: 'text/csv' });
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'Colombo_weather_2024-01-01_2024-12-31.csv';
a.click();
```

**Backend Tier Enforcement:**
```python
# In historical_api.py
if user.tier == "free":
    max_days = 30
elif user.tier == "researcher":
    max_days = 365
else:  # professional
    max_days = None  # unlimited

# Validate date range
if max_days and (end_date - start_date).days > max_days:
    raise HTTPException(
        status_code=403,
        detail=f"Your {user.tier} plan only allows access to the last {max_days} days"
    )
```

### Data Structure

**CSV Format:**
```csv
date,city,temperature,humidity,wind_speed,pressure,precipitation,weather_condition
2024-01-01,Colombo,28.5,75,12.3,1013.2,0.0,Partly Cloudy
2024-01-02,Colombo,29.1,72,10.8,1012.8,2.5,Light Rain
...
```

**JSON Format:**
```json
{
  "city": "Colombo",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "records": [
    {
      "date": "2024-01-01",
      "temperature": 28.5,
      "humidity": 75,
      "wind_speed": 12.3,
      "pressure": 1013.2,
      "precipitation": 0.0,
      "weather_condition": "Partly Cloudy"
    },
    ...
  ]
}
```

## �🚀 Deployment

### Production Build

#### Frontend
```bash
cd frontend
npm run build
# Deploy dist/ folder to your web server or CDN

# For preview
npm run preview
```

**Environment Variables for Production:**
Create `.env.production` in `frontend/`:
```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

#### Backend
```bash
cd services

# Install production dependencies
pip install gunicorn

# Run with Gunicorn (recommended for production)
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -

# Or with Uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Production Environment Variables:**
Create `.env.production` in `services/`:
```env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db-host:5432/GISDb
SECRET_KEY=your_very_secure_secret_key_here
STRIPE_SECRET_KEY=sk_live_...
# ... other production keys
```

### Docker Deployment (Optional)

**Dockerfile for Backend:**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: GISDb
      POSTGRES_USER: gis_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./services/data/GISDb_schema.sql:/docker-entrypoint-initdb.d/schema.sql
  
  backend:
    build: ./services
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://gis_user:secure_password@db:5432/GISDb
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up --build -d
```

### Database Migration for Production

```bash
# Backup existing data
pg_dump -U username GISDb > backup_$(date +%Y%m%d).sql

# Apply schema
psql -U username -d GISDb -f services/data/GISDb_schema.sql

# Verify tables
psql -U username -d GISDb -c "\dt"
```

### Monitoring & Maintenance

**Daily Data Collection:**
Schedule the unified daily collector:
```bash
# Linux/Mac crontab
0 2 * * * cd /path/to/services && python schedulers/unified_daily_collector.py

# Windows Task Scheduler
# Use schedulers/start_collector.bat
```

**Database Maintenance:**
```sql
-- Analyze tables for query optimization
ANALYZE weather_data;
ANALYZE news_articles;

-- Vacuum to reclaim space
VACUUM ANALYZE;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🔧 Maintenance Scripts

Located in `services/scripts/`:

- **`check_news_db.py`** - Inspect news articles in database
- **`seed_news.py`** - Seed initial news articles
- **`get_schema.py`** - Export database schema to SQL file
- **`test_historical_access.py`** - Test tier-based historical access limits
- **`test_real_news.py`** - Test NewsAPI integration

```bash
cd services/scripts

# Check news collection
python check_news_db.py

# Export current database schema
python get_schema.py

# Test historical access tiers
python test_historical_access.py
```

## 📊 Data Statistics

**Current Database Metrics:**
- **Total Weather Records**: 52,435
- **Date Range**: January 1, 1997 - October 16, 2025
- **Cities Covered**: 5 (Colombo, Jaffna, Kandy, Matara, Trincomalee)
- **Time Span**: 28 years of historical data
- **Database Tables**: 20
- **Total Database Size**: ~500MB (with indexes)

**Weather Data Coverage:**
- Temperature (°C)
- Humidity (%)
- Wind Speed (km/h)
- Atmospheric Pressure (hPa)
- Precipitation (mm)
- Weather Conditions
- Cloud Cover (%)
- UV Index
- Visibility (km)
- And 19 more parameters...

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Password Hashing**: Bcrypt hashing with salt for password security
- **Rate Limiting**: Tier-based API rate limiting (5, 5000, unlimited calls/month)
- **Audit Logging**: Comprehensive logging of all API access and security events
- **Threat Detection**: Real-time security alert monitoring
- **Incident Tracking**: Security incident management system
- **Network Monitoring**: Traffic analysis and anomaly detection
- **Data Validation**: Input sanitization and validation for all endpoints

## ⚖️ AI Ethics & Responsible AI

- **Bias Detection**: Continuous monitoring for model bias across demographics
- **Fairness Metrics**: Real-time fairness scoring and reporting
- **Decision Auditing**: Complete audit trail of AI model decisions
- **Temporal Analysis**: Track bias patterns across different time periods
- **Data Quality Validation**: Automated data quality checks
- **Ethics Reports**: Automated generation of ethics compliance reports
- **Transparency**: Model explainability and decision reasoning

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation
4. **Test your changes**
   ```bash
   # Backend tests
   cd services
   pytest tests/
   
   # Frontend tests
   cd frontend
   npm test
   ```
5. **Commit with clear messages**
   ```bash
   git commit -m 'Add amazing feature: detailed description'
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure CI/CD checks pass

**Contribution Areas:**
- 🐛 Bug fixes
- ✨ New features (especially new ML models)
- 📝 Documentation improvements
- 🧪 Test coverage expansion
- 🎨 UI/UX enhancements
- 🌍 Additional city/country support
- 🔒 Security improvements

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Saabir** - [SSaabir](https://github.com/SSaabir)

### Project Team
- **Backend Development**: FastAPI, AI Agents, Database Architecture
- **Frontend Development**: React, Tailwind CSS, Data Visualization
- **Data Science**: Machine Learning Models, Statistical Analysis
- **Security**: Authentication, Monitoring, Threat Detection
- **AI Ethics**: Bias Detection, Fairness Monitoring

---

## 🙏 Acknowledgments

- **Weather Data**: Historical weather data from multiple meteorological sources
- **AI Capabilities**: Powered by Groq AI and OpenAI GPT models
- **News Aggregation**: NewsAPI.org for climate news collection
- **Payment Processing**: Stripe for secure subscription management
- **Database**: PostgreSQL for robust data storage and geospatial support
- **Open Source Libraries**:
  - FastAPI, React, Tailwind CSS
  - LangChain, LangGraph for AI orchestration
  - Scikit-learn, Pandas, NumPy for data science
  - Recharts, Plotly for data visualization
- **Community**: Open source contributors and maintainers

---

## 📞 Support

For questions, issues, or feature requests:

- **GitHub Issues**: [Create an issue](https://github.com/SSaabir/Geospatial-Information-Operations/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SSaabir/Geospatial-Information-Operations/discussions)
- **Email**: [Contact the maintainer](mailto:saabir@example.com)

---

## 🗺️ Roadmap

**Upcoming Features:**
- [ ] Mobile app development (React Native)
- [ ] More cities and countries coverage
- [ ] Advanced ML models (LSTM, Transformer-based)
- [ ] Real-time weather station data integration
- [ ] Satellite imagery integration
- [ ] Climate change impact analysis
- [ ] API v2 with GraphQL support
- [ ] WebSocket support for real-time updates
- [ ] Multi-language support (i18n)
- [ ] Dark mode theme
- [ ] Export to more formats (Parquet, Excel)
- [ ] Automated report scheduling

**Recent Updates:**
- ✅ **v1.5.0** - Historical data download with tier enforcement (October 2025)
- ✅ **v1.4.0** - AI Ethics Dashboard with bias detection (October 2025)
- ✅ **v1.3.0** - Security monitoring dashboard (October 2025)
- ✅ **v1.2.0** - News collection and aggregation (October 2025)
- ✅ **v1.1.0** - Tier-based subscription system (October 2025)
- ✅ **v1.0.0** - Initial release with 28 years of historical data (October 2025)

---

## 📈 Performance

**System Benchmarks:**
- API Response Time: < 100ms (p95)
- Database Queries: < 50ms (with proper indexing)
- Historical Data Export: ~2 seconds for 1 year of data
- ML Predictions: < 500ms per request
- Concurrent Users Supported: 1000+ (with proper scaling)
- Uptime: 99.9% SLA target

**Optimization Techniques:**
- Database indexing on frequently queried columns
- Caching for frequently accessed data
- Asynchronous processing for heavy operations
- Connection pooling for database connections
- CDN for static assets delivery
- Efficient SQL queries (no N+1 problems)

---

**⭐ If you find this project helpful, please star the repository!**

**💼 For commercial use or enterprise support, please contact the maintainer.**