from pydantic import BaseModel


class FarmerContext(BaseModel):
    profile: dict
    farms: list[dict]
    active_crops: list[dict]
    recent_pests: list[dict]
    recent_journal_entries: list[dict]
    farm_summary: dict
    season_context: dict
