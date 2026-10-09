---
kind: config
status: CANONICAL
source: SBV refi-rate (sbv_macro_overlay)
group: macro
role: input Pillar A (macro gate DT5G)
writer: sbv_macro_overlay.py (người sửa tay); verify log data/sbv_verify_log.json do sbv_policy_verify.py ghi (cron Mon 08:05 qua refresh_deposit_cctg_weekly.sh)
---

# SBV refi-rate (`sbv_macro_overlay`)

**Status: CANONICAL**

## Là gì
Input Pillar A (macro gate DT5G).

## Ai ghi / cadence
`SBV_REFI_EVENTS` trong `sbv_macro_overlay.py` — CHỈ người sửa tay (không script nào tự ghi).
Kiểm hằng tuần: `sbv_policy_verify.py` (chuỗi 4 của `refresh_deposit_cctg_weekly.sh`, Thứ Hai 08:05
ICT, từ 2026-10-09; thay `check_sbv_weekly.sh` thứ Sáu đã retire). Nguồn A = `sbv.gov.vn/vi/lãi-suất1`
(script tự fetch, UA trình duyệt); nguồn B = ≥1 nguồn khác chủ do agent cite. Ghi
`data/sbv_verify_log.json`: `verified_at` (lần cuối LẤY ĐƯỢC SỐ + khớp nguồn B + khớp
`SBV_REFI_EVENTS`) tách `attempted_at` (mọi lần thử); `last_verified` = ngày của `verified_at`
(cho `macro_healthcheck.py` INFO). Lãi NHNN ≠ `SBV_REFI_EVENTS` ⇒ 🔴 Trading Daily, KHÔNG tự sửa.

## Bẫy
- **`last_verified` trước 2026-10-09 KHÔNG đáng tin**: `check_sbv_weekly.sh` đẩy nó cả khi fetch
  hỏng (`fetch_failed_assumed_unchanged`) — hỏng MỌI tuần 2026-07-03→10-09 (URL cũ 404 + WAF chặn
  UA bot). Định dạng cũ còn ở `legacy_history`; mốc kiểm thật dùng `verified_at`.
- Trang NHNN ghi "Ngày áp dụng 19/03/2023" cạnh QĐ 1123/QĐ-NHNN ngày 16/06/2023 (sự kiện thật
  19/06/2023) — lỗi hiển thị phía NHNN; `sbv_policy_verify.py` chỉ so LÃI, không so ngày.
