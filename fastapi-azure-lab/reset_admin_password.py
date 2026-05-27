import asyncio
import getpass
import os

from dotenv import load_dotenv
from pymongo import AsyncMongoClient

from app.config import settings
from app.security import hash_password
from app.utils import now_utc

load_dotenv()


async def main() -> None:
    if not settings.mongodb_url:
        print("MONGODB_URL chua duoc cau hinh. Khong the reset password admin.")
        return

    email = os.getenv("ADMIN_EMAIL", "admin@coursematch.local").strip().lower()
    password = os.getenv("ADMIN_PASSWORD") or getpass.getpass("New admin password: ")

    if not password:
        print("Password khong duoc de trong.")
        return

    client = AsyncMongoClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    result = await db.users.update_one(
        {"email": email, "role": "admin"},
        {
            "$set": {
                "password_hash": hash_password(password),
                "updated_at": now_utc(),
            }
        },
    )
    await client.close()

    if result.matched_count == 0:
        print(f"Khong tim thay admin: {email}")
        return

    print(f"Da reset password admin local: {email}")


if __name__ == "__main__":
    asyncio.run(main())
