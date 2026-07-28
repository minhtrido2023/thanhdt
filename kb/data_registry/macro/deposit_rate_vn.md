---
kind: config
status: CANONICAL-PROXY
source: deposit_rate_vn.py (DEPOSIT_EVENTS + data/deposit_rate_vn_events.csv append-only)
group: macro
role: LIVE production input qua current_deposit_rate()
writer: 26 mốc frozen 2026-06-19 + CSV append-only (routine Layer A cài 2026-07-17)
---

# `deposit_rate_vn.py` (`DEPOSIT_EVENTS` + `data/deposit_rate_vn_events.csv` append-only)

**Status: CANONICAL-PROXY**

## Là gì
Big-4 (VCB/BIDV/CTG/Agribank) lãi suất tiết kiệm 12M, step-series 26 mốc frozen 2011→2026-06
(hardcode) + CSV extension append-only cho mốc tương lai, forward-fill.

## Ai ghi / cadence
26 mốc frozen calibrate **1 lần** (2026-06-19) từ hình dạng lending-rate Trading Economics 1999-2023 +
vài mốc web Big-4 (KHÔNG sửa lại — caveat b). **ĐÃ có refresh routine Layer A (cài 2026-07-17,
`Winston_20260717_072420`)**: cron `refresh_deposit_rate_vn.sh` 08:10 ICT ngày 3 hàng tháng chỉ NHẮC
Discord + best-effort fetch (KHÔNG tự ghi); con người xác nhận rồi chạy `append_deposit_rate.py
--rate --effective --source` append 1 dòng CSV (chỉ effective_date > 2026-06-01 mới có hiệu lực =
point-in-time thật). Freshness WARN >45 ngày ở `ops_health_check.sh` §8.

## Bẫy
3 caveat bắt buộc đọc trước khi dùng: **(a)** chỉ phủ Big-4, chưa có chuỗi top10 ngoài nhóm này;
**(b)** toàn bộ 26 mốc được neo hồi tố CÙNG 1 lần ngày 2026-06-19 — KHÔNG phải point-in-time thật cho
quá khứ, mọi backtest chạy trên lịch sử (kể cả dự án Pillar A′ đang pre-registered,
`Taylor_20260713_124803`) mang bias hindsight biết trước, chỉ mốc THÊM MỚI từ nay trở đi mới có thể là
point-in-time thật; **(c)** đang là input **LIVE production** qua `current_deposit_rate()`: (i)
`rating_8l.py` gentle NEUTRAL-only deposit tilt ±0.03 trên `value_score_v3` (validated 2026-06-19, chạy
mỗi ngày trong `pt_8l_daily.sh` 17:45 ICT — KHÔNG dormant, ảnh hưởng rating sống mỗi ngày), (ii)
deposit-gate RECOVERY_PARK floor 7.5% (dormant từ 2013). Routine cập nhật tháng (Layer A):
`mike/agents/Winston/proposal_deposit_rate_monthly_refresh_20260713.md` (job `Winston_20260713_131255`)
— **ĐÃ duyệt + cài đặt 2026-07-17** (`Winston_20260717_072420`): CSV append-only +
`append_deposit_rate.py` + cron nhắc ngày 3 + WARN freshness; **(iii) `dcf_valuation.py` +
`dcf_backtest.py`** (DCF 2-stage FCFE — dùng `current_deposit_rate()` làm risk-free rate baseline, job
Taylor_20260714_051643, research tool, NOT wired production).
