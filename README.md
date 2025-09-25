# 🌍 Geospatial Information Operations (GIS)

> **An intelligent geospatial data analysis and weather prediction system powered by AI agents and modern web technologies.**

## 🔍 Project Overview

The **Geospatial Information Operations** project is a comprehensive platform that combines geospatial data analysis, weather prediction, and intelligent data processing using multi-agent systems. The application provides real-time weather insights, predictive analytics, and interactive dashboards for environmental monitoring and decision-making.

### 🎯 Key Features

- **🤖 AI-Powered Weather Analysis**: Multi-agent system using LangGraph for intelligent data collection and analysis
- **📊 Interactive Dashboards**: Real-time visualization of weather patterns, trends, and predictions
- **🌡️ Weather Prediction**: Machine learning models for temperature, humidity, and weather forecasting
- **💬 Intelligent Chat Interface**: Natural language queries for weather data and insights
- **🗄️ Database Integration**: PostgreSQL with geospatial capabilities for historical weather data
- **🔐 User Authentication**: Secure login system with role-based access control
- **📈 Trend Analysis**: Historical data analysis and future trend predictions
- **🌐 RESTful API**: FastAPI backend for seamless data exchange

### 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │  PostgreSQL DB  │
│   (Vite + Tailwind) │ ◄──► │  (Python + AI)   │ ◄──► │  (Geospatial)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User Interface │    │   AI Agents     │    │  Weather APIs   │
│  • Dashboard    │    │  • Collector    │    │  • Historical   │
│  • Weather Form │    │  • Orchestrator │    │  • Real-time    │
│  • Chat System  │    │  • Trend Agent  │    │  • Predictions  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🤖 AI Agent System

The backend employs a sophisticated multi-agent architecture:

- **🔍 Collector Agent**: Gathers weather data from multiple APIs and databases
- **🎯 Orchestrator Agent**: Coordinates data processing and agent communication  
- **📈 Trend Agent**: Analyzes patterns and generates predictive insights
- **📝 Report Agent**: Creates comprehensive weather reports and summaries

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
- **FastAPI 0.104** - High-performance web framework
- **Python 3.10+** - Core programming language
- **LangGraph** - Multi-agent workflow orchestration
- **LangChain** - AI/LLM integration framework
- **SQLAlchemy 2.0** - Database ORM
- **PostgreSQL** - Primary database with geospatial support
- **Groq API** - Language model integration

### Data Science & ML
- **Pandas & NumPy** - Data manipulation and analysis
- **Scikit-learn** - Machine learning algorithms
- **Prophet** - Time series forecasting
- **Statsmodels** - Statistical modeling
- **Matplotlib & Plotly** - Data visualization

### APIs & External Services
- **SerpAPI** - Web search and data collection
- **Weather APIs** - Real-time weather data
- **OpenAI/Groq** - Language model services

---

## 🚀 Quick Start Guide

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
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/GISDb

# API Keys
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
OPENAI_API_KEY=your_openai_key_here

# Server Configuration
ENVIRONMENT=development
SECRET_KEY=your_secret_key_here
```

#### Database Setup

```bash
# Create PostgreSQL database
createdb GISDb

# Run migrations (if any)
alembic upgrade head
```

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

### 🏠 **Home Dashboard**
- Real-time weather overview
- Interactive charts and graphs
- Quick access to key metrics
- Weather alerts and notifications

### 🌡️ **Weather Predictor**
- Input weather parameters
- AI-powered predictions
- Historical data comparison
- Confidence intervals and accuracy metrics

### 💬 **Intelligent Chat**
- Natural language weather queries
- AI agent responses
- Data visualization in chat
- Context-aware conversations

### 📊 **Analytics Dashboard**
- Trend analysis and forecasting
- Historical data visualization
- Performance metrics
- Export capabilities

### 👤 **User Management**
- Secure authentication
- User profiles and preferences
- Admin dashboard
- Role-based access control

---

## 🔧 Development

### Project Structure
```
Geospatial-Information-Operations/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Application pages
│   │   ├── contexts/       # React contexts
│   │   └── assets/         # Static assets
│   └── package.json
├── services/                # FastAPI backend
│   ├── agents/             # AI agent implementations
│   │   ├── collector.py    # Data collection agent
│   │   ├── orchestrator.py # Agent orchestration
│   │   └── trend.py        # Trend analysis agent
│   ├── api/                # API endpoints
│   ├── models/             # Database models
│   ├── data/               # Data files and datasets
│   └── requirements.txt
└── README.md
```

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

Key API endpoints available:

- `GET /api/weather/current` - Current weather data
- `POST /api/weather/predict` - Weather predictions
- `GET /api/weather/history` - Historical weather data
- `POST /api/chat/query` - Chat with AI agents
- `GET /api/dashboard/metrics` - Dashboard analytics

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

## 🚀 Deployment

### Production Build

#### Frontend
```bash
cd frontend
npm run build
# Deploy dist/ folder to your web server
```

#### Backend
```bash
cd services
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Docker Deployment (Optional)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Saabir** - [SSaabir](https://github.com/SSaabir)

---

## 🙏 Acknowledgments

- Weather data provided by various meteorological APIs
- AI capabilities powered by Groq and OpenAI
- Open source community for excellent libraries and frameworks

---

**⭐ Star this repository if you find it helpful!**