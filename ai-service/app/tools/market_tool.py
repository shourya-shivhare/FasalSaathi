"""
Market price tool — fetches real mandi prices from AGMARKNET API.
Used by LangGraph market_worker node in crop_advisor_graph.
"""
import asyncio
import logging
from langchain_core.tools import tool
from app.tools.agmarknet_client import fetch_mandi_prices

logger = logging.getLogger(__name__)


@tool
def get_market_price(crop: str = "wheat", location: str = "Delhi") -> str:
    """Fetch current real mandi price for a crop from AGMARKNET API."""
    try:
        # Run the async client in a sync context
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, fetch_mandi_prices(crop, location))
                records = future.result(timeout=15)
        else:
            records = asyncio.run(fetch_mandi_prices(crop, location))

        if not records:
            return f"Market data temporarily unavailable for {crop} in {location}. Please try again shortly."

        # Build a summary from the top records
        lines = [f"Current mandi prices for {crop} in {location}:"]
        for r in records[:5]:
            lines.append(
                f"  • {r.get('market', 'Unknown')} ({r.get('district', '')}): "
                f"₹{r.get('modal_price', 'N/A')}/qtl "
                f"(Min: ₹{r.get('min_price', 'N/A')}, Max: ₹{r.get('max_price', 'N/A')}) "
                f"— {r.get('arrival_date', '')}"
            )
        return "\n".join(lines)

    except Exception as e:
        logger.error("get_market_price tool error: %s", e)
        return f"Market data temporarily unavailable for {crop}. Please try again shortly."
