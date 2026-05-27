# CourseMatch Strict Rules

> Tài liệu này liệt kê toàn bộ quy tắc bắt buộc của đồ án CourseMatch.
> **Vi phạm bất kỳ quy tắc nào dưới đây có thể dẫn đến sai kết quả hoặc điểm trừ.**

---

## SR-01 – Real Data Only for Algorithm Evaluation

- Kết quả thuật toán **phải** được đo trên dữ liệu thật: tài liệu khóa học thật và CV/nhu cầu học viên thật.
- Tuyệt đối không dùng dữ liệu tự chế (fake/generated) để tính Top-1 Accuracy, Hit Rate@3, hay bất kỳ metric nào trong báo cáo.

---

## SR-02 – Demo Data Can Only Be Used for Technical Testing

- Seed/demo data chỉ được phép dùng để kiểm tra kỹ thuật (unit test, kiểm tra API, kiểm tra DB connection).
- Demo data **không được** xuất hiện trong phần kết quả, đánh giá, hay bảng số liệu của báo cáo.

---

## SR-03 – Original Files Are Raw Inputs, Not Final Database Records

- File PDF/DOCX/XLSX gốc là đầu vào thô.
- MongoDB chỉ lưu **kết quả sau trích xuất**: `extracted_text`, `cleaned_text`, `keywords`, `binary_vector`.
- Lưu file gốc bằng GridFS là **tùy chọn**, không phải yêu cầu bắt buộc.

---

## SR-04 – Binary Matching Means 0/1 Feature Representation

- "Nhị phân" trong đồ án này có nghĩa là **vector 0/1 theo kỹ năng/từ khóa**.
- `1` = kỹ năng/từ khóa **xuất hiện** trong tài liệu.
- `0` = kỹ năng/từ khóa **không xuất hiện** trong tài liệu.
- **Tuyệt đối không** hiểu "nhị phân" là so sánh bytes của file PDF hay Word.

```json
{
  "Python": 1,
  "Pandas": 1,
  "SQL": 0,
  "React": 0,
  "MongoDB": 0
}
```

---

## SR-05 – Labels Must Be Real or Validated

- Nhãn dùng để đánh giá thuật toán phải là nhãn thật hoặc đã được xác nhận bởi học viên/giảng viên.
- Nhãn do học viên tự chọn khóa học phù hợp (`student_selected`) là hợp lệ.
- Không tự gán nhãn giả để inflate accuracy.

---

## SR-06 – Supported File Formats

Hệ thống **phải** xử lý được các định dạng sau:

| Format | MIME Type |
|--------|-----------|
| PDF | `application/pdf` |
| DOCX | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| XLSX | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (tùy chọn) |

---

## SR-07 – Extraction Libraries

Phải dùng đúng thư viện theo định dạng file:

| Format | Library |
|--------|---------|
| PDF | `pypdf` hoặc `PyMuPDF` |
| DOCX | `python-docx` |
| XLSX | `openpyxl` |

Không được dùng `subprocess`, `os.system`, hay công cụ ngoài Python để đọc file.

---

## SR-08 – Failed Extraction Must Be Visible

- Nếu file không trích xuất được, `processing_status` phải là `"failed"`.
- `error_message` phải lưu nội dung lỗi cụ thể.
- Không được silently fail (không được bắt lỗi rồi bỏ qua).

---

## SR-09 – MongoDB Stores Structured Documents

- MongoDB chỉ lưu dữ liệu **đã được cấu trúc hóa**: JSON/Dictionary.
- Không lưu raw bytes của file vào field thông thường.
- Nếu cần lưu file gốc, dùng **GridFS** (tùy chọn).

---

## SR-10 – Do Not Store Secrets in MongoDB

- Không lưu JWT secret, API key, hay thông tin nhạy cảm vào MongoDB.
- Tất cả secrets phải lưu trong file `.env` (không push lên Git).

---

## SR-11 – Passwords Must Be Hashed

- Mật khẩu **phải** được hash trước khi lưu vào MongoDB.
- Dùng `pwdlib[argon2]` hoặc `bcrypt`.
- Tuyệt đối không lưu plaintext password.

---

## SR-12 – FastAPI Must Use RESTful API

- Tất cả endpoint phải tuân chuẩn RESTful: đúng HTTP method, đúng status code.
- Swagger `/docs` phải truy cập được và phản ánh đúng API.

---

## SR-13 – JWT Authentication Is Required

- Tất cả endpoint (trừ `/auth/register`, `/auth/login`, `/`, `/health`) phải yêu cầu JWT.
- Token phải có thời hạn (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- Không dùng session hoặc cookie để xác thực.

---

## SR-14 – Role Authorization Is Required

- Role chỉ gồm `admin` và `student`.
- Endpoint upload course document chỉ `admin` mới được gọi.
- Endpoint upload student document chỉ `student` mới được gọi.
- Không bypass role check bằng bất kỳ cách nào.

---

## SR-15 – Async/Await Is Required Where Appropriate

- Tất cả MongoDB query phải dùng async/await với PyMongo Async API.
- File I/O nặng phải dùng `asyncio` hoặc `run_in_executor`.

---

## SR-16 – React Must Be SPA

- Frontend phải là Single Page Application (SPA).
- Routing phải dùng React Router DOM (client-side routing).
- Không dùng multi-page HTML hoặc server-side rendering.

---

## SR-17 – Frontend Must Not Hard-Code Backend URL

- Backend URL phải đọc từ biến môi trường `VITE_API_BASE_URL`.
- Không hard-code `http://localhost:8000` hay bất kỳ URL cố định nào trong source code.

---

## SR-18 – Cloud Deployment Is Required

- Frontend phải deploy lên **Azure Static Web Apps**.
- Backend phải deploy lên **Azure App Service**.
- Database phải dùng **MongoDB Atlas**.

---

## SR-19 – Environment Variables Must Be Hidden

- File `.env` **không được** push lên GitHub.
- Repo phải có `.env.example` (không chứa giá trị thật).
- `.env` phải có trong `.gitignore`.

---

## SR-20 – CORS Must Be Configured

- FastAPI phải cấu hình CORS cho phép frontend domain.
- Local dev: `http://localhost:5173`.
- Production: Azure Static Web Apps URL.
- Không dùng `allow_origins=["*"]` trong production.

---

## SR-21 – Report Must Explain NoSQL Thinking

- Báo cáo **phải** giải thích lý do chọn MongoDB (document-oriented, flexible schema).
- Phải so sánh được với SQL (relational vs document).
- Phải giải thích embedding vs referencing trong schema.

---

## SR-22 – Report Must Include Real Data Proof

- Báo cáo **phải** có screenshot MongoDB Atlas với dữ liệu thật.
- Phải có screenshot kết quả matching từ dữ liệu thật.
- Phải có bảng số liệu evaluation từ dữ liệu thật có nhãn xác nhận.
