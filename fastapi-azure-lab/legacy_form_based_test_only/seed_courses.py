import asyncio

from dotenv import load_dotenv
from pymongo import AsyncMongoClient

from app.config import settings
from app.utils import now_utc

load_dotenv()

SAMPLE_COURSES = [
    {
        "title": "Python Basic",
        "category": "Programming",
        "level": "Beginner",
        "skills": ["Python", "Variables", "Functions"],
        "description": "Nhap mon Python cho nguoi moi bat dau.",
        "duration_weeks": 4,
    },
    {
        "title": "Python for Data Analysis",
        "category": "Data",
        "level": "Intermediate",
        "skills": ["Python", "Pandas", "Numpy"],
        "description": "Phan tich du lieu voi Python, Pandas va Numpy.",
        "duration_weeks": 6,
    },
    {
        "title": "Web Development with React",
        "category": "Web",
        "level": "Beginner",
        "skills": ["React", "JavaScript", "HTML", "CSS"],
        "description": "Xay dung giao dien web hien dai voi React.",
        "duration_weeks": 6,
    },
    {
        "title": "FastAPI Backend Development",
        "category": "Backend",
        "level": "Intermediate",
        "skills": ["FastAPI", "Python", "REST API", "MongoDB"],
        "description": "Xay dung backend API bat dong bo voi FastAPI.",
        "duration_weeks": 5,
    },
    {
        "title": "SQL Fundamentals",
        "category": "Database",
        "level": "Beginner",
        "skills": ["SQL", "Database", "Query"],
        "description": "Kien thuc nen tang ve co so du lieu quan he va SQL.",
        "duration_weeks": 4,
    },
    {
        "title": "Data Visualization Basics",
        "category": "Data",
        "level": "Beginner",
        "skills": ["Visualization", "Charts", "Python", "Matplotlib"],
        "description": "Trinh bay du lieu bang bieu do va dashboard co ban.",
        "duration_weeks": 4,
    },
]


async def main() -> None:
    if not settings.mongodb_url:
        print("MONGODB_URL chua duoc cau hinh. Khong the seed du lieu.")
        return

    client = AsyncMongoClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    now = now_utc()

    for course in SAMPLE_COURSES:
        document = {
            **course,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        await db.courses.update_one(
            {"title": document["title"]},
            {"$set": document},
            upsert=True,
        )

    await client.close()
    print(f"Da seed {len(SAMPLE_COURSES)} khoa hoc mau.")


if __name__ == "__main__":
    asyncio.run(main())
