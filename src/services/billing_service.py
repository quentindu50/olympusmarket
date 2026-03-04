import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from ..models.mission import Mission, MissionStatus

NIGHT_SURCHARGE_RATE = 0.5  # 50% surcharge
SUNDAY_SURCHARGE_RATE = 0.5
BASE_RATE_PER_KM = 2.5  # euros per km


@dataclass
class Invoice:
    id: str
    mission_id: str
    patient_id: str
    base_amount: float
    surcharge_amount: float
    total_amount: float
    distance_km: float
    has_night_surcharge: bool
    has_sunday_surcharge: bool
    tiers_payant: bool
    generated_at: datetime
    status: str  # "draft", "ready", "transmitted"


class BillingService:
    def __init__(self):
        self.invoices: Dict[str, Invoice] = {}

    def check_mission_ready_for_billing(
        self, mission: Mission
    ) -> Tuple[bool, List[str]]:
        missing = []
        if not mission.transport_document_present:
            missing.append("transport_document")
        if not mission.prescription_validated:
            missing.append("prescription")
        if mission.distance_km is None:
            missing.append("distance_km")

        terminal_statuses = {MissionStatus.COMPLETED, MissionStatus.AUTO_DROPPED}
        has_terminal = any(
            e.status in terminal_statuses for e in mission.status_events
        )
        if not has_terminal:
            missing.append("terminal_status")

        return (len(missing) == 0, missing)

    def calculate_invoice(
        self,
        mission: Mission,
        patient,
        distance_km: float,
        tiers_payant: bool = False,
    ) -> Invoice:
        base_amount = distance_km * BASE_RATE_PER_KM
        surcharge_amount = 0.0
        has_night = self.is_night_time(mission.pickup_time)
        has_sunday = self.is_sunday(mission.pickup_time)

        if has_night:
            surcharge_amount += base_amount * NIGHT_SURCHARGE_RATE
        if has_sunday:
            surcharge_amount += base_amount * SUNDAY_SURCHARGE_RATE

        total_amount = base_amount + surcharge_amount

        invoice = Invoice(
            id=str(uuid.uuid4()),
            mission_id=mission.id,
            patient_id=patient.id,
            base_amount=base_amount,
            surcharge_amount=surcharge_amount,
            total_amount=total_amount,
            distance_km=distance_km,
            has_night_surcharge=has_night,
            has_sunday_surcharge=has_sunday,
            tiers_payant=tiers_payant,
            generated_at=datetime.now(timezone.utc),
            status="draft",
        )
        self.invoices[invoice.id] = invoice
        return invoice

    def is_night_time(self, dt: datetime) -> bool:
        """Return True if time is between 22:00 and 06:00."""
        hour = dt.hour
        return hour >= 22 or hour < 6

    def is_sunday(self, dt: datetime) -> bool:
        """Return True if datetime is on Sunday (weekday() == 6)."""
        return dt.weekday() == 6
