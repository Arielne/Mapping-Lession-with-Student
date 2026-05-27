# Error Report

Ngày kiểm tra: 2026-05-27

## Kết luận

Dự án chưa chạy được end-to-end.

Frontend build thành công, nhưng backend chưa chạy hoàn chỉnh vì chưa có MongoDB local hoặc MongoDB Atlas được cấu hình trong `backend/.env`.

## Kết quả đã chạy thử

### 1. Frontend

Lệnh:

```powershell
cd frontend
npm.cmd run build
```

Kết quả:

```text
vite v5.4.21 building for production...
96 modules transformed.
✓ built
```

Trạng thái:

- Frontend production build chạy được.
- `dist/` đã được tạo.
- Source frontend không hard-code backend URL trong `src`; backend URL đọc từ `VITE_API_BASE_URL`.

Ghi chú:

Khi chạy dev server trong môi trường sandbox:

```powershell
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

có lúc Vite báo:

```text
Cannot read directory "../../../..": Access is denied.
Could not resolve "./cjs/react.development.js"
Could not resolve "./lib/axios.js"
Could not resolve "./cjs/react-dom.development.js"
```

Các file dependency thực tế vẫn tồn tại trong `node_modules`, nên đây là lỗi môi trường/quyền truy cập khi Vite quét filesystem, không phải lỗi thiếu file source.

### 2. Backend

Lệnh kiểm tra cú pháp:

```powershell
py -m compileall backend
```

Kết quả:

```text
Compiling backend files...
```

Trạng thái:

- Backend không có lỗi cú pháp Python.
- Dependencies Python đã được cài bằng:

```powershell
cd backend
py -m pip install -r requirements.txt
```

Lệnh kiểm tra thư viện:

```powershell
py -c "import fastapi, motor, pydantic, jwt, pwdlib, pypdf, docx, openpyxl; print('backend dependencies ok')"
```

Kết quả:

```text
backend dependencies ok
```

Lệnh chạy backend:

```powershell
cd backend
py -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Trạng thái:

- Backend không mở được port `8000` trong lần chạy thử.
- Port MongoDB local `27017` cũng không có process lắng nghe.
- Project hiện chưa có `backend/.env` thật để trỏ tới MongoDB Atlas.

## Lý do chưa chạy được

### Lỗi chính: chưa cấu hình MongoDB

Backend khởi động sẽ chạy lifespan:

```python
await connect_mongo()
await create_indexes()
```

`create_indexes()` cần kết nối MongoDB. Hiện tại:

- Không có MongoDB local đang chạy ở `localhost:27017`.
- Chưa có `backend/.env` chứa `MONGODB_URL` thật.
- Vì vậy FastAPI chưa thể hoàn tất startup để phục vụ API.

## Cách khắc phục

### Cách 1: Dùng MongoDB Atlas theo đúng docs

Tạo file:

```text
backend/.env
```

Nội dung mẫu:

```env
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster-url>/coursematch_db
MONGODB_DB_NAME=coursematch_db
JWT_SECRET_KEY=<chuoi_bi_mat_dai_va_ngau_nhien>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:5173
```

Sau đó chạy:

```powershell
cd backend
py -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Kiểm tra:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health
```

### Cách 2: Dùng MongoDB local

Cài và chạy MongoDB Community Server, bảo đảm port `27017` đang mở.

File `backend/.env`:

```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=coursematch_db
JWT_SECRET_KEY=<chuoi_bi_mat_dai_va_ngau_nhien>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:5173
```

Sau đó chạy backend như trên.

### Chạy frontend

File `frontend/.env` hiện đã có:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Chạy:

```powershell
cd frontend
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

Nếu dev server còn lỗi quyền truy cập trong thư mục hiện tại, dùng bản build:

```powershell
cd frontend
npm.cmd run build
npm.cmd run preview -- --host 127.0.0.1 --port 4173
```

## Trạng thái sau khi khắc phục

Khi MongoDB được cấu hình đúng:

1. Backend sẽ mở `http://127.0.0.1:8000`.
2. Swagger sẽ mở tại `http://127.0.0.1:8000/docs`.
3. Frontend sẽ gọi backend qua `VITE_API_BASE_URL`.
4. Có thể test workflow: register, login, upload document, matching, save labels, evaluation.

