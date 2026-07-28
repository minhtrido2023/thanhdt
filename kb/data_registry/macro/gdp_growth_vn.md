---
kind: config
status: CANONICAL
source: gdp_growth_vn.py (GDP_ANNUAL)
group: macro
note: single-tier REAL (World Bank), CHƯA cài cron (refresh hàng năm low-urgency)
writer: fetch 1 lần 2026-07-17 (job Taylor_20260717_063638)
---

# `gdp_growth_vn.py` (`GDP_ANNUAL`)

**Status: CANONICAL (single-tier REAL, không proxy)**

## Là gì
Tăng trưởng GDP THỰC Việt Nam, annual — World Bank Open Data API `NY.GDP.MKTP.KD.ZG` ("GDP growth
annual %", growth của GDP giá cố định = REAL), chuỗi đầy đủ 26 năm 2000-2025 (long-run 15y avg =
6.22%).

## Ai ghi / cadence
Fetch **1 lần** 2026-07-17 (job `Taylor_20260717_063638`), WB `lastupdated`=2026-07-13; refresh
idempotent bằng `refresh_gdp_growth_vn.py` (re-fetch WB API, ghi đè `GDP_ANNUAL` atomic, chỉ khi
khác) — cadence **hàng năm, low-urgency**, CHƯA cài cron.

## Bẫy
Cùng nhà cung cấp với feed WB CMO commodity đã có (`auto_update_commodity_wb.*`). Dùng làm thành phần
real-growth của DCF terminal growth (`dcf_earning_power.py`, job Taylor_20260717_063638 — **research,
NOT wired production**; kết luận: GDP terminal g là level/display fix, KHÔNG phải alpha). 2 lưu ý: (a)
point-in-time `longrun_real_gdp(asof)` chỉ dùng năm ≤ asof.year−1 (năm đã công bố trọn); (b) PHẢI dùng
bình quân dài hạn 15-20y (đã fade sẵn hiệu ứng hội tụ + COVID trough), KHÔNG dùng năm gần nhất làm
terminal g vĩnh viễn (Damodaran convergence — dùng thẳng 7-8% hiện tại phóng đại grossly, hit Gordon
guard 23% releases).
