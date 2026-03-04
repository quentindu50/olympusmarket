from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PrescriberType(Enum):
    DOCTOR = "doctor"
    SERVICE = "service"
    HOSPITAL = "hospital"
    DIALYSIS_CENTER = "dialysis_center"
    CLINIC = "clinic"


@dataclass
class Prescriber:
    id: str
    type: PrescriberType
    name: str
    address: str
    phone: Optional[str] = None
