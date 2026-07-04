# CourseMatch — Đặc tả UI "Warm EdTech" (B+D)

Bản đặc tả cho redesign UI trên nhánh `feature/ui-redesign`.
Mockup xem tại [`docs/mockups/ui-directions.html`](mockups/ui-directions.html) (mở trực tiếp bằng trình duyệt, không cần chạy gì) — phương án được chốt là mục **"Kết hợp B + D — Warm EdTech"**.

## Design tokens

Toàn bộ khai báo trong `:root` của `coursematch-frontend/src/styles.css` — đổi theme chỉ cần sửa ở đây.

| Token | Giá trị | Dùng cho |
|---|---|---|
| `--bg` | `#f6f1e7` | Nền trang (kem giấy) |
| `--surface` | `#fdfaf3` | Mặt thẻ, panel, bảng |
| `--ink` | `#2e2a24` | Chữ chính |
| `--ink-soft` | `#7a7264` | Chữ phụ, meta |
| `--line` | `#e7dcc6` | Viền thẻ, kẻ bảng |
| `--accent` | `#b4552d` | Terracotta — xem quy tắc bên dưới |
| `--good` | `#6b7a5a` | Xanh ô liu — phù hợp cao / thành công |
| `--warn` | `#c99a3f` | Hổ phách — phù hợp trung bình / cảnh báo |
| `--bad` | `#a8442c` | Đỏ đất — lỗi / phù hợp thấp |

## Quy tắc quan trọng nhất: kỷ luật accent

Terracotta (`--accent`) **chỉ xuất hiện ở 4 loại vị trí**:

1. Nhãn mục (`.eyebrow`)
2. Gạch chân link nav đang active
3. Nút hành động chính (`.button`)
4. Trạng thái cần chú ý (badge "Thấp", chấm "Đang xử lý")

Mọi chỗ khác dùng neutral. Mức độ phù hợp dùng **màu ngữ nghĩa riêng** (`--good`/`--warn`/`--bad`), không dùng accent — để accent luôn là dấu nhấn, không thành hình nền.

## Typography

- **Tiêu đề / con số lớn:** Fraunces (Google Fonts, subset `vietnamese`), fallback Georgia. Weight 600, letter-spacing hơi âm.
- **Nội dung / dữ liệu:** Be Vietnam Pro (subset `vietnamese`), fallback system sans.
- Con số trong bảng/thống kê: `font-variant-numeric: tabular-nums`.

## Hình khối

- Bo góc thẻ/panel: 16–18px; nút: pill (999px); input: 10px.
- Vân giấy: overlay SVG noise ~5% trên `body::after` (đã có sẵn trong CSS, đừng xóa).
- Bóng đổ ấm, nhẹ: `rgba(90, 68, 40, .1)` thay vì bóng xám/xanh.

## Hiển thị mức độ phù hợp

- **Phía student** (MatchResults, gợi ý): vòng tròn % (`ScoreRing` trong `src/components/ScoreRing.jsx`) + badge chữ "Phù hợp cao / Trung bình / Thấp". Ngưỡng: ≥ 70% cao (`--good`), ≥ 45% trung bình (`--warn`), còn lại thấp (`--bad`).
- **Phía admin** (bảng nhiều dòng): thanh bar + badge, không dùng vòng tròn (quét cột nhanh hơn).

## Phạm vi trang

| Trang | Mức thay đổi |
|---|---|
| `HomePage` | Làm lại hero 2 cột (copy + minh họa sản phẩm), bỏ 3 thẻ feature |
| `MatchResultsPage` | Thêm `ScoreRing`, giữ cấu trúc dữ liệu |
| Các trang còn lại | Chỉ ăn theo reskin của `styles.css`, không đổi JSX |

## Những gì KHÔNG làm (đã cân nhắc và loại)

- Animation dài (nhịp thở 8s trên hero, Ken Burns, typewriter) — app công cụ cần phản hồi tức thì. Ngoại lệ duy nhất: chấm trạng thái "đang xử lý" pulse chậm, có `prefers-reduced-motion` guard.
- Âm thanh.
- Đổi cấu trúc route / logic — PR này thuần giao diện.
