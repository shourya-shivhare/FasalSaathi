# FasalSaathi 🌾

> An AI-powered agricultural assistance platform helping Indian farmers with crop advice, weather insights, and market prices.

## Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| React 19 (Vite) | UI framework |
| Tailwind CSS v4 | Styling |

### Backend + AI
| Technology | Purpose |
|---|---|
| FastAPI | REST API server |
| LangChain | LLM chains, RAG pipeline |
| LangGraph | Stateful multi-step AI agents |
| Fine-tuned LLM | Custom model trained on agricultural knowledge base |

### Database
| Technology | Purpose |
|---|---|
| PostgreSQL | User data, crops, sessions |
| FAISS | Vector store for RAG / semantic search |

---

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
    │
    ├── PostgreSQL               ← structured user/app data
    └── FAISS                    ← vector embeddings for RAG
```

---

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

---

## Core Features

### 🌱 Crop & Pest Recommendation
Recommends the best crops and flags potential pest threats based on the farmer's soil type, location, and season. Powered by a **fine-tuned LLM** trained on a curated agricultural knowledge base using FAISS for retrieval-augmented generation (RAG).

### 🌦️ Weather-Based Suggestions
Fetches real-time weather data via an external weather API and provides actionable farming advice — irrigation schedules, sowing windows, frost warnings — tailored to the farmer's location.

### 📜 Government Policy Suggestions
Surfaces relevant central and state government schemes, subsidies, and policies (e.g., PM-KISAN, crop insurance, MSP updates) based on the farmer's profile and crop selection.

---

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Google AI API key ([get one here](https://aistudio.google.com/))

---

### 1. Frontend
```bash
cd frontend
npm install
npm run dev          # → http://localhost:5173
```

`.env`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # fill in values
uvicorn main:app --port 8000 --reload
```

`.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/fasalsaathi
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
cp .env.example .env         # fill in values
uvicorn main:app --port 8001 --reload
```

`.env`:
```env
LLM_API_KEY=your-llm-api-key
FAISS_INDEX_PATH=./faiss_index
WEATHER_API_KEY=your-weather-api-key
```


## AI Features

- **Crop & Pest Recommendation** — fine-tuned LLM + FAISS RAG pipeline over an agricultural knowledge base for context-aware crop and pest advice
- **Weather-Based Suggestions** — real-time weather API integration with LangGraph nodes that translate forecasts into actionable farming guidance
- **Government Policy Suggestions** — retrieval over a curated policy knowledge base to surface relevant schemes, subsidies, and MSP alerts for the farmer
- **Conversational Chat** — multi-turn conversation with session memory using LangChain LCEL
- **Stateful Agent Routing** — LangGraph `StateGraph` classifies each query and routes it to the appropriate node (crop, weather, policy, or general)
- **Tool Calling** — extensible `@tool` functions for weather API, mandi prices, and policy lookup
