import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axiosClient, { getApiError } from "../api/axiosClient";

export default function MatchResultsPage() {
  const { id } = useParams();
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [running, setRunning] = useState(false);

  async function loadExisting() {
    setError("");
    try {
      const response = await axiosClient.get(`/matching/student-documents/${id}/results`);
      setResult(response.data);
    } catch (err) {
      if (err?.response?.status !== 404) setError(getApiError(err));
    }
  }

  useEffect(() => {
    loadExisting();
  }, [id]);

  async function runMatching() {
    setRunning(true);
    setError("");
    setMessage("");
    try {
      const response = await axiosClient.post(`/matching/student-documents/${id}`, null, { params: { top_k: 3 } });
      setResult(response.data);
      setMessage("Đã tạo danh sách gợi ý khóa học phù hợp.");
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setRunning(false);
    }
  }

  function formatScore(value) {
    return `${((value || 0) * 100).toFixed(1)}%`;
  }

  const recommendations = result?.recommendations?.length ? result.recommendations : result?.results || [];

  return (
    <main className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Gợi ý khóa học</p>
          <h1>Khóa học phù hợp với CV / hồ sơ học viên</h1>
        </div>
        <button className="button" type="button" onClick={runMatching} disabled={running}>
          {running ? "Đang phân tích..." : "Tạo gợi ý"}
        </button>
      </div>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
      {!result && <p>Chưa có kết quả. Cần có tài liệu khóa học thật và CV/hồ sơ học viên đã trích xuất được text.</p>}
      {result && (
        <section className="panel">
          <div className="match-meta">
            <p><strong>Phương pháp:</strong> {result.algorithm_name}</p>
            <p><strong>Số đặc trưng văn bản:</strong> {result.vocabulary_size}</p>
            <p><strong>Thời gian xử lý:</strong> {result.processing_time_ms.toFixed(2)} ms</p>
          </div>
          <div className="match-list">
            {recommendations.map((item) => (
              <article className="match-item" key={item.course_document_id}>
                <h2>#{item.rank} {item.course_title}</h2>
                <p><strong>Mức độ phù hợp:</strong> {((item.score || item.match_score || 0) * 100).toFixed(2)}%</p>
                <p><strong>Lý do gợi ý:</strong> {item.explanation || item.recommendation_reason}</p>
                <div className="keyword-section">
                  <strong>Kỹ năng trùng:</strong>
                  <div className="tags compact-tags">
                    {(item.matched_keywords?.length ? item.matched_keywords : item.relevant_skills || []).map((skill) => <span key={skill}>{skill}</span>)}
                    {!(item.matched_keywords?.length || item.relevant_skills?.length) && <span>Chưa phát hiện rõ</span>}
                  </div>
                </div>
                <div className="keyword-section">
                  <strong>Kỹ năng nên học thêm:</strong>
                  <div className="tags compact-tags missing-tags">
                    {(item.missing_keywords?.length ? item.missing_keywords : item.suggested_learning_outcomes || []).map((skill) => <span key={skill}>{skill}</span>)}
                    {!(item.missing_keywords?.length || item.suggested_learning_outcomes?.length) && <span>Không có đề xuất bổ sung</span>}
                  </div>
                </div>
                <details>
                  <summary>Chi tiết kỹ thuật</summary>
                  <div className="score-breakdown">
                    <span>TF-IDF cosine: {formatScore(item.score_breakdown?.tfidf_cosine_score ?? item.score_breakdown?.text_similarity_score)}</span>
                    <span>Keyword overlap: {formatScore(item.score_breakdown?.keyword_overlap_score)}</span>
                  </div>
                  <p><strong>Từ khóa/nội dung liên quan:</strong> {item.matched_terms.length ? item.matched_terms.join(", ") : "Không có"}</p>
                </details>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
