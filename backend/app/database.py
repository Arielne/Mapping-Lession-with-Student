from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def connect_mongo() -> None:
    global client, database
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.MONGODB_DB_NAME]


async def close_mongo() -> None:
    if client is not None:
        client.close()


def get_database() -> AsyncIOMotorDatabase:
    if database is None:
        raise RuntimeError("MongoDB has not been initialized")
    return database


async def create_indexes() -> None:
    db = get_database()
    await db.users.create_index("email", unique=True)
    await db.course_documents.create_index("uploaded_by")
    await db.course_documents.create_index("title")
    await db.course_documents.create_index("processing_status")
    await db.student_documents.create_index("user_id")
    await db.student_documents.create_index("student_code")
    await db.student_documents.create_index("processing_status")
    await db.match_results.create_index("student_document_id")
    await db.match_results.create_index("course_document_id")
    await db.match_results.create_index([("student_document_id", 1), ("rank", 1)])

