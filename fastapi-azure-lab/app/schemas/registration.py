from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.course import CourseResponse


class RegistrationCreate(BaseModel):
    course_id: str


class RegistrationResponse(BaseModel):
    id: str
    user_id: str
    course_id: str
    status: Literal["interested"] = "interested"
    registered_at: datetime


class RegistrationWithCourse(RegistrationResponse):
    course: CourseResponse | None = None
