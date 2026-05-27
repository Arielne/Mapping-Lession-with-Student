import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <h1>CourseMatch</h1>
          <p>{user.full_name} · {user.role}</p>
        </div>
      </section>
      <section className="grid">
        <Link className="tile" to="/courses">
          <strong>Course Documents</strong>
          <span>Processed course files and keywords</span>
        </Link>
        {user.role === "admin" ? (
          <>
            <Link className="tile" to="/admin/upload-course">
              <strong>Upload Course</strong>
              <span>PDF, DOCX, XLSX</span>
            </Link>
            <Link className="tile" to="/evaluation">
              <strong>Evaluation</strong>
              <span>Top-1, Hit Rate@3, processing time</span>
            </Link>
          </>
        ) : (
          <>
            <Link className="tile" to="/student/upload">
              <strong>Upload Document</strong>
              <span>CV or learning need</span>
            </Link>
            <Link className="tile" to="/student/documents">
              <strong>My Documents</strong>
              <span>Extraction status and matching</span>
            </Link>
          </>
        )}
      </section>
    </main>
  );
}

