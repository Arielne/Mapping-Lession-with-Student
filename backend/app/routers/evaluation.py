from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_database
from app.dependencies import get_current_admin, get_current_user
from app.schemas.evaluation import LabelRequest

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


def _valid_object_ids(values: list[str]) -> list[ObjectId]:
    if not all(ObjectId.is_valid(value) for value in values):
        raise HTTPException(status_code=400, detail="Invalid ObjectId")
    return [ObjectId(value) for value in values]


@router.post("/labels")
async def save_labels(payload: LabelRequest, current_user: Annotated[dict, Depends(get_current_user)]):
    if not ObjectId.is_valid(payload.student_document_id):
        raise HTTPException(status_code=404, detail="Student document not found")
    student_id = ObjectId(payload.student_document_id)
    document = await get_database().student_documents.find_one({"_id": student_id})
    if document is None:
        raise HTTPException(status_code=404, detail="Student document not found")
    if current_user["role"] != "admin" and document["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    course_ids = _valid_object_ids(payload.validated_course_ids)
    existing_count = await get_database().course_documents.count_documents({"_id": {"$in": course_ids}})
    if existing_count != len(course_ids):
        raise HTTPException(status_code=400, detail="One or more courses do not exist")

    await get_database().student_documents.update_one(
        {"_id": student_id},
        {
            "$set": {
                "validated_course_ids": course_ids,
                "label_source": payload.label_source,
            }
        },
    )
    return {"message": "Labels saved successfully"}


async def _labeled_documents() -> list[dict]:
    cursor = get_database().student_documents.find(
        {"validated_course_ids.0": {"$exists": True}, "processing_status": "processed"}
    )
    return [document async for document in cursor]


async def _metrics_payload() -> tuple[dict, list[dict]]:
    labeled = await _labeled_documents()
    total = len(labeled)
    if total == 0:
        return (
            {
                "total_labeled_students": 0,
                "top1_accuracy": 0.0,
                "hit_rate_at_3": 0.0,
                "avg_processing_time_ms": 0.0,
            },
            [],
        )

    top1_correct = 0
    hit_at_3 = 0
    all_times: list[float] = []
    per_student: list[dict] = []
    for document in labeled:
        cursor = get_database().match_results.find({"student_document_id": document["_id"]}).sort("rank", 1)
        results = [item async for item in cursor]
        validated_ids = {course_id for course_id in document.get("validated_course_ids", [])}
        top1 = results[0] if results else None
        top3 = results[:3]
        is_top1_correct = bool(top1 and top1["course_document_id"] in validated_ids)
        is_hit_at_3 = any(item["course_document_id"] in validated_ids for item in top3)
        if is_top1_correct:
            top1_correct += 1
        if is_hit_at_3:
            hit_at_3 += 1
        all_times.extend(float(item.get("processing_time_ms", 0.0)) for item in results)

        top1_title = None
        if top1:
            course = await get_database().course_documents.find_one({"_id": top1["course_document_id"]})
            top1_title = course["title"] if course else "Deleted course"

        validated_titles = []
        async for course in get_database().course_documents.find({"_id": {"$in": list(validated_ids)}}):
            validated_titles.append(course["title"])

        per_student.append(
            {
                "student_document_id": str(document["_id"]),
                "student_code": document.get("student_code"),
                "top1_correct": is_top1_correct,
                "in_top3": is_hit_at_3,
                "top1_predicted_course": top1_title,
                "validated_courses": validated_titles,
            }
        )

    avg_time = sum(all_times) / len(all_times) if all_times else 0.0
    return (
        {
            "total_labeled_students": total,
            "top1_accuracy": round(top1_correct / total, 4),
            "hit_rate_at_3": round(hit_at_3 / total, 4),
            "avg_processing_time_ms": round(avg_time, 2),
        },
        per_student,
    )


@router.get("/metrics")
async def get_metrics(current_user: Annotated[dict, Depends(get_current_admin)]):
    summary, _ = await _metrics_payload()
    return summary


@router.get("/report")
async def get_report(current_user: Annotated[dict, Depends(get_current_admin)]):
    summary, per_student = await _metrics_payload()
    return {"summary": summary, "per_student": per_student}

