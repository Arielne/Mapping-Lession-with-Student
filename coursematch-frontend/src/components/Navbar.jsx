import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const isStudent = user?.role === "student";
  const isAdmin = user?.role === "admin";

  return (
    <header className="navbar">
      <Link to="/" className="brand">
        CourseMatch
      </Link>
      <nav className="nav-links">
        {isStudent && <NavLink to="/student/documents/upload">Upload tài liệu</NavLink>}
        {isStudent && <NavLink to="/student/documents">Tài liệu của tôi</NavLink>}
        {isAdmin && <NavLink to="/admin/course-documents">Tài liệu khóa học</NavLink>}
        {isAdmin && <NavLink to="/admin/evaluation">Đánh giá</NavLink>}
      </nav>
      <div className="nav-actions">
        {user ? (
          <>
            <span className="user-pill">{user.full_name}</span>
            <button type="button" className="button ghost" onClick={logout}>
              Đăng xuất
            </button>
          </>
        ) : (
          <>
            <Link className="button ghost" to="/login">
              Đăng nhập
            </Link>
            <Link className="button" to="/register">
              Đăng ký
            </Link>
          </>
        )}
      </div>
    </header>
  );
}
