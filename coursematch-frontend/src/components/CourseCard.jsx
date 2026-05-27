export default function CourseCard({ course, children }) {
  return (
    <article className="course-card">
      <div className="course-card-header">
        <div>
          <h3>{course.title}</h3>
          <p className="course-meta">
            {course.category} · {course.level} · {course.duration_weeks} tuần
          </p>
        </div>
        {course.is_active === false && <span className="status muted">Đã ẩn</span>}
      </div>
      <p>{course.description}</p>
      <div className="tags">
        {(course.skills || []).map((skill) => (
          <span key={skill}>{skill}</span>
        ))}
      </div>
      {children && <div className="card-actions">{children}</div>}
    </article>
  );
}
