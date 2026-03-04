from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    id: str
    sender_id: str  # driver or regulation user
    recipient_id: str
    content: str
    sent_at: datetime
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
