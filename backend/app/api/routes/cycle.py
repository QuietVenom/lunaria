from fastapi import APIRouter, Query, HTTPException, Depends
from datetime import date, timedelta, datetime, timezone
from typing import Optional
from app.services.cycle import get_day_info
from app.models import DayInfo
import logging

router = APIRouter(prefix="/cycle", tags=["cycle"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_utc_datetime() -> datetime:
    """Gets the current UTC datetime."""
    return datetime.now(timezone.utc)

@router.get("/day-info", response_model=DayInfo)
async def day_info_api(
    query_date: Optional[date] = Query(None, description="The date to check cycle info for (YYYY-MM-DD). Default: today."),
    last_period_start_date: Optional[date] = Query(None, description="The start date of the last period (YYYY-MM-DD)."),
    cycle_length: int = Query(28, ge=21, le=35, description="Approximate total cycle length in days."),
    period_length: int = Query(5, ge=1, description="Number of menstrual (period) days."),
    include_details: bool = Query(False, description="If true, includes textual phase details in response."),
    current_utc_datetime: datetime = Depends(get_current_utc_datetime)
):
    """
    Retrieves information about a specific date within a menstrual cycle.

    Args:
        query_date: The date to check cycle info for (YYYY-MM-DD). Default: today.
        last_period_start_date: The start date of the last period (YYYY-MM-DD).
        cycle_length: Approximate total cycle length in days.
        period_length: Number of menstrual (period) days.
        include_details: If true, includes textual phase details in response.
        current_utc_datetime: current UTC datetime (used for timezone awareness)

    Returns:
        A dictionary containing date, cycle day, phase, and optional phase details.

    Raises:
        HTTPException: If input values are invalid or if an error occurs during calculation.
    """
    target = query_date or current_utc_datetime.date()
    anchor = last_period_start_date or (current_utc_datetime.date() - timedelta(days=28))

    logger.info(f"Request received: query_date={query_date}, last_period_start_date={last_period_start_date}, cycle_length={cycle_length}, period_length={period_length}, include_details={include_details}")

    if last_period_start_date and last_period_start_date > target:
        logger.warning("Last period start date in the future.")
        raise HTTPException(status_code=400, detail="The last period start date cannot be in the future.")

    try:
        return get_day_info(target, anchor, cycle_length, period_length, include_details)
    except ValueError as e:
        logger.error(f"ValueError during calculation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("An unexpected error occurred.") #Logs the full stack trace.
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
