# Report Notes for CourseMatch

**Hướng dẫn viết báo cáo đồ án – Lập trình tổ chức lưu trữ và xử lý dữ liệu**  
**Version:** 1.0

---

## 1. Project Summary

Viết phần tóm tắt dự án (khoảng 200-300 từ) bao gồm:

- **Tên hệ thống:** CourseMatch – Hệ thống đối sánh khóa học với nhu cầu học viên từ tài liệu thật
- **Mục tiêu:** Hệ thống nhận tài liệu khóa học thật (PDF/DOCX) và CV/nhu cầu học viên thật, trích xuất nội dung, tạo vector nhị phân 0/1 theo bộ từ khóa kỹ năng, và dùng thuật toán Jaccard Similarity để đối sánh và xếp hạng khóa học phù hợp.
- **Tech stack:** FARM Stack – FastAPI + React.js + MongoDB Atlas, deploy lên Azure.
- **Kết quả:** Top-1 Accuracy = X%, Hit Rate@3 = Y% (điền số liệu thật vào).

---

## 2. Data Processing Explanation

Mô tả rõ pipeline xử lý dữ liệu trong báo cáo:

### 2.1 Thu thập dữ liệu

```
Nguồn tài liệu khóa học:
- [Ghi tên nguồn thật, ví dụ: "Syllabus môn Học máy – Trường ĐH X"]
- [Syllabus môn Phân tích dữ liệu – Trường ĐH Y]
- [Đề cương khóa học Python – Tổ chức Z]

Nguồn tài liệu học viên:
- [Số lượng học viên tham gia: N học viên]
- [Loại tài liệu: CV / File mô tả nhu cầu]
- [Có ẩn danh hóa không]
```

### 2.2 Trích xuất text

Giải thích:
- PDF được đọc bằng `pypdf` (hoặc `PyMuPDF`): `PdfReader → extract_text()`
- DOCX được đọc bằng `python-docx`: `Document → paragraphs → text`
- Text thô được lưu vào field `extracted_text`

### 2.3 Làm sạch và chuẩn hóa

Giải thích:
- Chuyển về lowercase
- Loại bỏ ký tự đặc biệt, dấu câu
- Chuẩn hóa khoảng trắng
- Kết quả lưu vào `cleaned_text`

### 2.4 Tạo vector nhị phân

Giải thích:
- Bộ từ khóa SKILL_DICTIONARY gồm N kỹ năng (liệt kê)
- Duyệt qua `cleaned_text`, kiểm tra từng kỹ năng có xuất hiện không
- Tạo `binary_vector`: `{skill: 1}` nếu xuất hiện, `{skill: 0}` nếu không
- Lưu vào MongoDB document

---

## 3. MongoDB NoSQL Explanation

Phần quan trọng trong báo cáo – phải giải thích rõ lý do dùng NoSQL:

### 3.1 Tại sao chọn MongoDB?

```
1. Dữ liệu có cấu trúc linh hoạt:
   - binary_vector có số lượng key thay đổi theo SKILL_DICTIONARY
   - SQL sẽ cần N cột hoặc EAV (Entity-Attribute-Value) phức tạp
   - MongoDB lưu dict/object trực tiếp: {"Python": 1, "React": 0, ...}

2. Dữ liệu mảng/lồng nhau tự nhiên:
   - keywords: ["Python", "Pandas", "SQL"] → MongoDB native array
   - SQL cần junction table riêng

3. Schema linh hoạt:
   - Trong quá trình phát triển, cần thêm/bớt field
   - MongoDB không cần ALTER TABLE

4. Phù hợp với dữ liệu text/NLP:
   - Lưu extracted_text (đoạn văn dài) trực tiếp trong document
   - SQL LONGTEXT ít linh hoạt hơn khi kết hợp với structured data
```

### 3.2 Document-Oriented Design

```
Trong MongoDB, một course_document chứa toàn bộ thông tin:
- Metadata (title, filename, size)
- Extracted content (extracted_text, cleaned_text)
- Processed data (keywords, binary_vector)
- Status (processing_status, error_message)

→ Một query lấy được tất cả cần cho matching
→ Không cần JOIN nhiều bảng như SQL
```

---

## 4. Difference from SQL

Trình bày bảng so sánh:

| Tiêu chí | MongoDB (CourseMatch) | SQL (Giả sử dùng PostgreSQL) |
|----------|----------------------|------------------------------|
| Schema | Flexible, không cần migration | Fixed, cần ALTER TABLE |
| Binary vector | Native object `{skill: 0/1}` | Cần N cột hoặc JSON column |
| Keywords array | Native array field | Junction table |
| Text storage | Field trong document | LONGTEXT/TEXT column |
| Query | `find({binary_vector.Python: 1})` | `WHERE skills LIKE '%Python%'` |
| Horizontal scale | Built-in sharding | Cần cấu hình phức tạp |
| Phù hợp với đồ án | ✅ | Có thể làm nhưng phức tạp hơn |

---

## 5. RESTful API Benefit

Giải thích trong báo cáo:

```
Lợi ích của RESTful API trong CourseMatch:

1. Separation of Concerns:
   React frontend và FastAPI backend hoàn toàn tách biệt
   → Có thể deploy độc lập, thay thế độc lập

2. Stateless:
   Mỗi request tự mang JWT token → không cần session
   → Backend scale dễ dàng (horizontal)

3. Standard HTTP Methods:
   GET (read), POST (create), DELETE (remove) → dễ hiểu, dễ test
   → Swagger /docs tự động document

4. Swagger /docs:
   FastAPI tự tạo OpenAPI documentation từ code
   → Developer khác có thể test API không cần đọc code
```

---

## 6. Algorithm Explanation

Viết phần giải thích thuật toán trong báo cáo:

```
Thuật toán: Jaccard Similarity trên Binary Keyword Vector

Bước 1: Xây dựng bộ từ khóa SKILL_DICTIONARY (N kỹ năng)

Bước 2: Với mỗi tài liệu (khóa học hoặc học viên):
  - Trích xuất text thô từ PDF/DOCX
  - Làm sạch text (lowercase, remove punctuation)
  - Kiểm tra từng skill trong SKILL_DICTIONARY có xuất hiện không
  - Tạo binary_vector: {skill: 1 nếu xuất hiện, 0 nếu không}

Bước 3: Tính Jaccard Similarity giữa học viên và mỗi khóa học:
  A = tập kỹ năng của học viên (value = 1)
  B = tập kỹ năng của khóa học (value = 1)
  J(A,B) = |A ∩ B| / |A ∪ B|

Bước 4: Xếp hạng khóa học theo score giảm dần

Bước 5: Trả về top-K khóa học phù hợp nhất
```

---

## 7. Evaluation Explanation

```
Phương pháp đánh giá:
- Dữ liệu: [N] học viên thật đã upload tài liệu và xác nhận nhãn
- Nhãn: học viên tự chọn khóa học phù hợp với mình sau khi xem kết quả
- Không dùng dữ liệu tự chế hay seed data

Metrics:
1. Top-1 Accuracy:
   = (số học viên được dự đoán đúng khóa top-1) / (tổng số học viên có nhãn)
   = [X] / [N] = [X/N * 100]%

2. Hit Rate@3:
   = (số học viên có khóa đúng trong top-3) / (tổng số học viên có nhãn)
   = [Y] / [N] = [Y/N * 100]%

3. Avg Processing Time:
   = [Z] ms per matching operation

Nhận xét: [Viết nhận xét về kết quả, hạn chế, hướng cải thiện]
```

---

## 8. Screenshots to Include

Báo cáo phải có đủ các screenshot sau:

| # | Screenshot | Mô tả |
|---|-----------|-------|
| 1 | React Frontend – Home Page | Trang chủ sau khi login |
| 2 | Admin Upload Course Document | Form upload và kết quả sau khi upload |
| 3 | Course Documents List | Danh sách khóa học với status "processed" |
| 4 | Student Upload Document | Form upload CV/nhu cầu |
| 5 | Match Results Page | Top-3 khóa học phù hợp với score |
| 6 | Evaluation Metrics Page | Top-1 Accuracy, Hit Rate@3 |
| 7 | Swagger /docs | Giao diện API documentation |
| 8 | MongoDB Atlas – Collections | Danh sách collections với document count |
| 9 | MongoDB Atlas – Sample Document | Ví dụ một course_document với binary_vector |
| 10 | Azure App Service | Backend đang chạy, URL |
| 11 | Azure Static Web Apps | Frontend đang chạy, URL |
| 12 | Azure App Service – Configuration | Environment variables (che giá trị nhạy cảm) |
| 13 | GitHub Repository | Cấu trúc thư mục, `.env` không có trong repo |

> ⚠️ **Che thông tin nhạy cảm trong screenshot:**  
> - MongoDB connection string  
> - JWT_SECRET_KEY  
> - Passwords  
> - Thông tin cá nhân học viên (nếu cần)

---

## 9. Final Submission Checklist

Trước khi nộp, kiểm tra tất cả mục sau:

### Code

- [ ] GitHub repo public (hoặc share với giảng viên)
- [ ] `.env` không có trong repo
- [ ] `.env.example` có trong repo
- [ ] `requirements.txt` đầy đủ và chính xác
- [ ] `package.json` đầy đủ
- [ ] README.md trong repo có hướng dẫn chạy local

### Deployment

- [ ] Frontend live tại `https://<app>.azurestaticapps.net`
- [ ] Backend Swagger tại `https://<app>.azurewebsites.net/docs`
- [ ] Login hoạt động trên production
- [ ] Upload file hoạt động trên production
- [ ] Matching hoạt động trên production

### Database

- [ ] MongoDB Atlas có tài liệu khóa học thật (ít nhất 5 khóa)
- [ ] MongoDB Atlas có tài liệu học viên thật (ít nhất 5 học viên)
- [ ] Các document có `processing_status = "processed"`
- [ ] match_results collection có dữ liệu
- [ ] student_documents có `validated_course_ids` (nhãn thật)

### Algorithm

- [ ] Binary vector 0/1 được tạo đúng
- [ ] Jaccard score tính đúng (kiểm tra tay ít nhất 1 ví dụ)
- [ ] Top-K ranking đúng thứ tự
- [ ] Evaluation metrics từ dữ liệu thật

### Báo cáo

- [ ] Giải thích NoSQL vs SQL
- [ ] Giải thích thuật toán Jaccard với ví dụ cụ thể
- [ ] Bảng kết quả evaluation với số liệu thật
- [ ] Screenshot đầy đủ (che thông tin nhạy cảm)
- [ ] Danh sách link: GitHub, Frontend URL, Backend /docs URL
- [ ] Không có số liệu từ demo/fake data trong báo cáo

### Links cần nộp

| Item | Link |
|------|------|
| GitHub Source Code | `https://github.com/...` |
| Frontend Live Demo | `https://....azurestaticapps.net` |
| Backend Swagger /docs | `https://....azurewebsites.net/docs` |
| PDF Report | File đính kèm |
