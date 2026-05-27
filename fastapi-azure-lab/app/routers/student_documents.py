from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.dependencies import get_current_user, require_database, require_student
from app.schemas.student_document import DocumentPurpose, StudentDocumentDetail, StudentDocumentListItem
from app.services.file_validation_service import validate_upload
from app.services.gridfs_storage_service import read_file_from_gridfs, save_file_to_gridfs
from app.services.text_extraction_service import extract_text
from app.services.text_normalization_service import normalize_text, preview_text
from app.utils import now_utc, serialize_document, to_object_id

router = APIRouter(prefix="/student/documents", tags=["Student Documents"])


def with_preview(document: dict) -> dict:
    item = serialize_document(document)
    item["text_preview"] = preview_text(item.get("normalized_text", ""))
    return item


async def get_authorized_student_document(document_id: str, db, current_user: dict) -> dict:
    document = await db.student_documents.find_one({"_id": to_object_id(document_id)})
    if document is None or not document.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai lieu student.")
    if current_user.get("role") != "admin" and document["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ban khong co quyen truy cap tai lieu nay.")
    return document


@router.post("/upload", response_model=StudentDocumentDetail, status_code=status.HTTP_201_CREATED)
async def upload_student_document(
    student_alias: str = Form(...),
    document_purpose: DocumentPurpose = Form(...),
    consent_confirmed: bool = Form(...),
    file: UploadFile = File(...),
    db=Depends(require_database),
    current_user=Depends(require_student),
):
    if not consent_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ban phai xac nhan file duoc phep su dung va da an thong tin nhay cam neu can.",
        )

    content = await file.read()
    validate_upload(file, content)
    gridfs_file_id = await save_file_to_gridfs(
        db,
        file.filename or "uploaded-student-document",
        content,
        file.content_type or "application/octet-stream",
        {"uploaded_by": str(current_user["_id"]), "document_type": "student_document"},
    )
    extracted_text, extraction_error = extract_text(file.filename or "", content)
    normalized_text = normalize_text(extracted_text)
    if extraction_error:
        extraction_status = "failed"
    elif normalized_text:
        extraction_status = "success"
    else:
        extraction_status = "empty_text"

    document = {
        "user_id": current_user["_id"],
        "student_alias": student_alias,
        "document_purpose": document_purpose,
        "gridfs_file_id": gridfs_file_id,
        "original_filename": file.filename or "",
        "content_type": file.content_type or "",
        "file_size_bytes": len(content),
        "extracted_text": extracted_text,
        "normalized_text": normalized_text,
        "extraction_status": extraction_status,
        "extraction_error": extraction_error,
        "consent_confirmed": consent_confirmed,
        "ground_truth_course_id": None,
        "uploaded_at": now_utc(),
        "is_active": True,
    }
    result = await db.student_documents.insert_one(document)
    created = await db.student_documents.find_one({"_id": result.inserted_id})
    return with_preview(created)


@router.get("/me", response_model=list[StudentDocumentListItem])
async def list_my_student_documents(db=Depends(require_database), current_user=Depends(require_student)):
    documents = await db.student_documents.find(
        {"user_id": current_user["_id"], "is_active": True}
    ).sort("uploaded_at", -1).to_list(length=200)
    return [with_preview(document) for document in documents]


@router.get("/{document_id}", response_model=StudentDocumentDetail)
async def get_student_document(document_id: str, db=Depends(require_database), current_user=Depends(get_current_user)):
    document = await get_authorized_student_document(document_id, db, current_user)
    return with_preview(document)


@router.get("/{document_id}/download")
async def download_student_document(document_id: str, db=Depends(require_database), current_user=Depends(get_current_user)):
    document = await get_authorized_student_document(document_id, db, current_user)
    content, filename, content_type = await read_file_from_gridfs(db, document["gridfs_file_id"])
    return Response(
        content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{document_id}")
async def soft_delete_student_document(document_id: str, db=Depends(require_database), current_user=Depends(get_current_user)):
    document = await get_authorized_student_document(document_id, db, current_user)
    await db.student_documents.update_one(
        {"_id": document["_id"]},
        {"$set": {"is_active": False}},
    )
    return {"message": "Da an tai lieu student. File goc GridFS duoc giu lai."}
