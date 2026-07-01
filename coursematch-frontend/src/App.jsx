import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import AdminCourseDocumentsPage from "./pages/AdminCourseDocumentsPage";
import StudentUploadPage from "./pages/StudentUploadPage";
import StudentDocumentsPage from "./pages/StudentDocumentsPage";
import MatchResultsPage from "./pages/MatchResultsPage";
import AdminEvaluationPage from "./pages/AdminEvaluationPage";
import FavoritesPage from "./pages/FavoritesPage";

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute role="user" />}>
          <Route path="/student/documents/upload" element={<StudentUploadPage />} />
          <Route path="/student/documents" element={<StudentDocumentsPage />} />
          <Route path="/student/documents/:id/matches" element={<MatchResultsPage />} />
          <Route path="/student/favorites" element={<FavoritesPage />} />
        </Route>
        <Route element={<AdminRoute />}>
          <Route path="/admin/course-documents" element={<AdminCourseDocumentsPage />} />
          <Route path="/admin/evaluation" element={<AdminEvaluationPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}
