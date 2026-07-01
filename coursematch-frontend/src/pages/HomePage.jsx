import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <main className="home-shell">
      <section className="home-hero">
        <div className="home-hero-content">
          <p className="eyebrow">CourseMatch</p>
          <h1>Tim mon hoc phu hop voi ban</h1>
          <p>
            He thong giup sinh vien kham pha nhung mon hoc phu hop voi ky nang,
            so thich va muc tieu hoc tap cua minh.
          </p>
          <div className="hero-actions">
            {(user?.role === "user" || user?.role === "student") && (
              <Link className="button" to="/student/documents/upload">
                Tim khoa hoc phu hop
              </Link>
            )}
            {user?.role === "admin" && (
              <Link className="button" to="/admin/course-documents">
                Quan ly mon hoc
              </Link>
            )}
            {!user && (
              <>
                <Link className="button" to="/login">
                  Dang nhap
                </Link>
                <Link className="button secondary" to="/register">
                  Tao tai khoan
                </Link>
              </>
            )}
          </div>
        </div>

        <div className="home-preview" aria-label="Minh hoa goi y mon hoc">
          <div className="preview-card primary">
            <span>Phu hop nhat</span>
            <h2>Data Analytics</h2>
            <p>Python · SQL · Dashboard</p>
          </div>
          <div className="preview-card">
            <span>Da luu</span>
            <h2>UI/UX Design</h2>
            <p>Research · Wireframe</p>
          </div>
          <div className="preview-card">
            <span>Goi y</span>
            <h2>AI Foundation</h2>
            <p>Machine Learning · Python</p>
          </div>
        </div>
      </section>

      <section className="home-feature-row" aria-label="Quy trinh CourseMatch">
        <div>
          <strong>01</strong>
          <h2>Nhap ho so</h2>
          <p>Upload CV hoac mo ta ky nang, so thich va muc tieu hoc tap.</p>
        </div>
        <div>
          <strong>02</strong>
          <h2>So khop mon hoc</h2>
          <p>He thong doi chieu voi tai lieu mon hoc do nha truong cap nhat.</p>
        </div>
        <div>
          <strong>03</strong>
          <h2>Luu mon phu hop</h2>
          <p>Danh dau nhung mon ban quan tam de xem lai khi can chon mon.</p>
        </div>
      </section>
    </main>
  );
}
