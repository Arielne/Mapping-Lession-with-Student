# CourseMatch RESTful API Specification

**Base URL (Local):** `http://localhost:8000`  
**Base URL (Production):** `https://<backend>.azurewebsites.net`  
**Auth:** Bearer JWT Token (header: `Authorization: Bearer <token>`)  
**Content-Type:** `application/json` (trừ upload endpoints dùng `multipart/form-data`)

---

## Error Format

Tất cả lỗi trả về theo format chuẩn:

```json
{
  "detail": "Error message here"
}
```

| HTTP Status | Ý nghĩa |
|-------------|---------|
| `200` | OK |
| `201` | Created |
| `400` | Bad Request (validation error) |
| `401` | Unauthorized (no token / invalid token) |
| `403` | Forbidden (wrong role) |
| `404` | Not Found |
| `422` | Unprocessable Entity (Pydantic validation) |
| `500` | Internal Server Error |

---

## 1. System APIs

### GET /

```
Method:   GET
Auth:     None
Role:     Public
```

**Response 200:**
```json
{
  "message": "CourseMatch API is running",
  "version": "1.0.0"
}
```

### GET /health

```
Method:   GET
Auth:     None
Role:     Public
```

**Response 200:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 2. Auth APIs

### POST /auth/register

```
Method:   POST
Auth:     None
Role:     Public
```

**Request Body:**
```json
{
  "full_name": "Nguyen Van A",
  "email": "student@example.com",
  "password": "SecurePassword123",
  "role": "student"
}
```

**Response 201:**
```json
{
  "id": "682e1a000000000000000001",
  "full_name": "Nguyen Van A",
  "email": "student@example.com",
  "role": "student",
  "created_at": "2026-05-27T10:00:00Z"
}
```

**Errors:**
- `400` – Email already registered
- `422` – Validation error (missing field, invalid email format)

---

### POST /auth/login

```
Method:   POST
Auth:     None
Role:     Public
```

**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "SecurePassword123"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401` – Invalid email or password

---

### GET /auth/me

```
Method:   GET
Auth:     Required (any role)
Role:     admin, student
```

**Response 200:**
```json
{
  "id": "682e1a000000000000000001",
  "full_name": "Nguyen Van A",
  "email": "student@example.com",
  "role": "student",
  "created_at": "2026-05-27T10:00:00Z"
}
```

---

## 3. Course Document APIs

### POST /course-documents/upload

```
Method:       POST
Auth:         Required
Role:         admin only
Content-Type: multipart/form-data
```

**Form Data:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | File | Yes | PDF hoặc DOCX |
| `title` | string | Yes | Tên khóa học |
| `source_note` | string | No | Ghi chú nguồn tài liệu |

**Response 201:**
```json
{
  "id": "682e1a000000000000000002",
  "title": "Python for Data Analysis",
  "original_filename": "python_data_analysis.pdf",
  "processing_status": "uploaded",
  "created_at": "2026-05-27T10:00:00Z"
}
```

**Errors:**
- `400` – Unsupported file type
- `403` – Not admin
- `413` – File too large (> 10MB)

---

### GET /course-documents

```
Method:   GET
Auth:     Required
Role:     admin, student
```

**Query Params:**

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 20 | Max results |
| `status` | string | all | Filter by processing_status |

**Response 200:**
```json
[
  {
    "id": "682e1a000000000000000002",
    "title": "Python for Data Analysis",
    "original_filename": "python_data_analysis.pdf",
    "keywords": ["Python", "Pandas", "SQL"],
    "processing_status": "processed",
    "created_at": "2026-05-27T10:00:00Z"
  }
]
```

---

### GET /course-documents/{id}

```
Method:   GET
Auth:     Required
Role:     admin, student
Path Param: id (course document ObjectId)
```

**Response 200:** Full document including `binary_vector` and `extracted_text`.

**Errors:**
- `404` – Course document not found

---

### DELETE /course-documents/{id}

```
Method:   DELETE
Auth:     Required
Role:     admin only
Path Param: id (course document ObjectId)
```

**Response 200:**
```json
{
  "message": "Course document deleted successfully"
}
```

**Errors:**
- `403` – Not admin
- `404` – Not found

---

## 4. Student Document APIs

### POST /student-documents/upload

```
Method:       POST
Auth:         Required
Role:         student only
Content-Type: multipart/form-data
```

**Form Data:**

| Field | Type | Required |
|-------|------|----------|
| `file` | File | Yes |
| `student_code` | string | No |

**Response 201:**
```json
{
  "id": "682e1a000000000000000003",
  "original_filename": "SV01_learning_need.docx",
  "processing_status": "uploaded",
  "created_at": "2026-05-27T10:20:00Z"
}
```

---

### GET /student-documents/me

```
Method:   GET
Auth:     Required
Role:     student
```

**Response 200:** Array of student documents belonging to current user.

---

### GET /student-documents/{id}

```
Method:   GET
Auth:     Required
Role:     student (owner only), admin
Path Param: id
```

**Response 200:** Full student document with `binary_vector`, `detected_keywords`.

---

## 5. Matching APIs

### POST /matching/run/{student_document_id}

```
Method:   POST
Auth:     Required
Role:     student (owner), admin
Path Param: student_document_id
```

**Behavior:**
1. Load student `binary_vector`
2. Load all `course_documents` with `processing_status = "processed"`
3. Compute Jaccard(student, course) for each course
4. Save all results to `match_results`
5. Return top-K results

**Response 200:**
```json
{
  "student_document_id": "682e1a000000000000000003",
  "total_courses_compared": 8,
  "results": [
    {
      "rank": 1,
      "course_id": "682e1a000000000000000002",
      "course_title": "Python for Data Analysis",
      "match_score": 0.67,
      "matched_keywords": ["Python", "Pandas"]
    }
  ]
}
```

**Errors:**
- `404` – Student document not found
- `400` – Student document not yet processed (status != "processed")

---

### GET /matching/results/{student_document_id}

```
Method:   GET
Auth:     Required
Role:     student (owner), admin
```

**Response 200:** Array of all match_results for this student document, sorted by rank.

---

### GET /matching/top/{student_document_id}

```
Method:   GET
Auth:     Required
Role:     student (owner), admin
Query Param: k (int, default=3)
```

**Response 200:** Top-K match results with course details.

---

## 6. Evaluation APIs

### POST /evaluation/labels

```
Method:   POST
Auth:     Required
Role:     admin or student (own document)
```

**Request Body:**
```json
{
  "student_document_id": "682e1a000000000000000003",
  "validated_course_ids": ["682e1a000000000000000002"],
  "label_source": "student_selected"
}
```

**Response 200:**
```json
{
  "message": "Labels saved successfully"
}
```

---

### GET /evaluation/metrics

```
Method:   GET
Auth:     Required
Role:     admin
```

**Response 200:**
```json
{
  "total_labeled_students": 15,
  "top1_accuracy": 0.73,
  "hit_rate_at_3": 0.87,
  "avg_processing_time_ms": 38.4
}
```

---

### GET /evaluation/report

```
Method:   GET
Auth:     Required
Role:     admin
```

**Response 200:**
```json
{
  "summary": {
    "total_labeled_students": 15,
    "top1_accuracy": 0.73,
    "hit_rate_at_3": 0.87,
    "avg_processing_time_ms": 38.4
  },
  "per_student": [
    {
      "student_document_id": "...",
      "student_code": "SV01",
      "top1_correct": true,
      "in_top3": true,
      "top1_predicted_course": "Python for Data Analysis",
      "validated_courses": ["Python for Data Analysis"]
    }
  ]
}
```
