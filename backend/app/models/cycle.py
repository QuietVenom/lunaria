from datetime import date
from pydantic import BaseModel
from typing import Optional

class PhaseDetails(BaseModel):
    energy: str
    emotional: str
    nutrition: str
    exercise: str

class DayInfo(BaseModel):
    date: date
    cycleDay: int
    phase: str
    details: Optional[dict] = None
