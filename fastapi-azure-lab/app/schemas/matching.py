from datetime import datetime

from pydantic import BaseModel


class MatchItem(BaseModel):
    rank: int
    course_document_id: str
    course_title: str
    score: float
    matched_terms: list[str]
    student_active_terms: int
    course_active_terms: int


class MatchResultResponse(BaseModel):
    id: str
    student_document_id: str
    algorithm_name: str
    generated_at: datetime
    processing_time_ms: float
    vocabulary_size: int
    top_k: int
    results: list[MatchItem]
    ground_truth_course_id: str | None = None
    top1_correct: bool | None = None
    hit_at_3: bool | None = None
