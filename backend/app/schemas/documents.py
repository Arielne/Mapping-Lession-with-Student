from datetime import datetime
from typing import Any

from pydantic import BaseModel


class CourseDocumentSummary(BaseModel):
    id: str
    title: str
    original_filename: str
    keywords: list[str] = []
    processing_status: str
    created_at: datetime


class CourseUploadResponse(BaseModel):
    id: str
    title: str
    original_filename: str
    processing_status: str
    created_at: datetime


class StudentUploadResponse(BaseModel):
    id: str
    original_filename: str
    processing_status: str
    created_at: datetime


class StudentDocumentSummary(BaseModel):
    id: str
    original_filename: str
    student_code: str | None = None
    detected_keywords: list[str] = []
    processing_status: str
    created_at: datetime


class DocumentDetail(BaseModel):
    id: str
    data: dict[str, Any]

