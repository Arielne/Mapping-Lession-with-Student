from __future__ import annotations

from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


def extract_text(filename: str, content: bytes) -> tuple[str, str | None]:
    extension = Path(filename).suffix.lower()
    try:
        if extension == ".pdf":
            return extract_pdf_text(content), None
        if extension == ".docx":
            return extract_docx_text(content), None
        return "", "Unsupported file type."
    except Exception as exc:
        return "", str(exc)


def extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    page_texts = []
    for page in reader.pages:
        page_texts.append(page.extract_text() or "")
    return "\n".join(page_texts).strip()


def extract_docx_text(content: bytes) -> str:
    document = Document(BytesIO(content))
    parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text]

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text:
                    parts.append(cell.text)

    return "\n".join(parts).strip()
