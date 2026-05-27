# CourseMatch Backend

CourseMatch - Mapping Khoa Hoc voi Nhu Cau Hoc Vien.

## Kien truc

- FastAPI + Pydantic
- MongoDB local voi PyMongo Async API
- GridFS luu file PDF/DOCX goc dang binary
- MongoDB Document luu JSON da trich xuat: `extracted_text`, `normalized_text`, metadata va trang thai extraction
- JWT authentication voi role `admin` va `student`
- Matching baseline: binary vector 0/1 tu `CountVectorizer`, `ngram_range=(1, 2)`, Jaccard similarity

## Database

Database local chinh thuc cho kien truc tai lieu:

```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=coursematch_document_db
```

Collections nghiep vu du kien:

- `users`
- `course_documents`
- `student_documents`
- `match_results`
- GridFS: `fs.files`, `fs.chunks`

Database cu `coursematch_db` chi la du lieu technical test, khong dung cho bao cao ket qua chinh thuc.

## Data Policy

- Du lieu danh gia chinh thuc phai la file PDF/DOCX that.
- Khong seed du lieu khoa hoc/hoc vien gia cho database `coursematch_document_db`.
- Khong luu thong tin ca nhan nhay cam khong can thiet.
- Student phai xac nhan file duoc phep su dung va da an thong tin nhay cam neu can.
- `ground_truth_course_id` chi dung de tinh evaluation sau khi matching, khong tham gia vector hoa, scoring hoac xep hang.
- File goc duoc luu GridFS. Soft delete document khong tu xoa file GridFS trong ban dau de giu lich su du lieu that.

## API chinh

- Auth: `/auth/register`, `/auth/login`, `/auth/me`
- System: `/`, `/health`, `/docs`
- Admin Course Documents: `/admin/course-documents/*`
- Student Documents: `/student/documents/*`
- Matching: `/matching/student-documents/{student_document_id}`
- Evaluation: `/admin/evaluation/summary`

Các route cũ `/courses`, `/learning-needs`, `/recommendations`, `/registrations` vẫn được giữ dưới tag Swagger `Legacy - Technical Test Only`; không dùng cho dữ liệu thật hoặc đánh giá thuật toán.

## Chay local

```powershell
cd d:\demo\fastapi-azure-lab
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Kiem tra ky thuat

```powershell
.\.venv\Scripts\python.exe -c "from main import app; print(app.title)"
.\.venv\Scripts\python.exe -m compileall main.py app
```

Không chạy `seed_courses.py` cho database mới.

## Buoc tiep theo

1. User cung cap it nhat 2 tai lieu khoa hoc that PDF/DOCX.
2. User cung cap it nhat 1 file nhu cau/CV that da an thong tin nhay cam.
3. Upload local, chay matching va gan ground truth.
4. Kiem tra evaluation.
5. Sau do moi tao/ket noi MongoDB Atlas.
6. Sau do moi deploy Azure.

Hien tai chi chay local, chua deploy Azure va chua ket noi MongoDB Atlas.
