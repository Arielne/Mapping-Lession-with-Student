from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import require_admin, require_database
from app.schemas.evaluation import EvaluationSummary, GroundTruthUpdate
from app.schemas.student_document import StudentDocumentListItem
from app.services.matching_service import calculate_ground_truth_metrics
from app.services.text_normalization_service import preview_text
from app.utils import serialize_document, to_object_id

router = APIRouter(prefix="/admin", tags=["Evaluation"])


def student_with_preview(document: dict) -> dict:
    item = serialize_document(document)
    item["text_preview"] = preview_text(item.get("normalized_text", ""))
    return item


@router.get("/student-documents", response_model=list[StudentDocumentListItem])
async def list_student_documents_for_admin(db=Depends(require_database), current_admin=Depends(require_admin)):
    documents = await db.student_documents.find({"is_active": True}).sort("uploaded_at", -1).to_list(length=500)
    return [student_with_preview(document) for document in documents]


@router.put("/student-documents/{student_document_id}/ground-truth")
async def update_ground_truth(
    student_document_id: str,
    payload: GroundTruthUpdate,
    db=Depends(require_database),
    current_admin=Depends(require_admin),
):
    student_document = await db.student_documents.find_one({"_id": to_object_id(student_document_id), "is_active": True})
    if student_document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai lieu student.")

    course_document = await db.course_documents.find_one(
        {"_id": to_object_id(payload.course_document_id), "is_active": True}
    )
    if course_document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai lieu khoa hoc ground truth.")

    ground_truth_id = course_document["_id"]
    await db.student_documents.update_one(
        {"_id": student_document["_id"]},
        {"$set": {"ground_truth_course_id": ground_truth_id}},
    )

    match_result = await db.match_results.find_one({"student_document_id": student_document["_id"]})
    if match_result is not None:
        top1_correct, hit_at_3 = calculate_ground_truth_metrics(match_result.get("results", []), ground_truth_id)
        await db.match_results.update_one(
            {"_id": match_result["_id"]},
            {
                "$set": {
                    "ground_truth_course_id": ground_truth_id,
                    "top1_correct": top1_correct,
                    "hit_at_3": hit_at_3,
                }
            },
        )

    return {"message": "Da cap nhat ground truth.", "ground_truth_course_id": str(ground_truth_id)}


@router.get("/evaluation/summary", response_model=EvaluationSummary)
async def get_evaluation_summary(db=Depends(require_database), current_admin=Depends(require_admin)):
    labeled_documents = await db.student_documents.find(
        {"is_active": True, "ground_truth_course_id": {"$ne": None}}
    ).to_list(length=500)

    rows = []
    processing_times = []
    top1_correct_count = 0
    hit_at_3_count = 0

    for document in labeled_documents:
        match_result = await db.match_results.find_one({"student_document_id": document["_id"]})
        if match_result is None:
            continue

        ground_truth_course = await db.course_documents.find_one({"_id": document["ground_truth_course_id"]})
        results = match_result.get("results", [])
        predicted_top1 = results[0] if results else None
        top1_correct = match_result.get("top1_correct")
        hit_at_3 = match_result.get("hit_at_3")
        if top1_correct:
            top1_correct_count += 1
        if hit_at_3:
            hit_at_3_count += 1
        processing_times.append(float(match_result.get("processing_time_ms", 0)))

        rows.append(
            {
                "student_document_id": str(document["_id"]),
                "student_alias": document.get("student_alias", ""),
                "ground_truth_course_id": str(document["ground_truth_course_id"]),
                "ground_truth_course_title": ground_truth_course.get("course_title") if ground_truth_course else None,
                "predicted_top1_course_id": str(predicted_top1["course_document_id"]) if predicted_top1 else None,
                "predicted_top1_course_title": predicted_top1.get("course_title") if predicted_top1 else None,
                "top1_correct": top1_correct,
                "hit_at_3": hit_at_3,
            }
        )

    total = len(rows)
    if total == 0:
        return {
            "message": "Chua du du lieu that co ground truth va ket qua matching de danh gia.",
            "total_labeled_documents": 0,
            "top1_correct_count": 0,
            "top1_accuracy": None,
            "hit_at_3_count": 0,
            "hit_rate_at_3": None,
            "average_processing_time_ms": None,
            "rows": [],
        }

    return {
        "message": "Da tinh evaluation tren cac tai lieu co ground truth va match result.",
        "total_labeled_documents": total,
        "top1_correct_count": top1_correct_count,
        "top1_accuracy": top1_correct_count / total,
        "hit_at_3_count": hit_at_3_count,
        "hit_rate_at_3": hit_at_3_count / total,
        "average_processing_time_ms": sum(processing_times) / total,
        "rows": rows,
    }
