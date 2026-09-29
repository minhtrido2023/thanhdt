# Execution alpha — GIAI ĐOẠN 1: ĐO SỰ THẬT (job Taylor_20260925_155521)

**Phạm vi:** chỉ ĐO trên dữ liệu lịch sử. Không đổi tham số thực thi, không đặt lệnh,
không đụng cron. Không đề xuất thay đổi nào.

**Kết luận một dòng:** giả định `sd = 40 bps` vừa ĐÚNG vừa SAI tuỳ thiết kế nghiên cứu —
sd thật ở mức **94,6 bps** (so sánh theo MỨC) nhưng **40,8 bps** (trong cùng phiên × mã).
Cộng với N thật = **143 cụm**, không phải 327 lệnh, **mọi biến thể pre-flight chạy lại đều ra
MARGINAL — không có biến thể nào còn GO**. Theo ranh giới cứng của dispatch, **DỪNG tại Việc 1,
không làm Việc 2**.

---

## 1. Dữ liệu và cách đo

| | |
|---|---|
| Nguồn | `data/execution_logs/dnse_raw_*.jsonl`, 84 file, 39.607 dòng |
| Trường giá | `averagePrice` + `fillQuantity` **từ chính bản ghi order của broker** (§6). Không dùng bất kỳ field ước tính nào. |
| Lọc account | `accountNo` là phép ĐẦU TIÊN áp lên mọi record (§12), ở cả `orders`, `place_order`, `cancel_order`; với `orders` còn bắt `account_no` cấp record phải khớp `accountNo` trong từng order. |
| Kết quả | **780 order phân biệt → 327 order CÓ KHỚP** (SpaceX 206 / ZaloPay 121), 38 mã, 32 phiên, 2026-07-01 → 2026-09-25, notional **4,40 tỷ VND** |
| Rớt lại | 1 order (VPB 2026-09-25) — BQ chưa sync bar hôm nay (23:45 ICT). **N phân tích = 326.** |

Script: `extract_fills.py` → `fills.csv` · `slippage.py` → `slippage.csv` · `analyse.py` → `stats.json`.

### Bẫy đã gặp và xử lý: OHLC của BQ là giá ĐÃ ĐIỀU CHỈNH
`ticker.Close` là giá điều chỉnh, `ticker.Price` là giá đóng cửa THÔ. Một fill xảy ra ở giá THÔ.
Ví dụ thật: VPB 2026-09-21 có `Close=22.570` nhưng `Price=28.450` — lệch 26%. So fill với
`Open/High/Low` chưa quy đổi sẽ sinh slippage giả hàng nghìn bps.
Cách xử lý: hệ số `adj_f = Price/Close` (nhân, một vô hướng cho cả thanh giá trong ngày),
`Open_raw = Open × adj_f`, v.v.

**Hai self-check cơ học xác nhận phép quy đổi đúng (cả hai đều 0 vi phạm / 326):**
1. Không lệnh LO nào khớp tệ hơn chính limit của nó.
2. Không fill nào nằm ngoài `[Low_raw, High_raw]` của phiên. *(Nếu quên quy đổi, riêng các fill VPB đã rơi ra ngoài.)*

### Mốc tham chiếu — vì sao chọn từng mốc (báo CẢ 4, không chọn trước 1)

| Mốc | Câu hỏi nó trả lời | Vì sao đáng tin / hạn chế |
|---|---|---|
| **prev_close (thô)** | *Implementation shortfall* đầy đủ — plan dựng tối hôm trước từ chính giá đóng cửa đó (`send_plan_report` 21:00 ICT), nên đây là **giá tại thời điểm QUYẾT ĐỊNH**. | Đúng về khái niệm nhưng chứa cả gap qua đêm, thứ đường thực thi **không điều khiển được**. |
| **open phiên (thô)** | *Arrival price* cho bot đặt ~09:05–09:15. Loại bỏ gap qua đêm ⇒ đo đúng phần thực thi CÓ THỂ cải thiện. | **Mốc chính** dùng cho mọi phân rã bên dưới. Đạt được thật (lệnh ATO khớp đúng giá mở cửa). |
| **close phiên (thô)** | "Chờ đến cuối phiên thì hơn hay kém?" | Nhiễm adverse selection: BAL mua momentum, nên close cao hơn là dấu hiệu chọn mã đúng, không phải thực thi tệ. Đọc thận trọng. |
| **limit của chính mình** | Đã tiêu bao nhiêu phần trần đuổi giá; có được cải thiện giá không. | Cơ học, không nhiễu. |
| *(range_pos)* | `(fill − Low)/(High − Low)`, đảo dấu cho lệnh bán. Không phụ thuộc phân phối; 0 = giá tốt nhất trong ngày. | Bổ trợ. |

**VWAP phiên: KHÔNG có, và không giả vờ có.** `ticker*.Trading_Value = Volume × Price` (derived) nên
`Trading_Value/Volume` trả về đúng `Price`, không phải VWAP (CLAUDE.md đã ghi bẫy này; đã xác minh lại
bằng số: VPB 9,476e11/33.308.149 = 28.450 = `Price`). `mike/data/upcom_vwap_history.csv` chỉ có UPCOM
từ 2026-08-18 — **giao 0 lệnh** với tập fill này.

---

## 2. Phân phối THẬT (con số mà phán GO đang phụ thuộc vào)

Dấu: **dương = TỆ cho mình** (mua đắt hơn / bán rẻ hơn). Đơn vị bps.

### 2a. Mức lệnh (n = 326) — **KHÔNG dùng con số này cho pre-flight**

| Mốc | mean | **sd** | skew | ex-kurt | p01 | p05 | p25 | med | p75 | p95 | p99 | min | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| vs open | 5,52 | **94,58** | −1,42 | 6,50 | −370 | −145 | 0,00 | 12,3 | 44,0 | 96,0 | 248 | −370 | 360 |
| vs prev_close | −8,75 | **148,32** | −6,95 | 65,51 | −382 | −207 | −18,8 | 17,2 | 49,3 | 98,7 | 136 | −1.526 | 192 |
| vs close | 25,86 | **143,61** | 0,35 | 3,67 | −371 | −191 | −47,4 | 31,5 | 85,7 | 216 | 522 | −529 | 583 |
| vs limit riêng | −0,26 | **2,15** | −8,73 | 79,83 | −14,4 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | −25,3 | −0,00 |

Phân phối **lệch trái mạnh và đuôi dày** (vs prev_close: skew −6,95, ex-kurt 65,5) — không phải chuẩn.
Đây là lý do mọi t-statistic dưới đây đều kèm bootstrap theo cụm, không chỉ dựa vào t.

### 2b. So với giả định `sd = 40 bps`

| Cách đo | sd đo được | so với 40 bps |
|---|---|---|
| Mức lệnh, vs open | **94,58** | **×2,36** |
| Cụm (phiên × mã), vs open | **78,47** | **×1,96** |
| **Trong cụm** (dư sau khi khử fixed-effect phiên × mã) | **40,81** | **×1,02 — trùng gần như chính xác** |

**Giả định 40 bps không sai một cách đơn giản: nó đúng cho một thiết kế GHÉP CẶP** (hai cánh A/B
trên CÙNG mã, CÙNG phiên) và sai ×2,4 cho một thiết kế so sánh theo MỨC. Bản pre-flight gốc
không khai thiết kế nào, nên số đó chưa từng là một giả định kiểm chứng được.

---

## 3. ĐẾM N CHO ĐÚNG

| Cách đếm | N | /năm (quy đổi 86 ngày lịch) |
|---|---|---|
| Order (cách đếm CŨ, **sai**) | 326 | 1.384 |
| **(phiên × mã) — ĐÚNG, dùng cho pre-flight** | **143** | **607** |
| (phiên × mã × account) | 172 | 730 |
| (phiên) | 31 | 132 |

Nhiều lệnh cùng mã cùng phiên chia sẻ MỘT cú sốc giá. Hệ quả đo được, không phải lý thuyết:

| Đại lượng | Mức lệnh | Mức cụm (phiên × mã) |
|---|---|---|
| slip vs close | mean 25,86 · **t = 3,25** | mean 1,09 · **t = 0,08** |
| range_pos_cost | 0,621 · **t = 7,94 (p<1e-13)** | 0,538 · **t = 1,67 (p = 0,096)** |

Cả hai "phát hiện" ở mức lệnh **biến mất hoàn toàn** khi đếm N trung thực. Đây đúng bài học
đã ghi từ job ORB `_052050` — lần này bắt được TRƯỚC khi báo cáo, không phải sau khi bị bác bỏ.

---

## 4. TỔNG CHI PHÍ THẬT — và một ngày duy nhất chiếm 82%

Bootstrap **theo cụm** (phiên × mã), 5.000 lần, trên tổng chi phí VND có trọng số notional:

| Mốc | Tổng chi phí 86 ngày | CI95 | P(chi phí ≤ 0) | bps trọng số notional |
|---|---|---|---|---|
| vs open | **5.949.344 VND** | [−2,17tr ; +15,04tr] | **0,076** | 13,53 |
| vs prev_close | −230.436 VND | [−8,94tr ; +7,84tr] | 0,511 | −0,52 |
| vs close | 6.348.920 VND | [−8,89tr ; +22,01tr] | 0,203 | 14,44 |
| vs limit riêng | −245.097 VND | [−0,67tr ; −0,02tr] | 1,000 | −0,56 |

**Tổng chi phí thực thi KHÔNG khác 0 một cách có ý nghĩa ở mức 5%** (P = 0,076 vs open).

**Và nó bị một sự kiện chi phối:**

| | chi phí vs open | bps trọng số |
|---|---|---|
| Toàn bộ | 5.949.344 | 13,53 |
| Bỏ riêng mã PVT | 3.203.557 | 7,45 |
| **Bỏ riêng phiên 2026-07-21** | **1.066.264** | **2,70** |

**82% toàn bộ chi phí slippage đo được đến từ MỘT phiên: 2026-07-21.** Không phải lỗi dữ liệu —
`adj_f = 1,0`, không corp action, cả hai self-check đều qua. Hôm đó PVT mở 16.650, ta mua
17.100–17.250 rải từ 09:30 đến 13:00 (cả 2 account), phiên đóng 16.300, đỉnh ngày 17.600 →
+270…+360 bps trên 5 lệnh. Đó là chi phí **đuổi giá một mã trong một ngày**, không phải mức nền.

Bỏ ngày đó ra: toàn mẫu còn **+2,50 bps, cluster t = 0,39** — tức là **không có gì**.

---

## 5. Phân rã theo nguồn — chỉ tách nơi CÓ bằng chứng (§29)

Tất cả vs open, mức cụm (phiên × mã):

| Trục | Ô | n_clu | mean bps | **cluster t** | Đọc |
|---|---|---|---|---|---|
| **Thời điểm đặt** | **≤09:15 (cửa sổ mở cửa)** | **76** | **+13,75** | **+4,98** | **CÓ THẬT** |
| | 09:15–11:30 | 66 | +14,73 | +1,55 | chưa kết luận |
| | 13:00–14:30 | 39 | −13,95 | −0,66 | chưa kết luận |
| Chiều | mua | 73 | +10,44 | +1,35 | chưa kết luận |
| | bán | 71 | +2,52 | +0,24 | chưa kết luận |
| Account | SpaceX | 111 | +2,73 | +0,35 | chưa kết luận |
| | ZaloPay | 61 | +19,31 | +1,91 | gợi ý, chưa đủ |
| Kích thước / volume ngày | mọi bucket | 4–126 | −32…+33 | \|t\| ≤ 0,89 | **không có quan hệ đo được** |
| Notional lệnh | >50 triệu | 14 | +40,06 | +1,69 | gợi ý, chưa đủ |
| | ≤50 triệu | 129 | +4,5…+12,0 | ≤ 0,98 | chưa kết luận |

### Phát hiện CHẮC CHẮN thứ nhất — cửa sổ mở cửa tốn ~14 bps, mọi lát cắt

| Lát cắt | n_clu | mean bps | t |
|---|---|---|---|
| tất cả | 76 | +13,75 | **4,98** |
| bỏ ngày 2026-07-21 | 75 | +13,93 | **4,99** |
| chỉ SpaceX | 58 | +12,23 | **4,45** |
| chỉ ZaloPay | 29 | +17,24 | **3,44** |
| chỉ MUA | 38 | +17,06 | **3,84** |
| chỉ BÁN | 38 | +10,44 | **3,21** |

**Cả chiều mua VÀ chiều bán đều tốn tiền** ⇒ loại trừ cách giải thích "thị trường trôi"
(trôi giá phải giúp một chiều và hại chiều kia). Đây là chữ ký của **vượt spread** trong phiên
khớp liên tục sáng. Độ lớn ~14 bps trên mã ~25.000 VND ≈ 35 VND < một bước giá (100 VND) — nhất
quán về độ lớn với nửa spread.

### Phát hiện CHẮC CHẮN thứ hai — ta gần như KHÔNG BAO GIỜ được cải thiện giá

**321/326 lệnh (98,5%) khớp ĐÚNG BẰNG limit của chính mình.** Chi phí cải thiện giá cộng dồn
toàn kỳ: −245.097 VND (−0,56 bps). Hệ quả: **giá khớp của ta được quyết định bởi CÔNG THỨC
ĐẶT LIMIT, gần như không phải bởi thị trường.** Mọi "execution alpha" ở đây thực chất là câu hỏi
về công thức limit, không phải về vi cấu trúc. *(Quan sát cơ học, không phải khuyến nghị.)*

### Không tách được (nói thẳng, không quy chụp)
- **Chi phí do kích thước lệnh / thanh khoản**: không có bucket nào đạt \|t\| > 0,89. Với N này,
  quan hệ size→impact **chưa đo được**, KHÔNG phải "không tồn tại".
- **Chi phí do loại lệnh**: 327/327 đều là `LO`. Không có biến thiên để đo.
- **Chi phí do đuổi giá (chase)**: không tách được khỏi "đặt limit rộng ngay từ đầu", vì
  98,5% khớp tại limit — dữ liệu hiện có không phân biệt được hai cơ chế này.

---

## 6. Ngân sách chi phí so với khoảng cách 1,5pp

Base: NAV hoạt động gộp 2 account 2026-09-25 = **1.578,9 triệu VND**.
Notional 86 ngày 4,398 tỷ → quy năm 18,67 tỷ = **11,8× NAV vòng quay**.

| Cấu phần | VND/năm | pp NAV | Backtest có mô hình hoá? |
|---|---|---|---|
| Phí môi giới thật 0,097%/chiều | 18,11tr | 1,15 | **CÓ** (backtest dùng 0,1% ⇒ hơi thừa −0,03pp) |
| Thuế bán 0,1% trên notional bán | 7,35tr | **0,47** | **KHÔNG** |
| Slippage vs open — toàn bộ | 25,25tr | **1,60** | **KHÔNG** |
| Slippage vs open — bỏ 2026-07-21 | 4,53tr | **0,29** | **KHÔNG** |
| *trong đó riêng cửa sổ ≤09:15* | 5,80tr | *0,37* | **KHÔNG** |

**Phần backtest KHÔNG mô hình hoá = 2,03pp** (tính cả ngày outlier) hoặc **0,72pp** (bỏ ra).
Khoảng 1,5pp của `CLAUDE.md` nằm **giữa hai con số này** — nhất quán, nhưng đòi hỏi biết ngày
outlier thuộc loại "sẽ lặp lại" hay "một lần".

⚠️ **Vòng quay 11,8×/năm là ước lượng CAO**: 86 ngày này gồm giai đoạn dựng danh mục ban đầu
tháng 7. Mọi con số pp NAV ở trên tỷ lệ thuận với vòng quay ⇒ đều là **cận trên**.

---

## 7. CHẠY LẠI PRE-FLIGHT — không còn biến thể nào GO

`mike/bin/rnd_preflight_power.py`, `--n-rule per-event`, `--n-trials 10` (giữ nguyên khai báo gốc).

| # | Thiết kế | mean bps | sd bps | N | obs/năm | DSR@N | N cần DSR 0,95 | **Phán** |
|---|---|---|---|---|---|---|---|---|
| A | **GỐC — toàn giả định** | 10 | 40 | 327 | 1.300 | 0,998 | 169 | ✅ GO |
| B | So theo MỨC, sd+N đo được | 6,5 | 94,58 | 143 | 607 | 0,227 | 2.198 (3,6 năm) | ⚠️ MARGINAL |
| C | như B, dùng mean trọng số | 13,5 | 94,58 | 143 | 607 | 0,552 | 512 (0,8 năm) | ⚠️ MARGINAL |
| D | **GHÉP CẶP** trong (phiên × mã), cắt ~½ chi phí | 3,0 | 40,81 | 143 | 607 | 0,244 | 1.922 (3,2 năm) | ⚠️ MARGINAL |
| E | GHÉP CẶP, cắt 100% chi phí cluster-mean | 6,5 | 40,81 | 143 | 607 | 0,628 | 412 (0,7 năm) | ⚠️ MARGINAL |
| F | GHÉP CẶP, giữ nguyên effect 10 bps gốc | 10 | 40,81 | 143 | 607 | **0,908** | 176 (0,3 năm) | ⚠️ MARGINAL |

**Phán mới: MARGINAL trên mọi biến thể. Không biến thể nào còn GO.**

Ba sai số nhân vào nhau đã tạo ra phán GO gốc:

| Tham số | Giả định gốc | Đo được | Hệ số |
|---|---|---|---|
| sd | 40 bps | 94,58 (mức) / 40,81 (ghép cặp) | ×2,36 / ×1,02 |
| N có sẵn | 327 | 143 | ÷2,29 |
| obs/năm | 1.300 | 607 | ÷2,14 |

Và một sai số thứ tư, quan trọng hơn cả ba: **effect size 10 bps không còn hợp lý.**
Không thể tiết kiệm nhiều hơn số đang trả. Chi phí cluster-mean đo được là **6,5 bps**
(2,5 bps nếu bỏ ngày outlier) ⇒ mọi kịch bản có effect ≥10 bps đã **vượt trần vật lý**.
Hàng F tồn tại chỉ để cho thấy: **kể cả giữ nguyên giả định lạc quan gốc, chỉ riêng sửa sd và N
đã đủ hạ GO xuống MARGINAL.**

---

## 8. DỪNG TẠI ĐÂY

Dispatch quy định: *"Nếu pre-flight chạy lại cho MARGINAL hoặc NO-GO thì DỪNG LẠI ở đây, báo cáo,
không làm tiếp việc 2."* Pre-flight cho MARGINAL trên mọi biến thể ⇒ **Việc 2 KHÔNG được thực hiện.**
Không liệt kê giả thuyết, không ước lượng độ lớn, không đề xuất thay đổi nào.

### n-rule / n-trials khai báo trung thực (Step 0, skill `quant-research`)
- **n-rule = per-event**, 1 quan sát = **1 cụm (phiên × mã)**, KHÔNG phải 1 order.
  Lý do: nhiều order cùng mã cùng phiên chia sẻ một cú sốc giá — đã chứng minh bằng số ở §3.
- **n-trials = 10** (giữ nguyên khai báo gốc để so sánh được). Job này thực tế đã chạy
  **4 mốc tham chiếu × 6 trục phân rã**; nếu tính trung thực số so sánh đã nhìn thì n-trials
  gần 20–30 hơn, và mọi phán ở §7 chỉ **xấu đi**. Không có biến thể nào được chọn lọc sau khi
  nhìn kết quả: 4 mốc đã khai trước khi chạy và **cả 4 đều được báo**.

### Điều kiện để mở lại hướng này
Bốn điều kiện, **cần đồng thời**, không phải chọn một:
1. Tích luỹ đủ **≥412 cụm (phiên × mã)** ⇒ thêm ~0,45 năm ở nhịp 607/năm (hàng E).
2. Thiết kế phải **GHÉP CẶP** trong cùng (phiên × mã) — chỉ thiết kế đó mới có sd 40,8 bps.
   Thiết kế so theo mức cần 3,6 năm và nên coi là không khả thi.
3. Effect kỳ vọng phải **≤6,5 bps** — trần vật lý đo được, không được khai cao hơn.
4. Phải biết ngày 2026-07-21 thuộc loại nào. Nếu là một lần ⇒ chi phí nền chỉ **2,7 bps**
   và ngay cả hàng E cũng lạc quan. Cần thêm quan sát để phân biệt, không suy đoán được từ N=1.

### Điều đã học được MIỄN PHÍ (dù hướng dừng)
- Chi phí thực thi tổng thể **không khác 0 có ý nghĩa** (P = 0,076). Câu chuyện "đang chảy máu
  vì thực thi" **không được dữ liệu ủng hộ**; phần lớn khoảng cách 1,5pp là **thuế bán
  (0,47pp — chắc chắn, cơ học, không giảm được bằng kỹ thuật thực thi)** cộng một đuôi hiếm.
- Hai sự thật cơ học chắc chắn, không cần thêm N: **98,5% khớp đúng tại limit của mình**, và
  **cửa sổ mở cửa ≤09:15 tốn 13,75 bps ổn định (t = 4,98, đúng ở mọi lát cắt)**.
  Hai điều này đúng bất kể hướng R&D có mở lại hay không.

---

## 9. Artifact

| File | Nội dung |
|---|---|
| `extract_fills.py` → `fills.csv` | 327 fill thật, lọc account theo §12 |
| `slippage.py` → `slippage.csv` | 326 fill kèm 4 mốc + range_pos + bucket thời điểm/size |
| `analyse.py` → `stats.json` | phân phối, bootstrap theo cụm, toàn bộ phân rã |
