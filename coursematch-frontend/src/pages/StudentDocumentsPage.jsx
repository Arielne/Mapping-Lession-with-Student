import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axiosClient, { getApiError } from "../api/axiosClient";

export default function StudentDocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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
    loadDocuments();
  }, []);

  async function downloadFile(doc) {
    setError("");
    try {
      const response = await axiosClient.get(`/student/documents/${doc.id}/download`, {
        responseType: "blob",
      });
      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = doc.original_filename;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(getApiError(err));
    }
  }

  function formatPurpose(value) {
    if (value === "anonymized_cv") return "CV đã ẩn thông tin nhạy cảm";
    if (value === "learning_need") return "Nhu cầu học tập";
    if (value === "profile_text") return "Mo ta ky nang / so thich";
    return value;
  }

  return (
    <main className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Học viên</p>
          <h1>CV / Hồ sơ nhu cầu của tôi</h1>
        </div>
        <Link className="button" to="/student/documents/upload">Upload CV / Nhu cầu</Link>
      </div>
      {error && <p className="error">{error}</p>}
      {loading ? <p>Đang tải...</p> : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Mã học viên</th>
                <th>Loại hồ sơ</th>
                <th>File</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.student_alias}</td>
                  <td>{formatPurpose(doc.document_purpose)}</td>
                  <td>{doc.original_filename}</td>
                  <td>{doc.extraction_status}</td>
                  <td className="table-actions">
                    <Link className="button" to={`/student/documents/${doc.id}/matches`}>Xem gợi ý</Link>
                    <button className="button secondary" type="button" onClick={() => downloadFile(doc)}>Download</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {!loading && documents.length === 0 && <p>Chưa có tài liệu. Hãy upload file thật để test nghiệp vụ.</p>}
    </main>
  );
}
