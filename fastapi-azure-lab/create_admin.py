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
        print("MONGODB_URL chua duoc cau hinh. Khong the tao admin.")
        return

    email = os.getenv("ADMIN_EMAIL") or input("Admin email: ").strip().lower()
    full_name = os.getenv("ADMIN_FULL_NAME") or input("Admin full name: ").strip()
    password = os.getenv("ADMIN_PASSWORD") or getpass.getpass("Admin password: ")

    if not email or not full_name or not password:
        print("ADMIN_EMAIL, ADMIN_FULL_NAME, va password khong duoc de trong.")
        return

    client = AsyncMongoClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]

    existing_user = await db.users.find_one({"email": email})
    if existing_user is not None:
        print(f"Admin/user voi email nay da ton tai, khong tao trung: {email}")
        await client.close()
        return

    user = {
        "full_name": full_name,
        "email": email,
        "password_hash": hash_password(password),
        "role": "admin",
        "created_at": now_utc(),
    }
    await db.users.insert_one(user)
    print(f"Da tao admin local: {email}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
