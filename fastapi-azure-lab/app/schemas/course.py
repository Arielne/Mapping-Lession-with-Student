from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

CourseLevel = Literal["Beginner", "Intermediate", "Advanced"]


class CourseBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    category: str = Field(..., min_length=2, max_length=80)
    level: CourseLevel
    skills: list[str] = Field(default_factory=list)
    description: str = Field(..., min_length=5)
    duration_weeks: int = Field(..., ge=1, le=100)
    is_active: bool = True


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=150)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    level: CourseLevel | None = None
    skills: list[str] | None = None
    description: str | None = Field(default=None, min_length=5)
    duration_weeks: int | None = Field(default=None, ge=1, le=100)
    is_active: bool | None = None


class CourseResponse(CourseBase):
    id: str
    created_at: datetime
    updated_at: datetime


class CourseRecommendation(BaseModel):
    course: CourseResponse
    match_score: int
    matched_skills: list[str]
