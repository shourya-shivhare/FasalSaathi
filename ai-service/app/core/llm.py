"""
LLM factory – returns a configured ChatGoogleGenerativeAI instance.
Includes retry logic for transient 429 (quota) errors.
"""
import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, AIMessage
from app.core.config import settings

logger = logging.getLogger(__name__)

# Maximum retries for 429 RESOURCE_EXHAUSTED errors
MAX_RETRIES = 3
BASE_DELAY = 5  # seconds


def get_llm(temperature: float | None = None):
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
        max_retries=2,          # langchain's built-in retry
        request_timeout=30,
    )


def safe_llm_invoke(llm, prompt, fallback: str = "I'm sorry, I'm temporarily unavailable. Please try again in a moment.") -> str:
    """
    Invoke LLM with retry logic for 429 quota errors.
    Returns the response content string, or fallback on persistent failure.
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = llm.invoke(prompt)
            content = response.content
            if isinstance(content, list):
                # Join text blocks if content is a list
                content = "".join(str(block.get("text", "")) if isinstance(block, dict) else str(block) for block in content)
            return str(content)
        except Exception as e:
            err_str = str(e).lower()
            is_quota_error = any(kw in err_str for kw in [
                "429", "resource_exhausted", "quota", "rate limit",
                "too many requests", "resourceexhausted"
            ])
            if is_quota_error and attempt < MAX_RETRIES - 1:
                delay = BASE_DELAY * (2 ** attempt)
                logger.warning(f"Quota limit hit (attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {delay}s...")
                time.sleep(delay)
                continue
            else:
                logger.error(f"LLM invoke failed: {e}")
                return fallback
    return fallback
