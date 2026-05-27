from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.course import CourseLevel


class LearningNeedBase(BaseModel):
    desired_category: str = Field(..., min_length=2, max_length=80)
    current_level: CourseLevel
    desired_skills: list[str] = Field(default_factory=list)
    learning_goal: str = Field(..., min_length=5, max_length=500)


class LearningNeedCreate(LearningNeedBase):
    pass


class LearningNeedUpdate(BaseModel):
    desired_category: str | None = Field(default=None, min_length=2, max_length=80)
    current_level: CourseLevel | None = None
    desired_skills: list[str] | None = None
    learning_goal: str | None = Field(default=None, min_length=5, max_length=500)


class LearningNeedResponse(LearningNeedBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
