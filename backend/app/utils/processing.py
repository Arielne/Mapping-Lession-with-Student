import asyncio
from datetime import datetime, timezone

from bson import ObjectId

from app.database import get_database
from app.utils.file_extractor import extract_text
from app.utils.keyword_extractor import extract_keywords
from app.utils.text_cleaner import clean_text
from app.utils.vectorizer import build_binary_vector


async def process_document(
    collection_name: str,
    document_id: ObjectId,
    file_bytes: bytes,
    mime_type: str,
    keyword_field: str,
) -> None:
    db = get_database()
    collection = db[collection_name]
    now = datetime.now(timezone.utc)
    await collection.update_one(
        {"_id": document_id},
        {"$set": {"processing_status": "processing", "updated_at": now}},
    )
    try:
        extracted_text = await asyncio.to_thread(extract_text, file_bytes, mime_type)
        cleaned_text = clean_text(extracted_text)
        keywords = extract_keywords(cleaned_text)
        binary_vector = build_binary_vector(keywords)
        await collection.update_one(
            {"_id": document_id},
            {
                "$set": {
                    "extracted_text": extracted_text,
                    "cleaned_text": cleaned_text,
                    keyword_field: keywords,
                    "binary_vector": binary_vector,
                    "processing_status": "processed",
                    "error_message": None,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
    except Exception as exc:
        await collection.update_one(
            {"_id": document_id},
            {
                "$set": {
                    "processing_status": "failed",
                    "error_message": str(exc),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

