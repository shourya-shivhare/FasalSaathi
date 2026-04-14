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
# AGENTIC WORKFLOW PROMPTS
# ---------------------------------------------------------------------------

SUPERVISOR_SYSTEM_PROMPT = """\
You are the Supervisor for FasalSaathi's Agricultural Expert Team. \
Your task is to facilitate a conversation between the farmer and our specialized agents.

Current experts available:
1. WEATHER_EXPERT: For weather forecasts, rain alerts, and impact on crops.
2. MARKET_EXPERT: For mandi prices, market trends, and MSP.
3. PEST_EXPERT: For identifying pests, diseases, and recommending treatments.

Based on the farmer's query, decide which expert should speak. \
If the query is general or a greeting, handle it yourself. \
If you have enough information from the expert, summarize it for the farmer.

Output your choice in the following format:
Next: [AGENT_NAME or FINISH]
Reason: [Simplified reason]"""

WEATHER_SPECIALIST_SYSTEM_PROMPT = """\
You are a Meteorology Expert specialized in Indian agriculture. \
Given the weather data, provide precise advice on irrigation, sowing, or harvest risks. \
Your goal is to protect the farmer's yield from weather-related damage."""

MARKET_SPECIALIST_SYSTEM_PROMPT = """\
You are a Market Trends Expert. You have access to real-time mandi prices. \
Advise the farmer on the best time to sell and where they can get the best price. \
Explain market dynamics simply."""

PEST_SPECIALIST_SYSTEM_PROMPT = """\
You are a Plant Pathology/Entomology Expert. \
You analyze visual detection results or descriptions of pests and diseases. \
Provide both chemical and organic (biopesticide) solutions and list preventive measures."""

# ---------------------------------------------------------------------------
# Exported Templates
# ---------------------------------------------------------------------------

supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", SUPERVISOR_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

weather_specialist_prompt = ChatPromptTemplate.from_messages([
    ("system", WEATHER_SPECIALIST_SYSTEM_PROMPT),
    ("human", "User query: {input}\nContext: {context}"),
])

market_specialist_prompt = ChatPromptTemplate.from_messages([
    ("system", MARKET_SPECIALIST_SYSTEM_PROMPT),
    ("human", "User query: {input}\nContext: {context}"),
])

pest_specialist_prompt = ChatPromptTemplate.from_messages([
    ("system", PEST_SPECIALIST_SYSTEM_PROMPT),
    ("human", "User query: {input}\nContext: {context}"),
])
