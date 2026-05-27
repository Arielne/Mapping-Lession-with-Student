import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    role: "student",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await register(form);
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Register failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Register</h1>
        <label>
          Full name
          <input value={form.full_name} onChange={(event) => update("full_name", event.target.value)} required />
        </label>
        <label>
          Email
          <input value={form.email} onChange={(event) => update("email", event.target.value)} required />
        </label>
        <label>
          Password
          <input
            type="password"
            value={form.password}
            onChange={(event) => update("password", event.target.value)}
            minLength={8}
            required
          />
        </label>
        <label>
          Role
          <select value={form.role} onChange={(event) => update("role", event.target.value)}>
            <option value="student">student</option>
            <option value="admin">admin</option>
          </select>
        </label>
        {error && <p className="error">{error}</p>}
        <button className="primary" disabled={busy}>
          {busy ? "Creating..." : "Register"}
        </button>
        <p className="muted">
          Already registered? <Link to="/login">Login</Link>
        </p>
      </form>
    </main>
  );
}

