# LAG/PEAD — xếp hạng chất lượng trong cửa sổ nhìn trước thay vì FIFO theo ngày công bố

**Job** `Taylor_20260804_051145` · Taylor · 2026-08-04
**Trạng thái: NGHIÊN CỨU — KHÔNG WIRE. Kết luận = KHÔNG ĐỦ BẰNG CHỨNG (not proven), không phải "nên làm".**
Không sửa file production nào. Toàn bộ chạy trên bản sao trong `mike/agents/Taylor/exp_lagrank_20260804/`.
`git diff` trên `deploy_golive_dt5g_v4/`, `pt_v23_audit_2014.py`, `simulate_holistic_nav.py` = sạch (bản sao riêng).

---

## 0. Câu trả lời 1 dòng

Ý tưởng **đúng về mặt cơ chế** (hiệu ứng dịch đúng chiều theo quy mô vốn như lý thuyết dự đoán), nhưng
**độ lớn không phân biệt được với nhiễu**: ở quy mô SpaceX/ZaloPay (NAV 1B) biến thể tốt nhất cho
**+0,79pp CAGR/năm với t = 0,88** (cần ~2), **DSR trên phần tăng thêm = 0,51** (cổng 0,95), **LOO: bỏ 2
năm tốt nhất là hết sạch edge**, **MaxDD xấu đi ở 10/10 biến thể** và **Calmar tốt nhất chỉ BẰNG** FIFO.
Ngay trong chế độ ràng buộc vẫn có **4/10 biến thể ÂM**; ở NAV 50B thì **9/10 ÂM**. → **NO-GO cho wire.**
Chi tiết dưới đây, kể cả phần ủng hộ ý tưởng (PBO ở 1B = 0,475, đạt cổng — cổng duy nhất đi qua được).

---

## 1. Câu hỏi 1 — Định nghĩa "cửa sổ nhìn trước" và cách xếp hạng

### 1.1 Cơ chế (không đổi luật T+5)

Luật T+5 giữ nguyên tuyệt đối: mỗi mã vẫn chỉ được MUA đúng phiên T+5 sau `Release_Date` của nó.
Chỉ **THỨ TỰ ƯU TIÊN VỐN** thay đổi, và chỉ khi vốn/slot không đủ cho tất cả:

| Tham số | Giá trị thử | Ý nghĩa |
|---|---|---|
| `LAGRANK_WINDOW` (K) | **0** | Chỉ sắp xếp lại các ứng viên **đã đến hạn hôm nay** (không giữ vốn lại). Không bỏ tín hiệu nào. |
| | **5** | **Đặt chỗ vốn trước**: gom cả ứng viên sẽ đến T+5 trong **5 phiên tới** vào cùng một bảng xếp hạng. Ứng viên đến hạn hôm nay mà **thua hạng** một mã sắp tới sẽ bị **HOÃN** (giữ vốn lại cho mã hạng cao hơn). |
| `LAGRANK_KEY` | 5 khoá (§1.2) | Metric xếp hạng |

Hợp lệ point-in-time vì: một mã "sắp tới T+5 trong 5 phiên tới" là mã có `Release_Date` **đã nằm trong
QUÁ KHỨ** — biết được ngày T+5 của nó không cần bất kỳ thông tin tương lai nào.

Hoãn tiêu 1 ngày trong hạn `max_fill_days=5` sẵn có (đúng quy ước hao hụt đang dùng cho ca thiếu tiền/
hết slot — **không phát minh cơ chế thực thi mới**), và không bao giờ đụng vào lệnh đã khớp một phần.
Không có dòng tiền nào bị dịch chuyển ở bước này → self-check dòng tiền không bị ảnh hưởng.

### 1.2 Năm metric xếp hạng + xác nhận POINT-IN-TIME (điều kiện bắt buộc)

Kiểm tra từng khoá tới tận nguồn. **Không khoá nào chạm `profit_*` hay bất kỳ cột forward nào.**

| Khoá | Định nghĩa | Nguồn | Bằng chứng PIT |
|---|---|---|---|
| `surprise` | `surprise_B_MA` = (NP_P0 − mean(NP_P1..P4)) / max(\|exp\|,1e9), clip ±5 | `data/earnings_surprise_data.pkl` | Toàn bộ là quý **đã công bố** tại `Release_Date` — `pt_v23_audit_2014.py:1005-1006` |
| `dnpr` | `d_NPR` = NP_R quý này − NP_R quý trước (gia tốc tăng trưởng LN) | `ev.groupby("ticker")["NP_R"].diff()` | 2 quý đã báo cáo, `:1015` |
| `pahl3` | Bình quân **suy giảm theo nửa đời 3 năm** của post-return các sự kiện **TRƯỚC ĐÓ** | vòng lặp `:1017-1029` | `hist.append(...)` nằm **SAU** khi gán `pa_HL3` → post_ret của chính sự kiện đang xét **không bao giờ** vào công thức. Đây là chỗ dễ rò rỉ nhất và code gốc đã đúng. |
| `fill` | `log1p(ADV)`, ADV = `Volume_3M_P50 × PxAdv` tại ngày tín hiệu (T+4) | `liq_lag[(tk,sd)]`, `:1329-1332` | Median volume 3 tháng **trailing**, giá tại/trước ngày xếp hạng. Đại diện cho "đặt được bao nhiêu % slot mục tiêu" mà dispatch hỏi. |
| `blend` | `z(surprise) + z(pahl3)` với **z GIÃN DẦN** | `engine_lagrank.py:_z()` | `mean/std` dùng `.expanding().shift(1)` theo thứ tự ngày tín hiệu → hằng số chuẩn hoá **chỉ từ sự kiện trước đó**. z toàn mẫu sẽ rò rỉ phân phối 2014-2026 vào quyết định năm 2014 — nhỏ nhưng là look-ahead thật, đã tránh. |

**DCF margin-of-safety** (dispatch có gợi ý) **cố ý không đưa vào**: `dcf_valuation.py` là non-decisional,
không có chuỗi giá trị point-in-time theo ngày cho toàn universe 2014-2026, dựng mới sẽ là nguồn
look-ahead lớn nhất trong cả bài. **8L rating** cũng không dùng làm khoá xếp hạng vì nó **đã là cổng
nhị phân ≤3 chạy trước** — mọi ứng viên trong bảng đều đã pass, xếp hạng bằng nó gần như vô nghĩa
(và KB đã ghi: rating là *gate*, không phải *return-tilt*).

---

## 2. Câu hỏi 2 — Có mô phỏng ĐÚNG tình huống thiếu vốn không? **CÓ, đo được**

Đây là điều kiện dispatch nhấn mạnh nhất, nên kiểm chứng trước khi đọc bất kỳ số P&L nào.

Chạy song song **hai quy mô NAV, cùng một panel tín hiệu** (5.317 tín hiệu LAG ở cả hai):

| | NAV 50B (chuẩn repo) | **NAV 1B (quy mô SpaceX/ZaloPay)** |
|---|---|---|
| Sự kiện cổ phiếu book LAG | 5.997 | **2.278** |
| Lệnh vào LAG khớp thật (N_ent) | 1.498 | **795** |
| Tên riêng biệt (N_tk) | 506 | **357** |

**Cùng một tập tín hiệu, NAV 1B chỉ hấp thụ được 53% số lệnh vào của NAV 50B.** Ràng buộc vốn có thật
và cắn mạnh ở 1B → rule "ưu tiên khi thiếu vốn" **có đất diễn**, không phải no-op. Ở 50B ràng buộc
lỏng hơn nhiều (đúng như dispatch dự đoán) — 50B ở đây đóng vai **chân đối chứng cho giả thuyết cơ chế**
(nếu rule chỉ hoạt động qua kênh thiếu vốn, hiệu ứng ở 50B phải ~0), không phải chân quyết định.

Chứng cứ trực tiếp cơ chế có kích hoạt: ở K=5, log in ra **1.108-1.114 phiên có ≥1 lần hoãn, tổng
16.450-16.629 lượt hoãn, trung vị 16 lượt/phiên**.

> ⚠️ **Giới hạn phải nói rõ**: 1B mô phỏng **ràng buộc vốn CƠ CẤU** (sổ nhỏ so với dòng tín hiệu). Nó
> **KHÔNG** mô phỏng đúng ca SpaceX/ZaloPay đang gặp — 3+ tuần HOLD ALL vì tiền **kẹt trong vị thế
> đang nắm và không có lệnh bán**. Đó là ràng buộc cấp tính, có tính giai đoạn, và bản chất là bài
> toán **thanh lý/luân chuyển vốn**, không phải bài toán xếp hạng ứng viên mua. Kết quả dưới đây
> **không trả lời được** ca đó; xem §5.2.

---

## 3. Câu hỏi 3 — N và độ rộng (rủi ro chính)

`w0` = chỉ sắp xếp lại; `w5` = có đặt chỗ vốn (bỏ qua tín hiệu yếu hơn).

**NAV = 1B:**

| Biến thể | N_ent | Δ | N_tk | Δ | HHI | Δ |
|---|---|---|---|---|---|---|
| **FIFO (baseline)** | **795** | — | **357** | — | 0,0047 | — |
| A_surprise **w0** | 816 | +2,6% | 366 | +2,5% | 0,0047 | 0% |
| A_blend w0 | 801 | +0,8% | 355 | −0,6% | 0,0048 | +2% |
| B_surprise **w5** | 660 | **−17,0%** | 314 | **−12,0%** | 0,0055 | **+17%** |
| B_blend w5 | 662 | **−16,7%** | 316 | **−11,5%** | 0,0054 | **+15%** |
| B_dnpr w5 | 672 | **−15,5%** | 322 | **−9,8%** | 0,0052 | **+11%** |
| B_fill w5 | 635 | **−20,1%** | 299 | **−16,2%** | 0,0056 | **+19%** |

**Kết luận độ rộng — tách bạch 2 chế độ:**

- **`w0` (chỉ sắp xếp lại) KHÔNG làm mất độ rộng gì cả** (N_ent còn nhỉnh hơn baseline vì thứ tự tốt
  hơn giúp khớp được nhiều hơn trong hạn 5 ngày). Đây là biến thể **an toàn với đặc trưng học thuật
  của PEAD** (edge đến từ độ rộng). Nếu sau này có lý do làm gì đó, đây là dạng duy nhất không đánh đổi.
- **`w5` (đặt chỗ vốn) mất độ rộng thật**: −17% lệnh, −12% tên, tập trung +17%. **Đúng rủi ro dispatch
  cảnh báo.** Ở 50B còn nặng hơn: N_ent 1.498 → 1.146-1.178 (−22%).

**Kiểm tra sâu — mất độ rộng có phải nguyên nhân gây lỗ không?** Đếm lệnh vào theo từng năm (NAV 1B):
mức cắt của `w5` **đều đặn 15-25% ở MỌI năm**, không dồn vào năm nào. Trong khi đó **2021 là năm tệ
nhất của MỌI biến thể** (−3,9 đến −11,1pp so với FIFO) — kể cả các biến thể `w0` **không cắt lệnh nào**.

→ Nên **không** quy được khoản lỗ 2021 cho việc mất độ rộng. Nguyên nhân là **chất lượng lựa chọn**:
trong năm bull mạnh nhất mẫu, đúng những tên bị các khoá này xếp hạng thấp lại là những tên chạy tốt.
Đây là một phát hiện độc lập và **bất lợi hơn** cho ý tưởng: nếu chỉ là mất độ rộng thì còn chỉnh được
bằng cách nới K; còn khoá xếp hạng **chọn sai trong bull** thì là vấn đề của chính metric.

---

## 4. Câu hỏi 4 — IS/OOS, N_trials, DSR, PBO, LOO

### 4.1 Khai báo N_trials (kỷ luật multiple-testing, KB §5)

**N_trials = 10 cho mỗi quy mô NAV** = 5 khoá xếp hạng × 2 cấu hình cửa sổ (K∈{0,5}).
Tổng số lần chạy engine: **24** = 20 biến thể + 2 chân đối chứng FIFO + 2 chân **copy-control**.
Không có vòng tune nào khác; K=5 và 5 khoá chọn **trước** khi nhìn kết quả đầu tiên.

### 4.2 Self-check bắt buộc — chân đối chứng tái lập số đã pin

| | FULL CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| `L0_ctrl50B` (engine production) | 28,86% | 1,90 | −17,8% | 1,62 |
| **R3 pin chính thức `results_registry.md` (2026-08-03)** | **28,86%** | **1,90** | **−17,8%** | **1,62** |
| `L0b_copyctrl50B` (engine bản sao, `LAGRANK_KEY=off`) | 28,86% | 1,90 | −17,8% | 1,62 |

`copyctrl` khớp control **tuyệt đối trên cả 5 chỉ tiêu VÀ cả 13 năm (Δ = +0,0pp mọi năm)** ở cả 1B và
50B → **bản sao engine với knob TẮT là byte-identical**, mọi chênh lệch dưới đây là do chính cơ chế.
Self-check dòng tiền = **0 VND** ở mọi chân.

### 4.3 Kết quả — dấu ĐẢO NGƯỢC theo quy mô vốn

**Phần tăng thêm so với FIFO (%/năm), tính từ chuỗi hiệu log-return hàng ngày:**

| Biến thể | **NAV 1B (ràng buộc)** | **NAV 50B (không ràng buộc)** |
|---|---|---|
| A_dnpr w0 | +0,28 | −0,01 |
| A_surprise w0 | +0,57 | −0,94 |
| A_pahl3 w0 | −0,26 | −0,30 |
| A_fill w0 | +0,27 | −0,93 |
| A_blend w0 | +0,52 | −0,49 |
| **B_surprise w5** | **+0,79** | −0,91 |
| B_pahl3 w5 | +0,69 | −0,30 |
| B_blend w5 | +0,36 | −0,52 |
| B_dnpr w5 | **−0,47** | −0,61 |
| B_fill w5 | **−0,21** | +0,04 |
| | **6/10 dương** | **1/10 dương** |

**Điểm ỦNG HỘ ý tưởng, ghi nhận sòng phẳng**: tỉ lệ dấu dịch rõ theo quy mô vốn (**6/10 ở 1B vs 1/10 ở
50B**) — đúng chiều dose-response mà cơ chế dự đoán (chỉ có thể giúp khi vốn thật sự cắn). Nếu rule là
nhiễu thuần thì không có lý do gì để dấu sắp xếp theo quy mô NAV như vậy.

**Nhưng ngay trong chế độ ràng buộc, 4/10 biến thể vẫn ÂM** (`pahl3` w0 −0,26; `dnpr` w5 −0,47;
`fill` w5 −0,21). Tức **bản thân việc xếp hạng không tự động tốt** — nó phụ thuộc hoàn toàn vào chọn
đúng khoá, mà "khoá nào đúng" lại chính là thứ đang được chọn hậu nghiệm từ 10 lần thử.

**Nhưng độ lớn không qua nổi cổng nào:**

| Biến thể (NAV 1B) | +%/năm | IR năm | **t-stat** | **DSR (phần tăng thêm)** |
|---|---|---|---|---|
| B_surprise w5 (tốt nhất) | +0,79 | 0,25 | **0,88** | **0,51** |
| B_pahl3 w5 | +0,69 | 0,24 | 0,83 | 0,49 |
| A_surprise w0 | +0,57 | 0,21 | 0,72 | 0,45 |
| A_blend w0 | +0,52 | 0,22 | 0,78 | 0,47 |

t-stat cao nhất **0,88** — chưa đạt ngay cả mức ý nghĩa danh nghĩa (~2) **trước khi** khấu trừ
multiple-testing. `DSR` trên phần tăng thêm cao nhất **0,51**, cổng 0,95 → **RED FLAG toàn bộ 10/10**.

> Ghi chú phương pháp: DSR trên **mức tuyệt đối** = 1,0000 cho **mọi** chân, kể cả FIFO baseline — vì
> tất cả đều là cùng một hệ V2.4 Sharpe ~1,6/12,5 năm, chỉ khác một phép sắp xếp. Con số đó **vô nghĩa
> cho quyết định wire**. Nên áp DSR lên **chuỗi hiệu** (treatment − baseline), tức "phần THÊM có phân
> biệt được với 0 sau khi khấu trừ 10 lần thử không". Đó là bảng trên.

### 4.4 PBO (CSCV, S=16)

Tính trên **họ đầy đủ 11 cấu hình** (10 biến thể + FIFO) ở mỗi quy mô:

- **NAV 1B: PBO = 0,475** (< 0,5 → **ĐẠT**) · **NAV 50B: PBO = 0,747** (≥ 0,5 → **KHÔNG ĐẠT**)

Đây là **cổng duy nhất mà chế độ ràng buộc vốn đi qua được** — ghi nhận đúng mức. Ở 50B thì PBO 0,75
nói thẳng: cấu hình thắng IS ở quy mô đó chủ yếu là hiện tượng chọn hậu nghiệm → **ưu tiên cấu hình
robust-trung vị, không lấy IS-best**, và cấu hình robust-trung vị ở đây chính là **FIFO hiện tại**.

> ⚠️ Số PBO phải tính trên **toàn bộ** họ đã thử. Bản tính giữa chừng khi còn thiếu 2 chân (9 cấu hình)
> cho 0,567 ở 1B; thêm đủ `B_dnpr_w5` + `B_fill_w5` thì thành 0,475. Con số đúng để trích dẫn là
> **0,475** — chính vì độ nhạy này mà việc chạy nốt 2 chân yếu là cần thiết, không phải cho đủ hình thức.

### 4.5 Per-year LOO (OOS 2020+) — tất cả đều LUMPY

| Biến thể | Δ full-OOS | Bỏ 2 năm gánh nhiều nhất | Kết luận |
|---|---|---|---|
| B_surprise w5 (1B) | +1,81pp | **−0,06pp** (bỏ 2026+2023) | edge biến mất sạch |
| A_surprise w0 (1B) | +0,67pp | **−0,86pp** (bỏ 2025+2023) | đảo âm |
| A_blend w0 (1B) | +0,46pp | **−0,97pp** (bỏ 2025+2023) | đảo âm |
| B_pahl3 w5 (1B) | −0,24pp | −1,83pp | âm ngay từ đầu |
| B_blend w5 (50B) | +2,69pp | −0,47pp (bỏ 2021+2020) | đảo âm |

**Không có biến thể nào sống sót phép thử bỏ-2-năm.** Đúng dạng "1-2 năm gánh hết edge = reshuffle-luck"
mà KB §5 yêu cầu loại.

### 4.6 Chỉ tiêu điều chỉnh rủi ro (NAV 1B) — quan trọng hơn CAGR

| | CAGR | Sharpe | **MaxDD** | **Calmar** |
|---|---|---|---|---|
| **FIFO** | 25,90% | 1,67 | **−17,7%** | **1,46** |
| A_surprise w0 | 26,62% | 1,69 | −18,7% | 1,42 |
| A_blend w0 | 26,55% | 1,69 | −18,5% | 1,44 |
| B_surprise w5 | 26,89% | 1,73 | −18,4% | **1,46** |
| B_pahl3 w5 | 26,77% | 1,71 | −19,6% | 1,37 |
| B_fill w5 | 25,64% | 1,64 | −18,2% | 1,41 |
| B_dnpr w5 | 25,32% | 1,64 | −18,1% | 1,40 |
| A_pahl3 w0 | 25,58% | 1,64 | −19,8% | 1,29 |

**MaxDD xấu đi ở 10/10 biến thể** (−17,7% → −18,1%…−19,8%). Calmar tốt nhất chỉ **bằng** FIFO (1,46).
Tức phần CAGR nhích thêm được **mua bằng đúng lượng rủi ro tương ứng** — không có bữa trưa miễn phí.
Trên trục mà đội dùng để quyết (risk-adjusted), **không biến thể nào thắng**.

---

## 5. Câu hỏi 5 — Kết luận & khuyến nghị

### 5.1 Verdict: **NO-GO / KHÔNG ĐỦ BẰNG CHỨNG ĐỂ WIRE**

Không đề xuất thiết kế wiring. Không có biến thể nào "thắng rõ ràng". Áp mọi cổng đã chốt của đội:

| Cổng | Ngưỡng | Tốt nhất đạt được | |
|---|---|---|---|
| t-stat phần tăng thêm | ~2 | 0,88 | ❌ |
| DSR (phần tăng thêm) | ≥0,95 | 0,51 | ❌ |
| **PBO** | <0,5 | **0,475 (1B)** / 0,747 (50B) | **✅ ở 1B** / ❌ ở 50B |
| LOO bỏ-2-năm giữ dấu dương | >0 | −0,06pp | ❌ |
| Calmar > baseline | >1,46 | 1,46 (bằng) | ❌ |
| MaxDD không xấu đi | ≤−17,7% | −18,4% | ❌ |
| Không mất độ rộng PEAD | ~0% | `w5` −16…−20% N | ❌ (`w0`: ✅) |

**1/7 cổng đạt** (và chỉ đạt ở một trong hai quy mô). Chưa cần tới cổng quant-skeptic.

Cổng quyết định vẫn là **t-stat / DSR**: chúng đo trực tiếp "phần thêm có phân biệt được với 0 không",
và câu trả lời là **không, còn xa**. PBO đạt chỉ nói "trong họ này không có hiện tượng chọn hậu nghiệm
nghiêm trọng ở quy mô 1B" — nó **không** biến một hiệu ứng t=0,88 thành hiệu ứng thật.

### 5.2 Nói thẳng phần ý tưởng có lý — và điều kiện để mở lại

Ý tưởng của user **không sai về nguyên lý**, và có 2 tín hiệu ủng hộ thật, không nên bỏ qua:

1. **Tỉ lệ dấu dịch đúng chiều theo quy mô vốn** (6/10 dương ở 1B vs 1/10 ở 50B) — dose-response đúng
   như cơ chế dự đoán, không phải dạng nhiễu ngẫu nhiên.
2. **Biến thể `w0` (chỉ sắp xếp lại, không giữ vốn) không mất độ rộng nào** — nó tránh được rủi ro
   chính mà dispatch lo, và ở 1B cho +0,3…+0,6pp (4/5 khoá dương).
3. **PBO ở chế độ ràng buộc (1B) = 0,475, dưới cổng** — họ cấu hình này không có dấu hiệu overfit
   chọn-hậu-nghiệm nghiêm trọng ở đúng quy mô đang quan tâm.

Vấn đề thuần tuý là **độ lớn quá nhỏ so với nhiễu** trên 12,5 năm dữ liệu. Với IR ~0,25, cần **~60+
năm** dữ liệu để t đạt 2. **Không có lượng backtest thêm nào trên cùng mẫu này cứu được** — chạy thêm
biến thể chỉ làm N_trials tăng và DSR/PBO xấu đi.

**Điều đáng làm tiếp, nếu user muốn theo đuổi** (theo thứ tự giá trị/chi phí):

- **(A) Đo đúng ca thật trước đã.** Ràng buộc thật của SpaceX/ZaloPay là **tiền kẹt trong vị thế đang
  nắm, không có lệnh bán** (3+ tuần HOLD ALL) — **khác** ràng buộc cơ cấu mà 1B mô phỏng. Việc đúng là
  đo trước: trong các đợt HOLD ALL đó, **thực tế đã bỏ lỡ bao nhiêu ứng viên LAG, và chúng diễn biến
  ra sao**. Nếu số lệnh bỏ lỡ nhỏ hoặc chúng không tệ hơn số đã mua thì toàn bộ hướng này vô nghĩa với
  ca thật, bất kể backtest nói gì. **Đây mới là câu hỏi gốc**, và nó rẻ hơn nhiều một vòng backtest nữa.
- **(B) Nếu (A) cho thấy có mất mát thật**, ưu tiên `w0` (sắp xếp lại thuần) chứ **không** `w5`:
  không mất độ rộng, không cần đặt chỗ vốn, rủi ro gần như bằng 0 nếu sai. Nhưng vẫn phải qua cổng
  DSR/PBO/quant-skeptic — và với bằng chứng hiện tại nó **sẽ không qua**.
- **(C) KHÔNG nên**: thêm khoá xếp hạng mới hay quét K rộng hơn trên cùng mẫu 2014-2026. PBO đã 0,57-0,75;
  mỗi lần thử thêm chỉ làm cổng khó hơn mà không thêm thông tin.

### 5.3 Cảnh báo diễn giải

- **Đừng trích "+0,79pp/năm" như một edge.** t=0,88, DSR 0,58, LOO đảo dấu. Đó là một con số **không
  phân biệt được với 0**.
- **Đừng trích các số OOS đẹp** (vd B_blend_w5 50B: OOS Calmar 2,25 vs 1,77). LOO cho thấy chúng do
  2020+2021 gánh; bỏ 2 năm đó là còn −0,47pp. Ngoài ra mọi biến thể **thua ở IS** và thắng ở OOS —
  không có gì được tune trên IS nên đây không phải overfit theo nghĩa cổ điển, mà là **dấu hiệu hiệu
  ứng không ổn định theo chế độ thị trường**, còn đáng ngại hơn cho việc triển khai forward.

---

## 6. Tái lập & phạm vi

```bash
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
D=mike/agents/Taylor/exp_lagrank_20260804
$D/run.sh <TAG> $D/engine_lagrank.py NAV_TOTAL_B=<1|50> LAGRANK_KEY=<off|dnpr|surprise|pahl3|fill|blend> LAGRANK_WINDOW=<0|5>
$DNA_PYEXE $D/analyze_legs.py  <label>=<csv> ...     # chỉ tiêu + N/độ rộng, recompute độc lập từ CSV
$DNA_PYEXE $D/loo_lagrank.py   <base.csv> <label>=<csv> ...
$DNA_PYEXE $D/dsr_pbo_lagrank.py <N_trials> <label>=<csv> ...
```

Môi trường ghim: `$DNA_PYEXE` (pandas 3), `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`,
`AUDIT_END=2026-06-19`, `BQ_CACHE_THREADS=1`, `LAG_ADV_BASIS=price` (mặc định production hiện hành).
Mọi CSV đầu ra mang `EXP_TAG` riêng + hậu tố `_nav1B` (kỷ luật §8 — **không** trùng tên canonical nào).

**Lưới đã quét ĐỦ 24/24 chân** (20 biến thể + 2 control + 2 copy-control). Không có chân nào bị bỏ,
không có phần nào bị cắt ngắn.

**Bug hạ tầng (log, không phải dữ liệu):** attempt-1 của job bị cắt giữa chừng nhưng **tiến trình nền
vẫn sống**; attempt-2 lỡ chạy trùng 6 chân lên cùng đường dẫn log trước khi phát hiện và kill. Hệ quả:
6 file `*_1B.log` chứa NUL bytes (2 tiến trình cùng ghi). **CSV không bị ảnh hưởng** (các tiến trình
trùng bị kill khi còn ở pha nạp BQ, trước khi ghi CSV ~4 phút), và mọi chân đều kết thúc `EXIT=0` +
self-check 0 VND. Bài học đáng ghi: `run.sh` nên khoá theo `EXP_TAG` — cùng họ với §8 (một cấu hình =
một tên đầu ra), nhưng áp cho *log* chứ không chỉ CSV.
