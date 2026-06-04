from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_user, require_database
from app.schemas.matching import MatchResultResponse
from app.services.matching_service import build_matches, calculate_ground_truth_metrics
from app.utils import now_utc, serialize_document, to_object_id

router = APIRouter(prefix="/matching", tags=["Matching"])


def ensure_match_item_fields(result: dict) -> dict:
    for item in result.get("results", []):
        if not isinstance(item, dict):
            continue
        item.setdefault("course_id", item.get("course_document_id"))
        item.setdefault("source_course_document_id", item.get("course_document_id"))
        item.setdefault("match_score", item.get("score", 0.0))
        item.setdefault("similarity_score", item.get("score", item.get("match_score", 0.0)))
        item.setdefault("matched_keywords", item.get("relevant_skills", item.get("matched_terms", []))[:12])
        item.setdefault("missing_keywords", item.get("missing_or_recommended_skills", []))
        item.setdefault("explanation", item.get("recommendation_reason", "No explanation is available for this saved result."))
        item.setdefault("recommendation_reason", "Ket qua cu chua co ly do goi y. Hay tao goi y lai de cap nhat giai thich.")
        item.setdefault("relevant_skills", item.get("matched_terms", [])[:12])
        item.setdefault("missing_or_recommended_skills", [])
        item.setdefault("suggested_learning_outcomes", item.get("missing_or_recommended_skills", []))
        item.setdefault(
            "score_breakdown",
            {
                "career_goal_score": 0.0,
                "current_skill_match_score": 0.0,
                "missing_skill_coverage_score": 0.0,
                "text_similarity_score": item.get("score", 0.0),
            },
        )
        item.setdefault("algorithm_name", result.get("algorithm_name", "binary_jaccard_ngram_v1"))
        item.setdefault("algorithm", item.get("algorithm_name", result.get("algorithm_name", "binary_jaccard_ngram_v1")))
        item.setdefault("is_recommended", item.get("similarity_score", item.get("score", 0.0)) > 0)
        item.setdefault("created_at", result.get("generated_at", now_utc()))
        item.setdefault("explanation_algorithm_name", "keyword_overlap_v1")
        item.setdefault("baseline_algorithm_name", None)
        item.setdefault("student_active_terms", 0)
        item.setdefault("course_active_terms", 0)
    result["recommendations"] = result.get("recommendations") or result.get("results", [])
    return result


async def get_authorized_document(student_document_id: str, db, current_user: dict) -> dict:
    document = await db.student_documents.find_one({"_id": to_object_id(student_document_id), "is_active": True})
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai lieu student.")
    if current_user.get("role") != "admin" and document["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ban khong co quyen chay matching tai lieu nay.")
    return document


async def _run_matching_for_document(
    student_document_id: str,
    top_k: int,
    db,
    current_user: dict,
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
        "recommendations": match_data["recommendations"],
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
    return ensure_match_item_fields(serialize_document(saved))


@router.post("/student-documents/{student_document_id}", response_model=MatchResultResponse)
async def run_matching(
    student_document_id: str,
    top_k: int = Query(default=3, ge=1, le=20),
    db=Depends(require_database),
    current_user=Depends(get_current_user),
):
    return await _run_matching_for_document(student_document_id, top_k, db, current_user)


@router.post("/recommend/{student_document_id}", response_model=MatchResultResponse)
async def post_recommend_courses(
    student_document_id: str,
    top_k: int = Query(default=3, ge=1, le=20),
    db=Depends(require_database),
    current_user=Depends(get_current_user),
):
    return await _run_matching_for_document(student_document_id, top_k, db, current_user)


@router.get("/recommend/{student_document_id}", response_model=MatchResultResponse)
async def get_recommend_courses(
    student_document_id: str,
    top_k: int = Query(default=3, ge=1, le=20),
    db=Depends(require_database),
    current_user=Depends(get_current_user),
):
    return await _run_matching_for_document(student_document_id, top_k, db, current_user)


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
    return ensure_match_item_fields(serialize_document(result))
