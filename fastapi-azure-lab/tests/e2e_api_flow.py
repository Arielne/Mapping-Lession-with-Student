import asyncio
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import certifi
import fitz
from bson import ObjectId
from docx import Document
from pymongo import AsyncMongoClient

from app.config import settings
from app.security import hash_password
from app.utils import now_utc


BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8012"
RUN_ID = f"codex_e2e_{int(time.time())}_{uuid4().hex[:8]}"
PASSWORD = f"{RUN_ID}_Password1"


def request_json(method: str, path: str, payload=None, token: str | None = None, expected: tuple[int, ...] = (200,)):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            if response.status not in expected:
                raise AssertionError(f"{method} {path} returned {response.status}, expected {expected}")
            return response.status, json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        if exc.code in expected:
            body = exc.read().decode("utf-8")
            return exc.code, json.loads(body) if body else None
        raise


def request_multipart(method: str, path: str, fields: dict, file_field: str, filename: str, content_type: str, content: bytes, token: str, expected: tuple[int, ...] = (201,)):
    boundary = f"----{RUN_ID}"
    body = bytearray()
    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode())
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode())
    body.extend(content)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    request = urllib.request.Request(f"{BASE_URL}{path}", data=bytes(body), headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
            if response.status not in expected:
                raise AssertionError(f"{method} {path} returned {response.status}, expected {expected}")
            return response.status, json.loads(response_body) if response_body else None
    except urllib.error.HTTPError as exc:
        if exc.code in expected:
            response_body = exc.read().decode("utf-8")
            return exc.code, json.loads(response_body) if response_body else None
        raise


def build_docx(text: str) -> bytes:
    document = Document()
    document.add_paragraph(text)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def build_pdf(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


async def cleanup(db, user_ids: list[str], document_ids: list[str], gridfs_ids: list[str]) -> None:
    object_user_ids = [ObjectId(value) for value in user_ids if ObjectId.is_valid(value)]
    object_document_ids = [ObjectId(value) for value in document_ids if ObjectId.is_valid(value)]
    object_gridfs_ids = [ObjectId(value) for value in gridfs_ids if ObjectId.is_valid(value)]
    if object_document_ids:
        await db.match_results.delete_many({"student_document_id": {"$in": object_document_ids}})
        await db.course_documents.delete_many({"_id": {"$in": object_document_ids}})
        await db.student_documents.delete_many({"_id": {"$in": object_document_ids}})
    if object_user_ids:
        await db.users.delete_many({"_id": {"$in": object_user_ids}, "email": {"$regex": f"^{RUN_ID}"}})
    if object_gridfs_ids:
        await db.fs.files.delete_many({"_id": {"$in": object_gridfs_ids}})
        await db.fs.chunks.delete_many({"files_id": {"$in": object_gridfs_ids}})


async def main() -> None:
    if not settings.mongodb_url:
        raise AssertionError("MONGODB_URL is not configured")

    client = AsyncMongoClient(settings.mongodb_url, tls=True, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    db = client[settings.mongodb_db_name]
    user_ids: list[str] = []
    document_ids: list[str] = []
    gridfs_ids: list[str] = []

    try:
        await client.admin.command("ping")
        admin_email = f"{RUN_ID}_admin@example.test"
        admin_insert = await db.users.insert_one(
            {
                "full_name": "Codex E2E Admin",
                "email": admin_email,
                "password_hash": hash_password(PASSWORD),
                "role": "admin",
                "created_at": now_utc(),
            }
        )
        user_ids.append(str(admin_insert.inserted_id))

        student_email = f"{RUN_ID}_student@example.test"
        _, student = request_json(
            "POST",
            "/auth/register",
            {"full_name": "Codex E2E Student", "email": student_email, "password": PASSWORD},
            expected=(201,),
        )
        user_ids.append(student["id"])

        _, student_login = request_json("POST", "/auth/login", {"email": student_email, "password": PASSWORD})
        _, admin_login = request_json("POST", "/auth/login", {"email": admin_email, "password": PASSWORD})
        student_token = student_login["access_token"]
        admin_token = admin_login["access_token"]

        status_code, _ = request_json("GET", "/admin/course-documents", token=student_token, expected=(403,))
        assert status_code == 403

        status_code, _ = request_multipart(
            "POST",
            "/student/documents/upload",
            {"student_alias": RUN_ID, "document_purpose": "learning_need", "consent_confirmed": "true"},
            "file",
            "bad.txt",
            "text/plain",
            b"not allowed",
            student_token,
            expected=(400,),
        )
        assert status_code == 400

        course_pdf_text = "Python SQL dashboard analytics pandas business reporting"
        _, course_pdf = request_multipart(
            "POST",
            "/admin/course-documents/upload",
            {"course_title": f"{RUN_ID} Python Analytics PDF", "source_name": RUN_ID},
            "file",
            f"{RUN_ID} course.pdf",
            "application/pdf",
            build_pdf(course_pdf_text),
            admin_token,
        )
        document_ids.append(course_pdf["id"])
        gridfs_ids.append(course_pdf["gridfs_file_id"])
        assert course_pdf["extraction_status"] == "success"
        assert course_pdf["normalized_text"]

        course_docx_text = "React frontend component css routing"
        _, course_docx = request_multipart(
            "POST",
            "/admin/course-documents/upload",
            {"course_title": f"{RUN_ID} React DOCX", "source_name": RUN_ID},
            "file",
            f"{RUN_ID} course.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            build_docx(course_docx_text),
            admin_token,
        )
        document_ids.append(course_docx["id"])
        gridfs_ids.append(course_docx["gridfs_file_id"])
        assert course_docx["extraction_status"] == "success"
        assert course_docx["normalized_text"]

        student_text = "My CV includes Python SQL pandas dashboard analytics"
        _, student_document = request_multipart(
            "POST",
            "/student/documents/upload",
            {"student_alias": RUN_ID, "document_purpose": "anonymized_cv", "consent_confirmed": "true"},
            "file",
            f"{RUN_ID} cv.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            build_docx(student_text),
            student_token,
        )
        document_ids.append(student_document["id"])
        gridfs_ids.append(student_document["gridfs_file_id"])
        assert student_document["extraction_status"] == "success"
        assert student_document["normalized_text"]

        _, match_result = request_json(
            "POST",
            f"/matching/student-documents/{student_document['id']}?top_k=3",
            token=student_token,
        )
        results = match_result["results"]
        assert match_result["algorithm_name"] == "binary_jaccard_ngram_v1"
        assert results
        assert all(0 <= item["score"] <= 1 for item in results)
        assert [item["rank"] for item in results] == list(range(1, len(results) + 1))
        assert [item["score"] for item in results] == sorted([item["score"] for item in results], reverse=True)
        assert results[0]["course_document_id"] == course_pdf["id"]

        saved_match = await db.match_results.find_one({"student_document_id": ObjectId(student_document["id"])})
        assert saved_match is not None
        assert saved_match["algorithm_name"] == "binary_jaccard_ngram_v1"

        gridfs_count = await db.fs.files.count_documents({"_id": {"$in": [ObjectId(value) for value in gridfs_ids]}})
        assert gridfs_count == len(gridfs_ids)

        print(json.dumps({
            "run_id": RUN_ID,
            "database": settings.mongodb_db_name,
            "top_matches": [
                {
                    "rank": item["rank"],
                    "course_title": item["course_title"],
                    "course_document_id": item["course_document_id"],
                    "score": item["score"],
                    "matched_terms": item["matched_terms"],
                }
                for item in results[:3]
            ],
        }, ensure_ascii=True))
    finally:
        await cleanup(db, user_ids, document_ids, gridfs_ids)
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
