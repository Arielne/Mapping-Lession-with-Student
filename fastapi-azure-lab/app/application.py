from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_mongo_connection, connect_to_mongo, get_database_status
from app.routers import (
    admin_course_documents,
    auth,
    courses,
    evaluation,
    learning_needs,
    matching,
    recommendations,
    registrations,
    student_documents,
    system,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.app_name,
    description="CourseMatch - He thong doi sanh tai lieu khoa hoc va nhu cau hoc vien bang PDF/DOCX, GridFS va binary Jaccard matching.",
    version="2.0.0",
    lifespan=lifespan,
)

allowed_origins = ["http://localhost:5173"]
if settings.frontend_url:
    allowed_origins.append(settings.frontend_url)
if settings.allowed_origins:
    allowed_origins.extend(
        origin.strip()
        for origin in settings.allowed_origins.split(",")
        if origin.strip()
    )
allowed_origins = list(dict.fromkeys(allowed_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(system.router)
app.include_router(auth.router)
app.include_router(admin_course_documents.router)
app.include_router(student_documents.router)
app.include_router(matching.router)
app.include_router(evaluation.router)

# Legacy form-based routes kept only for old technical tests.
app.include_router(courses.router)
app.include_router(learning_needs.router)
app.include_router(recommendations.router)
app.include_router(registrations.router)
