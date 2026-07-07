import { useEffect, useMemo, useState } from "react";
import axiosClient, { getApiError } from "../api/axiosClient";

const emptyForm = {
  course_title: "",
  course_description: "",
  is_active: true,
  file: null,
};

const visibilityFilters = [
  { value: "all", label: "Tất cả" },
  { value: "visible", label: "Đang hiển thị" },
  { value: "hidden", label: "Đang ẩn" },
];


export default function AdminCourseDocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState(null);
  const [viewing, setViewing] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  const [search, setSearch] = useState("");
  const [visibilityFilter, setVisibilityFilter] = useState("all");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [fileInputKey, setFileInputKey] = useState(0);

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


  const filteredDocuments = useMemo(() => {
    const keyword = search.trim().toLowerCase();
    return documents.filter((doc) => {
      const haystack = `${doc.course_title} ${doc.original_filename} ${doc.course_description || ""}`.toLowerCase();
      const matchesSearch = !keyword || haystack.includes(keyword);
      const matchesVisibility = visibilityFilter === "all"
        || (visibilityFilter === "visible" && doc.is_active !== false)
        || (visibilityFilter === "hidden" && doc.is_active === false);
      return matchesSearch && matchesVisibility;
    });
  }, [documents, search, visibilityFilter]);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function resetUploadForm() {
    setForm(emptyForm);
    setFileInputKey((current) => current + 1);
  }

  function openCreate() {
    setEditing(null);
    setViewing(null);
    setShowUpload(true);
    setMessage("");
    setError("");
  }

  function startEdit(doc) {
    setShowUpload(false);
    setViewing(null);
    setEditing({
      id: doc.id,
      course_title: doc.course_title || "",
      course_description: doc.course_description || "",
      is_active: doc.is_active !== false,
    });
    setMessage("");
    setError("");
  }

  async function viewDetail(doc) {
    setError("");
    try {
      const response = await axiosClient.get(`/admin/course-documents/${doc.id}`);
      setViewing(response.data);
      setShowUpload(false);
      setEditing(null);
    } catch (err) {
      setError(getApiError(err));
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    if (!form.file || !/\.(pdf|docx)$/i.test(form.file.name)) {
      setError("Chỉ chấp nhận file PDF hoặc DOCX.");
      return;
    }

    const data = new FormData();
    data.append("course_title", form.course_title);
    data.append("source_name", "Tài liệu khóa học");
    data.append("course_description", form.course_description);
    data.append("is_active", String(form.is_active));
    data.append("file", form.file);

    setSubmitting(true);
    try {
      await axiosClient.post("/admin/course-documents/upload", data, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMessage("Tài liệu đã được thêm thành công.");
      resetUploadForm();
      setShowUpload(false);
      await loadDocuments();
    } catch (err) {
      setError(getApiError(err) || "Không thể xử lý tài liệu. Vui lòng thử lại.");
    } finally {
      setSubmitting(false);
    }
  }

  async function saveEdit(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    if (!editing?.course_title.trim()) {
      setError("Tên khóa học không được rỗng.");
      return;
    }

    setSubmitting(true);
    try {
      await axiosClient.put(`/admin/course-documents/${editing.id}`, {
        course_title: editing.course_title,
        source_name: "Tài liệu khóa học",
        course_description: editing.course_description,
        is_active: editing.is_active,
      });
      setMessage("Đã cập nhật thông tin tài liệu.");
      setEditing(null);
      await loadDocuments();
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function toggleVisible(doc) {
    setError("");
    setMessage("");
    try {
      const nextVisible = doc.is_active === false;
      await axiosClient.put(`/admin/course-documents/${doc.id}`, { is_active: nextVisible });
      setMessage(nextVisible ? "Đã cập nhật trạng thái hiển thị của tài liệu." : "Tài liệu đã được ẩn khỏi kết quả tìm kiếm của sinh viên.");
      await loadDocuments();
    } catch (err) {
      setError(getApiError(err));
    }
  }

  async function softDelete(doc) {
    const confirmed = window.confirm(`Xóa tài liệu "${doc.course_title}" khỏi danh sách hiển thị?`);
    if (!confirmed) return;

    setError("");
    setMessage("");
    try {
      await axiosClient.delete(`/admin/course-documents/${doc.id}`);
      setMessage("Tài liệu đã được ẩn khỏi kết quả tìm kiếm của sinh viên.");
      await loadDocuments();
    } catch (err) {
      setError(getApiError(err));
    }
  }

  function renderEditor() {
    if (!showUpload && !editing) return null;
    const isEditing = Boolean(editing);
    const data = isEditing ? editing : form;
    const update = isEditing
      ? (field, value) => setEditing((current) => ({ ...current, [field]: value }))
      : updateField;

    return (
      <div className="modal-backdrop" role="presentation">
        <section className="panel admin-editor-modal" role="dialog" aria-modal="true" aria-label={isEditing ? "Sửa tài liệu khóa học" : "Thêm tài liệu khóa học"}>
          <form className="form" onSubmit={isEditing ? saveEdit : handleSubmit}>
            <div className="form-heading-row">
              <div>
                <p className="eyebrow">{isEditing ? "Chỉnh sửa" : "Tải lên"}</p>
                <h2>{isEditing ? "Sửa tài liệu khóa học" : "Thêm tài liệu khóa học"}</h2>
              </div>
              <button className="button ghost" type="button" onClick={() => { setShowUpload(false); setEditing(null); resetUploadForm(); }}>Đóng</button>
            </div>
            <label>
              Tên khóa học
              <input value={data.course_title} onChange={(event) => update("course_title", event.target.value)} required />
            </label>
            <label>
              Mô tả ngắn
              <textarea value={data.course_description} onChange={(event) => update("course_description", event.target.value)} rows="3" placeholder="Tóm tắt nội dung hoặc mục tiêu của khóa học" />
            </label>
            {!isEditing && (
              <label>
                File PDF/DOCX
                <input key={fileInputKey} type="file" accept=".pdf,.docx" onChange={(event) => update("file", event.target.files?.[0] || null)} required />
              </label>
            )}
            <label className="checkbox-label">
              <input type="checkbox" checked={data.is_active} onChange={(event) => update("is_active", event.target.checked)} />
              Hiển thị cho sinh viên tìm kiếm
            </label>
            {!isEditing && <p className="form-note">Sau khi tải lên, hệ thống sẽ tự động phân tích nội dung và nhận diện kỹ năng liên quan.</p>}
            <button className="button" type="submit" disabled={submitting}>{submitting ? "Đang lưu..." : isEditing ? "Lưu thay đổi" : "Tải lên tài liệu"}</button>
          </form>
        </section>
      </div>
    );
  }

  return (
    <main className="page admin-doc-page">
      <section className="admin-doc-header compact">
        <div>
          <p className="eyebrow">Admin</p>
          <h1>Tài liệu khóa học</h1>
          <p>Quản lý tài liệu khóa học để sinh viên có thể tìm thấy các môn học phù hợp.</p>
        </div>
        <button className="button admin-add-button" type="button" onClick={openCreate}>
          <span aria-hidden="true">+</span>
          Thêm tài liệu
        </button>
      </section>


      {message && <p className="success compact-alert">{message}</p>}
      {error && <p className="error compact-alert">{error}</p>}

      <section className="panel admin-doc-table-panel">
        <div className="admin-list-toolbar dashboard-toolbar">
          <div>
            <h2>Danh sách tài liệu khóa học</h2>
            <p>{filteredDocuments.length} tài liệu phù hợp bộ lọc</p>
          </div>
          <div className="admin-filter-row">
            <label className="search-field">
              <span aria-hidden="true">⌕</span>
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Tim theo ten khoa hoc, ten file..." />
            </label>
            <select value={visibilityFilter} onChange={(event) => setVisibilityFilter(event.target.value)} aria-label="Lọc trạng thái hiển thị">
              {visibilityFilters.map((option) => <option value={option.value} key={option.value}>{option.label}</option>)}
            </select>
          </div>
        </div>

        {loading ? <p>Đang tải...</p> : (
          <div className="table-wrap admin-doc-table-wrap">
            <table className="admin-doc-table">
              <thead>
                <tr>
                  <th>STT</th>
                  <th>Tài liệu / Khóa học</th>
                  <th>Trạng thái hiển thị</th>
                  <th>Hành động</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocuments.map((doc, index) => {
                  return (
                    <tr key={doc.id}>
                      <td data-label="STT">{index + 1}</td>
                      <td data-label="Tài liệu / Khóa học">
                        <div className="course-doc-title-cell">
                          <span className="pdf-chip">PDF</span>
                          <div>
                            <strong>{doc.course_title}</strong>
                            <span className="doc-file-name">{doc.original_filename}</span>
                            {doc.course_description && <span className="doc-description-line">{doc.course_description}</span>}
                          </div>
                        </div>
                      </td>
                      <td data-label="Trạng thái hiển thị">
                        <button className={doc.is_active === false ? "switch-toggle" : "switch-toggle active"} type="button" onClick={() => toggleVisible(doc)} aria-label="Đổi trạng thái hiển thị">
                          <span />
                          {doc.is_active === false ? "Đang ẩn" : "Đang hiển thị"}
                        </button>
                      </td>
                      <td data-label="Hành động" className="table-actions doc-actions">
                        <button className="button ghost" type="button" onClick={() => viewDetail(doc)}>Xem</button>
                        <button className="button ghost" type="button" onClick={() => startEdit(doc)}>Sửa</button>
                        <button className="button ghost" type="button" onClick={() => toggleVisible(doc)}>{doc.is_active === false ? "Hiện" : "Ẩn"}</button>
                        <button className="button danger subtle-danger" type="button" onClick={() => softDelete(doc)}>Xóa</button>
                      </td>
                    </tr>
                  );
                })}
                {!filteredDocuments.length && (
                  <tr>
                    <td colSpan="4" className="empty-table-cell">Không có tài liệu phù hợp.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {viewing && (
        <div className="modal-backdrop" role="presentation">
          <section className="panel admin-editor-modal detail-modal" role="dialog" aria-modal="true" aria-label="Chi tiết tài liệu khóa học">
            <div className="form-heading-row">
              <div>
                <p className="eyebrow">Chi tiết</p>
                <h2>{viewing.course_title}</h2>
              </div>
              <button className="button ghost" type="button" onClick={() => setViewing(null)}>Đóng</button>
            </div>
            <p className="muted">{viewing.original_filename}</p>
            {viewing.course_description && <p>{viewing.course_description}</p>}
            <pre>{viewing.text_preview || viewing.extracted_text || "Không có nội dung trích xuất."}</pre>
          </section>
        </div>
      )}

      {renderEditor()}
    </main>
  );
}
