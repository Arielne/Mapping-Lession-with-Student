import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ role }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <main className="page"><p>Đang kiểm tra đăng nhập...</p></main>;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const isAllowedRole = !role || user.role === role || (role === "user" && user.role === "student");

  if (!isAllowedRole) {
    return <Navigate to={user.role === "admin" ? "/admin/course-documents" : "/student/documents"} replace />;
  }

  return <Outlet />;
}
