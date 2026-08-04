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
- ⏳ (re-scoped) Skeptic rerun REAL-fill vs min(open,L) proxy trên correlated gap-up @NAV target — RE-SCOPED 2026-08-04 (user PHƯƠNG ÁN A) — RE-SCOPED, KHÔNG phải pass. User (John) chốt 2026-08-04 phương án A: chấp nhận KHÔNG đo được real-fill-vs-proxy bằng paper. Nguyên văn: 'Vol-scale vì là bước bảo hiểm rẻ tiền, tôi đồng ý chọn A cho go-live.' | LÝ DO KHÔNG ĐO ĐƯỢC (đo 2026-08-04, job Taylor_20260804_091700): (1) PaperBroker mô phỏng fill ĐÚNG BẰNG giá limit đã đặt (80/80 lệnh, sai lệch 0/80) → paper KHÔNG BAO GIỜ sinh ra fill thật để so với proxy min(open,L), đây là sai công cụ đo chứ không phải thiếu thời gian; (2) quy mô probe paper gross ~343tr/phiên vs NAV target 50 tỷ ≈ 0,7% → không kiểm được size-impact (đúng chỗ quant-skeptic gọi killer objection); (3) base-rate sáng gap-up TƯƠNG QUAN RỘNG (≥50% rổ 6 mã open > prev_close×1,015) = 10/642 phiên 2024-01→2026-08 = 1,56% (~1 lần/64 phiên ≈ 3 tháng), cửa sổ 20 phiên evidence có 0 lần. | RỦI RO CÒN TREO ĐƯỢC CHẤP NHẬN TƯỜNG MINH: size-impact ở quy mô NAV 50 tỷ chưa từng được kiểm. Giảm nhẹ (không xoá): NAV live thực tế 2026-08-04 = SpaceX 965tr + ZaloPay 907tr ≈ 1,9% NAV target 50 tỷ, tức quy mô lệnh live hiện tại CÙNG BẬC với quy mô paper đã đo (paper_init_cash 1 tỷ) — regime chưa kiểm (50 tỷ) KHÔNG phải regime đang deploy hôm nay. Nếu NAV tiến gần 50 tỷ thì phải mở lại câu hỏi này.
- ✅ (pass) User sign-off trước khi bật live — 2026-08-04 (job Taylor_20260804_124404): user John sign-off phương án A cho go-live ('Vol-scale vì là bước bảo hiểm rẻ tiền, tôi đồng ý chọn A cho go-live'). quant-skeptic verify quyết định re-scope gate 4 + đề xuất flip live: **CONFIRMED / confidence high** (log mike/logs/verify_20260804_124744.log) — independent recompute khớp: base-rate gap-up 10/642=1,5576%, NAV live SpaceX/ZaloPay ~1,8-1,9% NAV target 50B, 5 script chạy lại ALL-PASS, và skeptic tự xác minh trong brokers.py::_try_fill rằng PaperBroker khớp đúng giá đặt (⇒ gate 4 đúng là RE-SCOPE, không phải PASS). 3 recommended_reruns đã ghi nhận: (i) mở lại gate 4 khi NAV live tiến gần 50B / gross lệnh vượt ~343tr/phiên, (ii) verify lại cờ hiệu lực của account RocketX (enabled=false) TRƯỚC khi cho nó giao dịch, (iii) xử lý netting nội bộ probe harness.

## ℹ️ Ghi chú vận hành

Cap-widen KHÔNG có marker riêng trong journal (áp silent trong _buy_chase_pct) — đo qua stress script + so limit price ngày gap-up; cần phiên executor paper + ngày gap mới có evidence tự động. Từ 2026-07-07: probe harness chạy paper main mỗi ngày (6 BUY/phiên trên quote thật — xem entry extreme_regime cho cron). | 2026-08-04 (job Taylor_20260804_091700): kiểm checkpoint bằng dữ liệu thật — báo cáo mike/agents/Taylor/research/vol_scale_chase_cap_checkpoint_20260804.md. Từ 2026-07-28 probe harness netting nội bộ (INTERNAL_ONLY/NETTED) nên 0 lệnh BUY tới executor → luồng evidence dừng. | 2026-08-04 (job Taylor_20260804_124404): user chốt phương án A → gate 4 re-scoped, chương trình paper ĐÓNG (luồng evidence paper main đã chết từ 07-28 do netting nội bộ, và kể cả sống lại cũng không đóng được gate 4). Bước kế: quant-skeptic verify rồi mới flip chase_cap_vol_scale_enabled ở live.

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/execution_logs/exec_main_*_journal.csv`
- `secrets/trading_bot_accounts.json (chase_cap_vol_scale_enabled=true, chỉ paper main)`
- `stress_vol_scale_chase_cap.py`
