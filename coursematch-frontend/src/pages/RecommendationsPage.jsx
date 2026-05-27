import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axiosClient, { getApiError } from "../api/axiosClient";
import CourseCard from "../components/CourseCard";

export default function RecommendationsPage() {
  const { needId } = useParams();
  const [recommendations, setRecommendations] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRecommendations() {
      setLoading(true);
      setError("");
      try {
        const response = await axiosClient.get(`/recommendations/${needId}`);
        setRecommendations(response.data);
      } catch (err) {
        setError(getApiError(err));
      } finally {
        setLoading(false);
      }
    }

    loadRecommendations();
  }, [needId]);

  async function saveRegistration(courseId) {
    setMessage("");
    setError("");
    try {
      await axiosClient.post("/registrations", { course_id: courseId });
      setMessage("Đã lưu khóa học quan tâm.");
    } catch (err) {
      if (err?.response?.status === 409) {
        setMessage("Khóa học này đã có trong danh sách quan tâm.");
        return;
      }
      setError(getApiError(err));
    }
  }

  return (
    <main className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Gợi ý</p>
          <h1>Khóa học phù hợp</h1>
        </div>
      </div>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>Đang tải gợi ý...</p>
      ) : (
        <div className="course-grid">
          {recommendations.map((item) => (
            <CourseCard key={item.course.id} course={item.course}>
              <div className="recommendation-info">
                <strong>Match score: {item.match_score}</strong>
                <span>Matched skills: {item.matched_skills.length ? item.matched_skills.join(", ") : "Chưa có"}</span>
              </div>
              <button className="button" type="button" onClick={() => saveRegistration(item.course.id)}>
                Lưu quan tâm
              </button>
            </CourseCard>
          ))}
        </div>
      )}
      {!loading && recommendations.length === 0 && <p>Chưa có khóa học phù hợp.</p>}
    </main>
  );
}
