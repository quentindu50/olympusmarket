from dataclasses import dataclass
from enum import Enum
from typing import Optional


class VehicleType(Enum):
    AMBULANCE = "ambulance"
    VSL = "vsl"
    TAXI = "taxi"


@dataclass
class Vehicle:
    id: str
    name: str
    type: VehicleType
    is_available: bool = True
    current_driver_id: Optional[str] = None
