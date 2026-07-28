---
kind: reference
group: cron-detail
title: papertrade_daily.sh (15:30) — step nội bộ đáng chú ý
belongs_to: ../cron_registry.md  # dòng bảng chính 15:30
---

# §papertrade_daily.sh (15:30) — step nội bộ đáng chú ý

> Chi tiết kỹ thuật của 1 cron cụ thể (`papertrade_daily.sh`, 23 step) — tách khỏi bảng chính vì
> không cần đọc mỗi lần tra lịch tổng. Bảng chính (dòng 15:30) chỉ trỏ tới đây.

`[1] pull_us_market` (Pillar B feed) → `[2] refresh_lagged_caches` (input LAG live) → `[3] snapshot_state_vintage`
→ `[4] macro_healthcheck` (ghi `macro_health.json`, input fail-safe `get_gated_state`) → `[6]`/`[6b] custom30_history`
(blend audit / **production** `custom30v_8l`) → `[7][8][11][12] pt_v11/pt_v12/pt_v4/pt_v22` (control-arm
`engine_room_oos` panel, review 2026-12-01 — **pt_v22 là PRODUCTION**, đọc bởi `trading_bot/strategies.py`)
→ `[14] papertrade_compare` (ghi `compare5.csv`, đọc bởi registry 15:20) → `[17] orb_pt` (trial mở, event-end)
→ `[19][20][21][22]` alerts/feeds (`[22] edge_health_monitor --refresh` — rebuild `data/lag_edge_health.csv`
vô điều kiện mỗi lần chạy; dừng ở 2026-05-11 là ĐÚNG lịch sử mùa vụ (zero sự kiện NP_R 05-05→07-07),
KHÔNG phải bug — điều tra + đóng 2026-07-12, `Taylor_20260712_155038`) → `[26] phosphorus_dgc_weekly`
(Fri only). Block RETIRED `[15][16][18][23][24][25]`
giữ nguyên comment-out (archive pattern, KHÔNG xoá — xem coding_guidelines §10).

↩ [Về cron_registry (bảng chính)](../cron_registry.md) · [index nhóm cron-detail](index.md)
