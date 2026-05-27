from datetime import datetime, timezone
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status

from app.database import get_database
from app.dependencies import get_current_student, get_current_user
from app.schemas.documents import DocumentDetail, StudentDocumentSummary, StudentUploadResponse
from app.utils.file_extractor import MAX_UPLOAD_BYTES, is_supported_file
from app.utils.processing import process_document
from app.utils.serializers import serialize_document

router = APIRouter(prefix="/student-documents", tags=["student-documents"])


@router.post("/upload", response_model=StudentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_student_document(
    background_tasks: BackgroundTasks,
    current_user: Annotated[dict, Depends(get_current_student)],
    file: UploadFile = File(...),
    student_code: str | None = Form(None),
):
    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    if not is_supported_file(file.filename or "", file.content_type or "", allow_xlsx=False):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    now = datetime.now(timezone.utc)
    document = {
        "user_id": current_user["_id"],
        "student_code": student_code,
        "original_filename": file.filename,
        "file_type": file.content_type,
        "file_size_bytes": len(file_bytes),
        "source_type": "real_student_need",
        "extracted_text": "",
        "cleaned_text": "",
        "detected_keywords": [],
        "binary_vector": {},
        "validated_course_ids": [],
        "label_source": None,
        "processing_status": "uploaded",
        "error_message": None,
        "created_at": now,
        "updated_at": now,
    }
    result = await get_database().student_documents.insert_one(document)
    background_tasks.add_task(
        process_document,
        "student_documents",
        result.inserted_id,
        file_bytes,
        file.content_type,
        "detected_keywords",
    )
    created = await get_database().student_documents.find_one({"_id": result.inserted_id})
    return serialize_document(created)


@router.get("/me", response_model=list[StudentDocumentSummary])
async def list_my_documents(current_user: Annotated[dict, Depends(get_current_student)]):
    cursor = get_database().student_documents.find({"user_id": current_user["_id"]}).sort("created_at", -1)
    return [serialize_document(document) async for document in cursor]


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_student_document(document_id: str, current_user: Annotated[dict, Depends(get_current_user)]):
    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=404, detail="Student document not found")
    document = await get_database().student_documents.find_one({"_id": ObjectId(document_id)})
    if document is None:
        raise HTTPException(status_code=404, detail="Student document not found")
    if current_user["role"] != "admin" and document["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"id": document_id, "data": serialize_document(document)}

