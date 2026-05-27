# CourseMatch Frontend

CourseMatch - He thong doi sanh tai lieu khoa hoc va nhu cau hoc vien.

## Cong nghe

- React Vite
- React Router DOM
- Axios
- Context API
- CSS thuan

## Cau hinh

Tao `.env` tu `.env.example`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Chay local

Backend can chay tai `http://127.0.0.1:8000`.

```powershell
cd d:\demo\coursematch-frontend
npm.cmd install
npm.cmd run dev
```

Hoac dung script Windows:

```powershell
.\run_dev.cmd
```

Frontend:

```text
http://localhost:5173
```

## Trang chinh

- `/` Home
- `/login`
- `/register`
- `/admin/course-documents`
- `/student/documents/upload`
- `/student/documents`
- `/student/documents/:id/matches`
- `/admin/evaluation`

## Data Policy

- Giao dien moi chi phuc vu luong upload PDF/DOCX that.
- Khong dung luong form category/skills/registration cu cho bao cao.
- Du lieu danh gia chinh thuc phai co file that va ground truth do hoc vien/xac nhan khao sat.
- Ground truth khong tham gia qua trinh tinh diem matching.

Hien tai chi chay local, chua deploy Azure va chua ket noi MongoDB Atlas.
