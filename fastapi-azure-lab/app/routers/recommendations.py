from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import require_database, require_student
from app.schemas.course import CourseRecommendation
from app.utils import serialize_document, to_object_id

router = APIRouter(prefix="/recommendations", tags=["Legacy - Technical Test Only"])


@router.get("/{need_id}", response_model=list[CourseRecommendation])
async def get_recommendations(
    need_id: str,
    db=Depends(require_database),
    current_user=Depends(require_student),
):
    need = await db.learning_needs.find_one(
        {"_id": to_object_id(need_id), "user_id": current_user["_id"]}
    )
    if need is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay nhu cau hoc.")

    courses = await db.courses.find({"is_active": True}).to_list(length=500)
    desired_skills = {skill.strip().lower() for skill in need.get("desired_skills", [])}
    results = []

    for course in courses:
        score = 0
        if course.get("category") == need.get("desired_category"):
            score += 3
        if course.get("level") == need.get("current_level"):
            score += 2

        course_skills = course.get("skills", [])
        matched_skills = [
            skill for skill in course_skills if skill.strip().lower() in desired_skills
        ]
        score += len(matched_skills)

        if score > 0:
            results.append(
                {
                    "course": serialize_document(course),
                    "match_score": score,
                    "matched_skills": matched_skills,
                }
            )

    return sorted(results, key=lambda item: item["match_score"], reverse=True)
