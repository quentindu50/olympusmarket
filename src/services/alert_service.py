import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class AlertType(Enum):
    LATE_MISSION = "late_mission"
    AUTO_DROP = "auto_drop"
    DRIVER_OUT_OF_ZONE = "driver_out_of_zone"
    NO_GPS_MOVEMENT = "no_gps_movement"
    OPEN_INCIDENT = "open_incident"
    MISSING_DOCUMENT = "missing_document"


@dataclass
class Alert:
    id: str
    type: AlertType
    message: str
    created_at: datetime
    mission_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    driver_id: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class AlertService:
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}

    def create_alert(
        self,
        alert_type: AlertType,
        message: str,
        mission_id: Optional[str] = None,
        vehicle_id: Optional[str] = None,
        driver_id: Optional[str] = None,
    ) -> Alert:
        alert = Alert(
            id=str(uuid.uuid4()),
            type=alert_type,
            message=message,
            created_at=datetime.utcnow(),
            mission_id=mission_id,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
        )
        self.alerts[alert.id] = alert
        return alert

    def resolve_alert(self, alert_id: str) -> Alert:
        alert = self.alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        return alert

    def get_open_alerts(self) -> List[Alert]:
        return [a for a in self.alerts.values() if not a.resolved]

    def get_alerts_for_mission(self, mission_id: str) -> List[Alert]:
        return [a for a in self.alerts.values() if a.mission_id == mission_id]
