import { useEffect, useState } from "react";
import axiosClient, { getApiError } from "../api/axiosClient";

export default function AdminEvaluationPage() {
  const [summary, setSummary] = useState(null);
  const [studentDocuments, setStudentDocuments] = useState([]);
  const [courseDocuments, setCourseDocuments] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState({});
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadData() {
    setError("");
    try {
      const [summaryResponse, studentResponse, courseResponse] = await Promise.all([
        axiosClient.get("/admin/evaluation/summary"),
        axiosClient.get("/admin/student-documents"),
        axiosClient.get("/admin/course-documents"),
      ]);
      setSummary(summaryResponse.data);
      setStudentDocuments(studentResponse.data);
      setCourseDocuments(courseResponse.data.filter((doc) => doc.is_active));
    } catch (err) {
      setError(getApiError(err));
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function saveGroundTruth(studentDocumentId) {
    const courseId = selectedCourse[studentDocumentId];
    if (!courseId) return;
    setError("");
    setMessage("");
    try {
      await axiosClient.put(`/admin/student-documents/${studentDocumentId}/ground-truth`, {
        course_document_id: courseId,
      });
      setMessage("Đã lưu ground truth.");
      loadData();
    } catch (err) {
      setError(getApiError(err));
    }
  }

  return (
    <main className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Evaluation</p>
          <h1>Đánh giá thuật toán</h1>
        </div>
      </div>
      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}
      {summary && (
        <section className="feature-grid metrics">
          <div><h2>{summary.total_labeled_documents}</h2><p>Labeled documents</p></div>
          <div><h2>{summary.top1_accuracy == null ? "N/A" : `${(summary.top1_accuracy * 100).toFixed(2)}%`}</h2><p>Top-1 Accuracy</p></div>
          <div><h2>{summary.hit_rate_at_3 == null ? "N/A" : `${(summary.hit_rate_at_3 * 100).toFixed(2)}%`}</h2><p>Hit Rate@3</p></div>
        </section>
      )}
      {summary?.message && <p className="muted-text">{summary.message}</p>}
      <section className="panel">
        <h2>Gán ground truth</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Alias</th>
                <th>File</th>
                <th>Status</th>
                <th>Ground truth</th>
              </tr>
            </thead>
            <tbody>
              {studentDocuments.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.student_alias}</td>
                  <td>{doc.original_filename}</td>
                  <td>{doc.extraction_status}</td>
                  <td className="ground-truth-cell">
                    <select value={selectedCourse[doc.id] || doc.ground_truth_course_id || ""} onChange={(event) => setSelectedCourse((current) => ({ ...current, [doc.id]: event.target.value }))}>
                      <option value="">Chọn khóa học thật phù hợp</option>
                      {courseDocuments.map((course) => <option key={course.id} value={course.id}>{course.course_title}</option>)}
                    </select>
                    <button className="button" type="button" onClick={() => saveGroundTruth(doc.id)}>Lưu</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      {summary?.rows?.length > 0 && (
        <section className="panel detail-panel">
          <h2>Kết quả từng tài liệu</h2>
          <pre>{JSON.stringify(summary.rows, null, 2)}</pre>
        </section>
      )}
    </main>
  );
}
