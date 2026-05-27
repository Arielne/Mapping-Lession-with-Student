import { useState } from "react";
import axiosClient from "../api/axiosClient";
import UploadForm from "../components/UploadForm";

export default function AdminUploadCoursePage() {
  const [title, setTitle] = useState("");
  const [sourceNote, setSourceNote] = useState("");
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
    data.append("title", title);
    data.append("source_note", sourceNote);
    data.append("file", file);
    try {
      const response = await axiosClient.post("/course-documents/upload", data);
      setMessage(`Uploaded ${response.data.original_filename} (${response.data.processing_status})`);
      setTitle("");
      setSourceNote("");
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
        <h1>Upload Course</h1>
      </section>
      <UploadForm
        busy={busy}
        submitLabel="Upload Course"
        onSubmit={handleSubmit}
        fields={
          <>
            <label>
              Title
              <input value={title} onChange={(event) => setTitle(event.target.value)} required />
            </label>
            <label>
              Source note
              <input value={sourceNote} onChange={(event) => setSourceNote(event.target.value)} />
            </label>
            <label>
              File
              <input
                type="file"
                accept=".pdf,.docx,.xlsx"
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

