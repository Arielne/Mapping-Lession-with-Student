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
      setMessage("Da tao danh sach goi y khoa hoc phu hop.");
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
          <p className="eyebrow">Goi y khoa hoc</p>
          <h1>Khoa hoc phu hop voi CV / ho so hoc vien</h1>
        </div>
        <button className="button" type="button" onClick={runMatching} disabled={running}>
          {running ? "Dang phan tich..." : "Tao goi y"}
        </button>
      </div>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
      {!result && <p>Chua co ket qua. Can co tai lieu khoa hoc that va CV/ho so hoc vien da trich xuat duoc text.</p>}
      {result && (
        <section className="panel">
          <div className="match-meta">
            <p><strong>Phuong phap:</strong> {result.algorithm_name}</p>
            <p><strong>So dac trung n-gram:</strong> {result.vocabulary_size}</p>
            <p><strong>Thoi gian xu ly:</strong> {result.processing_time_ms.toFixed(2)} ms</p>
          </div>
          <div className="match-list">
            {recommendations.map((item) => (
              <article className="match-item" key={item.course_document_id}>
                <h2>#{item.rank} {item.course_title}</h2>
                <p><strong>Muc do phu hop:</strong> {formatScore(item.similarity_score ?? item.score ?? item.match_score)}</p>
                <p><strong>Thuat toan:</strong> {item.algorithm || item.algorithm_name}</p>
                <p><strong>Trang thai:</strong> {item.is_recommended ? "Duoc goi y" : "Diem tuong dong thap"}</p>
                <p><strong>Ly do goi y:</strong> {item.explanation || item.recommendation_reason}</p>
                <div className="keyword-section">
                  <strong>Ky nang trung:</strong>
                  <div className="tags compact-tags">
                    {(item.matched_keywords?.length ? item.matched_keywords : item.relevant_skills || []).map((skill) => <span key={skill}>{skill}</span>)}
                    {!(item.matched_keywords?.length || item.relevant_skills?.length) && <span>Chua phat hien ro</span>}
                  </div>
                </div>
                <div className="keyword-section">
                  <strong>Ky nang nen hoc them:</strong>
                  <div className="tags compact-tags missing-tags">
                    {(item.missing_keywords?.length ? item.missing_keywords : item.suggested_learning_outcomes || []).map((skill) => <span key={skill}>{skill}</span>)}
                    {!(item.missing_keywords?.length || item.suggested_learning_outcomes?.length) && <span>Khong co de xuat bo sung</span>}
                  </div>
                </div>
                <details>
                  <summary>Chi tiet ky thuat</summary>
                  <div className="score-breakdown">
                    <span>Binary Jaccard n-gram: {formatScore(item.score_breakdown?.binary_jaccard_ngram_score ?? item.similarity_score)}</span>
                    <span>Keyword overlap de giai thich: {formatScore(item.score_breakdown?.keyword_overlap_score)}</span>
                  </div>
                  <p><strong>Tu khoa/noi dung lien quan:</strong> {item.matched_terms.length ? item.matched_terms.join(", ") : "Khong co"}</p>
                  {item.created_at && <p><strong>Thoi diem tao:</strong> {new Date(item.created_at).toLocaleString()}</p>}
                </details>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
