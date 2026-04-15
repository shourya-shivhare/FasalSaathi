# FasalSaathi — Developer Guide

## Overview

FasalSaathi is an AI-powered agricultural assistant for Indian farmers. It is a **three-service architecture**: a React (Vite) frontend, a FastAPI backend (user/auth/data), and a separate FastAPI AI service (LangChain/LangGraph agents + YOLOv8 detection).

---

## Architecture at a Glance

```
┌──────────────────┐        ┌──────────────────────┐        ┌──────────────────────────┐
│   Frontend       │───────▶│   Backend (port 8000)│───────▶│  AI Service (port 8001)  │
│   React + Vite   │  REST  │   FastAPI + SQLite    │ proxy  │  FastAPI + LangGraph     │
│   port 5173      │◀───────│   Auth, Users, CRUD   │◀───────│  Gemini, YOLO, Agents    │
└──────────────────┘        └──────────────────────┘        └──────────────────────────┘
```

**Frontend** → calls `Backend /api/v1/*` for auth, user CRUD, and proxied AI operations.  
**Backend** → owns the database, proxies some requests to the AI service.  
**AI Service** → runs all LLM and ML workloads independently; never touches the DB.

---

## 1. Frontend (`/frontend`)

**Stack:** React 18, Vite, Zustand, React Router, Lucide Icons.

### Key directories

| Path | Purpose |
|---|---|
| `src/app/routes.jsx` | Route definitions; every route has a `protected` flag for auth gating |
| `src/features/` | Feature-scoped pages — `dashboard`, `chat`, `crop-suggestion`, `schemes`, `market`, `profile`, `onboarding` |
| `src/pages/` | Standalone pages — `Home.jsx` (landing), `scan/ScanPage.jsx` (pest detection) |
| `src/stores/` | Zustand stores — `useUserStore`, `useChatStore`, `useFieldStore`, `useResultsStore`, `useThemeStore` |
| `src/components/` | Shared UI (`layout/`, `shared/`, `ui/`) |
| `src/lib/api.jsx` | Centralised API client wrapping `fetch` calls to the backend |
| `src/styles/` | CSS design tokens, themes (light/dark) |

### State Management (Zustand)

- **`useUserStore`** — Auth tokens, farmer profile, login/register/logout, onboarding completion. Persisted via `zustand/persist` under key `fasalsaathi-user`.
- **`useChatStore`** — Chat messages, session ID, analysis context from the orchestrator pipeline. Handles both standard chat and scan-context injection. Persisted under `fasalsaathi-chat`.
- **`useResultsStore`** — Persisted crop and scheme recommendation results so they survive page navigation.
- **`useFieldStore`** — Manages crop field data (local).
- **`useThemeStore`** — Light/dark toggle, persisted, applies `data-theme` to document root.

### Chat & AI Integration Flow

1. **Standard Chat** — `useChatStore.sendMessage(text)` → `POST /api/v1/chat/` → Backend proxies to AI service → LangGraph `crop_advisor_graph` runs → response displayed.
2. **Orchestrator** — Typing `/analyze <query>` triggers `POST /api/v1/agents/full-analysis` → Backend proxies to AI service orchestrator pipeline → Planner → Crop Agent → Scheme Agent → summary returned and stored in `analysisContext`.
3. **Scan Handoff** — After YOLOv8 pest detection on `ScanPage`, user clicks "Chat with AI Expert" → `injectScanContext()` creates a hidden system message with detection metadata → navigates to chat → AI acknowledges the pest and advises treatment.

---

## 2. Backend (`/backend`)

**Stack:** FastAPI, SQLAlchemy, Alembic, SQLite, JWT (python-jose), bcrypt.

### Entry point: `main.py`

- Creates all tables via `Base.metadata.create_all()`.
- Mounts CORS middleware (allows `localhost:5173` and `localhost:3000`).
- Includes API router at `/api/v1`.

### API Router (`app/api/v1/router.py`)

| Prefix | Module | Purpose |
|---|---|---|
| `/auth` | `endpoints/auth.py` | Register, login (JWT), token refresh |
| `/users` | `endpoints/users.py` | `GET /me`, `PATCH` profile |
| `/crops` | `endpoints/crops.py` | CRUD for crop reference data |
| `/weather` | `endpoints/weather.py` | Proxied weather lookups |
| `/chat` | `endpoints/chat.py` | Proxies chat requests to `AI_SERVICE_URL/api/chat/` |
| `/detect` | `endpoints/detect.py` | Proxies image upload to `AI_SERVICE_URL/detect/` for YOLOv8 inference |
| `/schemes` | `endpoints/schemes.py` | Proxies scheme recommendation to AI service |
| `/agents` | `endpoints/agents.py` | Proxies orchestrator pipeline and individual agent calls |

### Database Models

- **`User`** — email, hashed_password, phone, farmer profile fields (state, district, age, gender, land_size_acres, crops_grown, category, annual_income).
- **`Crop`** — reference table (name, scientific_name, ideal_soil, ideal_season, water_requirement).
- **`Scheme`** — government scheme metadata with structured eligibility JSON, state/crop arrays, age bounds, apply URL.

### Auth

- Password hashing via bcrypt.
- JWT access tokens (7-day expiry by default).
- `get_current_user` dependency via `Authorization: Bearer <token>`.

---

## 3. AI Service (`/ai-service`)

**Stack:** FastAPI, LangChain, LangGraph, Google Gemini (via `langchain-google-genai`), YOLOv8 (Ultralytics).

### Entry point: `main.py` (port 8001)

Mounts four routers:

| Prefix | Router | Purpose |
|---|---|---|
| `/api/chat` | `routers/chat.py` | LangGraph-powered conversational agent |
| `/api/crop-advisor` | `routers/crop_advisor.py` | Direct crop advisory endpoint |
| `/api/v1/agents` | `routers/orchestrator_router.py` | Orchestrator pipeline + individual agent endpoints |
| `/detect` | `routers/detection.py` | YOLOv8 pest detection image upload |

### LLM Configuration (`app/core/llm.py`)

- Factory function `get_llm()` returns a `ChatGoogleGenerativeAI` instance using the Gemini model configured in `.env`.
- `safe_llm_invoke()` wraps every LLM call with retry logic (3 attempts, exponential backoff) for 429 quota errors, and returns a graceful fallback string on persistent failure.

### Multi-Agent Architecture

There are **two distinct agent systems** running in the AI service:

#### A. LangGraph Crop Advisor (Chat Pipeline)

Located in `app/graphs/crop_advisor_graph.py`. This is a **supervisor-worker graph** built with LangGraph's `StateGraph`:

```
START → supervisor → (conditional) → weather_agent / market_agent / pest_agent → synthesizer → END
                └───────── FINISH ─────────────────────────────────────────────→ synthesizer → END
```

- **Supervisor Node** — LLM-based router. Parses the user query and decides which specialist agent should respond (WEATHER_EXPERT, MARKET_EXPERT, PEST_EXPERT, or FINISH).
- **Worker Nodes** — Each specialist has access to tools (weather API, market API) and a domain-specific prompt. They produce contextual advice.
- **Synthesizer Node** — Final node that merges worker advice with any `analysis_context` (crop/scheme results from the orchestrator) into a cohesive, farmer-friendly response.
- **Greeting fast-path** — Simple greetings bypass the full graph via regex matching in the chat router, saving 2 LLM calls.

#### B. Agent Orchestrator Pipeline

Located in `services/agent_orchestrator.py`. This is a **sequential pipeline** with shared context:

```
User Input → Planner Agent → [Pest Context] → Crop Recommendation Agent → Scheme Recommendation Agent → Unified Summary
```

- **Planner Agent** (`app/agents/planner_agent.py`) — Dynamically decides which agents (pest, crop, scheme) need to run based on the user's query and existing context. Uses low-temperature LLM for deterministic JSON output.
- **Crop Recommendation Agent** (`app/agents/crop_recommendation_agent.py`) — Takes farmer profile (state, soil, season, water, past crops, pest context) and returns 3–5 ranked crop suggestions with confidence scores.
- **Scheme Recommendation Agent** (`app/agents/scheme_recommendation_agent.py`) — Matches the farmer's profile against 25+ Indian government schemes, scoring eligibility.
- **Shared Context** — Each agent's output is injected into a `shared_context` dict. The crop agent's output (crop names, reasoning) feeds into the scheme agent for more relevant matches.
- **Failure Isolation** — If one agent fails, the pipeline continues. Errors are logged per-step.

### YOLOv8 Pest Detection (`/detect`)

- Accepts image upload (JPG, PNG, WebP).
- Saves to a temp file, runs `infer.py → run_inference()` using a trained YOLOv8 model.
- Returns JSON with detected pest names, bounding boxes, confidence scores, severity levels, and treatment suggestions.
- Temp file cleaned up in `finally` block.

---

## 4. Data Flow Summary

```
Farmer opens app
  → Signup/Login (Backend JWT)
  → Onboarding (profile saved to Backend DB)
  → Dashboard loads (weather, soil, alerts from field data)

Farmer scans a crop image
  → Frontend uploads to Backend /api/v1/detect
  → Backend proxies to AI Service /detect
  → YOLOv8 runs inference → results returned
  → Farmer clicks "Chat with AI" → scan context injected into chat

Farmer asks a question in chat
  → Frontend sends to Backend /api/v1/chat/
  → Backend proxies to AI Service /api/chat/
  → LangGraph supervisor routes to specialist → synthesizer responds

Farmer requests crop/scheme recommendations
  → Frontend calls Backend /api/v1/agents/*
  → Backend proxies to AI Service orchestrator
  → Planner → Crop Agent → Scheme Agent → unified summary
  → Results persisted in useResultsStore + shared as analysisContext with chat
```

---

## 5. Running Locally

```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 — AI Service
cd ai-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# Terminal 3 — Frontend
cd frontend
npm install
npm run dev
```

**Required environment variables:**

- `backend/.env` — `DATABASE_URL`, `SECRET_KEY`, `AI_SERVICE_URL`
- `ai-service/.env` — `GOOGLE_API_KEY`, `LLM_MODEL` (e.g. `gemini-1.5-flash`), `LLM_TEMPERATURE`
- `frontend/.env` — `VITE_API_BASE_URL` (defaults to `http://localhost:8000/api/v1`)
