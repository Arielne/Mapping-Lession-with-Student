# CourseMatch Architecture

**Version:** 1.0  
**Date:** 2026-05-27

---

## 1. High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        User Browser                            │
└───────────────────────────┬────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌────────────────────────────────────────────────────────────────┐
│              React SPA Frontend                                │
│              Azure Static Web Apps                             │
│                                                                │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│   │   Auth   │  │  Admin   │  │ Student  │  │   Match  │     │
│   │  Pages   │  │  Pages   │  │  Pages   │  │  Pages   │     │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                                                                │
│   ┌────────────────────────────────────────────────────────┐  │
│   │  axiosClient (base URL from VITE_API_BASE_URL env var) │  │
│   └────────────────────────────────────────────────────────┘  │
└───────────────────────────┬────────────────────────────────────┘
                            │ RESTful API calls
                            │ Authorization: Bearer <JWT>
                            ▼
┌────────────────────────────────────────────────────────────────┐
│              FastAPI Backend                                   │
│              Azure App Service                                 │
│                                                                │
│   ┌──────────────────────────────────────────────────────┐    │
│   │  FastAPI Routers                                     │    │
│   │  /auth  /course-documents  /student-documents        │    │
│   │  /matching  /evaluation                              │    │
│   └───────────────────────────┬──────────────────────────┘    │
│                               │                                │
│   ┌───────────────────────────▼──────────────────────────┐    │
│   │  File Processing Pipeline                            │    │
│   │  file_extractor → text_cleaner                       │    │
│   │  → keyword_extractor → vectorizer                   │    │
│   └───────────────────────────┬──────────────────────────┘    │
│                               │                                │
│   ┌───────────────────────────▼──────────────────────────┐    │
│   │  Matching Engine                                     │    │
│   │  matcher.py (Jaccard Similarity)                     │    │
│   └───────────────────────────┬──────────────────────────┘    │
└───────────────────────────────┼────────────────────────────────┘
                                │ PyMongo Async
                                ▼
┌────────────────────────────────────────────────────────────────┐
│              MongoDB Atlas (Cloud)                             │
│                                                                │
│   coursematch_db                                               │
│   ├── users                                                    │
│   ├── course_documents                                         │
│   ├── student_documents                                        │
│   ├── match_results                                            │
│   └── fs.files / fs.chunks  (GridFS, optional)                │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. FARM Stack Mapping

| Layer | Technology | Role |
|-------|-----------|------|
| **F** – Frontend | React.js + Vite | SPA, UI, routing, state |
| **A** – API | FastAPI (Python) | RESTful API, business logic, file processing |
| **R** – Runtime/Server | Uvicorn + Azure App Service | ASGI server, deployment host |
| **M** – MongoDB | MongoDB Atlas | Document database, storing structured data |

---

## 3. Frontend Architecture

```
frontend/src/
├── main.jsx              ← Entry point, wrap với BrowserRouter + AuthProvider
├── App.jsx               ← Route definitions
├── api/
│   └── axiosClient.js    ← Axios instance, interceptors cho JWT
├── context/
│   └── AuthContext.jsx   ← Global auth state (user, token, login, logout)
├── components/
│   ├── Navbar.jsx
│   ├── UploadBox.jsx
│   ├── ProtectedRoute.jsx  ← Redirect nếu chưa login
│   ├── AdminRoute.jsx      ← Redirect nếu không phải admin
│   ├── DocumentCard.jsx
│   └── MatchResultCard.jsx
└── pages/
    ├── HomePage.jsx
    ├── LoginPage.jsx
    ├── RegisterPage.jsx
    ├── AdminUploadCoursePage.jsx
    ├── CourseDocumentsPage.jsx
    ├── StudentUploadDocumentPage.jsx
    ├── StudentDocumentsPage.jsx
    ├── MatchResultsPage.jsx
    └── EvaluationPage.jsx
```

**State Management:** Context API (không dùng Redux – đơn giản hóa).

**Auth Flow:**
```
Login → nhận JWT token → lưu vào AuthContext (memory + localStorage)
Request → axiosClient tự attach "Authorization: Bearer <token>"
Logout → xóa token khỏi AuthContext
```

---

## 4. Backend Architecture

```
backend/
├── main.py               ← FastAPI app, include routers, CORS config
├── requirements.txt
├── .env.example
└── app/
    ├── config.py         ← Pydantic Settings (đọc .env)
    ├── database.py       ← PyMongo Async client, collection getters
    ├── security.py       ← JWT create/verify, password hash/verify
    ├── dependencies.py   ← get_current_user, get_current_admin, get_current_student
    ├── utils/
    │   ├── file_extractor.py   ← PDF/DOCX/XLSX text extraction
    │   ├── text_cleaner.py     ← Normalize, lowercase, clean
    │   ├── keyword_extractor.py← SKILL_DICTIONARY, keyword matching
    │   ├── vectorizer.py       ← Build binary_vector dict
    │   └── matcher.py          ← Jaccard Similarity, ranking
    ├── schemas/
    │   ├── auth.py             ← RegisterRequest, LoginRequest, TokenResponse
    │   ├── course_document.py  ← CourseDocumentResponse
    │   ├── student_document.py ← StudentDocumentResponse
    │   └── match_result.py     ← MatchResultResponse
    └── routers/
        ├── auth.py
        ├── course_documents.py
        ├── student_documents.py
        ├── matching.py
        └── evaluation.py
```

**Dependency Injection Flow:**
```
Request → Router → Depends(get_current_user) → decode JWT
                                              → fetch user from DB
                                              → return user object
```

---

## 5. Runtime Architecture

```
Uvicorn (ASGI server)
   └── FastAPI Application
         ├── CORS Middleware
         ├── Router: /auth
         ├── Router: /course-documents
         ├── Router: /student-documents
         ├── Router: /matching
         └── Router: /evaluation
```

**Startup:**
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CourseMatch API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 6. Deployment Architecture

```
GitHub Repository
       ↓ (CI/CD or manual)
┌──────────────────────┐    ┌──────────────────────────┐
│ Azure Static Web Apps│    │   Azure App Service      │
│ (Frontend)           │    │   (Backend FastAPI)      │
│                      │    │                          │
│ Build: npm run build │    │ Runtime: Python 3.11     │
│ Publish dir: dist/   │    │ Start: uvicorn main:app  │
│                      │    │ Env: Application Settings│
└──────────────────────┘    └──────────┬───────────────┘
                                       │ MONGODB_URL
                                       ▼
                            ┌──────────────────────────┐
                            │   MongoDB Atlas          │
                            │   Cluster M0             │
                            │   coursematch_db         │
                            └──────────────────────────┘
```

---

## 7. CORS Architecture

```
Local Development:
  Frontend: http://localhost:5173
  Backend:  http://localhost:8000
  FRONTEND_URL=http://localhost:5173

Production:
  Frontend: https://<app>.azurestaticapps.net
  Backend:  https://<app>.azurewebsites.net
  FRONTEND_URL=https://<app>.azurestaticapps.net
```

FastAPI CORS config đọc `FRONTEND_URL` từ `.env` → không hard-code.

---

## 8. Authentication Architecture

```
Client                    FastAPI Backend              MongoDB
  │                            │                          │
  │── POST /auth/login ────────▶                          │
  │   {email, password}        │── find user by email ──▶│
  │                            │◀─ user document ─────────│
  │                            │                          │
  │                            │ verify password hash     │
  │                            │ create JWT token         │
  │◀── {access_token} ─────────│                          │
  │                            │                          │
  │── GET /auth/me ────────────▶                          │
  │   Authorization: Bearer    │ decode JWT               │
  │                            │── find user by id ──────▶│
  │◀── {user info} ────────────│◀─ user document ─────────│
```

**JWT Payload:**
```json
{
  "sub": "user_id_string",
  "role": "student",
  "exp": 1748390400
}
```
