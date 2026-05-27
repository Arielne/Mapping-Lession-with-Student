import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosClient, { getApiError } from "../api/axiosClient";

export default function CreateNeedPage() {
  const [form, setForm] = useState({
    desired_category: "Data Analysis",
    current_level: "Beginner",
    desired_skills: "Python, Pandas, Data Visualization",
    learning_goal: "Hoc phan tich du lieu bang Python",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const payload = {
        desired_category: form.desired_category,
        current_level: form.current_level,
        desired_skills: form.desired_skills.split(",").map((item) => item.trim()).filter(Boolean),
        learning_goal: form.learning_goal,
      };
      const response = await axiosClient.post("/learning-needs", payload);
      navigate(`/recommendations/${response.data.id}`);
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="page narrow">
      <section className="panel">
        <h1>Tạo nhu cầu học tập</h1>
        <form onSubmit={handleSubmit} className="form">
          <label>
            Category mong muốn
            <input value={form.desired_category} onChange={(event) => updateField("desired_category", event.target.value)} required />
          </label>
          <label>
            Trình độ hiện tại
            <select value={form.current_level} onChange={(event) => updateField("current_level", event.target.value)}>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </label>
          <label>
            Kỹ năng mong muốn
            <input value={form.desired_skills} onChange={(event) => updateField("desired_skills", event.target.value)} placeholder="Python, Pandas" required />
          </label>
          <label>
            Mục tiêu học tập
            <textarea value={form.learning_goal} onChange={(event) => updateField("learning_goal", event.target.value)} rows="4" required />
          </label>
          {error && <p className="error">{error}</p>}
          <button className="button" type="submit" disabled={submitting}>
            {submitting ? "Đang tạo..." : "Tạo và xem gợi ý"}
          </button>
        </form>
      </section>
    </main>
  );
}
