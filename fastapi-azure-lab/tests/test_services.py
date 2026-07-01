from io import BytesIO

import pytest
from docx import Document
from fastapi import HTTPException

from app.dependencies import get_current_user
from app.services.file_validation_service import validate_upload
from app.services.matching_service import ALGORITHM_NAME, compute_binary_jaccard_ngram_matches
from app.services.text_extraction_service import extract_text


class DummyUploadFile:
    def __init__(self, filename: str, content_type: str):
        self.filename = filename
        self.content_type = content_type


def test_binary_jaccard_uses_binary_unigram_and_bigram_features():
    courses = [
        {
            "_id": "course-python-sql",
            "course_title": "Python SQL Analytics",
            "normalized_text": "python sql dashboard",
        },
        {
            "_id": "course-react",
            "course_title": "React Frontend",
            "normalized_text": "react css component",
        },
    ]

    result = compute_binary_jaccard_ngram_matches("python python sql", courses, top_k=2)

    assert result["algorithm_name"] == ALGORITHM_NAME
    assert result["results"][0]["course_document_id"] == "course-python-sql"
    assert result["results"][0]["score"] == pytest.approx(1 / 3)
    assert all(0 <= item["score"] <= 1 for item in result["results"])
    assert [item["rank"] for item in result["results"]] == [1, 2]
    assert result["results"][0]["score"] >= result["results"][1]["score"]
    assert result["vocabulary_size"] > 3


def test_upload_validation_rejects_empty_and_spoofed_files():
    pdf = DummyUploadFile("cv.pdf", "application/pdf")
    with pytest.raises(HTTPException):
        validate_upload(pdf, b"")

    spoofed_pdf = DummyUploadFile("cv.pdf", "application/pdf")
    with pytest.raises(HTTPException):
        validate_upload(spoofed_pdf, b"not a real pdf")

    txt = DummyUploadFile("cv.txt", "text/plain")
    with pytest.raises(HTTPException):
        validate_upload(txt, b"plain text")


def test_docx_extraction_uses_document_paragraph_text():
    document = Document()
    document.add_paragraph("Python SQL dashboard")
    buffer = BytesIO()
    document.save(buffer)

    extracted_text, extraction_error = extract_text("course.docx", buffer.getvalue())

    assert extraction_error is None
    assert "Python SQL dashboard" in extracted_text


def test_missing_bearer_token_returns_401():
    with pytest.raises(HTTPException) as exc_info:
        import asyncio

        asyncio.run(get_current_user(credentials=None, db=None))

    assert exc_info.value.status_code == 401
