# MongoDB Database Schema

**Database name:** `coursematch_db`  
**Version:** 1.0

---

## 1. Database Name

```
coursematch_db
```

---

## 2. Main Collections

| Collection | Mục đích |
|------------|---------|
| `users` | Tài khoản admin và student |
| `course_documents` | Tài liệu khóa học đã upload và xử lý |
| `student_documents` | Tài liệu học viên đã upload và xử lý |
| `match_results` | Kết quả đối sánh Jaccard giữa học viên và khóa học |
| `fs.files` *(optional)* | GridFS metadata nếu lưu file gốc |
| `fs.chunks` *(optional)* | GridFS binary chunks nếu lưu file gốc |

---

## 3. Collection: `users`

### Schema

```json
{
  "_id": "ObjectId(\"682e1a000000000000000001\")",
  "full_name": "Nguyen Van A",
  "email": "student@example.com",
  "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$...",
  "role": "student",
  "created_at": "2026-05-27T10:00:00Z",
  "updated_at": "2026-05-27T10:00:00Z"
}
```

### Field Descriptions

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `_id` | ObjectId | Auto | MongoDB document ID |
| `full_name` | string | Yes | Họ tên đầy đủ |
| `email` | string | Yes | Unique, dùng để login |
| `password_hash` | string | Yes | Argon2 hash, không lưu plaintext |
| `role` | string | Yes | `"admin"` hoặc `"student"` |
| `created_at` | datetime | Auto | UTC, tạo bởi backend |
| `updated_at` | datetime | Auto | UTC, cập nhật bởi backend |

### Roles

```
admin   → Upload course docs, xem tất cả, xem evaluation
student → Upload student docs, chạy matching, xem kết quả của mình
```

---

## 4. Collection: `course_documents`

### Schema

```json
{
  "_id": "ObjectId(\"682e1a000000000000000002\")",
  "title": "Python for Data Analysis",
  "uploaded_by": "ObjectId(\"682e1a000000000000000099\")",
  "original_filename": "python_data_analysis.pdf",
  "file_type": "application/pdf",
  "file_size_bytes": 245000,
  "source_type": "real_course_document",
  "source_note": "Official syllabus provided by instructor",
  "extracted_text": "This course covers Python, Pandas, SQL and visualization...",
  "cleaned_text": "python pandas sql visualization data analysis numpy matplotlib",
  "keywords": ["Python", "Pandas", "SQL", "Data Visualization"],
  "binary_vector": {
    "Python": 1,
    "Pandas": 1,
    "SQL": 1,
    "Data Visualization": 1,
    "React": 0,
    "FastAPI": 0,
    "MongoDB": 0,
    "Machine Learning": 0,
    "Power BI": 0,
    "Excel": 0,
    "English": 0,
    "Communication": 0
  },
  "processing_status": "processed",
  "error_message": null,
  "created_at": "2026-05-27T10:00:00Z",
  "updated_at": "2026-05-27T10:05:00Z"
}
```

### Field Descriptions

| Field | Type | Notes |
|-------|------|-------|
| `title` | string | Tên khóa học |
| `uploaded_by` | ObjectId | Ref → `users._id` (phải là admin) |
| `original_filename` | string | Tên file gốc |
| `file_type` | string | MIME type |
| `file_size_bytes` | int | Kích thước file |
| `source_type` | string | `"real_course_document"` (bắt buộc với dữ liệu thật) |
| `source_note` | string | Ghi chú nguồn tài liệu |
| `extracted_text` | string | Text raw từ file |
| `cleaned_text` | string | Text sau khi làm sạch |
| `keywords` | array[string] | Danh sách từ khóa tìm thấy |
| `binary_vector` | object | Dict skill → 0/1 |
| `processing_status` | string | `uploaded` / `processing` / `processed` / `failed` |
| `error_message` | string/null | Lỗi nếu status = failed |

---

## 5. Collection: `student_documents`

### Schema

```json
{
  "_id": "ObjectId(\"682e1a000000000000000003\")",
  "user_id": "ObjectId(\"682e1a000000000000000001\")",
  "student_code": "SV01",
  "original_filename": "SV01_learning_need.docx",
  "file_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "file_size_bytes": 120000,
  "source_type": "real_student_need",
  "extracted_text": "I want to learn Python, Pandas and Data Visualization for my data analyst career.",
  "cleaned_text": "learn python pandas data visualization data analyst career",
  "detected_keywords": ["Python", "Pandas", "Data Visualization"],
  "binary_vector": {
    "Python": 1,
    "Pandas": 1,
    "SQL": 0,
    "Data Visualization": 1,
    "React": 0,
    "FastAPI": 0,
    "MongoDB": 0,
    "Machine Learning": 0,
    "Power BI": 0,
    "Excel": 0,
    "English": 0,
    "Communication": 0
  },
  "validated_course_ids": ["ObjectId(\"682e1a000000000000000002\")"],
  "label_source": "student_selected",
  "processing_status": "processed",
  "error_message": null,
  "created_at": "2026-05-27T10:20:00Z",
  "updated_at": "2026-05-27T10:25:00Z"
}
```

### Field Descriptions

| Field | Type | Notes |
|-------|------|-------|
| `user_id` | ObjectId | Ref → `users._id` (phải là student) |
| `student_code` | string | Mã học viên (SV01, SV02…) |
| `source_type` | string | `"real_student_need"` |
| `detected_keywords` | array[string] | Từ khóa phát hiện từ text |
| `binary_vector` | object | Dict skill → 0/1 |
| `validated_course_ids` | array[ObjectId] | Nhãn thật – các khóa học học viên xác nhận phù hợp |
| `label_source` | string | `"student_selected"` / `"instructor_validated"` |

---

## 6. Collection: `match_results`

### Schema

```json
{
  "_id": "ObjectId(\"682e1a000000000000000004\")",
  "student_document_id": "ObjectId(\"682e1a000000000000000003\")",
  "course_document_id": "ObjectId(\"682e1a000000000000000002\")",
  "match_score": 0.67,
  "matched_keywords": ["Python", "Pandas"],
  "student_keywords": ["Python", "Pandas", "Data Visualization"],
  "course_keywords": ["Python", "Pandas", "SQL", "Data Visualization"],
  "rank": 1,
  "algorithm": "Jaccard Binary Vector",
  "processing_time_ms": 42,
  "created_at": "2026-05-27T10:30:00Z"
}
```

### Field Descriptions

| Field | Type | Notes |
|-------|------|-------|
| `student_document_id` | ObjectId | Ref → `student_documents._id` |
| `course_document_id` | ObjectId | Ref → `course_documents._id` |
| `match_score` | float | Jaccard score [0.0 – 1.0] |
| `matched_keywords` | array[string] | Giao của hai tập từ khóa |
| `student_keywords` | array[string] | Từ khóa của học viên |
| `course_keywords` | array[string] | Từ khóa của khóa học |
| `rank` | int | Thứ hạng (1 = tốt nhất) |
| `algorithm` | string | `"Jaccard Binary Vector"` |
| `processing_time_ms` | int | Thời gian tính toán (ms) |

---

## 7. Embedding and Referencing Strategy

### Referencing (dùng cho quan hệ liên collection)

```
users._id  ←─────────────  course_documents.uploaded_by
users._id  ←─────────────  student_documents.user_id
student_documents._id  ←── match_results.student_document_id
course_documents._id   ←── match_results.course_document_id
```

**Lý do dùng referencing:**
- Tránh duplicate dữ liệu user khi nhiều documents cùng user.
- Dễ cập nhật thông tin user mà không cần update toàn bộ document.

### Embedding (dùng cho dữ liệu thuộc về document)

```
course_documents  → keywords[], binary_vector{}
student_documents → detected_keywords[], binary_vector{}, validated_course_ids[]
match_results     → matched_keywords[], student_keywords[], course_keywords[]
```

**Lý do dùng embedding:**
- Keywords và binary_vector luôn được đọc cùng với document → query 1 lần.
- Dữ liệu nhỏ, không thay đổi sau khi xử lý.
- match_results lưu snapshot từ khóa tại thời điểm matching → không bị ảnh hưởng nếu document bị xóa sau.

---

## 8. NoSQL Design Rationale

### Tại sao chọn MongoDB thay vì SQL?

| Tiêu chí | MongoDB | SQL (PostgreSQL/MySQL) |
|----------|---------|----------------------|
| Schema | Flexible (binary_vector có thể thay đổi số key) | Fixed schema, cần migration |
| Keywords array | Native array field | Junction table |
| Binary vector | Native object/dict field | JSON column hoặc nhiều row |
| File metadata | Cùng document với text đã xử lý | Tách nhiều bảng |
| Scale | Horizontal scaling dễ dàng | Vertical scaling chủ yếu |
| Document-oriented | Phù hợp với dữ liệu text/NLP | Phù hợp với dữ liệu quan hệ |

**Kết luận:** Dữ liệu của CourseMatch có cấu trúc lồng nhau (keywords[], binary_vector{}) và schema có thể thay đổi theo bộ từ khóa → MongoDB phù hợp hơn SQL.

---

## 9. Recommended Indexes

```javascript
// users
db.users.createIndex({ email: 1 }, { unique: true })

// course_documents
db.course_documents.createIndex({ uploaded_by: 1 })
db.course_documents.createIndex({ title: 1 })
db.course_documents.createIndex({ processing_status: 1 })

// student_documents
db.student_documents.createIndex({ user_id: 1 })
db.student_documents.createIndex({ student_code: 1 })
db.student_documents.createIndex({ processing_status: 1 })

// match_results
db.match_results.createIndex({ student_document_id: 1 })
db.match_results.createIndex({ course_document_id: 1 })
db.match_results.createIndex({ student_document_id: 1, rank: 1 })
```
