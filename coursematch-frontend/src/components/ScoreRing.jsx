const RADIUS = 23;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export function matchLevel(percent) {
  if (percent >= 70) return "hi";
  if (percent >= 45) return "mid";
  return "lo";
}

export function matchLevelLabel(percent) {
  const level = matchLevel(percent);
  if (level === "hi") return "Phù hợp cao";
  if (level === "mid") return "Phù hợp trung bình";
  return "Phù hợp thấp";
}

export default function ScoreRing({ percent, size = 56 }) {
  const pct = Math.max(0, Math.min(100, percent || 0));
  const filled = (pct / 100) * CIRCUMFERENCE;

  return (
    <span
      className={`score-ring level-${matchLevel(pct)}`}
      role="img"
      aria-label={`Mức độ phù hợp ${Math.round(pct)}%`}
    >
      <svg viewBox="0 0 54 54" width={size} height={size}>
        <circle className="ring-track" cx="27" cy="27" r={RADIUS} fill="none" strokeWidth="6" />
        <circle
          className="ring-value"
          cx="27"
          cy="27"
          r={RADIUS}
          fill="none"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={`${filled} ${CIRCUMFERENCE}`}
          transform="rotate(-90 27 27)"
        />
      </svg>
      <b>{Math.round(pct)}%</b>
    </span>
  );
}
