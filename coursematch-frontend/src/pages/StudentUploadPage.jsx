import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosClient, { getApiError } from "../api/axiosClient";

export default function StudentUploadPage() {
  const [mode, setMode] = useState("file");
  const [form, setForm] = useState({
    student_alias: "",
    document_purpose: "learning_need",
    consent_confirmed: false,
    file: null,
    current_skills: "",
    interests: "",
    career_goals: "",
    learning_preferences: "",
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

    try {
      let response;
      if (mode === "file") {
        if (!form.file || !/\.(pdf|docx)$/i.test(form.file.name)) {
          setError("Chi chap nhan file PDF hoac DOCX.");
          return;
        }

        const data = new FormData();
        data.append("student_alias", form.student_alias);
        data.append("document_purpose", form.document_purpose);
        data.append("consent_confirmed", String(form.consent_confirmed));
        data.append("file", form.file);

        response = await axiosClient.post("/student/documents/upload", data, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      } else {
        response = await axiosClient.post("/student/documents/profile-text", {
          student_alias: form.student_alias,
          current_skills: form.current_skills,
          interests: form.interests,
          career_goals: form.career_goals,
          learning_preferences: form.learning_preferences,
          consent_confirmed: form.consent_confirmed,
        });
      }
      navigate(`/student/documents/${response.data.id}/matches`);
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="page narrow">
      <section className="panel">
        <h1>Upload CV / Nhu cau hoc tap</h1>
        <div className="segmented-control">
          <button className={mode === "file" ? "active" : ""} type="button" onClick={() => setMode("file")}>
            File PDF/DOCX
          </button>
          <button className={mode === "text" ? "active" : ""} type="button" onClick={() => setMode("text")}>
            Nhap ky nang / so thich
          </button>
        </div>

        <form className="form" onSubmit={handleSubmit}>
          <label>
            Ma dinh danh hoc vien
            <input value={form.student_alias} onChange={(event) => updateField("student_alias", event.target.value)} placeholder="SV01" required />
          </label>

          {mode === "file" ? (
            <>
              <label>
                Loai ho so
                <select value={form.document_purpose} onChange={(event) => updateField("document_purpose", event.target.value)}>
                  <option value="learning_need">Nhu cau hoc tap</option>
                  <option value="anonymized_cv">CV da an thong tin nhay cam</option>
                </select>
              </label>
              <label>
                File PDF/DOCX
                <input type="file" accept=".pdf,.docx" onChange={(event) => updateField("file", event.target.files?.[0] || null)} required={mode === "file"} />
              </label>
            </>
          ) : (
            <>
              <label>
                Ky nang hien co
                <textarea value={form.current_skills} onChange={(event) => updateField("current_skills", event.target.value)} placeholder="Vi du: Excel co ban, da hoc Python, biet SQL, thich phan tich du lieu..." rows={4} />
              </label>
              <label>
                So thich
                <textarea value={form.interests} onChange={(event) => updateField("interests", event.target.value)} placeholder="Vi du: dashboard, AI, thiet ke web, kinh doanh, bao cao so lieu..." rows={3} />
              </label>
              <label>
                Muc tieu nghe nghiep / muc tieu hoc
                <textarea value={form.career_goals} onChange={(event) => updateField("career_goals", event.target.value)} placeholder="Vi du: muon lam Data Analyst, Backend Developer, Digital Marketing..." rows={3} />
              </label>
              <label>
                Cach hoc mong muon
                <textarea value={form.learning_preferences} onChange={(event) => updateField("learning_preferences", event.target.value)} placeholder="Vi du: can khoa thuc hanh, de bat dau, co project cuoi khoa..." rows={3} />
              </label>
            </>
          )}

          <label className="checkbox-label">
            <input type="checkbox" checked={form.consent_confirmed} onChange={(event) => updateField("consent_confirmed", event.target.checked)} />
            Toi xac nhan noi dung duoc phep su dung va khong chua thong tin nhay cam khong can thiet.
          </label>
          {error && <p className="error">{error}</p>}
          <button className="button" type="submit" disabled={submitting}>
            {submitting ? "Dang xu ly..." : mode === "file" ? "Upload ho so" : "Tao ho so goi y"}
          </button>
        </form>
      </section>
    </main>
  );
}
