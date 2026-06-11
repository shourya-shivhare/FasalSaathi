# Deployment and Environment Configuration Guide

This document outlines the system requirements, environment configurations, and setup steps required to deploy FasalSaathi in local development and production environments.

---

## System Requirements

- **Operating System**: Linux (recommended for production YOLO inference), macOS, or Windows 10/11.
- **Python**: Version `3.11` or `3.12` (avoid Python 3.13 in production if PyTorch/YOLO GPU compilation is required).
- **Node.js**: Version `18` or `20` (LTS versions).
- **Databases**:
  - **PostgreSQL**: For core user profile registry and application storage.
  - **SQLite**: Used internally by the AI Service for thread checkpointers (`graph_checkpoints.db`) and user memories (`ai_memory.db`).

---

## 1. Environment Configurations

Create `.env` files in each of the three project directories.

### Frontend Client (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Backend API Gateway (`backend/.env`)
```env
PROJECT_NAME=FasalSaathi
DATABASE_URL=postgresql://postgres:postgres_password@localhost:5432/fasalsaathi
SECRET_KEY=your-jwt-signing-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]
AI_SERVICE_URL=http://localhost:8001
```

### AI Service (`ai_service/.env`)
```env
GOOGLE_API_KEY=your-gemini-studio-api-key
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.3
YOLO_WEIGHTS_PATH=models/best.pt
YOLO_CONF_THRESHOLD=0.35
YOLO_OUTPUT_DIR=uploads/detections
```

---

## 2. YOLOv8 Model Setup

FasalSaathi requires trained YOLOv8 model weights for pest classification.
1. Place the weights file `best.pt` in: `FasalSaathi/models/best.pt` or `FasalSaathi/ai_service/models/best.pt`.
2. The path is configured via `YOLO_WEIGHTS_PATH` in the AI Service `.env`.
3. At startup, the AI service automatically checks if the file exists and loads it into memory via Ultralytics YOLO engine.

---

## 3. Deployment Steps

Follow these steps to spin up the system.

### Step A: Backend Setup & Database Migration
1. Activate virtual environment and install requirements:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Initialize database schemas:
   ```bash
   # Ensure PostgreSQL is running and database 'fasalsaathi' exists
   python -c "from app.db.session import engine; from app.models.base import Base; Base.metadata.create_all(bind=engine)"
   ```
3. Run the gateway server:
   ```bash
   uvicorn main:app --port 8000 --reload
   ```

### Step B: AI Service Setup
1. Activate virtual environment and install dependencies:
   ```bash
   cd ../ai_service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start the AI service on port 8001:
   ```bash
   uvicorn main:app --port 8001 --reload
   ```
   *Note: At startup, the service runs a cleaning script that sweeps expired image cache items from the `uploads/` folder.*

### Step C: Frontend Launch
1. Install node dependencies:
   ```bash
   cd ../frontend
   npm install
   ```
2. Launch Vite dev server:
   ```bash
   npm run dev
   ```

---

## 4. Quota and Error Management

Because the Gemini free tier enforces a strict limit of 15 requests per minute, the AI Service implements:
1. **Exponential Retry Policy**: Calls to LLMs and remote weather services are wrapped in `retry_async` using custom `RetryPolicy` rules:
   - **LLM_RETRY**: 3 attempts, base delay 2s, max delay 10s. Limits retry scope to API rate limit codes (e.g. 429, resource_exhausted).
2. **Graceful Quota Intercepts**: If rate limits are exhausted, the API returns a structured message: *"I'm experiencing high traffic right now. Please wait a moment and try again."* instead of throwing internal server errors.

---

## Code References
- API configuration: [config.py](file:///e:/Desktop/Web%20Development/FasalSaathi/ai_service/app/core/config.py)
- Startup logic: [main.py](file:///e:/Desktop/Web%20Development/FasalSaathi/ai_service/main.py)
- Gateway entry: [main.py](file:///e:/Desktop/Web%20Development/FasalSaathi/backend/main.py)
