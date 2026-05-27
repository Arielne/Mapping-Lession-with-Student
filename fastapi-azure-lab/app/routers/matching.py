from fastapi import APIRouter, Depends, HTTPException, Query, status
from sklearn.feature_extraction.text import CountVectorizer

from app.dependencies import get_current_user, require_database
from app.schemas.matching import MatchResultResponse
from app.services.matching_service import build_matches, calculate_ground_truth_metrics
from app.utils import now_utc, serialize_document, to_object_id

router = APIRouter(prefix="/matching", tags=["Matching"])


async def get_authorized_document(student_document_id: str, db, current_user: dict) -> dict:
    document = await db.student_documents.find_one({"_id": to_object_id(student_document_id), "is_active": True})
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai lieu student.")
    if current_user.get("role") != "admin" and document["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ban khong co quyen chay matching tai lieu nay.")
    return document


@router.post("/student-documents/{student_document_id}", response_model=MatchResultResponse)
async def run_matching(
    student_document_id: str,
    top_k: int = Query(default=3, ge=1, le=20),
    db=Depends(require_database),
    current_user=Depends(get_current_user),
):
    student_document = await get_authorized_document(student_document_id, db, current_user)
    if student_document.get("extraction_status") != "success" or not student_document.get("normalized_text"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tai lieu student khong co text doc duoc. PDF scan chua duoc ho tro OCR trong ban hien tai.",
        )

    course_documents = await db.course_documents.find(
        {"is_active": True, "extraction_status": "success", "normalized_text": {"$ne": ""}}
    ).to_list(length=500)
    if not course_documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chua co tai lieu khoa hoc that da trich xuat text thanh cong de matching.",
        )

    try:
        match_data = build_matches(student_document["normalized_text"], course_documents, top_k)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Khong tao duoc vocabulary matching: {exc}")

    top1_correct, hit_at_3 = calculate_ground_truth_metrics(
        match_data["results"],
        student_document.get("ground_truth_course_id"),
    )
    result_document = {
        "student_document_id": student_document["_id"],
        "algorithm_name": match_data["algorithm_name"],
        "generated_at": now_utc(),
        "processing_time_ms": match_data["processing_time_ms"],
        "vocabulary_size": match_data["vocabulary_size"],
        "top_k": top_k,
        "results": match_data["results"],
        "ground_truth_course_id": student_document.get("ground_truth_course_id"),
        "top1_correct": top1_correct,
        "hit_at_3": hit_at_3,
    }
    await db.match_results.update_one(
        {"student_document_id": student_document["_id"]},
        {"$set": result_document},
        upsert=True,
    )
    saved = await db.match_results.find_one({"student_document_id": student_document["_id"]})
    return serialize_document(saved)


@router.get("/student-documents/{student_document_id}/results", response_model=MatchResultResponse)
async def get_matching_results(
    student_document_id: str,
    db=Depends(require_database),
    current_user=Depends(get_current_user),
):
    student_document = await get_authorized_document(student_document_id, db, current_user)
    result = await db.match_results.find_one({"student_document_id": student_document["_id"]})
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chua co ket qua matching cho tai lieu nay.")
    return serialize_document(result)
