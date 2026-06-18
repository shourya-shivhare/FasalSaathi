"""
FasalSaathi unified graph state — the single TypedDict for the entire pipeline.

Key design decisions:
  - NO tool_registry in state (lives in runtime context, never checkpointed)
  - NO uploaded_image bytes (only uploaded_image_id: str)
  - intervention_attempts for loop prevention
  - graph_path for observability
  - state_schema_version for checkpoint migration
"""
from __future__ import annotations

import operator
from typing import TypedDict, Annotated, Any


def _merge_dicts(left: dict, right: dict) -> dict:
    """Reducer that merges dicts (right overwrites left on key collision)."""
    merged = left.copy()
    merged.update(right)
    return merged


# ── Sub-TypedDicts ────────────────────────────────────────────────────────────


class FarmerProfile(TypedDict, total=False):
    user_id: str
    name: str
    state: str
    district: str
    village: str
    farmer_category: str
    crop_types: list[str]
    annual_income: int | None
    gender: str | None
    age: int | None
    soil_type: str
    season: str
    water_availability: str
    land_size_acres: float | None
    past_crops: list[str]
    preferred_language: str          # "ENGLISH" or "HINDI"
    # Farm Management context (injected by ContextBuilder)
    profile: dict                    # Nested profile data from ContextBuilder
    farms: list[dict]                # Full farm details with active_crop_count
    active_crops: list[dict]         # Active crop cycles with farm association
    crop_history: list[dict]         # Historical completed/abandoned cycles
    pest_history: list[dict]         # Pest detection records
    recent_pests: list[dict]         # Alias for pest_history (backward compat)
    recent_journal_entries: list[dict]
    farm_summary: dict               # Aggregate stats
    season_context: dict


class ExecutionTraceEntry(TypedDict, total=False):
    node: str
    duration_ms: float
    confidence: float
    tools_used: list[str]
    reasoning: str
    status: str             # success | failed | skipped | interrupted
    timestamp: str


class PlannerOutput(TypedDict, total=False):
    agents: list[str]
    execution_hints: dict   # {parallel: [[...]], priority: {...}}
    requires_image: bool
    reasoning: str
    confidence: float


class ValidationResult(TypedDict, total=False):
    validated_agents: list[str]
    execution_graph: dict   # {"groups": [["crop","market"], ["scheme"]]}
    graph_score: float
    warnings: list[str]
    pending_action: str | None
    reasoning: str


# ── Main Graph State ─────────────────────────────────────────────────────────


class FasalSaathiState(TypedDict, total=False):
    # ── Schema Version ────────────────────────────────
    state_schema_version: int       # default: 1

    # ── User Input ────────────────────────────────────
    user_query: str
    farmer_profile: FarmerProfile

    # ── Image (reference only — NO raw bytes) ─────────
    uploaded_image_id: str | None   # UUID pointing to uploads/{id}.ext
    image_metadata: dict | None     # {image_id, filename, mime_type, size_kb, uploaded_at}
    image_context: str | None

    # ── Routing ───────────────────────────────────────
    intent: str                     # greeting | data_retrieval | data_analysis | conversational | workflow | follow_up
    sub_intents: list[str]
    intent_confidence: float
    pending_action: str | None      # waiting_for_image | waiting_for_info | None

    # ── Planning ──────────────────────────────────────
    planner_output: PlannerOutput | None
    validation_result: ValidationResult | None

    # ── Agent Results ─────────────────────────────────
    pest_detection_result: dict | None
    crop_recommendations: dict | None
    market_analysis: dict | None
    scheme_recommendations: dict | None

    # ── Reasoning + Confidence ────────────────────────
    reasoning_steps: Annotated[list[dict], operator.add]
    confidence_scores: Annotated[dict[str, float], _merge_dicts]

    # ── Chat ──────────────────────────────────────────
    messages: Annotated[list, operator.add]
    chat_history: list[dict]

    # ── Memory ────────────────────────────────────────
    memory_context: dict

    # ── Loop Prevention ───────────────────────────────
    intervention_attempts: Annotated[dict[str, int], _merge_dicts]

    # ── Observability ─────────────────────────────────
    execution_trace: Annotated[list[ExecutionTraceEntry], operator.add]
    graph_path: Annotated[list[str], operator.add]
    errors: Annotated[list[dict], operator.add]
    tool_outputs: Annotated[dict[str, Any], _merge_dicts]
    timestamps: Annotated[dict[str, str], _merge_dicts]

    # ── Output ────────────────────────────────────────
    final_response: str
    final_summary: str | None
