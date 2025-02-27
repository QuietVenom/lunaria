from datetime import date, timedelta, datetime, timezone
from typing import Dict, Any
from app.models import PhaseDetails, DayInfo
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_utc_datetime() -> datetime:
    """Gets the current UTC datetime."""
    return datetime.now(timezone.utc)

current_utc_datetime = get_current_utc_datetime()

# Constants
DEFAULT_CYCLE_LENGTH = 28
DEFAULT_PERIOD_LENGTH = 5
LAST_PERIOD_START = (current_utc_datetime.date() - timedelta(days=28))

MIN_CYCLE_LENGTH = 21
MAX_CYCLE_LENGTH = 35

VALID_PHASES = {"menstrual", "follicular", "ovulatory", "luteal"}

# Predefined textual details for each phase
PHASE_DETAILS = {
    "menstrual": PhaseDetails(
        energy="Energy levels may be lower. Focus on rest and gentle movement.",
        emotional="You may experience mood swings. Practice self-compassion.",
        nutrition="Iron-rich foods are important. Stay hydrated and consider warm, nourishing meals.",
        exercise="Light exercises like walking or gentle yoga are recommended.",
    ),
    "follicular": PhaseDetails(
        energy="Energy levels begin to rise. Good time for new projects.",
        emotional="Increased optimism and creativity. Social energy is high.",
        nutrition="Focus on lean proteins and fresh vegetables to support hormonal balance.",
        exercise="Great time for high-intensity workouts and trying new activities.",
    ),
    "ovulatory": PhaseDetails(
        energy="Peak energy levels. Take advantage of natural confidence.",
        emotional="High communication skills and social confidence.",
        nutrition="Eat light, fresh foods. Support detoxification with leafy greens.",
        exercise="Perfect for challenging workouts and endurance training.",
    ),
    "luteal": PhaseDetails(
        energy="Energy gradually decreases. Listen to your body's needs.",
        emotional="May experience PMS symptoms. Focus on self-care.",
        nutrition="Include complex carbs and magnesium-rich foods to support mood.",
        exercise="Moderate exercise like swimming or pilates works well.",
    ),
}

def clamp_cycle_length(value: int) -> int:
    return max(MIN_CYCLE_LENGTH, min(value, MAX_CYCLE_LENGTH))

def get_cycle_day(target_date: date, last_period_start_date: date, cycle_length: int) -> int:
    """
    Calculates the cycle day for a given target date.

    Args:
        target_date: The date for which to calculate the cycle day.
        last_period_start_date: The date of the start of the last menstrual period.
        cycle_length: The length of the menstrual cycle in days.

    Returns:
        The cycle day (1-based).

    Raises:
        ValueError: If input values are invalid.
    """
    if not isinstance(target_date, date) or not isinstance(last_period_start_date, date):
        raise ValueError("target_date and last_period_start_date must be date objects.")
    if cycle_length <= 0:
        raise ValueError("cycle_length must be a positive integer.")
    if target_date < last_period_start_date:
        raise ValueError("Target date can not be before the last period start date.")

    clamped = clamp_cycle_length(cycle_length)
    diff = (target_date - last_period_start_date).days
    return (diff % clamped) + 1

def get_cycle_phase(cycle_day: int, cycle_length: int, period_length: int, luteal_phase_length: int = 14) -> str:
    """
    Estimates the phase of the menstrual cycle based on the cycle day, length, and period length.

    Args:
        cycle_day: The current day of the menstrual cycle (1-based).
        cycle_length: The total length of the menstrual cycle in days.
        period_length: The length of the menstrual period in days.
        luteal_phase_length: The length of the luteal phase in days (defaults to 14).

    Returns:
        The estimated phase of the menstrual cycle ("menstrual", "follicular", "ovulatory", or "luteal").

    Raises:
        ValueError: If any input value is invalid.

    Disclaimer:
        This is a simplified model and may not accurately represent individual menstrual cycles.
        It should not be used for medical purposes.
    """

    if cycle_day <= 0 or cycle_length <= 0 or period_length <= 0 or luteal_phase_length <= 0:
        raise ValueError("Cycle day, cycle length, period length, and luteal phase length must be positive integers.")
    if period_length > cycle_length:
        raise ValueError("Period length cannot be longer than cycle length.")
    clamped = clamp_cycle_length(cycle_length)

    if cycle_day <= period_length:
        return "menstrual"

    luteal_start = clamped - luteal_phase_length
    if cycle_day >= luteal_start:
        return "luteal"

    ovulation_day = clamped - luteal_phase_length - 1
    if ovulation_day <= cycle_day <= ovulation_day + 2:
        return "ovulatory"

    return "follicular"

def get_phase_details(phase: str) -> PhaseDetails:
    if phase not in VALID_PHASES:
        logger.warning(f"Unexpected phase encountered: {phase}")
        return PHASE_DETAILS["follicular"] #returning default
    return PHASE_DETAILS[phase]

def get_day_info(target_date: date, last_period_start_date: date, cycle_length: int, period_length: int, include_details: bool = False) -> DayInfo:
    """
    Retrieves information about a specific date within a menstrual cycle.

    Args:
        target_date: The date for which to retrieve information.
        last_period_start_date: The date of the start of the last menstrual period.
        cycle_length: The length of the menstrual cycle in days.
        period_length: The length of the menstrual period in days.
        include_details: Whether to include detailed phase information.

    Returns:
        A DayInfo object containing date, cycle day, phase, and optional phase details.

    Raises:
        ValueError: If input values are invalid or if an error occurs during phase calculation.
    """
    if not isinstance(target_date, date) or not isinstance(last_period_start_date, date):
        raise ValueError("target_date and last_period_start_date must be date objects.")
    if cycle_length <= 0 or period_length <= 0:
        raise ValueError("cycle_length and period_length must be positive integers.")
    if target_date < last_period_start_date:
        raise ValueError("Target date can not be before the last period start date.")

    try:
        cycle_day = get_cycle_day(target_date, last_period_start_date, cycle_length)
        phase = get_cycle_phase(cycle_day, cycle_length, period_length)

        day_info = DayInfo(
            date=target_date.isoformat(),
            cycleDay=cycle_day,
            phase=phase
        )

        if include_details:
            day_info.details = get_phase_details(phase).model_dump()

        logger.info(f"get_day_info result: {day_info}")
        return day_info

    except ValueError as e:
        raise ValueError(f"Error calculating day info: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")
