<p align="center">
  <img src="https://img.shields.io/badge/FasalSaathi-🌾%20Farm%20Smartly-1A7A40?style=for-the-badge&labelColor=0d1117" alt="FasalSaathi Banner" />
</p>

<h1 align="center">FasalSaathi 🌾</h1>

<p align="center">
  <strong>AI-Powered Agricultural Advisory Platform for Indian Farmers</strong><br/>
  Pest detection • Crop recommendations • Government schemes • Weather intelligence
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-🦜-1C3A4F" />
  <img src="https://img.shields.io/badge/LangGraph-StateGraph-6B46C1" />
  <img src="https://img.shields.io/badge/YOLOv8-Pest%20Detection-FF6F00?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?logo=google&logoColor=white" />
</p>

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    🌐  React + Vite  (:5173)                     │
│          Zustand state · React Router · Tailwind CSS             │
└───────────────────────────┬──────────────────────────────────────┘
                            │ REST / multipart
┌───────────────────────────▼──────────────────────────────────────┐
│                ⚡  FastAPI Backend  (:8000)                       │
│  Auth (JWT) · User CRUD · Profile Enrichment · Proxy Layer      │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │ /auth  /users  /crops  /weather  /chat  /detect  /agents │   │
│  └───────────────────────────────────────────────────────────┘   │
└───────────────────────────┬──────────────────────────────────────┘
                            │ httpx (authenticated proxy)
┌───────────────────────────▼──────────────────────────────────────┐
│                🤖  AI Service  (:8001)                            │
│  LangChain LCEL · LangGraph Agents · YOLOv8 · Agent Pipeline   │
│  ┌──────────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Crop Rec. Agent  │  │ Scheme Agent │  │  Pest Detection │   │
│  └──────────────────┘  └──────────────┘  │  (YOLOv8)       │   │
│  ┌──────────────────┐  ┌──────────────┐  └─────────────────┘   │
│  │ Chat (LangGraph) │  │ Orchestrator │                         │
│  │ Supervisor-Worker│  │  (Pipeline)  │                         │
│  └──────────────────┘  └──────────────┘                         │
└───────────────────────────┬──────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         🧠 Gemini     🗄️ PostgreSQL   📸 YOLO .pt
         (LLM API)     (User data)    (Trained model)
```

---

## 🧠 AI Agent System

FasalSaathi uses a **multi-agent architecture** with 4 specialized agents and 2 orchestration patterns.

### Agent Overview

| Agent | Purpose | Model | Trigger |
|-------|---------|-------|---------|
| 🌾 **Crop Recommendation** | Recommends 3–5 best crops for the season | Gemini 2.5 Flash | Individual endpoint or pipeline |
| 🏛️ **Scheme Recommendation** | Matches farmer to 25+ government schemes | Gemini 2.5 Flash | Individual endpoint or pipeline |
| 🐛 **Pest Detection** | YOLOv8 image classification with treatment tips | YOLOv8 (custom) | Image upload |
| 💬 **Conversational Chat** | Multi-turn farming assistant | LangGraph StateGraph | Chat messages |

### Crop Recommendation Agent
- **Input:** State, soil type, season, water availability, land size, past crops, pest context
- **Processing:** Structured agronomist prompt → Gemini LLM → JSON parsing
- **Output:** Ranked crop list with confidence scores, yield estimates, and reasoning
- **Fallback:** Season-specific hardcoded defaults (Kharif/Rabi/Zaid) if LLM fails

### Scheme Recommendation Agent
- **Seed DB:** 25 curated real Indian government schemes with eligibility metadata
- **5-Stage Pipeline:**
  1. Pre-filter by state (including all-India schemes)
  2. Hard-filter by age, gender, and income constraints
  3. Inject context from upstream agents (crop + pest results)
  4. LLM ranking with eligibility scores (0.0–1.0) and explanations
  5. Fuzzy-match and enrich with full scheme metadata (apply URLs, ministry, etc.)

### Pest Detection (YOLOv8)
- **12 Classes:** Ants, Bees, Beetles, Caterpillars, Earwigs, Earthworms, Grasshoppers, Moths, Slugs, Snails, Wasps, Weevils
- **Performance:** mAP@0.5 = 0.773
- **Post-processing:** Each detection enriched with severity label (🔴 High / 🟡 Medium / 🟢 Low) and 3–5 actionable treatment suggestions

### Conversational Chat (LangGraph)
- **Architecture:** Supervisor-Worker pattern using LangGraph `StateGraph`
- **Nodes:** Supervisor (LLM router) → Weather / Market / Pest specialists → Synthesizer
- **Optimization:** Greeting regex fast-path skips LLM calls for "hi", "namaste", etc.
- **Memory:** In-memory session history (configurable, default 10 messages)

---

## 🔄 Orchestrator Pipeline

The full analysis pipeline runs agents **sequentially with shared context**:

```
User Profile + Pest Scan
        │
        ▼
  ┌─────────────────────────┐
  │ 1. Pest Context Inject  │  (passthrough — no LLM call)
  └───────────┬─────────────┘
              ▼
  ┌─────────────────────────┐
  │ 2. Crop Recommendation  │  reads pest context
  │    Agent                │  → outputs top crops
  └───────────┬─────────────┘
              ▼
  ┌─────────────────────────┐
  │ 3. Scheme Recommendation│  reads pest + crop context
  │    Agent                │  → outputs matched schemes
  └───────────┬─────────────┘
              ▼
  ┌─────────────────────────┐
  │ 4. Unified Summary      │  farmer-friendly paragraph
  └─────────────────────────┘
```

**Error Isolation:** Each agent is wrapped in its own try/catch. If one fails, the rest continue — the response indicates which steps succeeded.

---

## ✨ Core Features

### 🦟 Real-Time Pest Detection
Upload a photo → get instant pest identification with confidence scores, severity labels, bounding boxes, and step-by-step treatment recommendations. After detection, seamlessly hand off to the AI chat for follow-up questions.

### 🌱 Smart Crop Advisory
AI-powered crop recommendations based on your soil, location, season, water availability, and pest history. Considers crop rotation and avoids pest-susceptible crops.

### 📜 Government Scheme Matching
Personalized scheme recommendations from a curated database of 25+ real Indian government schemes (PM-KISAN, PMFBY, KCC, PMKSY, etc.). Filtered by state, age, gender, income, and farmer category.

### 🌦️ Live Weather Intelligence
Real-time weather data via Open-Meteo API (free, no key required). Dashboard shows temperature, humidity, wind speed, weather condition, and risk level. Contextual alerts generated from actual conditions.

### 💬 Agentic Chat Assistant
Multi-turn conversational AI that autonomously routes queries to specialist agents (weather, market, pest) using a LangGraph Supervisor. Supports Hindi and regional language responses.

### 🔐 Secure Authentication
JWT-based auth with profile enrichment — the backend transparently injects the logged-in user's profile data into all AI requests, so agents always have full context.

---

## 📁 Project Structure

```
FasalSaathi/
├── frontend/                     # React 19 + Vite + Tailwind CSS
│   └── src/
│       ├── components/           # UI primitives (Card, Badge, Modal, etc.)
│       │   ├── layout/           # Sidebar, PageWrapper
│       │   └── ui/               # Reusable design system components
│       ├── features/             # Feature modules
│       │   ├── auth/             # Login, Register, Onboarding
│       │   ├── chat/             # ChatPage (LangGraph integration)
│       │   ├── dashboard/        # DashboardPage + WeatherCard, SoilHealth, etc.
│       │   ├── fields/           # AddFieldForm, FieldMap
│       │   ├── profile/          # ProfilePage (real data)
│       │   └── scan/             # ScanPage → pest detection + AI handoff
│       ├── stores/               # Zustand state (useUserStore, useFieldStore, useChatStore)
│       └── lib/                  # API client, constants, utilities
│
├── backend/                      # FastAPI REST API (:8000)
│   ├── main.py                   # App entry point
│   └── app/
│       ├── api/v1/endpoints/     # Route handlers
│       │   ├── auth.py           # POST /auth/login, /auth/register
│       │   ├── users.py          # GET/PUT /users/me
│       │   ├── chat.py           # POST /chat → AI service proxy
│       │   ├── detect.py         # POST /detect → YOLO inference
│       │   ├── agents.py         # POST /agents/* → AI pipeline proxy
│       │   ├── schemes.py        # GET /schemes
│       │   ├── crops.py          # GET /crops
│       │   └── weather.py        # GET /weather/current
│       ├── core/                 # Config, security (JWT)
│       ├── db/                   # SQLAlchemy engine + session
│       ├── models/               # ORM models (User, Crop, Scheme)
│       └── schemas/              # Pydantic I/O models
│
├── ai-service/                   # AI Backend (:8001)
│   ├── main.py                   # FastAPI app with 4 routers
│   ├── train.py                  # YOLOv8 training script
│   ├── infer.py                  # YOLO inference (CLI + importable)
│   ├── evaluate.py               # Model evaluation (mAP, P, R, F1)
│   ├── services/
│   │   └── agent_orchestrator.py # Sequential pipeline with context sharing
│   ├── utils/
│   │   └── pest_map.py           # 12-class pest → treatment mapping
│   └── app/
│       ├── agents/               # Standalone agent implementations
│       │   ├── crop_recommendation_agent.py
│       │   └── scheme_recommendation_agent.py
│       ├── graphs/
│       │   └── crop_advisor_graph.py  # LangGraph StateGraph (Supervisor-Worker)
│       ├── chains/
│       │   └── chat_chain.py     # LangChain LCEL conversational chain
│       ├── routers/              # FastAPI route handlers
│       │   ├── chat.py           # /api/chat — LangGraph chat
│       │   ├── crop_advisor.py   # /api/crop-advisor
│       │   ├── detection.py      # /detect — YOLO inference
│       │   └── orchestrator_router.py  # /api/v1/agents/*
│       ├── schemas/
│       │   └── agent_schemas.py  # All Pydantic models for agent I/O
│       ├── data/
│       │   └── seed_schemes.py   # 25 curated Indian gov. schemes
│       ├── tools/                # @tool functions for LangGraph
│       │   ├── weather_tool.py
│       │   └── market_tool.py
│       ├── prompts/
│       │   └── templates.py      # All system prompts
│       ├── memory/
│       │   └── chat_history.py   # Session-based chat memory
│       └── core/
│           ├── config.py         # Pydantic settings (env-driven)
│           └── llm.py            # LLM factory + safe_llm_invoke retry wrapper
│
├── models/
│   └── best.pt                   # Trained YOLOv8 pest detection weights
├── data/                         # YOLO dataset (train/valid/test + data.yaml)
└── README.md
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| React 19 (Vite) | UI framework & dev server |
| Tailwind CSS v4 | Utility-first styling |
| Zustand | Global state management (persisted) |
| React Router v6 | Client-side routing |
| Recharts | Dashboard charts (irrigation usage) |
| Lucide React | Icon system |

### Backend
| Technology | Purpose |
|---|---|
| FastAPI | REST API server (port 8000) |
| SQLAlchemy | ORM for PostgreSQL |
| Pydantic v2 | Request/response validation |
| python-jose | JWT authentication |
| httpx | Async HTTP client (AI service proxy) |
| bcrypt | Password hashing |

### AI Service
| Technology | Purpose |
|---|---|
| FastAPI | AI API server (port 8001) |
| LangChain | LLM chains, LCEL pipelines |
| LangGraph | Stateful multi-agent orchestration |
| Google Generative AI | Gemini 2.5 Flash LLM |
| Ultralytics YOLOv8 | Real-time pest detection |
| Pydantic | Agent I/O schemas |

### Infrastructure
| Technology | Purpose |
|---|---|
| PostgreSQL | Persistent user/crop/scheme data |
| Open-Meteo API | Free weather data (no API key) |
| Google AI Studio | Gemini API keys |

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18+
- **Python** 3.11+
- **PostgreSQL** 15+
- **Google AI API Key** — [Get one here](https://aistudio.google.com/)

### 1. Frontend

```bash
cd frontend
npm install
npm run dev          # → http://localhost:5173
```

Create `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
uvicorn main:app --port 8000 --reload
```

Create `backend/.env`:
```env
PROJECT_NAME=FasalSaathi
DATABASE_URL=postgresql://user:password@localhost:5432/fasalsaathi
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]
AI_SERVICE_URL=http://localhost:8001
```

### 3. AI Service

```bash
cd ai-service
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python main.py               # → http://localhost:8001
```

Create `ai-service/.env`:
```env
GOOGLE_API_KEY=your-google-api-key
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.3
YOLO_WEIGHTS_PATH=models/best.pt
YOLO_CONF_THRESHOLD=0.35
YOLO_OUTPUT_DIR=outputs/detections
```

### 4. ML Pipeline (Pest Detection)

```bash
# Train model
python ai-service/train.py --epochs 10

# Evaluate on test set
python ai-service/evaluate.py

# Run inference on a single image
python ai-service/infer.py --image path/to/crop_photo.jpg
```

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login, returns JWT access token |
| GET | `/api/v1/users/me` | Get current user profile |
| PUT | `/api/v1/users/me` | Update user profile |

### Core Features
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/` | Chat with AI assistant (LangGraph) |
| POST | `/api/v1/detect/` | Upload image → pest detection + suggestions |
| GET | `/api/v1/weather/current` | Current weather for location |
| GET | `/api/v1/crops/` | List crops database |
| GET | `/api/v1/schemes/` | List government schemes |

### AI Agents (Authenticated + Profile-Enriched)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agents/crop-recommendation` | Get AI crop recommendations |
| POST | `/api/v1/agents/scheme-recommendation` | Get matched government schemes |
| POST | `/api/v1/agents/full-analysis` | Run full pipeline (pest → crop → schemes) |

### AI Service Direct (Internal)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/` | LangGraph conversational agent |
| POST | `/api/crop-advisor/` | Crop advisor (LangGraph graph) |
| POST | `/api/v1/agents/*` | Agent endpoints (crop, scheme, pipeline) |
| POST | `/detect/` | Direct YOLO inference |

---

## ⚠️ Known Limitations

| Issue | Impact | Mitigation |
|-------|--------|------------|
| **Gemini Free Tier quota** | 20 req/day on free tier | `safe_llm_invoke` retry + graceful fallbacks per agent |
| **Weather/Market tools** | Stub implementations | Weather: uses Open-Meteo (real). Market: static simulated data |
| **Chat memory** | In-memory only | Sessions lost on AI service restart. Swap for Redis/DB in production |
| **Scheme database** | Static 25-scheme seed | Update `seed_schemes.py` as new schemes are announced |

---

## 🗺️ Roadmap

- [ ] Upgrade to Gemini 2.0 Flash (1500 req/day) for production quotas
- [ ] Integrate real AGMARKNET mandi price API
- [ ] Add Redis-backed chat memory for persistence across restarts
- [ ] Multi-language UI (Hindi, Marathi, Telugu, Tamil)
- [ ] Push notifications for weather alerts and scheme deadlines
- [ ] Mobile app (React Native) with camera integration

---

## 📄 License

This project is built for educational and demonstration purposes.

---

<p align="center">
  <strong>Built with 🌱 for Indian farmers</strong>
</p>
