# FasalSaathi 🌾

> An AI-powered agricultural assistance platform helping Indian farmers with crop advice, weather insights, and market prices.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + Vite + Tailwind CSS v4 |
| Backend | Python + FastAPI |
| AI Service | Python + FastAPI + LangChain + LangGraph |
| LLM | Google Gemini (via `langchain-google-genai`) |
| Database | SQLAlchemy (SQLite → PostgreSQL in prod) |

## Architecture

```
Browser  (React/Vite — :5173)
    │
    │  REST API calls
    ▼
FastAPI Backend  (:8000)         ← auth, crops, weather, chat proxy
    │
    │  HTTP (httpx)
    ▼
FastAPI AI Service  (:8001)      ← LangChain chains + LangGraph agents
```

## Project Structure

```
FasalSaathi/
├── frontend/               # React + Vite + Tailwind CSS
│   └── src/
│       ├── components/     # common/, layout/, ui/
│       ├── features/       # auth/, chat/, crop/, dashboard/
│       ├── pages/
│       ├── services/       # api.js — unified API client
│       ├── hooks/
│       ├── store/          # global state
│       ├── styles/
│       └── utils/
│
├── backend/                # FastAPI REST API
│   └── app/
│       ├── api/v1/endpoints/   # auth, users, crops, weather, chat
│       ├── core/               # config, security
│       ├── db/                 # SQLAlchemy engine & session
│       ├── models/             # ORM models
│       ├── schemas/            # Pydantic I/O models
│       ├── services/           # business logic
│       └── utils/
│
├── ai-service/             # LangChain + LangGraph AI backend
│   └── app/
│       ├── chains/         # LCEL chains (chat_chain)
│       ├── graphs/         # LangGraph StateGraphs (crop_advisor)
│       ├── tools/          # @tool functions (weather, market)
│       ├── prompts/        # prompt templates
│       ├── memory/         # session chat history
│       ├── routers/        # FastAPI routers
│       └── core/           # config, llm factory
│
└── FasalSaathi.docx        # Project requirements document
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Google AI API key ([get one here](https://aistudio.google.com/))

---

### 1. Frontend
```bash
cd frontend
npm install
npm run dev          # → http://localhost:5173
```

`.env`:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # then fill in values
uvicorn main:app --port 8000 --reload
```

Key `.env` variables:
```
DATABASE_URL=sqlite:///./fasalsaathi.db
SECRET_KEY=your-secret-key
AI_SERVICE_URL=http://localhost:8001
```

---

### 3. AI Service
```bash
cd ai-service
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # then add GOOGLE_API_KEY
uvicorn main:app --port 8001 --reload
```

Key `.env` variables:
```
GOOGLE_API_KEY=your-google-ai-api-key
LLM_MODEL=gemini-1.5-flash
```

---

## API Overview

| Method | Endpoint | Service | Description |
|--------|----------|---------|-------------|
| POST | `/api/v1/auth/register` | Backend | Register a new user |
| POST | `/api/v1/auth/login` | Backend | Login, returns JWT |
| GET | `/api/v1/crops/` | Backend | List all crops |
| GET | `/api/v1/weather/current` | Backend | Current weather |
| POST | `/api/v1/chat/` | Backend → AI | Chat with the AI assistant |
| POST | `/api/chat/` | AI Service | General farming chatbot (LangChain) |
| POST | `/api/crop-advisor/` | AI Service | Crop advisor agent (LangGraph) |

## AI Features

- **Conversational Chat** — multi-turn conversation with session memory using LangChain LCEL
- **Crop Advisor Agent** — LangGraph `StateGraph` that routes queries to weather/market/general advice nodes based on intent
- **Tool Calling** — extensible `@tool` functions for weather API and mandi price lookup
