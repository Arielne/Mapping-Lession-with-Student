from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.dependencies import require_admin, require_database
from app.schemas.course_document import CourseDocumentDetail, CourseDocumentListItem
from app.services.file_validation_service import validate_upload
from app.services.gridfs_storage_service import read_file_from_gridfs, save_file_to_gridfs
from app.services.text_extraction_service import extract_text
from app.services.text_normalization_service import extract_skills, normalize_text, preview_text
from app.utils import now_utc, serialize_document, serialize_documents, to_object_id

router = APIRouter(prefix="/admin/course-documents", tags=["Admin Course Documents"])


def with_preview(document: dict) -> dict:
    item = serialize_document(document)
    item["text_preview"] = preview_text(item.get("normalized_text", ""))
    return item


@router.post("/upload", response_model=CourseDocumentDetail, status_code=status.HTTP_201_CREATED)
async def upload_course_document(
    course_title: str = Form(...),
    source_name: str = Form(...),
    source_url_or_note: str | None = Form(default=None),
    file: UploadFile = File(...),
    db=Depends(require_database),
    current_admin=Depends(require_admin),
):
    content = await file.read()
    validate_upload(file, content)

    gridfs_file_id = await save_file_to_gridfs(
        db,
        file.filename or "uploaded-course-document",
        content,
        file.content_type or "application/octet-stream",
        {"uploaded_by": str(current_admin["_id"]), "document_type": "course_document"},
    )
    extracted_text, extraction_error = extract_text(file.filename or "", content)
    normalized_text = normalize_text(extracted_text)
    extracted_skills = extract_skills(normalized_text)
    if extraction_error:
        extraction_status = "failed"
    elif normalized_text:
        extraction_status = "success"
    else:
        extraction_status = "empty_text"

    now = now_utc()
    document = {
        "course_title": course_title,
        "source_name": source_name,
        "source_url_or_note": source_url_or_note,
        "gridfs_file_id": gridfs_file_id,
        "original_filename": file.filename or "",
        "content_type": file.content_type or "",
        "file_size_bytes": len(content),
        "extracted_text": extracted_text,
        "normalized_text": normalized_text,
        "extracted_skills": extracted_skills,
        "extraction_status": extraction_status,
        "extraction_error": extraction_error,
        "uploaded_by": current_admin["_id"],
        "created_at": now,
        "updated_at": now,
        "is_active": True,
    }
    result = await db.course_documents.insert_one(document)
    created = await db.course_documents.find_one({"_id": result.inserted_id})
    return with_preview(created)


@router.get("", response_model=list[CourseDocumentListItem])
async def list_course_documents(db=Depends(require_database), current_admin=Depends(require_admin)):
    documents = await db.course_documents.find({}).sort("created_at", -1).to_list(length=200)
    return [with_preview(document) for document in documents]


@router.get("/{document_id}", response_model=CourseDocumentDetail)
async def get_course_document(document_id: str, db=Depends(require_database), current_admin=Depends(require_admin)):
    document = await db.course_documents.find_one({"_id": to_object_id(document_id)})
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai lieu khoa hoc.")
    return with_preview(document)


@router.get("/{document_id}/download")
async def download_course_document(document_id: str, db=Depends(require_database), current_admin=Depends(require_admin)):
    document = await db.course_documents.find_one({"_id": to_object_id(document_id)})
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai lieu khoa hoc.")
    content, filename, content_type = await read_file_from_gridfs(db, document["gridfs_file_id"])
    return Response(
        content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{document_id}")
async def soft_delete_course_document(document_id: str, db=Depends(require_database), current_admin=Depends(require_admin)):
    result = await db.course_documents.update_one(
        {"_id": to_object_id(document_id)},
        {"$set": {"is_active": False, "updated_at": now_utc()}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai lieu khoa hoc.")
    return {"message": "Da an tai lieu khoa hoc. File goc GridFS duoc giu lai de bao toan lich su."}
