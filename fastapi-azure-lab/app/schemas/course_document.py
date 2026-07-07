from datetime import datetime
from typing import Literal

from pydantic import BaseModel
from pydantic import Field

ExtractionStatus = Literal["success", "empty_text", "failed"]


class CourseDocumentListItem(BaseModel):
    id: str
    course_title: str
    source_name: str
    source_url_or_note: str | None = None
    course_description: str = ""
    manual_skills: list[str] = Field(default_factory=list)
    original_filename: str
    content_type: str
    file_size_bytes: int
    extraction_status: ExtractionStatus
    extracted_skills: list[str] = Field(default_factory=list)
    text_preview: str = ""
    uploaded_by: str
    created_at: datetime
    updated_at: datetime
    is_active: bool


class CourseDocumentDetail(CourseDocumentListItem):
    gridfs_file_id: str
    extracted_text: str
    normalized_text: str


class CourseDocumentUpdate(BaseModel):
    course_title: str | None = None
    source_name: str | None = None
    source_url_or_note: str | None = None
    course_description: str | None = None
    manual_skills: list[str] | None = None
    is_active: bool | None = None
