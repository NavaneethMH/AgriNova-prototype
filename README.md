# AgriNova 🌱
> **Smarter Farming from Space** — AI-powered precision agriculture SaaS platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+PostGIS-blue)](https://postgis.net)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://docs.docker.com/compose)

## 🚀 Quick Start (Docker — Recommended)

```bash
# 1. Clone and enter the project
cd AgriNova

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration section)

# 3. Start all services
docker-compose -f docker/docker-compose.yml up --build

# App available at:
#   Frontend: http://localhost:3000
#   Backend API: http://localhost:8000
#   API Docs: http://localhost:8000/docs
```

## 🛠 Development Setup (Without Docker)

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16 with PostGIS extension
- Redis (optional, for caching)

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
alembic upgrade head             # Run migrations
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                       # Starts at http://localhost:5173
```

### AI Engine (standalone)
```bash
cd ai-engine
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python train_model.py             # Train the initial model
```

## 🏗 Project Structure

```
AgriNova/
├── frontend/               # React + TypeScript + Vite + TailwindCSS
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Route-level page components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API service layer
│   │   ├── store/          # State management
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Utility functions
│   └── public/
│
├── backend/                # FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── api/            # Route handlers (v1)
│   │   ├── core/           # Config, security, dependencies
│   │   ├── db/             # Database session, base model
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   └── services/       # Business logic services
│   └── requirements.txt
│
├── ai-engine/              # Scikit-Learn ML prediction module
│   ├── predictor.py        # Main prediction interface
│   ├── model.py            # RandomForest model
│   ├── features.py         # Feature engineering
│   └── train_model.py      # Model training script
│
├── earth-engine/           # Google Earth Engine adapter
│   ├── gee_service.py      # GEE API integration + fallback
│   └── simulation.py       # Simulated NDVI/NDWI data
│
├── weather-service/        # OpenWeather API integration
│   ├── openweather_service.py
│   └── scheduler.py        # Background weather fetch
│
├── database/               # Alembic migrations + SQL schema
│   ├── migrations/
│   ├── schema.sql
│   └── alembic.ini
│
├── docker/                 # Docker configuration
│   ├── Dockerfile.frontend
│   ├── Dockerfile.backend
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── tests/                  # Test suites
│   ├── backend/            # pytest tests
│   ├── ai/                 # AI module tests
│   └── frontend/           # Vitest tests
│
├── shared/                 # Shared constants & types
├── docs/                   # API documentation
└── .env.example            # Environment variable template
```

## 🔐 Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Description | Required |
|---|---|---|
| `SECRET_KEY` | JWT signing key (32+ chars) | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `OPENWEATHER_API_KEY` | OpenWeather API key | ⚠️ Weather features |
| `GEE_SERVICE_ACCOUNT_EMAIL` | Google Earth Engine SA email | ⚠️ Real satellite data |
| `GEE_CREDENTIALS_PATH` | Path to GEE service account JSON | ⚠️ Real satellite data |

> **Note:** If GEE credentials are not provided, the app automatically uses simulated NDVI/NDWI data. All other features work without external API keys.

## 📡 API Endpoints

Full interactive documentation at `http://localhost:8000/docs`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| GET | `/api/v1/dashboard` | Aggregated dashboard data |
| POST | `/api/v1/farms` | Create farm with polygon |
| GET | `/api/v1/farms` | List user's farms |
| PUT | `/api/v1/farms/{id}` | Update farm |
| DELETE | `/api/v1/farms/{id}` | Delete farm |
| GET | `/api/v1/weather/{farm_id}` | Current weather |
| GET | `/api/v1/satellite/{farm_id}` | Latest NDVI/NDWI |
| POST | `/api/v1/predict` | Run AI prediction |
| GET | `/api/v1/recommendations/{farm_id}` | AI recommendations |
| GET | `/api/v1/analytics/{farm_id}` | Historical analytics |

## 🧠 AI Module

The moisture stress prediction uses a **RandomForest Classifier** with these features:
- NDVI (Normalized Difference Vegetation Index)
- NDWI (Normalized Difference Water Index)
- Temperature (°C)
- Humidity (%)
- Rainfall (mm)

**Outputs:** Stress Level (Healthy/Moderate/Critical), Stress Score (0–100), Confidence (%), Recommendation text

## 🛡 Security Features
- JWT authentication with refresh tokens
- Bcrypt password hashing
- Rate limiting (60 req/min per IP)
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic schemas)
- Environment variable secrets management

## 🧪 Testing

```bash
# Backend tests
cd backend && pytest tests/ -v --cov=app

# Frontend tests
cd frontend && npm run test

# AI module tests
cd ai-engine && pytest tests/ -v
```

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript 5, Vite, TailwindCSS |
| State | React Query (TanStack Query v5) |
| Forms | React Hook Form + Zod |
| Maps | React Leaflet + Leaflet Draw |
| Charts | Recharts |
| Backend | FastAPI, Python 3.12 |
| ORM | SQLAlchemy 2.0 (async) |
| DB | PostgreSQL 16 + PostGIS |
| Auth | JWT (python-jose) + bcrypt |
| AI/ML | Scikit-Learn, NumPy, Pandas |
| Satellite | Google Earth Engine Python API |
| Weather | OpenWeather API |
| Deployment | Docker, Docker Compose, Nginx |

## 📄 License

MIT License — AgriNova Team
