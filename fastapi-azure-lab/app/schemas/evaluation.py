from pydantic import BaseModel


class GroundTruthUpdate(BaseModel):
    course_document_id: str


class EvaluationRow(BaseModel):
    student_document_id: str
    student_alias: str
    ground_truth_course_id: str
    ground_truth_course_title: str | None = None
    predicted_top1_course_id: str | None = None
    predicted_top1_course_title: str | None = None
    top1_correct: bool | None = None
    hit_at_3: bool | None = None


class EvaluationSummary(BaseModel):
    message: str
    total_labeled_documents: int
    top1_correct_count: int
    top1_accuracy: float | None = None
    hit_at_3_count: int
    hit_rate_at_3: float | None = None
    average_processing_time_ms: float | None = None
    rows: list[EvaluationRow]
