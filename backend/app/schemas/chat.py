from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: str | None = None
    context: dict | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str | None = None
