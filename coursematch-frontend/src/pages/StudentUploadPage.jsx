import { useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosClient, { getApiError } from "../api/axiosClient";
import { useAuth } from "../context/AuthContext";

const allowedFilePattern = /\.(pdf|docx)$/i;
const maxFileSize = 10 * 1024 * 1024;
const minDescriptionLength = 20;

const text = {
  title: "T\u1ea3i l\u00ean h\u1ed3 s\u01a1 h\u1ecdc t\u1eadp",
  description: "T\u1ea3i l\u00ean CV ho\u1eb7c nhu c\u1ea7u h\u1ecdc t\u1eadp \u0111\u1ec3 CourseMatch ph\u00e2n t\u00edch k\u1ef9 n\u0103ng, m\u1ee5c ti\u00eau v\u00e0 \u0111\u1ec1 xu\u1ea5t kh\u00f3a h\u1ecdc ph\u00f9 h\u1ee3p.",
  warning: "Ch\u1ec9 h\u1ed7 tr\u1ee3 file PDF ho\u1eb7c DOCX. Vui l\u00f2ng \u1ea9n c\u00e1c th\u00f4ng tin nh\u1ea1y c\u1ea3m tr\u01b0\u1edbc khi t\u1ea3i l\u00ean.",
  studentCode: "M\u00e3 h\u1ecdc vi\u00ean",
  studentCodeHelp: "M\u00e3 h\u1ecdc vi\u00ean \u0111\u01b0\u1ee3c l\u1ea5y t\u1eeb t\u00e0i kho\u1ea3n \u0111\u0103ng nh\u1eadp.",
  profileType: "Lo\u1ea1i h\u1ed3 s\u01a1",
  cv: "CV c\u00e1 nh\u00e2n",
  need: "Nhu c\u1ea7u h\u1ecdc t\u1eadp",
  fileLabel: "File t\u1ea3i l\u00ean",
  needLabel: "M\u00f4 t\u1ea3 nhu c\u1ea7u h\u1ecdc t\u1eadp",
  needPlaceholder: "V\u00ed d\u1ee5: Em mu\u1ed1n h\u1ecdc ph\u00e2n t\u00edch d\u1eef li\u1ec7u, \u0111ang bi\u1ebft Excel c\u01a1 b\u1ea3n, mu\u1ed1n t\u00ecm m\u00f4n ph\u00f9 h\u1ee3p \u0111\u1ec3 \u0111i theo h\u01b0\u1edbng Data Analyst.",
  needHelp: "H\u00e3y vi\u1ebft m\u1ee5c ti\u00eau, s\u1edf th\u00edch, n\u1ec1n t\u1ea3ng hi\u1ec7n c\u00f3 ho\u1eb7c h\u01b0\u1edbng ngh\u1ec1 nghi\u1ec7p mong mu\u1ed1n.",
  dropTitle: "K\u00e9o th\u1ea3 file v\u00e0o \u0111\u00e2y ho\u1eb7c b\u1ea5m \u0111\u1ec3 ch\u1ecdn file",
  dropHelp: "H\u1ed7 tr\u1ee3 PDF, DOCX. Dung l\u01b0\u1ee3ng t\u1ed1i \u0111a 10MB.",
  privacy: "T\u00f4i x\u00e1c nh\u1eadn file ho\u1eb7c m\u00f4 t\u1ea3 \u0111\u00e3 \u0111\u01b0\u1ee3c ki\u1ec3m tra v\u00e0 kh\u00f4ng ch\u1ee9a th\u00f4ng tin nh\u1ea1y c\u1ea3m kh\u00f4ng c\u1ea7n thi\u1ebft.",
  submit: "G\u1eedi h\u1ed3 s\u01a1 ph\u00e2n t\u00edch",
  processing: "\u0110ang x\u1eed l\u00fd...",
  chooseFile: "Vui l\u00f2ng ch\u1ecdn file PDF ho\u1eb7c DOCX.",
  invalidFile: "File kh\u00f4ng h\u1ee3p l\u1ec7. Ch\u1ec9 h\u1ed7 tr\u1ee3 PDF ho\u1eb7c DOCX.",
  fileTooLarge: "File v\u01b0\u1ee3t qu\u00e1 dung l\u01b0\u1ee3ng t\u1ed1i \u0111a 10MB.",
  needRequired: "Vui l\u00f2ng nh\u1eadp m\u00f4 t\u1ea3 nhu c\u1ea7u h\u1ecdc t\u1eadp.",
  consent: "Vui l\u00f2ng x\u00e1c nh\u1eadn quy\u1ec1n ri\u00eang t\u01b0 tr\u01b0\u1edbc khi t\u1ea3i l\u00ean.",
  success: "H\u1ed3 s\u01a1 \u0111\u00e3 \u0111\u01b0\u1ee3c t\u1ea3i l\u00ean th\u00e0nh c\u00f4ng.",
  failed: "Kh\u00f4ng th\u1ec3 t\u1ea3i h\u1ed3 s\u01a1. Vui l\u00f2ng th\u1eed l\u1ea1i.",
  statusLabel: "Tr\u1ea1ng th\u00e1i x\u1eed l\u00fd h\u1ed3 s\u01a1",
};

const statusSteps = [
  { key: "uploading", label: "\u0110ang t\u1ea3i l\u00ean" },
  { key: "analyzing", label: "\u0110ang ph\u00e2n t\u00edch h\u1ed3 s\u01a1" },
  { key: "success", label: "Ph\u00e2n t\u00edch th\u00e0nh c\u00f4ng" },
  { key: "error", label: "L\u1ed7i ph\u00e2n t\u00edch" },
];

export default function StudentUploadPage() {
  const { user } = useAuth();
  const [form, setForm] = useState({
    document_purpose: "anonymized_cv",
    consent_confirmed: false,
    file: null,
    learning_description: "",
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState("idle");
  const [dragActive, setDragActive] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const studentAlias = useMemo(() => user?.email || user?.id || "", [user]);
  const isLearningNeed = form.document_purpose === "learning_need";

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function setSelectedFile(file) {
    setError("");
    setMessage("");
    setStatus("idle");
    updateField("file", file || null);
  }

  function validateForm() {
    if (isLearningNeed) {
      if (form.learning_description.trim().length < minDescriptionLength) return text.needRequired;
    } else {
      if (!form.file) return text.chooseFile;
      if (!allowedFilePattern.test(form.file.name)) return text.invalidFile;
      if (form.file.size > maxFileSize) return text.fileTooLarge;
    }
    if (!form.consent_confirmed) return text.consent;
    return "";
  }

  async function submitCvFile() {
    const data = new FormData();
    data.append("student_alias", studentAlias);
    data.append("document_purpose", form.document_purpose);
    data.append("consent_confirmed", String(form.consent_confirmed));
    data.append("file", form.file);
    return axiosClient.post("/student/documents/upload", data, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  }

  async function submitLearningNeed() {
    return axiosClient.post("/student/documents/profile-text", {
      student_alias: studentAlias,
      current_skills: "",
      interests: "",
      career_goals: "",
      learning_preferences: form.learning_description.trim(),
      consent_confirmed: form.consent_confirmed,
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);
    setStatus("uploading");

    try {
      const response = isLearningNeed ? await submitLearningNeed() : await submitCvFile();
      setStatus("analyzing");
      setTimeout(() => {
        setStatus("success");
        setMessage(text.success);
        setTimeout(() => navigate(`/student/documents/${response.data.id}/matches`), 650);
      }, 350);
    } catch (err) {
      setStatus("error");
      setError(getApiError(err) || text.failed);
      setSubmitting(false);
    }
  }

  function handleProfileTypeChange(event) {
    updateField("document_purpose", event.target.value);
    setError("");
    setMessage("");
    setStatus("idle");
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragActive(false);
    if (!isLearningNeed) setSelectedFile(event.dataTransfer.files?.[0] || null);
  }

  function handleDrag(event, active) {
    event.preventDefault();
    setDragActive(active);
  }

  return (
    <main className="page student-upload-page">
      <section className="student-upload-card panel">
        <div className="student-upload-heading">
          <p className="eyebrow">CourseMatch</p>
          <h1>{text.title}</h1>
          <p>{text.description}</p>
        </div>

        <div className="upload-warning" role="note">
          <span aria-hidden="true">!</span>
          <p>{text.warning}</p>
        </div>

        <form className="form student-upload-form" onSubmit={handleSubmit}>
          <label>
            {text.studentCode}
            <input value={studentAlias} readOnly aria-readonly="true" />
            <small>{text.studentCodeHelp}</small>
          </label>

          <label>
            {text.profileType}
            <select value={form.document_purpose} onChange={handleProfileTypeChange}>
              <option value="anonymized_cv">{text.cv}</option>
              <option value="learning_need">{text.need}</option>
            </select>
          </label>

          {isLearningNeed ? (
            <label className="learning-need-field">
              {text.needLabel}
              <textarea
                value={form.learning_description}
                rows={7}
                placeholder={text.needPlaceholder}
                onChange={(event) => updateField("learning_description", event.target.value)}
              />
              <small>{text.needHelp}</small>
            </label>
          ) : (
            <div className="upload-field-group">
              <span className="field-label">{text.fileLabel}</span>
              <button
                className={dragActive ? "file-dropzone active" : "file-dropzone"}
                type="button"
                onClick={() => fileInputRef.current?.click()}
                onDragEnter={(event) => handleDrag(event, true)}
                onDragOver={(event) => handleDrag(event, true)}
                onDragLeave={(event) => handleDrag(event, false)}
                onDrop={handleDrop}
              >
                <span className="file-dropzone-icon" aria-hidden="true">UP</span>
                <strong>{text.dropTitle}</strong>
                <small>{text.dropHelp}</small>
                {form.file && <em>{form.file.name}</em>}
              </button>
              <input
                ref={fileInputRef}
                className="sr-only-file"
                type="file"
                accept=".pdf,.docx"
                onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
              />
            </div>
          )}

          <label className="checkbox-label privacy-check">
            <input type="checkbox" checked={form.consent_confirmed} onChange={(event) => updateField("consent_confirmed", event.target.checked)} />
            {text.privacy}
          </label>

          {status !== "idle" && (
            <div className="upload-status-list" aria-label={text.statusLabel}>
              {statusSteps.map((step) => (
                <span className={status === step.key ? "active" : status === "success" && step.key !== "error" ? "done" : ""} key={step.key}>
                  {step.label}
                </span>
              ))}
            </div>
          )}

          {error && <p className="error">{error}</p>}
          {message && <p className="success">{message}</p>}

          <button className="button upload-submit-button" type="submit" disabled={submitting}>
            {submitting ? text.processing : text.submit}
          </button>
        </form>
      </section>
    </main>
  );
}
