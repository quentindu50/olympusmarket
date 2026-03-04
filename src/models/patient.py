from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Patient:
    id: str
    last_name: str
    first_name: str
    social_security_number: str
    amo: str  # Assurance Maladie Obligatoire
    postal_code: str
    city: str  # auto-filled from postal code
    amc: Optional[str] = None  # Assurance Maladie Complémentaire
    documents: List[str] = field(default_factory=list)  # document ids
    transport_history: List[str] = field(default_factory=list)  # mission ids
