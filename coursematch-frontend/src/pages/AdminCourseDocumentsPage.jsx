import { useEffect, useState } from "react";
import axiosClient, { getApiError } from "../api/axiosClient";

export default function AdminCourseDocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [form, setForm] = useState({ course_title: "", source_name: "", source_url_or_note: "", file: null });
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadDocuments() {
    setLoading(true);
    setError("");
    try {
      const response = await axiosClient.get("/admin/course-documents");
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

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    const data = new FormData();
    data.append("course_title", form.course_title);
    data.append("source_name", form.source_name);
    if (form.source_url_or_note) data.append("source_url_or_note", form.source_url_or_note);
    data.append("file", form.file);

    try {
      await axiosClient.post("/admin/course-documents/upload", data, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMessage("Đã upload tài liệu khóa học.");
      setForm({ course_title: "", source_name: "", source_url_or_note: "", file: null });
      event.target.reset();
      loadDocuments();
    } catch (err) {
      setError(getApiError(err));
    }
  }

  async function loadDetail(id) {
    setError("");
    try {
      const response = await axiosClient.get(`/admin/course-documents/${id}`);
      setSelected(response.data);
    } catch (err) {
      setError(getApiError(err));
    }
  }

  async function softDelete(id) {
    setError("");
    setMessage("");
    try {
      await axiosClient.delete(`/admin/course-documents/${id}`);
      setMessage("Đã xóa mềm tài liệu khóa học.");
      loadDocuments();
    } catch (err) {
      setError(getApiError(err));
    }
  }

  async function downloadFile(doc) {
    setError("");
    try {
      const response = await axiosClient.get(`/admin/course-documents/${doc.id}/download`, {
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

  return (
    <main className="page admin-layout">
      <section className="panel">
        <h1>Upload tài liệu khóa học</h1>
        <form className="form" onSubmit={handleSubmit}>
          <label>
            Course title
            <input value={form.course_title} onChange={(event) => updateField("course_title", event.target.value)} required />
          </label>
          <label>
            Source name
            <input value={form.source_name} onChange={(event) => updateField("source_name", event.target.value)} required />
          </label>
          <label>
            Source note optional
            <input value={form.source_url_or_note} onChange={(event) => updateField("source_url_or_note", event.target.value)} />
          </label>
          <label>
            File PDF/DOCX
            <input type="file" accept=".pdf,.docx" onChange={(event) => updateField("file", event.target.files?.[0] || null)} required />
          </label>
          {error && <p className="error">{error}</p>}
          {message && <p className="success">{message}</p>}
          <button className="button" type="submit">Upload</button>
        </form>
      </section>
      <section>
        <div className="page-heading">
          <div>
            <p className="eyebrow">Admin</p>
            <h1>Tài liệu khóa học thật</h1>
          </div>
        </div>
        {loading ? <p>Đang tải...</p> : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Course</th>
                  <th>File</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id}>
                    <td>{doc.course_title}</td>
                    <td>{doc.original_filename}</td>
                    <td>{doc.extraction_status}</td>
                    <td>{new Date(doc.created_at).toLocaleString()}</td>
                    <td className="table-actions">
                      <button className="button ghost" type="button" onClick={() => loadDetail(doc.id)}>Chi tiết</button>
                      <button className="button secondary" type="button" onClick={() => downloadFile(doc)}>Download</button>
                      <button className="button danger" type="button" onClick={() => softDelete(doc.id)}>Xóa mềm</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {selected && (
          <section className="panel detail-panel">
            <h2>{selected.course_title}</h2>
            <p><strong>Nguồn:</strong> {selected.source_name}</p>
            <p><strong>Status:</strong> {selected.extraction_status}</p>
            <pre>{selected.extracted_text || "Không có text trích xuất."}</pre>
          </section>
        )}
      </section>
    </main>
  );
}
