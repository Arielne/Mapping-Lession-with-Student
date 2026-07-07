from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.dependencies import require_database, require_student
from app.schemas.registration import RegistrationCreate, RegistrationResponse, RegistrationWithCourse
from app.utils import now_utc, serialize_document, to_object_id

router = APIRouter(prefix="/registrations", tags=["Legacy - Technical Test Only"])


@router.post("", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(
    payload: RegistrationCreate,
    db=Depends(require_database),
    current_user=Depends(require_student),
):
    course_object_id = to_object_id(payload.course_id)
    course = await db.courses.find_one({"_id": course_object_id, "is_active": True})
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay khoa hoc.")

    registration = {
        "user_id": current_user["_id"],
        "course_id": course_object_id,
        "status": "interested",
        "registered_at": now_utc(),
    }
    try:
        result = await db.registrations.insert_one(registration)
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ban da luu khoa hoc nay.")

    created_registration = await db.registrations.find_one({"_id": result.inserted_id})
    return serialize_document(created_registration)


@router.get("/me", response_model=list[RegistrationWithCourse])
async def list_my_registrations(
    db=Depends(require_database),
    current_user=Depends(require_student),
):
    registrations = await db.registrations.find({"user_id": current_user["_id"]}).sort("registered_at", -1).to_list(length=200)
    results = []
    for registration in registrations:
        item = serialize_document(registration)
        course = await db.courses.find_one({"_id": registration["course_id"]})
        item["course"] = serialize_document(course)
        results.append(item)
    return results


@router.delete("/{registration_id}")
async def delete_registration(
    registration_id: str,
    db=Depends(require_database),
    current_user=Depends(require_student),
):
    result = await db.registrations.delete_one(
        {"_id": to_object_id(registration_id), "user_id": current_user["_id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay dang ky.")
    return {"message": "Da huy khoa hoc quan tam."}
