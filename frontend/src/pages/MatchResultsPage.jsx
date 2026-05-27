import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axiosClient from "../api/axiosClient";

export default function MatchResultsPage() {
  const { studentDocumentId } = useParams();
  const [results, setResults] = useState([]);
  const [selected, setSelected] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    axiosClient
      .get(`/matching/top/${studentDocumentId}?k=3`)
      .then(({ data }) => setResults(data.results || []))
      .catch((err) => setError(err.response?.data?.detail || "Cannot load results"));
  }, [studentDocumentId]);

  function toggle(courseId) {
    setSelected((current) =>
      current.includes(courseId) ? current.filter((id) => id !== courseId) : [...current, courseId]
    );
  }

  async function saveLabels() {
    setMessage("");
    setError("");
    try {
      await axiosClient.post("/evaluation/labels", {
        student_document_id: studentDocumentId,
        validated_course_ids: selected,
        label_source: "student_selected",
      });
      setMessage("Labels saved");
    } catch (err) {
      setError(err.response?.data?.detail || "Cannot save labels");
    }
  }

  return (
    <main className="page">
      <section className="page-head">
        <h1>Match Results</h1>
      </section>
      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}
      <div className="list">
        {results.map((result) => (
          <article className="row" key={result.course_id}>
            <div>
              <strong>#{result.rank} {result.course_title}</strong>
              <p>Score: {(result.match_score * 100).toFixed(1)}%</p>
              <div className="chips">
                {(result.matched_keywords || []).map((keyword) => (
                  <span key={keyword}>{keyword}</span>
                ))}
              </div>
            </div>
            <label className="check">
              <input
                type="checkbox"
                checked={selected.includes(result.course_id)}
                onChange={() => toggle(result.course_id)}
              />
              Validated
            </label>
          </article>
        ))}
      </div>
      <button className="primary" disabled={selected.length === 0} onClick={saveLabels}>
        Save Labels
      </button>
    </main>
  );
}

