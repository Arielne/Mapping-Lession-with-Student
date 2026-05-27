import { useEffect, useMemo, useState } from "react";
import axiosClient, { getApiError } from "../api/axiosClient";
import CourseCard from "../components/CourseCard";

const levels = ["", "Beginner", "Intermediate", "Advanced"];

export default function CoursesPage() {
  const [courses, setCourses] = useState([]);
  const [filters, setFilters] = useState({ category: "", level: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const categories = useMemo(
    () => Array.from(new Set(courses.map((course) => course.category))).sort(),
    [courses],
  );

  useEffect(() => {
    async function loadCourses() {
      setLoading(true);
      setError("");
      try {
        const params = {};
        if (filters.category) params.category = filters.category;
        if (filters.level) params.level = filters.level;
        const response = await axiosClient.get("/courses", { params });
        setCourses(response.data);
      } catch (err) {
        setError(getApiError(err));
      } finally {
        setLoading(false);
      }
    }

    loadCourses();
  }, [filters.category, filters.level]);

  return (
    <main className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Danh sách</p>
          <h1>Khóa học đang mở</h1>
        </div>
        <div className="filters">
          <select value={filters.category} onChange={(event) => setFilters((current) => ({ ...current, category: event.target.value }))}>
            <option value="">Tất cả category</option>
            {categories.map((category) => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
          <select value={filters.level} onChange={(event) => setFilters((current) => ({ ...current, level: event.target.value }))}>
            {levels.map((level) => (
              <option key={level || "all"} value={level}>{level || "Tất cả level"}</option>
            ))}
          </select>
        </div>
      </div>
      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>Đang tải khóa học...</p>
      ) : (
        <div className="course-grid">
          {courses.map((course) => <CourseCard key={course.id} course={course} />)}
        </div>
      )}
    </main>
  );
}
