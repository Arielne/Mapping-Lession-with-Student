import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <main className="page hero-page">
      <section className="hero">
        <div>
          <p className="eyebrow">CourseMatch</p>
          <h1>Gợi ý khóa học phù hợp từ CV và nhu cầu học tập</h1>
          <p className="hero-copy">
            CourseMatch đọc CV hoặc hồ sơ nhu cầu học tập dạng PDF/DOCX, phân tích năng lực và mục tiêu của học viên để xếp hạng các khóa học phù hợp nhất.
          </p>
          <div className="hero-actions">
            {(user?.role === "user" || user?.role === "student") && (
              <Link className="button" to="/student/documents/upload">
                Upload CV / Nhu cầu học tập
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
          <p>Upload CV ẩn danh hoặc hồ sơ mô tả kỹ năng hiện tại, mục tiêu nghề nghiệp và nội dung muốn học thêm.</p>
        </div>
        <div>
          <h2>Cho admin</h2>
          <p>Upload tài liệu khóa học thật có mục tiêu, nội dung học, kỹ năng đầu ra, đối tượng phù hợp và điều kiện đầu vào.</p>
        </div>
        <div>
          <h2>Gợi ý minh bạch</h2>
          <p>Hiển thị mức độ phù hợp, lý do gợi ý và các kỹ năng/nội dung liên quan được phát hiện từ hồ sơ học viên.</p>
        </div>
      </section>
    </main>
  );
}
