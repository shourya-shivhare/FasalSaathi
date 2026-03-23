from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import uuid

from app.chains.chat_chain import chat_chain

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    session_id = payload.session_id or str(uuid.uuid4())
    user_input = payload.messages[-1].content

    answer = chat_chain.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}},
    )
    return ChatResponse(answer=answer, session_id=session_id)
