import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosClient, { getApiError } from "../api/axiosClient";

export default function StudentUploadPage() {
  const [form, setForm] = useState({
    student_alias: "",
    document_purpose: "learning_need",
    consent_confirmed: false,
    file: null,
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    const data = new FormData();
    data.append("student_alias", form.student_alias);
    data.append("document_purpose", form.document_purpose);
    data.append("consent_confirmed", String(form.consent_confirmed));
    data.append("file", form.file);

    try {
      await axiosClient.post("/student/documents/upload", data, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      navigate("/student/documents");
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="page narrow">
      <section className="panel">
        <h1>Upload nhu cầu/CV</h1>
        <p className="warning-text">Chỉ chấp nhận PDF hoặc DOCX. Không tải lên thông tin nhạy cảm không cần thiết.</p>
        <form className="form" onSubmit={handleSubmit}>
          <label>
            Student alias
            <input value={form.student_alias} onChange={(event) => updateField("student_alias", event.target.value)} placeholder="SV01" required />
          </label>
          <label>
            Document purpose
            <select value={form.document_purpose} onChange={(event) => updateField("document_purpose", event.target.value)}>
              <option value="learning_need">learning_need</option>
              <option value="anonymized_cv">anonymized_cv</option>
            </select>
          </label>
          <label>
            File PDF/DOCX
            <input type="file" accept=".pdf,.docx" onChange={(event) => updateField("file", event.target.files?.[0] || null)} required />
          </label>
          <label className="checkbox-label">
            <input type="checkbox" checked={form.consent_confirmed} onChange={(event) => updateField("consent_confirmed", event.target.checked)} />
            Tôi xác nhận file được phép sử dụng và đã ẩn thông tin nhạy cảm nếu cần.
          </label>
          {error && <p className="error">{error}</p>}
          <button className="button" type="submit" disabled={submitting}>
            {submitting ? "Đang upload..." : "Upload"}
          </button>
        </form>
      </section>
    </main>
  );
}
