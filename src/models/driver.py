from dataclasses import dataclass, field
from typing import Optional
from .vehicle import VehicleType


@dataclass
class Driver:
    id: str
    first_name: str
    last_name: str
    vehicle_id: Optional[str] = None
    vehicle_type: VehicleType = VehicleType.AMBULANCE

    @property
    def identifier(self) -> str:
        """2-letter identifier: first letter of last name + first letter of first name."""
        return (self.last_name[0] + self.first_name[0]).upper()
