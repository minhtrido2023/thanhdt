# Charter — Vol-scale buy chase-cap (patch#3) (`vol_scale_chase_cap`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-07-01 · **Kết thúc dự kiến:** mở (event-anchored)

## 🎯 Mục đích

Nới trần đuổi mua theo realised vol 20d (clamp(k·rvol, static, ceil), k=2.0/ceil=0.04, monotone-safe, fail-safe về static) có wiring đúng trên quote thật không? (executor-path stress đã PASS 15/15)

## 📅 Nghiệm thu / mốc kết thúc

10 phiên EVIDENCE (executor chạy thật trên paper main) từ phiên thật đầu tiên 2026-07-07 → ước ~2026-07-20. Mốc cũ 2026-07-14 bỏ — 07-01→07-06 flag bật nhưng 0 phiên executor = 0 evidence, không đếm.

## ✅ Tiêu chí GO/NO-GO

- ✅ (pass) Executor-path stress 15/15 PASS (wiring · WIDEN clamp-to-ceil · MONOTONE · fail-safe rvol absent/0/<0 · NEG-control) — stress_vol_scale_chase_cap.py — CHẠY LẠI 2026-08-04 trên code hiện tại: RESULT PASS (14 assert: config wiring 4, WIDEN 2, MONOTONE 1, FAIL-SAFE 3, LIMIT-PRICE 2, NEG-control live 2). Lần chạy này đi THẬT qua nhánh fail-safe ('no chunks → fail-safe').
- ✅ (pass) Paper sạch: wiring đúng trên quote thật + fail-safe khi thiếu rvol cache — Đo 2026-08-04 trên 80 lệnh BUY THẬT / 13 phiên executor paper main (07-07→07-27). rvol_20d nạp thành công 80/80 (0 lần rơi fail-safe) → wiring sống trên quote thật; trần nới luôn nằm trong [static 1,5%; ceil 4,0%], max chase quan sát +1,95% < ceil. Trần THỰC SỰ chạm 3/80 lệnh (2 lệnh bị clip đúng vol-cap, 1 lệnh cross ở ask nằm giữa static-cap và vol-cap). CAVEAT: nhánh fail-safe khi THIẾU rvol cache chưa từng xảy ra trên paper (cache luôn đủ) — bằng chứng đến từ stress harness chạy qua Executor thật, không phải từ 1 phiên paper.
- ✅ (pass) Không can thiệp NORMAL-path ngày non-gap — Cô lập code: `_buy_chase_pct` chỉ có ĐÚNG 1 call-site (executor.py:426, nhánh BUY của _limit_price) — sell-path/dip-cross/gap-adaptive không chạm. Đo thực nghiệm: 77/80 lệnh (96,3%) giá đặt GIỐNG HỆT chân static; 3 lệnh lệch: MBB 07-07 +50đ (+0,19% vs giá static), HDB 07-07 +50đ (+0,18%), ACB 07-16 +150đ (+0,64%). Cả 3 rơi vào phiên mã chạy +1,77%..+2,81% TRONG PHIÊN (gap mở cửa +0,37%/−0,37%/−0,65% → không phải ngày gap-up mở cửa). Không có ca nào lệch trong ngày giá nằm gọn trong ±1,5%. ⚠️ Đọc chữ 'ngày non-gap' theo NGHĨA ĐEN thì 3 ca này là lệch — chờ user phân xử ở cổng sign-off.
- ⏳ (pending) Skeptic rerun REAL-fill vs min(open,L) proxy trên correlated gap-up @NAV target — BLOCKED — KHÔNG đóng được bằng harness paper hiện tại (đo 2026-08-04): (1) 80/80 lệnh khớp ĐÚNG BẰNG giá limit đã đặt → PaperBroker mô phỏng, ZERO dữ liệu fill thật; (2) quy mô ~343tr/phiên vs NAV target 50B (~0,7%) → không kiểm được size-impact, đúng chỗ quant-skeptic gọi killer objection; (3) base-rate sáng gap-up TƯƠNG QUAN RỘNG (≥50% rổ 6 mã có open > prev_close×1,015) = 10/642 phiên 2024-01→2026-08 = 1,56% (~1 lần/64 phiên ≈ 3 tháng); cửa sổ evidence 20 phiên có 0 lần. Chờ thêm trên paper KHÔNG bao giờ đóng được vì fill là mô phỏng → cần user chọn hướng (re-scope / live pilot size nhỏ / park).
- ⏳ (pending) User sign-off trước khi bật live

## ℹ️ Ghi chú vận hành

Cap-widen KHÔNG có marker riêng trong journal (áp silent trong _buy_chase_pct) — đo qua stress script + so limit price ngày gap-up; cần phiên executor paper + ngày gap mới có evidence tự động. Từ 2026-07-07: probe harness chạy paper main mỗi ngày (6 BUY/phiên trên quote thật — xem entry extreme_regime cho cron). | 2026-08-04 (job Taylor_20260804_091700): kiểm checkpoint bằng dữ liệu thật — báo cáo mike/agents/Taylor/research/vol_scale_chase_cap_checkpoint_20260804.md. Từ 2026-07-28 probe harness netting nội bộ (INTERNAL_ONLY/NETTED) nên 0 lệnh BUY tới executor → luồng evidence dừng.

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/execution_logs/exec_main_*_journal.csv`
- `secrets/trading_bot_accounts.json (chase_cap_vol_scale_enabled=true, chỉ paper main)`
- `stress_vol_scale_chase_cap.py`
