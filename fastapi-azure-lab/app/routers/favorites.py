from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.dependencies import require_database, require_student
from app.schemas.favorite import FavoriteCourseCreate, FavoriteCourseResponse
from app.services.text_normalization_service import preview_text
from app.utils import now_utc, serialize_document, to_object_id

router = APIRouter(prefix="/student/favorites", tags=["Student Favorites"])


def favorite_with_course(favorite: dict, course: dict | None) -> dict:
    item = serialize_document(favorite)
    if course is None:
        item.update(
            {
                "course_title": "Khoa hoc khong con kha dung",
                "source_name": "",
                "source_url_or_note": None,
                "original_filename": "",
                "extracted_skills": [],
                "text_preview": "",
                "is_active": False,
            }
        )
        return item

    item.update(
        {
            "course_title": course.get("course_title", ""),
            "source_name": course.get("source_name", ""),
            "source_url_or_note": course.get("source_url_or_note"),
            "original_filename": course.get("original_filename", ""),
            "extracted_skills": course.get("extracted_skills", []),
            "text_preview": preview_text(course.get("normalized_text", "")),
            "is_active": course.get("is_active", True),
        }
    )
    return item


@router.post("", response_model=FavoriteCourseResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    payload: FavoriteCourseCreate,
    db=Depends(require_database),
    current_user=Depends(require_student),
):
    course_id = to_object_id(payload.course_document_id)
    course = await db.course_documents.find_one({"_id": course_id, "is_active": True})
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai lieu khoa hoc.")

    favorite = {
        "user_id": current_user["_id"],
        "course_document_id": course_id,
        "source_student_document_id": to_object_id(payload.source_student_document_id)
        if payload.source_student_document_id
        else None,
        "match_score": payload.match_score,
        "note": payload.note,
        "saved_at": now_utc(),
    }
    try:
        result = await db.favorite_course_documents.insert_one(favorite)
    except DuplicateKeyError:
        existing = await db.favorite_course_documents.find_one(
            {"user_id": current_user["_id"], "course_document_id": course_id}
        )
        return favorite_with_course(existing, course)

    created = await db.favorite_course_documents.find_one({"_id": result.inserted_id})
    return favorite_with_course(created, course)


@router.get("/me", response_model=list[FavoriteCourseResponse])
async def list_my_favorites(db=Depends(require_database), current_user=Depends(require_student)):
    favorites = await db.favorite_course_documents.find(
        {"user_id": current_user["_id"]}
    ).sort("saved_at", -1).to_list(length=200)
    results = []
    for favorite in favorites:
        course = await db.course_documents.find_one({"_id": favorite["course_document_id"]})
        results.append(favorite_with_course(favorite, course))
    return results


@router.delete("/{favorite_id}")
async def delete_favorite(favorite_id: str, db=Depends(require_database), current_user=Depends(require_student)):
    result = await db.favorite_course_documents.delete_one(
        {"_id": to_object_id(favorite_id), "user_id": current_user["_id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay khoa hoc yeu thich.")
    return {"message": "Da bo khoi danh sach yeu thich."}


@router.delete("/course-documents/{course_document_id}")
async def delete_favorite_by_course(
    course_document_id: str,
    db=Depends(require_database),
    current_user=Depends(require_student),
):
    result = await db.favorite_course_documents.delete_one(
        {"course_document_id": to_object_id(course_document_id), "user_id": current_user["_id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay khoa hoc yeu thich.")
    return {"message": "Da bo khoi danh sach yeu thich."}
