from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import require_database, require_student
from app.schemas.learning_need import LearningNeedCreate, LearningNeedResponse, LearningNeedUpdate
from app.utils import clean_update_data, now_utc, serialize_document, serialize_documents, to_object_id

router = APIRouter(prefix="/learning-needs", tags=["Legacy - Technical Test Only"])


@router.post("", response_model=LearningNeedResponse, status_code=status.HTTP_201_CREATED)
async def create_learning_need(
    payload: LearningNeedCreate,
    db=Depends(require_database),
    current_user=Depends(require_student),
):
    now = now_utc()
    need = payload.model_dump()
    need["user_id"] = current_user["_id"]
    need["created_at"] = now
    need["updated_at"] = now
    result = await db.learning_needs.insert_one(need)
    created_need = await db.learning_needs.find_one({"_id": result.inserted_id})
    return serialize_document(created_need)


@router.get("/me", response_model=list[LearningNeedResponse])
async def list_my_learning_needs(
    db=Depends(require_database),
    current_user=Depends(require_student),
):
    needs = await db.learning_needs.find({"user_id": current_user["_id"]}).sort("created_at", -1).to_list(length=100)
    return serialize_documents(needs)


@router.put("/{need_id}", response_model=LearningNeedResponse)
async def update_learning_need(
    need_id: str,
    payload: LearningNeedUpdate,
    db=Depends(require_database),
    current_user=Depends(require_student),
):
    need_object_id = to_object_id(need_id)
    update_data = clean_update_data(payload.model_dump())
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Khong co du lieu de cap nhat.")

    update_data["updated_at"] = now_utc()
    result = await db.learning_needs.update_one(
        {"_id": need_object_id, "user_id": current_user["_id"]},
        {"$set": update_data},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay nhu cau hoc.")

    updated_need = await db.learning_needs.find_one({"_id": need_object_id})
    return serialize_document(updated_need)
