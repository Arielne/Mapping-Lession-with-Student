from datetime import datetime
from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from app.schemas.course_document import ExtractionStatus

DocumentPurpose = Literal["learning_need", "anonymized_cv"]


class StudentDocumentListItem(BaseModel):
    id: str
    user_id: str
    student_alias: str
    document_purpose: DocumentPurpose
    original_filename: str
    content_type: str
    file_size_bytes: int
    extraction_status: ExtractionStatus
    extracted_skills: list[str] = Field(default_factory=list)
    consent_confirmed: bool
    ground_truth_course_id: str | None = None
    text_preview: str = ""
    uploaded_at: datetime
    is_active: bool = True


class StudentDocumentDetail(StudentDocumentListItem):
    gridfs_file_id: str
    extracted_text: str
    normalized_text: str
