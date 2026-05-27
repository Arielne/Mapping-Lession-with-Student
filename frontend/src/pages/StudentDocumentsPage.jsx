import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axiosClient from "../api/axiosClient";

export default function StudentDocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState("");

  useEffect(() => {
    axiosClient
      .get("/student-documents/me")
      .then(({ data }) => setDocuments(data))
      .catch((err) => setError(err.response?.data?.detail || "Cannot load documents"));
  }, []);

  async function runMatching(id) {
    setBusyId(id);
    setError("");
    try {
      await axiosClient.post(`/matching/run/${id}`);
      window.location.href = `/matching/${id}`;
    } catch (err) {
      setError(err.response?.data?.detail || "Matching failed");
    } finally {
      setBusyId("");
    }
  }

  return (
    <main className="page">
      <section className="page-head">
        <h1>My Documents</h1>
      </section>
      {error && <p className="error">{error}</p>}
      <div className="list">
        {documents.map((document) => (
          <article className="row" key={document.id}>
            <div>
              <strong>{document.original_filename}</strong>
              <p>{document.student_code || "No student code"}</p>
              <div className="chips">
                {(document.detected_keywords || []).map((keyword) => (
                  <span key={keyword}>{keyword}</span>
                ))}
              </div>
            </div>
            <div className="actions">
              <span className={`status ${document.processing_status}`}>{document.processing_status}</span>
              {document.processing_status === "processed" && (
                <button className="primary" onClick={() => runMatching(document.id)} disabled={busyId === document.id}>
                  {busyId === document.id ? "Running..." : "Run Matching"}
                </button>
              )}
              <Link className="button-link" to={`/matching/${document.id}`}>
                Results
              </Link>
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}

