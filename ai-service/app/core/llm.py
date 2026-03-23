"""
LLM factory – returns a configured ChatGoogleGenerativeAI instance.
Swap this out to change the provider (OpenAI, Ollama, etc.).
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings


def get_llm(temperature: float | None = None):
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
    )
