import certifi
from pymongo import ASCENDING, AsyncMongoClient
from pymongo.errors import PyMongoError

from app.config import settings

client: AsyncMongoClient | None = None
db = None
database_status = {
    "configured": bool(settings.mongodb_url),
    "connected": False,
    "message": "MONGODB_URL chua duoc cau hinh.",
}


async def connect_to_mongo() -> None:
    global client, db, database_status

    if not settings.mongodb_url:
        database_status = {
            "configured": False,
            "connected": False,
            "message": "MONGODB_URL chua duoc cau hinh.",
        }
        return

    try:
        client = AsyncMongoClient(
            settings.mongodb_url,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
        )
        db = client[settings.mongodb_db_name]
        await client.admin.command("ping")
        await create_indexes()
        database_status = {
            "configured": True,
            "connected": True,
            "message": "MongoDB da ket noi.",
        }
    except PyMongoError as exc:
        client = None
        db = None
        database_status = {
            "configured": True,
            "connected": False,
            "message": f"Khong ket noi duoc MongoDB: {exc}",
        }


async def close_mongo_connection() -> None:
    global client, db

    if client is not None:
        await client.close()
    client = None
    db = None


async def create_indexes() -> None:
    if db is None:
        return

    await db.users.create_index([("email", ASCENDING)], unique=True)
    await db.course_documents.create_index([("created_at", ASCENDING)])
    await db.course_documents.create_index([("is_active", ASCENDING)])
    await db.student_documents.create_index([("user_id", ASCENDING)])
    await db.student_documents.create_index([("is_active", ASCENDING)])
    await db.match_results.create_index([("student_document_id", ASCENDING)], unique=True)
    await db.favorite_course_documents.create_index(
        [("user_id", ASCENDING), ("course_document_id", ASCENDING)],
        unique=True,
    )
    await db.favorite_course_documents.create_index([("saved_at", ASCENDING)])

    # Legacy technical-test index. These routes are no longer used for official matching.
    await db.registrations.create_index(
        [("user_id", ASCENDING), ("course_id", ASCENDING)],
        unique=True,
    )


def get_database():
    return db


def get_database_status() -> dict:
    return database_status


def get_public_database_status() -> dict:
    configured = bool(database_status.get("configured"))
    connected = bool(database_status.get("connected"))
    if connected:
        status = "connected"
    elif configured:
        status = "unavailable"
    else:
        status = "not_configured"

    return {
        "configured": configured,
        "connected": connected,
        "status": status,
    }
