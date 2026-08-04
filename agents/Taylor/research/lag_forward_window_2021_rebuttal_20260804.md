# Phản biện "2021 là năm sóng F0 nên không dùng để đánh giá xếp hạng chất lượng"

**Job** `Taylor_20260804_061252` · Taylor · 2026-08-04
**Đối tượng**: kết luận NO-GO của job `Taylor_20260804_051145`
(`research/lag_forward_window_ranking_20260804.md`)
**Trạng thái: KHÔNG WIRE. Verdict NO-GO GIỮ NGUYÊN — nhưng LÝ DO thay đổi, và 2 chỗ trong report gốc
phải ĐÍNH CHÍNH.**
Không sửa file production nào; không chạy lại engine (đọc lại 24 CSV audit đã đóng băng của job trước).
Toàn bộ script mới ở `mike/agents/Taylor/exp_lagrank_2021_20260804/`.

---

## 0. Ba câu trả lời 1 dòng

1. **Tiền đề của user về 2021: ĐÚNG, và đúng một cách áp đảo.** 2021 là năm bất thường nhất trong
   13 năm mẫu trên MỌI thước đo "melt-up bừa bãi" — breadth 87,8%, thanh khoản **+296% YoY**,
   92,0% mã tăng, trung bình +126%, và **chất lượng bị TRỪNG PHẠT** (IC(ROE_Min3Y, return) = **−0,39**,
   nhóm PE rẻ thua nhóm PE đắt **−39,0pp**). Điểm tổng hợp z = **+2,08**, năm nhì (2014) chỉ +0,87.
2. **Suy luận "nên 2021 làm lệch phép thử xếp hạng": KHÔNG ĐƯỢC DỮ LIỆU ỦNG HỘ.** Chính trong 2021,
   khoá xếp hạng chạy **TỐT HƠN trung bình**: rank-IC của `surprise_B_MA` = **+0,181 (cao thứ 2 / 13
   năm)**, decile cao nhất vượt trung bình rổ **+5,67pp**. Và **cùng năm đó, cùng khoá đó, ở NAV 50B
   luật xếp hạng THẮNG FIFO +10…+34pp** trên sổ LAG (z = +1,25…+3,17), trong khi ở 1B thua −6,7…−18,9pp
   (z = −1,41…−2,89). Một chế độ thị trường vô hiệu hoá xếp hạng chất lượng **không thể** vừa giúp ở
   quy mô này vừa hại ở quy mô kia. 2021 là **ngoại lai PHƯƠNG SAI**, không phải **thiên lệch** chống
   lại xếp hạng chất lượng.
3. **Xử lý 2021 đúng cách rồi thì sao?** Cổng LOO (trước đây 0/10 sống sót) **chuyển thành 9/10 ROBUST**
   — đây là thay đổi thật, đáng ghi nhận. Nhưng **2 cổng quyết định vẫn thất bại rõ**: t tốt nhất
   0,88 → **1,50** (cần 2), DSR tốt nhất 0,51 → **0,71** (cổng 0,95). Và khi đếm **đúng** bậc tự do
   mới (chọn năm nào để loại là 1 phép tìm nữa: N_trials 10 → 130), **DSR tụt xuống 0,42–0,48 — THẤP
   HƠN cả bản có 2021**. Loại 2021 **không** cứu được cổng quyết định.

---

## 1. Câu hỏi 1 — 2021 có thật sự bất thường? **CÓ, và duy nhất trong mẫu**

`dispersion_by_year.py` — hai tầng đo độc lập, mọi số tính tại chỗ từ dữ liệu thô
(cache ghim `data/bq_cache_asof20260729_postrestate`, universe thanh khoản `Volume_3M_P50 ≥ 20k`).

### 1.1 Tầng thị trường — 3/3 dấu hiệu F0 đều cực đoan

| năm | breadth >MA200 (%) | % mã tăng | TB return (%) | σ chéo (%) | **turnover (nghìn tỷ)** | IC(ROE_Min,ret) | PE rẻ − PE đắt (pp) |
|---|---|---|---|---|---|---|---|
| 2014 | 79,1 | 84,4 | +41,3 | 62,0 | 565 | −0,17 | −11,6 |
| 2017 | 58,8 | 70,9 | +37,9 | 72,7 | 876 | −0,04 | −32,2 |
| 2020 | 52,9 | 85,2 | +59,3 | 79,3 | 1.550 | −0,06 | +28,0 |
| **2021** | **87,8** | **92,0** | **+126,1** | **145,0** | **6.141 (+296%)** | **−0,39** | **−39,0** |
| 2022 | 32,0 | 7,2 | −48,3 | 28,2 | 4.629 | +0,36 | −1,9 |
| 2023 | 52,2 | 73,9 | +27,3 | 41,9 | 4.085 | +0,10 | +0,7 |
| 2025 | 53,2 | 54,5 | +19,7 | 75,1 | 7.046 | −0,14 | −2,9 |

*(bảng đầy đủ 13 năm: `tier2_market_by_year.csv`)*

2021 đứng **nhất tuyệt đối** ở breadth, % mã tăng, return trung bình, σ chéo, cú nhảy thanh khoản, và
**âm nhất** ở IC chất lượng. Cú nhảy turnover 1.550 → 6.141 nghìn tỷ (**+296%**) là cú nhảy thanh
khoản lớn nhất trong 13 năm — chính là dấu vân tay F0 mà user mô tả. **Tiền đề của user: CONFIRMED.**

### 1.2 Tầng tín hiệu — nhưng khoá xếp hạng KHÔNG bị vô hiệu hoá trong 2021

Đây là chỗ lập luận rẽ hướng. Đo trên **đúng rổ ứng viên mà luật xếp hạng sắp lại** (5.389 sự kiện
qua cổng LAG `NP_R≥15 ∧ prior_n_good≥4 ∧ pa_HL3≥5 ∧ forensic`), so `post_ret` = drift thực T+5→T+30
(chính là cửa sổ sổ LAG kiếm tiền — `analyze_earnings_reaction.py:131`):

| năm | N sự kiện | σ(post_ret) | IQR | **IC surprise** | IC blend | spread T3−T1 (pp) | **D10 − TB rổ (pp)** |
|---|---|---|---|---|---|---|---|
| 2019 | 304 | 13,8 | 11,5 | +0,077 | +0,128 | −0,2 | −0,2 |
| 2020 | 307 | 23,7 | 19,1 | −0,035 | −0,017 | −1,4 | +7,0 |
| **2021** | **581** | **20,3** | **23,3** | **+0,181** | **+0,146** | **+7,0** | **+5,7** |
| 2022 | 650 | 15,7 | 16,8 | +0,192 | +0,162 | +7,3 | +6,5 |
| 2024 | 563 | 13,6 | 9,8 | +0,016 | −0,140* | −0,0 | −1,8 |
| 2025 | 643 | 13,0 | 12,8 | +0,005 | +0,039 | −0,2 | +0,5 |

*(`tier1_lagpool_by_year.csv`, `decile_by_year.csv`; *ô 2024 là IC của `d_NPR`)*

- **IC surprise 2021 = +0,181 → cao thứ 2 trong 13 năm** (chỉ sau 2022 +0,192).
- **IQR của post_ret 2021 = 23,3pp → CAO NHẤT mẫu.** Độ phân tán **không** bị nén — nó **giãn ra**.
- **Decile cao nhất (D10, chính là phần được cấp vốn trước khi thiếu tiền) vượt trung bình rổ +5,67pp**
  — hạng 4/12 năm. Không có dấu hiệu "đầu bảng hỏng".

→ Cơ chế user đề xuất ("tín hiệu chất lượng nào cũng thua trong năm đầu cơ") **không xảy ra với
những khoá thực sự dùng trong nghiên cứu**. Lý do rất thẳng: các khoá đó là **cường độ PEAD**
(earnings-surprise, gia tốc lợi nhuận), **không phải** trục chất lượng/định giá. Đúng là trục
chất lượng/giá trị bị trừng phạt nặng trong 2021 (IC_ROE −0,39, rẻ−đắt −39pp) — nhưng đó là **trục
KHÁC**, không có mặt trong nghiên cứu này.

---

## 2. Câu hỏi 2 — 2 năm nào bị LOO loại? **2026 + 2023, KHÔNG phải 2021**

Chạy lại `loo_lagrank.py` nguyên bản của job trước (B_surprise_w5, NAV 1B, OOS 2020+):

| Bỏ năm | Δ vs FIFO |
|---|---|
| (không bỏ) | +1,81pp |
| **bỏ 2021** | **+3,07pp** ← cải thiện MẠNH NHẤT trong 7 năm |
| bỏ 2022 | +2,44pp |
| bỏ 2025 | +2,11pp |
| bỏ 2020 | +1,56pp |
| bỏ 2024 | +1,45pp |
| bỏ 2023 | +1,02pp |
| bỏ 2026 | +1,01pp |
| **bỏ 2026 + 2023** | **−0,06pp** ← "bỏ 2 năm" của report gốc |

**Xác nhận: 2021 KHÔNG nằm trong 2 năm bị loại.** Phép LOO bỏ 2 năm **gánh nhiều edge nhất**
(2026+2023); 2021 nằm ở đầu ngược lại — nó **kéo edge xuống**, đúng như user nghi. Report gốc **không
sai** khi ghi "−0,06pp khi bỏ 2 năm", nhưng câu đó dễ bị đọc thành "2021 gánh edge", nên cần nói rõ.

---

## 3. Câu hỏi 4 (phần chính) — Loại 2021 thì mọi cổng ra sao? **CẢ HAI BẢN, không chọn bản đẹp**

`gates_ex2021.py` — công thức y hệt job gốc để so trực tiếp được.

### 3.1 NAV 1B (chế độ ràng buộc vốn — quy mô SpaceX/ZaloPay)

| Biến thể | ΔCAGR có 2021 | **ΔCAGR ex-2021** | t có | **t ex** | DSR có | **DSR ex** |
|---|---|---|---|---|---|---|
| B_pahl3_w5 | +0,69% | +1,31% | 0,83 | **1,50** | 0,49 | **0,71** |
| B_surprise_w5 | +0,79% | **+1,28%** | 0,88 | 1,36 | 0,51 | 0,66 |
| A_blend_w0 | +0,52% | +0,95% | 0,78 | 1,37 | 0,47 | 0,67 |
| A_surprise_w0 | +0,57% | +0,92% | 0,72 | 1,10 | 0,45 | 0,56 |
| B_blend_w5 | +0,36% | +0,91% | 0,41 | 0,98 | 0,33 | 0,52 |
| A_fill_w0 | +0,27% | +0,77% | 0,39 | 1,06 | 0,32 | 0,55 |
| A_dnpr_w0 | +0,28% | +0,50% | 0,45 | 0,76 | 0,35 | 0,43 |
| A_pahl3_w0 | −0,26% | +0,10% | −0,44 | 0,16 | 0,10 | 0,22 |
| B_fill_w5 | −0,21% | +0,29% | −0,24 | 0,31 | 0,14 | 0,27 |
| B_dnpr_w5 | −0,47% | −0,29% | −0,55 | −0,31 | 0,08 | 0,11 |
| | 6/10 dương | **9/10 dương** | max 0,88 | **max 1,50** | max 0,51 | **max 0,71** |

**PBO (CSCV, S=16, họ đủ 11 cấu hình): 0,4749 → 0,4134** (đạt cả hai bản).
**LOO bỏ-2-năm: 0/10 sống sót → 9/10 ROBUST** (chỉ `B_dnpr_w5` vẫn LUMPY).

### 3.2 NAV 50B (chân đối chứng) — loại 2021 làm **XẤU ĐI**, không tốt lên

| Biến thể | ΔCAGR có 2021 | **ΔCAGR ex-2021** | t có | **t ex** |
|---|---|---|---|---|
| A_fill_w0 | −0,93% | −1,27% | −1,46 | **−2,06** |
| A_surprise_w0 | −0,94% | −1,41% | −1,33 | **−2,00** |
| A_pahl3_w0 | −0,30% | −1,15% | −0,46 | −1,92 |
| B_blend_w5 | −0,52% | −1,39% | −0,52 | −1,37 |
| B_surprise_w5 | −0,91% | −1,36% | −0,87 | −1,27 |
| | 1/10 dương | **0/10 dương** | — | 2 chân **ÂM có ý nghĩa** |

LOO ở 50B: **10/10 vẫn LUMPY** cả hai bản. LAG-sleeve mean delta: −0,48pp → **−2,09pp**,
số chân có mean dương **5/10 → 0/10**.

**Đây là điểm chí tử:** ở 50B, loại 2021 không chỉ không cứu — nó đẩy 2 biến thể tới **t ≈ −2,0**,
tức "luật xếp hạng làm HẠI có ý nghĩa thống kê". Nếu 2021 bị coi là năm phải loại vì lý do chế độ
thị trường, thì phải loại ở **cả hai** quy mô, và khi đó chân 50B nói NO-GO còn to hơn trước.

### 3.3 Placebo — bỏ MỘT năm nào cũng làm t tăng, đó là số học của việc xoá 8% mẫu xấu nhất

`why2021.py` phần (1). t của chuỗi hiệu sau khi bỏ **từng** năm (NAV 1B):

| Biến thể | t(đủ) | 2014 | 2016 | 2018 | 2020 | **2021** | 2022 | 2024 | 2026 | dải |
|---|---|---|---|---|---|---|---|---|---|---|
| B_surprise_w5 | 0,88 | 1,05 | 1,17 | 1,05 | 0,67 | **1,36** | 0,96 | 0,63 | 0,48 | 0,47–1,36 |
| A_blend_w0 | 0,78 | −0,07 | 0,95 | 0,72 | 0,60 | **1,37** | 1,03 | 0,68 | 0,74 | −0,07–1,37 |
| B_pahl3_w5 | 0,83 | 0,56 | 1,24 | 0,40 | 0,69 | **1,50** | 0,77 | 0,84 | 0,77 | 0,19–1,50 |

2021 **đúng là** năm cho t cao nhất (nhất quán với §1: nó là năm ngoại lai thật). Nhưng **cả dải
0,47–1,50 nằm dưới 2** — nên **không phép loại-một-năm nào** đưa được cổng t qua ngưỡng. Kết luận
"không phân biệt được với 0" là **bất biến với việc chọn năm loại**, không phải hệ quả của việc để
2021 trong mẫu.

### 3.4 Loại 1 năm là 1 BẬC TỰ DO MỚI — và nó phải trả giá trong DSR

Chọn "loại 2021" là chọn 1 trong 13 năm khả dĩ **sau khi đã thấy kết quả**. Kỷ luật
multiple-testing (KB §5) buộc đưa phép tìm đó vào `N_trials`:

| N_trials | SR_0 | DSR B_pahl3_w5 | DSR B_surprise_w5 | DSR A_blend_w0 |
|---|---|---|---|---|
| 10 (họ gốc, ex-2021) | 0,01752 | 0,714 | 0,664 | 0,668 |
| 13 (chỉ đếm phép chọn năm) | 0,01895 | 0,687 | 0,636 | 0,639 |
| 26 | 0,02240 | 0,619 | 0,565 | 0,568 |
| **130 = 10 cấu hình × 13 năm** | **0,02916** | **0,476** | **0,423** | **0,423** |

**Ở không gian tìm kiếm trung thực (N=130), DSR ex-2021 = 0,42–0,48 — THẤP HƠN cả bản có 2021
(0,51).** Nói cách khác: sau khi trả đúng phí cho bậc tự do vừa dùng, việc loại 2021 **không mua
được gì cả**.

---

## 4. Câu hỏi 3 — Có năm nào khác giống 2021? **KHÔNG, 2021 đứng một mình**

Điểm tổng hợp melt-up = trung bình 6 z-score (breadth, % mã tăng, return TB, nhảy turnover, và
IC chất lượng + rẻ−đắt đảo dấu) — `meltup_markers_by_year.csv`:

| năm | 2021 | 2014 | 2017 | 2020 | 2025 | 2023 | 2019 | 2016 | 2015 | 2024 | 2018 | 2022 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **z** | **+2,08** | +0,87 | +0,52 | +0,18 | +0,06 | −0,10 | −0,19 | −0,47 | −0,50 | −0,52 | −0,52 | −1,26 |

2021 là **năm duy nhất trên +1**, và cao **2,4×** năm nhì. Về mặt "1 ngoại lệ hay 1 pattern lặp",
dữ liệu ủng hộ **1 ngoại lệ** → phần lập luận này của user **vững**.

⚠️ **Giới hạn phải nói rõ**: mẫu là 2014–2026 (13 năm). 2007 — năm mà user gợi ý có thể tương tự
(trước sập 2008) — **không nằm trong mẫu và không mở rộng vào được**: engine warm-up từ 2014, và
`CLAUDE.md` ghi rõ thị trường VN trước 2008 quá mỏng (2007 ≈ 74 mã) nên breadth/universe signal
không có nghĩa. Nên câu "2021 là duy nhất" đúng **trong 2014-2026**, không phải trong toàn lịch sử VN.

---

## 5. ĐÍNH CHÍNH report gốc — 2 chỗ

### 5.1 §3 report gốc quy sai nguyên nhân của 2021

Report gốc viết: *"Nguyên nhân là **chất lượng lựa chọn**: trong năm bull mạnh nhất mẫu, đúng những
tên bị các khoá này xếp hạng thấp lại là những tên chạy tốt."* — **Dữ liệu sự kiện BÁC BỎ câu này.**
Trong 2021, tên bị xếp hạng CAO chạy **tốt hơn** tên xếp hạng thấp: spread T3−T1 = **+7,0pp**,
D10 vượt trung bình rổ **+5,7pp**, IC = **+0,181** (cao thứ 2 mẫu).

Cách đọc đúng — bằng chứng cơ chế (`noise_band.py`, `why2021.py` phần 2):

| Bằng chứng | 2021 @ NAV 1B | 2021 @ NAV 50B |
|---|---|---|
| Δ sổ LAG vs FIFO, 10 biến thể | **−6,7 … −18,9pp** (10/10 âm) | **+10,3 … +33,8pp** (10/10 dương) |
| z(2021) trong 13 Δ hàng năm | **−1,41 … −2,89** | **+1,25 … +3,17** |
| % tiền mặt nhàn rỗi của sổ LAG | 49,2 (FIFO) vs 49,3 / 49,7 | 48,9 vs 48,7 / 49,9 |
| `nav_bal_ref` (sổ BAL) | **giống hệt mọi chân** | giống hệt |

Ba điều này khoá chặt chẩn đoán:
- **Không phải kênh tiền nhàn rỗi** — tỉ lệ tiền mặt lệch < 0,5pp.
- **Không phải sổ BAL** — sổ BAL bit-identical, toàn bộ chênh lệch nằm trong sổ LAG.
- **Không phải "khoá xếp hạng chọn sai trong bull"** — cùng khoá, cùng năm, cùng rổ tín hiệu, ở 50B
  nó **thắng đậm**. Cái đổi duy nhất là **có bao nhiêu ứng viên được cấp vốn** (1B nuôi ~56/581 = 10%
  rổ; 50B nuôi ~105/581 = 18%).

Kết luận cơ chế đúng: **2021 là năm σ chéo lớn nhất mẫu (σ 145%, IQR 133pp)** → trong một sổ nhỏ
(1B, ~12 slot) việc đảo thứ tự vài tên tạo ra chênh lệch hàng chục pp **thuần do phương sai**, hai
chiều. Ở 1B nó rơi về phía âm; ở 50B (sổ rộng hơn, luật trung bình bắt đầu có hiệu lực) nó rơi về
phía dương. Đó là **noise được phóng đại**, không phải **bias chống lại xếp hạng chất lượng**.

### 5.2 Bảng cổng §5.1 report gốc: LOO nên đọc lại

Cổng "LOO bỏ-2-năm giữ dấu dương" ❌ trong report gốc **chủ yếu là hiện vật 2021**: loại 2021 thì
9/10 chân ROBUST. Bảng cổng đúng cho NAV 1B nên là:

| Cổng | Ngưỡng | có 2021 | **ex-2021** |
|---|---|---|---|
| t-stat phần tăng thêm | ~2 | 0,88 ❌ | **1,50 ❌** |
| DSR (N_trials=10) | ≥0,95 | 0,51 ❌ | 0,71 ❌ |
| **DSR (N=130, đếm cả phép loại năm)** | ≥0,95 | 0,51 ❌ | **0,42–0,48 ❌ (xấu hơn)** |
| PBO | <0,5 | 0,475 ✅ | **0,413 ✅** |
| LOO bỏ-2-năm | >0 | −0,06 ❌ | **+0,00…+1,42 ✅ (9/10)** |
| Calmar > FIFO | >1,46 | 1,46 (bằng) ❌ | không tính lại được sạch trên mẫu khuyết năm |
| MaxDD không xấu đi | ≤−17,7% | −18,4% ❌ | như trên |
| Không mất độ rộng PEAD | ~0% | `w5` −16…−20% ❌ / `w0` ✅ | không đổi (không phụ thuộc năm) |

**1/7 → 2/7 cổng đạt** (PBO + LOO). Vẫn không có cổng quyết định nào đi qua.

---

## 6. KẾT LUẬN LẠI

**Verdict: NO-GO — GIỮ NGUYÊN.** Không phải vì bỏ qua phản biện của user, mà vì đã kiểm và dữ liệu
trả lời rõ:

1. **User đúng về 2021** (năm F0 bất thường, duy nhất trong mẫu) — CONFIRMED bằng 6 thước đo độc lập.
2. **User không đúng ở bước suy luận** rằng điều đó làm lệch phép thử: khoá xếp hạng **hoạt động tốt
   hơn bình thường** trong 2021 ở tầng tín hiệu (IC +0,181, hạng 2/13), và **thắng +15pp ở NAV 50B**
   cùng năm. Hại chỉ xảy ra ở 1B — đó là chữ ký của **phương sai sổ nhỏ trong năm σ chéo cao nhất
   mẫu**, không phải chữ ký của "tín hiệu chất lượng bị vô hiệu hoá".
3. **Ngay cả khi CHẤP NHẬN loại 2021 như regime outlier biết trước** (giả định có lợi nhất cho ý
   tưởng): t max 1,50 < 2; DSR max 0,71 < 0,95; và sau khi trả phí bậc tự do (N=130) DSR còn
   **0,42–0,48, thấp hơn bản có 2021**. Placebo cho thấy **không** phép loại-một-năm nào đưa t lên 2
   (dải 0,47–1,50). Ở 50B, loại 2021 đẩy 2 chân xuống **t ≈ −2,0 (hại có ý nghĩa)**.
4. **Điều kiện mở lại verdict — nói trước, để không phải tranh luận sau**: cần **t ≥ 2 và DSR ≥ 0,95
   trên phần tăng thêm, tại N_trials đã đếm đủ mọi phép tìm** (kể cả chọn cửa sổ mẫu). Với IR ~0,25
   quan sát được, mẫu 12,5 năm **về mặt số học không thể** đạt mức đó — cần ~60 năm. **Không có vòng
   backtest nào trên cùng mẫu 2014-2026 cứu được**; thêm biến thể chỉ làm N_trials tăng và DSR xấu đi.

**Điều ĐÁNG làm tiếp không đổi so với report gốc (§5.2 mục A): đo ca thật trước.** Ràng buộc thật của
SpaceX/ZaloPay là **tiền kẹt trong vị thế đang nắm, không có lệnh bán** (3+ tuần HOLD ALL) — khác
ràng buộc cơ cấu mà 1B mô phỏng. Đếm xem trong các đợt HOLD ALL đó **thực tế bỏ lỡ bao nhiêu ứng
viên LAG và chúng diễn biến ra sao**. Rẻ hơn một vòng backtest nữa, và trả lời đúng câu hỏi gốc.

**Một ghi nhận sòng phẳng cho ý tưởng, sau phản biện này nó MẠNH HƠN trước:** ở NAV 1B, mean Δ sổ LAG
qua 13 năm là **+1,53pp/năm khi loại 2021** (9/10 chân dương) so với +0,37pp khi có 2021, và PBO đạt
cổng ở cả hai bản. Cơ chế **có** dịch đúng chiều. Vấn đề duy nhất — và là vấn đề không giải được bằng
thêm backtest — là **độ lớn quá nhỏ so với nhiễu trên mẫu có sẵn**.

---

## 7. Tái lập

```bash
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
E=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_lagrank_2021_20260804
cd $E
$DNA_PYEXE $E/dispersion_by_year.py       # tier1/tier2 theo năm  -> tier1_*.csv tier2_*.csv
$DNA_PYEXE $E/decile_and_analogues.py     # decile + điểm melt-up -> decile_by_year.csv meltup_markers_by_year.csv
$DNA_PYEXE $E/gates_ex2021.py 1B          # mọi cổng, 2 bản       -> gates_ex2021_1B.csv
$DNA_PYEXE $E/gates_ex2021.py 50B         #                       -> gates_ex2021_50B.csv
$DNA_PYEXE $E/why2021.py                  # placebo + cơ chế
$DNA_PYEXE $E/noise_band.py               # Δ sổ LAG theo năm + z(2021)
```

Đầu vào: **24 CSV audit đã đóng băng** của job `Taylor_20260804_051145` trong `data/` (không chạy lại
engine, không sinh CSV mới trong `data/`), `data/earnings_surprise_data.pkl`,
`data/earnings_events_classified.csv`, `data/forensic_flags.csv`, cache ghim
`data/bq_cache_asof20260729_postrestate`. Interpreter `$DNA_PYEXE` (pandas 3).
DSR/PBO **import nguyên bản** từ `dsr_pbo_annex.py`, không tự dựng lại công thức.

**Đã thử và LOẠI BỎ (ghi lại để không ai lặp):**
- Bootstrap "cohort ngẫu nhiên" để dựng dải nhiễu tổng hợp: cần số vị thế đồng thời của sổ LAG, ước
  từ TX ra **1–3 tên** (bất hợp lý cho sổ chạy 56–77 lệnh vào/năm) → phép nhân dồn nổ thành hàng
  nghìn %. Thay bằng **σ chéo-năm của chính Δ sổ LAG** (§5.1) — ít giả định hơn, mọi đầu vào là output
  engine đã audit. Code còn trong `noise_band.py` phần docstring để khỏi ai dựng lại.
- Đo "độ trễ khớp lệnh" từ `holding_id`: ngày trong `holding_id` **là ngày khớp**, không phải ngày tín
  hiệu → cột `delay` ra 0 ở mọi chân, vô dụng. Không có trường ngày-tín-hiệu trong CSV audit.
