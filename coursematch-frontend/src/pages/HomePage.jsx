import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import ScoreRing from "../components/ScoreRing";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <main className="page hero-page">
      <section className="hero-split">
        <div className="hero-copy-col">
          <p className="eyebrow">Matching bằng phân tích tài liệu</p>
          <h1>
            Một bản CV.
            <br />
            Đúng <em>khóa học</em> bạn cần.
          </h1>
          <p className="hero-copy">
            Tải lên CV hoặc hồ sơ nhu cầu học tập (PDF/DOCX). CourseMatch phân tích năng lực và mục tiêu của bạn, rồi xếp hạng những khóa học phù hợp nhất — kèm lý do vì sao.
          </p>
          <div className="hero-actions">
            {(user?.role === "user" || user?.role === "student") && (
              <Link className="button" to="/student/documents/upload">
                Tải CV / Nhu cầu lên ngay
              </Link>
            )}
            {user?.role === "admin" && (
              <Link className="button" to="/admin/course-documents">
                Quản lý tài liệu khóa học
              </Link>
            )}
            {!user && (
              <>
                <Link className="button" to="/register">
                  Tải CV lên ngay
                </Link>
                <Link className="button ghost" to="/login">
                  Đã có tài khoản? Đăng nhập →
                </Link>
              </>
            )}
          </div>
          <div className="hero-proof">
            <span>
              <b>PDF · DOCX</b>
              định dạng hỗ trợ
            </span>
            <span>
              <b>Top 3</b>
              gợi ý kèm lý do
            </span>
            <span>
              <b>&lt; 30s</b>
              từ upload đến kết quả
            </span>
          </div>
        </div>
        <div className="hero-stage" aria-hidden="true">
          <div className="stage-arch"></div>
          <div className="stage-doc">
            <span className="pg"></span>
            <span>
              CV_cua_ban.pdf
              <small>Đã phân tích xong</small>
            </span>
          </div>
          <div className="stage-line"></div>
          <div className="stage-course">
            <div className="cat">Khớp nhất cho bạn</div>
            <h3>Lập trình Python nâng cao</h3>
            <p>Khớp với kinh nghiệm và mục tiêu nghề nghiệp trong hồ sơ của bạn.</p>
            <div className="rowx">
              <span className="level-badge level-hi">Phù hợp cao</span>
              <ScoreRing percent={91} size={44} />
            </div>
          </div>
          <div className="stage-chip">+7 khóa học phù hợp khác</div>
        </div>
      </section>
    </main>
  );
}
