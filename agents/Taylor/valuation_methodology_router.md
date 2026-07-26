# Khung phương pháp luận định giá theo TIER / NGÀNH — router cho full-report cổ phiếu đơn lẻ

> **Tác giả:** Taylor (Quant) · **Job:** `Taylor_20260721_104423` · **Ngày:** 2026-07-21
> **Đối tượng đọc:** Mike, trước MỖI lần làm full-report một ticker (quy ước "gõ mã 3 ký tự = full
> report" — thread Discord `1521013312681414728`: định giá + dự báo quý + DCF + nhận định).
>
> **STATUS: GUIDANCE THAM KHẢO — KHÔNG phải công thức cứng, KHÔNG tự động hoá, KHÔNG chạm production.**
> Không có dòng nào ở đây được wire vào `custom30V` / `BAL` / `LAG` / `rating_8l.py` / `trading_rules.json`.
> Mục tiêu là **chặn các lỗi phương pháp lặp lại**, không phải thay thế domain judgment từng case.
> Mọi con số dưới đây đều đo được từ BQ cache và có lệnh tái lập ở §7.

---

## 0. Cách dùng file này (đọc 30 giây trước mỗi report)

Đây là một **router**, không phải sách giáo khoa. Đội đã có **18 framework ngành chi tiết** trong
`mike/agents/Taylor/*_valuation_framework.md`. File này trả lời câu hỏi đứng TRƯỚC chúng:
*"ticker này thuộc tier nào, ngành nào → mở framework nào, dùng phương pháp gì, WACC bao nhiêu, và
tôi có được phép tin DCF của nó không?"*

Trình tự bắt buộc, 4 bước:

```
B1. Phân tier (§1)      → mcap, thanh khoản → range beta/WACC hợp lý
B2. Test lõi sạch (§2)  → CF_OA vs NP dạng TTM, so với base rate NGÀNH → có được tin DCF không
B3. Chọn phương pháp (§3) → ICB_Code → phương pháp chính + framework ngành để mở
B4. Checklist WACC (§4) → 6 câu hỏi, đặc biệt câu double-count
```

Nếu B2 fail → **KHÔNG được trình bày DCF như con số neo chính** trong report; hạ nó xuống mức tham
khảo và nói rõ lý do. Đây là thay đổi hành vi quan trọng nhất của tài liệu này.

---

## 1. Việc 1a — Phân tier theo vốn hoá / thanh khoản → beta & WACC

### 1.1 ⚠️ BẪY DỮ LIỆU QUAN TRỌNG NHẤT: `risk_rating.Beta` KHÔNG phải beta

**Đừng bao giờ cắm `risk_rating.Beta` (hoặc cột `Risk_Rating.Beta` mirror trong `ticker_1m`) thẳng
vào công thức CAPM.** Nó là **bin thứ hạng 1–5**, không phải hệ số hồi quy.

Bằng chứng đo được (snapshot 2026-07-20, n=394 mã có cả 2 giá trị): FPT có `Beta=2.0`, HPG `Beta=4.0`,
VNM `Beta=1.0` — đây là giá trị nguyên, rời rạc. Nếu ai đó đọc "FPT beta = 2.0" và cắm vào CAPM thì
sẽ ra WACC khổng lồ và fair value bằng một nửa sự thật.

**Bảng quy đổi bin → beta thật** (beta hồi quy tuần, cửa sổ 5 năm, vs VNINDEX; Spearman(bin, beta
thật) = **0.878**, khớp với kết quả `beta_reverse_engineer_results.csv` là `risk_rating` ranks giống
framework weekly-5y nhất, mean spearman 0.835):

| `risk_rating.Beta` bin | n | **beta thật (trung vị)** | đọc là |
|---|---|---|---|
| 1 | 58 | **0.43** | phòng thủ mạnh |
| 2 | 89 | **0.74** | phòng thủ |
| 3 | 86 | **1.01** | theo thị trường |
| 4 | 81 | **1.23** | chu kỳ / nhạy |
| 5 | 80 | **1.51** | đầu cơ / đòn bẩy cao |

Dùng bảng này khi cần beta nhanh mà không muốn chạy hồi quy. Khi con số quan trọng (report chính
thức) → **tra bảng beta thật ở §1.1b** (đã tính sẵn cho toàn bộ mã), không cần chạy tay.

**Sai số nếu dùng bin làm proxy** (đo trên 402 mã, quý 2026Q3) — biết trước để không dùng bừa:

| bin | MAE | p90 | % mã lệch > 0.30 beta |
|---|---|---|---|
| 1 | 0.141 | 0.335 | 14% |
| **2** | **0.200** | **0.449** | **21%** ← lệch nhiều nhất, đừng dùng |
| 3 | 0.170 | 0.382 | 18% |
| 4 | 0.128 | 0.301 | 11% ← chặt nhất |
| 5 | 0.175 | 0.349 | 16% |

⇒ **Bin 2 là bin tệ nhất để thay thế tạm** (IQR rộng nhất, 1/5 số mã lệch >0.30). Bin 1 và 4 tạm
chấp nhận được. Nhưng khi đã có §1.1b thì không có lý do gì dùng bin nữa.

### 1.1b Bảng beta thật toàn bộ mã — `data_beta_universe.csv` (dùng cái này)

Script `mike/agents/Taylor/beta_universe.py` → **`mike/agents/Taylor/data_beta_universe.csv`**
(1.288 mã, chạy lại bất cứ lúc nào, ~1 phút). Tra thẳng file, không tính tay từng case.

| Cột | Ý nghĩa |
|---|---|
| `beta_5y` / `r2_5y` / `t_5y` | **beta chính** — hồi quy tuần, 260 tuần, vs VNINDEX + độ tin cậy |
| `beta_3y` | cửa sổ 156 tuần — so với `beta_5y` để xem beta có ổn định không |
| `status` | `OK` / `LOW_CONFIDENCE_ILLIQUID` / `INSUFFICIENT_HISTORY` |
| `adv_vnd`, `mcap_vnd`, `in_prune`, `bin` | thanh khoản, vốn hoá, có trong `ticker_prune` không, bin cũ |

**Quy tắc đọc:**
- `status=OK` (ADV ≥ 2 tỷ **và** R² ≥ 0.10) → dùng `beta_5y` thẳng. 253/1.288 mã.
- `status=LOW_CONFIDENCE_ILLIQUID` → **bỏ beta đo**, xem §1.2. Toàn thị trường có 846/1.288 mã
  R² < 0.10 — với nhóm này beta gần như vô nghĩa.
- `status=INSUFFICIENT_HISTORY` (< 104 tuần ≈ 2 năm, thường là mã mới niêm yết) → dùng **beta trung
  vị của ngành (`icb`) hoặc của tier**, **không** dùng bin `risk_rating` (bin cũng cần lịch sử).
- Beta không ổn định ở đuôi: `|beta_3y − beta_5y|` trung vị 0.185, **p90 0.523**. Khi con số quan
  trọng, xem cả 2 cột; lệch nhiều ⇒ nói rõ độ bất định trong report thay vì đưa 1 số.

**Đã kiểm chứng**: script tái tạo đúng cả 14 case tính tay ở §1.3 (median |sai lệch| 0.011,
max 0.061). Gotcha: cột `time` trong `bq_cache/ticker/*.parquet` là VARCHAR → phải `CAST(time AS DATE)`.

### 1.2 Tier theo vốn hoá & thanh khoản

`mcap = Price × OShares` (dùng **`Price`** = giá KHÔNG điều chỉnh, không phải `Close` — `Close` đã
adjust cổ tức/chia tách nên nhân với số cổ phiếu hiện tại sẽ ra vốn hoá sai). Thanh khoản dùng
`Trading_Value_1M_P50`. Snapshot 2026-07-20, 771 mã:

**⚠️ Bẫy dữ liệu thêm (phát hiện 2026-07-26, case PVT)**: `OShares` trong `ticker_financial` (BCTC
theo quý) chỉ cập nhật khi có báo cáo mới — nếu DN chia cổ tức bằng cổ phiếu/phát hành thêm GIỮA 2 kỳ
báo cáo, field này **lỗi thời** cho tới báo cáo quý kế tiếp. Ví dụ PVT: BCTC Q1/2026 (release 04/05)
ghi `OShares=469.931.235`, nhưng công ty phát hành cổ tức 10% bằng CP hoàn tất 08/06/2026 →
`OShares` thật = 516.918.938 từ 05/06/2026 trở đi. Bảng `ticker` (và `ticker_1m`, cùng schema) **cập
nhật hàng ngày**, đã bắt kịp đúng ngày 05/06 — dùng `ticker.OShares` cho vốn hoá/EPS/số cổ phiếu hiện
tại, **KHÔNG dùng `ticker_financial.OShares`** cho mục đích này (chỉ dùng field đó khi cần đúng số
cổ phiếu TẠI THỜI ĐIỂM báo cáo, ví dụ tính lại EPS lịch sử của quý đó).

| Tier | Định nghĩa | n | mcap trung vị | GTGD trung vị | **beta thật p25 / trung vị / p75** |
|---|---|---|---|---|---|
| **1 — mega-cap blue-chip** | mcap ≥ 30.000 tỷ **và** GTGD ≥ 50 tỷ/ngày | 36 | 115.500 tỷ | 188 tỷ | 0.92 / **1.06** / 1.21 |
| **2 — mid-cap** | mcap ≥ 5.000 tỷ | 125 | 11.400 tỷ | 14,4 tỷ | 0.48 / **0.92** / 1.20 |
| **3 — small-cap / kém thanh khoản** | còn lại | 610 | 594 tỷ | 0,10 tỷ | 0.29 / **0.56** / 1.01 |

**Gợi ý WACC theo tier** (cost of equity; ERP VN 6,5% và rf = lãi suất huy động 12M Big-4 theo
`deposit_rate_vn.py` — nhất quán với `dcf_valuation_framework.md`):

| Tier | beta dùng | size premium | **CoE gợi ý** | ghi chú |
|---|---|---|---|---|
| 1 | 0.9–1.1 (đo thật) | **0** | **10,5–13%** | thanh khoản cao, track record dài, không cộng thêm phí quy mô |
| 2 | 0.8–1.2 (đo thật) | +1,0–1,5pp | **12,5–15%** | |
| 3 | **đừng tin beta đo** | **+2–3pp** | **15–18%** | xem cảnh báo dưới |

> ### ⚠️ 1.2b ĐÍNH CHÍNH QUAN TRỌNG (2026-07-21): premium neo vào **THANH KHOẢN**, không phải vốn hoá
>
> Đã đo trực tiếp bằng dữ liệu VN (`size_premium_vn.py`, 31.345 quan sát tháng, 2015-02→2026-07,
> alpha = phần dư CAPM sau khi **kiểm soát beta**, universe point-in-time, walk-forward IS/OOS):
>
> - **KHÔNG có size premium ở VN.** Alpha theo ngũ phân vị vốn hoá phẳng và không đơn điệu
>   (+3,17 / +3,51 / −0,21 / +3,37 / +1,82 pp/năm). L/S nhỏ-trừ-lớn: FULL +1,35pp (t=0,23),
>   IS −0,35, OOS +2,62 — **vô nghĩa ở mọi cách chia** (tercile/quintile/decile). DSR 0,26–0,33.
> - **Cái tồn tại thật là ILLIQUIDITY premium**: trung hoà size, L/S (ADV thấp − ADV cao) =
>   **+6,55pp/năm, t=2,84, p=0,005; IS +7,95 / OOS +5,50; DSR 0,978** — thứ duy nhất vượt ngưỡng
>   DSR 0,95 của đội.
> - Bằng chứng dứt điểm: trong nửa **thanh khoản cao**, L/S nhỏ-trừ-lớn là **ÂM** nhất quán
>   (FULL −4,04 / IS −5,31 / OOS −3,10). Giữa các mã thanh khoản tốt, mã nhỏ không hề thắng mã lớn.
>
> **⇒ Thay trục premium từ vốn hoá sang ADV** (`Trading_Value_1M_P50`):
>
> | ADV (GTGD trung vị 1M) | premium cộng vào CoE |
> |---|---|
> | ≥ 50 tỷ/ngày | **0** |
> | 10–50 tỷ | **+1pp** |
> | 2–10 tỷ | **+2–3pp** |
> | < 2 tỷ | **+4–6pp** (neo vào +6,55pp đo được, làm tròn xuống cho thận trọng) |
>
> Bảng tier ở trên vẫn dùng được vì tier tương quan mạnh với thanh khoản — nhưng khi tier và ADV
> **mâu thuẫn** (mã vốn hoá lớn nhưng GTGD mỏng, hoặc small-cap giao dịch sôi động) thì **theo ADV**.
>
> Đây là input **định giá** (mức đền bù rủi ro đòi hỏi), **không phải tín hiệu giao dịch** — theo
> đúng định nghĩa nó nằm ở các mã ta không thể vào lệnh với size.
>
> 🐞 **Bẫy đã sập một lần, đừng lặp lại:** lần đo đầu tiên dùng `mcap = Close × OShares` cho ra
> "size premium +9,3pp/năm" — **giả hoàn toàn**. `Close` đã điều chỉnh cổ tức nên vốn hoá **quá khứ**
> bị chiết lùi (median mcap 2014: 324 tỷ theo `Close` vs 947 tỷ theo `Price` — thấp 2,9 lần, thu hẹp
> dần về 1,0 lần ở 2026), khiến nhóm "nhỏ nhất" thực chất bị nhồi bởi các mã **trả cổ tức cao/lâu
> năm** — một tilt value trá hình. **Luôn dùng `Price × OShares` cho vốn hoá; `Close` chỉ dùng để
> tính return.**

> ⚠️ **Beta small-cap THẤP là ảo giác thanh khoản, không phải an toàn.** Tier 3 có beta trung vị
> 0.56 — thấp hơn cả blue-chip. Nguyên nhân là giá giao dịch thưa/đứng im (stale pricing) làm hiệp
> phương sai với thị trường bị triệt tiêu, không phải vì doanh nghiệp ít rủi ro hơn Vinamilk.
> TV1 (beta đo 0.24, GTGD 0,7 tỷ/ngày) và NCT (beta 0.20, GTGD 2,3 tỷ) là ví dụ. **Với tier 3, bỏ
> qua beta đo và dùng size premium cố định +2–3pp.**

### 1.3 Ground-truth các case đã phân tích thủ công (beta thật, đo 2021-07 → 2026-07)

| Mã | tier | **beta thật** | bin | Bài học |
|---|---|---|---|---|
| **FPT** | 1 | **0.71** | 2 | **Từng dùng beta 1,00–1,15 → SAI rõ rệt.** Beta thật 0.71 → CoE ~11%, không phải 12,5–13,75%. |
| VNM | 1 | 0.46 | 1 | phòng thủ điển hình |
| VCB | 1 | 0.77 | 2 | |
| GMD | 1 | 0.72 | 3 | |
| ACB | 1 | 0.87 | 3 | |
| MBB | 1 | 1.17 | 4 | ngân hàng ≠ đồng nhất về beta |
| MWG | 1 | 1.24 | 4 | |
| HPG | 1 | 1.25 | 4 | thép = chu kỳ, beta cao đúng bản chất |
| PNJ | 2 | 0.79 | 2 | |
| DGC | 2 | 1.07 | 4 | |
| SAB | 2 | 0.43 | 1 | |
| PVT | 2 | 0.96 | 4 | |
| TV1 | 3 | 0.24 | 2 | beta ảo do kém thanh khoản — dùng size premium |
| NCT | 3 | 0.20 | – | như trên |

**Kết luận case FPT:** giả thuyết trong dispatch được xác nhận bằng số. Beta thật 0.71 (tier 1,
size premium 0) → CoE ≈ rf 6,8% + 0.71×6,5% ≈ **11,4%**, nằm đúng vùng 10–11% mà test độ nhạy đã
chỉ ra là khớp consensus sell-side (BVSC 94.500 / HSC 123.100 / DSC 135.900, TB 12m 98.717) — chứ
không phải 12,5–13,75% đã dùng ban đầu.

---

## 2. Việc 2 — Bài test "lõi sạch hay không": CF_OA vs NP (BẮT BUỘC, mọi ticker)

### 2.1 Ý tưởng

Lợi nhuận ròng (`NP`) là số kế toán dồn tích; dòng tiền kinh doanh (`CF_OA`) là tiền thật. Nếu NP
đẹp mà CF_OA không theo, phần chênh là **accrual không có tiền đứng sau** — có thể là phải thu phình,
tồn kho phình, hoặc ghi nhận doanh thu sớm. **Chạy test này TRƯỚC khi tin bất kỳ DCF nào**, không
chỉ khi có scandal.

Đơn vị đã xác minh: `CF_OA_P0`, `NP_P0` trong `ticker_financial` là **VND tuyệt đối** (không phải
tỷ lệ trên tài sản như tên gọi trong dictionary gợi ý). DGC 2026Q1: `CF_OA_P0 = -1,093e12` = −1.093
tỷ đồng, `NP_P0 = +4,088e11` = +409 tỷ — khớp chính xác ground-truth trong dispatch. ✓

### 2.2 ⚠️ ĐÍNH CHÍNH QUAN TRỌNG: phải dùng TTM, KHÔNG dùng 1 quý

Bản test 1-quý như mô tả ban đầu **có lỗi mùa vụ nghiêm trọng**. Đo trên toàn bộ 46.004 quan sát
(2014–2026):

| Quý dương lịch | n | tỷ lệ PASS (1 quý) | **tỷ lệ CF_OA ÂM** |
|---|---|---|---|
| **Q1** | 12.300 | **0.430** | **0.494** |
| Q2 | 11.096 | 0.542 | 0.378 |
| Q3 | 11.089 | 0.555 | 0.365 |
| Q4 | 11.519 | 0.570 | 0.346 |

**Gần một nửa doanh nghiệp VN có CF_OA âm ở Q1** (dồn vốn lưu động sau Tết/sau quyết toán năm) —
đây là nhịp bình thường, không phải dấu hiệu bệnh. Hệ quả cụ thể: **FPT 2026Q1 có CF_OA = −2.848 tỷ
trong khi NP = +2.487 tỷ** → test 1-quý sẽ gắn cờ FPT là "lõi bẩn", một **dương tính giả** với đúng
doanh nghiệp sạch nhất trong nhóm case.

Chuyển sang **TTM (tổng 4 quý: `CF_OA_P0..P3` vs `NP_P0..P3`)** thì mùa vụ biến mất (pass rate theo
quý: 0.485 / 0.493 / 0.491 / 0.522). → **Định nghĩa chính thức của test là bản TTM.**

Cũng cần đính chính một chi tiết ground-truth: **TV1 KHÔNG "CF_OA≥NP mọi quý"** — ở mức 1 quý TV1
chỉ pass 64% (vd 2016Q2: CF_OA −55,3 tỷ < NP +6,2 tỷ). Ở mức **TTM thì TV1 pass 80%, và 6 kỳ gần
nhất pass liên tục 6/6** — kết luận "lõi sạch" vẫn ĐÚNG, nhưng chỉ đứng vững trên nền TTM. Điều này
củng cố thêm việc phải dùng TTM.

### 2.3 ⚠️ Ngưỡng phải so theo NGÀNH, không so với 50%

Base rate TTM khác nhau rất mạnh giữa các ngành (n mã ≥ 8):

| ICB-2 | Ngành | pass rate TTM |
|---|---|---|
| 87 | Dịch vụ tài chính | **0.306** |
| 86 | Bất động sản | 0.399 |
| 45 | Bán lẻ | 0.415 |
| 85 | Bảo hiểm | 0.419 |
| 53 | Dầu khí | 0.438 |
| 13 | Hoá chất | 0.441 |
| 95 | Công nghệ | 0.461 |
| 37 | Hàng cá nhân/gia dụng (PNJ) | 0.471 |
| 35 | Thực phẩm & đồ uống | 0.497 |
| 17 | Tài nguyên cơ bản / thép | 0.499 |
| 23 | Xây dựng & VLXD | 0.514 |
| 57 | Y tế | 0.525 |
| 27 | Hạ tầng vận tải | 0.534 |
| 83 | Ngân hàng | 0.618 |
| 75 | Tiện ích | **0.649** |

BĐS pass 0.40 là **bình thường theo cấu trúc** (tiền ra trước nhiều năm, ghi nhận doanh thu khi bàn
giao) — không phải cả ngành đều gian lận. Tiện ích pass 0.65 cũng là cấu trúc (thu tiền đều, ít
vốn lưu động). **So một mã với base rate ngành của nó, không so với 50%.**

### 2.4 Quy trình test (3 bước, chạy trước mọi DCF)

1. **Tính TTM pass** cho ~12 kỳ gần nhất của mã (lệnh §7).
2. **So với base rate ngành** ở bảng §2.3.
3. **Đọc kết quả:**

| Tình huống | Kết luận | Hành động trong report |
|---|---|---|
| TTM pass gần/trên base rate ngành, kỳ gần nhất ✓ | **Lõi sạch** | DCF dùng được như neo chính |
| Pass tốt trong quá khứ nhưng **≥3 kỳ TTM gần nhất ✗ liên tiếp** | **Đang xấu đi** — cảnh báo thật | Hạ DCF xuống tham khảo; nêu rõ trong nhận định |
| Pass thấp **kinh niên nhưng đúng chuẩn ngành** | Đặc thù mô hình KD | Không gắn cờ; đổi sang phương pháp phù hợp (§3) |
| Pass thấp **và thấp hơn hẳn ngành** | **Cờ đỏ thật** | Không neo vào DCF; điều tra vốn lưu động |

**Kết quả trên các case ground-truth (TTM, 2014–2026):**

| Mã | TTM pass | 6 kỳ gần nhất | Đọc |
|---|---|---|---|
| **TV1** | **0.80** | ✓✓✓✓✓✓ | Lõi sạch — xác nhận. Cao hơn hẳn base ngành hạ tầng 0.53. |
| **FPT** | 0.68 | ✓✓✓✓✓✓ | Lõi sạch, cao hơn hẳn base ngành công nghệ 0.46. |
| **GMD** | 0.60 | ✓✗✓✓✓✓ | Ổn, trên base ngành 0.53 dù đang đầu tư lớn. |
| **DGC** | 0.60 | ✓✓**✗✗✗✗** | **Cờ đỏ đúng chuẩn "đang xấu đi": 4 kỳ TTM liên tiếp fail.** Tín hiệu mạnh hơn quan sát 1 quý ban đầu — không phải cú sốc một quý mà là xu hướng 1 năm. |
| **PNJ** | **0.18** | ✗✗✗✗✗✓ | Thấp hơn RẤT nhiều so với base ngành 0.47 → cờ đỏ thật, không chỉ là "đặc thù tồn kho vàng". Nhất quán với xử lý PNJ hiện tại (đã loại khỏi rổ CAPIT qua due-diligence gate). |

Điểm đáng chú ý: test này **phân biệt đúng cả 5 case mà không cần biết gì về scandal** — DGC và PNJ
bị gắn cờ từ số liệu dòng tiền thuần tuý, TV1/FPT/GMD sạch. Đó là lý do nó xứng đáng là bước bắt buộc.

> **Giới hạn cần thành thật:** đây là bài test **mô tả/chẩn đoán**, chưa được backtest như một tín
> hiệu dự báo lợi nhuận. Nó nói "đừng tin DCF của mã này", KHÔNG nói "bán mã này". Đừng trích dẫn
> nó như alpha đã kiểm chứng. Base rate ngành ở §2.3 dùng ICB hiện tại gán ngược cho lịch sử
> (không point-in-time) — đủ tốt để làm mốc so sánh, không đủ để làm tín hiệu giao dịch.

---

## 3. Việc 1b — Ngành (ICB) → phương pháp định giá → framework để mở

| Nhóm | ICB | **Phương pháp CHÍNH** | Tránh | Framework chi tiết |
|---|---|---|---|---|
| **(a) Ngân hàng** | 8355 | **P/B vs Gordon**: `justified_PB = (ROE5Y − g)/(COE − g)`, COE 13%, g 5% | ❌ **FCF-DCF**, `Debt_Eq`, `CF_OA`, `ROIC` | `banking_valuation_framework.md` |
| | | *Vì sao:* đòn bẩy LÀ sản phẩm, không phải cờ rủi ro; "capex/FCF" không có nghĩa với ngân hàng; phát hành khoản vay làm méo CF_OA. Chú ý: base rate CF_OA≥NP ngành NH là 0.62 nhưng **không dùng test §2 cho ngân hàng** — CF_OA của NH phản ánh tăng trưởng tín dụng, không phải chất lượng lợi nhuận. | | |
| **(b) Hạ tầng/tiện ích ĐANG mở rộng công suất** | 2777, 75xx | **Earnings-power** (LN chuẩn hoá) hoặc **EV/EBITDA**; nếu vẫn dùng DCF thì **tách capex tăng trưởng khỏi capex duy trì** | ❌ FCF-DCF thuần | `logistics_port_valuation_framework.md`, `energy_valuation_framework.md` |
| | | *Case GMD:* FCF hiện tại bị capex TĂNG TRƯỞNG (Gemalink Phase 2) đè → DCF-FCF thuần ra "định giá quá cao" −63%…−82% **sai lệch**, trong khi earnings-power ra ~58.800 (gần target CTCK +19–22%). Dấu hiệu nhận biết pha đầu tư: `CF_Invest_P0` âm lớn kéo dài + `ROIC5Y` bị nén dưới `ROIC_Trailing`. | | |
| **(c) Hạ tầng/tiện ích MATURE, hết nợ, capex ~0** | 2777, 75xx | **DDM có trọng số theo độ tin cậy quản trị** (xem §3.1) | ⚠️ full-FCF DCF nếu quản trị chưa rõ ràng | `soe_governance_framework.md` |
| | | *Case TV1:* full-FCF cho 40.000–140.000 vs DDM cổ tức thực trả 12.000–19.000. Khoảng cách này KHÔNG phải sai số mô hình — nó chính là **câu hỏi quản trị**: tiền giữ lại có thực sự về tay cổ đông không? | | |
| **(d) Hàng hoá/tồn kho biến động theo giá thị trường** | 37xx (vàng), 13xx, nông sản | **Chuẩn hoá dòng tiền qua đủ 1 chu kỳ** | ❌ TTM thô, ❌ TB 3 năm thô | `retail_valuation_framework.md`, `fertchem_rubber_valuation_framework.md` |
| | | *Case PNJ:* TTM FCF 3.685 tỷ bị thổi bởi 1 quý Tết bất thường; TB 3 năm 440 tỷ lại bị kéo xuống bởi các năm tồn kho vàng phình do giá vàng leo. **Cả hai đều sai.** Cần trải qua đủ chu kỳ giá hàng hoá, hoặc tách riêng phần lãi/lỗ tồn kho khỏi biên lợi nhuận cốt lõi. | | |
| **(e) Tech / dịch vụ dòng tiền ổn định** | 95xx | **DCF chuẩn (2-stage FCFE)** nhưng **WACC calibrate đúng tier** | ❌ WACC "một mức cho tất cả" | `dcf_valuation_framework.md`, `tech_valuation_framework.md` |
| | | *Case FPT:* xem §4.2 — lỗi ở đây không phải mô hình mà là chi phí vốn. | | |
| **(f) Commodity cyclical (thép, cao su, hoá chất)** | 17xx, 13xx | **LN/dòng tiền chuẩn hoá qua chu kỳ** (cyclically-adjusted, kiểu Graham/Shiller); P/B ở đáy chu kỳ | ❌ P/E hiện tại (bẫy: P/E thấp nhất ở ĐỈNH chu kỳ) | `steel_buildmat_valuation_framework.md`, `fertchem_rubber_valuation_framework.md` |
| | | Beta cao là ĐÚNG bản chất ở nhóm này (HPG 1.25, DGC 1.07) — đừng "sửa" xuống. | | |

**Các nhóm khác đã có framework sẵn, mở trực tiếp:** bảo hiểm (`insurance_`), chứng khoán
(`securities_`), bất động sản (`re_`), dược (`pharma_`), hàng không (`aviation_`), xây dựng
(`construction_`), viễn thông (`telecom_`), dệt may (`textile_`), F&B (`fnb_`), chăn nuôi
(`livestock_`), holdco/SOTP (`holdco_sotp_`), Viettel (`viettel_logistics_infra_`).

### 3.1 Thang trọng số DDM ↔ full-FCF cho nhóm (c)

Khoảng cách giữa hai mô hình = mức chiết khấu quản trị. Chọn điểm neo theo bằng chứng, không theo cảm tính:

| Bằng chứng quan sát được | Neo về |
|---|---|
| Lịch sử chi trả cổ tức đều ≥5 năm, payout ổn định, không pha loãng bất thường | **Gần full-FCF** (70–100%) |
| Có trả cổ tức nhưng thất thường, hoặc tiền mặt tích tụ không rõ mục đích | **Trung điểm** (40–60%) |
| Quản trị chưa rõ ràng, cổ đông nhà nước chi phối không có chính sách cổ tức công bố, tiền giữ lại không sinh lời (ROIC thấp) | **Gần DDM** (0–30%) |

TV1 rơi vào nhóm 3 → neo gần DDM (12.000–19.000), đúng như kết luận thủ công đã đưa ra.

---

## 4. Việc 3 — Checklist WACC (6 câu, trả lời TRƯỚC khi bấm số)

### 4.1 Sáu câu hỏi

1. **Tier vốn hoá?** (§1.2) → biết ngay có được cộng size premium không. Tier 1 = **0**.
2. **Beta lấy từ đâu?** — Nếu đọc từ BQ: **đó là bin 1–5, phải quy đổi qua bảng §1.1**, đừng cắm
   thẳng. Nếu là tier 3: **bỏ beta đo, dùng size premium +2–3pp** (beta thấp ở đây là ảo giác thanh khoản).
3. **rf lấy đúng as-of chưa?** — lãi suất huy động 12M Big-4 qua `deposit_rate_vn.py`, không dùng số nhớ trong đầu.
4. **Cơ cấu vốn thật của DN?** — `Debt_Eq_P0`. Nếu DN gần như không nợ (TV1) thì WACC ≈ CoE, đừng
   giả định một tỷ lệ D/E "chuẩn ngành". Nếu là ngân hàng → không dùng WACC (§3a).
5. **🔴 CÓ ĐANG DOUBLE-COUNT RỦI RO KHÔNG?** — xem §4.2. Đây là câu quan trọng nhất.
6. **Chạy độ nhạy WACC ±1pp và ĐƯA VÀO REPORT** — không trình bày fair value như một con số đơn lẻ.

### 4.2 🔴 Lỗi double-count — lỗi phổ biến nhất, và là lỗi đã mắc với FPT

**Quy tắc: một luận điểm rủi ro định tính chỉ được vào mô hình MỘT LẦN.**

Với FPT, luận điểm "AI ăn mòn moat outsourcing" đã bị đưa vào **hai chỗ cùng lúc**: vừa hạ growth
path (stage-1 g), vừa nâng beta lên 1,00–1,15 → nâng WACC lên 12,5–13,75%. Cùng một nỗi lo, bị phạt
hai lần, nhân với nhau. Kết quả: fair value base/bull 48.723–67.976 so với consensus TB 12m 98.717.

**Chọn một trong hai, không phải cả hai:**

| Nếu rủi ro là… | Đưa vào | Không đưa vào |
|---|---|---|
| **về mức/tốc độ dòng tiền** ("AI làm doanh thu outsourcing chậm lại") | **growth path** (g thấp hơn, hoặc kịch bản bear riêng) | ❌ không nâng WACC |
| **về độ bất định/phân tán của dòng tiền** ("không biết kết quả sẽ ra sao, dải rất rộng") | **WACC** (hoặc tốt hơn: kịch bản có xác suất) | ❌ không hạ luôn base-case g |

Cách xử lý sạch nhất cho rủi ro định tính: **để WACC theo tier (thị trường quyết), thể hiện luận
điểm qua các KỊCH BẢN growth có gán xác suất.** Như vậy người đọc thấy được giả định, thay vì nó bị
chôn trong một con số chiết khấu.

### 4.3 Vì sao WACC nhạy đến vậy (đo được)

Mô hình 2-stage FCFE, g=8%, g_term=3,4% — fair value tương đối (r=13,3% ≙ 100):

| WACC | 10,0% | 11,0% | 12,0% | 13,0% | **13,3%** | 13,75% |
|---|---|---|---|---|---|---|
| Fair value (chỉ số) | **151,5** | **131,1** | 115,5 | 103,2 | **100,0** | 95,5 |

**Giảm 1pp WACC → fair value tăng +12% đến +18%** (biên độ càng lớn khi r càng thấp). Hạ WACC từ
13,3% xuống 11% làm fair value tăng **+31%** — đủ để lấp gần hết khoảng cách FPT vs consensus, và
khớp chính xác với test độ nhạy thủ công (fair value nhảy lên 80.000–110.000 ở WACC 10–11%).

**Hệ quả về cách trình bày:** vì fair value nhạy như vậy, **mọi report phải kèm bảng độ nhạy WACC
±1pp**. Một con số fair value đơn lẻ tạo cảm giác chính xác giả tạo trong khi thực chất nó chỉ là
một điểm trên đường cong dốc.

---

## 5. Bảng tra nhanh — dán vào đầu mỗi report

```
Ticker: ___    ICB: ___    mcap: ___ tỷ    GTGD 1M P50: ___ tỷ

B1 TIER      → [1 mega / 2 mid / 3 small]   size premium: [0 / +1..1,5pp / +2..3pp]
   beta      → bin BQ = ___ → beta thật ≈ ___ (bảng §1.1) | tier 3 ⇒ BỎ beta, dùng premium
B2 LÕI SẠCH  → TTM pass 12 kỳ = ___ | base rate ngành = ___ | 3 kỳ gần nhất: _ _ _
   ⇒ [sạch → DCF neo chính] / [đang xấu → DCF chỉ tham khảo] / [đặc thù ngành → đổi phương pháp]
B3 PHƯƠNG PHÁP → nhóm (a)…(f) = ___ → mở framework: ______________
B4 WACC      → rf ___ + beta ___ × 6,5% + premium ___ = ___%
   ✅ đã kiểm tra KHÔNG double-count rủi ro vào cả g LẪN WACC?
   ✅ đã có bảng độ nhạy WACC ±1pp trong report?
```

---

## 6. Giới hạn của tài liệu này (đọc để không dùng sai)

- **Là guidance, không phải công thức tự động.** Mỗi ticker vẫn cần judgment; các ngưỡng ở đây là
  mốc tham chiếu để tránh lỗi thô, không phải quy tắc quyết định.
- **Test §2 chưa được backtest như tín hiệu dự báo** — nó là bộ lọc "có tin được DCF không", không
  phải tín hiệu mua/bán. Đừng để nó rò vào logic giao dịch.
- **Base rate ngành §2.3 không point-in-time** (gán ICB hiện tại cho lịch sử) — đủ để so sánh tương
  đối, không đủ để làm gate production.
- **Beta đo trên cửa sổ 2021-07 → 2026-07** (5 năm, tần suất tuần). Cửa sổ này chứa hậu-COVID +
  chu kỳ 2022; beta sẽ khác nếu đổi cửa sổ. Đo lại khi cần con số cho report chính thức.
- **Không có gì ở đây chạm production.** Research-only, theo đúng phạm vi dispatch.
- Ranh giới nghề: mọi kết luận neo vào số đo được, không phải narrative tuỳ nghi.

---

## 7. Tái lập (mọi con số trên đều chạy lại được)

Nguồn dữ liệu — đã tra `mike/kb/data_registry.md` trước khi chọn: `data/bq_cache/ticker/{year}.parquet`
(OHLCV lịch sử), `ticker_financial.parquet`, `ticker_1m.parquet` (snapshot hiện tại), `risk_rating.parquet`.
Interpreter: `/home/trido/thanhdt/wc_venv/bin/python` (`$DNA_PYEXE`), `duckdb SET threads=1`.

```python
# --- Beta thật (weekly, 5y, vs VNINDEX) cho 1 mã ---
import duckdb, pandas as pd, numpy as np
c = duckdb.connect(); c.execute("SET threads=1")
files = [f"data/bq_cache/ticker/{y}.parquet" for y in range(2021, 2027)]
src = "read_parquet([" + ",".join(f"'{f}'" for f in files) + "])"
px = c.execute(f"select time,ticker,Close,VNINDEX from {src} where time>=DATE '2021-07-01'").df()
mw = (px[['time','VNINDEX']].dropna().drop_duplicates('time').set_index('time')['VNINDEX']
        .sort_index().resample('W-FRI').last().pct_change().dropna())
sw = (px[px.ticker=='FPT'].set_index('time')['Close']
        .resample('W-FRI').last().pct_change().reindex(mw.index))
ok = sw.notna() & mw.notna()
print("beta =", np.cov(sw[ok], mw[ok])[0,1] / mw[ok].var())   # FPT -> 0.71

# --- Test lõi sạch TTM cho 1 mã ---
d = c.execute("""select ticker,quarter,CF_OA_P0,CF_OA_P1,CF_OA_P2,CF_OA_P3,
                        NP_P0,NP_P1,NP_P2,NP_P3
                 from 'data/bq_cache/ticker_financial.parquet'
                 where ticker='DGC' and time>=DATE '2014-01-01' order by time""").df()
d['cfoa_ttm'] = d[[f'CF_OA_P{i}' for i in range(4)]].sum(axis=1, min_count=4)
d['np_ttm']   = d[[f'NP_P{i}'    for i in range(4)]].sum(axis=1, min_count=4)
d['pass_ttm'] = d.cfoa_ttm >= d.np_ttm
print(d.pass_ttm.mean(), d.tail(6)[['quarter','pass_ttm']].to_string(index=False))

# --- Vốn hoá & tier (LƯU Ý: Price, không phải Close) ---
c.execute("""select ticker, Price*OShares/1e9 mcap_ty, Trading_Value_1M_P50/1e9 tv_ty, ICB_Code
             from 'data/bq_cache/ticker_1m.parquet'
             where time=(select max(time) from 'data/bq_cache/ticker_1m.parquet')
               and OShares>0 and ticker='FPT'""").df()
```

**Liên quan:** `dcf_valuation_framework.md` (mô hình 2-stage FCFE chi tiết + hiệu chuẩn thực nghiệm),
`beta_reverse_engineer_results.csv` (bằng chứng `risk_rating` ranks giống weekly-5y),
`soe_governance_framework.md` (nhóm c), `mike/kb/data_registry.md` (nguồn dữ liệu canonical).

**Script & dữ liệu của chính router này** (job `Taylor_20260721_112050`):

| File | Dùng để |
|---|---|
| `beta_universe.py` → `data_beta_universe.csv` | beta thật toàn bộ mã (§1.1b) — **tra file, đừng tính tay** |
| `beta_universe.py` → `data_beta_bin_map.csv` | bảng quy đổi bin → beta thật (§1.1) |
| `size_premium_vn.py` → `data_size_premium.csv` | đo premium theo vốn hoá/thanh khoản (§1.2b) |
| `research/asymmetric_beta_regime.md` | beta bất đối xứng theo regime — **THĂM DÒ**, chưa dùng được |

Chạy lại: `source ./wc_env.sh && $DNA_PYEXE mike/agents/Taylor/<script>.py` (từ thư mục
`/home/trido/thanhdt/WorkingClaude`).

---

## 8. Điều chỉnh bear-case DCF theo beta bất đối xứng (đã duyệt 2026-07-21)

Nguồn: `research/asymmetric_beta_regime.md` (job `Taylor_20260721_112050`), user duyệt dùng ở tầng
**định giá/giám sát rủi ro** — KHÔNG áp dụng cho chọn cổ phiếu/sizing/DT5G/V2.4.

**Phát hiện**: beta đo khi thị trường giảm cao hơn rõ rệt và ổn định so với beta đo khi thị trường
tăng (asym +0,23 IS / +0,34 OOS, sống qua kiểm soát thanh khoản) — tương quan giữa các cổ phiếu tăng
mạnh ở đuôi xấu của thị trường (mọi mã rơi cùng nhau khi khủng hoảng/downtrend), không tăng tương ứng
ở đuôi tốt (mã nào có câu chuyện riêng mới bứt phá). **Hiệu ứng này KHÔNG tập trung riêng ở nhóm "đầu
cơ"** (turnover, biến động riêng lẻ không có tương quan) — đây là hiện tượng thị trường rộng, không
phải cách phân loại cổ phiếu.

**Quy tắc áp dụng — kịch bản Bear của mọi DCF từ nay**:
- Dùng **beta chuẩn (§1.1b) + 0,25** làm beta cho kịch bản Bear (thay vì cùng 1 beta cho cả 3 kịch bản
  Bear/Base/Bull như trước đây).
- Base và Bull vẫn dùng beta chuẩn — bất đối xứng chỉ có bằng chứng vững ở đuôi xấu, KHÔNG có bằng
  chứng tương ứng ở đuôi tốt (đừng tự suy ra "Bull nên trừ beta" — chưa đo được).
- Ví dụ: FPT beta chuẩn 0,71 → Bear dùng 0,96 thay vì 0,71 (chi phí vốn cổ phần Bear tăng thêm
  ~0,25×6,5%≈1,6pp so với cách cũ).

**Ghi chú gửi risk-auditor (song song, không thay thế quy tắc trên)**: mọi ước tính drawdown danh mục
hiện tại dùng beta vô điều kiện đang **lạc quan quá mức ~0,15 đến 0,34 beta** trong giai đoạn
CRISIS/BEAR thực tế — đây là ghi chú hiệu chỉnh cho việc đọc số, không phải đề xuất đổi cơ chế risk
gate/DT5G.

**Giới hạn** (đọc trước khi dùng): đây vẫn là phát hiện THĂM DÒ, chưa qua quant-skeptic; +0,25 là ước
lượng điểm giữa (asym đo được 0,23-0,34 tuỳ IS/OOS), không phải hằng số chính xác — coi là mức điều
chỉnh thận trọng hợp lý, không phải con số đã tối ưu.
