# REPORT — Trần sizing BAL khi sổ ít mã (job Taylor_20261022_095008)

PREREG: `PREREG.md` (md5 `6c278b95abe09fde87cb30c337e1b9e1`, ghi trước khi chạy số). READ-ONLY: không sửa
production, không pin. Engine chạy trong worktree `wt-balcap-20261022` (commit `f66dab18` + knob
`BAL_WMAX_NAV`, mặc định tắt; diff đầy đủ ở `engine_knob.patch`). Output engine nằm ở `data/v23_golive_audit_*_exp_<tag>_*.csv`
(tên non-canonical). Script: `q2q3_ledger.py` → `q2q3_pin0.json`; `legs_metrics.py` → `legs_metrics.json`; `logs/boot_*.log`.

## TL;DR
- **NO-GO cho trần.** Theo luật khoá trong PREREG, không mức w nào vừa giữ được CAGR (sàn nhiễu −0,46pp)
  vừa cải thiện MaxDD ≥0,46pp ở cả pin0% lẫn pin1M.
- **Không có lệch sizing live-backtest.** Công thức live trùng engine: 10% × sổ BAL. VPI 5,1% NAV nằm ở
  **p93** phân phối trọng số lệnh BAL backtest (p92 khi n_bal=1), tức đầu cao nhưng vẫn trong dải.
- **Đính chính job trước.** Câu "sổ BAL backtest luôn đa dạng hoá" là **SAI**. Backtest có 0 mã ở 39% số ngày,
  1-2 mã ở 22%, trung vị 2 mã. Cửa sổ sổ 1-2 mã **không** có đuôi tệ hơn sổ ≥3 mã, mà theo chiều ngược lại
  (Fisher p=0,24).
- Lỗ −1,07% NAV của VPI là gần mức trần cơ học của sổ 1 mã: 5,1% × stop −21%. Nó hiếm trong cửa sổ ít mã
  (1/26) vì sổ ít mã có phơi nhiễm nhỏ, chứ không phải vì sizing sai.

## Q1 — Cơ chế sizing (code)
- Engine: `simulate_holistic_nav.py:1129-1132` đặt `target_value = cur_nav × tier_weight[play_type]`, trong đó
  cur_nav = NAV sổ BAL (cash + ETF park + cổ phiếu + pending). **Không phụ thuộc n_bal**: không chia
  1/n mà là slot cố định. Nếu thiếu tiền thì `target = 0,95 × cash` (`:1193-1194`). Hàm chỉ chia
  1/max_positions khi không có tier weight.
- Trọng số: `regime_size_overlay.py:25-26` FULL 10%, WEAK 5% (8L ≥4, **chỉ áp trong BEAR/CRISIS**,
  `:27,102`). BAL_KW: `pt_v23_audit_2014.py:2007` (max_positions 12 `:731`, stop −20%, hold 45, sector 8 tối đa 4,
  RE_BACKLOG miễn).
- Sổ BAL trong hệ: `pt_v23_audit_2014.py:2148-2170`. Combined = cap_bal + cap_lag, band allocator ±10pp
  quanh w_LAG {CRISIS 0,5 / BEAR 0 / NEUTRAL+ 0,65 hoặc 0,50 theo edge}. Vì vậy **%NAV hệ của một lệnh ≈ 10% × s**,
  s = cap_bal/combined. Đo được: s trung vị 0,49; NEUTRAL 0,49; BULL 0,36; **BEAR 1,0** (lệnh BAL lúc này = 10% NAV hệ).
- Live: `deploy_golive_dt5g_v4/golive_recommend_v23.py:94` (`POS_PCT=0.10, WEAK_PCT=0.05`), `:762`, `:1183`
  (`weight_base="BAL_book"`). Plan quy ra VND theo `BAL_book = active_nav × (1 − w_lag_current)`, vd
  `plan_SpaceX_2026-09-17.json` sizing_note: 977,18tr × (1−0,4788) × 10% = 50,93tr.
- **Trần hiện có**: `trading_rules.json` `sizing.name_cap_pct=0.10` (10% NAV/mã) và
  `execution_limits.max_value_per_order_pct=0.05` (5% NAV/lệnh mẹ, bot chia nhỏ ≤200tr). **Không có trần
  % NAV riêng cho BAL theo n_bal.**
- ⚠️ Ghi nhận phụ: công thức quy VND trong plan là văn xuôi do DollarBill viết, không phải code, và đã từng
  trôi. Plan 05/08 (VIC, không khớp) ghi "slot 10% active_nav = 95,56tr", tức gấp khoảng 2 lần công thức BAL_book.
  Plan 31/07 (AGG) ghi "BAL 50% NAV". Từ 16/09 các plan đều dùng đúng BAL_book. Tôi không đo thêm phần này.

## Q2 — n_bal và trọng số (ledger R3 pin0% `4707bcbe`)
| | Backtest |
|---|---|
| Ngày n_bal = 0 / 1-2 / ≥3 | **39,3% / 22,0% / 38,8%** (trung vị 2; trung vị khi ≥1 = 4) |
| Trọng số %NAV hệ, mọi lệnh BAL (N=367) | trung vị 2,38%, p90 5,04%, max 6,62% |
| Không tính ABANDONED_REFUND (N=267) | trung vị 3,49%, p90 5,10% |
| n_bal=1 lúc vào (N=10, không ABANDONED) | trung vị 3,10%, max 5,12% |
| n_bal=2 (N=17) | trung vị 4,88%, max 5,18% |
| Số mã BAL mới mỗi 77 phiên (N=40 cửa sổ) | trung vị 4; 47,5% cửa sổ ≤3 mã |

**Live nằm ở đâu**: SpaceX 5,1% ở **p93** (n=1: p92). ZaloPay 2,6% ở p51. ZaloPay thấp hơn vì slot tính trên
active_nav 598tr (phần bot, `plan_ZaloPay_2026-09-17.json`) trong khi NAV tổng gồm cả DGC legacy.

**Vì sao live chỉ có 1 mã** (từ 77 file recommendations từ 01/07 tới nay, cộng plan): có đúng **3 mã BAL phát tín hiệu**
(AGG 30/07; VIC 04-05/08, 25/08-08/09; VPI 19/08-18/09), mỗi ngày nhiều nhất 2 mã. Mức này **bình thường** so với
backtest (trung vị 4 mã/77 phiên). Hai mã không mua được vì:
(1) **thiếu tiền**: AGG 31/07 cần 45,66tr, cash 4,53tr; VIC 05-06/08 cần 87tr, cash 4,82tr (deferred_reason trong plan);
(2) **signal_hold paper-track tới 16/09** (decided_by user 19/08) chặn VIC/VPI từ 26/08. Khi hold hết hạn, chỉ còn VPI
có tín hiệu.

## Q3 — Đuôi theo n_bal (cửa sổ 21 phiên không chồng lấn)
Tổng 147 cửa sổ. Loại 41 cửa sổ có CAPIT-B mở (P&L sleeve tính qua bal_stocks_ref có lẫn CAPIT) và 34 cửa sổ
n_bal(a)=0. P&L = sleeve cổ phiếu BAL quy về NAV hệ.

| n_bal đầu cửa sổ | N | trung vị | p05 | min | ≤ −0,70% | ≤ −1,07% |
|---|---|---|---|---|---|---|
| 1-2 | 26 | −0,06% | −0,59% | −1,22% | 1 | 1 |
| ≥3 | 46 | +1,04% | −3,46% | −5,72% | 7 | 6 |

Fisher 2 phía: ≤−0,70% p=0,24; ≤−1,07% p=0,41. **Không đo được đuôi dày hơn khi sổ ít mã**. Chiều
ngược lại mới đúng: đuôi xấu đến từ sổ nhiều mã (beta). Live SpaceX −1,07% ở p3,8% trong nhóm 1-2 mã. Cửa sổ này
hiếm, nhưng gần đúng mức trần cơ học w×stop.
Tỉ lệ STOP theo n_bal lúc vào: 1-2 mã 2/26 (7,7%), ≥3 mã 30/240 (12,5%), Fisher p=0,75. Các holding chồng thời gian
nên p chỉ mang tính mô tả.

## Q4 — Overlay trần w_max %NAV hệ mỗi lệnh BAL (N trial = 6)
Control **byte-identical**: `4707bcbe` (pin0%) và `bcd0469f` (pin1M). Self-check 0 VND ở cả 8 chân (BAL+LAG).
Tiền thừa ở lại sổ BAL theo luật engine của cấu hình pin (park 0,3; tiền nhàn rỗi 0% hoặc dep1m).
Metric tính lại từ CSV; trên ledger pin chúng khớp registry (23,37 / −14,6 / 1,60).

| Chân | CAGR | ΔCAGR | Sharpe | MaxDD | ΔDD | Calmar | IS CAGR/DD | OOS CAGR/DD | p01 21p | boot DD5th |
|---|---|---|---|---|---|---|---|---|---|---|
| ctrl pin0% | 23,37 | — | 1,87 | −14,64 | — | 1,60 | 20,00/−13,89 | 26,57/−14,08 | −7,04 | −25,2 |
| w=3% | 22,74 | **−0,63** | 1,89 | −14,34 | +0,31 | 1,59 | 19,70/−10,81 | 25,62/−12,60 | −6,79 | −23,1 |
| w=4% | 23,56 | +0,19 | 1,91 | −14,77 | −0,13 | 1,59 | 20,00/−12,27 | 26,95/−13,46 | −7,06 | −24,5 |
| w=5% | 22,77 | **−0,60** | 1,84 | −14,71 | −0,06 | 1,55 | 19,99/−13,90 | 25,40/−14,07 | −7,15 | −25,0 |
| ctrl pin1M | 25,71 | — | 2,05 | −14,03 | — | 1,83 | 22,47/−14,03 | 28,78/−13,02 | −7,13 | −23,6 |
| w=3% | 24,75 | **−0,96** | 2,07 | −12,24 | +1,79 | 2,02 | 22,29/−10,06 | 27,07/−11,31 | −6,30 | −21,0 |
| w=4% | 26,07 | +0,37 | 2,13 | −13,13 | +0,90 | 1,99 | 22,41/−11,03 | 29,57/−12,44 | −6,91 | −21,8 |
| w=5% | 25,48 | −0,23 | 2,04 | −13,45 | +0,57 | 1,89 | 22,56/−13,45 | 28,24/−12,95 | −6,55 | −23,2 |

**Phán theo PREREG**:
- w=3%: phá CAGR ở cả 2 quy ước (−0,63 / −0,96).
- w=5%: phá CAGR ở pin0% (−0,60).
- w=4%: CAGR giữ được, ΔCAGR +0,19/+0,37 nằm trong sàn nhiễu. Nhưng MaxDD pin0% **xấu đi** 0,13pp, không đạt ≥0,46pp.

⇒ **NO-GO**.

Đọc thêm (mô tả, NGOÀI luật):
- **Đường đi lấn át tín hiệu.** w=5% hầu như chỉ ràng buộc trong BEAR (s=1), nhưng vẫn mất 0,60pp CAGR,
  nhiều hơn w=4%. Kết quả không đơn điệu theo w nên phần lớn chênh lệch là nhiễu đường đi, cỡ sàn 0,46pp hoặc hơn.
- **Có cải thiện, nhưng có trả giá.** MaxDD IS cải thiện nhất quán (w=3%: +3,1/+4,0pp; w=4%: +1,6/+3,0pp) và
  bootstrap DD5th đẹp hơn (w=3%: +2,1/+2,6pp; w=4%: +0,7/+1,8pp). Ở w=3% cái giá là CAGR. Ở w=4%, phần cải thiện
  DD toàn kỳ của pin0% bằng 0.
- **Trần rò vì xấp xỉ 2-pass.** s(t−1) lấy từ đường control, nên ở w=3% pin0% có 22 lệnh vượt trần >0,5pp
  (max 5,34%). Lưới thô và đã khoá, nên điều này không đổi kết luận.

## Q5 — Kết luận
(a) **Lệch live-backtest về sizing: không có thật.** Live dùng đúng công thức engine. VPI 5,1% là một slot đầy
đủ ở đầu cao của dải backtest (p93). Sổ 1 mã cũng không phải chuyện lạ của backtest (22% số ngày có 1-2 mã). Cái
hiếm thật là −1,07% trong một cửa sổ sổ ít mã (1/26). Ca này là w×stop trên một lệnh xấu (VPI −21%), không phải
rủi ro sizing hệ thống. N live = 1, nên không suy rộng.
(b) **Trần không cải thiện đuôi mà vẫn giữ CAGR**, theo đúng tiêu chí khoá trước.
(c) **NO-GO.** Không đề xuất đổi production. Không cần quant-skeptic cho một NO-GO. Nếu Mike muốn theo hướng
"w=4% cải thiện DD bootstrap", đó là câu hỏi MỚI, cần PREREG mới (đo sàn nhiễu đường đi riêng cho knob này, chạy cả
trên cấu hình park 0 đang live) rồi mới gọi quant-skeptic.

## Giới hạn
- Overlay chạy trên cấu hình pin **park 0,3** (dispatch chỉ định 4707bcbe). Live hiện là park 0 (pin `537e349b`),
  chưa chạy.
- Cap là xấp xỉ 2-pass, có rò (xem trên).
- Q3 dùng bal_stocks_ref nên phải loại 41 cửa sổ có CAPIT-B; nhóm 1-2 mã chỉ có N=26.
- Ghi chú về công thức plan trôi (05/08) chỉ là quan sát từ 3 file plan, chưa audit đầy đủ.
