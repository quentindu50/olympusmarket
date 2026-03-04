from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class DocumentType(Enum):
    CARTE_VITALE = "carte_vitale"
    MUTUELLE = "mutuelle"
    BON_TRANSPORT = "bon_transport"
    ORDONNANCE = "ordonnance"
    FEUILLE_SOINS = "feuille_soins"


@dataclass
class Document:
    id: str
    type: DocumentType
    uploaded_at: datetime
    patient_id: Optional[str] = None
    mission_id: Optional[str] = None
    content: Optional[str] = None  # file path or base64
