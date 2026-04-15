"""
Agricultural AI Planner Agent
─────────────────────────────
Dynamically determines which agents (pest, crop, scheme) need to run
based on the farmer's raw query and available context.
"""
import json
import logging
from typing import Dict, Any

from app.core.llm import get_llm, safe_llm_invoke
from app.schemas.agent_schemas import PlannerResponse

logger = logging.getLogger(__name__)

PLANNER_PROMPT = """
You are an **Agricultural AI Planner** inside a system called **FasalSaathi**.

Your role is to **analyze the farmer's query and decide which agents should be executed**, NOT to answer the query.

---

## 🧩 Available Agents

1. pest
   - Detects or identifies pests/diseases from symptoms or images
   - Provides pest-related context that may affect crop decisions

2. crop
   - Recommends suitable crops based on farmer conditions (soil, season, location, pest context)

3. scheme
   - Suggests relevant government schemes, subsidies, or financial assistance
   - Uses crop recommendations and farmer profile for personalization

---

## 📥 Inputs Available to You

You may receive:
- Farmer Query: Natural language input
- shared_context (optional):
  - pest_detection (e.g., "aphids detected")
  - crop_recommendations (e.g., ["wheat", "mustard"])
  - user profile (location, land size, etc.)

Use this context intelligently:
- If required data is already present, avoid re-calling that agent unnecessarily
- Build decisions based on BOTH query + context

---

## 🧠 Decision Rules

### 1. Pest Agent
Include "pest" if:
- Query mentions insects, pests, disease, infection, damage symptoms
- OR image-related diagnosis is implied
- OR pest context is missing but needed for safe crop recommendation

### 2. Crop Agent
Include "crop" if:
- Query asks what to grow, crop suggestions, next season planning
- OR pest is present and crop decision depends on it
- OR no crop recommendations exist in shared_context

### 3. Scheme Agent
Include "scheme" if:
- Query mentions subsidy, loan, insurance, government help
- OR crops are recommended and financial support is relevant
- OR scheme suggestions are not already in context

---

## 🔗 Dependency Awareness
- pest -> influences crop (avoid pest-susceptible crops)
- crop -> influences scheme (schemes depend on crop choices)

If multiple needs are present, include ALL relevant agents.

---

## ⚙️ Execution Priority Rules
Always follow this strict order if running multiple:
1. pest
2. crop
3. scheme

Only include agents that are necessary.

---

## 🚫 Important Constraints
- DO NOT answer the farmer's question
- DO NOT hallucinate new agents
- DO NOT include unnecessary agents
- ONLY return valid JSON (no markdown, no explanation outside JSON)

---

## 📤 Output Format

{{
  "agents": ["pest", "crop", "scheme"],
  "priority": ["pest", "crop", "scheme"],
  "reasoning": "clear and short explanation based on query and context"
}}

---

## 🧾 Farmer Query
"{user_query}"

## 📎 Shared Context
{shared_context}
"""

def _fallback_plan() -> str:
    """Fallback plan if the LLM fails."""
    return json.dumps({
        "agents": ["pest", "crop", "scheme"],
        "priority": ["pest", "crop", "scheme"],
        "reasoning": "Fallback to running all agents due to LLM error."
    })


async def run_planner_agent(user_query: str, shared_context: Dict[str, Any]) -> PlannerResponse:
    """
    Execute the Planner Agent.
    """
    logger.info("🧠 Planner Agent invoked for query: '%s'", user_query)
    
    if not user_query:
        # Default to running all if no query is provided (legacy mode)
        logger.info("🧠 No user query, defaulting to full sequential pipeline.")
        return PlannerResponse(
            agents=["pest", "crop", "scheme"],
            priority=["pest", "crop", "scheme"],
            reasoning="No query provided; running default sequential pipeline."
        )

    context_str = json.dumps(shared_context, indent=2) if shared_context else "No active context."
    
    prompt_text = PLANNER_PROMPT.format(
        user_query=user_query,
        shared_context=context_str
    )

    llm = get_llm(temperature=0.1) # low temp for deterministic JSON
    raw = safe_llm_invoke(
        llm,
        prompt_text,
        fallback=_fallback_plan(),
    )

    try:
        # Strip markdown fences if present
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        if text.startswith("json"):
            text = text[4:].strip()
            
        data = json.loads(text)
        plan = PlannerResponse(**data)
        logger.info("🧠 Planner decision: %s", plan.priority)
        return plan
    except Exception as e:
        logger.error("🧠 Failed to parse Planner output: %s. Falling back to all.", e)
        return PlannerResponse(
            agents=["pest", "crop", "scheme"],
            priority=["pest", "crop", "scheme"],
            reasoning="Parse failure fallback."
        )
