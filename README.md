# CourseMatch

CourseMatch is a FARM stack application for matching real course documents with real student learning needs using binary keyword vectors and Jaccard Similarity.

The implementation follows the requirements in `docs/`:

- FastAPI backend with RESTful APIs and JWT authentication.
- MongoDB/MongoDB Atlas document storage.
- React SPA frontend with React Router and Axios.
- PDF/DOCX/XLSX extraction through Python libraries only.
- No fake/generated data for algorithm evaluation.

## Local Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload
```

Swagger runs at `http://localhost:8000/docs`.

## Local Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

The frontend runs at `http://localhost:5173`.

