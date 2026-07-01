import { useEffect, useState } from "react";
import axiosClient, { getApiError } from "../api/axiosClient";

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadFavorites() {
    setLoading(true);
    setError("");
    try {
      const response = await axiosClient.get("/student/favorites/me");
      setFavorites(response.data);
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadFavorites();
  }, []);

  async function removeFavorite(id) {
    setError("");
    setMessage("");
    try {
      await axiosClient.delete(`/student/favorites/${id}`);
      setFavorites((current) => current.filter((item) => item.id !== id));
      setMessage("Da bo khoa hoc khoi danh sach yeu thich.");
    } catch (err) {
      setError(getApiError(err));
    }
  }

  return (
    <main className="page course-browser-page">
      <div className="course-toolbar">
        <div className="filter-icon" aria-hidden="true">♡</div>
        <div className="filter-pills">
          <span className="filter-pill active">Yeu thich</span>
          <span className="filter-pill">Luu de xem lai</span>
        </div>
      </div>

      <div className="page-heading">
        <div>
          <p className="eyebrow">Hoc vien</p>
          <h1>Khoa hoc yeu thich</h1>
        </div>
        <strong className="result-count">{favorites.length} ket qua</strong>
      </div>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
      {loading && <p>Dang tai...</p>}
      {!loading && favorites.length === 0 && (
        <section className="empty-state">
          <h2>Chua co khoa hoc yeu thich</h2>
          <p>Hay vao trang goi y, bam bieu tuong trai tim de luu lai nhung mon hoc phu hop voi ban.</p>
        </section>
      )}

      <div className="course-card-grid">
        {favorites.map((item) => (
          <article className="subject-card" key={item.id}>
            <div className="subject-card-top">
              <span className="category-chip">{item.source_name || "Khoa hoc"}</span>
              <button className="heart-button active" type="button" onClick={() => removeFavorite(item.id)} title="Bo yeu thich">
                ♥
              </button>
            </div>
            <h2>{item.course_title}</h2>
            <p className="course-meta">{item.original_filename || "Tai lieu khoa hoc"}</p>
            <p>{item.text_preview || "Mon hoc da duoc luu de ban xem lai khi can chon mon phu hop."}</p>
            <div className="subject-tags">
              {(item.extracted_skills || []).slice(0, 4).map((skill) => <span key={skill}>{skill}</span>)}
              {(item.extracted_skills || []).length > 4 && <span>+{item.extracted_skills.length - 4}</span>}
            </div>
            <div className="subject-card-footer">
              <span>★ {item.match_score != null ? `${(item.match_score * 100).toFixed(1)}% phu hop` : "Da luu"}</span>
              <span className="saved-label">Mon da luu</span>
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}
