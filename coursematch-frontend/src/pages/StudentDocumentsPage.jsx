import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axiosClient, { getApiError } from "../api/axiosClient";

const text = {
  eyebrow: "H\u1ecdc vi\u00ean",
  title: "H\u1ed3 s\u01a1 c\u1ee7a t\u00f4i",
  upload: "Upload CV / Nhu c\u1ea7u",
  loading: "\u0110ang t\u1ea3i...",
  empty: "Ch\u01b0a c\u00f3 h\u1ed3 s\u01a1. H\u00e3y t\u1ea3i CV ho\u1eb7c nh\u1eadp nhu c\u1ea7u h\u1ecdc t\u1eadp \u0111\u1ec3 xem g\u1ee3i \u00fd.",
  view: "Xem g\u1ee3i \u00fd",
  delete: "X\u00f3a l\u1ecbch s\u1eed",
  deleted: "\u0110\u00e3 x\u00f3a l\u1ecbch s\u1eed mapping.",
  confirmDelete: "X\u00f3a h\u1ed3 s\u01a1 n\u00e0y kh\u1ecfi l\u1ecbch s\u1eed mapping?",
  type: "Lo\u1ea1i h\u1ed3 s\u01a1",
  file: "Ngu\u1ed3n d\u1eef li\u1ec7u",
  action: "H\u00e0nh \u0111\u1ed9ng",
};

export default function StudentDocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState("");

  async function loadDocuments() {
    setLoading(true);
    setError("");
    try {
      const response = await axiosClient.get("/student/documents/me");
      setDocuments(response.data);
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  function formatPurpose(value) {
    if (value === "anonymized_cv") return "CV c\u00e1 nh\u00e2n";
    if (value === "learning_need" || value === "profile_text") return "Nhu c\u1ea7u h\u1ecdc t\u1eadp";
    return value;
  }

  function formatSource(doc) {
    if (doc.document_purpose === "profile_text" || doc.document_purpose === "learning_need") return "M\u00f4 t\u1ea3 nhu c\u1ea7u h\u1ecdc t\u1eadp";
    return doc.original_filename || "CV / t\u00e0i li\u1ec7u";
  }

  async function deleteHistory(doc) {
    if (!window.confirm(text.confirmDelete)) return;
    setDeletingId(doc.id);
    setError("");
    setMessage("");
    try {
      await axiosClient.delete(`/student/documents/${doc.id}`);
      setDocuments((current) => current.filter((item) => item.id !== doc.id));
      setMessage(text.deleted);
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setDeletingId("");
    }
  }

  return (
    <main className="page student-history-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">{text.eyebrow}</p>
          <h1>{text.title}</h1>
        </div>
        <Link className="button" to="/student/documents/upload">{text.upload}</Link>
      </div>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
      {loading ? <p>{text.loading}</p> : (
        <div className="table-wrap student-history-table-wrap">
          <table className="student-history-table">
            <thead>
              <tr>
                <th>{text.type}</th>
                <th>{text.file}</th>
                <th>{text.action}</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id}>
                  <td>{formatPurpose(doc.document_purpose)}</td>
                  <td>{formatSource(doc)}</td>
                  <td className="table-actions">
                    <Link className="button" to={`/student/documents/${doc.id}/matches`}>{text.view}</Link>
                    <button className="button secondary subtle-danger" type="button" onClick={() => deleteHistory(doc)} disabled={deletingId === doc.id}>
                      {deletingId === doc.id ? "\u0110ang x\u00f3a..." : text.delete}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {!loading && documents.length === 0 && <p className="empty-state">{text.empty}</p>}
    </main>
  );
}
