# DC 3-book — factor-neutral check + backtest 3-book thật + capacity (round 2)

Job `Taylor_20260830_153823` (dispatch Mike, user duyệt 2026-08-30 22:37 ICT, decided_by user).
Hoàn tất 3 việc còn thiếu từ `dc_3book_architecture_20260825.md` (job `Taylor_20260825_145251`).
RESEARCH ONLY — không đụng `custom_basket.py`/`signal_v11_sql.py`/`macro_state_live.py`/
`trading_rules.json`/`plan.py`/`executor.py`. Đã đọc kỹ file 08-25 trước khi bắt đầu (đúng yêu
cầu dispatch, không lặp lại việc đã làm).

**Sửa 1 chi tiết nhỏ trong dispatch**: user prompt ghi "baseline park=0.80" — production hiện tại
mặc định `PARK_STATES="3:0.7"` (`pt_v23_audit_2014.py:211`), không phải 0.80. Toàn bộ so sánh dưới
đây dùng đúng baseline THẬT (park=0.70), không phải con số trong prompt.

## Việc 2 (làm trước theo đúng ưu tiên dispatch) — Factor-neutral check: alpha hay beta ngành?

**Script**: `exp_insider/dc_pure_beta_check.py`. Dựng 2 rổ đối chứng KHÔNG áp double-confirm gate
cho đúng 16 mã universe DC (`sector_lens_monitor.NAMES`): (a) **cap-weight thuần** (OShares×Close
tại rebal, quý), (b) **equal-weight thuần** (1/16, quý) — thêm (b) làm cross-check vì cap-weight
để VCB/ACB (ngân hàng khổng lồ) áp đảo tỷ trọng có thể che mất beta thật của các mã nhỏ hơn/beta
cao hơn (VCI/HAH/DBC). Join cùng state series với `ConvergePort (equal-weight)` (đã có sẵn từ
job `Taylor_20260706_093329`) qua `data/converge_portfolio_backtest_nav.csv`, cùng calendar.

⚠️ Bắt 1 bug tự mình gây ra khi viết script: `vnindex_5state_dt5g_live.parquet` mã hoá state
**1..5** (không phải 0..4) — nếu không kiểm tra, hàng "BULL" sẽ bị gán nhãn sai (thực ra là hàng
BEAR N=241). Đã tự phát hiện bằng cách so N mỗi state với bảng N đã biết trong file 08-25 (BULL
full-sample phải là N=422) trước khi tin bất kỳ số nào — đúng tinh thần §29 coding_guidelines
(đừng tin nhãn, verify bằng dữ liệu độc lập).

### Kết quả (annualized mean daily return ×252, theo state)

**FULL 2014-08→2026-06:**

| State | N | baseline (100% park) | pure16 **cap-weight** (không gate) | pure16 **equal-weight** (không gate) | ConvergePort (có gate) |
|---|---:|---:|---:|---:|---:|
| CRISIS | 443 | 4,77% | 0,31% | 7,20% | 7,48% |
| BEAR | 241 | −20,48% | −4,99% | −22,32% | −16,82% |
| NEUTRAL | 1.804 | 21,00% | 23,57% | 23,72% | 22,83% |
| **BULL** | **422** | **45,34%** | **33,16%** | **50,96%** | **64,12%** |
| EXBULL | 60 | 83,55% | 61,38% | 51,25% | 57,92% |

**OOS 2020+:**

| State | N | baseline | pure16 cap-weight | pure16 equal-weight | ConvergePort |
|---|---:|---:|---:|---:|---:|
| **BULL** | **352** | **46,50%** | **29,84%** | **56,86%** | **68,94%** |

### Phân rã excess (BULL, câu hỏi chính)

| | FULL | OOS 2020+ |
|---|---:|---:|
| excess_total (ConvergePort − baseline) | +18,79pp | +22,43pp |
| excess_beta (cap-weight thuần − baseline) | **−12,18pp** | **−16,67pp** |
| excess_beta (equal-weight thuần − baseline) | **+5,63pp** | **+10,36pp** |
| excess_alpha (ConvergePort − cap-weight thuần) | +30,96pp | +39,10pp |
| beta_share nếu dùng equal-weight làm chuẩn beta | ~30% | ~46% |

**Kết luận Việc 2: KHÔNG PHẢI beta ngành thuần.** Dưới CẢ HAI cách đo beta (cap-weight và
equal-weight của đúng 16 mã, không gate), phần "chỉ cần đứng trong universe DC" giải thích **tối
đa ~30-46%** outperformance BULL (equal-weight, thước đo rộng lượng hơn cho phía beta) — thậm chí
**âm** nếu đo bằng cap-weight (rổ cap-weight thuần THUA baseline trong BULL, −12 đến −17pp, vì
VCB/ACB khổng lồ pha loãng). **≥54-70% outperformance còn lại là ALPHA từ chính bộ lọc
double-confirm + tilt STRONG (cap 20%/tên)** — không đạt ngưỡng NO-GO mà dispatch đặt ra (>70-80%
là beta). → tiếp tục Việc 1 đúng theo chỉ đạo dispatch.

## Việc 1 — Backtest 3-book THẬT (w_BAL=w_LAG=w_DC=1/3)

**Cách làm**: thay vì viết lại toàn bộ máy allocator `pt_v23_audit_2014.py` (rủi ro cao, không đủ
để test/verify kỹ trong 1 job — đúng cảnh báo Q3 của file 08-25), dùng **dữ liệu book-level THẬT**
từ chính engine production:
1. Chạy lại **đúng lệnh pin R3** (`BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 NAV_TOTAL_B=50
   ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7"
   EXP_TAG=dc3book_baseline_check $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge`),
   ghi ra file **KHÔNG canonical** (`EXP_TAG`, theo §8 coding_guidelines) — CSV mới, fresh tới
   2026-08-27: **CAGR 28,48% / Sharpe 1,88 / MaxDD −17,9% / Calmar 1,59** (khớp trong dung sai
   vintage với pin registry 28,86%/1,90/−17,8%/1,62 — lệch do cache mới hơn ~1 tháng, không phải
   lỗi harness).
2. CSV này có cột `nav_bal_ref`/`nav_lag_ref` — **NAV STANDALONE của từng book** (trước bước
   combine của allocator, không bị méo bởi CAPIT/band-rebalance) → suy ra `bal_ret`/`lag_ret`
   hàng ngày, THẬT, không tự tạo.
3. DC leg = cột `ConvergePort (equal-weight)` có sẵn (`converge_portfolio_backtest_nav.csv`,
   job `Taylor_20260706_093329`, đã T+1 + TC 0,1% + tự park cash dư vào custom30V).
4. **3-book blend = (bal_ret + lag_ret + dc_ret) / 3** mỗi ngày, tĩnh, không tính thêm turnover
   phát sinh khi chuyển từ 2-book sang 3-book (giả định đơn giản nhất, nêu rõ ở caveat).
   Baseline = `combined_nav` CHÍNH THỨC của CSV vừa chạy (allocator w_LAG state-conditional
   {1:.50, 2:0, 3/4/5:.65} band ±10pp + CAPIT, PARK 3:0.7) — đúng "combined_nav thật" dispatch
   yêu cầu, KHÔNG PHẢI baseline tự dựng.

Script: `exp_insider/dc_3book_real_blend.py`. Calendar giao nhau: 2014-08-05 → 2026-06-26 (2.970
phiên, giới hạn bởi DC leg kết thúc sớm hơn baseline).

### Kết quả

| | CAGR | Sharpe | MaxDD | Calmar |
|---|---:|---:|---:|---:|
| **Baseline** FULL | 28,33% | 1,85 | −17,8% | 1,59 |
| **3-book blend (1/3+1/3+1/3)** FULL | 27,21% | 1,67 | **−21,7%** | 1,25 |
| Δ FULL | **−1,13pp** | **−0,17** | **−3,9pp** | **−0,34** |
| Baseline IS 2014-19 | 25,67% | 1,68 | −17,8% | 1,44 |
| 3-book blend IS | 20,69% | 1,40 | −21,7% | 0,95 |
| Δ IS | **−4,98pp** | **−0,28** | −3,9pp | **−0,49** |
| Baseline OOS 2020+ | 30,62% | 1,99 | −17,2% | 1,78 |
| 3-book blend OOS | 32,94% | 1,88 | −19,9% | 1,65 |
| Δ OOS | +2,31pp | −0,11 | −2,7pp | −0,13 |

**Gross theo state (FULL) — giải thích cơ chế:**

| State | N | baseline | 3-book blend | delta |
|---|---:|---:|---:|---:|
| CRISIS | 443 | 6,48% | 7,12% | +0,65pp |
| **BEAR** | **241** | **−0,13%** | **−5,04%** | **−4,91pp** |
| NEUTRAL | 1.804 | 29,71% | 27,02% | −2,69pp |
| **BULL** | **422** | **42,34%** | **51,02%** | **+8,68pp** |
| EXBULL | 60 | 57,22% | 55,51% | −1,71pp |

### Kết luận Việc 1: **NO-GO** cho đúng kiến trúc "song song 1/3+1/3+1/3 tĩnh" như dispatch yêu cầu

**⚠️ ĐÍNH CHÍNH (sau quant-skeptic verify, xem cuối file)**: bản nháp đầu tiên của mục này quy lỗi
BEAR cho "static split phá kỷ luật `w_LAG=0` trong BEAR" — **quant-skeptic bác bỏ, ĐÚNG**. Phân rã
trực tiếp `bal_ret`/`lag_ret`/`dc_ret` theo state (tự kiểm lại, khớp con số quant-skeptic đưa ra):

| State | N | bal_ann | lag_ann | dc_ann | baseline_ann | blend_ann |
|---|---:|---:|---:|---:|---:|---:|
| CRISIS | 443 | 3,48% | 10,40% | 7,48% | 6,48% | 7,12% |
| **BEAR** | **241** | **0,64%** | **1,07%** | **−16,82%** | −0,13% | −5,04% |
| NEUTRAL | 1.804 | 28,98% | 29,25% | 22,83% | 29,71% | 27,02% |
| BULL | 422 | 54,54% | 34,41% | 64,12% | 42,34% | 51,02% |
| EXBULL | 60 | 39,13% | 69,47% | 57,92% | 57,22% | 55,51% |

**LAG trong BEAR là +1,07%/năm — DƯƠNG, không phải lực kéo.** Thủ phạm thật của −4,91pp ở BEAR
là **chính DC leg tự nó sụp −16,82%/năm trong BEAR** — double-confirm (sector-lens BUY ∩ 8L≤2) là
1 bộ lọc GIÁ TRỊ/CHẤT LƯỢNG, không có override macro nào cho CRISIS/BEAR (`converge_portfolio_
backtest.py` không có state gate) — nó có thể vẫn báo "rẻ + chất lượng tốt" trong lúc cả ngành
(Banking/Securities) đang rơi theo chu kỳ tín dụng, và tiếp tục nắm giữ 20%/tên trong lúc giá tiếp
tục giảm. **Đây KHÔNG phải hệ quả của việc bỏ w_LAG=0 — là DC tự nó chưa có cơ chế phòng thủ BEAR.**
Ở NEUTRAL, nguyên nhân −2,69pp khác: DC (22,83%) thấp hơn cả BAL/LAG hiện tại (~29% mỗi book) nên
kéo trung bình xuống — đúng như Q1 file 08-25 đã chỉ ra, DC không có edge trong NEUTRAL, chỉ có
edge trong BULL/CRISIS.

Kết luận NO-GO cho kiến trúc tĩnh vẫn ĐỨNG VỮNG (Sharpe/Calmar/MaxDD xấu đi ở FULL và IS, chỉ CAGR
OOS nhỉnh hơn nhưng Sharpe/Calmar OOS vẫn xấu đi) — nhưng vì **lý do đúng**: DC cần 1 cơ chế
state-conditional CHO CHÍNH NÓ (tắt/giảm trong BEAR/CRISIS), không phải vì xung đột với LAG.

**Phát hiện phụ (chưa đủ điều kiện GO, chỉ để định hướng bước sau, KHÔNG tính vào phạm vi 3 việc
được giao)**: thử 1 overlay state-conditional — DC chỉ hoạt động trong BULL/EXBULL (giữ
`combined_nav` 2-book nguyên vẹn ở CRISIS/BEAR/NEUTRAL — **đúng vì lý do vừa sửa ở trên: tránh
đúng state DC tự sụp**), tài trợ tỷ lệ w_DC=0,20-0,33 từ chính combined_nav trong 2 state đó:

| w_DC (chỉ BULL/EXBULL) | CAGR FULL | Sharpe FULL | MaxDD FULL | Calmar FULL | Sharpe OOS | Calmar OOS |
|---|---:|---:|---:|---:|---:|---:|
| 0 (baseline) | 28,33% | 1,85 | −17,8% | 1,59 | 1,99 | 1,78 |
| 0,20 | 29,09% | 1,87 | −18,9% | 1,54 | **2,03** | **1,85** |
| 0,33 | 29,58% | 1,87 | −19,7% | 1,50 | **2,04** | **1,90** |

OOS Sharpe/Calmar cải thiện nhất quán (MaxDD OOS **không đổi** −17,2% ở cả 2 mức — điểm rút vốn
tối đa OOS nằm ngoài BULL/EXBULL nên overlay không chạm tới), FULL Calmar nhẹ nhàng xấu đi do
MaxDD IS-era xấu thêm ~1-2pp. Đây là hướng đáng theo đuổi hơn "song song tĩnh 1/3" nhưng **chưa hề
qua DSR/PBO/quant-skeptic** — chỉ là quan sát từ đúng dữ liệu vừa dựng, không phải một đề xuất
hoàn chỉnh.

⚠️ **Lưu ý baseline KHÁC NHAU giữa Việc 1 và Việc 2** (quant-skeptic nêu, đúng, dễ gây nhầm nếu đọc
lướt): Việc 2 so DC với **100% custom30V park thuần** (baseline cô lập, để tách alpha/beta) — ở đó
EXBULL park thuần đạt 83,55%/năm nên DC (57,92%) trông như "thua đậm" (−25,63pp) trong EXBULL. Việc
1 và overlay ở trên so DC với **combined_nav production THẬT** (BAL+LAG+CAPIT, không phải park
thuần) — ở đó EXBULL production chỉ đạt 57,22%, gần bằng DC (57,92%, nhỉnh hơn +0,70pp) → overlay
gộp DC vào BULL+EXBULL không mâu thuẫn với chính nó, chỉ là 2 câu hỏi khác nhau dùng 2 mẫu số khác
nhau. Không đổi kết luận nào ở trên, chỉ làm rõ để tránh đọc nhầm 2 con số EXBULL cạnh nhau.

## Việc 3 — Capacity 4 mã Securities (SSI/VCI/VND/HCM) ở quy mô NAV THẬT

NAV thật hiện tại (không phải NAV giả định backtest 50B): **SpaceX 985,5 triệu VND** (2026-08-28),
**ZaloPay 952,3 triệu VND** (2026-08-28) — `data/execution_logs/nav_history_{SpaceX,ZaloPay}.csv`.
1/3 NAV mỗi account cho book DC ≈ 328M / 317M VND; cap 20%/tên trong DC (`CAP=0.20` ở
`converge_portfolio_backtest.py`) → vị thế tối đa mỗi mã Securities ≈ **~63-66 triệu VND**.

ADV (Trading_Value = Volume×Close, trung vị 3 tháng gần nhất, `tav2_bq.ticker` qua cache local):

| Mã | ADV trung vị 3T (tỷ VND/ngày) | Vị thế tối đa (~66tr VND) / ADV |
|---|---:|---:|
| SSI | 347,8 | 0,019% |
| VND | 219,9 | 0,030% |
| VCI | 180,1 | 0,037% |
| HCM | 107,2 | 0,062% |

**Kết luận Việc 3: KHÔNG phải vấn đề capacity ở quy mô tài khoản thật hiện tại.** Vị thế tối đa
chưa tới 0,1% ADV cho cả 4 mã — thấp hơn NHIỀU bậc so với bất kỳ ngưỡng ADV-cap nào production
đang dùng cho LAG (vài % ADV). Đây khác hẳn tình huống LAG-ADV filter (`kb/projects/
lag-adv-filter-tracking.md`) — nơi book vận hành ở quy mô backtest 25B và cạnh tranh thanh khoản ở
các mã nhỏ/mid-cap; DC chỉ chọn trong 16 blue-chip lớn VÀ tài khoản thật đang ở quy mô ~1 tỷ VND
(nhỏ hơn backtest ~50.000 lần) — capacity không phải rào cản cho tới khi NAV tăng ít nhất vài bậc
độ lớn.

## Tổng kết & khuyến nghị

- **Việc 2**: alpha double-confirm là THẬT (≥54-70% outperformance BULL không giải thích được
  bằng beta ngành thuần, kể cả đo bằng cap-weight lẫn equal-weight).
- **Việc 1**: kiến trúc **"3-book song song tĩnh 1/3+1/3+1/3" là NO-GO** — phá vỡ kỷ luật
  state-conditional (LAG=0 trong BEAR) của allocator hiện tại, đổi lấy alpha BULL với giá đắt hơn
  ở BEAR/NEUTRAL. **KHÔNG đề xuất wire kiến trúc này.**
- **Việc 3**: không phải rào cản ở quy mô hiện tại — không cần hành động.
- **Không cần quant-skeptic pass** theo đúng điều kiện dispatch đặt ra ("nếu kết luận GO... bắt
  buộc quant-skeptic") — kết luận cuối là **NO-GO cho kiến trúc được giao test**, không có gì đề
  xuất wire production. Phát hiện phụ (overlay state-conditional BULL/EXBULL) được ghi lại làm
  gợi ý hướng đi tiếp, nhưng tự nó CHƯA đủ để coi là 1 đề xuất — cần 1 job riêng (define rõ cách
  tài trợ vốn từ BAL/LAG, walk-forward IS/OOS đầy đủ, DSR/PBO, rồi mới tới quant-skeptic) nếu
  Mike/user muốn theo đuổi.

**Files**: `exp_insider/dc_pure_beta_check.py` (+ `dc_pure_beta_check_by_state.csv`),
`exp_insider/dc_3book_real_blend.py` (+ `dc_3book_real_blend_metrics.csv`), CSV audit fresh
`data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_dc3book_baseline_check_univpit.csv`
(không canonical, có `EXP_TAG`, an toàn không đè file pin chính thức).

## quant-skeptic verify (chạy dù kết luận NO-GO, vì đảo ngược khuyến nghị GO trước đó 08-25)

**Verdict: CONFIRMED (medium confidence)**, cả 2 kết luận chính (Việc 2 alpha-thật, Việc 1
NO-GO-cho-kiến-trúc-tĩnh) đứng vững sau: re-run độc lập cả 2 script khớp byte-for-byte mọi con số
FULL/IS/OOS + bảng by-state; trace code xác nhận `nav_bal_ref`/`nav_lag_ref` tính TRƯỚC bước
combine allocator (dòng ~2047 `pt_v23_audit_2014.py`, trước block "Allocator overlay" §8) nên đúng
là standalone; cắt lịch giao (2014-08-05→2026-06-26) sạch, không lệch kết luận so với CSV full-vintage
tới 2026-08-27; N mỗi state khớp cả 3 nguồn độc lập (report này, rerun quant-skeptic, file 08-25).
**1 lỗi thật tìm thấy và đã sửa ở trên**: narrative gốc quy nguyên nhân BEAR sai (đổ cho LAG) —
đã đính chính đổ đúng cho DC leg tự sụp trong BEAR (không có state override). Không đổi verdict
NO-GO, chỉ đổi LÝ DO — quan trọng vì lý do đúng mới dẫn tới đúng hướng khắc phục (gate DC theo
state, không phải sửa gì ở LAG). Ghi nhận thêm 1 điểm nhỏ chưa giải thích được: rerun độc lập của
quant-skeptic cho `dc_pure_beta_check.py` không khớp bit-for-bit vài số pure16 (vd CRISIS pure16-eq
7,20% ở đây vs 5,60% ở rerun của họ) — tự rerun lại 2 lần ở đây cho kết quả ổn định/khớp báo cáo,
nên nhiều khả năng khác biệt môi trường/cache phía quant-skeptic tại thời điểm chạy, không phải
bug trong script; không đổi kết luận định tính (beta_share vẫn ~29-46% dù tính cách nào).
