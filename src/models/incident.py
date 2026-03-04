from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class IncidentType(Enum):
    MISSION = "mission"
    VEHICLE = "vehicle"


@dataclass
class Incident:
    id: str
    type: IncidentType
    driver_id: str
    description: str
    reported_at: datetime
    mission_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    resolved: bool = False
