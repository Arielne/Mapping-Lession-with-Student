from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_mongo, connect_mongo, create_indexes, get_database
from app.routers import auth, course_documents, evaluation, matching, student_documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_mongo()
    await create_indexes()
    yield
    await close_mongo()


app = FastAPI(title="CourseMatch API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(course_documents.router)
app.include_router(student_documents.router)
app.include_router(matching.router)
app.include_router(evaluation.router)


@app.get("/")
async def root():
    return {"message": "CourseMatch API is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    db = get_database()
    await db.command("ping")
    return {"status": "healthy", "database": "connected"}

