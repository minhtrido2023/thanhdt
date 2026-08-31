# VN "Phản ứng hợp lý vs Overreaction" — khung tổng hợp 11 episode

> Job `Taylor_20260831_070702` · 2026-08-31 · Bước cuối chuỗi nghiên cứu hôm nay (dispatch từ
> Mike). Research-only, không wire production, không đổi DT5G/CAPIT.
> Input: 5 episode mới Bobby phân loại BLIND hôm nay (`vn_macro_regime_history.md`, đợt
> 2026-08-31: EP-2014-09, EP-2015-07, EP-2023-09, EP-2025-03, EP-2026-01) + 6 episode đã có sẵn
> phân tích giá/breadth chi tiết từ các job trước trong ngày (Wave1 2007-08, Wave2/3 2009-2012,
> 2018, COVID 2020, SCB/Fed 2022, 07/2026).

## Tóm tắt 1 dòng

**Có bằng chứng overreaction RÕ RÀNG ở đúng 1 case (2025-03, tariff "Liberation Day") và
underreaction (theo nghĩa cường độ panic, không phải theo nghĩa tổng dd%) ở đúng 1 nhóm case
(STRUCTURAL 2009-2012)** — KHÔNG phải kết luận chung "thị trường luôn phản ứng thái quá". Đa số
7/11 episode có phản ứng giá TƯƠNG XỨNG hợp lý với mức nghiêm trọng vĩ mô đo được.

---

## Phần 1 — Đối chiếu dữ liệu 5 episode mới (breadth, healing speed)

**Phương pháp** (giữ nguyên công thức đã lặp lại 6 lần hôm nay): `tav2_bq.ticker` JOIN
`tav2_mike.universe_pit` (PIT, `in_universe=TRUE`), oversold = `D_RSI<0,30`. Baseline calm = %
oversold trung bình trong ~5-6 tuần TRƯỚC episode. Healing = số phiên từ đỉnh breadth panic tới
lần đầu %oversold quay lại ≤ baseline (ngưỡng TƯƠNG ĐỐI, đã sửa theo Phát hiện #A của job 2020/2022
hôm nay — KHÔNG dùng ngưỡng tuyệt đối <5%).

| Episode | Baseline calm | Đỉnh breadth panic | Ngày đỉnh | Lệch vs đáy giá thật | Healing (phiên) |
|---|---|---|---|---|---|
| EP-2014-09 (OPEC oil) | 0,53% | **15,69%** | 2014-12-17 | TRÙNG NGÀY | **10** |
| EP-2015-07 (China deval) | 5,20% | **42,11%** | 2015-08-24 | TRÙNG NGÀY | **4** |
| EP-2023-09 (FX-defense/VIC-VHM) | 2,25% | **42,14%** | 2023-10-31 | TRÙNG NGÀY | **6** |
| EP-2025-03 (Liberation Day tariff) | 3,40% | **80,05%** | 2025-04-09 | TRÙNG NGÀY | **12** |
| EP-2026-01 (Credit/BĐS+oil war) | 5,06% | **47,73%** | 2026-03-09 | **−14 ngày (đi TRƯỚC đáy giá)** | 12 |

**Phát hiện chính:**
1. **4/5 episode mới xác nhận lại pattern robust đã có (breadth panic TRÙNG NGÀY đáy giá)** — đúng
   mẫu "capitulation-một-lần" của các case CONFIDENCE_LIQUIDITY sạch (2009/2020/2022 trước đó).
2. **EP-2026-01 là ngoại lệ — breadth panic đi TRƯỚC đáy giá 14 ngày**, giống mẫu STRUCTURAL
   (Wave2/3: breadth đi trước đáy giá 9 và 52 ngày, xem job 2012 hôm nay) chứ KHÔNG giống 4 case
   còn lại trong chính đợt này. Đây là bằng chứng ĐỘC LẬP (đo bằng giá, không dùng lại phân loại
   của Bobby) **CỦNG CỐ** verdict `MIXED` của Bobby cho EP-2026-01 — cơ chế "xói mòn dần" (grinding,
   giá còn drift xuống sau khi panic-selling đã xả) thay vì "cú sốc-rồi-capitulate" thuần túy.
3. **EP-2025-03 có đỉnh breadth panic CAO NHẤT trong TOÀN BỘ 11 episode phân tích hôm nay
   (80,05%)** — cao hơn cả case STRUCTURAL nặng nhất (Wave2/3 chỉ 29,5-31,7%) và cả case
   CONTAINABLE mạnh nhất trước đó (SCB 2022: 48,68%). Chi tiết ở Phần 3.

---

## Phần 2 — 2026-01 và 07/2026: hai episode tách biệt hay MỘT chuỗi chưa từng ổn định?

**Câu hỏi Bobby cờ nghi vấn**: đáy EP-2026-01 (2026-03-23) và đỉnh episode 07/2026 (2026-05-18)
cách nhau ~2 tháng — có phải thị trường "chưa bao giờ thực sự lành" giữa 2 điểm này?

### Bằng chứng breadth panic-oversold (đo trực tiếp, PIT, không suy diễn)

Kéo dữ liệu %oversold hàng ngày xuyên suốt 2026-03-20 → 2026-05-26:
- Đáy 2026-03-23: %oversold đạt đỉnh 20,85%.
- **Hồi phục THẬT**: xuống 4,98% chỉ sau 2 phiên (2026-03-25), rồi duy trì **1,4-5,4% liên tục suốt
  ~7-8 tuần** (2026-03-27 → 2026-05-18) — THẤP HƠN CẢ baseline calm trước episode (5,06%). Đây
  KHÔNG phải "chưa bao giờ lành" — theo đúng thước đo panic-oversold, đây là giai đoạn CALM THẬT,
  lành hơn cả mức bình thường trước đó.
- Chỉ bắt đầu nhích lại từ 2026-05-19 (5,96% → 10,92% ngày 05-20) — **SAU** đỉnh giá 07/2026
  (2026-05-18), tức là mở đầu đúng episode 07/2026 mới, không phải nối tiếp từ EP-2026-01.

### Bằng chứng giá (VNINDEX.csv, `data/VNINDEX.csv`)

Giá tăng ĐỀU trong toàn bộ cửa sổ: 1.591,17 (23/03 đáy) → 1.658 (25/03) → 1.694 (04/2026) →
**1.927,94 (18/05, đỉnh)** = **+21,17%**, không có nhịp rớt mạnh nào giữa chừng đáng gọi "chưa lành"
theo giá — đúng khớp số +21,17% đã ghi trong registry Bobby.

### Nhưng: bằng chứng breadth-THAM-GIA (participation) KHÁC — rally NÔNG, không rộng

Job trước trong ngày (`vn_breadth_of_prior_rally_20260831`) đã đo: **57,1% mã trong `ticker_prune`
ÂM trong 133 ngày trước đỉnh 07/2026** (cửa sổ này TRÙM cả EP-2026-01 lẫn phần đầu nhịp hồi) — tệ
hơn hẳn 2018 (45,4% mã âm cùng loại cửa sổ). Nhóm dẫn dắt chỉ số đi lên là **dầu khí họ PVN + mega-
cap (BSR/OIL/PVC/PVP/PVT/DCM/GVR/VIC)**, KHÔNG phải broad-based.

### Kết luận Phần 2 — 2 lớp bằng chứng KHÔNG mâu thuẫn nhau, chỉ đo 2 THỨ khác nhau

**Panic-oversold breadth** (đo "có đang bán tháo hoảng loạn không") nói: đây là **HAI episode
tách biệt thật** — có một giai đoạn calm-thật ~7-8 tuần ở giữa, không phải một chuỗi rơi liên tục
không ngừng nghỉ.

**Participation breadth** (đo "bao nhiêu mã thực sự tham gia hồi phục") nói: nhịp hồi 03→05/2026
**HẸP** — đa số cổ phiếu KHÔNG hồi theo chỉ số, chỉ ~10-15 mã dầu khí/mega-cap kéo. Đây chính là
kênh khớp với giả thuyết của Bobby theo một cách khác: hợp phần STRUCTURAL_ACCUMULATION tín
dụng/BĐS mà EP-2026-01 cờ (SBV chỉ cap 25% hạn mức QUÝ 1, chưa phải giải pháp cả năm) **CÓ THỂ**
chưa được giải quyết bên dưới bề mặt rally hẹp — nhưng đây LÀ MỘT GIẢ THUYẾT (đúng tinh thần Bobby
đã tự gắn cờ), không phải kết luận đã xác nhận. Xác nhận thật đòi hỏi đọc dữ liệu tín dụng/BĐS SAU
2026-03-23 bằng một dispatch macro-strategist riêng KHÔNG-BLIND, ngoài phạm vi job này.

**Đọc đúng theo kỷ luật N nhỏ**: đây là **2 sóng phân biệt với cơ chế dẫn dắt khác nhau ở nhịp
hồi** (không phải "chưa bao giờ ổn định" theo nghĩa đen), nhưng rally hẹp làm episode 07/2026 dễ
tổn thương hơn nếu nhóm dầu khí/mega-cap đảo chiều — đây là quan sát MÔ TẢ cho case cụ thể này, N=1
cặp episode liên tiếp, không tổng quát hoá thành quy luật.

---

## Phần 3 — Khung "phản ứng hợp lý vs overreaction": 11 episode

### Phương pháp — 2 trục độc lập, đối chiếu KHÔNG suy diễn vòng

**Trục nghiêm trọng vĩ mô** (Bobby, đọc BLIND, KHÔNG biết forward price) — xếp hạng thứ tự (ordinal,
5 bậc, dựa trên chính nhãn Bobby đã gắn — root cause + confidence + axis2, không tự chế thêm tiêu
chí mới):

| Bậc | Mô tả | Episode |
|---|---|---|
| **1 — nặng nhất** | STRUCTURAL, MULTI_YEAR, confidence clean | Wave1 (2007-08), Wave2/3 (2009-2012) |
| **2** | MIXED (structural đang tích luỹ + external overlay) | EP-2026-01 (ambiguous) |
| **3** | CONFIDENCE_LIQUIDITY nhưng root cause **ambiguous** (có tín hiệu trái chiều) | EP-2018-01, EP-2015-07 |
| **4** | CONFIDENCE_LIQUIDITY root cause **clean**, nhưng axis2 (containability) ambiguous | EP-2023-09, EP-2025-03 |
| **5 — nhẹ nhất** | CONFIDENCE_LIQUIDITY clean CẢ 2 trục | EP-2014-09, EP-2020-02, EP-2022-05 |

**Trục phản ứng giá THẬT** (đo trực tiếp, KHÔNG dùng lại nhãn Bobby): dd% đỉnh→đáy, đỉnh breadth
panic %, tốc độ healing (phiên). Dùng **đỉnh breadth panic %** làm thước đo CƯỜNG ĐỘ hoảng loạn
chính (sạch hơn dd% vì dd% bị nhiễu bởi ĐỘ DÀI episode — 1 case grinding-dài có thể dd sâu mà không
hề panic cấp tính; breadth panic đo đúng "có bán tháo dồn dập hay không").

### Bảng tổng hợp — sắp theo đỉnh breadth panic % (cao→thấp)

| Rank panic | Episode | Bậc nghiêm trọng | Đỉnh breadth panic | dd% | Healing (phiên) | Đọc |
|---|---|---|---|---|---|---|
| 1 | **EP-2025-03** (tariff) | **4** (nhẹ-trung, ambiguous) | **80,05%** | -18,11% | 12 | **OVERREACTION rõ nhất** |
| 2 | EP-2022-05 (SCB/Fed) | 5 (nhẹ nhất) | 48,68% | -40,34% | 47 | Overreaction có bối cảnh (xem ghi chú) |
| 3 | EP-2026-01 (Credit/BĐS+oil) | 2 (nặng) | 47,73% | -16,38% | 12 | **Tương xứng** (panic cao khớp bậc nặng) |
| 4 | EP-2023-09 (FX-defense) | 4 (nhẹ-trung) | 42,14% | -17,45% | 6 | Panic hơi cao so với bậc, nhưng healing rất nhanh (6 phiên) → nghiêng tương xứng |
| 5 | EP-2015-07 (China deval) | 3 (trung) | 42,11% | -17,50% | 4 | Panic cao vừa, healing cực nhanh → tương xứng |
| 6 | EP-2018-01 | 3 (trung) | 34,29% | -26,21% | 5 (lành SỚM rồi grind tiếp 5 tháng KHÔNG panic lại) | Panic ban đầu vừa phải, nhưng dd% + thời gian grind sau đó (155 ngày lệch) mới là dấu hiệu chính — không đơn giản overreaction/underreaction |
| 7 | EP-2020-02 (COVID) | 5 (nhẹ nhất theo domestic-axis, NHƯNG bản thân cú sốc toàn cầu rất lớn — xem giới hạn) | 32,9% | -33,51%/-35,68% | 12 | Tương xứng (cú sốc toàn cầu thật, không phải panic thái quá của riêng VN) |
| 8 | Wave2/3 leg1 (2012, STRUCTURAL) | **1** (nặng nhất) | 31,74% | -46,05%(giả)/-39,87%(thật) | 32 | **UNDERREACTION cường độ** (xem dưới) |
| 9 | Wave2/3 leg2 (2012, STRUCTURAL) | **1** (nặng nhất) | 29,52% | (cùng dd trên) | 91 | **UNDERREACTION cường độ**, healing CHẬM NHẤT (91 phiên) |
| 10 | EP-2014-09 (OPEC oil) | 5 (nhẹ nhất) | 15,69% | -19,12% | 10 | **Tương xứng nhất trong toàn bộ 11 case** — case tham chiếu "rational" |
| — | Wave1 (2007-08) | 1 (nặng nhất) | không đo (ngoài phạm vi job, universe_pit thưa/chưa verify giai đoạn này) | **-79,88%** | không đo | dd% tự nó đã tương xứng bậc 1 — không cần breadth để kết luận |

### Đọc kết quả — 3 case đáng nói cụ thể (đúng yêu cầu dispatch, không kết luận chung chung)

**1) OVERREACTION rõ nhất: EP-2025-03 (Trump "Liberation Day" tariff, 03-04/2025).** Bobby xếp
bậc 4/5 (root cause CONFIDENCE_LIQUIDITY clean, chỉ axis2 containability ambiguous vì tranh chấp
thương mại có thể tái diễn) — KHÔNG phải case nặng. Nhưng đỉnh breadth panic **80,05%** là cao NHẤT
trong toàn bộ 11 episode hôm nay, vượt xa cả case STRUCTURAL nặng nhất (Wave2/3: ~30%) và case
CONTAINABLE có bank-run thật (SCB 2022: 48,68%). Thời gian giảm chỉ **16 phiên** — nhanh và sâu bất
thường so với mức độ nghiêm trọng vĩ mô đo được (CPI/tín dụng VN không xấu đi, đây là chính sách
thương mại Mỹ nhắm vào toàn cầu, VN chỉ là 1 trong nhiều nước bị ảnh hưởng). Đây là chữ ký cổ điển
của **overreaction do tốc độ tin tức** (shock quá đột ngột để thị trường định giá dần dần), không
phải phản ánh đúng mức độ tổn hại vĩ mô thực.

**2) UNDERREACTION cường độ (không phải underreaction về tổng thiệt hại): Wave2/3 STRUCTURAL
2009-2012.** Đây là case Bobby xếp NẶNG NHẤT (bậc 1, STRUCTURAL/MULTI_YEAR) — nhưng đỉnh breadth
panic ở CẢ HAI đáy (31,74% và 29,52%) đều THẤP HƠN 6/9 episode "nhẹ hơn" khác đã đo (thấp hơn cả
2015 China-deval 42,11% hay 2023 FX-defense 42,14%, những case Bobby xếp bậc 3-4). Cơ chế: STRUCTURAL
không panic-sell dồn dập một lần — nó XÓI MÒN dần (grinding), nên breadth "mệt" và HỒI trước khi giá
chấp nhận đáy cuối cùng (lệch 9 và 52 ngày, đã ghi ở job 2012 hôm nay) — hệ quả thực tế: healing
speed CHẬM NHẤT (32 và 91 phiên) dù cường độ panic đỉnh lại THẤP — một washout-gate dựa thuần vào
`%oversold` đỉnh cao sẽ BỎ LỠ hoàn toàn dạng khủng hoảng nghiêm trọng nhất này, vì nó không bao giờ
tạo ra panic-spike đủ cao để trigger.

**3) Tương xứng nhất — case tham chiếu "rational": EP-2014-09 (OPEC oil, 09-12/2014).** Bậc nhẹ
nhất (5/5, CONFIDENCE_LIQUIDITY clean cả 2 trục — CPI/tín dụng/lãi suất huy động VN đều lành mạnh,
GDP tăng tốc, trigger hoàn toàn từ 1 quyết định OPEC bên ngoài) VÀ đỉnh breadth panic thấp nhất
(15,69%, thấp hơn TẤT CẢ 9 episode khác có dữ liệu) VÀ healing nhanh (10 phiên). Cả 3 chỉ số (bậc
nghiêm trọng, cường độ panic, tốc độ hồi) đều xếp cùng hạng — đây là case DUY NHẤT trong 11 case mà
cả 3 trục đo lường đồng thuận hoàn toàn "nhẹ" — chuẩn mực để so sánh các case khác.

### Giới hạn — kỷ luật N nhỏ, KHÔNG tổng quát hoá

1. **N=11 episode, một số bậc chỉ có 1-2 case** (bậc 2 chỉ có EP-2026-01) — bảng trên là **quan sát
   MÔ TẢ cho từng case cụ thể**, KHÔNG PHẢI tương quan đã kiểm định thống kê (không có p-value,
   không đủ N để chạy). Kết luận "case X là overreaction/underreaction" là nhận định ĐỊNH TÍNH có
   căn cứ số liệu, không phải một mô hình đã fit.
2. **dd% và breadth panic% đo 2 THỨ khác nhau, có thể mâu thuẫn nhau** (VD 2022: dd -40,34% rất sâu
   nhưng nằm trong bối cảnh Fed-hiking bear market Mỹ thật — `external_flag` FAIL cả 4 cụm theo job
   `vn_2022_2018_margin_signature_recheck` hôm nay — nên dd sâu ở đây một phần phản ánh cú sốc TOÀN
   CẦU thật, không thuần "VN overreact"). Đã ghi rõ trong cột "Đọc" thay vì gộp chung một kết luận.
3. **Wave1 (2007-08) không có breadth panic đo được trong job này** (ngoài phạm vi cửa sổ BQ query
   2014-06→2026-05 dùng hôm nay; universe_pit giai đoạn 2007-2008 chưa verify trong job này) — dd%
   -79,88% tự nó đã đủ tương xứng bậc 1, không ảnh hưởng kết luận tổng, nhưng là 1 ô trống cần biết.
4. **COVID (2020) đặt SAI vị trí nếu chỉ dùng đúng khung "domestic severity"** — Bobby xếp bậc 5
   (nhẹ nhất, vì macro NỘI ĐỊA VN hoàn toàn lành mạnh) nhưng bản thân cú sốc là đại dịch toàn cầu
   chưa từng có tiền lệ — dd -33,51% không hề "quá mức" nếu đánh giá đúng độ lớn cú sốc TOÀN CẦU,
   chỉ "quá mức" nếu chỉ nhìn thuần macro NỘI ĐỊA VN (đây chính xác là điều Bobby's registry đo —
   khung 2 trục KHÔNG bắt được "độ lớn cú sốc toàn cầu", chỉ bắt "cú sốc có xuất phát từ mất cân đối
   VN hay không"). Đọc bảng trên với hiểu biết này, không suy diễn quá tay.
5. **2018 không map gọn vào nhị phân overreaction/underreaction** — panic ban đầu (34,29%, bậc trung
   bình) lành nhanh (5 phiên) nhưng sau đó KHÔNG panic lại mà vẫn tiếp tục grind xuống thêm ~9,6%
   trong 5 tháng liên tục KHÔNG có cluster mới (theo job margin-signature-recheck hôm nay) — đây là
   dạng "phản ứng cấp tính đúng mức, nhưng suy yếu mạn tính kéo dài sau đó" — không phải một nhãn
   đơn giản nào trong 2 nhãn overreaction/underreaction.

---

## Giới hạn tổng thể phải mang theo (áp dụng CẢ 3 phần)

- Toàn bộ phân loại vĩ mô là của Bobby (macro-strategist), đọc BLIND — job này KHÔNG tự đánh giá
  lại tính đúng đắn của phân loại đó, chỉ đối chiếu dữ liệu giá/breadth với phân loại đã có.
- `universe_pit` PIT — mọi số breadth đều point-in-time, không lookahead.
- Tautology-trap: mọi số đo Phần 1-3 lấy TRỰC TIẾP từ giá/breadth của chính episode đang xét
  (không dùng return SAU episode để giải thích phản ứng TRONG episode) — đúng kỷ luật đã áp dụng
  xuyên suốt 7 job trước hôm nay.
- Đây là bước RESEARCH-ONLY cuối cùng của chuỗi hôm nay — không đề xuất wire threshold/gate mới
  vào production từ job này; nếu Mike/Taylor muốn dùng "đỉnh breadth panic %" làm 1 chỉ báo phân
  loại loại cú sốc (bổ sung cho healing-speed đã có), cần ít nhất 1 dispatch riêng để formalize +
  quant-skeptic review, N=11 hiện tại chỉ đủ cho quan sát mô tả.

## Artifact

- `breadth_query.sql` / `breadth_daily_5episodes.csv` — %oversold hàng ngày 2014-06→2026-05 (5
  episode mới + gap 2026-03→05).
- `breadth_query_2018.sql` / `breadth_daily_2018.csv` — %oversold hàng ngày 2018 (bổ sung dữ liệu
  còn thiếu cho episode đã nghiên cứu trước đó).
- `analyze_breadth.py` — tính baseline/đỉnh panic/lag/healing cho 5 episode mới.
