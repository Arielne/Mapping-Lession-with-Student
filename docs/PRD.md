# Product Requirements Document (PRD)

**Project:** CourseMatch  
**Version:** 1.0  
**Date:** 2026-05-27  
**Status:** Confirmed

---

## 1. Product Name

**CourseMatch – Hệ thống đối sánh khóa học với nhu cầu học viên từ tài liệu thật**

---

## 2. Product Vision

Xây dựng một hệ thống web FARM Stack cho phép học viên upload tài liệu mô tả nhu cầu học tập thật (CV, đề cương mong muốn) và nhận được gợi ý khóa học phù hợp nhất dựa trên thuật toán Jaccard Similarity với vector nhị phân 0/1 – được tính từ tài liệu khóa học thật do admin upload.

---

## 3. Problem Statement

Học viên thường khó tìm được khóa học phù hợp với nhu cầu và kỹ năng hiện tại của mình vì:

- Mô tả khóa học thường mang tính marketing, không phản ánh đúng nội dung.
- Học viên không biết so sánh kỹ năng mình cần vs kỹ năng khóa học dạy.
- Không có công cụ tự động đối sánh dựa trên tài liệu thật.

CourseMatch giải quyết vấn đề này bằng cách trích xuất nội dung từ tài liệu thật và đối sánh bằng thuật toán có thể đo lường được.

---

## 4. Target Users

| User | Mô Tả |
|------|-------|
| **Admin** | Người quản trị, upload tài liệu khóa học thật (syllabus, đề cương, PDF mô tả khóa học) |
| **Student** | Học viên, upload CV hoặc tài liệu mô tả nhu cầu học tập, xem kết quả matching |

---

## 5. Goals

- G-01: Hệ thống xử lý được file PDF/DOCX thật và trích xuất text chính xác.
- G-02: Tạo binary vector 0/1 từ bộ từ khóa/kỹ năng đã định nghĩa.
- G-03: Tính Jaccard Similarity và xếp hạng khóa học phù hợp.
- G-04: Lưu toàn bộ dữ liệu vào MongoDB Atlas dưới dạng structured document.
- G-05: Cung cấp RESTful API qua FastAPI với Swagger /docs.
- G-06: React SPA hiển thị kết quả matching trực quan.
- G-07: Đánh giá thuật toán bằng dữ liệu thật có nhãn xác nhận.
- G-08: Deploy thành công lên Azure.

---

## 6. Non-Goals

- Không xây dựng hệ thống recommendation dựa trên machine learning (chỉ dùng Jaccard).
- Không xây dựng chức năng thanh toán hay đăng ký khóa học.
- Không hỗ trợ real-time chat hay notification.
- Không xây dựng hệ thống quản lý khóa học đầy đủ (LMS).
- Không crawl dữ liệu từ internet – chỉ dùng file do người dùng upload.

---

## 7. Functional Requirements

### FR-01 – Authentication

- Hệ thống cho phép đăng ký tài khoản mới (`/auth/register`).
- Hệ thống cho phép đăng nhập và nhận JWT token (`/auth/login`).
- Hệ thống cho phép xem thông tin tài khoản hiện tại (`/auth/me`).
- JWT token có thời hạn cấu hình qua biến môi trường.

### FR-02 – Role-Based Access

- Role `admin`: upload course document, xem tất cả documents, xóa course document, xem evaluation.
- Role `student`: upload student document, xem document của mình, chạy matching, xem kết quả.
- Endpoint phải kiểm tra role trước khi xử lý.

### FR-03 – Course Document Upload (Admin)

- Admin upload file PDF/DOCX mô tả khóa học thật.
- File phải đúng format (PDF hoặc DOCX).
- File phải có tiêu đề khóa học (`title`).
- Hệ thống tạo record trong `course_documents` với `processing_status = "uploaded"`.
- Xử lý không đồng bộ: trích xuất → làm sạch → vector hóa → cập nhật `processing_status`.

### FR-04 – Student Document Upload (Student)

- Student upload file PDF/DOCX (CV hoặc mô tả nhu cầu học tập thật).
- Hệ thống tạo record trong `student_documents` với `processing_status = "uploaded"`.
- Xử lý không đồng bộ: trích xuất → làm sạch → vector hóa → cập nhật `processing_status`.

### FR-05 – Text Extraction

- PDF: dùng `pypdf` hoặc `PyMuPDF`.
- DOCX: dùng `python-docx`.
- XLSX: dùng `openpyxl` (nếu cần).
- Nếu trích xuất thất bại: `processing_status = "failed"`, `error_message` lưu chi tiết lỗi.

### FR-06 – Data Normalization

- Chuyển text về lowercase.
- Loại bỏ ký tự đặc biệt, dấu câu không cần thiết.
- Loại bỏ stop words (tùy chọn).
- Kết quả lưu vào `cleaned_text`.

### FR-07 – Binary Vectorization

- Hệ thống duy trì bộ từ khóa/kỹ năng toàn cục (skill dictionary).
- Với mỗi document, tạo `binary_vector`: `1` nếu từ khóa xuất hiện, `0` nếu không.
- Lưu `keywords` (danh sách từ khóa xuất hiện) và `binary_vector` vào MongoDB.

### FR-08 – Matching

- Student chạy matching trên một `student_document_id` cụ thể.
- Hệ thống tính Jaccard Similarity với tất cả `course_documents` có `processing_status = "processed"`.
- Lưu kết quả vào `match_results` với `rank`, `match_score`, `matched_keywords`.

### FR-09 – Recommendation Result

- API trả về top-K khóa học phù hợp nhất (mặc định K=3).
- Kết quả được xếp hạng theo `match_score` giảm dần.
- Frontend hiển thị danh sách kết quả với tên khóa học và điểm matching.

### FR-10 – Algorithm Evaluation

- Admin có thể xem metrics đánh giá thuật toán.
- Metrics bao gồm: Top-1 Accuracy, Hit Rate@3, Average Processing Time.
- Evaluation chỉ tính trên dữ liệu có `validated_course_ids` (nhãn thật).

---

## 8. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | API response time < 2 giây cho matching thông thường |
| NFR-02 | Hỗ trợ file upload tối đa 10MB |
| NFR-03 | JWT token expire sau 60 phút (cấu hình được) |
| NFR-04 | Password hash dùng Argon2 |
| NFR-05 | CORS chỉ cho phép domain frontend đã cấu hình |
| NFR-06 | MongoDB Atlas free tier tối thiểu (M0) |
| NFR-07 | Frontend responsive (desktop + mobile cơ bản) |
| NFR-08 | Swagger /docs truy cập được ở cả local và production |

---

## 9. Definition of Done

Đồ án được coi là hoàn thành khi **tất cả** các mục sau đều đạt:

- [ ] React SPA chạy được ở local (`http://localhost:5173`)
- [ ] React SPA deploy thành công lên Azure Static Web Apps
- [ ] FastAPI backend chạy được ở local (`http://localhost:8000`)
- [ ] FastAPI backend deploy thành công lên Azure App Service
- [ ] MongoDB Atlas có dữ liệu thật trong các collections
- [ ] Swagger `/docs` truy cập được và hiển thị đúng API
- [ ] JWT authentication hoạt động (register, login, protected route)
- [ ] Admin upload được file khóa học thật (PDF/DOCX)
- [ ] Student upload được CV/file nhu cầu thật (PDF/DOCX)
- [ ] PDF/DOCX extraction hoạt động đúng
- [ ] Binary vector 0/1 được tạo từ bộ từ khóa/kỹ năng
- [ ] Jaccard matching chạy được và trả về kết quả xếp hạng
- [ ] Evaluation metrics được tính từ dữ liệu thật có nhãn
- [ ] Báo cáo có screenshot và số liệu từ dữ liệu thật
