import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import AdminRoute from "./components/AdminRoute";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminUploadCoursePage from "./pages/AdminUploadCoursePage";
import CourseDocumentsPage from "./pages/CourseDocumentsPage";
import EvaluationPage from "./pages/EvaluationPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import MatchResultsPage from "./pages/MatchResultsPage";
import RegisterPage from "./pages/RegisterPage";
import StudentDocumentsPage from "./pages/StudentDocumentsPage";
import StudentUploadDocumentPage from "./pages/StudentUploadDocumentPage";

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/courses"
          element={
            <ProtectedRoute>
              <CourseDocumentsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/upload-course"
          element={
            <AdminRoute>
              <AdminUploadCoursePage />
            </AdminRoute>
          }
        />
        <Route
          path="/evaluation"
          element={
            <AdminRoute>
              <EvaluationPage />
            </AdminRoute>
          }
        />
        <Route
          path="/student/upload"
          element={
            <ProtectedRoute>
              <StudentUploadDocumentPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/documents"
          element={
            <ProtectedRoute>
              <StudentDocumentsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/matching/:studentDocumentId"
          element={
            <ProtectedRoute>
              <MatchResultsPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

