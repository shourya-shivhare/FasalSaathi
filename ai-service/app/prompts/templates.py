"""
System prompts for different agents/chains.
Centralise all prompt templates here.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ---------------------------------------------------------------------------
# General farming assistant prompt
# ---------------------------------------------------------------------------
FARMER_SYSTEM_PROMPT = """\
You are FasalSaathi, a friendly and knowledgeable agricultural assistant \
helping Indian farmers with crop advice, weather insights, market prices, \
and best farming practices. \
Answer in simple language. If the farmer writes in Hindi or a regional \
language, respond in the same language."""

farmer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", FARMER_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

# ---------------------------------------------------------------------------
# Crop advisor prompt (used by LangGraph agent)
# ---------------------------------------------------------------------------
CROP_ADVISOR_SYSTEM_PROMPT = """\
You are an expert crop advisor. Given the farmer's location, soil type, \
season, and available resources, recommend the best crops and practices. \
Be specific, practical, and concise."""

crop_advisor_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", CROP_ADVISOR_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)
