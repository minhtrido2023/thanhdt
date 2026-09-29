# A1 — Rate-regime × rổ parking custom30V (job Taylor_20260822_131318)

**Câu hỏi:** +7,4pp của parking custom30V có còn đứng trong bucket lãi suất hiện tại (HIGH, 6,8%)
không, và chi phí của sector-cap ngân hàng là bao nhiêu?

**Trả lời ngắn:** **KHÔNG.** Trong bucket HIGH, rổ parking chạy ≈ **−0,7%/năm** (CI 5–95%
[−22,3; +22,7]) so với đối chuẩn thật của nó là **tiền nhàn rỗi 0%/năm** — tức hoà vốn ở kịch bản
tốt nhất, không phải +7,4pp. Toàn bộ edge parking đo được nằm ở bucket **MID** (+21,2%/năm,
CI[+3,7; +41,2]) và **LOW** (+51,6%/năm, CI[+9,0; +96,9]). Sector-cap ngân hàng **gần như miễn phí
tính trung bình** (cap40 −0,4pp CAGR toàn kỳ; +1,3pp nếu chỉ tính phiên NEUTRAL) nhưng **đắt trong
đúng bucket HIGH** (−3,1pp) và có phương sai theo episode tới ±7pp.

---

## 0. Cảnh báo đọc số — 3 điều phải mang theo

1. **Đối chuẩn ĐÚNG của parking là TIỀN NHÀN RỖI 0%/năm, không phải VNINDEX.** `ETF_PARK={3:0.8}`
   nghĩa là trong NEUTRAL, 80% tiền nhàn rỗi của sổ BAL vào rổ thay vì nằm im (quy ước chi phí
   CLAUDE.md §Backtest: lãi tiền gửi nhàn rỗi 0%/năm). Bảng excess-vs-VNI ở §2 là góc đọc *tương
   đối*; bảng §3 (CAGR tuyệt đối) mới là góc đọc khớp với production.
2. **+7,4pp là delta CAGR của TOÀN HỆ V2.4 có/không parking (pin R3), KHÔNG phải excess của rổ.**
   Nghiên cứu này KHÔNG tái tạo +7,4pp và không phủ định nó về mặt số học — nó trả lời câu hỏi
   khác: *sức sinh lời của chính rổ, phân tách theo bucket lãi suất*. Kết luận "không còn đứng"
   nói về **cơ chế**, không phải về việc số 7,4 sai.
3. **N HIỆU DỤNG = 3 chu kỳ HIGH, 1 chu kỳ LOW, 4 chu kỳ MID** — không phải 675/354/1932 phiên.
   Mọi CI dưới đây đã dùng block-bootstrap L=20 nhưng bootstrap KHÔNG tạo thêm chu kỳ lãi suất.
   Bucket HIGH có 2 episode dài thật (2018-01→2019-12, 2022-10→2023-05) + 11 phiên đuôi 2026-06.

**Caveat nguồn (bắt buộc):** `deposit_rate_vn.py` status **CANONICAL-PROXY**, caveat (b) trong
`kb/data_registry/macro/deposit_rate_vn.md`: **26 mốc lãi suất được neo hồi tố CÙNG 1 lần ngày
2026-06-19**, không phải point-in-time thật. Nhãn bucket cho quá khứ mang **hindsight bias** — biết
trước hình dạng chu kỳ. Chỉ mốc thêm mới từ 2026-06 trở đi mới là PIT thật.

---

## 1. Thiết lập

| Hạng mục | Giá trị |
|---|---|
| Nguồn rổ | `tav2_bq.custom30v_8l` (CANONICAL) — 1.470 dòng / **49 rebal** 2014-08-05→2026-08-05 |
| Giá | `tav2_bq.ticker.Close` (adj ⇒ total return), 204 mã từng vào rổ, 567.889 dòng |
| State | `tav2_bq.vnindex_5state_dt5g_live` (**KHÔNG** dùng bảng không hậu tố = v3.4b BASE) |
| Lãi suất | `deposit_rate_vn.py` `DEPOSIT_EVENTS`, merge_asof backward |
| Bucket | LOW <5,0% · MID 5,0–6,5% · HIGH >6,5% |
| Phủ | 2.961 phiên 2014-08-05 → 2026-06-15; NEUTRAL = 1.795 phiên (60,6%) |
| Thực thi | **T+1**: trọng số dùng cho return phiên *t* = trọng số nắm giữ khi BƯỚC VÀO *t* (`shift(1)`). `effective_from == rebal_date` (đã kiểm BQ) nên áp trọng số mới ngay ngày rebal sẽ là nhìn trước |
| Phí | **CHƯA trừ** (rổ gross). Rebal quý ⇒ turnover thật nhỏ, nhưng mọi số dưới đây là cận trên |

**Selfcheck (0 VND, 4/4 đường):** NAV dựng bằng 2 đường độc lập — (a) `cumprod` daily portfolio
return, (b) sổ cái giá trị từng mã theo VND — khớp tuyệt đối:

```
[selfcheck NAV base]   max|cumprod - so_cai| = 0.000510 VND
[selfcheck NAV cap40]  max|cumprod - so_cai| = 0.000405 VND
[selfcheck NAV cap50]  max|cumprod - so_cai| = 0.000219 VND
[selfcheck ro NGAU NHIEN] max|cumprod - so_cai| = 0.000022 VND
[SELFCHECK PASS] 4/4 duong NAV khop 0 VND
```
(rổ ngẫu nhiên = 30 mã bốc thăm seed 20260822 mỗi kỳ — xác nhận logic trọng số/return không phụ
thuộc nội dung rổ. Sai số ~1e-4 VND trên NAV 1 tỷ = nhiễu float64, không phải lệch logic.)

Phân loại ngân hàng: **`ICB_Code = 8355`**, cho đúng 18 mã ABB/ACB/BID/CTG/EIB/HDB/LPB/MBB/MSB/
OCB/SHB/SSB/STB/TCB/TPB/VCB/VIB/VPB. (Lưu ý: `CLAUDE.md` mô tả `ICB_Code` là "CT/NH/BH/CK" —
thực tế cột này là **mã số ICB dạng FLOAT**, không phải chuỗi 2 ký tự.)

---

## 2. Bảng chính — excess CAGR vs VNINDEX theo bucket (pp/năm)

| scope | n_days | n_epi | bank_w | VNI | rổ gốc | **ex** | bank | nonbank | cap40 | cap50 | ex CI[5,95] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| ALL/LOW | 354 | **1** | 68,4% | 20,95 | 33,08 | **+12,13** | +13,18 | +11,12 | +8,52 | +9,90 | [+2,96; +21,26] |
| ALL/MID | 1932 | **4** | 45,3% | 12,90 | 20,60 | **+7,70** | +15,93 | +3,47 | +9,05 | +8,89 | [+0,17; +15,56] |
| ALL/HIGH | 675 | **3** | 50,5% | −4,00 | 0,90 | **+4,90** | +8,45 | −3,83 | +1,76 | +3,81 | **[−3,83; +15,43]** |
| ALL/* | 2961 | 8 | 49,2% | 9,70 | 17,17 | **+7,46** | +13,48 | +2,32 | +7,08 | +7,69 | [+1,88; +13,56] |
| NEUTRAL/LOW | 188 | 2 | 69,0% | 36,18 | 51,62 | **+15,44** | +16,97 | +23,67 | +17,20 | +17,04 | [+1,50; +26,40] |
| NEUTRAL/MID | 1212 | 15 | 38,9% | 15,51 | 21,16 | **+5,65** | +14,70 | +4,46 | +7,72 | +7,16 | **[−3,80; +15,55]** |
| **NEUTRAL/HIGH** | **395** | **6** | 47,2% | −0,93 | −0,70 | **+0,23** | +0,44 | −4,72 | −0,69 | −0,14 | **[−9,55; +8,35]** |
| NEUTRAL/* | 1795 | 21 | 43,9% | 13,61 | 18,72 | **+5,11** | +10,97 | +3,65 | +6,38 | +6,14 | **[−1,77; +12,54]** |

> `n_epi` ở hàng NEUTRAL là số run NEUTRAL×bucket liên tục — **không** phải số chu kỳ lãi suất độc
> lập (vẫn là 3 HIGH / 1 LOW / 4 MID).

**Đọc:** excess-vs-VNI trong HIGH (+4,90pp) **CI chứa 0** ⇒ không phân biệt được với nhiễu. Trong
đúng chế độ parking chạy (NEUTRAL/HIGH), excess xuống **+0,23pp** — bằng không trên thực tế.

---

## 3. Bảng đối chuẩn ĐÚNG — CAGR tuyệt đối vs tiền nhàn rỗi 0%/năm

| scope | VNI | **rổ gốc CAGR** | CI[5;95] | cap40 | cap50 | bank | nonbank |
|---|---:|---:|---|---:|---:|---:|---:|
| ALL/LOW | 20,95 | **33,08** | [+4,30; +71,61] | 29,46 | 30,85 | 34,12 | 32,07 |
| ALL/MID | 12,90 | **20,60** | [+4,75; +38,82] | 21,95 | 21,79 | 28,83 | 16,37 |
| ALL/HIGH | −4,00 | **0,90** | **[−22,90; +25,88]** | −2,24 | −0,19 | 4,45 | −7,83 |
| ALL/* | 9,70 | **17,17** | [+4,38; +30,89] | 16,79 | 17,39 | 23,18 | 12,02 |
| NEUTRAL/LOW | 36,18 | **51,62** | [+9,01; +96,93] | 53,37 | 53,22 | 53,15 | 59,85 |
| NEUTRAL/MID | 15,51 | **21,16** | [+3,72; +41,17] | 23,23 | 22,67 | 30,21 | 19,96 |
| **NEUTRAL/HIGH** | −0,93 | **−0,70** | **[−22,30; +22,67]** | −1,62 | −1,07 | −0,50 | −5,65 |
| NEUTRAL/* | 13,61 | **18,72** | [+4,82; +34,09] | 19,99 | 19,75 | 24,58 | 17,26 |

**Đây là câu trả lời chính của A1.** Cận dưới 5% của CAGR rổ:
- NEUTRAL/MID **+3,7%** và NEUTRAL/LOW **+9,0%** ⇒ vượt tiền mặt (0%) ở mức tin cậy 5%.
- NEUTRAL/HIGH **−22,3%** ⇒ **KHÔNG** vượt tiền mặt. Trung vị −0,7%. Parking trong bucket lãi
  suất cao lịch sử = hoà vốn với tiền mặt, kèm rủi ro đuôi −22%/năm.
- NEUTRAL/* (gộp) **+4,8%** ⇒ edge parking tổng thể vẫn đứng — nhưng nó **đến từ MID/LOW**.

---

## 4. Chi phí của sector-cap ngân hàng

Cơ chế cap: hạ TỔNG trọng số ngân hàng về 40%/50%, phần dư chia PRO-RATA cho non-bank theo trọng
số hiện có (bảo toàn thứ tự yieldcombo ẩn trong weight gốc — bảng BQ không có cột score để tính
lại yieldcombo PIT), waterfall name-cap 10%. Xác nhận cơ học: `bank weight max = 0.4000/0.5000`,
`name max = 0.1000`, `sum(w) ∈ [0.999997, 1.000003]`.

**Chi phí (âm = cap làm mất tiền), block-bootstrap trung vị vs rổ gốc:**

| scope | cap40 | cap50 |
|---|---:|---:|
| ALL/* | **−0,32pp** | **+0,27pp** |
| NEUTRAL/* | **+1,28pp** | **+1,05pp** |
| ALL/HIGH | **−3,02pp** | −1,02pp |
| NEUTRAL/HIGH | −0,97pp | −0,41pp |
| ALL/MID | +1,49pp | +1,30pp |
| ALL/LOW | −0,67pp | −0,01pp |

**Kết luận về cap: nó KHÔNG phải một chi phí, nó là một đánh đổi PHƯƠNG SAI.** Trung bình toàn kỳ
±1pp (cap50 thậm chí dương nhẹ), nhưng theo từng episode biên độ tới ±7pp:

| bucket | episode | n | bank_w | rổ gốc CAGR | bank | nonbank | **cap40−gốc** | **cap50−gốc** |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | 2014-08→2017-12 | 854 | **0,169** | 16,26 | +15,58ex | −2,73ex | −0,21 | 0,00 |
| HIGH | 2018-01→2019-12 | 500 | 0,450 | −0,39 | +1,45ex | −4,18ex | −1,98 | −0,46 |
| MID | 2020-01→2022-09 | 686 | 0,626 | 29,28 | +28,05ex | +18,02ex | +1,43 | +1,44 |
| HIGH | 2022-10→2023-05 | 164 | 0,653 | 9,87 | +29,34ex | +2,30ex | **−7,28** | −2,98 |
| MID | 2023-06→2024-03 | 209 | 0,734 | 38,79 | +19,30ex | −0,69ex | **+7,25** | +4,87 |
| LOW | 2024-04→2025-08 | 354 | 0,684 | 33,08 | +13,18ex | +11,12ex | −3,62 | −2,23 |
| MID | 2025-09→2026-05 | 183 | 0,807 | −6,09 | −23,58ex | −16,08ex | +2,53 | +2,17 |

Chi phí cap40 tập trung vào **đúng 1 episode** (2022-10→2023-05, cú siết lãi suất, ngân hàng
+29,3pp excess) — và được bù gần hết bởi episode kế tiếp (+7,25pp). Đó là chữ ký của **timing luck,
không phải của một chi phí cấu trúc**.

### ⚠️ Giới hạn quan trọng nhất của nhánh cap

**Trọng số ngân hàng của rổ TĂNG ĐƠN ĐIỆU theo thời gian: 16,9% → 45% → 62,6% → 65,3% → 73,4% →
68,4% → 80,7%.** Cấu hình hôm nay (74–78%) chỉ được thử trong **~3 năm gần nhất** (2023-06 trở đi,
≈750 phiên, 2 episode). Ở nửa đầu mẫu cap-40 gần như không binding (2014-17: chi phí đúng bằng
0,00–0,21pp vì rổ chỉ có 17% ngân hàng). Nghĩa là: **bảng chi phí trên bị pha loãng bởi giai đoạn
cap không có tác dụng gì.** Đọc cột episode, đừng đọc dòng ALL/*.

---

## 5. LOO theo năm (drop 1 năm, excess base vs VNI)

Chỉ drop những năm THỰC SỰ có phiên trong bucket đó (drop một năm ngoài bucket là no-op và sẽ
tạo ra "n_pos" giả — bug này đã xuất hiện ở lần chạy đầu, đã sửa).

| bucket | full | n_loo | n_pos | min | max | chi tiết |
|---|---:|---:|---:|---:|---:|---|
| LOW | +12,13 | 2 | **2/2** | +5,39 | +24,09 | 2024:+24,09 · 2025:+5,39 |
| MID | +7,70 | 7 | **7/7** | +3,01 | +10,18 | 2020:+3,96 2021:+3,01 2022:+10,18 2023:+7,72 2024:+6,94 2025:+9,97 2026:+8,65 |
| HIGH | +4,90 | 4 | **4/4** | +1,93 | +9,63 | 2018:+4,76 2019:+9,63 2022:+4,55 2023:+1,93 |
| * | +7,46 | 9 | **9/9** | +4,58 | +8,98 | — |

LOO **không** lật dấu ở bất kỳ bucket nào ⇒ excess-vs-VNI không do một năm duy nhất. Nhưng LOO đo
độ bền trước *outlier năm*, **không** đo độ bền trước *chế độ lãi suất* — với HIGH n_loo=4 nhưng
chỉ đến từ 2 chu kỳ, LOO ở đây yếu hơn vẻ ngoài của nó.

---

## 6. Ngân hàng: hai kết quả trái chiều cần phân biệt

Prompt trích finding #5 (ma trận 08-22): "bank excess lịch sử trong bucket 6,5–8% = **+1,0pp/năm**"
vs FPT +20,3pp. Đo ở đây cho **bank_ex trong ALL/HIGH = +8,45pp**. **Hai số này không mâu thuẫn —
chúng đo hai vật khác nhau:**

- finding #5 đo **cổ phiếu ngân hàng nói chung** (ACB/MBB/HDB Alpha-Lens) trong bucket.
- A1 đo **nhánh ngân hàng CỦA RỔ YIELDCOMBO** — tức những ngân hàng đã qua bộ lọc 8L + rẻ theo
  1/PE+1/PCF tại thời điểm rebal. Đó là một lát cắt *đã chọn lọc*, không phải sector.

Hàm ý: cơ chế "NIM co khi lãi suất huy động tăng" là **lý do đúng để lo về sector**, nhưng dữ liệu
KHÔNG cho thấy nhánh ngân hàng của rổ bị nó đánh sập trong HIGH — cái sập trong HIGH là **nhánh
NON-bank** (nonbank_ex −3,83pp toàn kỳ HIGH, −4,72pp trong NEUTRAL/HIGH; CAGR tuyệt đối −7,83%).
Đây là kết quả **ngược chiều với giả thuyết ban đầu của dispatch**, và là lý do chính khiến cap
ngân hàng đắt trong HIGH: nó chuyển tiền từ nhánh khoẻ hơn sang nhánh yếu hơn.

---

## 7. Kết luận + hàm ý

1. **+7,4pp KHÔNG còn đứng trong bucket hiện tại.** Trong NEUTRAL/HIGH rổ parking chạy −0,7%/năm
   (CI[−22,3;+22,7]) so với tiền nhàn rỗi 0% — hoà vốn, không có edge đo được. Edge parking đo
   được nằm ở MID (+21,2%, CI dương) và LOW (+51,6%, CI dương).
2. **Nhưng đây là HEDGE-shaped, không phải tín hiệu tắt parking.** Cận trên CI trong HIGH là
   +22,7%; trung vị −0,7% ⇒ chi phí kỳ vọng của việc *giữ* parking trong HIGH gần bằng 0, còn chi
   phí của việc *tắt nhầm* là mất toàn bộ đuôi phải. Với N=3 chu kỳ HIGH, khuyến nghị **KHÔNG đổi
   `ETF_PARK`**; đây là thông tin để định cỡ kỳ vọng, không phải để re-tune.
3. **Sector-cap ngân hàng ~miễn phí trung bình (±1pp), đắt −3,0pp riêng trong HIGH**, và toàn bộ
   chi phí đó đến từ 1 episode. Nhưng **mẫu lịch sử gần như không kiểm tra được cấu hình 78% hôm
   nay** — chỉ ~3 năm cuối có bank_w >65%. Đây là lý do KHÔNG nên kết luận "cap an toàn" từ dòng
   ALL/*.
4. **Rủi ro thật của rổ hiện tại không phải "ngân hàng đắt trong HIGH" mà là tập trung đơn khối:**
   78% một sector ⇒ rổ 30 mã có N hiệu dụng gần với ~5–8 vị thế độc lập. Đó là câu hỏi phương sai,
   trả lời được bằng dữ liệu; còn "ngân hàng có underperform trong HIGH không" thì dữ liệu nói
   **không** (bank_ex +8,45pp).

**Không đề xuất thay đổi production nào từ A1.** Mọi thay đổi rổ/cap phải qua quant-skeptic
CONFIRMED trước khi wire (§18 coding_guidelines).

**Artifacts:** `a1_daily.csv` (2.961 phiên × 5 chuỗi return + bucket + state) · `a1_bucket_table.csv`
· `a1_vs_cash.csv` · `a1_episodes.csv` · `a1_loo.csv` · `a1_peryear.csv` · `a1.log` ·
script `strategy_regime_matrix_20260822_a1.py` + `_a1b.py`.
