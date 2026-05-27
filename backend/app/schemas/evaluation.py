from pydantic import BaseModel, Field


class LabelRequest(BaseModel):
    student_document_id: str
    validated_course_ids: list[str] = Field(min_length=1)
    label_source: str = "student_selected"

