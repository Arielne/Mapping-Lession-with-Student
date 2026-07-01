import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const isStudent = user?.role === "user" || user?.role === "student";
  const isAdmin = user?.role === "admin";

  return (
    <header className="navbar">
      <Link to="/" className="brand">
        CourseMatch
      </Link>
      <nav className="nav-links">
        {isStudent && <NavLink to="/student/documents/upload">Upload CV / Nhu cau</NavLink>}
        {isStudent && <NavLink to="/student/documents">Ho so cua toi</NavLink>}
        {isStudent && <NavLink to="/student/favorites">Yeu thich</NavLink>}
        {isAdmin && <NavLink to="/admin/course-documents">Tai lieu khoa hoc</NavLink>}
        {isAdmin && <NavLink to="/admin/evaluation">Danh gia</NavLink>}
      </nav>
      <div className="nav-actions">
        {user ? (
          <>
            <span className="user-pill">{user.full_name}</span>
            <button type="button" className="button ghost" onClick={logout}>
              Dang xuat
            </button>
          </>
        ) : (
          <>
            <Link className="button ghost" to="/login">
              Dang nhap
            </Link>
            <Link className="button" to="/register">
              Dang ky
            </Link>
          </>
        )}
      </div>
    </header>
  );
}
