from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import close_mongo_connection, connect_to_mongo, get_database_status
from app.routers import (
    admin_course_documents,
    course_documents_public,
    auth,
    courses,
    evaluation,
    favorites,
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

allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
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
app.include_router(course_documents_public.router)
app.include_router(matching.router)
app.include_router(evaluation.router)
app.include_router(favorites.router)

# Legacy form-based routes kept only for old technical tests.
app.include_router(courses.router, include_in_schema=False)
app.include_router(learning_needs.router, include_in_schema=False)
app.include_router(recommendations.router, include_in_schema=False)
app.include_router(registrations.router, include_in_schema=False)


frontend_candidates = [
    Path(__file__).resolve().parent / "frontend_dist",
    Path.cwd() / "app" / "frontend_dist",
    Path("/home/site/wwwroot/app/frontend_dist"),
    Path("/tmp/coursematch/app/frontend_dist"),
]
frontend_dist = next(
    (candidate for candidate in frontend_candidates if (candidate / "index.html").exists()),
    frontend_candidates[0],
)
frontend_assets = frontend_dist / "assets"
frontend_index = frontend_dist / "index.html"

if frontend_assets.exists():
    app.mount("/assets", StaticFiles(directory=frontend_assets), name="frontend-assets")


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    if frontend_index.exists():
        return FileResponse(frontend_index)
    return {
        "app": settings.app_name,
        "status": "Online",
        "workflow": "document_upload_binary_gridfs_matching",
    }

