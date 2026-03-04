from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from .vehicle import VehicleType


class MissionStatus(Enum):
    PENDING = "pending"
    STARTED = "started"
    ARRIVED_ON_SITE = "arrived_on_site"
    PICKED_UP = "picked_up"
    DROPPED = "dropped"
    COMPLETED = "completed"
    AUTO_DROPPED = "auto_dropped"


@dataclass
class MissionStatusEvent:
    status: MissionStatus
    timestamp: datetime
    driver_id: str
    vehicle_id: str
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    is_automatic: bool = False  # True if triggered by auto-drop logic


@dataclass
class Mission:
    id: str
    patient_id: str
    driver_id: str
    vehicle_id: str
    vehicle_type: VehicleType
    pickup_time: datetime
    destination: str
    reason: str
    prescriber_id: str
    status: MissionStatus
    status_events: List[MissionStatusEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    auto_drop_delay_minutes: int = 20
    auto_drop_triggered: bool = False
    transport_document_present: bool = False
    prescription_validated: bool = False
    distance_km: Optional[float] = None
