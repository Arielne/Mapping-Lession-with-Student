from bson import ObjectId
from gridfs import AsyncGridFSBucket


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
