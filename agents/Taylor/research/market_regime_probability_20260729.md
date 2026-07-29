# Thị trường đang ở đâu? — ước lượng xác suất bằng percentile + base rate lịch sử

**Ngày dữ liệu: 2026-07-28** · job `Taylor_20260729_024754` · Taylor (Quant)
**Loại: RESEARCH / trả lời câu hỏi — KHÔNG wire signal mới vào production.**

---

## 0. Trả lời ngắn

| Kịch bản 12 tháng tới (tính từ 1680,62) | Ước lượng | Khoảng thô (90%) |
|---|---|---|
| **Bear-like** — có lúc rơi ≥20% dưới mức hiện tại | **~20%** | 10–35% |
| **Không bear** (đi ngang / điều chỉnh nông / hồi phục) | **~80%** | 65–90% |
| *— trong đó điều chỉnh 10–20% rồi hồi* | ~10–25% | rất rộng |

**Điểm cốt lõi, phải nói thẳng:** con số ~20% này **không khác biệt có ý nghĩa thống kê** so với
base rate vô điều kiện (19% từ 2014+, 25% từ 2008+). Định giá đang **hơi ủng hộ** (PE rẻ), kỹ thuật
đang **hơi bất lợi** (dưới MA200, −12,8% từ đỉnh 52w) — hai lực gần như triệt tiêu nhau. Cỡ mẫu
episode độc lập chỉ **9–24**, khoảng tin cậy rộng đến mức mọi con số lẻ đều là an-toàn-giả.

~~Định vị đúng nhất bằng một câu: **thị trường đang RẺ theo P/E nhưng KHÔNG rẻ theo P/B, và đang ở
trạng thái kỹ thuật xấu.**~~ Đây là vùng "bình thường-hơi-căng", **không phải** vùng định giá bong bóng
(2007, 2018, 2021) mà cũng **không phải** vùng khủng hoảng-cơ-hội (2008, 2012, 2020-03, 2022-11).

> ⚠️ **ĐÍNH CHÍNH LỚN 2026-07-29 (Phụ lục B) — vế "KHÔNG rẻ theo P/B" đã SAI.** Toàn bộ mức "đắt"
> của P/B đến từ **một mã duy nhất: VIC** (20,17% vốn hoá top-100, PB riêng 10,80 — cả hai đều là
> hiện tượng mới của 2025-2026). Đo bằng bất kỳ phương pháp nào bền với outlier đơn lẻ, P/B hiện tại
> nằm ở **phân vị 0,4–27 của 3 năm** thay vì 65,6. **Câu đúng: thị trường RẺ theo CẢ P/E lẫn P/B đối
> với cổ phiếu điển hình; chỉ số cap-weighted trông đắt vì VIC, không phải vì thị trường đắt.**
> Xem **Phụ lục B**. (Kết luận xác suất ~20% ở bảng trên **không đổi** — xem B.5.)

---

## 1. PE / PB thị trường hiện tại + phân vị lịch sử

### 1.1 Số hiện tại (2026-07-28)

| Chỉ số | Giá trị | Nguồn |
|---|---|---|
| VNINDEX | **1.680,62** | `tav2_bq.ticker` hàng `ticker='VNINDEX'` |
| PE thị trường (chính thức) | **12,46** | `ticker.VNINDEX_PE` (mirror trên hàng cổ phiếu) |
| PE thị trường (tự dựng, toàn bộ) | 12,39 | Σmcap/Σearn, 708 mã PE>0 |
| PE thị trường (tự dựng, top-100 mcap) | 12,93 | 100 mã lớn nhất |
| **PB thị trường (tự dựng, toàn bộ)** | **1,803** | Σmcap/Σbook, 767 mã PB>0 |
| PB thị trường (tự dựng, top-100 mcap) | 2,028 | 100 mã lớn nhất |
| ROE gộp (Σearn/Σbook) | ~~14,48%~~ → **14,61%** | hệ quả của 2 dòng trên · ⚠️ **đã sửa 2026-07-29, xem Phụ lục A.0** |

> **Không có cột `VNINDEX_PB` trong BQ.** PB thị trường **phải tự dựng** = Σ(Price×OShares) /
> Σ(BVPS×OShares) — cap-weighted harmonic, đúng định nghĩa PB chỉ số. Cùng công thức dựng luôn PE để
> **kiểm chứng**: PE tự dựng vs PE chính thức trên 3.134 phiên chồng lấn (2014-01→2026-07):
> corr mức 0,945 · corr biến động ngày 0,814 · sai số tuyệt đối trung vị 1,02 điểm · lệch mức trung
> bình −6,2% · **hiện tại gần như trùng khít (12,39 vs 12,46)**. ⇒ PB tự dựng đáng tin ở mức tương đương.

### 1.2 Phân vị (100 = đắt nhất lịch sử)

| Cửa sổ | N phiên | **PE** | **PB** | ROE gộp |
|---|---|---|---|---|
| Toàn bộ 2008+ (tự dựng) | 4.631 | **39,6** | **51,0** | 76,9 |
| 10 năm gần nhất | 2.499 | **15,8** | **38,7** | 86,7 |
| 5 năm gần nhất | 1.247 | **27,7** | **56,0** | 76,0 |
| 3 năm gần nhất | 747 | **11,5** | **65,6** | **99,6** |
| *PE chính thức, 2014+* | *3.134* | *10,3* | — | — |
| *PE chính thức, 3 năm* | *747* | *3,6* | — | — |

> ⚠️ **Cột PB ở bảng này đã bị VIC bóp méo — xem Phụ lục B.** Đo bằng phương pháp bền với một mã
> siêu lớn, phân vị PB là **13,5–35 (2008+) · 1,8–17,6 (10 năm) · 2,2–31,8 (5 năm) · 0,4–27,0 (3 năm)**,
> tức là **RẺ**, không phải 51,0/38,7/56,0/65,6 như bảng trên. Cột PE cũng bị nâng nhẹ (VIC PE=142,5):
> PE top-100 ex-VIC = **10,51**, phân vị **0,1 của 3 năm**.

Ngũ phân vị PE tự dựng 2008+: p05=8,64 · p25=11,29 · **p50=13,10** · p75=14,87 · p95=17,26
Ngũ phân vị PB tự dựng 2008+: p05=1,42 · p25=1,61 · **p50=1,79** · p75=2,07 · p95=2,58

### 1.3 Điều quan trọng nhất trong bảng trên: **PE và PB không nói cùng một câu chuyện**

- PE ở **phân vị 11,5 của 3 năm** (rẻ nhất top-12%) — theo PE chính thức thậm chí là **phân vị 3,6**.
- ~~PB ở **phân vị 65,6 của 3 năm** (đắt hơn 2/3 số phiên 3 năm qua).~~ ⚠️ **SAI — xem Phụ lục B.**
  PB "đắt" là ảo giác do VIC; đo bền với outlier thì PB ở **phân vị 0,4–27 của 3 năm**. **PE và PB
  THỰC RA nói CÙNG một câu chuyện: rẻ.** Cả tiêu đề §1.3 lẫn dòng gạch trên đều phải đọc ngược lại.
- Cầu nối: **ROE gộp 14,61% — phân vị 98,4 của 3 năm, 78,6 của 10 năm, nhưng chỉ 59,9 kể từ 2008.**
  ⚠️ **Đã sửa 2026-07-29 (Phụ lục A)**: số cũ (14,48% · phân vị 99,6/3Y · 86,7/10Y · 76,9/2008+) tính
  tử số và mẫu số trên hai rổ mã khác nhau.

Nói cách khác: **P/E rẻ vì E đang ở đỉnh chu kỳ lợi nhuận, không phải vì P rẻ.** Đây là dạng "rẻ"
mong manh nhất trong toàn bộ họ chỉ báo định giá — nếu biên lợi nhuận mean-revert, PE "12,4" sẽ tự
động đắt lên mà giá không cần giảm một đồng. ⚠️ **Đã định lượng lại 2026-07-29 (Phụ lục A.5): kịch bản
trung tâm là PE → 13,1 (+6%), vẫn ở phân vị ~25 của 10 năm. Mức "15–16" đòi hỏi ROE rơi về p05 hoặc
đáy 10 năm — kịch bản đuôi, không phải kịch bản cơ sở. Câu "sẽ biến thành 15–16" ở bản gốc là quá lời.** Bất cứ luận điểm "thị trường rẻ nên an toàn"
nào chỉ dựa trên PE mà bỏ qua dòng ROE này đều đang đếm thiếu một rủi ro thật.

Neo thứ ba, độc lập: **earnings yield 8,03% vs lãi suất huy động Big4-12M-online 6,80%**
(`data/deposit_rate_vn_events.csv`, xác nhận 2026-07-20) ⇒ phần bù **+1,23pp**. Dương nhưng mỏng —
không phải mức "rẻ đến mức không thể sai" (2012 và 2022-11 phần bù rộng hơn nhiều), cũng không âm
như các đỉnh 2018/2021.

---

## 2. Base rate: sau những giai đoạn định giá TƯƠNG ĐƯƠNG, chuyện gì đã xảy ra?

**Định nghĩa "bear"** dùng xuyên suốt: trong 252 phiên tới, VNINDEX **có lúc** rơi ≥20% dưới mức
đóng cửa ngày điều kiện (drawdown từ điểm vào, không phải từ đỉnh sau đó). Đây là định nghĩa khắt khe
đúng với câu hỏi "từ đây có rơi vào bear không".

**Cỡ mẫu báo theo EPISODE ĐỘC LẬP, không theo ngày** — ngày liên tiếp trong cùng một đợt gần như là
một quan sát duy nhất. CI 90% dưới đây là **block-bootstrap theo episode** (4.000 lần), đúng cách xử
lý chồng lấn.

| Điều kiện | N ngày | N episode | **P(bear 12M)** | CI90 | P(bình thường, không rơi >10%) | fwd 12M trung vị |
|---|---|---|---|---|---|---|
| Vô điều kiện 2008+ | 4.380 | — | 25% | — | 47% | +8,1% |
| Vô điều kiện 2014+ | 2.882 | — | 19% | — | 53% | +9,0% |
| **PE trong ±0,5 điểm (11,9–12,9)** | 672 | 21 | **15%** | [2%, 37%] | 64% | +9,0% |
| **PB trong ±5% (1,71–1,89)** | 745 | 21 | **15%** | [6%, 29%] | 43% | +4,9% |
| PE ∧ PB cùng trong dải | 320 | 17 | 16% | [3%, 38%] | 49% | +2,7% |
| Dưới MA200 (mọi định giá) | 1.656 | 20 | **26%** | [14%, 34%] | 54% | +9,7% |
| dd52w trong [−18%, −8%] | 1.088 | 29 | 26% | [11%, 46%] | 50% | +8,9% |
| **ANALOG ĐẦY ĐỦ** (dưới MA200 ∧ PE±0,75 ∧ dd52w −20..−6%) | 342 | **9** | **20%** | [4%, 50%] | 76% | +11,7% |

Horizon 6 tháng, analog đầy đủ: **P(bear) = 20%**, P(không rơi quá 10%) = 77%.
Phân phối lợi nhuận forward của analog đầy đủ: 1M +1,6% (40% âm) · 3M +5,6% (28% âm) ·
6M +12,6% (23% âm) · 12M +11,7% (27% âm) — đều là trung vị.

### 2.1 Chín episode analog — đây mới là "cỡ mẫu" thật

| Đợt | n ngày | fwd 3M | fwd 6M | fwd 12M | Đáy sâu nhất 12M |
|---|---|---|---|---|---|
| 2014-05-12 → 05-15 | 3 | +17,5% | +15,6% | +3,8% | −0,6% |
| 2014-10-27 → 2015-06-17 | 111 | −0,0% | −4,8% | +3,8% | −10,8% |
| 2016-02-05 → 04-21 | 45 | +13,0% | +21,2% | +29,6% | −0,2% |
| **2020-02-24 → 03-10** | 12 | −3,8% | −5,4% | +28,6% | **−27,0%** |
| 2020-05-11 → 08-24 | 61 | +1,4% | +13,5% | +53,2% | −5,2% |
| **2022-05-09 → 06-16** | 22 | −1,2% | −19,7% | −16,7% | **−28,2%** |
| **2022-08-01 → 09-16** | 33 | −16,5% | −12,5% | −1,7% | **−25,9%** |
| 2023-10-18 → 12-27 | 36 | +5,4% | +7,9% | +15,1% | −6,8% |
| 2025-04-03 → 05-07 | 19 | +14,0% | +37,9% | +41,2% | −11,0% |
| *(2026-03-23 → 03-24)* | 2 | +17,5% | chưa đủ | chưa đủ | chưa đủ |
| **⟶ 2026-07-20 → 07-28 (hiện tại)** | 7 | — | — | — | — |

**3/9 episode dẫn tới bear** (2020 COVID, 2022 lần 1, 2022 lần 2) = 33% theo episode, 20% theo ngày.
Đọc kỹ danh sách: 2 trong 3 ca bear (2022-05, 2022-08) là **đã ở giữa một bear market rồi** — điều
kiện lọc bắt được chúng trên đường xuống chứ không phải trước khi xuống. Ca duy nhất thực sự "đang
bình thường rồi rơi" là **2020-02 (COVID)** — một cú sốc ngoại sinh mà **không** chỉ báo định giá nào
báo trước được. Đây là lý do tôi không tin con số 33% và cũng không tin con số 15%: mẫu quá nhỏ và
cơ chế không đồng nhất.

---

## 3. Đối chiếu với tín hiệu hệ thống đang có sẵn

| Tín hiệu | Giá trị 2026-07-28 | Hàm ý | Đồng thuận với §1-2? |
|---|---|---|---|
| **DT5G** (`vnindex_5state_dt5g_live`) | **NEUTRAL (3)** liên tục từ 2026-02-13 (≈5,5 tháng) | phân bổ 70% | ✅ Đồng thuận — không CRISIS/BEAR, cũng không BULL |
| DT5G macro overlay | `active=False`, `state_dt4=3` = `state=3` | macro cap chưa kích hoạt | ✅ chưa có stress vĩ mô đủ để cap |
| `macro_health.json` | HEALTHY, `DT5G_macro`, missed_runs=0 | nguồn state tin cậy | — |
| **`market_stress`** | **flag=True**: `vix_elevated=True`, `vni_below_ma200=True` | cảnh báo mềm | ⚠️ **Đồng thuận với vế XẤU** |
| **CAPIT** | `capit_fired=True`, `breadth_oversold=0,372` > `washout_gate=0,31`, `capit_size=0,75` | đang giải ngân rổ washout | ⚠️ Đồng thuận: **hệ đang coi đây là vùng sợ hãi**, mua vào chứ không phòng thủ |
| **dd52w** | **−12,8%** (lúc CAPIT fire 07-20 mới ~−7%) | đã sâu thêm 5,8pp trong 6 phiên | ⚠️ thị trường vẫn đang xấu đi |
| VNINDEX vs MA200 | 1.680,62 / 1.772,63 = **0,948** | dưới MA200 | ⚠️ vế kỹ thuật xấu |

**Đọc tổng hợp — có một mâu thuẫn thật, đáng nêu tên:**
- Nhóm "chậm/định giá" (DT5G NEUTRAL, PE phân vị thấp) nói: **bình thường, hơi rẻ**.
- Nhóm "nhanh/kỹ thuật" (dưới MA200, dd52w −12,8% và đang sâu thêm, VIX cao, breadth oversold 0,372
  vượt xa gate 0,31) nói: **đang ở giữa một đợt bán tháo còn hiệu lực**.
- PB phân vị 65,6 (3 năm) + ROE phân vị 99,6 nói: **cái "rẻ" của PE là rẻ-nhờ-E-đỉnh, không phải
  rẻ-nhờ-P-thấp**.

Đây **không** phải mâu thuẫn cần "sửa" — đúng theo thiết kế: DT5G là **cổng phòng thủ chậm, price-
confirmed** (không tự re-risk theo macro, chỉ cap khi stress), CAPIT là **cổng mua-khi-sợ-hãi nhanh**.
Việc cả hai cùng bật (NEUTRAL + CAPIT fired) chính là trạng thái "sợ hãi có tính toán" mà hệ được
thiết kế để mua vào. Con số bootstrap ở §2 nói mức độ sợ hãi hiện tại là **hợp lý nhưng chưa phải cơ
hội hiếm**.

---

## 4. Kết luận dạng xác suất

**Trong 12 tháng tới, tính từ VNINDEX 1.680,62:**

| Kịch bản | Xác suất | Cơ sở |
|---|---|---|
| **Bear-like** (có lúc ≤ −20% so với hôm nay) | **~20%** (khoảng thật 10–35%) | analog đầy đủ 3/9 episode = 33% theo episode / 20% theo ngày; PE-band 15%; MA200-band 26%; vô điều kiện 19–25% |
| **Điều chỉnh nhưng không bear** (đáy trong khoảng −10%..−20%) | **~10–25%** | analog đầy đủ cho 4% (mẫu quá mỏng, không tin); các điều kiện rộng hơn cho 20–42% |
| **Bình thường / hồi phục** (không rơi quá −10% nữa) | **~55–75%** | analog đầy đủ 76%; PE-band 64%; vô điều kiện 47–53% |

Kỳ vọng trung tâm về lợi nhuận (trung vị analog): 3M **+5,6%**, 6M **+12,6%**, 12M **+11,7%** —
nhưng đuôi trái dày và thật (2022: −16,7% sau 12M).

**Ba điều tôi KHÔNG kết luận, vì dữ liệu không cho phép:**

1. **Không kết luận "định giá hiện tại làm giảm rủi ro bear".** P(bear) có điều kiện (15–26%) nằm
   trọn trong khoảng vô điều kiện (19–25%), và CI90 của mọi điều kiện đều phủ lên nó. Với 9–24
   episode độc lập, **không có power** để phân biệt. Ai nói "PE phân vị 11 nên an toàn" là đang đọc
   ra tín hiệu từ nhiễu.
2. **Không đưa con số lẻ đến 1 chữ số thập phân.** "20%" ở đây nghĩa là "một-phần-năm, cộng trừ
   một-phần-mười", không phải 20,3%.
3. **Không dự báo cú sốc ngoại sinh.** Ca bear "thật bất ngờ" duy nhất trong mẫu (2020-02 COVID) sinh
   ra từ thứ mà không mô hình định giá nào thấy trước. Nếu 12 tháng tới có một sự kiện loại đó,
   phân tích này vô hiệu — và đó chính là lý do cổng DT5G tồn tại như **bảo hiểm**, không phải như
   máy dự báo.

**Hàm ý sizing (định lượng, không narrative):** không có gì trong phân tích này đòi thay đổi tham số
production. DT5G NEUTRAL → 70%; CAPIT đã fire → rổ washout đang giải ngân theo `capit_size=0,75`.
Phân tích percentile **xác nhận** vị trí này là hợp lý: rẻ vừa đủ để không đứng ngoài, không đủ rẻ để
all-in, và có một rủi ro biên-lợi-nhuận-đỉnh (ROE phân vị 99,6/3 năm) mà không chỉ báo phòng thủ nào
của hệ đang theo dõi.

---

## 5. Giới hạn dữ liệu & phương pháp (đọc trước khi trích dẫn)

1. **`ticker.VNINDEX_PE` chỉ có từ 2016-07-01, KHÔNG phải 2006-03-30.** Đã kiểm chứng trực tiếp
   (`MIN(time) WHERE VNINDEX_PE IS NOT NULL` = 2016-07-01, N=2,91M hàng). Ghi chú trong kb memory
   `vnindex-pe-bq-gotcha` ("tồn tại từ 2006-03-30") **không còn đúng với trạng thái bảng hiện tại** —
   nên sửa. `data/VNINDEX_pe_only.csv` kéo dài về 2014-01-02 (nhưng cũ, dừng ở 2026-03-30).
2. **Không có `VNINDEX_PB` trong BQ** — PB thị trường là số **tự dựng**, không phải số công bố. Đã
   kiểm chứng bằng cách dựng PE song song và so với PE chính thức (corr 0,945).
3. **Trôi thành phần (composition drift)**: rổ tự dựng gồm cả HNX/UPCOM, VNINDEX chỉ có HOSE. Số mã
   hợp lệ tăng từ 157 (2008) lên 767 (2026). So sánh phân vị xuyên thời đại vì thế có sai lệch cấu
   trúc — đó là lý do tôi báo cả cửa sổ 3Y/5Y/10Y (ít trôi hơn) chứ không chỉ 2008+.
4. **Chồng lấn cửa sổ**: mọi CI dùng block-bootstrap theo episode (gap >21 phiên). CI tính theo ngày
   sẽ hẹp giả tạo 3-5 lần — đừng dùng.
5. **Cột mirror `t.VNINDEX` bị corrupt 2026-04-01..04-29** (làm tròn hàng chục, ≤0,29% —
   `kb/data_registry/price-volume/vnindex_mirror_col.md`). Chuỗi giá dùng ở đây đọc **hàng
   `ticker='VNINDEX'` gốc**, không đụng cột mirror ⇒ không ảnh hưởng. Cột `VNINDEX_PE` đọc từ hàng cổ
   phiếu đã kiểm tra tính nhất quán (min≈max mỗi ngày).
6. Tất cả là **phân tích mô tả/base-rate**, không phải mô hình dự báo, **không backtest lợi nhuận,
   không đề xuất wire**. Không cần quant-skeptic vì không có thay đổi production nào được đề xuất.

**Artifact tái lập:** `mike/agents/Taylor/exp_market_prob/` — `analyze.py` (percentile),
`eventstudy.py` / `eventstudy2.py` / `eventstudy3.py` (base rate + bootstrap),
`daily_panel.csv` / `panel_fwd.csv` (panel ngày), `percentiles.csv`, `baserates*.csv`.

---
---

# PHỤ LỤC A — ROE toàn thị trường: thống kê mô tả + đánh giá GO/NO-GO

**Bổ sung 2026-07-29** · job `Taylor_20260729_041421` · trả lời câu hỏi tiếp theo của user:
*"ROE bình quân hiện nay là bao nhiêu? Cho thêm thống kê mô tả (histogram). Có nên đưa vào làm
chỉ báo bổ sung cho tín hiệu thị trường không?"*

**Artifact**: `mike/agents/Taylor/exp_roe/` (`roe_desc.py`, `roe_fund.py`, `eventstudy_roe.py`,
`eventstudy_roe2.py`, `eventstudy_roe3.py`, `plot_roe.py` + CSV).
**Hình**: `mike/agents/Taylor/research/roe_market_histogram_20260729.png`

---

## A.0 Trả lời ngắn

| Câu hỏi | Trả lời |
|---|---|
| ROE thị trường hiện tại? | **14,6%** nếu hỏi "ROE gộp" (Σ lợi nhuận / Σ vốn chủ). **8,4%** nếu hỏi "mã trung vị". Hai con số đều đúng, đo hai thứ khác nhau — xem §A.1. |
| ROE có đang ở đỉnh chu kỳ không? | **Đỉnh 3 năm (phân vị 98) — nhưng chỉ ~phân vị 60-77 kể từ 2008.** Báo cáo chính §1.3 nói "đỉnh chu kỳ" là **hơi quá lời**; sửa lại ở §A.2. |
| Có nên wire ROE làm chỉ báo bổ sung cho DT5G/CAPIT? | **NO-GO.** Lý do chính không phải cỡ mẫu mà là **đồng nhất thức đại số**: ROE thị trường **= PB / PE**, khớp đến sai số máy (10⁻¹⁶). Nó không phải biến thứ ba — nó *là* PE và PB viết lại. Chi tiết §A.4. |

**Sửa 2 con số trong báo cáo chính** (§1.1 và §1.3), do lỗi rổ mẫu:

| Chỗ | Bản cũ | Bản đúng | Nguyên nhân |
|---|---|---|---|
| ROE gộp hiện tại | 14,48% | **14,61%** | Tử số tính trên 708 mã (PE>0), mẫu số trên 767 mã (PB>0) — hai rổ khác nhau. Nay ép **cùng một rổ**. |
| ROE phân vị 2008+ | 76,9 | **59,9** | hệ quả của cùng lỗi trên |
| ROE phân vị 3 năm | 99,6 | **98,4** | " |

Kết luận định tính của §1.3 (PE rẻ một phần nhờ E cao) **vẫn đứng**, nhưng **định lượng nhẹ hơn
nhiều so với câu đã viết** — xem §A.5.

---

## A.1 ROE hiện tại — 5 con số, đừng trộn lẫn

Dữ liệu 2026-07-28. Nguồn: `tav2_bq.ticker` (PE/PB/BVPS/OShares/Price theo phiên) và
`tav2_bq.ticker_financial` (NP_P0..P3, BVPS, OShares theo quý) — cả hai đã tra
`mike/kb/data_registry/` trước khi dùng.

| # | Cách đo | Giá trị | Rổ | Dùng khi nào |
|---|---|---|---|---|
| 1 | **ROE gộp, trọng số vốn chủ** = Σ(EPS×CP)/Σ(BVPS×CP) | **14,61%** | 708 mã (PE>0 ∧ PB>0) | Con số "thị trường" chuẩn — cùng hệ với PE/PB chỉ số. **Đây là số dùng ở §1.3 báo cáo chính.** |
| 2 | ROE gộp **từ số cơ bản, gồm cả doanh nghiệp LỖ** = Σ NP_TTM / Σ vốn chủ | **14,22%** | 1.214 mã, quý 2026Q3, **15,1% số mã đang lỗ** | Kiểm chứng: cách 1 có thiên lệch sống sót (loại mã lỗ). Chênh chỉ **−0,39pp** ⇒ thiên lệch nhỏ. |
| 3 | ROE gộp **rổ top-100 vốn hoá** (kích thước cố định) | **15,69%** | 100 mã | So sánh **xuyên thời đại** không bị trôi thành phần (rổ toàn bộ nở từ 150 → 924 mã). |
| 4 | **Trung bình giản đơn** ROE từng mã (winsor ±100%) | **12,42%** | 708 mã | "Doanh nghiệp trung bình" |
| 5 | **Trung vị** ROE từng mã, rổ đầy đủ (gồm mã lỗ) | **8,41%** | 1.090 mã | "Doanh nghiệp điển hình" — con số thấp nhất và **thật nhất với đa số mã** |

### Tại sao 14,6% (gộp) ≫ 8,4% (trung vị)? — không phải lỗi, là cấu trúc thị trường VN

| Nhóm | Số mã | % tổng vốn chủ | ROE gộp | ROE trung vị |
|---|---|---|---|---|
| **Ngân hàng** | 26 | **35,2%** | **15,92%** | **15,36%** |
| Phi ngân hàng | 1.064 | 64,8% | 13,58% | **8,33%** |
| *Top-15 theo vốn chủ* | 15 | 41,3% | **16,98%** | — |
| *1.075 mã còn lại* | 1.075 | 58,7% | 12,59% | 8,34% |

15 mã lớn nhất (VHM 23,7% · VCB 15,4% · VPB 15,6% · BID 16,2% · TCB 14,4% · CTG 20,2% · VIC 7,6% ·
MBB 18,5% · HPG 16,6% · ACB 15,8% · HDB 20,5% · ACV 14,7% · SHB 17,0% · GAS 16,4% · BSR 19,0%)
chiếm **41,3% vốn chủ toàn thị trường** và có ROE 17,0%. Đuôi dài 1.000+ mã nhỏ kéo trung vị xuống 8,4%
nhưng gần như không ảnh hưởng số gộp.

⇒ **Khi nói "ROE thị trường 14,6%" là đang nói về ~15 doanh nghiệp lớn nhất, chủ yếu là ngân hàng.**
Câu "biên lợi nhuận đang ở đỉnh chu kỳ" vì thế thực chất là câu về **chu kỳ lợi nhuận ngân hàng**,
không phải về 1.000 doanh nghiệp niêm yết còn lại.

---

## A.2 Thống kê mô tả đầy đủ — chuỗi thời gian ROE thị trường

Đơn vị %. `cur` = giá trị 2026-07-28. `pctile` = phân vị của giá trị hiện tại trong cửa sổ đó
(100 = cao nhất lịch sử).

### A.2.1 ROE gộp trọng số vốn chủ (cách đo #1, rổ toàn bộ)

| Cửa sổ | N phiên | cur | **pctile** | mean | median | std | skew | kurtosis | p05 | p25 | p50 | p75 | p95 | min | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2008+ | 4.631 | 14,61 | **59,9** | 14,77 | 14,24 | 1,90 | +0,87 | 0,00 | 12,26 | 13,55 | 14,24 | 15,91 | 18,98 | 11,58 | 19,65 |
| 10 năm | 2.499 | 14,61 | **78,6** | 13,83 | 13,78 | 1,09 | +0,22 | −0,15 | 11,98 | 13,12 | 13,78 | 14,53 | 15,80 | 11,58 | 16,84 |
| 5 năm | 1.247 | 14,61 | **69,3** | 13,85 | 13,80 | 1,41 | +0,18 | −1,07 | 11,78 | 12,59 | 13,80 | 15,06 | 16,04 | 11,58 | 16,84 |
| 3 năm | 747 | 14,61 | **98,4** | 12,94 | 12,94 | 0,89 | +0,25 | −1,12 | 11,71 | 12,10 | 12,94 | 13,74 | 14,52 | 11,58 | 14,67 |

### A.2.2 Hai cách đo kiểm chứng — kết luận không đổi về chất

| Cửa sổ | ROE gộp #1 | **ROE top-100 #3** | **ROE cơ bản (gồm mã lỗ) #2** |
|---|---|---|---|
| | cur 14,61% | cur **15,69%** | cur **14,22%** |
| 2008+ | pctile 59,9 (N=4.631 phiên) | pctile **76,3** (N=4.633) | pctile **77,3** (N=75 quý) |
| 10 năm | 78,6 | **85,9** (N=2.501) | **90,2** (N=41 quý) |
| 5 năm | 69,3 | **74,4** (N=1.249) | **81,0** (N=21 quý) |
| 3 năm | 98,4 | **97,7** (N=749) | **92,3** (N=13 quý) |

Thống kê mô tả ROE top-100 (2008+, N=4.633): mean 14,78 · median 14,27 · std 1,80 · skew +0,60 ·
kurt 2,66 · p05 12,65 · p25 13,66 · p50 14,27 · p75 15,59 · p95 18,21.

**Đọc bảng này:** cả ba cách đo đồng thuận rằng ROE **đang ở gần đỉnh 3 năm (phân vị 92-98)** nhưng
**chỉ ở phân vị 60-77 kể từ 2008**. Giai đoạn 2008-2012 ROE gộp 15,6-19,0% — cao hơn hẳn hôm nay.
Vậy phát biểu đúng là: **"ROE đang ở đỉnh của chu kỳ 3 năm hiện tại, KHÔNG phải đỉnh chu kỳ lịch sử."**
Câu trong §1.3 báo cáo chính cần hiểu theo nghĩa hẹp đó.

### A.2.3 Trung bình theo năm (bối cảnh chu kỳ)

| Năm | n mã TB | ROE gộp | ROE trung vị | PE | PB | | Năm | n mã TB | ROE gộp | ROE trung vị | PE | PB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2008 | 150 | 17,79 | 16,01 | 12,71 | 2,27 | | 2018 | 798 | 14,49 | 10,68 | 17,14 | 2,48 |
| 2009 | 219 | 16,16 | 15,51 | 12,38 | 1,99 | | 2019 | 832 | 13,89 | 10,00 | 15,30 | 2,13 |
| 2010 | 335 | 18,97 | 17,14 | 10,79 | 2,04 | | 2020 | 842 | 13,34 | 9,14 | 13,27 | 1,77 |
| 2011 | 447 | 17,78 | 14,72 | 8,85 | 1,58 | | 2021 | 891 | 14,57 | 9,90 | 16,75 | 2,43 |
| 2012 | 449 | 15,60 | 12,30 | 9,33 | 1,45 | | 2022 | 933 | 15,54 | 10,13 | 12,95 | 2,01 |
| 2013 | 466 | 14,38 | 10,65 | 11,93 | 1,71 | | 2023 | 871 | 13,72 | 8,85 | 11,66 | 1,60 |
| 2014 | 510 | 13,89 | 10,58 | 13,01 | 1,81 | | **2024** | 900 | **11,98** | **7,96** | 14,18 | 1,70 |
| 2015 | 536 | 13,94 | 11,20 | 12,11 | 1,68 | | 2025 | 932 | 13,07 | 8,67 | 13,89 | 1,82 |
| 2016 | 592 | 12,96 | 10,88 | 13,20 | 1,71 | | **2026** | 924 | **14,17** | 9,42 | 14,21 | 2,01 |
| 2017 | 693 | 14,09 | 10,67 | 15,23 | 2,15 | | | | | | | |

Chu kỳ rõ ràng: đáy **2024 (11,98%)** → hồi phục 2 năm liên tiếp → **14,17% (2026)**. Đây là lý do
phân vị 3 năm cao gần kịch trần: 3 năm gần nhất (2023-2026) chính là đáy chu kỳ + đường đi lên.
**Số hiện tại vẫn thấp hơn mọi năm 2008-2013.**

⚠️ Trôi thành phần: số mã hợp lệ tăng 150 → 924. Cột "ROE trung vị" giảm dần chủ yếu vì rổ nở ra
phía mã nhỏ, không hẳn vì doanh nghiệp xấu đi. **Cột ROE top-100 (§A.2.2) là cột duy nhất so sánh
xuyên thời đại được** — và nó cho phân vị 2008+ là 76,3, không phải 59,9.

---

## A.3 Histogram

Hình: `mike/agents/Taylor/research/roe_market_histogram_20260729.png` (3 panel).
Bảng bucket đầy đủ ở `exp_roe/hist_*.csv`. Bản rút gọn:

### A.3.1 Chuỗi thời gian ROE gộp — 2008+ vs 3 năm gần nhất (bước 0,5pp)

| Bucket ROE gộp (%) | 2008+ số phiên | % | 3 năm số phiên | % |
|---|---|---|---|---|
| 11,5–12,0 | 144 | 3,1 | 144 | **19,3** |
| 12,0–12,5 | 139 | 3,0 | 103 | 13,8 |
| 12,5–13,0 | 344 | 7,4 | 142 | **19,0** |
| 13,0–13,5 | 488 | 10,5 | 118 | 15,8 |
| **13,5–14,0** | **873** | **18,9** | 134 | 17,9 |
| 14,0–14,5 | 622 | 13,4 | 61 | 8,2 |
| **14,5–15,0 ⟵ hiện tại 14,61** | 589 | 12,7 | **45** | **6,0** |
| 15,0–16,0 | 411 | 8,9 | 0 | 0,0 |
| 16,0–17,0 | 299 | 6,4 | 0 | 0,0 |
| 17,0–18,0 | 336 | 7,3 | 0 | 0,0 |
| 18,0–19,0 | 157 | 3,4 | 0 | 0,0 |
| 19,0–20,0 | 229 | 4,9 | 0 | 0,0 |

**Hình dạng**: phân phối 2008+ **lệch phải** (skew +0,87) — đuôi dài về phía ROE cao 16-20% là di sản
2008-2012. Hiện tại 14,61% nằm ngay **đỉnh mode** của phân phối dài hạn (bucket 13,5-15,0 chiếm 45%
số phiên) ⇒ **không phải giá trị đuôi theo thang lịch sử.** Ngược lại, trên cửa sổ 3 năm nó là
bucket **cao nhất từng chạm** (0 phiên nào vượt 14,67%) ⇒ **là giá trị đuôi theo thang 3 năm.**
Toàn bộ mâu thuẫn "phân vị 60 vs phân vị 98" nằm gọn trong hai dòng này.

### A.3.2 Mặt cắt ngang ROE từng mã, quý gần nhất (N=1.090 mã, bước 2pp)

| Bucket ROE (%) | Số mã | % | | Bucket | Số mã | % |
|---|---|---|---|---|---|---|
| < −20 | 21 | 1,9 | | 12–14 | 71 | 6,5 |
| −20…−10 | 20 | 1,8 | | 14–16 | 75 | 6,9 |
| −10…−2 | 34 | 3,1 | | 16–18 | 51 | 4,7 |
| −2…0 | 37 | 3,4 | | 18–20 | 30 | 2,8 |
| **0–2** | **112** | **10,3** | | 20–24 | 63 | 5,8 |
| **2–4** | **107** | **9,8** | | 24–28 | 44 | 4,0 |
| 4–6 | 93 | 8,5 | | 28–32 | 22 | 2,0 |
| **6–8** | **98** | **9,0** | | 32–36 | 13 | 1,2 |
| 8–10 | 88 | 8,1 | | 36–40 | 2 | 0,2 |
| 10–12 | 80 | 7,3 | | ≥ 40 | 29 | 2,7 |

Thống kê: mean (winsor ±100%) **9,37%** · median **8,41%** · std (winsor) **16,90%** ·
skew (winsor) **−1,61** · **10,3% số mã lỗ** · **15,9% số mã có ROE > 20%** ·
ngũ phân vị p05 −6,06 · p25 3,01 · p50 8,41 · p75 15,37 · p95 29,64.
(Thô, không winsor: std 134% và skew −28 — hoàn toàn do vài mã vốn chủ gần cạn; **đừng trích số thô**.)

**Hình dạng**: đơn đỉnh, **mode ở 0-4%**, đuôi trái mỏng-nhưng-thật (10% mã lỗ), đuôi phải dày hơn
(2,7% mã ROE ≥40%). Gộp 3 năm gần nhất (N=13.253 quan sát mã-quý) hình dạng **gần như y hệt**
(median 7,02%, 14,2% mã lỗ) ⇒ **mặt cắt hiện tại không bất thường**; toàn bộ chuyển động chu kỳ nằm
ở nhóm vốn hoá lớn, không ở phân phối chung.

---

## A.4 GO/NO-GO — có nên đưa ROE vào làm chỉ báo bổ sung cho market-state?

### **VERDICT: NO-GO.** Không wire ROE-cycle-level thành gate/tilt/cảnh báo mới cho DT5G hay CAPIT.

Bốn lý do, xếp theo sức nặng. Lý do #1 tự nó đã đủ để đóng.

---

### A.4.1 (Quyết định) ROE thị trường **không phải biến mới** — nó là đồng nhất thức của PE và PB

```
ROE_gộp = Σearn/Σbook = (Σmcap/PE_gộp) / (Σmcap/PB_gộp) = PB_gộp / PE_gộp
```

Kiểm chứng số học trên **toàn bộ 4.631 phiên**, cùng một rổ mã:

| Kiểm định | Kết quả |
|---|---|
| max \|ROE_gộp − PB_gộp/PE_gộp\| | **1,39 × 10⁻¹⁶** (= sai số dấu phẩy động) |
| Hồi quy log(ROE) ~ log(PE) + log(PB) | **R² = 1,00000000**, β = [0,000 · **−1,000** · **+1,000**] |
| R²(fwd 12M ~ PE+PB) vs R²(fwd 12M ~ PE+PB+ROE), mức log, mẫu không chồng lấp | **0,4582 vs 0,4582 — bằng nhau tuyệt đối** |

Nói thẳng: đội đã có PE và có PB (§1 báo cáo chính). **Thêm ROE vào là thêm cột thứ ba được tính ra
từ hai cột đầu.** Không phải "đa cộng tuyến cao" — là **đa cộng tuyến hoàn hảo theo định nghĩa**.
Mọi "xác nhận" mà ROE mang lại đều là PE và PB nói lại lần nữa.

**Sắc thái cần nêu, không giấu:** đồng nhất thức đúng ở dạng **mức**. Ở dạng **hạng** (percentile
point-in-time, xếp hạng riêng từng biến — phép biến đổi đơn điệu nhưng **phi tuyến**), phân vị ROE
*không* còn là hàm tuyến tính của hai phân vị kia, nên R² có nhích: 0,3624 ({PE,PB}) → 0,3836
({PE,PB,ROE}). **Đó là lợi ích của phép biến đổi, không phải thông tin kinh tế mới** — và +0,02 R²
trên N=15 quan sát là nhiễu, không phải phát hiện.

### A.4.2 Sức dự báo đơn biến: **có dấu hiệu, nhưng chết ngay khi tính đúng cỡ mẫu**

Cỡ mẫu thật = **quan sát KHÔNG chồng lấp**: 1 điểm cuối tháng 7 mỗi năm, forward 12M không đè lên
nhau ⇒ **N = 15 năm (2010-2024)**. (IC tính trên ~3.900 *ngày* chồng lấp cho ra những con số to như
−0,51; chúng **không có ý nghĩa thống kê**, chỉ dùng để xem dấu.)

| Tín hiệu | N | ρ(Spearman) với fwd 12M | p thô | p Bonferroni | Qua BH 5%? |
|---|---|---|---|---|---|
| **ROE_gộp, phân vị mở rộng** | 15 | **−0,621** | **0,0134** | 0,161 | ❌ |
| ROE_gộp, phân vị mở rộng → min-DD 12M | 15 | −0,479 | 0,0711 | 0,853 | ❌ |
| ROE_gộp, phân vị 3 năm | 13 | −0,505 | 0,0780 | 0,936 | ❌ |
| PE, phân vị mở rộng → min-DD 12M | 15 | +0,357 | 0,191 | 1,000 | ❌ |
| PB, phân vị mở rộng | 15 | −0,275 | 0,321 | 1,000 | ❌ |
| PE, phân vị mở rộng | 15 | −0,011 | 0,970 | 1,000 | ❌ |

12 kiểm định (6 tín hiệu × 2 mục tiêu). Ngưỡng Bonferroni 5% = **0,0042**. **Không tín hiệu nào
qua Bonferroni, không tín hiệu nào qua Benjamini-Hochberg.** Đúng chuẩn multiple-testing discipline
đội đã chốt 2026-07-05.

Điều đáng ghi nhận: **ROE là biến đơn tốt nhất trong bộ** (ρ=−0,62, R² đơn biến 0,25 vs PE 0,00 và
PB 0,12) — dấu đúng chiều kinh tế (ROE cao → lợi nhuận forward thấp). Nhưng "tốt nhất trong 6 biến
được thử trên 15 quan sát" **chính là định nghĩa của lựa chọn quá khớp**. p=0,013 thô trở thành 0,16
sau khi tính đúng số phép thử.

### A.4.3 Base rate có điều kiện: các đợt ROE cao trong lịch sử — **6 đợt, và 2 ca xấu là cùng một năm**

Liệt kê **mọi** đợt ROE ở phân vị 3 năm ≥ 0,90 (gap >21 phiên = đợt mới):

| Đợt | n phiên | ROE lúc bắt đầu | fwd 12M | Đáy sâu nhất 12M | Kết cục |
|---|---|---|---|---|---|
| 2017-05-03 → 05-12 | 8 | 14,44% | **+42,7%** | −0,1% | lành |
| 2017-11-01 → 2018-04-27 | 98 | 14,62% | +9,7% | −1,1% | lành |
| 2018-08-01 → 10-31 | 63 | 14,94% | +1,2% | −7,8% | lành |
| 2021-08-02 → 11-17 | 76 | 16,84% | −4,6% | −12,5% | điều chỉnh |
| **2022-02-07 → 02-23** | 13 | 15,62% | **−29,0%** | **−39,1%** | **bear** |
| **2022-04-20 → 05-23** | 22 | 15,72% | **−24,7%** | **−34,1%** | **bear** |
| **⟶ 2026-04-16 → 07-28 (hiện tại)** | 67 | 13,97% | chưa đủ | chưa đủ | — |

2/6 đợt dẫn tới bear = 33% (vs vô điều kiện 19-25%). **Nhưng cả hai đều là năm 2022, cùng một chế độ
thị trường** ⇒ số sự kiện bear **thật sự độc lập = 1**. Với 1 sự kiện, bootstrap theo episode cho
CI90 rộng đến vô nghĩa (**[18%, 60%]** cho điều kiện phân vị ≥p90). Đây đúng là cái bẫy cỡ mẫu mà
§2.1 báo cáo chính đã cảnh báo.

Tệ hơn: kiểm định biên "trong dải PE hiện tại **và** ROE phân vị-3Y ≥0,8" cho ra `P(bear)=100%`,
CI90 = [100,100] — nghe như tín hiệu vàng, thực chất là **N_episode = 1** (chỉ 2022 có forward data).
**Con số 100% đó phải bị vứt bỏ, không được trích dẫn.**

### A.4.4 Giả thuyết mean-reversion cũng không đứng vững ở cỡ mẫu thật

Giả thuyết hợp lý (và là cơ sở duy nhất để ROE có giá trị *độc lập*): ROE cao → sẽ đảo về trung bình
→ E giảm → PE tự động đắt lên. Kiểm định trên **độ lệch cục bộ** `roe_gap` = ROE − TB trượt 5 năm
(khử xu thế thế kỷ):

| Giai đoạn | Chân trời | ρ trên dữ liệu ngày (chồng lấp) | ρ trên 1 điểm/năm | p |
|---|---|---|---|---|
| 2010+ | 252 phiên | −0,353 (N=3.624) | **−0,146** | **0,603** |
| 2010+ | 504 phiên | −0,469 (N=3.372) | **−0,218** | **0,455** |
| 2014+ | 252 phiên | −0,423 (N=2.882) | **−0,091** | **0,779** |
| 2014+ | 504 phiên | −0,553 (N=2.630) | **−0,164** | **0,631** |
| 2018+ | 252 phiên | −0,600 (N=1.886) | **−0,190** | **0,651** |

Khoảng cách giữa hai cột ρ là bài học chính: **toàn bộ vẻ "mean-reversion mạnh" đến từ chồng lấp cửa
sổ.** Khi mỗi năm chỉ đóng góp 1 quan sát, hiệu ứng còn −0,09…−0,22 với p 0,46-0,78 — **không phân
biệt được với 0**. `roe_gap` hiện tại chỉ **+0,75pp** (14,61% vs TB trượt 5 năm 13,85%) — độ lệch nhỏ,
không phải cực trị.

---

## A.5 Hệ quả cho báo cáo chính: "PE rẻ nhờ E đỉnh" đáng lo tới mức nào?

Câu §1.3 bản chính — *"nếu biên lợi nhuận mean-revert, PE 12,4 sẽ tự động biến thành 15-16"* — là
**quá bi quan**. Định lượng đúng (giá **không đổi**, chỉ E về mức chuẩn ⇒ PE ngụ ý = PB hiện tại / ROE chuẩn):

| Kịch bản ROE | ROE | PE ngụ ý | Chênh vs PE hiện tại 12,39 | Phân vị PE đó trong 10 năm |
|---|---|---|---|---|
| ROE giữ nguyên | 14,60% | 12,39 | — | 15,6 |
| **về trung vị 5 năm** | 13,80% | **13,12** | **+5,9%** | 24,5 |
| **về trung vị 10 năm** | 13,78% | **13,14** | **+6,0%** | 24,6 |
| về p25 của 10 năm | 13,12% | 13,79 | +11,3% | 34,1 |
| về p05 của 10 năm | 11,98% | 15,11 | +21,9% | 63,0 |
| về mức thấp nhất 10 năm | 11,58% | 15,63 | +26,1% | 74,9 |

**Kịch bản trung tâm: PE 12,4 → 13,1, tức +0,7 điểm.** Vẫn nằm ở phân vị ~25 của 10 năm — **vẫn rẻ**.
Mức "PE 15-16" đòi hỏi ROE rơi xuống **p05 hoặc mức thấp nhất 10 năm**, tức là kịch bản đuôi ~5%,
không phải kịch bản cơ sở. Rủi ro "E đỉnh" là **thật nhưng nhỏ hơn nhiều so với cách bản chính đã
diễn đạt** — đây là đính chính có ý nghĩa với người đọc.

Và quan trọng: **"PE chuẩn hoá theo chu kỳ" = PB / ROE_chuẩn = PB đổi đơn vị.** Chỉ số đo đúng cái
user đang lo lắng **đã có sẵn và đã báo ở §1.2: PB, phân vị 51 (2008+) / 66 (3 năm).** Không cần
chỉ báo mới nào cả.

---

## A.6 Nếu vẫn muốn dùng ROE — dùng thế nào cho đúng

NO-GO là với việc **wire vào hệ ra quyết định**. ROE vẫn có 2 chỗ dùng hợp lệ:

1. **Số báo cáo/diễn giải (nên làm, chi phí ~0)**: thêm dòng "ROE gộp + phân vị 3Y/10Y" vào báo cáo
   macro-view định kỳ, **chỉ để giải thích tại sao PE và PB lệch nhau** — đúng vai "cầu nối" ở §1.3.
   Không có ngưỡng, không kích hoạt hành động. Không cần quant-skeptic vì không đổi hành vi hệ thống.
2. **Nếu sau này muốn một lăng kính định giá bền chu kỳ** thì ứng viên đúng là **PB** (đã tồn tại,
   đã đo, không cần biến mới), **không phải ROE**. Kể cả vậy, PB đơn biến cũng chỉ đạt ρ=−0,275
   (p=0,32) trên 15 năm độc lập ⇒ **cũng chưa đủ chuẩn wire**. Muốn theo đuổi thì phải là một sprint
   riêng, và phải qua quant-skeptic.

**Cái KHÔNG nên làm** (nêu rõ để lần sau không ai làm lại): đặt ngưỡng kiểu "ROE phân vị 3Y ≥0,9 →
hạ 1 bậc phân bổ". Ngưỡng đó khớp đẹp lịch sử **chỉ vì nó trỏ vào 2022**, và nó **đang bật ngay lúc
này** (phân vị 98,4) — tức là sẽ cắt giảm phân bổ ngay trong kỳ CAPIT đang giải ngân, dựa trên bằng
chứng gồm **đúng một** sự kiện bear độc lập.

---

## A.7 Giới hạn phương pháp (phụ lục này)

1. **Trôi thành phần** — như §5.3 bản chính. Đã giảm thiểu bằng rổ top-100 kích thước cố định (§A.2.2),
   và đó là lý do phân vị 2008+ nên đọc theo cột top-100 (76,3) hơn là cột rổ toàn bộ (59,9).
2. **PE>0 làm rơi doanh nghiệp lỗ** khỏi cách đo #1 ⇒ thiên lệch sống sót, và thiên lệch này **thay đổi
   theo chu kỳ** (năm xấu nhiều mã lỗ hơn ⇒ bị loại nhiều hơn ⇒ ROE gộp trông đẹp giả). Đã đo trực
   tiếp bằng cách #2 (gồm cả mã lỗ): chênh **−0,39pp** hiện tại, tỷ lệ mã lỗ 15,1% (đỉnh 24,0% ở
   2023Q4). Nhỏ, nhưng có thật — **đừng dùng cách #1 để so hai năm cách xa nhau**.
3. **Trộn vintage quý** ở mặt cắt ngang: mỗi mã lấy bản ghi tài chính mới nhất, nên rổ hiện tại lẫn
   2026Q1 và 2026Q2 (độ trễ công bố khác nhau giữa các mã). Chấp nhận được cho thống kê mô tả,
   **không** dùng cho so sánh mã-với-mã chính xác.
4. **Điểm neo PIT**: cách #2 dùng `Release_Date` (ngày công bố) chứ không phải ngày kết thúc quý ⇒
   không nhìn trước. Cách #1 kế thừa cột PE/PB đã ghép sẵn trong `tav2_bq.ticker`; giả định các cột
   này đã tôn trọng độ trễ công bố **chưa được kiểm chứng độc lập trong sprint này** — nếu chúng ghép
   theo ngày kết thúc quý thì phân vị 3Y có sai lệch nhỏ theo hướng lạc quan.
5. **Chéo kiểm với cột báo cáo**: ROE tự tính (NP_TTM/vốn chủ) vs cột `ROE_Trailing` của
   `ticker_financial`: N=1.075, **corr 0,896**, sai số tuyệt đối trung vị **0,0045** (0,45pp). Khớp tốt;
   phần lệch nằm ở các mã vốn chủ nhỏ/biến động.
6. **Không có backtest lợi nhuận, không có thay đổi production nào được đề xuất** ⇒ đúng như bản
   chính, **không cần quant-skeptic**. Nếu ai đó muốn lật NO-GO này thành GO, đó là lúc bắt buộc phải
   qua quant-skeptic + DSR/PBO trước khi wire.

---
---

# PHỤ LỤC B — ĐÍNH CHÍNH: P/B "đắt" là ảo giác do **một mã duy nhất (VIC)**

**Ngày dữ liệu: 2026-07-28** · job `Taylor_20260729_050632` · Taylor (Quant)
**Nguồn gốc: user nghi ngờ rổ top-100 bị VIC bóp méo (thread 1525112292159651940); Mike query độc
lập xác nhận nghi ngờ có cơ sở. Phụ lục này kiểm tra lại TOÀN BỘ chuỗi lịch sử, không chỉ snapshot.**
**Loại: RESEARCH / đính chính báo cáo — KHÔNG wire production, không cần quant-skeptic.**

---

## B.0 Kết luận ngắn — **kết luận cũ về P/B ĐÃ BỊ LẬT**

| | Bản gốc §1.2 (cap-weighted, có VIC) | Đo bền với outlier |
|---|---|---|
| Phân vị PB, 3 năm | **65,6** → "đắt hơn 2/3 lịch sử 3 năm" | **0,4 – 27,0** → **rẻ nhất/gần rẻ nhất 3 năm** |
| Phân vị PB, 10 năm | 38,7 | **1,8 – 17,6** |
| Phân vị PB, 2008+ | 51,0 | **13,5 – 35,2** |

**Câu §1.3 của bản chính — "PE và PB không nói cùng một câu chuyện" — là SAI.** Sau khi khử méo,
**PE và PB nói CÙNG một câu chuyện: rẻ.** Cái "không nói cùng câu chuyện" thực chất là VIC nói một
câu chuyện riêng của nó.

Ba con số làm rõ quy mô:

1. VIC chiếm **20,17%** vốn hoá rổ top-100, PB riêng **10,80** (PE riêng **142,5**).
2. Bỏ VIC ra: PB top-100 rơi từ **2,028 → 1,683** (−17,0%); PE top-100 rơi **12,93 → 10,51** (−18,7%).
3. PB của **mã điển hình** (trung vị equal-weight của top-100) = **1,511**, ở **phân vị 0,4 của 3 năm** —
   tức gần như là mức rẻ nhất trong 3 năm qua.

⚠️ **Nhưng đọc cho đúng sắc thái**: 2,028 **không phải con số sai**. Nhà đầu tư mua đúng rổ cap-weighted
thực sự đang trả P/B 2,03. Câu đúng là: **"chỉ số đắt lên vì VIC, còn cổ phiếu điển hình thì rẻ"**, chứ
không phải "P/B 2,03 là số bịa". Sai lầm của bản gốc là **dùng một con số cap-weighted để trả lời câu
hỏi "thị trường có đắt không"** trong khi nó đã trở thành thước đo của một cổ phiếu.

---

## B.1 Phương pháp & kiểm chứng tái lập

Kéo lại panel **per-ticker, từng phiên, 2008-01-01 → 2026-07-28** (`tav2_bq.ticker`), giữ nguyên
định nghĩa đã công bố ở §1.1: `mcap = Price × OShares` · `book = BVPS × OShares` · rổ = 100 mã vốn hoá
lớn nhất mỗi phiên trong số mã có `PB>0, OShares>0, Price>0`. **463.102 dòng, 4.633 phiên.**

**Kiểm chứng tái lập trước khi kết luận bất cứ điều gì:**

| Kiểm định | Kết quả |
|---|---|
| PB rổ-toàn-bộ dựng lại vs chuỗi cũ (`agg_pepb.csv`) | corr = **1,00000000**, sai lệch tối đa **3,1×10⁻¹⁵**, số mã khớp **100% số phiên** |
| PB top-100 dựng lại vs chuỗi cũ | corr = **1,0000**, sai lệch trung vị ~0, tối đa 0,029 (chỉ ở vài phiên 2011/2019 do thứ tự xếp hạng khi bằng điểm) |
| Giá trị hiện tại | trùng khít tới 6 chữ số thập phân (2,028472 / 1,803128) |

⇒ Panel mới **là cùng một chuỗi** với bản đã báo cáo. Mọi chênh lệch dưới đây là do **phương pháp tổng
hợp**, không phải do dữ liệu khác.

**Xử lý dữ liệu hỏng**: 2 phiên (2025-05-04 và 2025-05-11, đều là **Chủ Nhật**) chỉ có đúng 1 bản ghi
(mã BDT, tỷ trọng 100%) — đã loại. 4.631 phiên còn lại đều có ≥95 mã. (Chuỗi cũ **có** dính 2 phiên
rác này; ảnh hưởng lên phân vị < 0,2 điểm — nêu ra để đầy đủ, không phải nguồn sai lệch.)

**Kiểm chứng dữ liệu VIC là THẬT, không phải lỗi số liệu** (query trực tiếp BQ):

| Ngày | Price | OShares | BVPS | PB | PE | mcap (tỷ VND) |
|---|---|---|---|---|---|---|
| 2024-12-31 | 40.550 | 3.823.661.561 | 42.958 | 0,944 | 16,25 | 155.049 |
| 2025-12-31 | 169.600 | 7.706.031.024 | 21.010 | 8,072 | 147,34 | 1.306.943 |
| **2026-07-28** | **213.800** | **7.762.186.429** | **19.802** | **10,797** | **142,49** | **1.659.555** |

Số cổ phiếu tăng gấp đôi trong khi BVPS giảm một nửa ⇒ **vốn chủ tổng gần như đứng yên** (164.000 →
153.700 tỷ) — đúng đặc trưng chia tách/thưởng, không phải tăng vốn thực. Toàn bộ mức PB 10,8 đến từ
**giá**: vốn hoá VIC ×10,7 trong 19 tháng. Đây là dữ liệu đúng, không phải rác.

---

## B.2 Bảng kết quả đầy đủ — 9 cách đo P/B (+ PE, ROE để đối chiếu)

Giá trị hiện tại và **phân vị lịch sử** (100 = đắt nhất). Mỗi cách đo được so với **chính chuỗi lịch sử
của nó**, không so chéo.

| Cách đo | Hiện tại | 2008+ | 10 năm | 5 năm | **3 năm** |
|---|---|---|---|---|---|
| **PB cap-weighted top-100 (BẢN ĐÃ BÁO CÁO)** | **2,028** | **50,4** | **36,2** | **56,7** | **66,8** |
| PB cap-weighted rổ-toàn-bộ (bản đã báo cáo) | 1,803 | 51,0 | 38,7 | 56,0 | 65,6 |
| — | | | | | |
| PB top-100 **EX-VIC** | 1,683 | 13,5 | **1,8** | 2,2 | **1,5** |
| PB rổ-toàn-bộ **EX-VIC** | 1,526 | 19,0 | 6,0 | 8,8 | 3,3 |
| PB top-100, **bỏ mã lớn nhất MỖI PHIÊN** (đối xứng) | 1,683 | 22,9 | 10,3 | 19,4 | **14,3** |
| PB top-100, **capped-weight 10%/mã** | 1,838 | 35,0 | 17,6 | 31,8 | **27,0** |
| PB top-100, **trimmed** (bỏ 5% PB cao + 5% PB thấp) | 1,663 | 30,3 | 2,5 | 4,1 | 0,9 |
| PB top-100, **trung vị equal-weight** (mã điển hình) | 1,511 | 35,2 | 10,2 | 5,5 | **0,4** |
| PB top-100, **trung bình equal-weight** | 2,363 | 61,7 | 35,3 | 31,8 | 24,5 |
| — | | | | | |
| PE top-100 cap-weighted | 12,93 | 40,3 | 20,3 | 37,0 | 22,6 |
| **PE top-100 EX-VIC** | **10,51** | 17,0 | 3,8 | 6,7 | **0,1** |
| ROE gộp top-100 | 15,69% | 63,5 | 79,8 | 63,9 | **97,7** |
| ROE gộp top-100 EX-VIC | 16,01% | 62,4 | 77,8 | 63,4 | **97,6** |

Đọc bảng:

- **Dòng 1 là dòng duy nhất nói "đắt".** Tám cách đo còn lại đều nằm ở nửa dưới, phần lớn ở phân vị
  một chữ số hoặc dưới 30 trên cửa sổ 3 năm.
- **Ngoại lệ đáng chú ý — `pb_ewmean` 2008+ = 61,7.** Trung bình cộng equal-weight bị kéo lên bởi đuôi
  phải (mã nhỏ PB cực cao), nên **trung vị** mới là thống kê bền đúng nghĩa; nêu ra để không giấu cột
  duy nhất còn hơi cao trong nhóm "bền".
- **ROE hầu như KHÔNG đổi khi bỏ VIC** (15,69% → 16,01%, phân vị 97,7 → 97,6). ⇒ **Toàn bộ Phụ lục A
  (NO-GO cho ROE, và cảnh báo "E đang ở đỉnh chu kỳ") vẫn đứng vững nguyên vẹn.** Điều này hợp lý:
  VIC vừa gần như không có lợi nhuận vừa có vốn chủ nhỏ so với vốn hoá, nên nó bóp méo **giá/sổ sách**
  chứ không bóp méo **lợi nhuận/sổ sách**.
- **PE cũng bị nâng, và nâng còn mạnh hơn PB theo tỷ lệ** (−18,7% vs −17,0% khi bỏ VIC), vì VIC đóng
  góp 20% vốn hoá nhưng chỉ ~0,14% lợi nhuận. PE ex-VIC = 10,51 ở **phân vị 0,1 của 3 năm** ⇒ luận
  điểm "PE rẻ" của bản chính **không những đứng vững mà còn mạnh hơn**.

**Vì sao chênh lệch lớn đến vậy dù chuỗi lịch sử ex-VIC cũng bị hạ?** Vì trong lịch sử VIC chỉ chiếm
1,6–10,4% (bảng B.3) nên chuỗi ex-VIC lịch sử gần như trùng chuỗi gốc; chỉ có **giá trị hôm nay** rơi
17%. Phân vị vì thế sụp từ 66,8 → 1,5. Đây chính là dấu hiệu định nghĩa của **méo mó do một tên duy
nhất, mới xuất hiện**.

![PB thị trường 5 cách đo](pb_exvic_20260729.png)

---

## B.3 Có mã nào KHÁC từng gây méo tương tự không? — **CÓ, và đây là câu trả lời quan trọng nhất về phương pháp**

Đây là điểm phải nói thẳng vì nó **làm dịu bớt** kết luận ở B.2: **VIC không phải trường hợp duy nhất
trong lịch sử.** Cap-weighting **luôn** phơi nhiễm với một mã siêu lớn; hôm nay là VIC, 2014 là GAS,
2012-2016 là VNM.

**Mọi mã từng chiếm >12% vốn hoá top-100 (2008+):**

| Mã | Số phiên | Từ | Đến | Tỷ trọng trung vị | Tỷ trọng max | PB trung vị | PB max |
|---|---|---|---|---|---|---|---|
| GAS | 718 | 2012-05-21 | 2015-04-27 | 15,33% | **20,95%** | 3,80 | 6,76 |
| VNM | 711 | 2011-08-02 | 2016-12-14 | 13,83% | 18,04% | 6,90 | 10,04 |
| MSN | 452 | 2011-04-21 | 2013-04-26 | 14,35% | 19,07% | 4,26 | 6,41 |
| **VIC** | **267** | 2011-03-30 | **2026-07-28** | 13,51% | **20,27%** | 7,35 | **13,09** |
| BVH | 138 | 2011-01-14 | 2012-04-09 | 13,52% | 16,23% | 4,70 | 6,13 |
| DPM | 28 | 2008-07-30 | 2008-10-31 | 12,26% | 13,20% | 4,11 | 5,05 |
| VCB | 4 | 2015-07-02 | 2015-07-07 | 12,25% | 12,55% | 3,25 | 3,27 |

Điều kiện méo mó gắt hơn — **tỷ trọng >15% ĐỒNG THỜI PB>5** (đúng hình dạng VIC hôm nay): **393
phiên-mã**, thuộc **5 mã**: GAS (149), VNM (127), VIC (81), MSN (26), BVH (10).

**Phân phối tỷ trọng mã lớn nhất:** trung vị 10,3% · p90 15,8% · p99 20,0% · **hiện tại 20,17%
(phân vị 99,4)**. Số phiên tỷ trọng top-1 ≥20%: **40 phiên, thuộc đúng 2 năm: 2014 (GAS) và 2026 (VIC)**.

**Mã lớn nhất theo năm (số bình quân trong năm):**

| Năm | Mã lớn nhất | Tỷ trọng TB | Tỷ trọng max | VIC (tỷ trọng TB / PB TB) |
|---|---|---|---|---|
| 2011 | MSN | 14,71% | 19,07% | 10,99% / 6,54 |
| 2012 | GAS | 15,03% | 16,92% | 10,49% / 5,73 |
| 2013 | GAS | 15,00% | 18,04% | 7,66% / 4,58 |
| **2014** | **GAS** | **17,61%** | **20,95%** | 6,45% / 4,27 |
| 2016 | VNM | 14,18% | 16,70% | 8,14% / 3,92 |
| 2018 | VIC | 9,22% | 10,60% | 8,74% / 5,81 |
| 2019 | VIC | 10,18% | 10,91% | 10,18% / 3,46 |
| 2021 | VCB | 7,23% | 9,57% | 7,09% / 3,06 |
| 2023 | VCB | 9,93% | 11,18% | 4,26% / 1,43 |
| 2024 | VCB | 9,21% | 10,44% | 2,98% / 1,05 |
| 2025 | VCB→VIC | 9,84% | — | 6,67% / 3,57 |
| **2026** | **VIC** | **15,94%** | **20,27%** | **15,94% / 9,18** |

**Hệ quả phương pháp — và đây là lý do phải tin cột "đối xứng" hơn cột "ex-VIC":**
So "ex-VIC hôm nay" với "ex-VIC lịch sử" **không hoàn toàn công bằng**, vì chuỗi lịch sử ex-VIC vẫn
còn nguyên GAS/VNM/MSN bên trong. Cách đo **đối xứng** — bỏ mã lớn nhất **mỗi phiên**, hoặc cap
10%/mã, hoặc trung vị equal-weight — áp cùng một quy tắc cho mọi ngày và **vẫn cho kết luận rẻ**
(3 năm: 14,3 / 27,0 / 0,4). **Đó mới là bằng chứng chính; cột ex-VIC (1,5) là cận dưới hào phóng nhất
và không nên trích dẫn một mình.**

**Đo trực tiếp mức méo mó** = tích của tỷ trọng × độ đắt = `PB cap-weighted − PB bỏ-mã-lớn-nhất`:

| | Giá trị |
|---|---|
| Hiện tại (VIC) | **+0,345 điểm PB** — phân vị **99,2** |
| Trung vị lịch sử | +0,104 |
| **Cao nhất TRƯỚC 2025** | **+0,333 — GAS, 2014-08-28** |
| Cao nhất toàn lịch sử | +0,372 — VIC, 2026-05-14 |
| Số phiên vượt +0,30 | 93 phiên, thuộc đúng 2 năm: **2014 và 2026** |

**Đây là chi tiết phải nói thẳng vì nó cắt bớt tính "chưa từng có" của câu chuyện:** mức méo mó hôm
nay (+0,345) **chỉ nhỉnh hơn kỷ lục GAS 2014 (+0,333) một chút**, không phải gấp nhiều lần. Cái *thực
sự* mới của 2025-2026 là **tỷ trọng VIC** nhảy từ dải 1,6-10,4% (2010-2024) lên 20,2%, và nó đi kèm
PB 10,8 — chứ không phải "lần đầu tiên chỉ số VN bị một mã bóp méo".

**Hệ quả trực tiếp:** vì 2014 cũng bị méo tương tự, **chuỗi lịch sử cap-weighted cũng có những đoạn bị
thổi phồng** ⇒ phân vị 66,8 vừa lấy tử số bị thổi vừa so với mẫu số có chỗ bị thổi. Chỉ chuỗi **đối
xứng** (drop-top1 / capped-10% / trung vị EW) mới sạch ở cả hai đầu — thêm một lý do nữa để tin cột
14,3 / 27,0 / 0,4 hơn cột 66,8.

**Độ lệch giữa "chỉ số" và "cổ phiếu điển hình" đang ở mức cực trị:** chênh lệch phân vị PIT-3-năm
giữa PB cap-weighted và PB trung vị = **+0,669** (0,673 vs 0,004) — **phân vị 99,4 của lịch sử**, và
chỉ 0,9% số phiên từng vượt +0,6 (rơi vào 2019, 2025, 2026). Chỉ số và cổ phiếu điển hình hiếm khi
nào lệch nhau nhiều như bây giờ.

---

## B.4 Nên dùng phương pháp nào từ nay?

**Khuyến nghị: báo SONG SONG 3 con số, không thay hẳn.** Không có một con số nào "đúng" — chúng trả
lời ba câu hỏi khác nhau:

| Con số | Trả lời câu hỏi | Hiện tại | Phân vị 3 năm |
|---|---|---|---|
| **PB cap-weighted** (giữ nguyên) | "Người mua nguyên rổ chỉ số đang trả bao nhiêu?" | 2,028 | 66,8 |
| **PB capped-weight 10%/mã** (thêm) | "Bỏ đi rủi ro tập trung một tên, chỉ số đắt hay rẻ?" | 1,838 | 27,0 |
| **PB trung vị equal-weight** (thêm) | "**Cổ phiếu điển hình** đắt hay rẻ?" — đúng câu hỏi mà đội thực sự quan tâm khi hỏi regime | 1,511 | 0,4 |

Vì sao chọn **capped-weight 10%** làm cột "bền" mặc định thay vì ex-VIC hay drop-top1:
- **đối xứng theo thời gian** (áp cùng luật cho 2014-GAS và 2026-VIC), **không cần chọn tên mã bằng tay**
  (không có bậc tự do để lỡ tay khớp dữ liệu), và **không vứt bỏ thông tin** — chỉ giới hạn ảnh hưởng.
- 10% là ngưỡng quy ước sẵn có (UCITS 5/10/40, và các "capped index" của MSCI/FTSE), **không phải tham
  số tự chọn theo dữ liệu VN** — quan trọng để tránh cáo buộc khớp-lịch-sử.
- ⚠️ Nói thẳng giới hạn: 10% vẫn là **một lựa chọn**. Với cap 5% con số sẽ còn thấp hơn, cap 15% cao hơn.
  Đây là lý do phải báo cả 3 cột chứ không thay một số đắt bằng một số rẻ khác rồi coi là chân lý.

**Không đề xuất wire bất cứ thứ gì vào production** — DT5G/CAPIT/V2.4 không đọc PB thị trường; đây
thuần tuý là số dùng cho diễn giải macro-view và báo cáo.

---

## B.5 Kết luận có đổi không? — **Định vị định giá: ĐỔI HẲN. Xác suất bear: KHÔNG ĐỔI.**

### B.5.1 Định vị định giá — ĐỔI

| | Bản gốc | Sau đính chính |
|---|---|---|
| P/E | rẻ (phân vị 11,5 / 3 năm) | **rẻ hơn nữa** (ex-VIC: 0,1 / 3 năm) |
| P/B | **KHÔNG rẻ** (65,6 / 3 năm) | **RẺ** (0,4–27,0 / 3 năm tuỳ phương pháp bền) |
| Hai chỉ báo có mâu thuẫn? | **CÓ** — "không nói cùng câu chuyện" | **KHÔNG** — cùng nói rẻ |
| Định vị tổng | "bình thường-hơi-căng" | **"rẻ theo định giá, xấu theo kỹ thuật"** |

Câu thay thế đúng cho §0: **thị trường RẺ theo cả P/E lẫn P/B đối với cổ phiếu điển hình, đang ở trạng
thái kỹ thuật xấu (dưới MA200, −12,8% từ đỉnh 52w), và chỉ số cap-weighted trông đắt hơn thực tế vì
một mã (VIC) chiếm 1/5 vốn hoá với P/B 10,8.**

### B.5.2 Xác suất bear 12 tháng — **KHÔNG ĐỔI, và đừng để bảng dưới đây bị đọc thành tín hiệu**

Chạy lại base rate có điều kiện (dải ±5% quanh giá trị hiện tại, đếm theo **episode độc lập**,
block-bootstrap 4.000 lần — đúng phương pháp §2):

| Điều kiện | N ngày | N episode | P(bear 12M) | CI90 | fwd 12M trung vị |
|---|---|---|---|---|---|
| Vô điều kiện 2008+ | 4.632 | — | 25,4% | — | +8,1% |
| PB cap-weighted ±5% (2,028) — *bản gốc* | 853 | 20 | 15,7% | **[6, 34]** | +5,3% |
| PB bỏ-mã-lớn-nhất ±5% (1,683) | 1.046 | 23 | **10,1%** | **[3, 24]** | +14,0% |
| PB capped-10% ±5% (1,838) | 1.116 | 20 | **6,9%** | **[1, 19]** | +11,9% |
| PB trung vị EW ±5% (1,511) | 761 | 17 | **27,0%** | **[2, 61]** | +9,9% |

**Đọc bảng này cho đúng: nó KHÔNG cho phép hạ ước lượng bear từ 20% xuống 7-10%.**
- Bốn cách đo cho **6,9% đến 27,0%** — **khoảng dao động rộng hơn cả khoảng cách tới base rate**.
  Nếu kết quả đảo chiều tuỳ cách đo, thì cái đang được đo là **cách đo**, không phải thị trường.
- Mọi CI90 đều phủ base rate vô điều kiện. Cột "bền nhất về mặt thống kê" (trung vị EW) lại cho con số
  **cao nhất** (27,0%), CI [2, 61] — vô nghĩa về mặt quyết định.
- N_episode 17-23, đúng cái bẫy cỡ mẫu §2.1 và A.4.3 đã cảnh báo.

⇒ **Giữ nguyên ước lượng ~20%, khoảng 10-35% của §0.** Đính chính này thay đổi **cách mô tả định giá**,
không thay đổi **phân phối xác suất kết cục**. Ai dùng phụ lục này để lập luận "định giá rẻ hơn ta
tưởng nên rủi ro thấp hơn ta tưởng" là đang vượt quá bằng chứng.

### B.5.3 Hàm ý thực tế cho đội (không phải khuyến nghị hành động)

1. **CAPIT đang giải ngân**: rổ CAPIT chọn theo washout/breadth trên `universe_pit`, **không đọc PB thị
   trường** ⇒ đính chính này **không đụng gì tới CAPIT**. Nhưng nó **loại bỏ một lý do phản đối**
   ("thị trường P/B đang đắt") nếu ai đó từng viện dẫn §1.2 để phản đối giải ngân.
2. **Cổ phiếu điển hình rẻ trong khi chỉ số không rẻ** là bối cảnh **thuận** cho các sleeve equal-weight/
   cap-nhỏ-vừa (custom30V cap 0,10/tên; BAL/LAG) và **bất lợi** cho việc lấy VNINDEX làm thước đo định
   giá. Đây là quan sát mô tả — **chưa đo, chưa backtest, không được coi là edge**.
3. **Không có thay đổi nào cho DT5G**: DT5G là gate giá/vĩ mô, không đọc PB. Không đề xuất thêm.

---

## B.6 Giới hạn của chính phụ lục này

1. **"Ex-VIC" không phải chuẩn mực trung lập** — bỏ tay một mã là một lựa chọn có bậc tự do. Đã bù bằng
   3 cách đo đối xứng (drop-top1 / capped-10% / trung vị EW) áp cùng luật cho mọi ngày; kết luận không
   phụ thuộc vào việc gọi tên VIC.
2. **Ngưỡng cap 10%, trim 5%, dải ±5% đều là quy ước** — không tối ưu hoá theo dữ liệu, nhưng cũng chưa
   quét độ nhạy đầy đủ. Kết luận "rẻ" bền qua cả 4 cách đo bền, nên rủi ro tham số thấp; **con số phân
   vị chính xác thì không** (biến động từ 0,4 đến 27,0).
3. **Rổ top-100 ex-VIC còn 99 mã** (không bổ sung mã thứ 101). Mã thứ 100 có tỷ trọng ~0,1% ⇒ ảnh hưởng
   dưới ngưỡng làm tròn.
4. **Trôi thành phần rổ** vẫn còn (như §5.3 và A.7.1) — rổ top-100 cố định kích thước đã giảm thiểu, nhưng
   bản chất doanh nghiệp trong rổ 2008 khác 2026.
5. **Vintage quý & điểm neo PIT**: kế thừa nguyên các cột `PB`/`BVPS`/`OShares` ghép sẵn trong
   `tav2_bq.ticker`; giả định các cột này tôn trọng độ trễ công bố **vẫn chưa được kiểm chứng độc lập**
   (giống A.7.4). Nếu chúng ghép theo ngày kết thúc quý thì phân vị 3 năm lệch nhẹ.
6. **Không có backtest, không có thay đổi production, không đề xuất wire** ⇒ như bản chính và Phụ lục A,
   **không cần quant-skeptic**. Nếu về sau ai muốn dùng PB (bất kể cách đo) làm gate/tilt, đó mới là lúc
   bắt buộc qua quant-skeptic + DSR/PBO.

**Tái lập**: `mike/agents/Taylor/exp_pb_exvic/` — `fetch2.py` (kéo panel) → `final.py` (9 cách đo +
phân vị + biểu đồ) → `scan.py` (quét méo mó theo mã/năm) → `baserate_robust.py` (base rate có điều kiện).
Dữ liệu trung gian: `t100_panel2.csv` (463k dòng), `pb_variants_final.csv`, `percentiles_final.csv`.
