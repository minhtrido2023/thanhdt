---
name: daily_financial_news_service_plan_2026
description: Kế hoạch tương lai — service tin tức tài chính hằng ngày (gánh nhắc SBV + feed tin)
metadata: 
  node_type: memory
  type: project
  originSessionId: 4fb305f6-9ad2-4e2f-9dfd-b054819e2145
---

User ([REDACTED]) muốn **sau này xây 1 service cập nhật tin tức thị trường tài chính hằng ngày**. Service đó sẽ gánh luôn việc theo dõi **thay đổi chính sách SBV** (lãi suất điều hành) — hiện đang là constant thủ công `SBV_REFI_EVENTS` trong `sbv_macro_overlay.py` + task nhắc `sbv_macro_tracker.py update` (task này CỐ Ý không migrate; chỉ để nhắc user tự cập nhật khi SBV đổi chính sách).

→ Khi build service tin tức: tích hợp tự-phát-hiện sự kiện đổi lãi suất SBV → cập nhật `sbv_refi_events.json` (Pillar A của macro-gate DT5G đọc list này) thay cho việc nhắc thủ công. Có thể mở rộng nuôi các tín hiệu khác (P4/commodity news, sự kiện vĩ mô). Liên quan [[server_bq_write_and_v34b_refresh_2026]] (hạ tầng cron server), DT5G macro-gate Pillar A.
