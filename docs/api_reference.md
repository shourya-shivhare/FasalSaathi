# FasalSaathi API Specification

FasalSaathi exposes client-facing REST endpoints via the FastAPI API Gateway (:8000) and routes core agentic execution to the FastAPI AI Service (:8001).

This document details the public API endpoints, payloads, response formats, and internal graph state schema.

---

## 1. Gateway REST Endpoints (Port 8000)

All endpoints below are exposed to the React web application.

### Authentication & Users

| Method | Endpoint | Auth | Request Schema / Form | Response |
|---|---|---|---|---|
| **POST** | `/api/v1/auth/register` | None | `{email, password, name}` | User JSON with JWT token |
| **POST** | `/api/v1/auth/login` | None | `{email, password}` | `{access_token, token_type}` |
| **GET** | `/api/v1/users/me` | JWT | None | User Profile JSON |
| **PUT** | `/api/v1/users/me` | JWT | User Profile Dictionary | Updated User Profile JSON |

### Core Chat & Diagnostics

| Method | Endpoint | Auth | Description | Payload Format |
|---|---|---|---|---|
| **POST** | `/api/v1/chat/` | JWT | Multi-turn Chat (Text Only) | JSON |
| **POST** | `/api/v1/detect/` | JWT | Image upload for pest scan | Multipart (form-data + File) |

### AI Pipeline Proxy (Backward-Compatible)

These endpoints are proxied transparently by the Gateway to the AI Service.

#### POST `/api/v1/agents/crop-recommendation`
- **Description**: Triggers crop recommendation agent with target profile.
- **Request Payload**:
  ```json
  {
    "user_id": "string",
    "state": "Madhya Pradesh",
    "district": "Indore",
    "farmer_category": "marginal",
    "soil_type": "Loamy",
    "season": "Kharif",
    "water_availability": "moderate",
    "land_size_acres": 2.5,
    "past_crops": ["rice"],
    "crop_types": ["wheat"]
  }
  ```
- **Response**:
  ```json
  {
    "crop_recommendations": [
      {
        "crop_name": "Soybean",
        "confidence": 0.95,
        "yield_estimate": "8-10 quintals/acre",
        "reasoning": "Fits Kharif season and loamy soil..."
      }
    ],
    "summary": "Full synthesis text...",
    "confidence": 0.95,
    "graph_path": ["memory_retrieve", "intent_router", "planner", "validator", "crop_recommendation", "summary", "memory_persist", "observability"]
  }
  ```

#### POST `/api/v1/agents/scheme-recommendation`
- **Description**: Finds government schemes matching eligibility parameters.
- **Response**: Returns matching items from the 25-scheme database under `scheme_recommendations`.

#### POST `/api/v1/agents/full-analysis`
- **Description**: Runs a sequential pipeline (crop recommend → market analysis → scheme recommend) in a single invocation.

---

## 2. AI Service Internal Endpoints (Port 8001)

These endpoints receive requests from the Gateway proxy.

### POST `/api/chat/`
- **Request Format**:
  ```json
  {
    "messages": [{"role": "user", "content": "What is the market price of wheat?"}],
    "session_id": "thread-abc-123",
    "context": {
      "state": "Madhya Pradesh",
      "soil_type": "Loamy"
    }
  }
  ```
- **Response Format**:
  ```json
  {
    "answer": "The current mandi price for wheat in Indore is 2,400 INR per quintal...",
    "session_id": "thread-abc-123",
    "graph_path": ["memory_retrieve", "intent_router", "planner", "validator", "market_intelligence", "summary", "memory_persist", "observability"],
    "confidence_scores": {"market": 0.9}
  }
  ```

### POST `/api/chat/upload`
- **Request Format**: `multipart/form-data` containing parameters `message`, `session_id`, `state`, `soil_type`, and an optional file field `image`.
- **Response Format**: Matches `/api/chat/` JSON response structure, returning the bounding-box and pest identification summary inside `answer`.

---

## 3. Graph State Schema (`FasalSaathiState`)

The state is transferred as a JSON object during checkpointer operations. Key fields:

```python
class FasalSaathiState(TypedDict):
    state_schema_version: str
    user_query: str
    farmer_profile: dict
    intent: str
    sub_intents: list[str]
    chat_history: list[dict]
    messages: list[AnyMessage]
    crop_recommendations: list[dict]
    market_intelligence: list[dict]
    scheme_recommendations: list[dict]
    pest_detection_result: dict
    confidence_scores: dict[str, float]
    uploaded_image_id: str
    image_metadata: dict
    intervention_attempts: dict[str, int]
    graph_path: list[str]
    timestamps: dict[str, str]
    final_summary: str
    final_response: str
```

---

## Code References
- Chat router: [chat.py](file:///e:/Desktop/Web%20Development/FasalSaathi/ai-service/app/routers/chat.py)
- Agent pipeline router: [agents.py](file:///e:/Desktop/Web%20Development/FasalSaathi/ai-service/app/routers/agents.py)
- State schema definition: [state.py](file:///e:/Desktop/Web%20Development/FasalSaathi/ai-service/app/graph/state.py)
