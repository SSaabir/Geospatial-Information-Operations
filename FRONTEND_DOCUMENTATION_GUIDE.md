# 🎨 Frontend Documentation & Backend Integration Guide
## GeoWeather AI - React Application

> **Last Updated:** October 17, 2025  
> **Purpose:** Line-by-line reference guide showing WHERE code is located and HOW it connects to backend  
> **Note:** This guide provides LINE NUMBERS and LOCATIONS, not actual code snippets

---

## 📋 Table of Contents

1. [Application Structure](#application-structure)
2. [Core Configuration Files](#core-configuration-files)
3. [Routing & Navigation](#routing--navigation)
4. [Authentication System](#authentication-system)
5. [Main Pages](#main-pages)
6. [Core Components](#core-components)
7. [Backend API Connections](#backend-api-connections)
8. [State Management](#state-management)
9. [Quick Reference Tables](#quick-reference-tables)

---

## 🏗️ Application Structure

### **Project Directory**
```
frontend/
├── src/
│   ├── main.jsx                    (11 lines) - Entry point
│   ├── App.jsx                     (141 lines) - Routing
│   ├── index.css                   - Global Tailwind styles
│   ├── App.css                     - Component styles
│   ├── components/                 - 15+ reusable components
│   ├── pages/                      - 20+ page components
│   └── contexts/
│       └── AuthContext.jsx         (308 lines) - Auth system
├── public/
│   └── favicon.svg                 - Custom icon
├── index.html                      (21 lines) - HTML template
├── vite.config.js                  - Build config + API proxy
├── tailwind.config.js              - Tailwind config
└── package.json                    - Dependencies
```

---

## ⚙️ Core Configuration Files

### **1. Entry Point: `main.jsx`**
**File:** `/frontend/src/main.jsx`  
**Total Lines:** 11

| Lines | Content | Notes |
|-------|---------|-------|
| 1-5 | React imports | React, ReactDOM, CSS, App |
| 7-11 | App rendering | ⚠️ StrictMode DISABLED (React-Leaflet compatibility) |

**Backend Connection:** None

---

### **2. HTML Template: `index.html`**
**File:** `/frontend/index.html`  
**Total Lines:** 21

| Lines | Content | Backend Connection |
|-------|---------|-------------------|
| 1-6 | DOCTYPE, meta, favicon | None |
| 7-11 | **SEO meta tags** ✅ NEW (Oct 17) | None |
| 13 | **Page title** ✅ UPDATED (Oct 17) | None |
| 16-19 | Root div + script | None |

**Recent Changes (Oct 17, 2025):**
- ✅ Line 6: Favicon changed to `/favicon.svg`
- ✅ Lines 7-11: Added description, keywords, author, theme-color
- ✅ Line 13: Title updated to "GeoWeather AI - Climate Intelligence Platform"

---

### **3. Vite Config: `vite.config.js`**
**File:** `/frontend/vite.config.js`

| Lines | Content | Backend Connection |
|-------|---------|-------------------|
| 1-4 | Imports & React plugin | None |
| 6-7 | Dev server (port 3000) | None |
| 8-12 | **API proxy** | ✅ Proxies `/api/*` → `http://localhost:8000` |

**Key:** All frontend API calls to `/api/*` automatically forwarded to backend

---

## 🧭 Routing & Navigation

### **Main App: `App.jsx`**
**File:** `/frontend/src/App.jsx`  
**Total Lines:** 141

#### **Structure**

| Lines | Content | Count | Backend Connection |
|-------|---------|-------|-------------------|
| 1-35 | Imports | 27 pages, 3 layouts, 1 context | None |
| 37-44 | App component | Main function | None |
| 46 | Login route | 1 route (no layout) | None |
| 53-66 | **Public routes** | 7 routes | None |
| 74-117 | **Protected routes** | 14+ routes | ✅ Via `FeatureGate` → `AuthContext` |

#### **Route Breakdown**

**Login Route (Line 46)**
- Path: `/login` → No header/footer

**Public Routes (Lines 53-66)**
| Line | Path | Component | Layout |
|------|------|-----------|--------|
| 53 | `/` | Home | Yes |
| 54 | `/about` | About | Yes |
| 55 | `/contact` | Contact | Yes |
| 56 | `/faq` | FAQ | Yes |
| 57 | `/terms` | Terms | Yes |
| 58 | `/pricing` | Pricing | Yes |
| 59 | `/checkout` | Checkout | Yes |

**Protected Routes (Lines 74-117)**

*User Routes:*
| Lines | Path | Component |
|-------|------|-----------|
| 74 | `/dashboard` | Dashboard |
| 75 | `/workflow` | Workflow |
| 76 | `/chat` | Chat |
| 77 | `/settings` | Settings |
| 78 | `/notifications` | NotificationPanel |
| 109 | `/historical-data` | HistoricalDataDownload |
| 110 | `/weather-predictor` | WeatherPredictor |
| 111 | `/ai-weather-insights` | AIWeatherInsights |

*Admin Routes (Lines 83-107):*
| Lines | Path | Component |
|-------|------|-----------|
| 83-90 | `/admin/security-dashboard` | SecurityDashboard |
| 91-98 | `/admin/ai-ethics-dashboard` | AIEthicsDashboard |
| 99-106 | `/admin/analytics-dashboard` | AnalyticsDashboard |
| 107 | `/admin/admin-dashboard` | AdminDashboard |

**Protection Mechanism:**
- All protected routes wrapped in `<FeatureGate>` component
- `FeatureGate` checks `isAuthenticated` from `AuthContext`
- Admin routes use `<FeatureGate adminOnly>` prop
- Redirects to `/login` if not authenticated

---

## 🔐 Authentication System

### **AuthContext: `contexts/AuthContext.jsx`**
**File:** `/frontend/src/contexts/AuthContext.jsx`  
**Total Lines:** 308

#### **Structure**

| Lines | Section | Purpose | Backend Endpoints |
|-------|---------|---------|------------------|
| 1-16 | Setup | Imports, API base URL | None |
| 18-44 | **API helper** | Centralized fetch with auth | All |
| 46-93 | **Token verification** | Auto-refresh on app load | `/auth/verify-token`, `/auth/refresh` |
| 95-125 | State setup | React state initialization | None |
| 127-168 | `login()` | User login | `/auth/login` |
| 170-190 | `register()` | User registration | `/auth/register` |
| 192-210 | `logout()` | Logout & clear tokens | `/auth/logout` |
| 212-233 | `updateProfile()` | Update user profile | `/auth/me` (PUT) |
| 235-252 | `changePassword()` | Change password | `/auth/change-password` |
| 254-270 | `changeTier()` | Change subscription | `/auth/me/tier` |
| 272-308 | Provider | Export context | None |

#### **Key Components**

**1. API Base URL (Line 5)**
```
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
```

**2. API Helper (Lines 18-44)**
| Lines | Function |
|-------|----------|
| 19 | Construct full URL |
| 21-26 | Set default headers (Content-Type: application/json) |
| 28-30 | **Auto-inject Bearer token** |
| 32-38 | Parse response & handle errors |

**3. Token Verification Flow (Lines 46-93)**
| Lines | Action | Backend Call |
|-------|--------|--------------|
| 50-53 | Get tokens from localStorage | None |
| 62-67 | Verify token validity | `POST /auth/verify-token` |
| 69-74 | If valid → restore state | None |
| 76-87 | If invalid → refresh token | `POST /auth/refresh` |
| 88-90 | If refresh fails → clear all | None |

#### **Authentication Functions**

| Lines | Function | Endpoint | Method | Request Data |
|-------|----------|----------|--------|--------------|
| 127-168 | `login()` | `/auth/login` | POST | `{ email, password }` |
| 170-190 | `register()` | `/auth/register` | POST | `{ email, password, full_name, username }` |
| 192-210 | `logout()` | `/auth/logout` | POST | `{ refresh_token }` |
| 212-233 | `updateProfile()` | `/auth/me` | PUT | `{ full_name, email, username, avatar_url }` |
| 235-252 | `changePassword()` | `/auth/change-password` | POST | `{ current_password, new_password }` |
| 254-270 | `changeTier()` | `/auth/me/tier` | POST | `{ new_tier }` |

**Response Format (Login/Register):**
```json
{
  "access_token": "JWT token (30 min)",
  "refresh_token": "JWT token (7 days)",
  "token_type": "bearer",
  "user": {
    "id": 123,
    "email": "user@example.com",
    "full_name": "John Doe",
    "tier": "free|researcher|professional",
    "is_admin": false,
    "avatar_url": null
  }
}
```

**Exported Context Values:**
```javascript
{
  user, isAuthenticated, isLoading,
  login, register, logout,
  updateProfile, changePassword, changeTier,
  apiCall
}
```

---

## 📄 Main Pages

### **1. Dashboard: `pages/Dashboard.jsx`**
**File:** `/frontend/src/pages/Dashboard.jsx`  
**Total Lines:** 388

#### **Structure**

| Lines | Section | Backend Connection |
|-------|---------|-------------------|
| 1-10 | Imports | None |
| 11-20 | State setup | None |
| 29-111 | **Data fetching** | ✅ 2 API calls |
| 113-153 | Tab handlers | None |
| 155-218 | **Quick stats cards** | Temperature, humidity, wind, UV |
| 220-388 | **Charts** | Temperature, weekly, regional |

#### **Backend API Calls**

| Lines | Endpoint | Method | Purpose | Response Data |
|-------|----------|--------|---------|---------------|
| 35-37 | `/dashboard/weather/trends?days=7` | GET | 7-day weather trends | `{ daily_temps: [...] }` |
| 66-81 | `/dashboard/activity/recent?limit=5` | GET | Recent activities | `{ activities: [...] }` |

#### **Data Processing**

| Lines | Action |
|-------|--------|
| 47, 49 | Round temperature to 1 decimal, humidity to integer |
| 167, 185 | Display rounded temperature in stats cards |
| 220-270 | Map daily_temps to Recharts format |

**Recent Changes (Oct 17, 2025):**
- ✅ Lines 47, 167, 185: Temperature rounding consistency

---

### **2. Settings: `pages/Settings.jsx`**
**File:** `/frontend/src/pages/Settings.jsx`  
**Total Lines:** 621

#### **Structure**

| Lines | Section | Backend Connection |
|-------|---------|-------------------|
| 1-10 | Imports | None |
| 11-45 | State setup | 3 states (userData, originalData, passwordData) |
| 47-67 | **Profile load** | From AuthContext |
| 90-95 | Cancel edit | Restore originalData |
| 132-169 | **Save profile** | `PUT /auth/me` |
| 218-257 | **Change password** | `POST /auth/change-password` |
| 452-478 | **Tier display** | Read-only (from user.tier) |
| 485-505 | **Cancel subscription** | Calls `changeTier('free')` |

#### **Backend API Calls**

| Lines | Action | Endpoint | Method | Request |
|-------|--------|----------|--------|---------|
| 136-142 | Save profile | `/auth/me` | PUT | `{ full_name, email, username, avatar_url }` |
| 224-229 | Change password | `/auth/change-password` | POST | `{ current_password, new_password }` |
| 489-491 | Cancel subscription | `/auth/me/tier` | POST | `{ new_tier: "free" }` |

**Recent Changes (Oct 17, 2025):**
- ✅ Line 92: Fixed cancel button to restore full `originalData` object
- ✅ Lines 452-478: Tier section made read-only with "Change Plan" button to `/pricing`
- ✅ Lines 485-505: Cancel subscription uses `changeTier('free')` from AuthContext

**Validation:**
- Lines 218-223: Password validation (current password, new password match)
- Lines 132-135: Profile validation (required fields check)

---

### **3. Historical Data Download: `pages/HistoricalDataDownload.jsx`**
**File:** `/frontend/src/pages/HistoricalDataDownload.jsx`  
**Total Lines:** 244

#### **Structure**

| Lines | Section | Backend Connection |
|-------|---------|-------------------|
| 1-13 | Imports | None |
| 14-20 | **Tier configuration** | Access limits by tier |
| 22-37 | State setup | 7 states |
| 39-51 | **Fetch access limits** | `GET /historical/access-limits` |
| 76-148 | **Download function** | `POST /historical/weather` |
| 150-244 | UI rendering | None |

#### **Tier Access Limits (Lines 14-20)**

| Tier | Max Days | Download Limit |
|------|----------|----------------|
| Free | 30 days | Limited |
| Researcher | 365 days | Extended |
| Professional | Unlimited | Unlimited |

#### **Backend API Calls**

| Lines | Endpoint | Method | Purpose | Response |
|-------|----------|--------|---------|----------|
| 39-51 | `/historical/access-limits` | GET | Get user's tier limits | `{ tier, access_info }` |
| 102-106 | `/historical/weather` | POST | Download historical data | `{ data: [...] }` |

**Download Request (Lines 102-106):**
```
POST /historical/weather?city={city}&start_date={date}&end_date={date}
Authorization: Bearer <token>
```

#### **Data Processing**

| Lines | Action |
|-------|--------|
| 76-89 | Date validation with tier limit enforcement |
| 102-110 | Fetch weather data from backend |
| 112-138 | Convert JSON to CSV format |
| 140-148 | Trigger browser download |

**Error Handling:**
- Lines 144-148: Handle 403 errors (tier access denied)
- Lines 76-89: Validate date range before API call

---

### **4. Weather Predictor: `pages/WeatherPredictor.jsx`**
**File:** `/frontend/src/pages/WeatherPredictor.jsx`  
**Total Lines:** 605

#### **Structure**

| Lines | Section | Backend Connection |
|-------|---------|-------------------|
| 1-16 | Imports | None |
| 17-18 | **API config** | Backend URL |
| 20-38 | State setup | 10+ states |
| 40-92 | **Prediction function** | `POST /api/weather/predict` |
| 94-605 | UI (form + results) | None |

#### **Backend API Call**

| Lines | Endpoint | Method | Request | Response |
|-------|----------|--------|---------|----------|
| 57-63 | `/api/weather/predict` | POST | Weather parameters | Prediction + confidence |

**Request Payload (Lines 57-63):**
```json
{
  "datetime": "2025-10-17T14:30:00",
  "sunrise": "06:00",
  "sunset": "18:30",
  "humidity": 75,
  "pressure": 1013,
  "temperature": 28.5
}
```

**Response (Lines 64-75):**
```json
{
  "prediction": "Clear",
  "confidence": 0.89,
  "processed_features": {...},
  "all_probabilities": {
    "Clear": 0.89,
    "Rain": 0.08,
    "Clouds": 0.03
  }
}
```

#### **Data Processing**

| Lines | Action |
|-------|--------|
| 40-53 | Validate all required fields |
| 57-63 | Send prediction request |
| 76-90 | Transform response and update state |

---

### **5. Chat: `pages/Chat.jsx`**
**File:** `/frontend/src/pages/Chat.jsx`  
**Total Lines:** 342

#### **Structure**

| Lines | Section | Backend Connection |
|-------|---------|-------------------|
| 1-10 | Imports | None |
| 11-33 | State setup | 4 states |
| 35-85 | **Send message function** | `POST /chat/send` |
| 87-342 | UI rendering | None |

#### **Backend API Call**

| Lines | Endpoint | Method | Request | Response |
|-------|----------|--------|---------|----------|
| 64-72 | `/chat/send` | POST | Message + history | AI response |

**Request Payload (Lines 54-72):**
```json
{
  "message": "What's the weather like?",
  "conversation_history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

**Authorization:**
- Lines 70-71: Includes `Authorization: Bearer <token>` from localStorage

**Response:**
```json
{
  "response": "AI generated response text...",
  "timestamp": "2025-10-17T14:30:00"
}
```

#### **Conversation Flow**

| Lines | Action |
|-------|--------|
| 35-53 | Validate message input |
| 54-62 | Build conversation history array |
| 64-72 | Send message to backend |
| 73-81 | Update messages state with response |

**Tier Restriction:**
- Chat feature available to **Professional tier only**
- Error handling for 403 responses (tier access denied)

---

## 🧩 Core Components

### **1. Header: `components/Header.jsx`**
**File:** `/frontend/src/components/Header.jsx`  
**Total Lines:** 296

| Lines | Section | Purpose |
|-------|---------|---------|
| 1-7 | Imports | React Router, Lucide icons, AuthContext |
| 8-13 | State | Mobile menu, dropdowns |
| 15-95 | Navigation logic | Menu toggles, logout |
| 97-142 | **Resources dropdown** ✅ NEW (Oct 17) | Pricing, About, Contact, FAQ, Terms |
| 144-186 | User menu | Profile, Settings, Logout |
| 188-296 | UI rendering | Desktop + mobile nav |

**Recent Changes (Oct 17, 2025):**
- ✅ Lines 97-142: Added "Resources" dropdown to main navigation
- Links: Pricing, About Us, Contact Us, FAQ, Terms of Service
- Hover to open, click to toggle behavior

**Backend Connection:**
- Lines 66-75: Logout function calls `logout()` from AuthContext → `POST /auth/logout`

---

### **2. Footer: `components/Footer.jsx`**
**File:** `/frontend/src/components/Footer.jsx`  
**Total Lines:** 156

| Lines | Section | Links |
|-------|---------|-------|
| 1-5 | Imports | React Router Link |
| 7-65 | Platform section | Features, Documentation, Weather Data, AI Insights |
| 67-90 | **Company section** ✅ UPDATED (Oct 17) | About, Contact, FAQ, Pricing, Support |
| 92-120 | Legal section | Terms, Privacy, Cookies |
| 122-156 | Social + copyright | Social icons, copyright text |

**Recent Changes (Oct 17, 2025):**
- ✅ Lines 67-90: Changed section title from "Resources" to "Company"
- ✅ Added links: About Us, Contact Us, FAQ, Pricing, Support Center

**Backend Connection:** None (static links)

---

### **3. Pricing: `components/Pricing.jsx`**
**File:** `/frontend/src/components/Pricing.jsx`  
**Total Lines:** 211

| Lines | Section | Content |
|-------|---------|---------|
| 1-7 | Imports | React Router, Lucide icons |
| 8-34 | **Plan definitions** | Free, Researcher, Professional |
| 36-83 | Pricing component | Main function |
| 85-117 | **Feature matrix** | 7 features across 3 tiers |
| 119-211 | UI rendering | Plan cards |

#### **Plan Pricing (Lines 8-34)**

| Tier | Price | Features (Lines) |
|------|-------|------------------|
| Free | $0/month | Lines 8-15: Basic features |
| Researcher | $29/month | Lines 17-23: Extended features |
| Professional | $99/month | Lines 25-34: Full features |

**Recent Changes (Oct 17, 2025):**
- ✅ Lines 22, 33: "Weather prediction available" added to all tiers
- ✅ Feature matrix (lines 85-117): 7 features comparison

**Backend Connection:**
- Clicking "Get Started" navigates to `/checkout?plan={tier}`
- Checkout page handles Stripe payment → backend creates subscription

---

## 🔌 Backend API Connections

### **Complete API Reference**

#### **Authentication APIs (AuthContext.jsx)**

| Function | Lines | Endpoint | Method | Request | Response |
|----------|-------|----------|--------|---------|----------|
| Token verification | 62-67 | `/auth/verify-token` | POST | Bearer token | `{ valid: true }` |
| Refresh token | 76-87 | `/auth/refresh` | POST | `{ refresh_token }` | New tokens |
| Login | 127-168 | `/auth/login` | POST | `{ email, password }` | Tokens + user |
| Register | 170-190 | `/auth/register` | POST | User data | Tokens + user |
| Logout | 192-210 | `/auth/logout` | POST | `{ refresh_token }` | Success message |
| Update profile | 212-233 | `/auth/me` | PUT | Profile data | Updated user |
| Change password | 235-252 | `/auth/change-password` | POST | Passwords | Success message |
| Change tier | 254-270 | `/auth/me/tier` | POST | `{ new_tier }` | Updated user |

**Backend File:** `/services/api/auth.py`

---

#### **Dashboard APIs (Dashboard.jsx)**

| Function | Lines | Endpoint | Method | Request | Response |
|----------|-------|----------|--------|---------|----------|
| Weather trends | 35-37 | `/dashboard/weather/trends` | GET | `?days=7` | Daily temperatures |
| Recent activity | 66-81 | `/dashboard/activity/recent` | GET | `?limit=5` | Activity log |

**Backend File:** `/services/api/dashboard_api.py`

---

#### **Historical Data APIs (HistoricalDataDownload.jsx)**

| Function | Lines | Endpoint | Method | Request | Response |
|----------|-------|----------|--------|---------|----------|
| Access limits | 39-51 | `/historical/access-limits` | GET | None | Tier access info |
| Download data | 102-106 | `/historical/weather` | POST | City, dates | Weather records |

**Backend File:** `/services/api/historical_api.py`

---

#### **AI & Prediction APIs**

| Page | Lines | Endpoint | Method | Request | Response |
|------|-------|----------|--------|---------|----------|
| WeatherPredictor | 57-63 | `/api/weather/predict` | POST | Weather params | Prediction + confidence |
| Chat | 64-72 | `/chat/send` | POST | Message + history | AI response |

**Backend Files:** 
- `/services/agents/predict/` (Weather ML model)
- `/services/api/chat_api.py` (Groq-powered chat)

---

#### **News & Alerts APIs (NewsAlerts.jsx)**

| Function | Lines | Endpoint | Method | Request | Response |
|----------|-------|----------|--------|---------|----------|
| Fetch alerts | 18-33 | `/api/news/alerts` | GET | `?threshold=high&limit=10` | Climate news |

**Backend File:** `/services/api/news_api.py`

---

### **Authorization Pattern**

**All authenticated requests include:**
```
Authorization: Bearer <access_token>
```

**Token Storage:**
- `localStorage.getItem('access_token')` - 30 min expiry
- `localStorage.getItem('refresh_token')` - 7 day expiry
- Auto-refresh handled by AuthContext (lines 46-93)

**Error Handling:**
- 401 Unauthorized → Trigger token refresh
- 403 Forbidden → Tier restriction or admin access required
- 404 Not Found → Resource doesn't exist
- 500 Server Error → Backend issue

---

## 📊 State Management

### **Global State (AuthContext)**

**Location:** `/frontend/src/contexts/AuthContext.jsx`  
**Lines:** 95-125

#### **State Variables**

| State | Type | Purpose | Storage |
|-------|------|---------|---------|
| `user` | Object | Current user data | localStorage |
| `isAuthenticated` | Boolean | Login status | Memory |
| `accessToken` | String | JWT access token | localStorage |
| `refreshToken` | String | JWT refresh token | localStorage |
| `isLoading` | Boolean | Initial auth check | Memory |

#### **User Object Structure**

```javascript
{
  id: 123,
  email: "user@example.com",
  full_name: "John Doe",
  tier: "free" | "researcher" | "professional",
  is_admin: false,
  avatar_url: null | "https://..."
}
```

#### **Context Usage in Components**

```javascript
import { useAuth } from '../contexts/AuthContext'

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth()
  
  // Access user data
  console.log(user.tier)
  
  // Call auth functions
  await login(email, password)
  await logout()
}
```

**Components Using AuthContext:**
- `App.jsx` (line 35) - Wraps entire app
- `FeatureGate.jsx` - Route protection
- `Dashboard.jsx` - User data display
- `Settings.jsx` - Profile management
- `Header.jsx` - User menu
- All protected pages

---

### **Local Component State**

**Pattern:** Each page manages its own UI state with `useState`

**Examples:**

| Component | State | Purpose | Lines |
|-----------|-------|---------|-------|
| Dashboard | `temperatureData` | Chart data | 11-20 |
| Settings | `userData` | Form data | 11-45 |
| Chat | `messages` | Conversation | 11-33 |
| WeatherPredictor | `formData` | Prediction inputs | 20-38 |

---

## 🎯 Quick Reference Tables

### **File → Backend Endpoint Mapping**

| Frontend File | Lines | Backend Endpoint | Backend File |
|--------------|-------|------------------|--------------|
| AuthContext.jsx | 127-168 | `POST /auth/login` | api/auth.py |
| AuthContext.jsx | 170-190 | `POST /auth/register` | api/auth.py |
| AuthContext.jsx | 212-233 | `PUT /auth/me` | api/auth.py |
| AuthContext.jsx | 235-252 | `POST /auth/change-password` | api/auth.py |
| AuthContext.jsx | 254-270 | `POST /auth/me/tier` | api/auth.py |
| Dashboard.jsx | 35-37 | `GET /dashboard/weather/trends` | api/dashboard_api.py |
| Dashboard.jsx | 66-81 | `GET /dashboard/activity/recent` | api/dashboard_api.py |
| Settings.jsx | 136-142 | `PUT /auth/me` | api/auth.py |
| Settings.jsx | 224-229 | `POST /auth/change-password` | api/auth.py |
| Settings.jsx | 489-491 | `POST /auth/me/tier` | api/auth.py |
| HistoricalDataDownload.jsx | 39-51 | `GET /historical/access-limits` | api/historical_api.py |
| HistoricalDataDownload.jsx | 102-106 | `POST /historical/weather` | api/historical_api.py |
| WeatherPredictor.jsx | 57-63 | `POST /api/weather/predict` | agents/predict/ |
| Chat.jsx | 64-72 | `POST /chat/send` | api/chat_api.py |
| NewsAlerts.jsx | 18-33 | `GET /api/news/alerts` | api/news_api.py |

---

### **Component → Page Mapping**

| Component | Used In | Lines | Purpose |
|-----------|---------|-------|---------|
| Header | All pages (except Login) | 1-296 | Navigation bar |
| Footer | All pages (except Login) | 1-156 | Footer links |
| FeatureGate | Protected routes (App.jsx) | 74-117 | Route protection |
| Pricing | Pricing page + standalone | 1-211 | Subscription plans |
| MapView | Map page | - | Interactive map |
| NewsAlerts | Dashboard, News page | 1-175 | Climate news |

---

### **Recent Changes Log (Oct 17, 2025)**

| File | Lines | Change | Impact |
|------|-------|--------|--------|
| index.html | 6 | Favicon changed to `/favicon.svg` | Branding |
| index.html | 7-11 | Added SEO meta tags | SEO improvement |
| index.html | 13 | Updated page title | Branding |
| Header.jsx | 97-142 | Added Resources dropdown | Better navigation |
| Footer.jsx | 67-90 | Changed Resources → Company | Clearer categorization |
| Pricing.jsx | 22, 33 | Weather prediction for all tiers | Feature availability |
| Settings.jsx | 92 | Fixed cancel button bug | Bug fix |
| Settings.jsx | 452-478 | Tier section read-only | UX improvement |
| Dashboard.jsx | 47, 167, 185 | Temperature rounding consistency | Data display |

---

### **Tier Feature Matrix**

| Feature | Free | Researcher | Professional | File Reference |
|---------|------|------------|--------------|----------------|
| Basic weather data | ✅ | ✅ | ✅ | Dashboard.jsx |
| Historical data | 30 days | 365 days | Unlimited | HistoricalDataDownload.jsx (lines 14-20) |
| Weather prediction | ✅ | ✅ | ✅ | WeatherPredictor.jsx |
| AI Chat assistant | ❌ | ❌ | ✅ | Chat.jsx (Professional only) |
| Map view | ✅ | ✅ | ✅ | MapView.jsx |
| News alerts | ✅ | ✅ | ✅ | NewsAlerts.jsx |
| Admin dashboards | ❌ | ❌ | ❌ | Admin only (not tier-based) |

---

### **Development Commands**

```bash
# Install dependencies
npm install

# Run development server (port 3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 📝 Notes for Developers

### **When Adding New Features:**

1. **New Page:**
   - Create in `/frontend/src/pages/`
   - Add import to `App.jsx` (lines 1-35)
   - Add route to `App.jsx` (lines 46-117)
   - Add to Header dropdown if public (Header.jsx lines 97-142)

2. **New API Call:**
   - Use `apiCall()` from AuthContext (lines 18-44)
   - Add endpoint to Backend API Connections table (this doc)
   - Handle 401/403 errors for auth/tier restrictions

3. **New Component:**
   - Create in `/frontend/src/components/`
   - Import where needed
   - Add to Component → Page Mapping table (this doc)

4. **Authentication Required:**
   - Wrap route in `<FeatureGate>` (App.jsx lines 74-117)
   - Use `useAuth()` hook to access user data
   - Check `isAuthenticated` before API calls

### **Common Patterns:**

**API Call Pattern:**
```javascript
// In component
const { apiCall } = useAuth()

const fetchData = async () => {
  try {
    const data = await apiCall('/endpoint', {
      method: 'GET' // or POST, PUT, etc.
    })
    // Handle success
  } catch (error) {
    // Handle error
  }
}
```

**Protected Component Pattern:**
```javascript
const { isAuthenticated, user } = useAuth()

if (!isAuthenticated) {
  return <Navigate to="/login" />
}

// Tier check
if (user.tier !== 'professional') {
  return <div>Professional tier required</div>
}
```

---

## 🔍 Troubleshooting Guide

### **Issue → File Location**

| Issue | Check These Files | Lines |
|-------|------------------|-------|
| Login not working | AuthContext.jsx | 127-168 |
| Token expired errors | AuthContext.jsx | 46-93 |
| Route not found | App.jsx | 46-117 |
| API calls failing | AuthContext.jsx | 18-44 |
| Tier restrictions | HistoricalDataDownload.jsx, Chat.jsx | 14-20, entire file |
| Profile not updating | Settings.jsx | 132-169 |
| Password change fails | Settings.jsx | 218-257 |
| Dashboard data not loading | Dashboard.jsx | 29-111 |
| Weather prediction errors | WeatherPredictor.jsx | 40-92 |
| Chat not responding | Chat.jsx | 35-85 |

---

## 📚 Additional Resources

- **Backend Documentation:** See `DOCUMENTATION_GUIDE.md` for backend API details
- **API Documentation:** Backend file `/services/README.md`
- **Database Schema:** `/services/data/GISDb_schema.sql`
- **Deployment Guide:** Project root `README.md`

---

**Last Updated:** October 17, 2025  
**Maintained By:** Development Team  
**Version:** 1.0.0
