# FasalSaathi 🌾

A full-stack MERN-style web application for agricultural assistance.

## Architecture

```
FasalSaathi/
├── frontend/        # React (Vite) + TailwindCSS
├── backend/         # Node.js + Express REST API
├── ai-service/      # Python FastAPI AI microservice
└── README.md
```

## Getting Started

### Frontend
```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

### Backend
```bash
cd backend
npm install
node server.js       # http://localhost:5000
```

### AI Service
```bash
cd ai-service
pip install -r requirements.txt
python main.py       # http://localhost:8000
```

## Communication Flow

```
React Frontend (5173)
       ↓ REST API calls
Express Backend (5000)
       ↓ HTTP (axios)
FastAPI AI Service (8000)
```

## Environment Variables

Create a `.env` file in `backend/`:
```
PORT=5000
AI_SERVICE_URL=http://localhost:8000
MONGO_URI=mongodb://localhost:27017/fasalsaathi
```

Create a `.env` file in `frontend/`:
```
VITE_API_URL=http://localhost:5000/api
```
