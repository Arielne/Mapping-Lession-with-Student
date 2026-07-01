import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { getApiError } from "../api/axiosClient";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const user = await login(email, password);
      const fallback = user.role === "admin" ? "/admin/course-documents" : "/student/documents";
      navigate(location.state?.from?.pathname || fallback, { replace: true });
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-intro">
          <p className="eyebrow">CourseMatch</p>
          <h1>Dang nhap</h1>
          <p>Vao he thong de tim, luu va xem lai nhung mon hoc phu hop voi ban.</p>
        </div>

        <form onSubmit={handleSubmit} className="form auth-form">
          <label>
            Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" autoComplete="email" required />
          </label>
          <label>
            Mat khau
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" required />
          </label>
          {error && <p className="error">{error}</p>}
          <button className="button auth-submit" type="submit" disabled={submitting}>
            {submitting ? "Dang dang nhap..." : "Dang nhap"}
          </button>
        </form>

        <p className="auth-note">
          Chua co tai khoan? <Link to="/register">Tao tai khoan sinh vien</Link>
        </p>
      </section>
    </main>
  );
}
