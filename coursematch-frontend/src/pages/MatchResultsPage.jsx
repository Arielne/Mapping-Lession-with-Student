import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import axiosClient, { getApiError } from "../api/axiosClient";

const MIN_VISIBLE_SCORE = 0.75;

export default function MatchResultsPage() {
  const { id } = useParams();
  const [result, setResult] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [activeFilter, setActiveFilter] = useState("all");
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
      setMessage("Da tao danh sach goi y khoa hoc phu hop.");
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
    return item.course_summary || item.text_preview || item.recommendation_reason || item.explanation || "Mon hoc nay phu hop voi ho so ky nang va muc tieu hoc tap cua ban.";
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
        setMessage("Da bo khoa hoc khoi danh sach yeu thich.");
      } else {
        const response = await axiosClient.post("/student/favorites", {
          course_document_id: item.course_document_id,
          source_student_document_id: id,
          match_score: displayScore(item),
        });
        setFavorites((current) => [response.data, ...current]);
        setMessage("Da them khoa hoc vao danh sach yeu thich.");
      }
    } catch (err) {
      setError(getApiError(err));
    }
  }

  const recommendations = result?.recommendations?.length ? result.recommendations : result?.results || [];
  const visibleRecommendations = recommendations.filter((item) => displayScore(item) >= MIN_VISIBLE_SCORE);
  const filters = useMemo(() => {
    const skillCounts = new Map();
    visibleRecommendations.forEach((item) => {
      (item.matched_keywords || item.relevant_skills || []).forEach((skill) => {
        skillCounts.set(skill, (skillCounts.get(skill) || 0) + 1);
      });
    });
    return ["all", ...Array.from(skillCounts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([skill]) => skill)];
  }, [visibleRecommendations]);

  const filteredRecommendations = activeFilter === "all"
    ? visibleRecommendations
    : visibleRecommendations.filter((item) => (item.matched_keywords || item.relevant_skills || []).includes(activeFilter));

  return (
    <main className="page course-browser-page">
      <div className="course-toolbar">
        <div className="filter-icon" aria-hidden="true">⌯</div>
        <div className="filter-pills">
          {filters.map((filter) => (
            <button
              className={activeFilter === filter ? "filter-pill active" : "filter-pill"}
              key={filter}
              type="button"
              onClick={() => setActiveFilter(filter)}
            >
              {filter === "all" ? "Tat ca" : filter}
            </button>
          ))}
        </div>
      </div>

      <div className="page-heading">
        <div>
          <p className="eyebrow">Goi y khoa hoc</p>
          <h1>Mon hoc phu hop voi ban</h1>
        </div>
        <div className="heading-actions">
          <strong className="result-count">{filteredRecommendations.length} ket qua</strong>
          <button className="button" type="button" onClick={runMatching} disabled={running}>
            {running ? "Dang phan tich..." : "Tao goi y"}
          </button>
        </div>
      </div>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
      {!result && <p>Chua co ket qua. Hay bam Tao goi y sau khi co CV hoac ho so ky nang/so thich.</p>}

      {result && (
        <>
          {visibleRecommendations.length === 0 && (
            <section className="empty-state">
              <h2>Chua co mon hoc dat muc phu hop 75%</h2>
              <p>Hay bo sung them ky nang, so thich hoac muc tieu hoc tap de he thong goi y chinh xac hon.</p>
            </section>
          )}
          <div className="match-list-view">
            {filteredRecommendations.map((item) => {
              const isFavorite = Boolean(favoriteFor(item.course_document_id));
              const skills = item.matched_keywords?.length ? item.matched_keywords : item.relevant_skills || [];
              const missing = item.missing_keywords?.length ? item.missing_keywords : item.suggested_learning_outcomes || [];
              return (
                <article className="match-row" key={item.course_document_id}>
                  <div className="match-row-main">
                    <div className="match-row-header">
                      <span className="category-chip">{skills[0] || "Mon hoc phu hop"}</span>
                      <strong>{formatScore(displayScore(item))} phu hop</strong>
                    </div>
                    <h2>{item.course_title}</h2>
                    <p>{shortDescription(item)}</p>
                    <div className="subject-tags">
                      {skills.slice(0, 4).map((skill) => <span key={skill}>{skill}</span>)}
                      {skills.length > 4 && <span>+{skills.length - 4}</span>}
                    </div>
                  </div>
                  <div className="match-row-actions">
                    <button
                      className={isFavorite ? "heart-button active" : "heart-button"}
                      type="button"
                      onClick={() => toggleFavorite(item)}
                      title={isFavorite ? "Bo yeu thich" : "Them vao yeu thich"}
                    >
                      {isFavorite ? "♥" : "♡"}
                    </button>
                  </div>
                  <h2>{item.course_title}</h2>
                  <p className="course-meta">#{item.rank} • {item.algorithm || item.algorithm_name}</p>
                  <p>{item.explanation || item.recommendation_reason}</p>
                  <div className="subject-tags">
                    {skills.slice(0, 3).map((skill) => <span key={skill}>{skill}</span>)}
                    {skills.length > 3 && <span>+{skills.length - 3}</span>}
                  </div>
                  <div className="subject-card-footer">
                    <span>★ {formatScore(item.similarity_score ?? item.score ?? item.match_score)}</span>
                    <details>
                      <summary>Xem chi tiet ›</summary>
                      <p><strong>Ky nang nen hoc them:</strong> {missing.length ? missing.slice(0, 8).join(", ") : "Khong co de xuat bo sung"}</p>
                      <p><strong>Tu khoa lien quan:</strong> {item.matched_terms?.length ? item.matched_terms.join(", ") : "Khong co"}</p>
                    </details>
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
