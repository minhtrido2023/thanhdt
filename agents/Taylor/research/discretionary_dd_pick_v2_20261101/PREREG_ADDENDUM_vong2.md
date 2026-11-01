# PREREG — bổ sung vòng 2 (tách khỏi PREREG.md gốc, md5 12d35014cec24767904c23dfea0a2ce5)

## Bổ sung vòng 2 (arch-review, 2026-11-01 — KHÔNG đổi tham số §1-5)
- Ngày lễ nằm trong mùa BCTC được coi là NGOÀI mùa (cổng `fa_ratings_earnings_window_daily.sh --check`
  trả SKIP) ⇒ áp trần ngoài mùa (light 1/tuần, full 2/tuần); chặt hơn, chủ ý.
- Ngưỡng MoS≥25% gần như không lọc (RESULTS.md) ⇒ dòng khối 08:00 mang nhãn cố định "xếp việc DD, KHÔNG
  phải tín hiệu mua"; mã chọn chỉ là THỨ TỰ làm việc DD.
