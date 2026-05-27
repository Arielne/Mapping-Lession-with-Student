from datetime import datetime, timezone
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.database import get_database
from app.dependencies import get_current_admin, get_current_user
from app.schemas.documents import CourseDocumentSummary, CourseUploadResponse, DocumentDetail
from app.utils.file_extractor import MAX_UPLOAD_BYTES, is_supported_file
from app.utils.processing import process_document
from app.utils.serializers import serialize_document

router = APIRouter(prefix="/course-documents", tags=["course-documents"])


@router.post("/upload", response_model=CourseUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_course_document(
    background_tasks: BackgroundTasks,
    current_user: Annotated[dict, Depends(get_current_admin)],
    file: UploadFile = File(...),
    title: str = Form(...),
    source_note: str | None = Form(None),
):
    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    if not is_supported_file(file.filename or "", file.content_type or "", allow_xlsx=True):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    now = datetime.now(timezone.utc)
    document = {
        "title": title.strip(),
        "uploaded_by": current_user["_id"],
        "original_filename": file.filename,
        "file_type": file.content_type,
        "file_size_bytes": len(file_bytes),
        "source_type": "real_course_document",
        "source_note": source_note,
        "extracted_text": "",
        "cleaned_text": "",
        "keywords": [],
        "binary_vector": {},
        "processing_status": "uploaded",
        "error_message": None,
        "created_at": now,
        "updated_at": now,
    }
    result = await get_database().course_documents.insert_one(document)
    background_tasks.add_task(
        process_document,
        "course_documents",
        result.inserted_id,
        file_bytes,
        file.content_type,
        "keywords",
    )
    created = await get_database().course_documents.find_one({"_id": result.inserted_id})
    return serialize_document(created)


@router.get("", response_model=list[CourseDocumentSummary])
async def list_course_documents(
    current_user: Annotated[dict, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query("all", alias="status"),
):
    query = {} if status_filter == "all" else {"processing_status": status_filter}
    cursor = get_database().course_documents.find(query).skip(skip).limit(limit).sort("created_at", -1)
    return [serialize_document(document) async for document in cursor]


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_course_document(document_id: str, current_user: Annotated[dict, Depends(get_current_user)]):
    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=404, detail="Course document not found")
    document = await get_database().course_documents.find_one({"_id": ObjectId(document_id)})
    if document is None:
        raise HTTPException(status_code=404, detail="Course document not found")
    return {"id": document_id, "data": serialize_document(document)}


@router.delete("/{document_id}")
async def delete_course_document(document_id: str, current_user: Annotated[dict, Depends(get_current_admin)]):
    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=404, detail="Course document not found")
    object_id = ObjectId(document_id)
    result = await get_database().course_documents.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Course document not found")
    await get_database().match_results.delete_many({"course_document_id": object_id})
    return {"message": "Course document deleted successfully"}

