import { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";

export default function EvaluationPage() {
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    axiosClient
      .get("/evaluation/report")
      .then(({ data }) => setReport(data))
      .catch((err) => setError(err.response?.data?.detail || "Cannot load evaluation"));
  }, []);

  const summary = report?.summary;

  return (
    <main className="page">
      <section className="page-head">
        <h1>Evaluation</h1>
      </section>
      {error && <p className="error">{error}</p>}
      {summary && (
        <section className="metrics">
          <div>
            <span>Total labeled</span>
            <strong>{summary.total_labeled_students}</strong>
          </div>
          <div>
            <span>Top-1 Accuracy</span>
            <strong>{(summary.top1_accuracy * 100).toFixed(1)}%</strong>
          </div>
          <div>
            <span>Hit Rate@3</span>
            <strong>{(summary.hit_rate_at_3 * 100).toFixed(1)}%</strong>
          </div>
          <div>
            <span>Avg Time</span>
            <strong>{summary.avg_processing_time_ms} ms</strong>
          </div>
        </section>
      )}
      <div className="list">
        {(report?.per_student || []).map((item) => (
          <article className="row" key={item.student_document_id}>
            <div>
              <strong>{item.student_code || item.student_document_id}</strong>
              <p>Top-1: {item.top1_predicted_course || "No result"}</p>
              <p>Validated: {item.validated_courses.join(", ")}</p>
            </div>
            <span className={`status ${item.in_top3 ? "processed" : "failed"}`}>
              {item.in_top3 ? "hit@3" : "miss"}
            </span>
          </article>
        ))}
      </div>
    </main>
  );
}

