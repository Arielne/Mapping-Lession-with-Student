from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

import docx2txt
import fitz

try:
    from docx import Document
except ImportError:  # pragma: no cover - optional fallback
    Document = None

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - optional fallback
    PdfReader = None


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
    try:
        with fitz.open(stream=content, filetype="pdf") as document:
            return "\n".join(page.get_text("text") for page in document).strip()
    except Exception:
        if PdfReader is None:
            raise
        reader = PdfReader(BytesIO(content))
        page_texts = []
        for page in reader.pages:
            page_texts.append(page.extract_text() or "")
        return "\n".join(page_texts).strip()


def extract_docx_text(content: bytes) -> str:
    try:
        with NamedTemporaryFile(suffix=".docx", delete=True) as temp_file:
            temp_file.write(content)
            temp_file.flush()
            return (docx2txt.process(temp_file.name) or "").strip()
    except Exception:
        if Document is None:
            raise

    document = Document(BytesIO(content))
    parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text]

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text:
                    parts.append(cell.text)

    return "\n".join(parts).strip()
