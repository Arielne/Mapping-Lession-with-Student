import { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";

export default function CourseDocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    axiosClient
      .get("/course-documents")
      .then(({ data }) => setDocuments(data))
      .catch((err) => setError(err.response?.data?.detail || "Cannot load courses"));
  }, []);

  return (
    <main className="page">
      <section className="page-head">
        <h1>Course Documents</h1>
      </section>
      {error && <p className="error">{error}</p>}
      <div className="list">
        {documents.map((document) => (
          <article className="row" key={document.id}>
            <div>
              <strong>{document.title}</strong>
              <p>{document.original_filename}</p>
              <div className="chips">
                {(document.keywords || []).map((keyword) => (
                  <span key={keyword}>{keyword}</span>
                ))}
              </div>
            </div>
            <span className={`status ${document.processing_status}`}>{document.processing_status}</span>
          </article>
        ))}
      </div>
    </main>
  );
}

