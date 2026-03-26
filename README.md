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
| FastAPI | REST API server (port 8000 + 8001) |
| LangChain | LLM chains, RAG pipeline |
| LangGraph | Stateful multi-step AI agents |
| **YOLOv8 (Ultralytics)** | **Real-time pest detection from farm images** |
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
├── data/                   # YOLO dataset (train/valid/test + data.yaml)
├── models/
│   └── best.pt             # Trained YOLOv8 pest detection weights
│
├── frontend/               # React + Vite + Tailwind CSS
│   └── src/
│       ├── components/     # common/, layout/, ui/
│       ├── features/       # auth/, chat/, crop/, dashboard/
│       ├── pages/
│       ├── services/       # unified API client
│       ├── hooks/
│       ├── store/          # global state (Zustand)
│       └── utils/
│
├── backend/                # FastAPI REST API (:8000)
│   └── app/
│       ├── api/v1/endpoints/   # auth, users, crops, weather, chat, detect
│       ├── core/               # config, security
│       ├── db/                 # SQLAlchemy engine & session
│       ├── models/             # ORM models
│       ├── schemas/            # Pydantic I/O models
│       └── services/           # business logic
│
├── ai-service/             # LangChain + LangGraph + YOLO AI backend (:8001)
│   ├── train.py            # YOLOv8 training script
│   ├── infer.py            # Inference module (CLI + importable)
│   ├── evaluate.py         # Model evaluation (mAP, P, R, F1)
│   ├── utils/
│   │   └── pest_map.py     # Pest → treatment suggestions mapping
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

### 🦟 Real-Time Pest Detection (YOLOv8)
Upload a photo of your crop and get instant pest identification with confidence scores and treatment recommendations. Trained on a **12-class pest dataset** (Ants, Bees, Beetles, Caterpillars, Earwigs, Earthworms, Grasshoppers, Moths, Slugs, Snails, Wasps, Weevils) achieving **mAP@0.5 = 0.773**.

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
GOOGLE_API_KEY=your-google-api-key
YOLO_WEIGHTS_PATH=models/best.pt
YOLO_CONF_THRESHOLD=0.35
```

### 4. ML Pipeline (Pest Detection)
```bash
# Train model (from project root)
python ai-service/train.py --epochs 10

# Evaluate model on test set
python ai-service/evaluate.py

# Run inference on a single image
python ai-service/infer.py --image path/to/crop_photo.jpg
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
| **POST** | **`/api/v1/detect`** | **Backend** | **Upload image → pest detection + suggestions** |
| POST | `/api/chat/` | AI Service | General farming chatbot (LangChain) |
| POST | `/api/crop-advisor/` | AI Service | Crop advisor agent (LangGraph) |

---

## AI Features

- **Crop & Pest Recommendation** — fine-tuned LLM + FAISS RAG pipeline over an agricultural knowledge base for context-aware crop and pest advice
- **Weather-Based Suggestions** — real-time weather API integration with LangGraph nodes that translate forecasts into actionable farming guidance
- **Government Policy Suggestions** — retrieval over a curated policy knowledge base to surface relevant schemes, subsidies, and MSP alerts for the farmer
- **Conversational Chat** — multi-turn conversation with session memory using LangChain LCEL
- **Stateful Agent Routing** — LangGraph `StateGraph` classifies each query and routes it to the appropriate node (crop, weather, policy, or general)
- **Tool Calling** — extensible `@tool` functions for weather API, mandi prices, and policy lookup
