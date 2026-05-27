import { useEffect, useState } from "react";
import axiosClient, { getApiError } from "../api/axiosClient";
import CourseCard from "../components/CourseCard";

const emptyForm = {
  title: "",
  category: "",
  level: "Beginner",
  skills: "",
  description: "",
  duration_weeks: 4,
  is_active: true,
};

export default function AdminCoursesPage() {
  const [courses, setCourses] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadCourses() {
    setLoading(true);
    setError("");
    try {
      const response = await axiosClient.get("/courses");
      setCourses(response.data);
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCourses();
  }, []);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function toPayload() {
    return {
      ...form,
      duration_weeks: Number(form.duration_weeks),
      skills: form.skills.split(",").map((item) => item.trim()).filter(Boolean),
    };
  }

  function editCourse(course) {
    setEditingId(course.id);
    setForm({
      title: course.title,
      category: course.category,
      level: course.level,
      skills: (course.skills || []).join(", "),
      description: course.description,
      duration_weeks: course.duration_weeks,
      is_active: course.is_active,
    });
  }

  function resetForm() {
    setEditingId(null);
    setForm(emptyForm);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      if (editingId) {
        await axiosClient.put(`/courses/${editingId}`, toPayload());
        setMessage("Đã cập nhật khóa học.");
      } else {
        await axiosClient.post("/courses", toPayload());
        setMessage("Đã thêm khóa học.");
      }
      resetForm();
      loadCourses();
    } catch (err) {
      setError(getApiError(err));
    }
  }

  async function softDelete(courseId) {
    setError("");
    setMessage("");
    try {
      await axiosClient.delete(`/courses/${courseId}`);
      setMessage("Đã xóa mềm khóa học.");
      loadCourses();
    } catch (err) {
      setError(getApiError(err));
    }
  }

  return (
    <main className="page admin-layout">
      <section className="panel">
        <h1>{editingId ? "Sửa khóa học" : "Thêm khóa học"}</h1>
        <form className="form" onSubmit={handleSubmit}>
          <label>
            Tiêu đề
            <input value={form.title} onChange={(event) => updateField("title", event.target.value)} required />
          </label>
          <label>
            Category
            <input value={form.category} onChange={(event) => updateField("category", event.target.value)} required />
          </label>
          <label>
            Level
            <select value={form.level} onChange={(event) => updateField("level", event.target.value)}>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </label>
          <label>
            Skills
            <input value={form.skills} onChange={(event) => updateField("skills", event.target.value)} placeholder="MongoDB, NoSQL" />
          </label>
          <label>
            Description
            <textarea value={form.description} onChange={(event) => updateField("description", event.target.value)} rows="4" required />
          </label>
          <label>
            Duration weeks
            <input value={form.duration_weeks} onChange={(event) => updateField("duration_weeks", event.target.value)} type="number" min="1" max="100" required />
          </label>
          {error && <p className="error">{error}</p>}
          {message && <p className="success">{message}</p>}
          <div className="form-actions">
            <button className="button" type="submit">{editingId ? "Lưu thay đổi" : "Thêm khóa học"}</button>
            {editingId && <button className="button ghost" type="button" onClick={resetForm}>Hủy</button>}
          </div>
        </form>
      </section>
      <section>
        <div className="page-heading">
          <div>
            <p className="eyebrow">Admin</p>
            <h1>Quản lý khóa học active</h1>
          </div>
        </div>
        {loading ? (
          <p>Đang tải khóa học...</p>
        ) : (
          <div className="course-grid compact">
            {courses.map((course) => (
              <CourseCard key={course.id} course={course}>
                <button className="button secondary" type="button" onClick={() => editCourse(course)}>Sửa</button>
                <button className="button danger" type="button" onClick={() => softDelete(course.id)}>Xóa mềm</button>
              </CourseCard>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
