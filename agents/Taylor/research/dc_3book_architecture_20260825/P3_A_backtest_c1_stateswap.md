# Giai đoạn 3, Phần A — Backtest thật: C1 state-conditional BULL-only LAG→DC swap

Job `Taylor_20260825_153800` (dispatch Mike). Script: `exp_dc3book_c1_stateswap_20260825.py`.
Output: `exp_dc3book_c1_stateswap_univpit.csv` (daily), `exp_dc3book_c1_stateswap_metrics.csv`.

## Phương pháp

Hai bucket dollar: `V_bal` (luôn ăn r_BAL, nav_bal_ref pct-change) + `V_slot` (ăn r_LAG khi
state≠BULL, r_DC khi state=BULL). Target weight `w_slot_tgt(t)` = **`w_lag_tgt(t)` đọc thẳng từ
cột thật trong CSV production** (golive-audit) — không hardcode 0.46. Band ±10pp quanh target
(cùng quy ước phase 2 Phần A). r_DC dùng đúng convention state-gated park (@0.80 chỉ NEUTRAL) như
phase 2. Turnover cost: mỗi lần regime flip (LAG↔DC, do state cắt qua/ra khỏi BULL) tính TC 0.1%
mỗi chiều = 0.2% round-trip trên TOÀN BỘ dollar của `V_slot` ngày đó — giả định thanh lý/tái xây
100%, không có overlap giữa danh mục PEAD của LAG và danh mục double-confirm bank/securities của
DC (đúng vì đây là 2 rổ mã khác nhau thật).

## Kết quả

| config | window | CAGR% | Sharpe | Sortino | MaxDD% | Calmar | N |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline_2book_prod (V2.4 thật) | FULL | 29.33 | 1.81 | 2.40 | -18.3 | 1.60 | 2965 |
| baseline_2book_prod | IS 2014-19 | 26.63 | 1.63 | 2.35 | -18.3 | 1.46 | 1354 |
| baseline_2book_prod | OOS 2020+ | 31.65 | 1.98 | 2.42 | -17.5 | 1.80 | 1611 |
| **exp_c1_stateswap** | **FULL** | **29.98** | **1.79** | **2.29** | **-18.2** | **1.65** | 2965 |
| exp_c1_stateswap | IS 2014-19 | 26.09 | 1.61 | 2.31 | -18.2 | 1.43 | 1354 |
| exp_c1_stateswap | OOS 2020+ | 33.35 | 1.94 | 2.27 | -17.5 | 1.90 | 1611 |
| static_3book_dc33 (phase 2 REF) | FULL | 27.05 | 1.70 | 2.16 | -19.9 | 1.36 | 2965 |

(`baseline_2book_prod` ở đây là `combined_nav` thật của production, khác với baseline
`baseline_2book_park80_SAMEWINDOW` phase 2 Phần A — phase 2 dùng đúng cột này với cùng tên
nhưng in ra 29.33% full window giống hệt, xác nhận nhất quán giữa 2 job.)

**CAGR delta FULL (net of turnover cost): +0.65pp** (29.98 vs 29.33). Đây là con số nhỏ hơn NHIỀU
so với ước tính gross linear phase 2 (+4.19pp/năm combined gross BULL) — vì (a) đó là gross BULL-
period-only, không phải CAGR full-sample net; (b) turnover cost thật đáng kể.

## Self-check

`max weight-leak = 0.00e+00` — 0 VND leak, bucket weights luôn tổng = 1.0 theo cấu trúc.

## Turnover cost — số đo thật, không ước tính

- **20 lần flip regime** trong 11.9 năm (1.68/năm), tương ứng **10 episode BULL** riêng biệt
  (2017-12, 2018-02→05, 2020-10, 2020-12→2021-03, 2021-07→12, 2024-01, 2024-05, 2025-03, 2025-05,
  2025-09→10, 2026-01→02).
- Turnover cost tích luỹ: **26.83%** trên 11.9 năm ≈ **2.26pp/năm drag**. Đây là chi phí LỚN —
  gần bằng toàn bộ phần lợi ích gross ước tính ở phase 2, giải thích vì sao CAGR net chỉ còn
  +0.65pp thay vì +4pp.
- Band rebalance (±10pp, tách biệt với turnover flip): 35 lần, cost tích luỹ 6.89%.

## ⚠️ Cảnh báo quan trọng — lệch IS/OOS

**IS (2014-2019) THUA baseline: 26.09% vs 26.63% (−0.54pp).** Toàn bộ lợi ích net dương đến từ
OOS (2020+): +1.70pp (33.35 vs 31.65). Sharpe/Sortino FULL cũng thấp hơn baseline nhẹ (1.79 vs
1.81 / 2.29 vs 2.40) — Calmar cao hơn (1.65 vs 1.60) nhờ MaxDD gần như không đổi (-18.2 vs -18.3).

Đây là dấu hiệu **CẦN THẬN TRỌNG**, không phải "GO" rõ ràng:
1. Lợi ích tập trung OOS trong khi backtest thường kỳ vọng edge ổn định/suy giảm nhẹ ngoài mẫu,
   không phải NGƯỢC LẠI (IS âm, OOS dương) — dạng lệch này có thể là may mắn thời điểm (2020+ có
   nhiều BULL episode "đẹp" hơn: covid rally 2020, 2021 breakout, 2024-2026) chứ không phải edge
   cấu trúc.
2. Chỉ **10 episode BULL độc lập** trong toàn mẫu — N sự kiện quá mỏng để tách "edge thật" khỏi
   "vài episode may mắn". Không đủ điều kiện chạy DSR/PBO có ý nghĩa thống kê (cần nhiều hơn 10
   quan sát độc lập).
3. MaxDD/Sharpe không cải thiện rõ — cải thiện chủ yếu ở CAGR/Calmar, tức là lợi nhuận tuyệt đối
   tăng nhẹ nhưng risk-adjusted không thuyết phục hơn baseline.

## Kết luận Phần A

**C1 net dương nhưng KHIÊM TỐN VÀ CHƯA ĐỦ TIN CẬY để đề xuất wire production.** +0.65pp CAGR sau
turnover cost thật, tập trung hoàn toàn ở OOS, N=10 episode BULL độc lập — dưới ngưỡng thống kê
đáng tin theo `quant-research` skill (không đủ N để DSR/PBO có ý nghĩa). Không phải NO-GO dứt
khoát (không có bằng chứng phản bác như C2), nhưng **KHÔNG đạt threshold để override quant-skeptic
gate mà không có thêm dữ liệu/robustness check** (walk-forward theo nhiều cửa sổ hơn 2, hoặc chờ
thêm episode BULL tương lai tích luỹ N).

**Khuyến nghị**: giữ như một hướng "theo dõi", không wire ngay. Nếu muốn tăng độ tin cậy: (a) chia
nhỏ hơn 2 cửa sổ IS/OOS (vd 3-4 cửa sổ rolling) để xem lợi ích OOS có nhất quán qua từng sub-period
hay chỉ 1-2 episode kéo toàn bộ số lên; (b) so sánh với việc KHÔNG chuyển gì cả nhưng đổi band để
giảm số lần flip (giảm turnover cost) — có thể cân bằng lại tốt hơn.
