import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="topbar">
      <NavLink className="brand" to="/">
        CourseMatch
      </NavLink>
      <nav>
        {user && <NavLink to="/courses">Courses</NavLink>}
        {user?.role === "admin" && <NavLink to="/admin/upload-course">Upload Course</NavLink>}
        {user?.role === "admin" && <NavLink to="/evaluation">Evaluation</NavLink>}
        {user?.role === "student" && <NavLink to="/student/upload">Upload Document</NavLink>}
        {user?.role === "student" && <NavLink to="/student/documents">My Documents</NavLink>}
        {!user && <NavLink to="/login">Login</NavLink>}
        {!user && <NavLink to="/register">Register</NavLink>}
      </nav>
      {user && (
        <button className="ghost" onClick={handleLogout}>
          Logout
        </button>
      )}
    </header>
  );
}

