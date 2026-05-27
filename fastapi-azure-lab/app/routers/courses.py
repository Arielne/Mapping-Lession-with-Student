from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import require_admin, require_database
from app.schemas.course import CourseCreate, CourseLevel, CourseResponse, CourseUpdate
from app.utils import clean_update_data, now_utc, serialize_document, serialize_documents, to_object_id

router = APIRouter(prefix="/courses", tags=["Legacy - Technical Test Only"])


@router.get("", response_model=list[CourseResponse])
async def list_courses(
    category: str | None = Query(default=None),
    level: CourseLevel | None = Query(default=None),
    db=Depends(require_database),
):
    filters = {"is_active": True}
    if category:
        filters["category"] = category
    if level:
        filters["level"] = level

    courses = await db.courses.find(filters).sort("created_at", -1).to_list(length=200)
    return serialize_documents(courses)


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str, db=Depends(require_database)):
    course = await db.courses.find_one({"_id": to_object_id(course_id), "is_active": True})
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay khoa hoc.")
    return serialize_document(course)


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreate,
    db=Depends(require_database),
    current_admin=Depends(require_admin),
):
    now = now_utc()
    course = payload.model_dump()
    course["created_at"] = now
    course["updated_at"] = now
    result = await db.courses.insert_one(course)
    created_course = await db.courses.find_one({"_id": result.inserted_id})
    return serialize_document(created_course)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    payload: CourseUpdate,
    db=Depends(require_database),
    current_admin=Depends(require_admin),
):
    update_data = clean_update_data(payload.model_dump())
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Khong co du lieu de cap nhat.")

    update_data["updated_at"] = now_utc()
    result = await db.courses.update_one({"_id": to_object_id(course_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay khoa hoc.")

    updated_course = await db.courses.find_one({"_id": to_object_id(course_id)})
    return serialize_document(updated_course)


@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    db=Depends(require_database),
    current_admin=Depends(require_admin),
):
    result = await db.courses.update_one(
        {"_id": to_object_id(course_id)},
        {"$set": {"is_active": False, "updated_at": now_utc()}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay khoa hoc.")
    return {"message": "Da an khoa hoc."}
