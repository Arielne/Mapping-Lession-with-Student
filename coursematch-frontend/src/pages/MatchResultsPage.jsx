import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import axiosClient, { getApiError } from "../api/axiosClient";

const MIN_VISIBLE_SCORE = 0.75;

const text = {
  eyebrow: "G\u1ee3i \u00fd kh\u00f3a h\u1ecdc",
  title: "M\u00f4n h\u1ecdc ph\u00f9 h\u1ee3p v\u1edbi b\u1ea1n",
  back: "Quay l\u1ea1i h\u1ed3 s\u01a1",
  create: "T\u1ea1o g\u1ee3i \u00fd",
  creating: "\u0110ang ph\u00e2n t\u00edch...",
  emptyTitle: "Ch\u01b0a c\u00f3 m\u00f4n h\u1ecdc \u0111\u1ea1t m\u1ee9c ph\u00f9 h\u1ee3p 75%",
  emptyDesc: "H\u00e3y b\u1ed5 sung th\u00eam k\u1ef9 n\u0103ng, s\u1edf th\u00edch ho\u1eb7c m\u1ee5c ti\u00eau h\u1ecdc t\u1eadp \u0111\u1ec3 h\u1ec7 th\u1ed1ng g\u1ee3i \u00fd ch\u00ednh x\u00e1c h\u01a1n.",
  noResult: "Ch\u01b0a c\u00f3 k\u1ebft qu\u1ea3. H\u00e3y b\u1ea5m T\u1ea1o g\u1ee3i \u00fd sau khi c\u00f3 CV ho\u1eb7c h\u1ed3 s\u01a1 nhu c\u1ea7u h\u1ecdc t\u1eadp.",
  saved: "\u0110\u00e3 th\u00eam kh\u00f3a h\u1ecdc v\u00e0o danh s\u00e1ch y\u00eau th\u00edch.",
  removed: "\u0110\u00e3 b\u1ecf kh\u00f3a h\u1ecdc kh\u1ecfi danh s\u00e1ch y\u00eau th\u00edch.",
  generated: "\u0110\u00e3 t\u1ea1o danh s\u00e1ch g\u1ee3i \u00fd kh\u00f3a h\u1ecdc ph\u00f9 h\u1ee3p.",
  results: "k\u1ebft qu\u1ea3",
};

export default function MatchResultsPage() {
  const { id } = useParams();
  const [result, setResult] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [running, setRunning] = useState(false);

  async function loadFavorites() {
    try {
      const response = await axiosClient.get("/student/favorites/me");
      setFavorites(response.data);
    } catch (err) {
      setError(getApiError(err));
    }
  }

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
    loadFavorites();
  }, [id]);

  async function runMatching() {
    setRunning(true);
    setError("");
    setMessage("");
    try {
      const response = await axiosClient.post(`/matching/student-documents/${id}`, null, { params: { top_k: 8 } });
      setResult(response.data);
      setMessage(text.generated);
      await loadFavorites();
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setRunning(false);
    }
  }

  function formatScore(value) {
    return `${((value || 0) * 100).toFixed(1)}%`;
  }

  function displayScore(item) {
    return item.match_score ?? item.similarity_score ?? item.score ?? 0;
  }

  function shortDescription(item) {
    return item.course_summary || item.text_preview || item.recommendation_reason || item.explanation || "M\u00f4n h\u1ecdc n\u00e0y ph\u00f9 h\u1ee3p v\u1edbi h\u1ed3 s\u01a1 k\u1ef9 n\u0103ng v\u00e0 m\u1ee5c ti\u00eau h\u1ecdc t\u1eadp c\u1ee7a b\u1ea1n.";
  }

  function favoriteFor(courseDocumentId) {
    return favorites.find((item) => item.course_document_id === courseDocumentId);
  }

  async function toggleFavorite(item) {
    setError("");
    setMessage("");
    const existing = favoriteFor(item.course_document_id);
    try {
      if (existing) {
        await axiosClient.delete(`/student/favorites/${existing.id}`);
        setFavorites((current) => current.filter((favorite) => favorite.id !== existing.id));
        setMessage(text.removed);
      } else {
        const response = await axiosClient.post("/student/favorites", {
          course_document_id: item.course_document_id,
          source_student_document_id: id,
          match_score: displayScore(item),
        });
        setFavorites((current) => [response.data, ...current]);
        setMessage(text.saved);
      }
    } catch (err) {
      setError(getApiError(err));
    }
  }

  const recommendations = result?.recommendations?.length ? result.recommendations : result?.results || [];
  const visibleRecommendations = recommendations.filter((item) => displayScore(item) >= MIN_VISIBLE_SCORE);

  return (
    <main className="page course-browser-page">
      <div className="page-heading match-heading-clean">
        <div>
          <p className="eyebrow">{text.eyebrow}</p>
          <h1>{text.title}</h1>
        </div>
        <div className="heading-actions">
          <Link className="button secondary" to="/student/documents">{text.back}</Link>
          <strong className="result-count">{visibleRecommendations.length} {text.results}</strong>
          <button className="button" type="button" onClick={runMatching} disabled={running}>
            {running ? text.creating : text.create}
          </button>
        </div>
      </div>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
      {!result && <p>{text.noResult}</p>}

      {result && (
        <>
          {visibleRecommendations.length === 0 && (
            <section className="empty-state">
              <h2>{text.emptyTitle}</h2>
              <p>{text.emptyDesc}</p>
            </section>
          )}
          <div className="match-list-view">
            {visibleRecommendations.map((item) => {
              const isFavorite = Boolean(favoriteFor(item.course_document_id));
              return (
                <article className="match-row" key={item.course_document_id}>
                  <div className="match-row-main">
                    <div className="match-row-header">
                      <strong>{formatScore(displayScore(item))} ph\u00f9 h\u1ee3p</strong>
                    </div>
                    <h2>{item.course_title}</h2>
                    <p>{shortDescription(item)}</p>
                  </div>
                  <div className="match-row-actions">
                    <button
                      className={isFavorite ? "heart-button active" : "heart-button"}
                      type="button"
                      onClick={() => toggleFavorite(item)}
                      title={isFavorite ? "B\u1ecf y\u00eau th\u00edch" : "Th\u00eam v\u00e0o y\u00eau th\u00edch"}
                    >
                      {isFavorite ? "\u2665" : "\u2661"}
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        </>
      )}
    </main>
  );
}
