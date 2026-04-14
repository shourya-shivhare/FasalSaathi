import logging
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from langchain_core.messages import HumanMessage, AIMessage

from app.graphs.crop_advisor_graph import crop_advisor_graph

router = APIRouter()
logger = logging.getLogger(__name__)

# ── Greeting fast-path ────────────────────────────────────────────────────────
# Simple greetings that don't need the full LangGraph pipeline (saves 2 LLM calls)
GREETING_PATTERNS = re.compile(
    r"^\s*(hi|hello|hey|namaste|namaskar|namasте|ram ram|jai hind|"
    r"good\s*(morning|afternoon|evening|night)|"
    r"kaise ho|kya hal|howdy|sup|yo|hola)\s*[!?.]*\s*$",
    re.IGNORECASE
)

GREETING_RESPONSES = [
    "Namaste! 🌾 I'm FasalSaathi, your smart farming companion. I can help you with:\n\n"
    "🌦️ **Weather updates** for your area\n"
    "💰 **Market prices** & mandi rates\n"
    "🐛 **Pest identification** & crop disease advice\n"
    "🌱 **Crop advisory** & farming tips\n\n"
    "How can I help you today?",
]


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: str | None = None
    context: Dict[str, Any] | None = None
    analysis_context: Dict[str, Any] | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    session_id = payload.session_id or str(uuid.uuid4())
    user_input = payload.messages[-1].content if payload.messages else ""

    # ── Fast-path: handle greetings without LLM calls ─────────────────────
    if len(payload.messages) <= 1 and GREETING_PATTERNS.match(user_input):
        logger.info(f"Greeting fast-path for: {user_input!r}")
        return ChatResponse(answer=GREETING_RESPONSES[0], session_id=session_id)

    # ── Full agentic pipeline ─────────────────────────────────────────────
    # Convert history for LangGraph
    history = []
    for m in payload.messages[:-1]:
        if m.role == "user":
            history.append(HumanMessage(content=m.content))
        else:
            history.append(AIMessage(content=m.content))

    # Extract location from context if present
    location = "Delhi"
    if payload.context:
        city = payload.context.get("district") or payload.context.get("city")
        state = payload.context.get("state")
        if city and state:
            location = f"{city}, {state}"
        elif city or state:
            location = city or state

    initial_state = {
        "messages": history + [HumanMessage(content=user_input)],
        "next_agent": "",
        "worker_context": "",
        "location": location,
        "final_answer": "",
        "analysis_context": payload.analysis_context or {},
    }

    try:
        result = crop_advisor_graph.invoke(initial_state)
        answer = result.get("final_answer", "")
        if not answer:
            answer = "I couldn't process that request. Could you rephrase your question?"
        return ChatResponse(answer=answer, session_id=session_id)
    except Exception as e:
        err_str = str(e).lower()
        is_quota = any(kw in err_str for kw in [
            "429", "resource_exhausted", "quota", "rate limit", "resourceexhausted"
        ])
        if is_quota:
            logger.warning(f"Quota exhausted during graph invoke: {e}")
            return ChatResponse(
                answer="⚠️ I'm experiencing high traffic right now. Please wait a moment and try again. "
                       "The AI service has a rate limit that resets shortly.",
                session_id=session_id
            )
        logger.error(f"Graph invoke error: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")
