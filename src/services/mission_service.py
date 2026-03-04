import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from ..models.mission import Mission, MissionStatus, MissionStatusEvent
from ..models.vehicle import VehicleType

# Valid status transitions
_VALID_TRANSITIONS = {
    MissionStatus.PENDING: {MissionStatus.STARTED},
    MissionStatus.STARTED: {MissionStatus.ARRIVED_ON_SITE},
    MissionStatus.ARRIVED_ON_SITE: {MissionStatus.PICKED_UP, MissionStatus.AUTO_DROPPED},
    MissionStatus.PICKED_UP: {MissionStatus.DROPPED},
    MissionStatus.DROPPED: {MissionStatus.COMPLETED},
    MissionStatus.COMPLETED: set(),
    MissionStatus.AUTO_DROPPED: set(),
}


class MissionService:
    def __init__(self):
        self.missions: Dict[str, Mission] = {}
        self._auto_drop_timers: Dict[str, datetime] = {}  # mission_id -> arrived_at time

    def create_mission(
        self,
        patient_id: str,
        driver_id: str,
        vehicle_id: str,
        vehicle_type: VehicleType,
        pickup_time: datetime,
        destination: str,
        reason: str,
        prescriber_id: str,
        auto_drop_delay_minutes: int = 20,
    ) -> Mission:
        mission_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        initial_event = MissionStatusEvent(
            status=MissionStatus.PENDING,
            timestamp=now,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
        )
        mission = Mission(
            id=mission_id,
            patient_id=patient_id,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            vehicle_type=vehicle_type,
            pickup_time=pickup_time,
            destination=destination,
            reason=reason,
            prescriber_id=prescriber_id,
            status=MissionStatus.PENDING,
            status_events=[initial_event],
            created_at=now,
            auto_drop_delay_minutes=auto_drop_delay_minutes,
        )
        self.missions[mission_id] = mission
        return mission

    def update_status(
        self,
        mission_id: str,
        new_status: MissionStatus,
        driver_id: str,
        vehicle_id: str,
        gps_lat: Optional[float] = None,
        gps_lon: Optional[float] = None,
    ) -> Mission:
        mission = self.missions.get(mission_id)
        if mission is None:
            raise ValueError(f"Mission {mission_id} not found")

        allowed = _VALID_TRANSITIONS.get(mission.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition from {mission.status} to {new_status}"
            )

        event = MissionStatusEvent(
            status=new_status,
            timestamp=datetime.now(timezone.utc),
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            gps_latitude=gps_lat,
            gps_longitude=gps_lon,
        )
        mission.status_events.append(event)
        mission.status = new_status

        if new_status == MissionStatus.ARRIVED_ON_SITE:
            self._auto_drop_timers[mission_id] = event.timestamp

        return mission

    def check_auto_drop(
        self, mission_id: str, current_time: Optional[datetime] = None
    ) -> bool:
        mission = self.missions.get(mission_id)
        if mission is None:
            return False
        if mission.vehicle_type != VehicleType.AMBULANCE:
            return False
        if mission.status != MissionStatus.ARRIVED_ON_SITE:
            return False
        if mission.auto_drop_triggered:
            return False

        arrived_at = self._auto_drop_timers.get(mission_id)
        if arrived_at is None:
            return False

        now = current_time or datetime.now(timezone.utc)
        elapsed = (now - arrived_at).total_seconds() / 60
        if elapsed <= mission.auto_drop_delay_minutes:
            return False

        # Trigger auto-drop
        event = MissionStatusEvent(
            status=MissionStatus.AUTO_DROPPED,
            timestamp=now,
            driver_id=mission.driver_id,
            vehicle_id=mission.vehicle_id,
            is_automatic=True,
        )
        mission.status_events.append(event)
        mission.status = MissionStatus.AUTO_DROPPED
        mission.auto_drop_triggered = True
        return True

    def get_missions_for_driver(self, driver_id: str) -> List[Mission]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        result = []
        for mission in self.missions.values():
            if mission.driver_id != driver_id:
                continue
            # Filter out COMPLETED missions older than 24h
            if mission.status == MissionStatus.COMPLETED:
                completed_events = [
                    e for e in mission.status_events if e.status == MissionStatus.COMPLETED
                ]
                if completed_events and completed_events[-1].timestamp < cutoff:
                    continue
            result.append(mission)
        return result

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        return self.missions.get(mission_id)

    def check_vehicle_conflict(
        self,
        vehicle_id: str,
        start_time: datetime,
        end_time: datetime,
        exclude_mission_id: Optional[str] = None,
    ) -> bool:
        for mission in self.missions.values():
            if mission.vehicle_id != vehicle_id:
                continue
            if exclude_mission_id and mission.id == exclude_mission_id:
                continue
            if mission.status in (MissionStatus.COMPLETED, MissionStatus.AUTO_DROPPED):
                continue
            # Assume mission window is [pickup_time, pickup_time + 2h] if no distance
            mission_end = mission.pickup_time + timedelta(hours=2)
            if start_time < mission_end and end_time > mission.pickup_time:
                return True
        return False

    def check_driver_conflict(
        self,
        driver_id: str,
        start_time: datetime,
        end_time: datetime,
        exclude_mission_id: Optional[str] = None,
    ) -> bool:
        for mission in self.missions.values():
            if mission.driver_id != driver_id:
                continue
            if exclude_mission_id and mission.id == exclude_mission_id:
                continue
            if mission.status in (MissionStatus.COMPLETED, MissionStatus.AUTO_DROPPED):
                continue
            mission_end = mission.pickup_time + timedelta(hours=2)
            if start_time < mission_end and end_time > mission.pickup_time:
                return True
        return False
