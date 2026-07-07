import { useEffect, useState } from "react";
import axiosClient, { getApiError } from "../api/axiosClient";

const text = {
  eyebrow: "H\u1ecdc vi\u00ean",
  title: "T\u00ecm ki\u1ebfm kh\u00f3a h\u1ecdc",
  description: "Nh\u1eadp t\u1eeb kh\u00f3a \u0111\u1ec3 xem c\u00e1c m\u00f4n h\u1ecdc \u0111ang \u0111\u01b0\u1ee3c nh\u00e0 tr\u01b0\u1eddng c\u00f4ng khai trong CourseMatch.",
  placeholder: "T\u00ecm theo t\u00ean m\u00f4n, n\u1ed9i dung, t\u00e0i li\u1ec7u...",
  loading: "\u0110ang t\u00ecm ki\u1ebfm...",
  empty: "Ch\u01b0a t\u00ecm th\u1ea5y kh\u00f3a h\u1ecdc ph\u00f9 h\u1ee3p.",
  startTitle: "Nh\u1eadp t\u1eeb kh\u00f3a \u0111\u1ec3 b\u1eaft \u0111\u1ea7u t\u00ecm ki\u1ebfm",
  startDesc: "V\u00ed d\u1ee5: Python, UI UX, Marketing, Ti\u1ebfng Anh, FastAPI, Data Analysis.",
  result: "k\u1ebft qu\u1ea3",
  source: "T\u00e0i li\u1ec7u",
};

export default function CourseSearchPage() {
  const [keyword, setKeyword] = useState("");
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const query = keyword.trim();
    if (!query) {
      setCourses([]);
      setLoading(false);
      setError("");
      return undefined;
    }

    let cancelled = false;
    const timeoutId = window.setTimeout(async () => {
      setLoading(true);
      setError("");
      try {
        const response = await axiosClient.get("/course-documents/search", {
          params: { q: query, limit: 30 },
        });
        let nextCourses = Array.isArray(response.data) ? response.data : [];

        if (nextCourses.length === 0) {
          const fallbackResponse = await axiosClient.get("/course-documents/search", {
            params: { q: "", limit: 50 },
          });
          const fallbackCourses = Array.isArray(fallbackResponse.data) ? fallbackResponse.data : [];
          const loweredQuery = query.toLowerCase();
          nextCourses = fallbackCourses.filter((course) => {
            const searchable = [
              course.course_title,
              course.course_description,
              course.text_preview,
              course.original_filename,
              course.source_name,
            ].filter(Boolean).join(" ").toLowerCase();
            return searchable.includes(loweredQuery);
          });
        }

        if (!cancelled) setCourses(nextCourses);
      } catch (err) {
        if (!cancelled) setError(getApiError(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 250);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [keyword]);

  const query = keyword.trim();

  return (
    <main className="page course-search-page">
      <section className="course-search-hero">
        <div>
          <p className="eyebrow">{text.eyebrow}</p>
          <h1>{text.title}</h1>
          <p>{text.description}</p>
        </div>
      </section>

      <section className="course-search-panel panel">
        <div className="course-search-toolbar">
          <label className="course-search-input">
            <span aria-hidden="true">+</span>
            <input value={keyword} placeholder={text.placeholder} onChange={(event) => setKeyword(event.target.value)} />
          </label>
          <strong>{courses.length} {text.result}</strong>
        </div>

        {error && <p className="error">{error}</p>}
        {loading && <p className="muted">{text.loading}</p>}

        {!loading && !query && (
          <div className="empty-state">
            <h2>{text.startTitle}</h2>
            <p>{text.startDesc}</p>
          </div>
        )}

        {!loading && query && courses.length === 0 && (
          <div className="empty-state">
            <h2>{text.empty}</h2>
            <p>{text.placeholder}</p>
          </div>
        )}

        {!loading && courses.length > 0 && (
          <div className="course-search-results">
            {courses.map((course, index) => (
              <article className="course-search-item" key={course.id || `${course.course_title}-${index}`}>
                <span className="course-search-index">{String(index + 1).padStart(2, "0")}</span>
                <div>
                  <h2>{course.course_title}</h2>
                  <p>{course.course_description || course.text_preview}</p>
                  <small>{text.source}: {course.original_filename || course.source_name}</small>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
