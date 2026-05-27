from pydantic import BaseModel


class MatchResultItem(BaseModel):
    rank: int
    course_id: str
    course_title: str
    match_score: float
    matched_keywords: list[str]


class MatchRunResponse(BaseModel):
    student_document_id: str
    total_courses_compared: int
    results: list[MatchResultItem]

