from __future__ import annotations

from pathlib import Path
from zipfile import BadZipFile, ZipFile
from io import BytesIO

from fastapi import HTTPException, UploadFile, status

from app.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
DOCX_ZIP_SIGNATURE = b"PK\x03\x04"
PDF_SIGNATURE = b"%PDF"
DOCX_REQUIRED_ENTRY = "word/document.xml"
MAX_DOCX_ENTRY_COUNT = 500
MAX_DOCX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024


def validate_upload_metadata(file: UploadFile) -> None:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chi chap nhan file .pdf hoac .docx. Khong ho tro .doc, .txt, anh hoac dinh dang khac.",
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content-Type khong hop le. Chi chap nhan PDF hoac DOCX.",
        )


async def read_limited_upload(file: UploadFile) -> bytes:
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File vuot qua gioi han {settings.max_upload_size_mb} MB.",
        )
    return content


def validate_file_size(content: bytes) -> None:
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File rong khong hop le.",
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File vuot qua gioi han {settings.max_upload_size_mb} MB.",
        )


def validate_file_signature(file: UploadFile, content: bytes) -> None:
    extension = Path(file.filename or "").suffix.lower()
    if extension == ".pdf" and not content.startswith(PDF_SIGNATURE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noi dung file khong phai PDF hop le.",
        )
    if extension == ".docx" and not content.startswith(DOCX_ZIP_SIGNATURE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noi dung file khong phai DOCX hop le.",
        )


def validate_docx_structure(content: bytes) -> None:
    try:
        with ZipFile(BytesIO(content)) as archive:
            entries = archive.infolist()
            names = {entry.filename for entry in entries}
            total_uncompressed_size = sum(entry.file_size for entry in entries)
    except BadZipFile as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noi dung file khong phai DOCX hop le.",
        ) from exc

    if DOCX_REQUIRED_ENTRY not in names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noi dung file khong phai DOCX hop le.",
        )

    if len(entries) > MAX_DOCX_ENTRY_COUNT or total_uncompressed_size > MAX_DOCX_UNCOMPRESSED_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File DOCX co cau truc qua lon hoac bat thuong.",
        )


def validate_upload(file: UploadFile, content: bytes) -> None:
    validate_upload_metadata(file)
    validate_file_size(content)
    validate_file_signature(file, content)
    if Path(file.filename or "").suffix.lower() == ".docx":
        validate_docx_structure(content)


async def read_and_validate_upload(file: UploadFile) -> bytes:
    validate_upload_metadata(file)
    content = await read_limited_upload(file)
    validate_file_size(content)
    validate_file_signature(file, content)
    if Path(file.filename or "").suffix.lower() == ".docx":
        validate_docx_structure(content)
    return content
