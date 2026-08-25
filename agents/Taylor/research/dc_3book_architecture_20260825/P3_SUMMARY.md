# SUMMARY — DC (Alpha Lens) 3-book architecture, giai đoạn 3

Job `Taylor_20260825_153800` (dispatch Mike). Tiếp nối giai đoạn 2 (job `_151108`) — user đã
approve cả 3 hướng: (A) backtest thật C1, (B) validate ma trận C3 bằng bootstrap+OOS, (C) capacity
sizing DC universe.

## Verdict tổng hợp

**C1 (state-conditional BULL-only LAG→DC swap): NET DƯƠNG NHƯNG KHIÊM TỐN, CHƯA ĐỦ TIN CẬY ĐỂ
WIRE.** Backtest thật (real w_lag_tgt(t), turnover cost thật ~2.26pp/năm drag): CAGR FULL +0.65pp
(29.98% vs baseline 29.33%), Sharpe/Sortino không cải thiện, Calmar nhích lên (1.65 vs 1.60). Toàn
bộ lợi ích net dương tập trung OOS (2020+, +1.70pp) — IS (2014-19) THUA baseline (-0.54pp). N=10
episode BULL độc lập trong 11.9 năm — không đủ cho DSR/PBO có ý nghĩa.

**Phần B GIẢI THÍCH TRỰC TIẾP vì sao**: bootstrap CI + OOS 3-giai-đoạn cho thấy leadership DC-vs-
LAG trong BULL KHÔNG ổn định qua thời gian — đảo ngược hoàn toàn giữa 2017-2020 (BAL dẫn áp đảo
50.3%, DC ÂM -2.9%) và 2020-nay (DC dẫn 52.9%). Đây không phải nhiễu backtest ở Phần A, mà là bản
chất thống kê thật của factor leadership trong BULL. Chỉ 2/5 state đủ tin cậy cho state-adaptive
design: **CRISIS** (DC dẫn nhất quán cả 3 giai đoạn lịch sử, dù CI rộng vì variance ngày cao) và
**NEUTRAL** (DC thua CẢ BAL LẪN LAG, CI 90% pooled không chứa 0, nhất quán 3 giai đoạn — kết luận
phủ định chắc chắn nhất). BEAR/BULL/EXBULL đều CHƯA đủ tin.

**Phần C: capacity KHÔNG còn "không phải rào cản"** như phase-2 kết luận — ở quy mô 200B
(SpaceX+ZaloPay gộp) và kịch bản trọng số nặng hơn (w_DC=0.46, đúng kịch bản C1 đang theo dõi):
- **DHG, MSH: đề xuất LOẠI KHỎI DC UNIVERSE** (vượt 100% ADV ở mọi kịch bản, cap an toàn <0.2%
  NAV — không đáng công thực thi). Còn 14/16 mã.
- **10/16 mã còn lại CAP_NEEDED** (vượt 5% ADV ở NAV=200B): MBB/HDB/VCB/VCI/VND/HCM/PVT/HAH/CTR/DBC.
- **Chỉ 4/16 mã (ACB/TCB/SSI/FPT) an toàn không cần cap** ở mọi kịch bản.
- **3/4 mã Securities (VCI/VND/HCM) CẦN CAP ở 200B** — khác kết luận phase-2 "cả 4 đều an toàn"
  (kết luận đó đúng cho kịch bản NHẸ hơn w=1/3 và không tách theo NAV 200B; SSI vẫn là mã Securities
  duy nhất an toàn mọi kịch bản).

## Khuyến nghị

1. **KHÔNG wire C1 ngay** — net dương nhưng dưới ngưỡng tin cậy thống kê (N=10 episode, lợi ích
   chỉ ở OOS, Phần B xác nhận leadership BULL không ổn định qua thời kỳ). Giữ hướng "theo dõi",
   không phải "GO" hay "NO-GO dứt khoát" như C2.
2. **Nếu bất kỳ lúc nào tiến tới wire** (C1 hoặc bất kỳ biến thể DC nào khác) — BẮT BUỘC áp dụng
   cap riêng theo bảng Phần C trước, không dùng cap cứng 0.20/mã mặc định cho 10 mã CAP_NEEDED, và
   loại DHG/MSH khỏi universe trước.
3. **Ma trận factor×regime (C3, hướng dài hạn phase-2 khuyến nghị #2)**: chỉ nên thiết kế
   state-adaptive weight cho CRISIS và NEUTRAL ngay bây giờ (đủ bằng chứng cross-period); BULL/BEAR/
   EXBULL cần chờ thêm dữ liệu lịch sử hoặc dùng cơ chế thích ứng mềm hơn, tránh hard-code theo
   điểm-ước-lượng đơn (rủi ro overfit vào giai đoạn 2020+, đã chứng minh cụ thể ở BULL).
4. **Không theo đuổi thêm ở vòng này**: đã đủ 3 mảnh dispatch yêu cầu. Bước tiếp theo (nếu có) là
   quant-skeptic pass đầy đủ trước khi bất kỳ phần nào của C1/C3 được đề xuất đưa vào
   `pt_v23_audit_2014.py`/`trading_rules.json` thật — theo đúng §18 coding_guidelines.

## File trong thư mục này (bổ sung giai đoạn 3)

- `exp_dc3book_c1_stateswap_20260825.py` — Phần A (+ `exp_dc3book_c1_stateswap_univpit.csv`,
  `exp_dc3book_c1_stateswap_metrics.csv`)
- `exp_dc3book_bootstrap_20260825.py` — Phần B (+ `exp_dc3book_bootstrap_ci.csv`,
  `exp_dc3book_oos_stability.csv`)
- `exp_dc3book_capacity_20260825.py` — Phần C (+ `exp_dc3book_capacity_sizing.csv`)
- `P3_A_backtest_c1_stateswap.md`, `P3_B_factormatrix_bootstrap.md`, `P3_C_capacity_sizing.md`,
  `P3_SUMMARY.md` (file này)
