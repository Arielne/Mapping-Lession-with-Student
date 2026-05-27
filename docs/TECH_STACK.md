# CourseMatch Tech Stack

**Version:** 1.0

---

## 1. Frontend

| Technology | Version | Role |
|-----------|---------|------|
| **React.js** | 18.x | UI framework, SPA |
| **Vite** | 5.x | Build tool, dev server |
| **React Router DOM** | 6.x | Client-side routing |
| **Axios** | 1.x | HTTP client, API calls |
| **Context API** | (built-in React) | Global state management (auth) |
| **CSS** | Vanilla / CSS Modules | Styling |

### Frontend Environment Variables

```env
# .env (local)
VITE_API_BASE_URL=http://127.0.0.1:8000

# Production (Azure Static Web Apps settings)
VITE_API_BASE_URL=https://<backend>.azurewebsites.net
```

### Frontend Dependencies (package.json)

```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "react-router-dom": "^6.0.0",
    "axios": "^1.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}
```

---

## 2. Backend

| Technology | Version | Role |
|-----------|---------|------|
| **FastAPI** | 0.111.x | Web framework, RESTful API |
| **Pydantic** | 2.x | Data validation, schemas |
| **PyMongo** (Async) | 4.x | MongoDB async driver |
| **PyJWT** | 2.x | JWT encode/decode |
| **pwdlib[argon2]** | 0.2.x | Password hashing (Argon2) |
| **python-multipart** | 0.0.x | File upload support |
| **python-dotenv** | 1.x | Load .env variables |
| **uvicorn** | 0.29.x | ASGI server |

### Backend Environment Variables

```env
# backend/.env.example
MONGODB_URL=mongodb+srv://username:password@cluster-url/coursematch_db
MONGODB_DB_NAME=coursematch_db
JWT_SECRET_KEY=replace_with_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:5173
```

### Backend Dependencies (requirements.txt)

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
pydantic==2.7.0
pydantic-settings==2.2.0
pymongo[srv]==4.7.0
motor==3.4.0
PyJWT==2.8.0
pwdlib[argon2]==0.2.0
python-multipart==0.0.9
python-dotenv==1.0.1
pypdf==4.2.0
python-docx==1.1.2
openpyxl==3.1.2
```

> **Note:** `motor` là async driver của PyMongo, được dùng với `asyncio`.

---

## 3. File Processing

| Library | Format | Usage |
|---------|--------|-------|
| **pypdf** (hoặc **PyMuPDF**) | PDF | Extract text từ PDF |
| **python-docx** | DOCX | Extract text từ Word document |
| **openpyxl** | XLSX | Extract text/data từ Excel (tùy chọn) |

### Ví dụ sử dụng

```python
# PDF với pypdf
from pypdf import PdfReader
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


# DOCX với python-docx
from docx import Document
import io

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])


# XLSX với openpyxl (tùy chọn)
import openpyxl
import io

def extract_text_from_xlsx(file_bytes: bytes) -> str:
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes))
    text_parts = []
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(values_only=True):
            text_parts.extend([str(cell) for cell in row if cell])
    return " ".join(text_parts)
```

---

## 4. Database

| Technology | Role |
|-----------|------|
| **MongoDB** (local) | Development database |
| **MongoDB Atlas** (M0 Free Tier) | Production database |
| **MongoDB Documents** | Primary data storage format |
| **GridFS** *(optional)* | Binary file storage nếu cần lưu file gốc |

**Database name:** `coursematch_db`

**Collections:**
- `users`
- `course_documents`
- `student_documents`
- `match_results`
- `fs.files`, `fs.chunks` *(GridFS, optional)*

---

## 5. Deployment

| Component | Service | Notes |
|-----------|---------|-------|
| **Frontend** | Azure Static Web Apps | Free tier, CI/CD từ GitHub |
| **Backend** | Azure App Service | Python 3.11, B1 tier |
| **Database** | MongoDB Atlas M0 | Free cluster, shared |
| **Source Code** | GitHub | `.env` trong `.gitignore` |

---

## 6. Development Tools

| Tool | Purpose |
|------|---------|
| VS Code | IDE |
| Postman / Thunder Client | API testing |
| MongoDB Compass | DB GUI |
| Git + GitHub | Version control |
| Azure Portal | Cloud management |
| Node.js 18+ | Frontend build |
| Python 3.11+ | Backend runtime |

---

## 7. Not Allowed

> Các công nghệ sau **không được phép** dùng trong đồ án:

| Không được dùng | Lý do |
|----------------|-------|
| Redux / Zustand | Context API đã đủ, không cần thêm |
| Next.js / Nuxt | Phải dùng React SPA + Vite |
| Express.js / Node backend | Backend phải là FastAPI Python |
| SQL databases (MySQL, PostgreSQL) | Database phải là MongoDB |
| SQLAlchemy / Django ORM | Backend phải dùng PyMongo |
| scikit-learn / TensorFlow | Thuật toán chỉ dùng Jaccard Similarity |
| OpenAI API / LLM embedding | Không dùng AI external API |
| Fake/generated data cho evaluation | Evaluation phải dùng dữ liệu thật |
| Subprocess để đọc file | Dùng Python libraries (pypdf, python-docx) |
| Hard-coded URLs | Dùng biến môi trường |
| Plaintext passwords | Phải dùng Argon2 hash |
