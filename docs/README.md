# CourseMatch Documentation Pack

## Tên Project

**CourseMatch – Hệ thống đối sánh khóa học với nhu cầu học viên từ tài liệu thật**

---

## Mục Tiêu

CourseMatch là hệ thống web (FARM Stack) cho phép học viên upload CV hoặc tài liệu mô tả nhu cầu học tập thật (PDF/DOCX), sau đó hệ thống tự động trích xuất nội dung, tạo vector nhị phân 0/1 theo bộ từ khóa/kỹ năng, và dùng thuật toán **Jaccard Similarity** để đối sánh với các khóa học mà admin đã upload từ tài liệu thật. Kết quả trả về danh sách khóa học được xếp hạng phù hợp nhất.

---

## Tech Stack – FARM Stack

| Layer      | Technology                              |
|------------|------------------------------------------|
| Frontend   | React.js (Vite + React Router + Axios)   |
| Backend    | FastAPI (Python)                         |
| Database   | MongoDB / MongoDB Atlas                  |
| Deployment | Azure Student (App Service + Static Web) |

---

## Document Index

| File | Purpose |
|------|---------|
| `README.md` | Tổng quan project, document index, workflow tóm tắt |
| `PRD.md` | Product Requirements Document – yêu cầu nghiệp vụ đầy đủ |
| `SYSTEM_DESIGN.md` | Thiết kế hệ thống, modules, luồng xử lý, bảo mật |
| `ARCHITECTURE.md` | Kiến trúc FARM Stack, sơ đồ tầng, CORS, Auth |
| `DATABASE_SCHEMA.md` | MongoDB schema đầy đủ cho tất cả collections |
| `API_SPEC.md` | RESTful API specification – method, endpoint, request, response |
| `WORKFLOW.md` | Workflow chi tiết: admin, student, matching, evaluation |
| `ALGORITHM.md` | Thuật toán Binary Vector + Jaccard Similarity |
| `EPICS_AND_STORIES.md` | Epics và User Stories theo chuẩn Agile |
| `STRICT_RULES.md` | Quy tắc bắt buộc – không được vi phạm |
| `TECH_STACK.md` | Danh sách thư viện, công cụ, phiên bản |
| `DEPLOYMENT.md` | Hướng dẫn deploy Azure + MongoDB Atlas |
| `REPORT_NOTES.md` | Ghi chú viết báo cáo, checklist nộp bài |

---

## Final Confirmed Workflow

```
Real course documents (PDF/DOCX/XLSX)    Real student CV / learning-need (PDF/DOCX)
         ↓                                             ↓
   Admin Upload                                  Student Upload
         ↓                                             ↓
   Backend Python reads file              Backend Python reads file
         ↓                                             ↓
   Extract raw text                        Extract raw text
         ↓                                             ↓
   Clean & normalize text                  Clean & normalize text
         ↓                                             ↓
   Convert to Dictionary/JSON             Convert to Dictionary/JSON
         ↓                                             ↓
   Store as MongoDB Document              Store as MongoDB Document
         ↓                                             ↓
   Create binary keyword vector           Create binary keyword vector
         ↓                                             ↓
                 ↓ Run Jaccard Similarity Matching ↓
                         ↓
              Return ranked course recommendations
                         ↓
         Evaluate algorithm with real validated labels
```

---

## Quy Tắc Quan Trọng

> ⚠️ **REAL DATA ONLY cho đánh giá thuật toán.**
> Seed/demo data chỉ được dùng để test kỹ thuật, tuyệt đối không đưa vào báo cáo kết quả thuật toán.

> ⚠️ **"Nhị phân" là vector 0/1 theo kỹ năng/từ khóa**, không phải so sánh bytes của file PDF/Word.

> ⚠️ **Không push `.env` lên GitHub. Không lưu plaintext password.**

---

## Cách Dùng Bộ Tài Liệu Này

1. Clone repo về máy.
2. Đọc `STRICT_RULES.md` trước tiên – đây là quy tắc bắt buộc.
3. Đọc `PRD.md` để hiểu yêu cầu nghiệp vụ.
4. Đọc `ARCHITECTURE.md` + `SYSTEM_DESIGN.md` để nắm cấu trúc hệ thống.
5. Dùng `DATABASE_SCHEMA.md` khi thiết kế MongoDB collections.
6. Dùng `API_SPEC.md` khi viết FastAPI routers.
7. Dùng `ALGORITHM.md` khi implement matching module.
8. Dùng `DEPLOYMENT.md` khi deploy lên Azure.
9. Dùng `REPORT_NOTES.md` khi viết báo cáo đồ án.

---

*CourseMatch – Đồ án môn Lập trình tổ chức lưu trữ và xử lý dữ liệu*
