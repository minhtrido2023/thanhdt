# A/B cross-mode (ab_cross vs ab_dip) — PARKED

> Gỡ khỏi `paper_programs_registry.json` (mảng `programs`, không còn render trong Paper Programs
> Daily Report lặp lại hàng ngày) 2026-07-15, job `Winston_20260715_084136`, user duyệt. Đã PAUSED
> từ 2026-07-07 — mục này chỉ chuyển từ "hiện diện PAUSED mỗi ngày trong report" sang "lưu trữ ở
> đây", không đổi trạng thái thật (vẫn paused, vẫn không có cron ab_cross/ab_dip nào chạy).

## Lý do park (khỏi report hàng ngày)

- Đã PAUSED từ 2026-07-07 (quyết định gốc: job `Taylor_20260707_071130`), 0 phiên từng chạy.
- Câu hỏi gốc ("chế độ đặt lệnh nào cho fill price tốt hơn NET — cross ngay vs chờ dip") đã được
  trả lời bằng đường khác: `cross_mode = "adaptive"` được chọn làm **production default** từ
  2026-06-26 (user + Taylor). Backtest lúc đó: always-TWAP hơn dip 3.5bps fill-rate nhưng variance
  gấp đôi; adaptive beat cả hai lựa chọn tĩnh.
- Không có mốc thời gian nào để xem lại (`end_or_trigger` chỉ ghi ngày PAUSED, không có điều kiện
  mở lại theo lịch) — hiển thị PAUSED giống hệt nhau mỗi ngày trong report daily là vô ích, không
  mang thêm thông tin cho người đọc.

## Điều kiện để mở lại (re-add vào registry nếu cần re-test)

- **NAV lớn hơn đáng kể** so với hiện tại — ở NAV nhỏ, khác biệt fill price giữa 2 chế độ đặt lệnh
  tĩnh (cross ngay vs chờ dip) không đủ ý nghĩa kinh tế để tách A/B; câu hỏi này chỉ đáng đo lại khi
  quy mô lệnh đủ lớn để basis-point fill difference tác động NAV thật.
- Nếu mở lại: cần 2 account paper chạy song song đủ mẫu (gate criteria gốc chưa từng đạt — "Cả 2
  account A/B có phiên chạy song song đủ mẫu" và "Khác biệt fill price có ý nghĩa thống kê" đều vẫn
  `pending`, chưa từng có bằng chứng nào tích lũy).

## Toàn bộ entry gốc (nguyên văn từ registry, không mất thông tin)

```json
{
  "id": "ab_cross",
  "name": "A/B cross-mode (ab_cross vs ab_dip)",
  "owner": "Taylor",
  "status": "paused",
  "pause_reason": "PAUSED — chưa từng bắt đầu (0 phiên), và câu hỏi đã được trả lời bằng đường khác: cross_mode 'adaptive' được chọn làm production default từ 2026-06-26 (user+Taylor, backtest: always-TWAP hơn dip 3.5bps fill-rate nhưng variance 2×; adaptive beat cả hai). Giữ entry để mở lại nếu cần re-test ở NAV lớn.",
  "objective": "So sánh 2 chế độ đặt lệnh (cross ngay vs chờ dip) trên cùng plan — chế độ nào cho fill price tốt hơn NET?",
  "start": null,
  "end": null,
  "end_or_trigger": "PAUSED 2026-07-07 (quyết định trong job Taylor_20260707_071130) — không wire cron cho ab_cross/ab_dip.",
  "gate_criteria": [
    {"text": "Cả 2 account A/B có phiên chạy song song đủ mẫu", "status": "pending"},
    {"text": "Khác biệt fill price có ý nghĩa thống kê trước khi kết luận", "status": "pending"}
  ],
  "probe": {
    "type": "command",
    "cmd": ["python3", "bot_ab_report.py", "--days", "10"],
    "timeout": 120,
    "max_chars": 1200
  },
  "data_sources": [
    "bot_ab_report.py",
    "data/bot_paper_ab_cross.json",
    "data/bot_paper_ab_dip.json"
  ],
  "notes": "Tính đến 2026-07-07 account ab_cross chưa chạy phiên nào — report sẽ nói thẳng điều đó."
}
```

## Tham chiếu

- Quyết định PAUSE gốc: job `Taylor_20260707_071130`.
- Quyết định park khỏi report daily: job `Winston_20260715_084136`, dispatch từ Mike, user duyệt.
- Adaptive cross_mode production default: quyết định 2026-06-26 (user + Taylor).
