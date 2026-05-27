from datetime import datetime, timezone
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import get_database
from app.dependencies import get_current_user
from app.schemas.matching import MatchRunResponse
from app.utils.matcher import rank_courses
from app.utils.serializers import serialize_document

router = APIRouter(prefix="/matching", tags=["matching"])


async def _load_student_document(document_id: str, current_user: dict) -> dict:
    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=404, detail="Student document not found")
    document = await get_database().student_documents.find_one({"_id": ObjectId(document_id)})
    if document is None:
        raise HTTPException(status_code=404, detail="Student document not found")
    if current_user["role"] != "admin" and document["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return document


def _response_items(results: list[dict], k: int | None = None) -> list[dict]:
    sliced = results if k is None else results[:k]
    return [
        {
            "rank": item["rank"],
            "course_id": str(item["course_document_id"]),
            "course_title": item["course_title"],
            "match_score": item["match_score"],
            "matched_keywords": item["matched_keywords"],
        }
        for item in sliced
    ]


@router.post("/run/{student_document_id}", response_model=MatchRunResponse)
async def run_matching(
    student_document_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    k: int = Query(3, ge=1, le=50),
):
    student_document = await _load_student_document(student_document_id, current_user)
    if student_document.get("processing_status") != "processed":
        raise HTTPException(status_code=400, detail="Student document not yet processed")

    cursor = get_database().course_documents.find({"processing_status": "processed"})
    courses = [course async for course in cursor]
    ranked = rank_courses(student_document.get("binary_vector") or {}, courses)

    student_object_id = student_document["_id"]
    await get_database().match_results.delete_many({"student_document_id": student_object_id})
    now = datetime.now(timezone.utc)
    records = []
    for item in ranked:
        records.append(
            {
                "student_document_id": student_object_id,
                "course_document_id": item["course_document_id"],
                "match_score": item["match_score"],
                "matched_keywords": item["matched_keywords"],
                "student_keywords": item["student_keywords"],
                "course_keywords": item["course_keywords"],
                "rank": item["rank"],
                "algorithm": item["algorithm"],
                "processing_time_ms": item["processing_time_ms"],
                "created_at": now,
            }
        )
    if records:
        await get_database().match_results.insert_many(records)

    return {
        "student_document_id": student_document_id,
        "total_courses_compared": len(courses),
        "results": _response_items(ranked, k),
    }


@router.get("/results/{student_document_id}")
async def get_matching_results(student_document_id: str, current_user: Annotated[dict, Depends(get_current_user)]):
    student_document = await _load_student_document(student_document_id, current_user)
    cursor = get_database().match_results.find({"student_document_id": student_document["_id"]}).sort("rank", 1)
    return [serialize_document(item) async for item in cursor]


@router.get("/top/{student_document_id}")
async def get_top_matching_results(
    student_document_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    k: int = Query(3, ge=1, le=50),
):
    student_document = await _load_student_document(student_document_id, current_user)
    cursor = (
        get_database()
        .match_results.find({"student_document_id": student_document["_id"]})
        .sort("rank", 1)
        .limit(k)
    )
    results = []
    async for item in cursor:
        course = await get_database().course_documents.find_one({"_id": item["course_document_id"]})
        results.append(
            {
                "rank": item["rank"],
                "course_id": str(item["course_document_id"]),
                "course_title": course["title"] if course else "Deleted course",
                "match_score": item["match_score"],
                "matched_keywords": item["matched_keywords"],
            }
        )
    return {"student_document_id": student_document_id, "results": results}

