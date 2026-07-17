# DCF upgrade — earning-power basis · GDP terminal growth · conditional refresh gate

> ĐÓNG 2026-07-17 (jobs `Taylor_20260717_063638` nghiên cứu → `Taylor_20260717_074106` triển khai).
> quant-skeptic **CONFIRMED high-confidence** (`mike/logs/verify_20260717_070358.log`).
> Full research writeup + implementation-status: `mike/agents/Taylor/dcf_earning_power_upgrade.md`.
> Owner: Taylor. Canonical model = `dcf_valuation.py` (FCFE, non-financial VN equities).

3 câu hỏi user, cả 3 đã KẾT LUẬN + TRIỂN KHAI (không còn "chờ user"):

## Việc 1 — earning-power basis thay FCFE → **NO-GO as replacement**
Earning-power (normalized 3Y-avg TTM net income) nâng raw IC (OOS 3M 0.073→0.119) + mở rộng coverage
+9k rows, NHƯNG **collinear 0.756 với 1/PE** và sau khi ⟂ 1/PE thì residual **IS sụp về ~0 (t−0.7)** —
đúng bẫy "composite-as-selector" (1/PE hút hết). FCFE giữ residual significant CẢ 2 window (lens tuyệt
đối thật). **Giữ FCFE làm basis margin-of-safety.** Earning-power chỉ dùng làm coverage-extension tùy
chọn cho tên FCFE-âm, KHÔNG bán là alpha mới.

## Việc 3 — GDP terminal growth → **LEVEL/DISPLAY fix, KHÔNG alpha** → wire `cap_rf` làm default
Terminal g **KHÔNG đổi cross-sectional edge** (IC phẳng mọi mode — g giống nhau mọi ticker/ngày →
differences-out khỏi within-month rank). Naive full-GDP (9.6%) fragile: 23% release chạm Gordon guard.
**Đã chốt `cap_rf`** (Damodaran: `g_term = min(cpi + long-run real GDP, risk-free)` = 6.80% @2026-06)
= 0% Gordon-clamp, IC không đổi, %cheap universe 55→69 (đo thật asof 2026-06-15; báo cáo ~57→66) —
DCF không còn "đọc mọi thứ RICH". **Đã đổi default hiển thị của `dcf_valuation.py` CPI→cap_rf** (job
074106): `DEFAULT_TERM_MODE = os.environ.get("DCF_TERMINAL_MODE","cap_rf")`, override qua env
`DCF_TERMINAL_MODE` hoặc `fair_value(term_mode=)` / CLI `--term`. **An toàn vì DCF non-decisional trong
production** (strategies.py chỉ ECHO cảnh báo, không chặn lệnh; custom_basket DCF overlay OFF mặc định
`BASKET_DCF_MODE=""`). Nguồn GDP mới: `gdp_growth_vn.py` (World Bank NY.GDP.MKTP.KD.ZG, 15y-avg 6.22%),
đã vào `data_registry.md`.

## Việc 2 — conditional refresh gate → **DONE + cron LIVE ngày 11**
`dcf_refresh_gate.py`: recompute DCF **chỉ khi** lãi suất Big-4 12M dịch **≥1.0pp** (boundary =1.0pp
**INCLUSIVE — CHỐT**, flag `THRESHOLD_INCLUSIVE=True`); else giữ số. State `data/dcf_refresh_state.json`
(atomic) + log append. Fail-safe: lỗi → refresh=True. Selfcheck 24/24 PASS. **Cron cài thật**
`10 1 11 * *` = 08:10 ICT ngày 11 hàng tháng (SAU deposit-rate ngày 3), user approved trực tiếp — xem
`kb/cron_registry.md`.
