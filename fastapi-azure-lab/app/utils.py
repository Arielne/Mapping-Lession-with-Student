from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Id khong dung dinh dang ObjectId.",
        )


def serialize_document(document: dict | None) -> dict | None:
    if document is None:
        return None

    item = dict(document)
    if "_id" in item:
        item["id"] = str(item.pop("_id"))
    for key in (
        "user_id",
        "course_id",
        "uploaded_by",
        "gridfs_file_id",
        "student_document_id",
        "course_document_id",
        "ground_truth_course_id",
    ):
        if key in item and isinstance(item[key], ObjectId):
            item[key] = str(item[key])
    if "results" in item and isinstance(item["results"], list):
        for result in item["results"]:
            if isinstance(result, dict):
                for key in ("course_document_id",):
                    if key in result and isinstance(result[key], ObjectId):
                        result[key] = str(result[key])
    return item


def serialize_documents(documents: list[dict]) -> list[dict]:
    return [serialize_document(document) for document in documents]


def clean_update_data(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}
