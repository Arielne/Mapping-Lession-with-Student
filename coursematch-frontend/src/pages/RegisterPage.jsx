import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getApiError } from "../api/axiosClient";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { register, login } = useAuth();
  const navigate = useNavigate();

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register(form);
      await login(form.email, form.password);
      navigate("/courses");
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="page narrow">
      <section className="panel">
        <h1>Đăng ký student</h1>
        <form onSubmit={handleSubmit} className="form">
          <label>
            Họ tên
            <input value={form.full_name} onChange={(event) => updateField("full_name", event.target.value)} required />
          </label>
          <label>
            Email
            <input value={form.email} onChange={(event) => updateField("email", event.target.value)} type="email" required />
          </label>
          <label>
            Password
            <input value={form.password} onChange={(event) => updateField("password", event.target.value)} type="password" minLength={6} required />
          </label>
          {error && <p className="error">{error}</p>}
          <button className="button" type="submit" disabled={submitting}>
            {submitting ? "Đang tạo tài khoản..." : "Đăng ký"}
          </button>
        </form>
        <p className="muted-text">
          Đã có tài khoản? <Link to="/login">Đăng nhập</Link>
        </p>
      </section>
    </main>
  );
}
