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

## 10. Kết quả backtest D0 (real-premium) — **NO-GO, khớp chính xác kỳ vọng pre-registered §1.1**
> Job `Taylor_20260713_141712` (tiếp `Taylor_20260713_131230`), chạy 2026-07-13. CHỈ D0 + control
> trong job này (D1/D2/D3 thuộc job song song riêng). Verdict: **NO-GO tự động ở N2**, kèm fail
> G1 + G2. Đây là kết quả ĐÚNG THIẾT KẾ: §1.1 đã dự đoán trước "D0 FAIL N2 nặng" — backtest xác
> nhận bằng số đo được, đóng dứt điểm hướng real-premium như mục tiêu (iii) của Amendment 1.

### 10.1. Thiết lập (đúng plan §3.1/§5, không tune gì thêm)
- Input: `rp_chg6m = (deposit_rate − CPI_yoy_shifted_M+1)` 6m-change (126 phiên), lag 5 phiên —
  y hệt `refi_chg6m`. Ngưỡng mượn nguyên {+0.5→NEUTRAL / +1.5→BEAR / +3.0→CRISIS}, debounce
  `_commit(7)` mượn nguyên từ `macro_state_live.py` (import trực tiếp, không copy).
- **Phương pháp overlay (khai báo, auditable)**: `state_D0[t] = min(published_DT5G[t],
  commit(dep_cap[t]))` trên bảng published `vnindex_5state_dt5g_live` thay vì re-run cả fuse —
  lý do: bản replica in-fuse drift 122/3107 phiên so bảng published NGAY CẢ KHI tắt dep-pillar
  (v34b base full-recompute trên giá retro-adjusted + cap-timing 2020/2023) → dùng nó làm control
  sẽ trộn lẫn base-drift với delta của dep layer. Overlay giữ control == published CHÍNH XÁC, mọi
  deviation quy được 100% cho dep layer. Fidelity: trong cửa sổ Pillar-A-im (chính là phần
  incremental cần đo) overlay == in-fuse exact; sai khác commit-timing chỉ khả dĩ bên trong
  2022-23 nơi Pillar A đã cap sẵn (redundant by definition) — và D0 không fire ở đó (xem 10.3).
- Harness: lệnh pin R3 nguyên văn (`pt_v23_audit_2014.py v23a none postbull 0 edge`, @50B,
  `BQ_CACHE_THREADS=1`, `PARK_STATES="3:0.7"`, `AUDIT_END=2026-06-19`, `$DNA_PYEXE`), state view
  swap in-process qua DuckDB view (zero touch cache thật). Output `EXP_TAG=depgate_D0/control` —
  không đè canonical (§8). **Self-check 0 VND cả BAL+LAG, cả 2 run.**

### 10.2. Kết quả integrated ablation
| Run | FULL CAGR | Sharpe | MaxDD | Calmar | IS 2014-19 | OOS 2020+ |
|---|---|---|---|---|---|---|
| control (published DT5G, same-vintage) | 27.11% | 1.81 | −18.3% | 1.48 | 23.37% | 30.61% |
| **D0 real-premium** | **22.05%** | 1.57 | −18.4% | 1.20 | 19.64% | 24.27% |
| **Delta** | **−5.06pp** | −0.24 | −0.1pp | −0.28 | **−3.73pp** | **−6.34pp** |

Per-year delta (chỉ năm có lệch): 2017 **−17.4pp** (32.95→15.55), 2019 −6.8pp, 2020 **−24.0pp**
(+22.78→−1.20), 2021 −18.3pp (103→85), 2025 −11.6pp, 2026 +3.2pp. Không năm nào D0 thắng đáng kể.

Kiểm chứng: (i) recompute độc lập `extract_peryear.py` từ CSV khớp chính xác engine print cả 2
run; (ii) Sharpe/MaxDD recompute từ DAILY rows khớp; (iii) **benign-window identity PASS** — NAV
byte-identical 839 phiên liên tục cho tới ĐÚNG phiên state-deviate đầu tiên (2017-05-24).

**Caveat control-vs-pin (khai báo trung thực):** control same-vintage ra 27.11 ≠ pin R3 27.84
(−0.73pp) dù đúng nguyên văn lệnh pin + AUDIT_END. Nguyên nhân thuộc lớp "mutation as-of" registry
đã cảnh báo sẵn (quy tắc #3 đầu file registry): từ ngày pin 07-12 tới nay, `fa_ratings`/
`fa_ratings_8l` re-rank 2 quý mở (07-12, +39/+16 rows), `custom30v_8l` republish daily, bảng DT5G
re-publish sau EW-leg fix, cache chuyển full_only (07-13). Ablation này so **control vs D0 CÙNG
vintage** nên delta sạch; verdict NO-GO bền với mọi level-shift ±0.73pp (delta −5.06pp).

### 10.3. Event-audit (primary, chuẩn `audit_dt5g_events.md`) — 8 episode, 358 phiên deviate
Artifact đầy đủ: `exp_depgate/event_audit_D0.csv` (từng phiên) + `_episodes.csv`. Tóm tắt:

| Ep | Cửa sổ | Phiên | Cap sâu nhất | Peak rp_chg6m | Pillar A? | VNINDEX fwd T+60 sau de-risk | Chi phí sleeve |
|---|---|---|---|---|---|---|---|
| 0 | 2017-05→09 | 80 | BEAR | +2.85 | im | **+4.2%** | −4.18pp |
| 1 | 2019-01→03 | 42 | BEAR | +2.02 | im | **+7.1%** | −3.74pp |
| 2 | **2020-08→2021-04** | 169 | BEAR | +2.89 | im | **+12.0%** | **−30.19pp** |
| 3 | 2025-01→02 | 17 | BEAR | +1.60 | im | −3.4% | −1.16pp |
| 4 | 2025-03 | 11 | NEUTRAL | +0.71 | im | +1.2% | −0.10pp |
| 5 | 2025-09→10 | 12 | NEUTRAL | +0.71 | im | +2.0% | −0.01pp |
| 6 | 2026-01→02 | 12 | NEUTRAL | +1.86 | im | +2.8% | −0.37pp |
| 7 | 2026-02→03 | 15 | BEAR | +1.86 | im | +0.5% | +4.22pp |

- **100% incremental** (cả 358 phiên đều Pillar-A-im) — G3 pass về mặt kỹ thuật nhưng vô nghĩa:
  phần "mới" của tín hiệu chính là phần SAI.
- **Zero phiên deviate trong toàn bộ 2022** — D0 im lặng hoàn toàn đúng cửa sổ sập 2022-10→12 cần
  fire nhất, y như §1.1 dự đoán (CPI tăng cùng nhịp lãi suất → premium thực đứng im).
- Forward T+60 sau de-risk trung bình **+3.3%** (7/8 episode dương) → de-risk đúng lúc thị trường
  ĐANG KHỎE — ngược hẳn tiêu chí insurance G2.
- Cú đắt nhất đúng cơ chế §1.1: 2020-08→2021-04 CPI sập 6.4→0.2 → premium thực +2.89 → cap BEAR
  xuyên 169 phiên mega-rally hậu-COVID, một mình tốn −30.2pp sleeve.
- Episode dương duy nhất (ep7, +4.22pp, trúng cú chỉnh 02-03/2026) nằm TRONG chu kỳ hindsight-
  anchored hiện tại — đúng loại "khoản bù" mà N2 loại trừ theo định nghĩa.

### 10.4. Gate §6 — phán quyết từng mục
| Gate | Định nghĩa | Kết quả | Verdict |
|---|---|---|---|
| **N2** | Chi phí 2017-18 >1.0pp không có bù ngoài cửa sổ hindsight | 2017 riêng −17.4pp năm / −4.18pp sleeve; bù duy nhất (+4.22pp) nằm trong cửa sổ hindsight 2026 | **NO-GO tự động** |
| N1 | Thắng chỉ nhờ 2022-23 | Moot — D0 không thắng; 2022 zero deviation | — |
| N3 | Delta dồn bất thường quanh anchor (leak) | Không có: tổng delta ÂM lớn, không có cụm lợi nhuận quanh anchor nào | pass (không leak DƯƠNG) |
| G1 | Do-no-harm ≥ −0.30pp | **−5.06pp** | FAIL |
| G2 | Incremental fwd T+60 không dương | **+3.3%** trung bình | FAIL |
| G3 | ≥50% phiên binds incremental | 100% | pass (vô nghĩa khi G1/G2 fail) |
| G4 | LOO | Moot (đã NO-GO) | — |
| G5 | quant-skeptic | Chưa chạy trong job này (được phép để lại theo dispatch; mọi số đều recompute độc lập từ CSV) | pending |

**VERDICT D0: NO-GO — đóng hướng real-premium.** Kết quả khớp chính xác kỳ vọng khai báo trước
(§1.1: "FAIL N2 nặng, fire ngược dấu 2017/2020-21, im trong 2022") nên theo chính §1.1 đây là
kết quả ĐÁNG TIN (không phải bất ngờ đẹp cần nghi bug). Cơ chế xác nhận định lượng: `rp_chg6m` bị
CPI-momentum ngược dấu chi phối — trong mẫu VN 2014-2026, premium thực mở rộng chủ yếu do
DISINFLATION, mà disinflation đi kèm bull. Trừ CPI khỏi deposit-rate làm tín hiệu TỆ ĐI so với
danh nghĩa ở cả 2 đầu: thêm false-positive (2017/2019/2020-21/2025) VÀ xóa true-positive (2022).

**Hàm ý cho family còn lại**: D0 out. Winner (nếu có) chọn trong {D1, D2, D3} ở job song song;
S4/A5 áp cho winner đó. N-ledger DEPOSIT-RATE-GATE: D0 đã tiêu 1/6, sổ vẫn đóng.

### 10.5. Artifacts
- State series + audit: `mike/agents/Taylor/exp_depgate/state_D0{.parquet,_full.csv}`,
  `event_audit_D0{.csv,_episodes.csv}`, log `run_D0.log`/`run_control.log`
- Harness CSV: `data/v23_golive_audit_..._exp_depgate_{D0,control}.csv` (17.370/18.169 rows)
- Code: `mike/agents/Taylor/exp_depgate_20260713.py` (build state), `run_depgate_variant.py`
  (view-swap runner) — không đụng `macro_state_live.py`/cache/production file nào.

## 11. Kết quả backtest D1/D2/D3 — **NO-GO CẢ 3 → family 0/4 GO, ĐÓNG HƯỚNG B**
> Job `Taylor_20260713_145605`, chạy 2026-07-13. Attempt 1 dispatch-layer timeout nhưng harness
> nền chạy xong toàn bộ (đúng bài học D0); attempt 2 harvest + verify. **Kết luận: không biến thể
> nào trong {D0,D1,D2,D3} qua gate §6 → hướng B (Pillar A′ deposit-rate) đóng hoàn toàn, KHÔNG
> tiến tới shadow-monitor. S4/A5 (winner-only) không chạy vì không có winner. N-ledger
> DEPOSIT-RATE-GATE: 4/6 tiêu, S4/A5 không dùng, sổ đóng.**

### 11.1. Phát hiện phương pháp QUAN TRỌNG trước khi đọc số: tie-break nondeterminism trong harness
Khi so run unsorted, NAV lệch **từ 2018-01-02** dù state của variant identical control tới tận
2023 — root cause: sizing của harness tie-break theo THỨ TỰ DÒNG của query result; DuckDB đổi
row-order theo NỘI DUNG parquet state được swap (hash-join layout) → 2 mã cùng score hoán đổi
`buy_amount` (vd MWG/PLX 2018-01-02), NAV lệch hàng tỷ VND TRƯỚC phiên state-diff đầu tiên.
- **Fix trong job**: patch stable-sort `(time,ticker)` lên `BQLocalCache.query` (chỉ result có
  CẢ 2 cột — không đụng các ORDER BY chủ ý khác), runner `run_depgate_variant_sorted.py`.
- **Determinism PROOF**: control chạy 2 lần (ctlSa/ctlSb) → **md5 byte-identical**
  (`f4421a1755d2d2ef75e4be86280eba04`).
- **Thang noise đo được**: unsorted control 27.11 vs sorted 27.65 = ~0.5pp thuần ordering; delta
  unsorted D1/D2/D3 (+0.40/+0.19/+0.40) nhiễm noise → **số sorted là số chính thức của family**.
  Hệ quả cho §10: caveat control-vs-pin −0.73pp trước đây thực ra TRỘN mutation-drift với ordering
  noise; drift thật (sorted control vs pin) chỉ **−0.19pp** (27.65 vs 27.84). Verdict D0 KHÔNG đổi
  (delta −5.06pp >> noise; N2/G2 của D0 dựa trên event-audit state-level, không nhiễm).
  ⚠️ Bài học chung cho mọi experiment view-swap trên `pt_v23_audit_2014.py` từ nay: **bắt buộc
  sort ổn định + determinism-pair control**, nếu không delta <±0.5pp không có nghĩa.

### 11.2. Integrated ablation (sorted, same-vintage, self-check 0 VND cả BAL+LAG mọi run)
| Run | FULL CAGR | Sharpe | MaxDD | Calmar | IS 2014-19 | OOS 2020+ | Delta FULL |
|---|---|---|---|---|---|---|---|
| control sorted (ctlSa≡ctlSb) | 27.65% | 1.83 | −18.3% | 1.51 | 23.37% | 31.70% | — |
| **D1 mirror-full** | 27.82% | 1.86 | −18.3% | 1.52 | 23.37% | 32.02% | **+0.17pp** |
| **D2 strong-only** | 27.84% | 1.85 | −18.3% | 1.52 | 23.37% | 32.06% | **+0.19pp** |
| **D3 blind-spot-only** | 27.63% | 1.84 | −18.3% | 1.51 | 23.37% | 31.65% | **−0.02pp** |

- **IS 2014-19 identical 23.37% cả 4 run** — overlay dormant in-sample, đúng dự đoán §5 (khớp
  chữ ký DT5G "+0.00pp exactly IS").
- **Benign-window identity PASS tuyệt đối**: D1/D2 NAV trùng control 2.267 phiên liên tục tới
  ĐÚNG 2023-02-07 (phiên deviate đầu); D3 trùng 3.012 phiên tới ĐÚNG 2026-01-28.
- Per-year delta ≠ 0 (D1): 2023 **+2.17pp** (23.54→25.71), 2024 −0.06, 2025 +0.16, 2026 −0.19 —
  toàn bộ edge nằm trong 1 năm 2023; 2024-25 chỉ là path-carry sau divergence. D2 y hệt trừ 2026
  (+0.01, không có mild tier). D3: identical mọi năm trừ 2026 (−0.21).
- Recompute độc lập `extract_peryear.py` từ CSV khớp engine print cả 4 run.
- DSR: **non-informative như khai báo trước §5.4** — deviate 70/58/30 phiên trên 3.107, excess
  series không đủ power; không ép ra số.

### 11.3. Event-audit (primary) — `exp_depgate/event_audit_D{1,2,3}{.csv,_episodes.csv}`
| Variant | Ep | Cửa sổ | Phiên | Cap | Pillar A? | fwd T+60 | Sleeve |
|---|---|---|---|---|---|---|---|
| D1 | 0 | 2023-02-07→03-16 | 28 | BEAR | **active (0% im)** | −2.4% | **+0.89pp** |
| D1 | 1 | 2023-04-04→04-19 | 12 | BEAR | **active (0% im)** | +3.9% | **+1.37pp** |
| D1 | 2 | 2026-01-28→02-12 | 12 | NEUTRAL | im (100%) | +2.8% | −0.37pp |
| D1 | 3 | 2026-06-16→07-09 | 18 | BEAR | im (100%) | +1.8%* | −0.92pp |
| D2 | — | = D1 bỏ ep2 (mild) | 58 | | | | |
| D3 | — | = chỉ ep2+ep3 (blind-spot) | 30 | | | | |

\* fwd60 của ep 2026-06 **truncated tại cuối chuỗi** (fwd20=fwd60=+1.81 vì clamp) — episode đang
diễn ra, chưa có kết cục.

**Đọc thẳng:** toàn bộ phần DƯƠNG của D1/D2 (+2.26pp sleeve) nằm trong 2023-02→04 nơi **Pillar A
đang active** (redundant 100%, đúng rủi ro corr-0.92 §7.2 — tín hiệu chỉ đào sâu thêm cú de-risk
Pillar A đã ra lệnh, và cửa sổ này nằm TRONG vùng loại trừ N1 2022-10→2023-06). Phần incremental
thuần (Pillar A im) = đúng 2 episode chu kỳ 2025-26 hindsight-anchored, cả 2 đều TỐN TIỀN
(−1.29pp) với VNINDEX forward DƯƠNG sau de-risk → phần "mới" của tín hiệu tới nay chỉ sai (hoặc
quá sớm — không phân biệt được cho tới khi chu kỳ hiện tại ngã ngũ).

**2017 — dự đoán N2 pre-registered SAI, và lý do sai có giá trị**: tín hiệu mild CÓ fire 126 phiên
(peak chg6m +1.0, dep_cap=NEUTRAL commit ~120 phiên) nhưng **không bind một phiên nào** — DT5G
published đứng NEUTRAL(3) gần trọn 2017 (245/250 phiên; chỉ 4 phiên BULL). Cap-overlay chỉ có răng
khi state Ở TRÊN mức cap; DT5G hiếm khi ở BULL/EXBULL (EX-BULL 59 ngày từ 2014) → **tier mild
cap-NEUTRAL gần như vô hiệu lịch sử**, và nỗi sợ false-positive-2017 hóa ra được chính độ bảo thủ
của DT5G base hóa giải. Chi phí 2017-18 = 0.00pp cho cả 3 variant.

### 11.4. Gate §6 — phán quyết từng variant
| Gate | D1 mirror-full | D2 strong-only | D3 blind-spot-only |
|---|---|---|---|
| **N1** (thắng chỉ nhờ 2022-23) | **NO-GO**: episode ngoài cửa sổ = 2026×2, sleeve **−1.29pp ≤ 0** | **NO-GO**: ngoài cửa sổ chỉ 2026-06, sleeve **−0.92pp ≤ 0** (per-year remainder +0.11 là path-carry của divergence 2023, không phải fire ngoài cửa sổ) | pass (không phụ thuộc 2022-23 — vì không thắng gì) |
| N2 (chi phí 2017-18 >1pp) | pass (0.00pp — xem 11.3) | pass (0.00pp) | pass (0.00pp) |
| N3 (leak quanh anchor) | pass (cụm dương duy nhất = 2023 redundant, N1 xử) | pass | pass (delta âm) |
| G1 do-no-harm | pass (+0.17, DD same, identity 2.267 phiên) | pass (+0.19) | pass (−0.02 ≥ −0.30, identity 3.012 phiên) |
| **G2** (incremental fwd60 không dương) | **FAIL** (+2.33% mean; ep cuối truncated) | **FAIL** (+1.81%*) | **FAIL** (+2.33% mean, sleeve −1.29pp) |
| **G3** (≥50% phiên binds incremental) | **FAIL** (30/70 = 43%) | **FAIL** (18/58 = 31%) | pass (100% by design) |
| G4 LOO | **FAIL** (100% edge = 1 năm 2023; LOO-2023 đổi dấu) | **FAIL** (như D1) | pass (moot, delta ≈ 0) |
| G5 quant-skeptic | **pending — verify CẢ CỤM D0-D3 một lần** (đề xuất giữ nguyên từ job D0; mọi số đã recompute độc lập từ CSV + md5 determinism proof) | pending | pending |
| **VERDICT** | **NO-GO** | **NO-GO** | **NO-GO** |

### 11.5. Tổng kết family + quyết định
- **0/4 variant GO (D0/D1/D2/D3 đều NO-GO)** → theo đúng quyết định pre-registered user đã duyệt
  (§9.2: "NO-GO = đóng hướng B"): **hướng Pillar A′/deposit-rate gate ĐÓNG HOÀN TOÀN — không
  shadow-monitor, không wire, không mở thêm biến thể.** Muốn mở lại → trial mới, duyệt N mới,
  và điều kiện thực chất duy nhất đáng để mở lại là: chu kỳ 2025-26 kết thúc với bằng chứng
  point-in-time thật (data prerequisite §2 của Winston vẫn NÊN chạy — chuỗi forward sạch có giá
  trị độc lập cho 2 consumer khác + cho việc đánh giá hồi tố chu kỳ này khi nó ngã ngũ).
- Diễn giải trung thực theo khung §0: backtest KHÔNG bác cơ chế kinh tế (chi phí vốn → thanh
  khoản) — nó xác nhận đúng điều §1 nói trước: tín hiệu này không chứng minh được bằng lịch sử
  (phần trùng Pillar A thì thừa, phần mới thì mới chỉ thấy tốn tiền), và lớp mild gần như vô hiệu
  dưới kiến trúc cap-DT5G. Insurance không có bằng chứng do-no-harm DƯƠNG ở phần incremental
  không đáng chiếm 1 lớp phức tạp trong `macro_state_live.py` production.
- Số R3 pin 27.84/1.84/−18.2/1.53 KHÔNG đổi (mọi run experiment tag riêng, không đè canonical).
- Còn treo duy nhất: **G5 — quant-skeptic verify cả cụm D0-D3** (artifact đầy đủ trong
  `exp_depgate/`; điểm cần skeptic soi nhất: (i) patch sort không đổi semantics harness — bằng
  chứng: control sorted vs pin chỉ lệch mutation-drift −0.19pp, xa dưới delta D0; (ii) đọc N1
  bằng sleeve-attribution thay vì per-year remainder cho D2).

### 11.6. Artifacts
- Runs sorted (chính thức): `data/..._exp_depgate_{ctlSa,ctlSb,D1S,D2S,D3S}.csv`; log
  `exp_depgate/run_{ctlSa,ctlSb,D1S,D2S,D3S}.log`. Unsorted (giữ làm bằng chứng noise):
  `..._exp_depgate_{D1,D2,D3}.csv` + log tương ứng.
- Event-audit: `exp_depgate/event_audit_D{1,2,3}{.csv,_episodes.csv}` (builder
  `exp_depgate/build_event_audit.py`, tự verify khớp bản D0 gốc atol 0.011).
- State series: `exp_depgate/state_D{1,2,3}{.parquet,_full.csv}`.
- Runner sorted: `mike/agents/Taylor/run_depgate_variant_sorted.py` (header ghi đầy đủ cơ chế
  nondeterminism); orchestration `exp_depgate/orchestrate_{d123,sorted}.sh`.
