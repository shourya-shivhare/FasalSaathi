"""
Market price tool – stub for LangGraph nodes.
Replace with a real mandi/AGMARKNET API call.
"""
from langchain_core.tools import tool


@tool
def get_market_price(crop: str = "wheat") -> str:
    """Fetch current mandi price for a crop."""
    # TODO: integrate real market API (e.g., Agmarknet)
    return f"Current mandi price for {crop}: ₹2,200/quintal in Delhi mandi."
