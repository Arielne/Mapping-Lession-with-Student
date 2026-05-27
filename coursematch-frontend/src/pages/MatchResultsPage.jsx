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
      setMessage("Đã chạy matching.");
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setRunning(false);
    }
  }

  return (
    <main className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Matching</p>
          <h1>Kết quả đối sánh</h1>
        </div>
        <button className="button" type="button" onClick={runMatching} disabled={running}>
          {running ? "Đang chạy..." : "Chạy matching"}
        </button>
      </div>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
      {!result && <p>Chưa có kết quả. Chỉ chạy được khi đã có tài liệu khóa học thật và tài liệu student có text.</p>}
      {result && (
        <section className="panel">
          <p><strong>Algorithm:</strong> {result.algorithm_name}</p>
          <p><strong>Vocabulary size:</strong> {result.vocabulary_size}</p>
          <p><strong>Processing time:</strong> {result.processing_time_ms.toFixed(2)} ms</p>
          <div className="match-list">
            {result.results.map((item) => (
              <article className="match-item" key={item.course_document_id}>
                <h2>#{item.rank} {item.course_title}</h2>
                <p><strong>Score:</strong> {(item.score * 100).toFixed(2)}%</p>
                <p><strong>Matched terms:</strong> {item.matched_terms.length ? item.matched_terms.join(", ") : "Không có"}</p>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
