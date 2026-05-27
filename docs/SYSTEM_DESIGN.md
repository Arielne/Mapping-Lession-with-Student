# CourseMatch System Design

**Version:** 1.0  
**Date:** 2026-05-27

---

## 1. System Overview

CourseMatch là hệ thống web FARM Stack gồm 3 tầng chính:

```
┌─────────────────────────────────────────────────────┐
│              React SPA (Frontend)                   │
│          Azure Static Web Apps                      │
└────────────────────┬────────────────────────────────┘
                     │ HTTPS + JWT
                     ▼
┌─────────────────────────────────────────────────────┐
│            FastAPI Backend (Python)                 │
│            Azure App Service                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │   Auth   │ │  Upload  │ │ Matching │            │
│  │  Module  │ │  Module  │ │  Module  │            │
│  └──────────┘ └──────────┘ └──────────┘            │
│  ┌─────────────────────────────────────┐            │
│  │         File Processing Pipeline   │            │
│  │  Extract → Clean → Vectorize       │            │
│  └─────────────────────────────────────┘           │
└────────────────────┬────────────────────────────────┘
                     │ PyMongo Async
                     ▼
┌─────────────────────────────────────────────────────┐
│              MongoDB Atlas                          │
│   users │ course_documents │ student_documents      │
│   match_results │ (fs.files, fs.chunks optional)    │
└─────────────────────────────────────────────────────┘
```

---

## 2. End-to-End Flow

### Admin Flow

```
Admin Login
   ↓
Upload course file (PDF/DOCX)
   ↓
POST /course-documents/upload
   ↓
Backend: save metadata to MongoDB (status: "uploaded")
   ↓
Background processing:
  1. Extract text (pypdf / python-docx)
  2. Clean & normalize text
  3. Match keywords from skill dictionary
  4. Build binary_vector {skill: 0/1}
  5. Update MongoDB document (status: "processed")
   ↓
Admin sees course in GET /course-documents
```

### Student Flow

```
Student Login
   ↓
Upload CV / learning-need file (PDF/DOCX)
   ↓
POST /student-documents/upload
   ↓
Backend: save metadata to MongoDB (status: "uploaded")
   ↓
Background processing:
  1. Extract text
  2. Clean & normalize text
  3. Match keywords from skill dictionary
  4. Build binary_vector
  5. Update MongoDB document (status: "processed")
   ↓
Student runs matching:
POST /matching/run/{student_document_id}
   ↓
Backend:
  1. Load student binary_vector
  2. Load all processed course binary_vectors
  3. Compute Jaccard(student_vector, course_vector) for each course
  4. Sort by score descending
  5. Save to match_results collection
   ↓
Student views results:
GET /matching/top/{student_document_id}?k=3
```

### Evaluation Flow

```
Admin confirms labels (validated_course_ids per student_document)
   ↓
POST /evaluation/labels
   ↓
GET /evaluation/metrics
   ↓
Backend computes:
  - Top-1 Accuracy
  - Hit Rate@3
  - Avg Processing Time
   ↓
GET /evaluation/report (full report)
```

---

## 3. Core Modules

### 3.1 Frontend Module

| Component | Chức năng |
|-----------|-----------|
| `AuthContext` | Quản lý JWT token, user info toàn app |
| `axiosClient` | Axios instance với base URL từ env, auto-attach JWT |
| `ProtectedRoute` | Chặn route nếu chưa login |
| `AdminRoute` | Chặn route nếu không phải admin |
| `UploadBox` | Component drag-and-drop upload file |
| `MatchResultCard` | Hiển thị kết quả matching một khóa học |

### 3.2 Backend API Module

| Router | Endpoints | Auth |
|--------|-----------|------|
| `auth.py` | register, login, me | Public / JWT |
| `course_documents.py` | upload, list, get, delete | Admin |
| `student_documents.py` | upload, list-me, get | Student |
| `matching.py` | run, results, top | Student |
| `evaluation.py` | labels, metrics, report | Admin |

### 3.3 File Processing Module

```
app/utils/file_extractor.py
  → extract_text_from_pdf(file_bytes) → str
  → extract_text_from_docx(file_bytes) → str
  → extract_text_from_xlsx(file_bytes) → str  (optional)
  → extract_text(file_bytes, mime_type) → str  (dispatcher)
```

### 3.4 Text Processing Module

```
app/utils/text_cleaner.py
  → clean_text(raw_text) → str
    (lowercase, remove punctuation, normalize whitespace)

app/utils/keyword_extractor.py
  → SKILL_DICTIONARY = ["Python", "Pandas", "SQL", ...]
  → extract_keywords(cleaned_text) → list[str]

app/utils/vectorizer.py
  → build_binary_vector(keywords_found) → dict[str, int]
    (all keys from SKILL_DICTIONARY, value 0 or 1)
```

### 3.5 Matching Module

```
app/utils/matcher.py
  → jaccard_score(student_vector, course_vector) → float
  → rank_courses(student_vector, all_course_vectors) → list[MatchResult]
```

### 3.6 Evaluation Module

```
app/routers/evaluation.py
  → compute_top1_accuracy(labeled_data) → float
  → compute_hit_rate_at_k(labeled_data, k=3) → float
  → compute_avg_processing_time(match_results) → float
```

---

## 4. Processing Status Design

Mỗi document có `processing_status` theo state machine:

```
uploaded → processing → processed
                    ↘ failed
```

| Status | Ý nghĩa |
|--------|---------|
| `uploaded` | File đã nhận, chưa xử lý |
| `processing` | Đang trích xuất và vector hóa |
| `processed` | Hoàn thành, sẵn sàng matching |
| `failed` | Lỗi, xem `error_message` |

Matching chỉ chạy với documents có `processing_status = "processed"`.

---

## 5. Security Design

| Layer | Biện pháp |
|-------|-----------|
| Password | Hash bằng Argon2 (`pwdlib[argon2]`) |
| API Auth | JWT HS256, expire sau 60 phút |
| Role Check | FastAPI Dependency (`get_current_admin`, `get_current_student`) |
| CORS | Chỉ cho phép domain frontend đã cấu hình |
| Secrets | Tất cả trong `.env`, không push Git |
| File Validation | Kiểm tra MIME type + extension trước khi xử lý |

---

## 6. Data Integrity

- `email` field trong `users` có unique index.
- `match_results` có index trên `student_document_id` và `course_document_id`.
- Nếu processing fail, document không bị xóa – giữ lại để debug và retry.
- `created_at` và `updated_at` được ghi tự động ở backend, không do client gửi.

---

## 7. Deployment Design

| Component | Service | Config |
|-----------|---------|--------|
| Frontend | Azure Static Web Apps | Build: `npm run build`, output: `dist/` |
| Backend | Azure App Service | Python 3.11+, `uvicorn main:app` |
| Database | MongoDB Atlas M0 | Whitelist Azure IP hoặc `0.0.0.0/0` cho dev |
| Env Vars | Azure App Service → Configuration | Không dùng `.env` file trên cloud |
| Source Code | GitHub | `.env` trong `.gitignore` |
