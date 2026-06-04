import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <main className="page hero-page">
      <section className="hero">
        <div>
          <p className="eyebrow">CourseMatch</p>
          <h1>Goi y khoa hoc tu tai lieu PDF/DOCX that</h1>
          <p className="hero-copy">
            CourseMatch luu file goc bang MongoDB GridFS, trich xuat text tu CV hoac ho so nhu cau hoc tap,
            sau do doi sanh voi tai lieu khoa hoc bang binary Jaccard n-gram de xep hang cac khoa hoc phu hop.
          </p>
          <div className="hero-actions">
            {(user?.role === "user" || user?.role === "student") && (
              <Link className="button" to="/student/documents/upload">
                Upload CV / Nhu cau hoc tap
              </Link>
            )}
            {user?.role === "admin" && (
              <Link className="button" to="/admin/course-documents">
                Quan ly tai lieu khoa hoc
              </Link>
            )}
            {!user && (
              <Link className="button secondary" to="/register">
                Bat dau
              </Link>
            )}
          </div>
        </div>
      </section>
      <section className="feature-grid">
        <div>
          <h2>Hoc vien</h2>
          <p>Upload CV hoac tai lieu nhu cau hoc tap dang PDF/DOCX. He thong chi dung text trich xuat tu file that de matching.</p>
        </div>
        <div>
          <h2>Admin</h2>
          <p>Upload tai lieu khoa hoc dang PDF/DOCX. File binary duoc luu trong GridFS, document thuong chi luu metadata va text.</p>
        </div>
        <div>
          <h2>Matching minh bach</h2>
          <p>Ket qua gom diem tuong dong, thuat toan, trang thai goi y va ly do duoc giai thich bang keyword overlap.</p>
        </div>
      </section>
    </main>
  );
}
