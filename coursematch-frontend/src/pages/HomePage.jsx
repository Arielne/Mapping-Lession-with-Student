import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <main className="page hero-page">
      <section className="hero">
        <div>
          <p className="eyebrow">CourseMatch</p>
          <h1>Hệ thống đối sánh tài liệu khóa học và nhu cầu học viên</h1>
          <p className="hero-copy">
            CourseMatch xử lý file PDF/DOCX thật, trích xuất nội dung thành JSON và matching bằng vector nhị phân.
          </p>
          <div className="hero-actions">
            {user?.role === "student" && (
              <Link className="button" to="/student/documents/upload">
                Upload tài liệu
              </Link>
            )}
            {user?.role === "admin" && (
              <Link className="button" to="/admin/course-documents">
                Quản lý tài liệu khóa học
              </Link>
            )}
            {!user && (
              <Link className="button secondary" to="/register">
                Bắt đầu
              </Link>
            )}
          </div>
        </div>
      </section>
      <section className="feature-grid">
        <div>
          <h2>Cho học viên</h2>
          <p>Upload CV ẩn danh hoặc mô tả nhu cầu học tập bằng PDF/DOCX.</p>
        </div>
        <div>
          <h2>Cho admin</h2>
          <p>Upload tài liệu khóa học thật, quản lý file gốc và nhãn ground truth.</p>
        </div>
        <div>
          <h2>Matching minh bạch</h2>
          <p>Biểu diễn văn bản bằng vector 0/1 và tính Jaccard similarity.</p>
        </div>
      </section>
    </main>
  );
}
