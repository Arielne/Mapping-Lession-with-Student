from datetime import datetime

from pydantic import BaseModel, Field


class FavoriteCourseCreate(BaseModel):
    course_document_id: str
    source_student_document_id: str | None = None
    match_score: float | None = None
    note: str | None = None


class FavoriteCourseResponse(BaseModel):
    id: str
    user_id: str
    course_document_id: str
    source_student_document_id: str | None = None
    match_score: float | None = None
    note: str | None = None
    saved_at: datetime
    course_title: str
    source_name: str = ""
    source_url_or_note: str | None = None
    original_filename: str = ""
    extracted_skills: list[str] = Field(default_factory=list)
    text_preview: str = ""
    is_active: bool = True
