import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from ..models.document import Document, DocumentType


class DocumentService:
    def __init__(self):
        self.documents: Dict[str, Document] = {}

    def add_document(
        self,
        doc_type: DocumentType,
        patient_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Document:
        doc = Document(
            id=str(uuid.uuid4()),
            type=doc_type,
            uploaded_at=datetime.now(timezone.utc),
            patient_id=patient_id,
            mission_id=mission_id,
            content=content,
        )
        self.documents[doc.id] = doc
        return doc

    def get_documents_for_mission(self, mission_id: str) -> List[Document]:
        return [d for d in self.documents.values() if d.mission_id == mission_id]

    def get_documents_for_patient(self, patient_id: str) -> List[Document]:
        return [d for d in self.documents.values() if d.patient_id == patient_id]

    def check_mission_documents_complete(
        self, mission_id: str
    ) -> Tuple[bool, List[str]]:
        """Check if BON_TRANSPORT and ORDONNANCE are present for mission."""
        docs = self.get_documents_for_mission(mission_id)
        present_types = {d.type for d in docs}
        required = {DocumentType.BON_TRANSPORT, DocumentType.ORDONNANCE}
        missing = [t.value for t in required if t not in present_types]
        return (len(missing) == 0, missing)

    def notify_missing_documents(self, mission_id: str) -> List[str]:
        """Return list of missing document types for a mission."""
        _, missing = self.check_mission_documents_complete(mission_id)
        return missing
