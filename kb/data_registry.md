# Data Registry — ĐÃ CHUYỂN SANG CẤU TRÚC OKF

> **File này giờ là STUB REDIRECT.** (2026-07-28, job Winston_20260728_104434)

Sổ đăng ký mọi nguồn dữ liệu hệ thống đã được migrate sang cấu trúc chuẩn mở **OKF**
(Open Knowledge Format: markdown + YAML frontmatter tối giản, 1 nguồn = 1 file, tổ chức
thư mục theo khái niệm) tại:

## 👉 [`kb/data_registry/`](data_registry/) — bắt đầu ở [`data_registry/index.md`](data_registry/index.md)

- Mỗi nguồn dữ liệu (bảng BQ / file local / config / script output / external API) = **1 file `.md`**
  với frontmatter (`kind`, `status`, `source`, `group`) + body prose (Là gì / Ai ghi-cadence / Bẫy).
- 13 thư mục nhóm (market-state, price-volume, fundamentals, macro, rating-8l, custom30, bq-cache,
  lag-book, research-caches, trading-bot, paper-harness, feeds, config-meta), mỗi thư mục có `index.md`.
- **Nguyên tắc bắt buộc** (status/obsolete process) + **quy tắc chọn universe** giữ trong
  `data_registry/index.md` và `data_registry/_universe-selection-rules.md`.
- Lịch sử biên tập registry: [`data_registry/CHANGELOG.md`](data_registry/CHANGELOG.md).

**Grep vẫn hoạt động:** `grep -rn "<tên nguồn>" mike/kb/data_registry/`.

File STUB này giữ lại (KHÔNG xoá) để các trích dẫn cũ `kb/data_registry.md` rải rác trong
tài liệu nghiên cứu lịch sử (agents/Taylor/*, agents/Winston/*) vẫn có nơi để đi tới.
