# Mapping-Lession-with-Student

CourseMatch document matching app with:

- FastAPI backend for authentication, PDF/DOCX upload, MongoDB GridFS storage, matching, and evaluation.
- React Vite frontend for admin and student workflows.
- MongoDB Atlas/local MongoDB configuration through environment variables.

## Project Structure

```text
coursematch-frontend/   React Vite UI
fastapi-azure-lab/      FastAPI backend
```

## Backend Setup

```powershell
cd fastapi-azure-lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
```

Fill `.env` locally. Do not commit `.env`.

Required backend variables:

```env
MONGODB_URL=
MONGODB_DB_NAME=coursematch_document_db
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
MAX_UPLOAD_SIZE_MB=10
MATCHING_MAX_FEATURES=500
```

Run backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Test:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Frontend Setup

```powershell
cd coursematch-frontend
npm install
copy .env.example .env
npm run dev -- --host 127.0.0.1 --port 5173
```

Frontend:

```text
http://127.0.0.1:5173/
```

## Main Workflow

1. Register/login as admin or student.
2. Admin uploads real course PDF/DOCX documents.
3. Student uploads a real CV or learning-need PDF/DOCX document.
4. Backend stores original binary files in MongoDB GridFS and extracted text/metadata in MongoDB.
5. Run matching for a student document.
6. Admin reviews evaluation summary.

## Azure App Service Startup Command

For Linux App Service:

```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

Set production secrets and URLs in Azure App Service Configuration, not in source code.
