# PLAN — Tín hiệu lãi suất huy động Big-4 (Pillar A′) bổ sung macro gate DT5G
> Taylor, 2026-07-13 · job Taylor_20260713_124803 · trạng thái: **PLAN PRE-REGISTERED — user ĐÃ DUYỆT 4 điểm §9; AMENDMENT 1 (D0 real-premium, job Taylor_20260713_131230) thêm TRƯỚC khi chạy bất kỳ backtest nào**
> Trial MỚI, sổ N riêng. Kế thừa scope `Taylor_20260713_122053` (phần B) + premise-check `Taylor_20260713_114905`.

> **AMENDMENT 1 (2026-07-13, job `Taylor_20260713_131230` — hợp lệ vì chưa tồn tại kết quả backtest nào):**
> User yêu cầu xét thêm LỆCH PHA lạm phát vs lãi suất huy động — premium THỰC của việc gửi tiền
> (`real_dep_premium = deposit_rate − CPI_yoy`) thay vì chỉ mức danh nghĩa. Family mở rộng
> **N=5 → N=6** bằng variant **D0 real-premium** (§4), input premium thực (§3.1), episode table
> premium thực đã enumerate MÔ TẢ (chưa backtest) ở §1.1. Mọi ngưỡng/fuse/debounce D0 mượn nguyên
> D1 — không tune thêm trục nào.

## 0. Tóm tắt 1 đoạn (cho người duyệt nhanh)

Thêm 1 lớp cap phòng thủ vào macro gate DT5G, đọc **6m-change của lãi suất huy động Big-4 12M**
(xu hướng, không phải mức tuyệt đối — đúng chỉ đạo user), chạy SONG SONG Pillar A (SBV refi) bằng
cùng cơ chế fuse/debounce, không thay thế gì. Lý do tồn tại: Pillar A đang **mù cấu trúc** với chu
kỳ thắt chặt 2025-26 (deposit +2.0pp trong khi refi đứng im 4.50% từ 2023-06). **Nhưng phải nói
thẳng trước khi đo: bằng chứng lịch sử của tín hiệu này cực mỏng** — ở ngưỡng STRONG, episode mang
thông tin MỚI so Pillar A chỉ có đúng **N=1, và đó chính là chu kỳ hiện tại** (chuỗi dữ liệu lại
được neo hồi tố 2026-06 khi đã biết chu kỳ này). Vì vậy plan này thiết kế theo khung **fail-safe
insurance kiểu DT5G** (giống easing-floor/macro-cap: đánh giá bằng event-audit + do-no-harm, không
phải return-enhancer), và khuyến nghị đầu ra tối đa là **SHADOW-MONITOR trước, không wire cap live
ngay** kể cả khi backtest GO.

## 1. Bối cảnh & số liệu nền (từ scope job, đã verify)

- **Nguồn dữ liệu có sẵn**: `deposit_rate_vn.py` (repo root) — proxy Big-4 12M, step-series 26 mốc
  2011→2026-06, forward-fill. Đã được `rating_8l.py` dùng làm deposit-lens hurdle + deposit-gate
  RECOVERY_PARK floor 7.5% (dormant từ 2013). **Chưa có trong `data_registry.md`** (gap, xem §2).
- **Tương quan với Pillar A (SBV refi)**: level +0.92, **6m-change chỉ +0.63**, lead-lag đối xứng
  (~0.6 hai chiều). 6 episode deposit đổi khi refi bất động ≥12m.
- **Chu kỳ hiện tại (động cơ của cả dự án)**: deposit đáy 4.7% (04/2024) → 6.8% (06/2026), +2.1pp;
  refi đứng im 4.50% từ 06/2023 → Pillar A im lặng hoàn toàn. Premise vĩ mô user đã verify ĐÚNG cả
  3 (deposit ↑, CPI đỉnh 5.6%, thanh khoản −55..70%).
- **Enumerate episode 6m-change trên proxy** (script mô tả chạy 2026-07-13, chưa phải backtest;
  ngưỡng mượn Pillar A {mild +0.5 / strong +1.5 / extreme +3.0} pp/6m):

| Ngưỡng | Episode | Peak chg6m | Pillar A lúc đó | Thông tin MỚI? | Kết cục thị trường |
|---|---|---|---|---|---|
| MILD ≥+0.5 | 2017-01→07 | +1.0 | refi flat (còn CẮT 07/2017) | **CÓ** | **FALSE POSITIVE** — 2017 bull, VNINDEX +48% |
| MILD ≥+0.5 | 2022-10→2023-03 | +2.0 | refi +2.0pp (Pillar A đã fire BEAR) | KHÔNG (trùng) | Đúng nhưng thừa — Pillar A đã cover |
| MILD ≥+0.5 | 2026-01→nay | +1.6 | refi im | **CÓ** | Đang diễn ra, chưa biết |
| STRONG ≥+1.5 | 2022-12→2023-03 | +2.0 | Pillar A đã fire | KHÔNG | (như trên) |
| STRONG ≥+1.5 | 2026-06→nay | +1.6 | refi im | **CÓ** | Đang diễn ra |
| EXTREME ≥+3.0 | — chưa từng có — | | | | |

→ **Đếm trung thực**: episode incremental (deposit fire ∧ Pillar A im) trong 15 năm = **2 ở MILD**
(2017 = false positive rõ; 2026 = đang diễn ra) và **1 ở STRONG** (2026, chưa có kết cục). Đây là
mẫu cỡ World-Cup — plan phải nói thẳng: **backtest KHÔNG THỂ chứng minh tín hiệu này bằng thống kê**;
nó chỉ có thể chứng minh tín hiệu **không phá gì** (do-no-harm) + cơ chế kinh tế hợp lý (deposit
rate = chi phí vốn thật của hệ ngân hàng, kênh truyền dẫn trực tiếp vào thanh khoản chứng khoán —
đối chiếu thanh khoản −55% cùng kỳ).

- **Trạng thái nếu wire hôm nay (2026-07-13)**: chg6m hiện tại = **+0.8** (cửa sổ 6m đã trượt qua
  mốc 01/2026) → MILD → cap NEUTRAL → **state không đổi** (đang NEUTRAL(3)). Nhưng 06/2026 đã chạm
  +1.6 → nếu D1 đã wire từ tháng 5, hệ đã bị cap **BEAR(2) = 20% cổ phiếu** trong ~1 tháng. Người
  duyệt cần thấy rõ: đây không phải lớp trang trí — nó có răng, và răng của nó suýt cắn ngay tháng
  trước. Chuỗi step thô làm chg6m nhảy bậc quanh ngưỡng (flicker cấu trúc) — thêm lý do bắt buộc
  debounce + shadow trước.

### 1.1. AMENDMENT 1 — enumerate MÔ TẢ premium thực (deposit − CPI), TRƯỚC khi backtest

**Nguồn CPI có sẵn**: `cpi_vn.py` (repo root) — CPI YoY tháng, 2 tier: **Tier-1 THẬT** từ NSO/GSO
chart-embed (2025-06→2026-06, 13 tháng — rolling window của NSO, không lùi xa hơn được); **Tier-2
PROXY** anchor nội suy tuyến tính 2011-01→2025-05 (cùng phương pháp hindsight-anchor như
`deposit_rate_vn.py`, calibrate 2026-07-06). Consumer hiện tại: chỉ `macro_confidence_regime.py`
(research). **Chưa có trong `data_registry.md`** — gộp vào prerequisite §2. Alignment khai báo
trước: CPI tháng M coi như usable từ đầu tháng M+1 (GSO công bố ~29 tháng M — publication shift,
không phải tham số tune).

**Kết quả enumerate (probe `probe_real_premium_20260713.py`, mô tả — KHÔNG phải backtest), cùng
ngưỡng mượn {+0.5/+1.5/+3.0} pp/6m trên `real_prem_chg6m`:**

| Tín hiệu | Episode MILD | Episode STRONG | Episode EXTREME |
|---|---|---|---|
| Danh nghĩa `dep_chg6m` (D1) | 3 (2017, 2022-23, 2026) | 2 (2022-12, 2026-06) | 0 |
| Thực `real_prem_chg6m` (D0) | **12** | **6** (2012, **2017-05→08 peak +2.48**, 2019-01, **2020-08→2021-02 peak +2.89**, 2025-01, 2026-02) | 1 (2012, peak +9.2) |

**Giả thuyết user đã kiểm tra thật — kết quả NGƯỢC với kỳ vọng**: false-positive 2017 KHÔNG biến
mất mà **nặng thêm** — CPI 2017 đang RƠI (4.7→2.5) trong khi deposit +1.0 → premium thực mở rộng
+2.48pp/6m → D0 fire STRONG → cap BEAR(2) giữa bull +48%. Tương tự 2020-08→2021-02 (CPI sập
6.4→0.2, premium thực +2.89 → cap BEAR xuyên mega-rally hậu-COVID) và 2012 (disinflation nhanh →
EXTREME → cap CRISIS trong năm VNINDEX +18%). Ngược lại, đúng cửa sổ sập thật 2022-10→12, CPI tăng
CÙNG NHỊP lãi suất → premium thực gần như đứng im (−0.19..+0.73) → D0 **im lặng đúng lúc cần fire
nhất**. Cơ chế: CPI YoY biến động mạnh hơn chuỗi deposit step nhiều → `real_prem_chg6m` bị chi phối
bởi CPI-momentum ngược dấu; trong mẫu VN 2011-2026, premium thực mở rộng chủ yếu do DISINFLATION —
mà disinflation lịch sử ở VN đi kèm bull (nới lỏng kỳ vọng), không phải bear.

**Kỳ vọng khai báo TRƯỚC khi chạy (chống tự lừa, đối xứng §4)**: D0 dự đoán **FAIL N2 nặng**
(chi phí 2017 + 2020-21 + 2012 lớn, không có khoản bù 2022). Nếu backtest ra D0 ĐẸP → nghi ngờ bug
/leak trước khi tin. Lý do vẫn chạy D0 thay vì bác trên giấy: (i) user yêu cầu kiểm tra thật;
(ii) chi phí đo nhỏ, kết quả auditable thay vì suy luận; (iii) event-audit D0 cho ta bảng forward
return của các cú fire — bằng chứng định lượng đóng hướng real-premium một lần cho dứt điểm.

## 2. Điều kiện tiên quyết về dữ liệu (KHÔNG phải trial — việc data-ops, làm trước/song song)

Bằng chứng lịch sử yếu là vấn đề CỐ ĐỊNH không sửa được; nhưng dữ liệu FORWARD sạch thì rẻ và làm
được ngay. Trước khi bất kỳ variant nào được phép wire (kể cả shadow), cần:

1. **Registry entry** cho `deposit_rate_vn.py` / `DEPOSIT_EVENTS` trong `mike/kb/data_registry.md`
   (status: CANONICAL-PROXY, caveat hindsight-anchor ghi rõ) — guideline §9.
2. **Routine cập nhật tháng** (Winston): mỗi đầu tháng chốt Big-4 12M posted rate từ nguồn public
   (website VCB/BIDV/CTG/Agribank, bảng CafeF/Vietstock), append mốc mới **kèm ngày thu thập thật**
   (`collected_date`) — từ nay trở đi chuỗi là point-in-time thật, hết hindsight cho tương lai.
2b. **(AMENDMENT 1) Registry entry + routine tháng cho `cpi_vn.py` luôn thể** — cùng gap, cùng
   fix: NSO chart-embed fetch được bằng script (đã chứng minh 2026-07-06), Winston append mốc CPI
   tháng mới kèm `collected_date` cùng nhịp với deposit-rate. Chi phí ~0 (cùng 1 routine).
3. **KHÔNG tái dựng lịch sử top10 ngoài Big-4** (đã kết luận ở scope: khó, bẩn, không đáng) — top10
   chỉ thu forward nếu sau này cần, ngoài phạm vi plan này. Vì chỉ có 1 chuỗi Big-4 gộp (không có
   per-bank history), **trục "cách tính trọng số Big4" KHÔNG thể test được trên dữ liệu hiện có** —
   loại khỏi family ngay từ đầu, khai báo để không ai mở thêm sau.

## 3. Thiết kế cơ chế — Pillar A′ (mirror Pillar A, zero tham số mới ở variant chính)

**Nguyên tắc**: mượn nguyên xi kiến trúc Pillar A trong `macro_state_live.py` — không phát minh
plumbing mới, không mở trục tune mới. User đã chốt 2 ràng buộc: (1) BỔ SUNG, Pillar A giữ nguyên;
(2) xoay quanh XU HƯỚNG (6m-change), không phải mức tuyệt đối.

```
dep_chg6m[t] = (deposit_rate[t] − deposit_rate[t−126 phiên]).shift(lag=5 phiên)   # y hệt refi_chg6m
dep_mild    = dep_chg6m ≥ +0.5   → đề xuất cap NEUTRAL(3)
dep_strong  = dep_chg6m ≥ +1.5   → đề xuất cap BEAR(2)
dep_extreme = dep_chg6m ≥ +3.0   → đề xuất cap CRISIS(1)
```

- **Fuse = OR cộng dồn vào cùng vòng fuse hiện có** (cùng chỗ `de/ds/dm` của Pillar A trong
  `get_macro_state`): tại mỗi phiên, cap = mức NẶNG nhất trong {Pillar A, Pillar A′, Pillar B}.
  Không nhân, không cộng điểm — đúng ngữ nghĩa "cap = trần trạng thái" hiện hành.
- **Debounce**: đi qua CÙNG `_commit(cap, cap_commit=7)` sẵn có — tự động, không thêm param.
- **Bull-aware bypass KHÔNG áp cho Pillar A′** (bypass hiện chỉ tắt Pillar B; Pillar A domestic
  vẫn sống trong bull — Pillar A′ cũng domestic nên đối xử y hệt Pillar A). Đây là lựa chọn thiết
  kế khai báo trước, và chính nó tạo ra rủi ro-2017 (§7.4) — chấp nhận đo chứ không né.
- **Chỉ CAP, không FLOOR** — đối xứng nguyên tắc đã chốt 2026-06-03 (re-risk chỉ qua DT base giá).
- **Ngưỡng {0.5/1.5/3.0} mượn nguyên Pillar A, KHÔNG tune**: biên độ 6m-change lịch sử của 2 chuỗi
  cùng cỡ (2022 cả hai +2.0pp) → mượn ngưỡng là defensible a priori và tiết kiệm toàn bộ N cho trục
  ngưỡng. Nếu ai muốn ngưỡng khác → trial mới, duyệt N mới.
### 3.1. (AMENDMENT 1) Input D0 — premium thực

```
cpi_daily[t]        = CPI_yoy tháng M, usable từ đầu tháng M+1 (publication shift), ffill theo ngày
real_dep_premium[t] = deposit_rate[t] − cpi_daily[t]
rp_chg6m[t]         = (real_dep_premium[t] − real_dep_premium[t−126 phiên]).shift(lag=5 phiên)
D0: rp_chg6m ≥ +0.5 → cap NEUTRAL · ≥ +1.5 → cap BEAR · ≥ +3.0 → cap CRISIS
```
Mọi thứ khác (OR-fuse cùng vòng, `_commit(7)`, không bypass bull, chỉ CAP) y hệt D1. KHÔNG tune
ngưỡng riêng cho D0 — nếu ai muốn ngưỡng real-premium khác → trial mới, duyệt N mới.

- **Tương tác với 2 consumer deposit-rate sẵn có** (khai báo chống nhầm lẫn): (i) deposit-lens
  hurdle trong `rating_8l.py` — tầng rating cổ phiếu, mức tuyệt đối, không liên quan; (ii)
  deposit-gate RECOVERY_PARK floor 7.5% — tầng parking vehicle, mức tuyệt đối, dormant. Pillar A′
  là tầng STATE CAP, xu hướng — 3 tầng đọc cùng 1 chuỗi nhưng không chồng logic. Không sửa 2 cái kia.

## 4. Family pre-registered — sổ N-ledger "DEPOSIT-RATE-GATE": **N = 6, đóng tại đây**
> (AMENDMENT 1: N=5 → N=6, thêm D0 TRƯỚC khi chạy bất kỳ run nào — không phải mở thêm sau khi
> thấy kết quả. Sau amendment này sổ ĐÓNG hẳn.)

| ID | Variant | Khác D1 chỗ nào | Giả thuyết cần bác/xác nhận |
|---|---|---|---|
| **D0 real-premium** | = D1 nhưng input là `rp_chg6m` (premium thực, §3.1) thay vì `dep_chg6m` | Trục user: dòng tiền phụ thuộc phần thưởng THỰC của tiết kiệm | Kỳ vọng khai báo trước từ §1.1: **FAIL N2** (fire ngược dấu 2012/2017/2020-21, im trong 2022) — chạy để có bằng chứng đo được, không bác trên giấy |
| **D1 mirror-full** | 3 ngưỡng {0.5/1.5/3.0} → cap {NEUTRAL/BEAR/CRISIS}, OR-fuse, lag 5, commit 7 | — (bản chuẩn) | Bản sao đối xứng Pillar A có do-no-harm không, hay chết vì 2017 |
| **D2 strong-only** | CHỈ 1 ngưỡng ≥+1.5 → cap BEAR; bỏ tier mild và extreme | Bỏ hẳn tier mild → miễn nhiễm false-positive 2017 (peak 2017 = +1.0 < 1.5) | Insurance tối giản: chỉ phản ứng khi thắt chặt huy động THẬT SỰ mạnh |
| **D3 blind-spot-only** | = D1 nhưng chỉ được fire khi Pillar A im (`refi_chg6m < 0.5`); refi đang tăng → nhường Pillar A | Trả lời thẳng rủi ro corr 0.92: tín hiệu CHỈ lấp đúng điểm mù, zero double-counting | Incremental value thuần — nếu D3 ≈ D1 thì phần trùng Pillar A vô nghĩa |
| **S4 sensitivity** (winner only) | Publication-lag stress: lag 5 → 26 phiên (~1 tháng lịch) | Chuỗi thật thu thập theo tháng — nếu edge chết khi trễ 1 tháng thì nó là ảo giác độ phân giải | Robustness, KHÔNG chọn lại winner bằng nó |
| **A5 ablation** (winner only, read-only) | Per-year LOO + event-list đầy đủ (từng phiên cap binds, forward T+20/T+60) | Đọc, không đổi lựa chọn | Chuẩn DT5G event-audit |

KHÔNG mở thêm biến thể/ngưỡng/trọng-số nào sau khi chạy. Trục trọng-số Big4 đã loại từ §2.3 (không
có dữ liệu per-bank). Muốn thêm gì giữa chừng → dừng, xin user duyệt N mới. S4/A5 áp cho winner
của {D0..D3} như cũ.

**Kỳ vọng độ lớn khai báo trước (chống tự lừa)**: cùng lớp với DT5G macro overlay — **Full CAGR
delta trong khoảng −0.3..+0.5pp**, phần lớn lịch sử byte-identical với baseline (overlay dormant).
Nếu variant nào ra **> +1pp Full** → nghi ngờ leak TRƯỚC KHI mừng, vì kênh leak ở đây rất cụ thể:
mốc lịch sử được neo hồi tố có thể vô tình đặt đúng trước các cú rơi (xem §7.1).

## 5. Phương pháp đo — event-audit là chính, walk-forward là phụ (nói rõ vì sao)

Bài học DT5G ghi thẳng trong CLAUDE.md: *"IS 2014-19 = +0.00pp exactly (overlay dormant in-sample)
→ walk-forward IS/OOS là công cụ SAI cho overlay hiếm-fire"*. Pillar A′ còn hiếm-fire hơn (3
episode MILD / 2 STRONG trong 15 năm). Vì vậy:

1. **Primary — event-level audit** (chuẩn `audit_dt5g_events.md`): liệt kê TỪNG phiên cap binds
   (dep-cap < base state), tách 2 nhóm: (a) incremental (Pillar A im) vs (b) redundant (Pillar A
   cũng fire). Với mỗi episode: forward VNINDEX T+20/T+60 sau ngày de-risk, chi phí/lợi ích exposure.
2. **Integrated ablation** trên harness chuẩn: `pt_v23_audit_2014.py` @50B, threads=1,
   `BQ_LOCAL_CACHE=1`, `$DNA_PYEXE`, baseline = **R3 re-pinned 27.84% / 1.84 / −18.2% / 1.53**
   (bản sau MOM-closure 07-12 — KHÔNG dùng 28.82% cũ). Output `_exp_depgate_<id>` — tuyệt đối
   không đè filename canonical (guideline §8). Self-check 0 VND từng run.
3. **Walk-forward IS/OOS + LOO**: vẫn chạy và báo cáo đủ (kỷ luật chung), nhưng diễn giải theo
   khung insurance: IS gần chắc chắn ≈ +0.00pp (dormant), phán quyết nằm ở event-audit + LOO các
   năm có fire (2017, 2022-23, 2026).
4. **DSR**: tính trên NAV daily config chọn với N=5 khai báo; **khai báo trước**: với overlay
   deviate vài chục phiên, DSR trên excess series nhiều khả năng không có power (như V2.5 đã học)
   — nếu DSR không tính được có nghĩa, báo cáo thẳng "non-informative" thay vì ép ra số đẹp. PBO:
   family 5 < 8 → không bắt buộc, không chạy.

## 6. Gate GO/NO-GO — định nghĩa TRƯỚC khi biết kết quả

**NO-GO tự động (bất kể số đẹp đến đâu):**
- N1. Variant thắng chỉ nhờ episode 2022-23 (cửa sổ Pillar A đã cover — nghĩa là edge đo được chỉ
  là bản sao Pillar A, đúng rủi ro corr 0.92) — đo bằng: loại riêng cửa sổ 2022-10→2023-06 khỏi
  chuỗi delta, nếu phần còn lại ≤ 0 → NO-GO.
- N2. Chi phí 2017-18 (false-positive đã biết trước) > 1.0pp gộp 2 năm mà không có khoản bù nào
  ngoài cửa sổ hindsight-anchored → NO-GO variant đó (dự đoán trước: D1 nhiều khả năng chết ở đây,
  D2/D3 sống — nếu ngược lại thì chính dự đoán này sai và phải hiểu vì sao trước khi đi tiếp).
- N3. Bất kỳ dấu hiệu nào cho thấy mốc DEPOSIT_EVENTS hồi tố tạo look-ahead cục bộ (vd delta dồn
  bất thường vào đúng tuần quanh 1 mốc anchor) → dừng, escalate, không diễn giải tiếp.

**GO (đủ TẤT CẢ) — và GO chỉ dẫn tới SHADOW, không phải wire live:**
- G1. Do-no-harm: Full CAGR delta ≥ **−0.30pp**, MaxDD không xấu hơn baseline, benign-window
  identity (ngoài các episode fire, NAV byte-identical baseline).
- G2. Event-audit: nhóm incremental episode có forward T+60 trung bình KHÔNG DƯƠNG (de-risk đúng
  lúc thị trường yếu đi — tiêu chí insurance, không đòi lợi nhuận).
- G3. Incremental thật: ≥ 50% số phiên cap-binds của variant thắng thuộc nhóm Pillar-A-im (nếu
  không, tín hiệu là echo — dùng D3 hoặc bỏ).
- G4. LOO: không năm nào bỏ-ra làm delta full đổi dấu từ + sang − quá 0.3pp (chuẩn chống
  1-năm-carry như mọi dự án trước).
- G5. quant-skeptic CONFIRMED.

**Sau GO — lộ trình staged bắt buộc (đây là khuyến nghị cứng của plan, không phải tùy chọn):**
1. **SHADOW-MONITOR** (không đụng state production): `macro_state_live.py` tính và publish thêm cột
   `cap_dep_shadow` + alert khi nó binds — DollarBill/user THẤY tín hiệu nhưng hệ không hành động.
   Chạy qua ít nhất **phần còn lại của chu kỳ thắt chặt hiện tại** (điểm kết tự nhiên: deposit đảo
   chiều hoặc chạm floor 7.5% của RECOVERY_PARK) + ≥ 2 mốc cập nhật forward thật của Winston (§2.2).
2. Review event-anchored (giống DC-book): shadow có fire đúng nhịp thị trường thật không, có
   flicker quanh ngưỡng không → lúc đó mới trình user quyết wire cap thật.
Lý do bắt buộc staged: N=1 episode incremental STRONG, và episode đó đang diễn ra — cách duy nhất
có thêm bằng chứng thật là QUAN SÁT nó bằng dữ liệu point-in-time thật, không phải backtest lại
quá khứ hồi tố lần nữa.

## 7. Rủi ro / overfitting khai báo trước (thứ tự theo mức nguy hiểm)

1. **Hindsight-anchor (nguy hiểm nhất, không sửa được cho quá khứ)**: 26 mốc DEPOSIT_EVENTS được
   calibrate hồi tố ngày 2026-06-19 từ web anchor — người calibrate (chính tôi) đã BIẾT 2022 sập vì
   lãi suất và ĐÃ THẤY chu kỳ 2025-26. Mọi kết quả backtest dương trên chuỗi này mang bias cấu trúc
   không định lượng được. Xử lý: (i) khung đánh giá insurance/do-no-harm thay vì đòi edge; (ii) gate
   N3 soi delta-dồn-quanh-anchor; (iii) S4 stress trễ 1 tháng; (iv) phán quyết cuối dời sang shadow
   forward point-in-time. **Không có walk-forward "thật" nào khả dĩ trên chuỗi này — nói thẳng, không
   giả vờ có.**
2. **Corr với Pillar A** (+0.92 level / +0.63 change): tín hiệu có thể chỉ là bản sao nhiễu. Xử lý:
   D3 blind-spot-only trong family + gate G3/N1 đo trực tiếp phần incremental.
3. **Mẫu quá mỏng**: 3 episode MILD / 2 STRONG / 0 EXTREME trong 15 năm; incremental STRONG N=1
   (đang diễn ra). Kết luận thống kê là bất khả — plan chấp nhận trước, chuyển trọng tâm sang cơ chế
   kinh tế + do-no-harm + forward observation. Nếu user muốn "chứng minh bằng lịch sử" thì câu trả
   lời trung thực là: **không thể, giống World Cup** — khác World Cup ở chỗ kênh nhân quả ở đây có
   thật và đo được (chi phí vốn → thanh khoản), nên đáng làm insurance chứ không đáng vứt.
4. **False-positive 2017 đã biết trước**: đợt deposit +1.0pp/6m giữa bull 2017 (VNINDEX +48%) —
   tier mild của D1 sẽ cap NEUTRAL giữa BULL, gần chắc chắn tốn tiền. Đây là phép thử tự nhiên tốt
   nhất trong mẫu: variant sống sót 2017 (D2 by design, D3 tùy refi) mới đáng đi tiếp.
5. **Step-series flicker**: chg6m nhảy bậc khi cửa sổ trượt qua anchor (thực tế vừa xảy ra: +1.6
   tháng 6 → +0.8 giữa tháng 7 mà rate không đổi). `cap_commit=7` đỡ một phần; S4 (lag 26) đo phần
   còn lại; forward data độ phân giải tháng đều đặn (§2.2) mới là fix gốc.
6. **Răng thật, cắn nhầm thì đau thật**: nếu wire D1/D2 lúc chg6m vượt 1.5 lần nữa, production tụt
   NEUTRAL→BEAR (70%→20% cổ phiếu) — một cú de-risk sai tốn hơn nhiều pp so mọi edge kỳ vọng. Đây
   là lý do thứ ba cho shadow-first.
7. **(AMENDMENT 1) CPI proxy = hindsight-anchor KÉP + nội suy**: D0 trừ 2 chuỗi proxy cho nhau —
   deposit (26 anchor hồi tố) − CPI (Tier-2 anchor nội suy tuyến tính, Tier-1 thật chỉ 13 tháng
   cuối). Nội suy tuyến tính làm `rp_chg6m` giữa các anchor thành slope nhân tạo mượt; sai số mức
   CPI ±vài phần mười pp là bình thường theo chính docstring nguồn. Mọi kết luận D0 vì thế yếu hơn
   D1-D3 một bậc về provenance — nếu (ngoài kỳ vọng) D0 GO, bắt buộc re-verify trên CPI Tier-1
   forward trước khi tin.
8. **Chu kỳ hiện tại có thể tự giải quyết**: deposit 6.8% đang tiến gần floor 7.5% của
   RECOVERY_PARK deposit-gate sẵn có (dormant từ 2013) — nếu vượt, hệ ĐÃ có một phản ứng phòng thủ
   ở tầng parking mà không cần Pillar A′. Tránh double-build: event-audit phải kiểm tra 2 cơ chế có
   fire chồng lên nhau trong kịch bản rate > 7.5% không.

## 8. Timeline & phân việc đề xuất

| Bước | Việc | Ai | Ước lượng |
|---|---|---|---|
| 0 | User duyệt plan (family N=5, gate §6, staged shadow-first) | user | — |
| 1 | Data prerequisites §2 (registry entry + routine tháng, forward-PIT) | Winston (dispatch riêng) | 0.5 ngày, song song |
| 2 | Module Pillar A′ (nhánh riêng trong `macro_state_live.py` hoặc wrapper exp, KHÔNG đụng bản prod) + unit test fuse/commit | Taylor | 0.5 ngày |
| 3 | 3 run D1/D2/D3 @50B + event-list; S4+A5 cho winner; DSR nếu có nghĩa | Taylor | 1 ngày |
| 4 | Viết kết quả vào plan này + registry; quant-skeptic verify | Taylor | 0.5 ngày |
| 5 | Nếu GO: trình user duyệt SHADOW wire (cột `cap_dep_shadow` + alert) — wire cap thật là quyết định RIÊNG sau review event-anchored | user | — |

## 9. User cần quyết (4 điểm)

1. Duyệt family 3 variant + 2 read-only (N=5 đóng sổ), ngưỡng mượn nguyên Pillar A không tune — §4.
2. Duyệt khung đánh giá insurance (event-audit primary, walk-forward diễn giải phụ) + gate §6,
   chấp nhận trước: NO-GO = đóng hướng B, và **GO cũng chỉ dẫn tới shadow-monitor**, không wire cap
   live trong dự án này.
3. Duyệt data prerequisites §2 giao Winston (routine cập nhật tháng — chi phí gần 0, có giá trị
   độc lập với GO/NO-GO vì 2 consumer khác đang dùng chung chuỗi).
4. Xác nhận đã đọc §1 dòng cuối + §7.6: nếu về sau wire thật, tín hiệu này có thể kéo production
   NEUTRAL→BEAR khi deposit tăng tốc — đó là hành vi THIẾT KẾ, cần user hiểu và muốn nó trước khi
   bất kỳ ai gõ dòng code wire.
