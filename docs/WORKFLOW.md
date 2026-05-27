# CourseMatch Optimized Workflow

**Version:** 1.0  
**Date:** 2026-05-27

---

## 1. Final Confirmed Workflow

```
Real course documents (PDF/DOCX/XLSX)       Real student CV / learning-need (PDF/DOCX)
       ↓                                              ↓
  Admin Upload                                   Student Upload
  POST /course-documents/upload                  POST /student-documents/upload
       ↓                                              ↓
  Backend nhận file (bytes)                     Backend nhận file (bytes)
       ↓                                              ↓
  Detect MIME type                              Detect MIME type
       ↓                                              ↓
  Extract raw text                              Extract raw text
  (pypdf / python-docx / openpyxl)             (pypdf / python-docx)
       ↓                                              ↓
  Clean & normalize text                        Clean & normalize text
  (lowercase, remove punctuation)              (lowercase, remove punctuation)
       ↓                                              ↓
  Match against SKILL_DICTIONARY               Match against SKILL_DICTIONARY
       ↓                                              ↓
  Build binary_vector {skill: 0/1}             Build binary_vector {skill: 0/1}
       ↓                                              ↓
  Save to MongoDB (course_documents)           Save to MongoDB (student_documents)
  processing_status = "processed"              processing_status = "processed"
       ↓                                              ↓
  ─────────────────────────────────────────────────────────────────
                         ↓ MATCHING ↓
  Student triggers: POST /matching/run/{student_document_id}
                         ↓
  Load student binary_vector from MongoDB
                         ↓
  Load all processed course binary_vectors from MongoDB
                         ↓
  For each course: compute Jaccard(student_vector, course_vector)
                         ↓
  Sort courses by Jaccard score descending → assign rank
                         ↓
  Save all match_results to MongoDB
                         ↓
  Return top-K ranked recommendations to frontend
  ─────────────────────────────────────────────────────────────────
                         ↓ EVALUATION ↓
  Student/Admin confirms labels (validated_course_ids)
                         ↓
  Admin runs: GET /evaluation/metrics
                         ↓
  Compute Top-1 Accuracy, Hit Rate@3, Avg Processing Time
                         ↓
  Present evaluation results with real validated data
```

---

## 2. Admin Workflow

### Step-by-Step

```
1. Admin đăng nhập
   POST /auth/login → nhận JWT token

2. Admin upload tài liệu khóa học thật
   POST /course-documents/upload
   Form data: file (PDF/DOCX), title, source_note

3. Backend xử lý (background/sync):
   a. Lưu metadata vào course_documents (status: uploaded)
   b. Đọc file bytes
   c. Gọi file_extractor.extract_text(file_bytes, mime_type)
   d. Gọi text_cleaner.clean_text(raw_text)
   e. Gọi keyword_extractor.extract_keywords(cleaned_text)
   f. Gọi vectorizer.build_binary_vector(keywords_found)
   g. Cập nhật document trong MongoDB (status: processed)

4. Admin xem danh sách khóa học
   GET /course-documents

5. Admin xem chi tiết một khóa học (để kiểm tra vector)
   GET /course-documents/{id}

6. Admin xóa khóa học nếu cần
   DELETE /course-documents/{id}

7. Admin xem kết quả evaluation
   GET /evaluation/metrics
   GET /evaluation/report
```

### Điều kiện bắt buộc cho Admin

- File phải là PDF hoặc DOCX thật từ tài liệu khóa học.
- `source_note` phải ghi rõ nguồn (tên trường, tên khóa học, nguồn tài liệu).
- Không upload file demo/giả để đo thuật toán.

---

## 3. Student Workflow

### Step-by-Step

```
1. Student đăng ký tài khoản
   POST /auth/register {role: "student"}

2. Student đăng nhập
   POST /auth/login → nhận JWT token

3. Student xem danh sách khóa học có sẵn (tùy chọn)
   GET /course-documents

4. Student upload CV / tài liệu mô tả nhu cầu học tập thật
   POST /student-documents/upload
   Form data: file (PDF/DOCX), student_code

5. Backend xử lý (tương tự admin):
   a. Extract text
   b. Clean text
   c. Extract keywords
   d. Build binary_vector
   e. Update status: processed

6. Student chạy matching
   POST /matching/run/{student_document_id}

7. Student xem top-3 khóa học phù hợp nhất
   GET /matching/top/{student_document_id}?k=3

8. Student xác nhận nhãn (khóa học nào thực sự phù hợp)
   POST /evaluation/labels
   {validated_course_ids: [...], label_source: "student_selected"}
```

---

## 4. Matching Workflow

### Chi tiết thuật toán

```
Input:
  student_vector = {Python: 1, Pandas: 1, SQL: 0, React: 0, ...}
  courses = [
    {id: "c1", title: "Python for DA", vector: {Python:1, Pandas:1, SQL:1, ...}},
    {id: "c2", title: "Web Dev", vector: {React:1, FastAPI:1, MongoDB:1, ...}},
    ...
  ]

Processing:
  For each course c in courses:
    student_active = {k for k,v in student_vector.items() if v == 1}
    course_active  = {k for k,v in c.vector.items() if v == 1}
    intersection   = student_active ∩ course_active
    union          = student_active ∪ course_active
    score          = len(intersection) / len(union)  if union else 0

  results = sort(courses, key=score, descending=True)
  assign rank = 1, 2, 3...

Output:
  match_results saved to MongoDB
  top-K returned to frontend
```

### Performance Notes

- Matching N khóa học với 1 student document: O(N × K) với K = số key trong vector.
- Với N ≤ 100 khóa học, thời gian < 50ms.
- Nếu N lớn hơn, có thể index theo bitmask để tối ưu.

---

## 5. Evaluation Workflow

```
Điều kiện: student_documents có validated_course_ids được xác nhận

1. Thu thập dữ liệu có nhãn:
   labeled_data = [
     {student_doc_id, validated_course_ids, top1_predicted, top3_predicted}
   ]

2. Tính Top-1 Accuracy:
   correct_top1 = count(students where top1_predicted in validated_course_ids)
   top1_accuracy = correct_top1 / total_labeled_students

3. Tính Hit Rate@3:
   hit_at_3 = count(students where any of top3_predicted in validated_course_ids)
   hit_rate_at_3 = hit_at_3 / total_labeled_students

4. Tính Avg Processing Time:
   avg_ms = mean(match_results.processing_time_ms)

5. Export report:
   GET /evaluation/report → JSON với per-student breakdown
```

---

## 6. Data Collection Workflow

### Thu thập tài liệu khóa học thật

```
Nguồn hợp lệ:
- Syllabus chính thức từ giảng viên
- Đề cương môn học từ nhà trường
- Tài liệu giới thiệu khóa học thật (PDF từ website chính thức)
- Brochure khóa học từ tổ chức đào tạo

Quy trình:
1. Thu thập file PDF/DOCX từ nguồn chính thức
2. Ghi chú nguồn vào source_note khi upload
3. Lưu file gốc để kiểm chứng nếu cần
```

### Thu thập tài liệu học viên thật

```
Nguồn hợp lệ:
- CV thật của học viên (ẩn danh nếu cần)
- Tài liệu học viên tự viết mô tả nhu cầu học tập
- Form khảo sát nhu cầu học tập (export ra DOCX)

Quy trình:
1. Học viên cung cấp file
2. Ẩn danh hóa nếu cần (xóa thông tin cá nhân nhạy cảm)
3. Học viên xác nhận nhãn sau khi thấy kết quả matching
```

---

## 7. Privacy Workflow

```
Đối với CV học viên thật:
  - Chỉ lưu extracted_text, cleaned_text, keywords, binary_vector vào MongoDB
  - File gốc có thể ẩn danh hóa trước khi upload
  - Không chia sẻ dữ liệu học viên giữa các tài khoản khác nhau
  - Student chỉ xem được documents của chính mình

Đối với tài liệu khóa học:
  - Course documents có thể public (tất cả users xem được)
  - Ghi rõ source_note để truy xuất nguồn gốc
```

---

## 8. Local to Cloud Workflow

```
Development (Local):
  Frontend: http://localhost:5173
  Backend:  http://localhost:8000
  Database: MongoDB local OR MongoDB Atlas
  .env: VITE_API_BASE_URL=http://localhost:8000

Testing (Staging):
  Backend:  Azure App Service (test slot)
  Database: MongoDB Atlas
  Frontend: Localhost với VITE_API_BASE_URL trỏ vào Azure backend

Production (Live):
  Frontend: Azure Static Web Apps → VITE_API_BASE_URL=https://<app>.azurewebsites.net
  Backend:  Azure App Service     → MONGODB_URL=mongodb+srv://...atlas...
  Database: MongoDB Atlas M0+

Deploy Order:
  1. MongoDB Atlas: tạo cluster, lấy connection string
  2. Backend: deploy lên Azure App Service, set env vars
  3. Frontend: deploy lên Azure Static Web Apps, set VITE_API_BASE_URL
  4. Update CORS: set FRONTEND_URL trong backend env vars
  5. Kiểm tra end-to-end: login → upload → matching → evaluation
```
