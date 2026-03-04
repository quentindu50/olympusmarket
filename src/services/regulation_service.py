from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ..models.mission import Mission, MissionStatus
from .mission_service import MissionService


class RegulationService:
    def __init__(self, mission_service: MissionService):
        self.mission_service = mission_service
        self.alerts: List[Dict] = []

    def get_dashboard(self, date: Optional[datetime] = None) -> Dict:
        if date is None:
            date = datetime.utcnow()

        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        now = datetime.utcnow()

        missions_today = [
            m for m in self.mission_service.missions.values()
            if day_start <= m.pickup_time < day_end
        ]

        active_statuses = {
            MissionStatus.PENDING,
            MissionStatus.STARTED,
            MissionStatus.ARRIVED_ON_SITE,
            MissionStatus.PICKED_UP,
            MissionStatus.DROPPED,
        }
        late_missions = [
            m for m in self.mission_service.missions.values()
            if m.pickup_time < now and m.status in active_statuses
        ]

        ambulances_on_site = [
            m for m in self.mission_service.missions.values()
            if m.status == MissionStatus.ARRIVED_ON_SITE
        ]

        return {
            "missions_today": missions_today,
            "late_missions": late_missions,
            "ambulances_on_site": ambulances_on_site,
            "open_incidents": 0,  # Placeholder; integrate with IncidentService if needed
            "available_vehicles": 0,
            "available_drivers": 0,
        }

    def create_mission(
        self,
        patient_id: str,
        driver_id: str,
        vehicle_id: str,
        vehicle_type,
        pickup_time: datetime,
        destination: str,
        reason: str,
        prescriber_id: str,
    ) -> Tuple[Optional[Mission], List[str]]:
        errors = []
        end_time = pickup_time + timedelta(hours=2)

        if self.mission_service.check_vehicle_conflict(vehicle_id, pickup_time, end_time):
            errors.append(f"Vehicle {vehicle_id} has a conflicting mission")

        if self.mission_service.check_driver_conflict(driver_id, pickup_time, end_time):
            errors.append(f"Driver {driver_id} has a conflicting mission")

        if errors:
            return None, errors

        mission = self.mission_service.create_mission(
            patient_id=patient_id,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            vehicle_type=vehicle_type,
            pickup_time=pickup_time,
            destination=destination,
            reason=reason,
            prescriber_id=prescriber_id,
        )
        return mission, []

    def get_real_time_tracking(self, mission_id: str) -> Dict:
        mission = self.mission_service.get_mission(mission_id)
        if mission is None:
            return {}

        last_event = mission.status_events[-1] if mission.status_events else None
        elapsed = None
        if last_event:
            elapsed = (datetime.utcnow() - last_event.timestamp).total_seconds()

        last_gps = None
        if last_event and last_event.gps_latitude is not None:
            last_gps = {
                "latitude": last_event.gps_latitude,
                "longitude": last_event.gps_longitude,
            }

        return {
            "mission_id": mission_id,
            "current_status": mission.status.value,
            "last_gps_position": last_gps,
            "elapsed_time_since_last_event": elapsed,
            "status_events": [
                {
                    "status": e.status.value,
                    "timestamp": e.timestamp.isoformat(),
                    "gps_latitude": e.gps_latitude,
                    "gps_longitude": e.gps_longitude,
                    "is_automatic": e.is_automatic,
                }
                for e in mission.status_events
            ],
        }

    def add_alert(self, alert_type: str, mission_id: str, message: str):
        self.alerts.append(
            {"type": alert_type, "mission_id": mission_id, "message": message, "resolved": False}
        )

    def get_open_alerts(self) -> List[Dict]:
        return [a for a in self.alerts if not a.get("resolved", False)]
