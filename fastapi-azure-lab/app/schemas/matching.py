from datetime import datetime

from pydantic import BaseModel, Field


class MatchItem(BaseModel):
    rank: int
    course_id: str
    course_document_id: str
    source_course_document_id: str
    course_title: str
    score: float
    match_score: float
    similarity_score: float
    course_summary: str = ""
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    explanation: str
    matched_terms: list[str]
    recommendation_reason: str
    relevant_skills: list[str]
    missing_or_recommended_skills: list[str]
    suggested_learning_outcomes: list[str] = Field(default_factory=list)
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    algorithm_name: str
    algorithm: str
    is_recommended: bool
    created_at: datetime
    explanation_algorithm_name: str | None = None
    baseline_algorithm_name: str | None = None
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
    recommendations: list[MatchItem] = Field(default_factory=list)
    ground_truth_course_id: str | None = None
    top1_correct: bool | None = None
    hit_at_3: bool | None = None
