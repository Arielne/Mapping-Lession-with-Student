import re

from fastapi import APIRouter, Depends, Query

from app.dependencies import require_database, require_student
from app.services.text_normalization_service import preview_text
from app.utils import serialize_document

router = APIRouter(prefix="/course-documents", tags=["Course Document Search"])


def to_search_item(document: dict) -> dict:
    item = serialize_document(document)
    return {
        "id": item["id"],
        "course_title": item.get("course_title", ""),
        "course_description": item.get("course_description", ""),
        "source_name": item.get("source_name", ""),
        "original_filename": item.get("original_filename", ""),
        "text_preview": preview_text(item.get("normalized_text", "")),
        "is_active": item.get("is_active", True),
    }


@router.get("/search")
async def search_course_documents(
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=20, ge=1, le=50),
    db=Depends(require_database),
    current_user=Depends(require_student),
):
    keyword = q.strip()
    query = {"is_active": True}
    if keyword:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        query["$or"] = [
            {"course_title": pattern},
            {"course_description": pattern},
            {"source_name": pattern},
            {"original_filename": pattern},
            {"normalized_text": pattern},
        ]

    documents = await db.course_documents.find(query).sort("course_title", 1).to_list(length=limit)
    return [to_search_item(document) for document in documents]
