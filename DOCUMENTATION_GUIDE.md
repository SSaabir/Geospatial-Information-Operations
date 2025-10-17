# 📚 Documentation Reference Guide
## Geospatial Information Operations Platform

> **Last Updated:** October 17, 2025  
> **Purpose:** Complete guide to all documentation, where to find it, and what to review for each component

---

## 🗂️ Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & System Design](#architecture--system-design)
3. [Database & Data Models](#database--data-models)
4. [AI & Machine Learning](#ai--machine-learning)
5. [Responsible AI & Ethics](#responsible-ai--ethics)
6. [Security & Authentication](#security--authentication)
7. [API Documentation](#api-documentation)
8. [Frontend Components](#frontend-components)
9. [Deployment & DevOps](#deployment--devops)
10. [Testing & Quality Assurance](#testing--quality-assurance)
11. [Data Collection & Schedulers](#data-collection--schedulers)
12. [Billing & Payments](#billing--payments)

---

## 📖 Project Overview

### **Primary Documentation**
| Document | Location | What to Review |
|----------|----------|----------------|
| **Main README** | `/README.md` | Complete project overview, setup instructions, features, tier system |
| **Backend README** | `/services/README.md` | Backend architecture, API structure, agent system |
| **Frontend README** | `/frontend/README.md` | React app structure, components, routing |
| **Schedulers README** | `/services/schedulers/README.md` | Daily data collection process, cron jobs |

### **When to Use:**
- 🆕 **New team members** → Start with Main README
- 🔧 **Setup & Installation** → Main README + Backend README
- 📱 **Frontend Development** → Frontend README
- ⚙️ **Understanding Features** → Main README (Features section)

---

## 🏗️ Architecture & System Design

### **Key Documents**
| Document | Location | What to Review |
|----------|----------|----------------|
| **Main README** | `/README.md` | System architecture diagram, technology stack |
| **Database Schema** | `/services/data/GISDb_schema.sql` | Complete 20-table database structure |
| **API Structure** | `/services/api/` (20+ files) | All endpoint implementations |

### **Key Files to Review:**
```
services/
├── main.py                    # FastAPI app entry point, all routers registered
├── db_config.py              # Database configuration and connection management
├── agents/
│   └── orchestrator.py       # Multi-agent coordination logic
└── api/
    ├── dashboard_api.py      # Dashboard data endpoints
    ├── historical_api.py     # Historical data with tier enforcement
    └── ...                   # 18+ other API modules
```

### **When to Use:**
- 🏗️ **System Design Review** → Main README + main.py
- 💾 **Database Changes** → GISDb_schema.sql
- 🔌 **API Integration** → Specific API files in `/services/api/`

---

## 💾 Database & Data Models

### **Primary Documentation**
| Document | Location | What to Review |
|----------|----------|----------------|
| **Database Schema** | `/services/data/GISDb_schema.sql` | All 20 tables, indexes, constraints |
| **User Model** | `/services/models/user.py` | User table, tier system, authentication |
| **Usage Model** | `/services/models/usage.py` | API usage tracking, rate limiting |
| **News Model** | `/services/models/news.py` | News article collection structure |

### **Tables by Category:**

#### **Core Tables** (Review: `/services/data/GISDb_schema.sql` lines 1-200)
- `users` - User accounts, tier management, authentication
- `weather_data` - 52,435 historical records (1997-2025)
- `usage_metrics` - API usage tracking
- `notifications` - User alerts

#### **Business Tables** (Review: lines 200-350)
- `payments` - Subscription payments
- `checkout_sessions` - Stripe checkout management
- `news_articles` - Climate news with sentiment analysis

#### **Security Tables** (Review: lines 350-550)
- `security_alerts` - Real-time threat detection
- `security_incidents` - Incident tracking
- `security_audit_log` - Security action auditing
- `auth_events` - Authentication logging
- `api_access_log` - API request monitoring
- `network_traffic` - Network activity
- `system_metrics` - System performance

#### **AI Ethics Tables** (Review: lines 550-750)
- `ai_decision_audit` - AI model decision tracking
- `bias_detection_log` - Bias detection results
- `fairness_metrics_log` - Fairness score monitoring
- `data_validation_log` - Data quality validation
- `ethics_reports` - Ethics compliance reports

#### **Environmental Data** (Review: lines 750-end)
- `air_quality_data` - Air quality measurements

### **When to Use:**
- 🗄️ **Database Migrations** → GISDb_schema.sql
- 👤 **User Management** → models/user.py + users table definition
- 📊 **Usage Tracking** → models/usage.py + usage_metrics table
- 🛡️ **Security Audit** → All security_* tables
- ⚖️ **AI Ethics Review** → All ai_*, bias_*, fairness_*, ethics_* tables

---

## 🤖 AI & Machine Learning

### **Primary Documentation**
| Document | Location | What to Review |
|----------|----------|----------------|
| **Collector Agent** | `/services/agents/collector.py` | Data collection agent, weather APIs |
| **Orchestrator Agent** | `/services/agents/orchestrator.py` | Multi-agent coordination, LangGraph |
| **Trend Agent** | `/services/agents/trend.py` | Pattern analysis, trend predictions |
| **Report Agent** | `/services/agents/report.py` | Report generation |
| **News Collector** | `/services/agents/news_collector.py` | Climate news aggregation |
| **Prediction Models** | `/services/agents/predict/` | ML models for weather prediction |

### **Key Sections:**

#### **Data Collection** (Review: `agents/collector.py`)
- Lines 1-100: Configuration and initialization
- Lines 100-300: Weather data collection logic
- Lines 300-500: Database integration
- Lines 500-732: Agent execution and tools

#### **Multi-Agent System** (Review: `agents/orchestrator.py`)
- Agent coordination using LangGraph
- Task distribution logic
- Error handling and retries

#### **Predictions** (Review: `agents/predict/`)
- ML model implementations
- Training data preprocessing
- Inference endpoints

### **When to Use:**
- 🤖 **Agent Development** → agents/orchestrator.py
- 📊 **Data Collection** → agents/collector.py
- 📈 **Trend Analysis** → agents/trend.py
- 🔮 **Prediction Logic** → agents/predict/ directory
- 📰 **News Integration** → agents/news_collector.py

---

## ⚖️ Responsible AI & Ethics

### **🎯 START HERE FOR RESPONSIBLE AI**

### **Primary Documentation**
| Document | Location | What to Review | Priority |
|----------|----------|----------------|----------|
| **Responsible AI Agent** | `/services/agents/responsible_ai.py` | **START HERE** - Core ethics implementation | ⭐⭐⭐ |
| **Security Framework** | `/services/agents/security_framework.py` | Security monitoring, threat detection | ⭐⭐⭐ |
| **AI Ethics API** | `/services/api/ai_ethics_api.py` | Ethics endpoints, bias detection API | ⭐⭐ |
| **AI Ethics Dashboard API** | `/services/api/ai_ethics_dashboard_api.py` | Dashboard data, real-time metrics | ⭐⭐ |
| **Database Schema** | `/services/data/GISDb_schema.sql` (lines 550-750) | Ethics tables structure | ⭐ |

### **Critical Files to Review:**

#### **1. Core Ethics Implementation** ⭐⭐⭐
**File:** `/services/agents/responsible_ai.py`

**What's Inside:**
- Bias detection algorithms
- Fairness metric calculations
- Data validation rules
- Decision auditing logic
- Ethics compliance checks

**Key Sections:**
```python
# Lines 1-50: Configuration and imports
# Lines 50-150: Bias detection methods
# Lines 150-250: Fairness scoring algorithms
# Lines 250-350: Data validation rules
# Lines 350-450: Decision audit trail
# Lines 450-end: Ethics report generation
```

**Review When:**
- Implementing new AI models
- Detecting bias in predictions
- Ensuring fairness across demographics
- Auditing AI decisions
- Generating ethics reports

---

#### **2. AI Ethics API Endpoints** ⭐⭐
**File:** `/services/api/ai_ethics_api.py`

**What's Inside:**
- `/ai-ethics/bias-detection` - Get bias detection results
- `/ai-ethics/fairness-metrics` - Fairness score monitoring
- `/ai-ethics/decisions` - AI decision audit trail
- `/ai-ethics/validate-data` - Data quality validation

**Review When:**
- Integrating ethics monitoring into frontend
- Creating ethics dashboards
- Accessing bias detection results
- Validating data quality

---

#### **3. AI Ethics Dashboard** ⭐⭐
**File:** `/services/api/ai_ethics_dashboard_api.py`

**What's Inside:**
- `/ai-ethics-dashboard/overview` - Ethics overview with calculated metrics
- `/ai-ethics-dashboard/bias-trends` - Temporal bias analysis (no mock data)
- `/ai-ethics-dashboard/fairness-scores` - Real-time fairness metrics

**Key Changes Made:**
- ✅ Removed mock temporal bias data (lines 102-108)
- ✅ Added real calculation from bias_detection_log table
- ✅ Calculates bias by hour from actual logs

**Review When:**
- Building ethics monitoring dashboards
- Analyzing bias patterns over time
- Tracking fairness metrics
- Generating compliance reports

---

#### **4. Database Tables for Ethics** ⭐
**File:** `/services/data/GISDb_schema.sql` (lines 550-750)

**Tables:**
```sql
-- AI Decision Auditing
CREATE TABLE ai_decision_audit (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    decision_type VARCHAR(50),
    input_data JSONB,
    output_data JSONB,
    confidence_score DECIMAL(5,4),
    explanation TEXT,
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_id VARCHAR(100)
);

-- Bias Detection
CREATE TABLE bias_detection_log (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    bias_type VARCHAR(50),
    severity DECIMAL(3,2),
    affected_groups TEXT,
    detection_method VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    remediation_status VARCHAR(50)
);

-- Fairness Metrics
CREATE TABLE fairness_metrics_log (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    metric_type VARCHAR(50),
    metric_value DECIMAL(5,4),
    demographic_group VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    threshold_passed BOOLEAN,
    notes TEXT
);

-- Data Validation
CREATE TABLE data_validation_log (
    id SERIAL PRIMARY KEY,
    validation_type VARCHAR(50),
    data_source VARCHAR(100),
    validation_result BOOLEAN,
    issues_found TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    severity VARCHAR(20)
);

-- Ethics Reports
CREATE TABLE ethics_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50),
    reporting_period VARCHAR(50),
    model_name VARCHAR(100),
    bias_score DECIMAL(5,4),
    fairness_score DECIMAL(5,4),
    compliance_status VARCHAR(50),
    recommendations TEXT,
    generated_by INTEGER REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    report_data JSONB
);
```

**Review When:**
- Setting up ethics monitoring database
- Understanding data structure for ethics
- Creating new ethics metrics
- Querying ethics data

---

### **Responsible AI Checklist** ✅

Use this checklist when implementing or reviewing AI features:

#### **Before Model Deployment:**
- [ ] Review `responsible_ai.py` bias detection methods
- [ ] Configure bias thresholds
- [ ] Set up fairness metrics logging
- [ ] Enable decision auditing
- [ ] Test with diverse datasets

#### **During Development:**
- [ ] Log all AI decisions to `ai_decision_audit` table
- [ ] Track bias scores in `bias_detection_log`
- [ ] Monitor fairness metrics in `fairness_metrics_log`
- [ ] Validate data quality using `data_validation_log`
- [ ] Review temporal bias patterns (morning/afternoon/evening/night)

#### **After Deployment:**
- [ ] Review ethics dashboard (`/ai-ethics-dashboard/overview`)
- [ ] Monitor bias trends over time
- [ ] Generate monthly ethics reports
- [ ] Review affected demographic groups
- [ ] Implement remediation for detected biases

---

### **Key Metrics to Monitor:**

**From `ai_ethics_dashboard_api.py`:**

1. **Bias Score** (0.0 - 1.0)
   - < 0.3: Low bias ✅
   - 0.3 - 0.7: Medium bias ⚠️
   - > 0.7: High bias ❌

2. **Fairness Score** (0.0 - 1.0)
   - > 0.8: Excellent ✅
   - 0.6 - 0.8: Good ⚠️
   - < 0.6: Poor ❌

3. **Temporal Bias** (by time period)
   - Morning (6-12)
   - Afternoon (12-18)
   - Evening (18-24)
   - Night (0-6)

4. **Data Quality** (validation pass rate)
   - > 95%: Excellent ✅
   - 85-95%: Good ⚠️
   - < 85%: Needs review ❌

---

### **When to Use Each Document:**

| Task | Primary Document | Secondary Documents |
|------|-----------------|---------------------|
| **Implementing bias detection** | `responsible_ai.py` | `ai_ethics_api.py`, database schema |
| **Creating ethics dashboard** | `ai_ethics_dashboard_api.py` | `responsible_ai.py` |
| **Auditing AI decisions** | `ai_decision_audit` table | `responsible_ai.py` |
| **Analyzing fairness** | `fairness_metrics_log` table | `ai_ethics_dashboard_api.py` |
| **Validating data quality** | `data_validation_log` table | `responsible_ai.py` |
| **Generating compliance reports** | `ethics_reports` table | All ethics tables |
| **Monitoring temporal bias** | `ai_ethics_dashboard_api.py` (lines 102-125) | `bias_detection_log` table |

---

## 🔒 Security & Authentication

### **Primary Documentation**
| Document | Location | What to Review |
|----------|----------|----------------|
| **Security Agent** | `/services/agents/security_agent.py` | Threat detection, anomaly detection |
| **Security Framework** | `/services/agents/security_framework.py` | Security monitoring framework |
| **Auth Middleware** | `/services/security/auth_middleware.py` | JWT authentication, route protection |
| **JWT Handler** | `/services/security/jwt_handler.py` | Token generation, validation, blacklisting |
| **Security API** | `/services/api/security_api.py` | Security alerts, incidents, audit logs |
| **Security Dashboard API** | `/services/api/security_dashboard_api.py` | Real-time security metrics |

### **Key Sections:**

#### **Authentication Flow** (Review: `security/auth_middleware.py` + `security/jwt_handler.py`)
- JWT token generation and validation
- Access token expiration (30 minutes)
- Refresh token expiration (7 days)
- Token blacklisting (optional)
- Password hashing with bcrypt

#### **Threat Detection** (Review: `agents/security_agent.py`)
- Real-time threat monitoring
- Anomaly detection algorithms
- Security alert generation
- Incident response automation

#### **Security Monitoring** (Review: `api/security_dashboard_api.py`)
- `/security-dashboard/overview` - Security overview statistics
- `/security-dashboard/alerts` - Recent security alerts
- `/security-dashboard/incidents` - Security incident tracking
- `/security-dashboard/network-traffic` - Network activity analysis

### **When to Use:**
- 🔐 **Authentication Setup** → auth_middleware.py + jwt_handler.py
- 🛡️ **Threat Detection** → security_agent.py
- 📊 **Security Monitoring** → security_dashboard_api.py
- 🔍 **Audit Logging** → security_audit_log table
- 🚨 **Incident Response** → security_incidents table

---

## 🔌 API Documentation

### **Complete API Reference**

**File:** `/README.md` (lines 500-800) - Complete API endpoint documentation

### **API Modules by Category:**

#### **Authentication** (Review: `/services/api/auth.py`)
- `POST /auth/login` - User login
- `POST /auth/register` - New user registration
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout
- `GET /auth/me` - Get current user
- `PUT /auth/profile` - Update user profile

#### **Historical Data** (Review: `/services/api/historical_api.py`)
- `POST /historical/weather` - Download historical data (tier-enforced)
- `GET /historical/cities` - List available cities
- `GET /historical/access-limits` - Get user's access limits
- `GET /historical/summary` - Statistical summary

**Key Implementation:**
```python
# Lines 18-25: Database connection setup
db_config = DatabaseConfig()

def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

# Lines 30-110: Main historical data endpoint with tier enforcement
# Lines 150-200: Cities list endpoint
# Lines 205-250: Access limits endpoint
# Lines 255-320: Statistical summary endpoint
```

#### **Dashboard** (Review: `/services/api/dashboard_api.py`)
- `GET /dashboard/stats` - Dashboard statistics
- `GET /dashboard/weather/current` - Current weather
- `GET /dashboard/weather/trends` - Weather trends
- `GET /dashboard/usage` - API usage metrics
- `GET /dashboard/notifications` - User notifications

**Recent Changes:**
- ✅ Removed CSV dependencies (lines 1-11)
- ✅ Removed mock data fallbacks (lines 130-169)
- ✅ Added real database queries

#### **AI Ethics** (Review: `/services/api/ai_ethics_api.py` + `ai_ethics_dashboard_api.py`)
- `GET /ai-ethics/bias-detection` - Bias detection results
- `GET /ai-ethics/fairness-metrics` - Fairness monitoring
- `GET /ai-ethics/decisions` - AI decision audit
- `GET /ai-ethics-dashboard/overview` - Ethics dashboard

#### **Security** (Review: `/services/api/security_api.py` + `security_dashboard_api.py`)
- `GET /security/alerts` - Security alerts
- `GET /security/incidents` - Security incidents
- `GET /security/audit-log` - Audit logs
- `GET /security-dashboard/overview` - Security dashboard

#### **All Other APIs:**
- **News** (`news_api.py`) - Climate news aggregation
- **Analytics** (`analytics_api.py`) - Weather trend analysis
- **Billing** (`billing_api.py`) - Subscription management
- **Payments** (`payments_api.py`) - Payment processing
- **Admin** (`admin_api.py`) - Admin operations
- **Forecast** (`forecast_api.py`) - Weather predictions
- **Chat** (`chat_api.py`) - AI chat interface
- **Orchestrator** (`orchestrator_api.py`) - Orchestrator tasks

### **When to Use:**
- 🔌 **API Integration** → Main README API section
- 📥 **Historical Data** → historical_api.py
- 📊 **Dashboard Data** → dashboard_api.py
- ⚖️ **Ethics Monitoring** → ai_ethics_api.py + ai_ethics_dashboard_api.py
- 🛡️ **Security Data** → security_api.py + security_dashboard_api.py

---

## 🎨 Frontend Components

### **Component Documentation**

#### **Core Components** (Review: `/frontend/src/components/`)
| Component | File | Purpose |
|-----------|------|---------|
| **Header** | `Header.jsx` | Navigation, user menu, resources dropdown |
| **Footer** | `Footer.jsx` | Footer with company links, contact info |
| **HistoricalDataDownload** | `HistoricalDataDownload.jsx` | Tier-aware data download (NEW) |
| **NewsAlerts** | `NewsAlerts.jsx` | Climate news display |
| **NotificationPanel** | `NotificationPanel.jsx` | User notifications |
| **UsageWidget** | `UsageWidget.jsx` | API usage tracking |
| **Pricing** | `Pricing.jsx` | Subscription plans |

#### **Pages** (Review: `/frontend/src/pages/`)
| Page | File | Purpose |
|------|------|---------|
| **Dashboard** | `Dashboard.jsx` | Main user dashboard with charts |
| **Settings** | `Settings.jsx` | User profile, subscription management |
| **WeatherPredictor** | `WeatherPredictor.jsx` | Weather prediction interface |
| **Chat** | `Chat.jsx` | AI assistant chat |
| **About Us** | `AboutUs.jsx` | Company information |
| **Contact Us** | `ContactUs.jsx` | Contact form |
| **FAQ** | `FaqPage.jsx` | Frequently asked questions |
| **Terms** | `TermsAndConditions.jsx` | Terms of service |

#### **Key Frontend Files:**

**Historical Data Download** (Review: `components/HistoricalDataDownload.jsx`)
- Lines 1-50: Imports and tier configuration
- Lines 50-100: State management
- Lines 100-150: Download logic with tier validation
- Lines 150-250: UI rendering

**Dashboard** (Review: `pages/Dashboard.jsx`)
- Lines 1-100: Imports, state, data fetching
- Lines 150-250: Quick stats cards (temperature, humidity, wind, UV)
- Lines 250-350: Charts (temperature trends, regional distribution)
- Lines 350-388: Historical download integration

**Settings** (Review: `pages/Settings.jsx`)
- Lines 1-100: State management
- Lines 100-200: Profile editing
- Lines 340-410: Subscription management (read-only tier display)
- Lines 410-510: Password change

### **Recent Changes:**

#### **Settings Page** (Updated October 17, 2025)
- ✅ Removed tier selection dropdown
- ✅ Fixed cancel button to restore original data
- ✅ Tier now read-only with "Change Plan" button to /pricing
- ✅ Cancel subscription properly uses changeTier('free')

#### **Dashboard** (Updated October 17, 2025)
- ✅ Rounded temperature to 1 decimal place
- ✅ Rounded humidity to whole numbers
- ✅ Integrated HistoricalDataDownload component

#### **Pricing** (Updated October 17, 2025)
- ✅ Updated tier promises (removed confusing forecast details)
- ✅ Made predictions available to all tiers
- ✅ Updated feature matrix

#### **Header** (Updated October 17, 2025)
- ✅ Added "Resources" dropdown menu
- ✅ Links to: Pricing, About, Contact, FAQ, Terms
- ✅ Mobile menu includes resources section

#### **Footer** (Updated October 17, 2025)
- ✅ Changed "Resources" to "Company" section
- ✅ Links to: About Us, Contact Us, FAQ, Pricing, Support
- ✅ Terms of Service in bottom bar

### **When to Use:**
- 🎨 **UI Development** → Specific component files
- 📥 **Data Download Feature** → HistoricalDataDownload.jsx
- 📊 **Dashboard Customization** → Dashboard.jsx
- ⚙️ **Settings Page** → Settings.jsx
- 💰 **Pricing Display** → Pricing.jsx
- 🧭 **Navigation** → Header.jsx + Footer.jsx

---

## 🚀 Deployment & DevOps

### **Deployment Documentation**

**File:** `/README.md` (lines 850-1100) - Complete deployment guide

### **Key Sections:**

#### **Production Build** (Review: README lines 850-900)
- Frontend build process
- Backend Gunicorn setup
- Environment variables for production

#### **Docker Deployment** (Review: README lines 900-1000)
- Dockerfile configuration
- Docker Compose setup
- Database initialization
- Service orchestration

#### **Database Migration** (Review: README lines 1000-1050)
- Backup procedures
- Schema application
- Table verification

#### **Monitoring & Maintenance** (Review: README lines 1050-1100)
- Daily data collection scheduling
- Database maintenance (ANALYZE, VACUUM)
- Table size monitoring
- Performance optimization

### **Configuration Files:**
- `/frontend/vite.config.js` - Vite configuration
- `/frontend/package.json` - Frontend dependencies
- `/services/requirements.txt` - Backend dependencies (cleaned, 60 packages)
- `/services/.env` - Environment variables (not committed)

### **When to Use:**
- 🚀 **Production Deployment** → README deployment section
- 🐳 **Docker Setup** → Docker Compose configuration
- 💾 **Database Backup** → Database migration section
- ⚙️ **Performance Tuning** → Monitoring section

---

## 🧪 Testing & Quality Assurance

### **Test Scripts**

**Location:** `/services/scripts/`

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `check_news_db.py` | Inspect news articles in database | After news collection |
| `seed_news.py` | Seed initial news articles | Setup, testing |
| `test_historical_access.py` | Test tier-based historical access | After tier changes |
| `test_real_news.py` | Test NewsAPI integration | News feature testing |

### **How to Run Tests:**

```bash
# Backend tests (if pytest is set up)
cd services
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Check news database
cd services/scripts
python check_news_db.py

# Test historical access tiers
python test_historical_access.py

# Test news collection
python test_real_news.py
```

### **When to Use:**
- 🧪 **After Database Changes** → check_news_db.py
- 🔐 **After Tier Updates** → test_historical_access.py
- 📰 **After News Changes** → test_real_news.py
- 🌱 **Initial Setup** → seed_news.py

---

## 📊 Data Collection & Schedulers

### **Scheduler Documentation**

**Primary File:** `/services/schedulers/README.md`

### **Key Components:**

#### **Unified Daily Collector** (Review: `/services/schedulers/unified_daily_collector.py`)
- Collects weather data from multiple sources
- Runs daily at 2 AM (configurable)
- Stores data in weather_data table
- Generates daily collection reports

#### **Batch Scripts:**
- `start_collector.bat` (Windows)
- `start_collector.sh` (Linux/Mac)

### **Setup Instructions:**

**Windows (Task Scheduler):**
```batch
# Use start_collector.bat
# Schedule to run daily at 2 AM
```

**Linux/Mac (Crontab):**
```bash
# Add to crontab:
0 2 * * * cd /path/to/services && python schedulers/unified_daily_collector.py
```

### **When to Use:**
- ⏰ **Scheduling Data Collection** → Schedulers README
- 📊 **Daily Weather Updates** → unified_daily_collector.py
- 🔍 **Collection Monitoring** → Daily collection reports

---

## 💳 Billing & Payments

### **Payment Integration**

#### **API Endpoints** (Review: `/services/api/payments_api.py` + `billing_api.py`)
- `POST /payments/create-checkout` - Create Stripe checkout
- `POST /payments/webhook` - Handle Stripe webhooks
- `GET /payments/history` - Payment history
- `GET /billing/subscription` - Subscription details
- `POST /billing/upgrade` - Upgrade tier
- `GET /billing/usage` - Billing usage summary

#### **Frontend** (Review: `/frontend/src/pages/Checkout.jsx`)
- Stripe payment integration
- Checkout flow
- Payment success handling

### **Tier Management:**
- **Free**: $0/mo - 30 days historical, 5 API calls/mo
- **Researcher**: $29/mo - 1 year historical, 5,000 API calls/mo
- **Professional**: $99/mo - 28 years historical, unlimited API calls

### **When to Use:**
- 💳 **Payment Integration** → payments_api.py
- 📊 **Subscription Management** → billing_api.py
- 🎯 **Tier Enforcement** → utils/tier.py + historical_api.py

---

## 🔄 Quick Reference by Role

### **For Backend Developers:**
1. Start with: `/README.md` + `/services/README.md`
2. Database: `/services/data/GISDb_schema.sql`
3. APIs: `/services/api/` (specific module)
4. Models: `/services/models/`
5. Configuration: `/services/db_config.py`

### **For Frontend Developers:**
1. Start with: `/frontend/README.md`
2. Components: `/frontend/src/components/`
3. Pages: `/frontend/src/pages/`
4. Routing: `/frontend/src/App.jsx`
5. Styling: `/frontend/src/index.css` + Tailwind

### **For Data Scientists:**
1. Start with: `/services/agents/` (all agent files)
2. Predictions: `/services/agents/predict/`
3. Data: `/services/data/preprocessed/`
4. Responsible AI: `/services/agents/responsible_ai.py` ⭐

### **For Security Reviewers:**
1. Start with: `/services/agents/security_framework.py` ⭐
2. Authentication: `/services/security/` (both files)
3. Security APIs: `/services/api/security_api.py` + `security_dashboard_api.py`
4. Database: Security tables in GISDb_schema.sql

### **For Ethics & Compliance:**
1. Start with: `/services/agents/responsible_ai.py` ⭐⭐⭐
2. Ethics APIs: `/services/api/ai_ethics_api.py` + `ai_ethics_dashboard_api.py`
3. Database: AI ethics tables in GISDb_schema.sql (lines 550-750)
4. Monitoring: AI Ethics Dashboard implementation

### **For DevOps Engineers:**
1. Start with: `/README.md` (deployment section)
2. Configuration: `/services/requirements.txt` + `/frontend/package.json`
3. Schedulers: `/services/schedulers/README.md`
4. Scripts: `/services/scripts/` (all maintenance scripts)

### **For Project Managers:**
1. Start with: `/README.md` (overview, features, roadmap)
2. Pricing: `/frontend/src/components/Pricing.jsx`
3. Documentation: This file (`DOCUMENTATION_GUIDE.md`)

---

## 📋 Document Update Checklist

When making changes to the codebase, update these documents:

### **After Adding New Features:**
- [ ] Update `/README.md` with new feature description
- [ ] Update API documentation in `/README.md` if new endpoints added
- [ ] Update this guide (`DOCUMENTATION_GUIDE.md`)
- [ ] Update relevant component/module-specific docs

### **After Database Changes:**
- [ ] Update `/services/data/GISDb_schema.sql`
- [ ] Update model files in `/services/models/`
- [ ] Document in this guide

### **After API Changes:**
- [ ] Update API documentation in `/README.md`
- [ ] Update API module file docstrings
- [ ] Update frontend integration if needed

### **After Security Changes:**
- [ ] Update security documentation
- [ ] Review and update security_framework.py docstrings
- [ ] Update this guide's security section

### **After AI/Ethics Changes:**
- [ ] Update responsible_ai.py documentation
- [ ] Update this guide's Responsible AI section
- [ ] Document new metrics or thresholds

---

## 🆘 Getting Help

### **Common Issues & Where to Look:**

| Issue | Check These Documents |
|-------|----------------------|
| **Setup fails** | `/README.md` setup section, Backend README |
| **Authentication not working** | `security/auth_middleware.py`, `security/jwt_handler.py` |
| **Database connection errors** | `db_config.py`, `.env` file |
| **Historical data not downloading** | `api/historical_api.py` (lines 18-25 for DB setup) |
| **Tier enforcement not working** | `utils/tier.py`, `api/historical_api.py` |
| **Dashboard showing errors** | `api/dashboard_api.py` (check for mock data removal) |
| **Ethics monitoring issues** | `agents/responsible_ai.py`, `api/ai_ethics_dashboard_api.py` |
| **Security alerts not working** | `agents/security_agent.py`, `api/security_dashboard_api.py` |
| **Payment integration issues** | `api/payments_api.py`, `api/billing_api.py` |

---

## 📞 Support & Resources

### **Internal Resources:**
- **Main README**: `/README.md`
- **This Guide**: `/DOCUMENTATION_GUIDE.md`
- **API Docs**: `/README.md` (lines 500-800)
- **Database Schema**: `/services/data/GISDb_schema.sql`

### **External Resources:**
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Tailwind CSS**: https://tailwindcss.com/
- **Stripe Integration**: https://stripe.com/docs
- **LangChain**: https://python.langchain.com/
- **PostgreSQL**: https://www.postgresql.org/docs/

---

## 🎯 Quick Start by Task

### **"I need to implement bias detection"**
→ Read `/services/agents/responsible_ai.py` (lines 50-150)

### **"I need to add a new API endpoint"**
→ Check existing API in `/services/api/`, update `/services/main.py`, document in `/README.md`

### **"I need to modify the database"**
→ Update `/services/data/GISDb_schema.sql`, update model in `/services/models/`

### **"I need to change tier limits"**
→ Review `/services/utils/tier.py` and `/frontend/src/components/Pricing.jsx`

### **"I need to add a new page"**
→ Create in `/frontend/src/pages/`, add route in `/frontend/src/App.jsx`, link in Header/Footer

### **"I need to understand the security"**
→ Start with `/services/agents/security_framework.py` and `/services/security/`

### **"I need to deploy to production"**
→ Follow `/README.md` deployment section (lines 850-1100)

---

**Last Updated:** October 17, 2025  
**Version:** 1.0  
**Maintainer:** Development Team

---

**📚 Remember:** This is a living document. Keep it updated as the project evolves!
