from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from bson import ObjectId
from gridfs import AsyncGridFSBucket


def safe_download_filename(filename: str | None) -> str:
    raw_name = Path(filename or "document").name
    clean_name = "".join(char if char.isalnum() or char in "._- " else "_" for char in raw_name).strip()
    return clean_name or "document"


def attachment_content_disposition(filename: str | None) -> str:
    safe_name = safe_download_filename(filename)
    ascii_name = safe_name.encode("ascii", "ignore").decode("ascii") or "document"
    encoded_name = quote(safe_name)
    return f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{encoded_name}'


async def save_file_to_gridfs(
    db,
    filename: str,
    content: bytes,
    content_type: str,
    metadata: dict,
) -> ObjectId:
    bucket = AsyncGridFSBucket(db)
    upload_stream = bucket.open_upload_stream(
        filename,
        metadata={**metadata, "content_type": content_type},
    )
    await upload_stream.write(content)
    await upload_stream.close()
    return upload_stream._id


async def read_file_from_gridfs(db, file_id: ObjectId) -> tuple[bytes, str, str]:
    bucket = AsyncGridFSBucket(db)
    stream = await bucket.open_download_stream(file_id)
    content = await stream.read()
    metadata = stream.metadata or {}
    return content, stream.filename, metadata.get("content_type", "application/octet-stream")
