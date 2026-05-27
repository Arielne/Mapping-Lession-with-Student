import { useEffect, useState } from "react";
import axiosClient, { getApiError } from "../api/axiosClient";
import CourseCard from "../components/CourseCard";

export default function MyRegistrationsPage() {
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRegistrations() {
      setLoading(true);
      setError("");
      try {
        const response = await axiosClient.get("/registrations/me");
        setRegistrations(response.data);
      } catch (err) {
        setError(getApiError(err));
      } finally {
        setLoading(false);
      }
    }

    loadRegistrations();
  }, []);

  return (
    <main className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Cá nhân</p>
          <h1>Khóa học đã quan tâm</h1>
        </div>
      </div>
      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>Đang tải danh sách...</p>
      ) : (
        <div className="course-grid">
          {registrations.map((registration) => (
            registration.course && <CourseCard key={registration.id} course={registration.course} />
          ))}
        </div>
      )}
      {!loading && registrations.length === 0 && <p>Bạn chưa lưu khóa học nào.</p>}
    </main>
  );
}
