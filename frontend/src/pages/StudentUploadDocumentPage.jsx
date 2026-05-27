import { useState } from "react";
import axiosClient from "../api/axiosClient";
import UploadForm from "../components/UploadForm";

export default function StudentUploadDocumentPage() {
  const [studentCode, setStudentCode] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) return;
    setBusy(true);
    setError("");
    setMessage("");
    const data = new FormData();
    if (studentCode) data.append("student_code", studentCode);
    data.append("file", file);
    try {
      const response = await axiosClient.post("/student-documents/upload", data);
      setMessage(`Uploaded ${response.data.original_filename} (${response.data.processing_status})`);
      setStudentCode("");
      setFile(null);
      event.target.reset();
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page narrow">
      <section className="page-head">
        <h1>Upload Document</h1>
      </section>
      <UploadForm
        busy={busy}
        submitLabel="Upload Document"
        onSubmit={handleSubmit}
        fields={
          <>
            <label>
              Student code
              <input value={studentCode} onChange={(event) => setStudentCode(event.target.value)} />
            </label>
            <label>
              File
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(event) => setFile(event.target.files[0])}
                required
              />
            </label>
          </>
        }
      />
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
    </main>
  );
}

