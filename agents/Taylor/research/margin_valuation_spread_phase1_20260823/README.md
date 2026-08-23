# PHASE 1 — margin theo KHOẢNG CÁCH ĐỊNH GIÁ, tầng ENGINE · **VERDICT: NO-GO**

> Job `Taylor_20260823_120317` · 2026-08-23 · RESEARCH-ONLY, **production KHÔNG bị sửa**.
> Prereg: `PREREG.md`, commit **`e27e5ec1`** — viết + commit **TRƯỚC** khi chạy leg đầu tiên.
> Plan gốc user duyệt: `agents/Taylor/plan_margin_valuation_spread_20260823.md`.
> **VÒNG CUỐI** trên tập 7 episode `dd52<=-20%` (user + Mike đồng thuận dừng sau vòng này).

## 0. Kết luận một đoạn

Ở tầng engine, **khoảng cách định giá KHÔNG mang thông tin gia tăng nào so với cổng `dd52<=-20%`
đang chạy**. Hợp hai trục (V7 = dd52 **hoặc** spread) cho CAGR **thấp hơn** cổng dd52 thuần
−0,0086pp và IS **thấp hơn** −0,018pp ở lãi vay thật 12,5% ⇒ **cổng G1 FAIL ở cả 3 mức lãi vay**.
Nhánh tranche V8 **trùng V0 tới 0 VND** trên 3.107 phiên (đúng như prereg §4.1 đã cảnh báo trước:
bậc T2/T3 không có một sự kiện nào trong cửa sổ engine) ⇒ **G6 không thể PASS**.

**Nhưng phát hiện quan trọng hơn cả verdict là về CÔNG CỤ**: tôi đo được **biên độ nhiễu path của
chính harness = 0,3854pp CAGR**, trong khi đại lượng H1 cần đo (|V7 − V0|) chỉ **0,0086pp** —
**nhiễu lớn gấp 45 lần tín hiệu**. Nghĩa là kể cả nếu spread CÓ tác dụng ở cỡ này, full-run engine
diff **không có khả năng phân giải nó**. Đây là giới hạn công cụ, phải nói rõ, không được đọc thành
"hiệu ứng bằng 0".

**Không có khuyến nghị wire. Không shadow-monitor "để dành" cho cơ chế sizing** (đúng prereg §7).
Việc B (dòng shadow-log hiển thị trong EOD) là mandate riêng, tách rời, đã xong — xem §7.

## 1. Hai điều kiện tin cậy — cả hai PASS trước khi đọc bất kỳ số nào

| Điều kiện | Kết quả |
|---|---|
| Chân control `f=1,0` tái lập pin R3 | CAGR **28,8627%** / MaxDD **−17,7851%** / Calmar **1,6229** / NAV cuối **1.178,0099B** / IS **27,0925%** / OOS **30,4786%** — **khớp tuyệt đối** |
| `engine_p1.py` INERT khi tắt 2 hunk | vs `E125_f13` (chạy 2026-08-03): **max \|diff\| = 0,0 VND trên 3.107 phiên** |
| `self-check 0 VND` | cash-flow identity max err = 0 VND, cả 2 book, mọi leg |

## 2. Bảng chính — 9 biến thể × 3 mức lãi vay (delta so BASE `f=1,0`)

`dMaxDD` ÂM = rủi ro XẤU đi. Bảng đầy đủ: `metrics_p1.csv`, log `logs/metrics_p1.log`.

**Lãi vay 12,5%/năm — số THẬT gói 1840 RocketX (trục đối chứng chính):**

| V | f | N sự kiện | CAGR | **dCAGR** | Sharpe | MaxDD | dMaxDD | dIS | dOOS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **V0** (production `dd52`) | 1,3 | 5 | 29,449% | **+0,586pp** | 1,869 | −17,819% | −0,034 | +0,302 | +0,858 |
| V1 (EY−margin ≥ 0) | 1,3 | 5 | 29,403% | +0,540pp | 1,863 | −17,788% | −0,003 | +0,251 | +0,816 |
| V2 (EY−margin ≥ +1pp) | 1,3 | **1** | 28,999% | +0,137pp | 1,836 | −17,787% | −0,002 | +0,246 | +0,033 |
| V3 (DY−deposit ≥ 0) | 1,3 | 5 | 29,526% | **+0,663pp** | 1,861 | −17,822% | −0,037 | +0,448 | +0,869 |
| V4 (V1 ∪ V3) | 1,3 | 6 | 29,505% | +0,642pp | 1,860 | −17,822% | −0,037 | +0,448 | +0,827 |
| V5 (V2 ∧ DT5G≥2) | 1,3 | **1** | 28,999% | +0,137pp | 1,836 | −17,787% | −0,002 | +0,246 | +0,033 |
| V6 (V5, f=1,5) | 1,5 | **1** | 28,998% | +0,135pp | 1,836 | −17,787% | −0,002 | +0,242 | +0,033 |
| **V7 (V0 ∪ V5) — test H1** | 1,3 | 6 | 29,440% | **+0,578pp** | 1,869 | −17,817% | −0,032 | +0,284 | +0,859 |
| V8 (V0 + tranche vốn) | 1,3 | 5 | 29,449% | +0,586pp | 1,869 | −17,819% | −0,034 | +0,302 | +0,858 |

## 3. Câu hỏi H1 — spread có THÊM gì so với `dd52` không? **KHÔNG.**

| Lãi vay | dCAGR (V7−V0) | dIS | dOOS | dMaxDD | G1 |
|---|---:|---:|---:|---:|---|
| 10% | **−0,0065pp** | −0,0138pp | +0,0004pp | +0,0013pp | **FAIL** |
| **12,5% (THẬT)** | **−0,0086pp** | −0,0179pp | +0,0003pp | +0,0016pp | **FAIL** |
| 15% (stress) | **−0,0095pp** | −0,0213pp | +0,0017pp | +0,0018pp | **FAIL** |

`V7 ∖ V0 = {E3 2016-01-18}` — **đúng một sự kiện**, và thêm nó làm CAGR **giảm** ở cả 3 mức lãi vay.
Đây chính là rủi ro tôi tự khai ở plan §10 ("V7 ≈ V0 ⇒ NO-GO, khả năng cao nhất") và ở prereg §4.3
(**trước khi chạy**) — nó xảy ra đúng như dự báo.

**V8 vs V0: max |diff| = 0,0 VND trên 3.107 phiên, ở cả 3 mức lãi vay.** Thang tranche khai trước
(T1 −20…−27,5 / T2 −27,5…−35 / T3 −35…−45) có **cả 5 sự kiện armed đều nằm trong T1** (dd52 −20,6%
… −25,3%); T2/T3 rỗng. Đáy 2022-11-15 (dd52 −40,3%) **không sinh washout event nào** nên T3 không
tồn tại kể cả về nguyên tắc. ⇒ **nhánh tranche KHÔNG có bằng chứng engine, không được khuyến nghị.**

## 4. Phát hiện phương pháp — THƯỚC ĐO NHIỄU (quan trọng nhất của vòng này)

Lãi vay là tham số chỉ **làm giảm** CAGR cho một chính sách CỐ ĐỊNH. Mọi vi phạm đơn điệu đo được
chính là **biên độ nhiễu path** của harness, tính bằng **cùng đơn vị** với đại lượng đang muốn đo.

| V | @10% | @12,5% | @15% | vi phạm đơn điệu |
|---|---:|---:|---:|---:|
| V0 / V1 / V2 / V4 / V5 / V6 / V7 / V8 | — | — | — | **0,0000pp** |
| **V3** | +0,2779 | **+0,6633** | +0,6570 | **+0,3854pp** ← không thể về kinh tế |

**Kiểm chứng độc lập**, đóng góp biên của **đúng một sự kiện** E6 (2020-02-03), = V4 − V3:
**+0,3751pp @10% · −0,0211pp @12,5% · −0,0222pp @15%** — **đổi dấu**, biên độ **0,3973pp**.
Đã xác minh không phải lỗi cấu hình: `*_leveraudit.csv` của V3 ở cả 3 mức lãi vay lever **đúng cùng
5 sự kiện {0,2,3,7,8}**, `loan_vnd` lệch < 0,05%. Đây là **path-divergence thật** — chênh lệch NAV
cực nhỏ làm lật các quyết định RỜI RẠC (slot, `max_positions`, trần %ADV) rồi compound 12,5 năm.

> **Tỷ lệ tín hiệu/nhiễu = 0,0086 / 0,3854 = 0,022.** Nhiễu lớn hơn tín hiệu **45 lần**.
> Full-run engine diff **không phân giải được** hiệu ứng ở cỡ này. Mọi tuyên bố "biến thể X hơn
> biến thể Y +0,08pp" trong họ này đều **nằm dưới ngưỡng phân giải của công cụ**.

Hệ quả trực tiếp: V3 (+0,663) và V4 (+0,642) "hơn" V0 (+0,586) lần lượt +0,077pp và +0,056pp —
**nhỏ hơn nhiễu 5-7 lần**, không được đọc là ưu thế.

## 5. Sáu cổng GO/NO-GO (prereg §7, không sửa sau khi thấy số)

| # | Cổng | Kết quả |
|---|---|---|
| 1 | V7 > V0 cả IS lẫn OOS, dCAGR OOS > 0 | 🔴 **FAIL** — dCAGR −0,009pp, dIS −0,018pp (cả 3 mức lãi vay) |
| 2 | ≥1 biến thể dCAGR FULL ≥ +0,30pp và dMaxDD xấu ≤ 0,50pp | 🟡 **PASS nhưng KHÔNG PHÂN BIỆT** — chính **V0 (control)** cũng qua (+0,586 / −0,034). Không biến thể MỚI nào vượt V0 quá ngưỡng nhiễu |
| 3 | DSR ≥ 0,95 trên chuỗi excess | 🔴 **FAIL cho TẤT CẢ**, gồm cả V0 đang LIVE (DSR 0,22–0,31 @N=8) ⇒ cổng như tôi đặc tả **không phân biệt được biến thể**, xem §5.1 |
| 4 | LOO theo episode, bỏ episode lớn nhất vẫn > 0 | 🟡 PASS trên V3 (bỏ E8 còn +0,239pp) — nhưng **N/A**: V7 đã trượt G1, và V2/V5/V6 có N=1 nên G4 vô nghĩa theo định nghĩa |
| 5 | 0 margin call @ maintenance 40% + lãi vay 15% | 🟢 **PASS** — 0 call / 0 liquidation trên 27 leg; equity_ratio mỏng nhất **87,24%** (2014-05-13, V3), cách ngưỡng gọi ký quỹ **47,24pp** |
| 6 | Dose-response đơn điệu theo thang spread và thang V8 | 🔴 **FAIL** — thang V8 **không kiểm định được** (V8 ≡ V0, 0 VND); thang spread V1(+0,540) → V2(+0,137) giảm khi siết ngưỡng, nhưng lẫn với "ít sự kiện hơn" nên không đọc được |

**PBO/CSCV** (N_trials = 8 ⇒ chạy đúng theo prereg): **0,071 / 0,124 / 0,080** ở S = 8/12/16 — đều
< 0,5, PASS. Nhưng PBO thấp ở đây phản ánh **mọi leg gần như trùng nhau**, không phải "chọn được
cấu hình bền".

⇒ **3/6 cổng FAIL (1, 3, 6); cổng 2 chỉ qua một cách tầm thường vì control cũng qua ⇒ NO-GO.**

### 5.1 Đính chính một đặc tả của chính tôi — cổng G3 sai chỗ, không phải biến thể sai
Prereg §7-3 đặt DSR trên **chuỗi excess**. Đo xong mới thấy: trên chuỗi excess **mọi leg đều RED**,
kể cả V0 đang chạy LIVE (DSR 0,288 @N=8). Trên **chuỗi của chính leg** (đúng cách D-step 2026-08-03
báo DSR 1,0000) thì mọi leg đều ~1,0 — **kể cả control**. Nguyên nhân: DSR-trên-leg đo *"danh mục
V2.4 có tốt không"* (câu trả lời: có, và lớp đòn bẩy hầu như không đổi được điều đó), còn
DSR-trên-excess đo *"lớp đòn bẩy có thêm gì không"* trên một chuỗi gần như toàn số 0 cộng nhiễu.
**Không cái nào phân biệt được biến thể ở cỡ hiệu ứng này.** Ghi lại để lần sau không dùng DSR làm
cổng phân biệt khi hiệu ứng nằm dưới ngưỡng nhiễu của harness — hãy đo ngưỡng nhiễu TRƯỚC.
Đây là lỗi đặc tả cổng của tôi, không phải phát hiện về biến thể.

### 5.2 Một điểm loại thẳng riêng cho V3/V4
Prereg §7 (và plan §2.5): *biến thể nào tốt hơn nhờ arm trong CRISIS ⇒ loại thẳng*. **V3 và V4 arm
E0 (2014-05-08) khi DT5G = 1 (CRISIS)** — mâu thuẫn nguyên tắc kiến trúc "chỉ arm ở PHA HỒI PHỤC".
Đóng góp của E0 chỉ +0,062pp (9,4% edge) nên chúng không tốt hơn *nhờ* CRISIS, nhưng chúng **vi phạm
kiến trúc**, và đó là lý do thứ hai đủ để không đề xuất chúng — độc lập với chuyện thống kê.

## 6. Điều gì KHÔNG kết luận được (giới hạn phải mang theo khi trích)

1. **Không kết luận "spread vô dụng".** Chỉ kết luận: ở tầng engine, qua kênh CAPIT, cỡ hiệu ứng của
   nó **nhỏ hơn ngưỡng phân giải của harness 45 lần**. Bằng chứng tầng vị thế (Phase 0: net12 median
   +30,2pp cho 4 episode DY≥deposit vs −4,9pp baseline) **không bị vòng này bác bỏ** — nó chỉ không
   sống sót qua tầng danh mục, vì kênh CAPIT quá nhỏ để truyền tải (D-step đã đo: đòn bẩy chỉ nhân
   lên phần vốn máy thực đặt vào washout, trung bình **0,272 NAV-book**, trên **1 trong 2 book**).
2. **Chuỗi lãi vay LỊCH SỬ vẫn là giả định `deposit + 5,0pp`.** Chỉ mức HÔM NAY (12,5%) là số thật.
   Mọi ngưỡng V1/V2/V4/V5/V6/V7 phụ thuộc giả định này — mắt xích yếu nhất, không sửa được bằng code.
3. **`deposit_rate_vn` có 26 mốc neo hồi tố cùng 1 lần 2026-06-19** ⇒ không point-in-time thật cho
   quá khứ; mọi kết luận lịch sử mang bias hindsight ở mức "biết đúng hình dạng chu kỳ lãi suất".
4. **Cửa sổ engine chỉ từ 2014** ⇒ hai episode spread mạnh nhất (2009-02 EY−margin +6,62pp;
   2012-11 DY−deposit +2,49pp) **không bao giờ có bằng chứng engine**. Đây là ràng buộc cứng, đã khai
   ở plan §6.4 trước khi chạy.
5. **G5 PASS không phải "an toàn tuyệt đối"** — nó nói: ở kênh CAPIT-only với f ≤ 1,5, gọi ký quỹ
   **không phải ràng buộc ràng buộc**. Ràng buộc thật là **không có edge**, không phải rủi ro cưỡng chế bán.

## 7. Việc B — shadow-log spread trong EOD (mandate riêng, ĐÃ XONG, tách rời kết quả trên)

`build_margin_spread_line()` + `get_margin_spread()` trong `dna_report.py`
(commit WorkingClaude **`5028becb`**), wire vào `mike/bin/eod_trading_report.sh`
(commit mike **`e1c0416f`**).
- Lãi vay **không hardcode**: đọc `data/trading_rules.json::capit_margin_lever.borrow_rate_annual`
  (nguồn + ngày xác nhận 2026-08-23 ghi trong docstring) ⇒ DNSE đổi biểu phí thì dòng report tự đổi.
- Tái dùng đúng khuôn §6b `coding_guidelines` (`build_dt_gate_line`/`build_value_radar_line`),
  fail-safe trả `None` ⇒ caller bỏ dòng, không crash report.
- **DISPLAY-ONLY**: không tác động sizing, không là gate, không ghi `trading_rules.json`.
- Test chạy **THẬT** (không fixture) 2026-08-23, gọi chính hàm `_dt_gate_line()` trích từ file
  production: `💵 Spread định giá: 🔴 EY median 9.24% − lãi vay 12.5% = -3.26pp · chỉ hiển thị,
  không tác động sizing/gate  [dữ liệu tới 2026-08-21, 339/358 mã có PE>0]`.
  So tay: khớp EY_med 9,24% đo độc lập ở `plan_margin_valuation_spread_20260823.md` §2.6.

## 8. Artifact

| File | Nội dung |
|---|---|
| `PREREG.md` | pre-registration, commit `e27e5ec1` trước mọi leg |
| `engine_p1.py` | bản sao `p5_engine/engine_lever.py` + 2 hunk khai trước (A: sửa lỗi tính lãi vay trên sự kiện KHÔNG được lever; B: `CAPIT_LEVER_TRANCHE`) |
| `run_p1.sh`, `driver.sh`, `driver_loo.sh`, `joblist*.txt`, `variants.json` | lệnh chạy đầy đủ, tái lập được |
| `arm_conditions_events.csv`, `build_arm_table.py`, `_dy_daily.csv` | bảng điều kiện ARM tại 15 sự kiện, đo theo NGÀY |
| `metrics_p1.csv` / `.py`, `margincall_p1.csv` / `.py`, `noise_ruler_p1.py`, `loo_episode_p1.csv` / `.py` | phân tích |
| `logs/` | 34 log leg + 4 log phân tích |
