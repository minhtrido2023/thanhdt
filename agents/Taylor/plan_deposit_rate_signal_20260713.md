# PLAN — Tín hiệu lãi suất huy động Big-4 (Pillar A′) bổ sung macro gate DT5G
> Taylor, 2026-07-13 · job Taylor_20260713_124803 · trạng thái: **PLAN PRE-REGISTERED — CHỜ USER DUYỆT, CHƯA CHẠY BACKTEST NÀO**
> Trial MỚI, sổ N riêng. Kế thừa scope `Taylor_20260713_122053` (phần B) + premise-check `Taylor_20260713_114905`.

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

## 2. Điều kiện tiên quyết về dữ liệu (KHÔNG phải trial — việc data-ops, làm trước/song song)

Bằng chứng lịch sử yếu là vấn đề CỐ ĐỊNH không sửa được; nhưng dữ liệu FORWARD sạch thì rẻ và làm
được ngay. Trước khi bất kỳ variant nào được phép wire (kể cả shadow), cần:

1. **Registry entry** cho `deposit_rate_vn.py` / `DEPOSIT_EVENTS` trong `mike/kb/data_registry.md`
   (status: CANONICAL-PROXY, caveat hindsight-anchor ghi rõ) — guideline §9.
2. **Routine cập nhật tháng** (Winston): mỗi đầu tháng chốt Big-4 12M posted rate từ nguồn public
   (website VCB/BIDV/CTG/Agribank, bảng CafeF/Vietstock), append mốc mới **kèm ngày thu thập thật**
   (`collected_date`) — từ nay trở đi chuỗi là point-in-time thật, hết hindsight cho tương lai.
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
- **Tương tác với 2 consumer deposit-rate sẵn có** (khai báo chống nhầm lẫn): (i) deposit-lens
  hurdle trong `rating_8l.py` — tầng rating cổ phiếu, mức tuyệt đối, không liên quan; (ii)
  deposit-gate RECOVERY_PARK floor 7.5% — tầng parking vehicle, mức tuyệt đối, dormant. Pillar A′
  là tầng STATE CAP, xu hướng — 3 tầng đọc cùng 1 chuỗi nhưng không chồng logic. Không sửa 2 cái kia.

## 4. Family pre-registered — sổ N-ledger "DEPOSIT-RATE-GATE": **N = 5, đóng tại đây**

| ID | Variant | Khác D1 chỗ nào | Giả thuyết cần bác/xác nhận |
|---|---|---|---|
| **D1 mirror-full** | 3 ngưỡng {0.5/1.5/3.0} → cap {NEUTRAL/BEAR/CRISIS}, OR-fuse, lag 5, commit 7 | — (bản chuẩn) | Bản sao đối xứng Pillar A có do-no-harm không, hay chết vì 2017 |
| **D2 strong-only** | CHỈ 1 ngưỡng ≥+1.5 → cap BEAR; bỏ tier mild và extreme | Bỏ hẳn tier mild → miễn nhiễm false-positive 2017 (peak 2017 = +1.0 < 1.5) | Insurance tối giản: chỉ phản ứng khi thắt chặt huy động THẬT SỰ mạnh |
| **D3 blind-spot-only** | = D1 nhưng chỉ được fire khi Pillar A im (`refi_chg6m < 0.5`); refi đang tăng → nhường Pillar A | Trả lời thẳng rủi ro corr 0.92: tín hiệu CHỈ lấp đúng điểm mù, zero double-counting | Incremental value thuần — nếu D3 ≈ D1 thì phần trùng Pillar A vô nghĩa |
| **S4 sensitivity** (winner only) | Publication-lag stress: lag 5 → 26 phiên (~1 tháng lịch) | Chuỗi thật thu thập theo tháng — nếu edge chết khi trễ 1 tháng thì nó là ảo giác độ phân giải | Robustness, KHÔNG chọn lại winner bằng nó |
| **A5 ablation** (winner only, read-only) | Per-year LOO + event-list đầy đủ (từng phiên cap binds, forward T+20/T+60) | Đọc, không đổi lựa chọn | Chuẩn DT5G event-audit |

KHÔNG mở thêm biến thể/ngưỡng/trọng-số nào sau khi chạy. Trục trọng-số Big4 đã loại từ §2.3 (không
có dữ liệu per-bank). Muốn thêm gì giữa chừng → dừng, xin user duyệt N mới.

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
7. **Chu kỳ hiện tại có thể tự giải quyết**: deposit 6.8% đang tiến gần floor 7.5% của
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
