# VN 2020 (COVID) & 2022 (SCB/Fed-hiking) Recovery Trigger — đối chứng với 2009

> Job `Taylor_20260831_040228` · 2026-08-31 · RESEARCH-ONLY, không wire production.
> Phương pháp lặp lại y hệt `vn_2009_recovery_trigger_20260831/REPORT.md` (job `Taylor_20260831_033154`):
> xác định đáy/peak thật bằng dữ liệu (không giả định), đo breadth panic (`universe_pit` D_RSI<0,30),
> đo volume/turnover inflection tách biệt khỏi đáy giá, đối chiếu lag với timeline chính sách PIT.
> Input Bobby (blind classification, KHÔNG đổi ở đây): `EP-2020-02` = `CONFIDENCE_LIQUIDITY`/`CONTAINABLE`
> (clean), `EP-2022-05` = `CONFIDENCE_LIQUIDITY`/`CONTAINABLE` (clean) — cả hai khác 2009 (`MIXED`/
> `EXTERNAL_CYCLE`). Đây chính là điểm đối chứng: N=3 case để xem 4 LEAD indicator rút ra từ 2009 có
> robust không.

## Nguồn dữ liệu

- Giá/khối lượng/Trading_Value VNINDEX daily: `data/VNINDEX.csv` (cùng nguồn đã dùng cho 2009, sạch
  hơn BQ mirror).
- Breadth oversold: `tav2_bq.ticker` JOIN `tav2_mike.universe_pit` (PIT), `D_RSI < 0.30` — công thức
  `washout_gate` giống hệt job 2009. N universe: ~1.160-1.170 (02-04/2020), ~1.246-1.254 (10/2022-02/2023)
  — lớn hơn NHIỀU so với N=228-375 của 2009 (quan trọng cho Bước 3, xem Phát hiện #A).
- Chính sách: dùng timeline PIT đã cho trong dispatch + xác minh lại 3 ngày cụ thể qua WebSearch (SBV
  official/Reuters/FocusEconomics/Central Banking — nguồn trích dưới mỗi mốc).

## Bước 1 — Đáy/peak thật (KHÔNG giả định)

### 2020 (COVID)

| Sự kiện | Ngày | Close VNINDEX |
|---|---|---|
| Peak trước crash | 2020-01-22 | 991,46 |
| **Đáy tuyệt đối** | **2020-03-24** | **659,21** |
| Peak shallow đầu tiên (trước 1 nhịp điều chỉnh -12,8%) | 2020-06-10 | 900,00 |
| Peak trước khủng hoảng KẾ TIẾP (2022) — dùng làm "peak" chính | 2022-01-06 | 1.528,57 |

**Chỉ có 1 đáy sạch, KHÔNG có sóng thứ 2 kiểu-khủng-hoảng.** Registry Bobby nhắc "giai đoạn Delta
wave Q3/2021 GDP -6,17% QoQ" nhưng thị trường KHÔNG lập đáy khủng hoảng lần 2 — chỉ số vẫn quanh
1.310-1.480 suốt Q3/Q4 2021 (xem bảng close cuối tháng dưới), một điều chỉnh -12,4% (02/07→19/07/2021,
đỉnh 1.420,27→giữa tháng) rồi tiếp tục leo. **Khác biệt cấu trúc quan trọng với 2009**: sau đáy 2020,
VNINDEX bước vào một **bull run liên tục ~22 tháng** (03/2020→01/2022) chỉ với các nhịp điều chỉnh nông
(-10% đến -14%, KHÔNG rơi vào breadth-panic mới — xem Bước 3), không giống 2009 vốn có "Wave 2 2008-2012"
tái khủng hoảng đã ghi trong `crisis-episode-clustering-reanalysis-20260830`.

Bottom→peak (đến ngay trước crisis kế tiếp 2022): **+131,88%** trong 653 ngày lịch (~21,5 tháng).
Bottom→peak (đến nhịp điều chỉnh nông ĐẦU TIÊN, ít comparable với 2009 hơn vì không phải reversal
thật): +36,53% trong 78 ngày.

### 2022 (SCB/Fed-hiking)

| Sự kiện | Ngày | Close VNINDEX |
|---|---|---|
| Peak trước decline | 2022-01-06 | 1.528,57 |
| **Đáy tuyệt đối** (trong cửa sổ dd52≤−20%, 04→11/2022) | **2022-11-15** | **911,90** |
| Drawdown đỉnh→đáy | | −40,34% |
| **Peak đảo chiều rõ ĐẦU TIÊN** (sau đó −10,2% trong 1 tháng, đúng khung "reversal rõ" như 2009 dùng
  cho mốc 22/10/2009) | **2023-09-06** | **1.245,50** |
| Peak chu kỳ dài hơn (không dùng chính, chỉ tham khảo) | 2024-06-13 | 1.301,51 |

Bottom→peak (đến peak đảo chiều rõ đầu tiên, **comparable trực tiếp với cách 2009 định nghĩa peak**):
**+36,58%** trong 295 ngày lịch (~9,7 tháng) — ngắn hơn ĐÁNG KỂ so với 2009 (+165,0%/240 ngày) VÀ so
với "peak-trước-khủng-hoảng-kế-tiếp" của 2020 (653 ngày), phù hợp việc 2022 KHÔNG có 1 bull run kéo dài
đa năm ngay sau — biên độ recovery khiêm tốn hơn nhiều.

## Bước 2 — Lag từng mốc chính sách → đáy giá

### 2020

| Mốc | Ngày | Nguồn | Lag → đáy giá (24/02→24/03) | Lag → breadth peak (23/03) |
|---|---|---|---|---|
| WHO công bố pandemic / VN ca đầu | 01-02/2020 | registry Bobby | +52 ngày (mốc rộng, không chính xác 1 ngày) | +51 ngày |
| **SBV cắt lãi suất lần 1** (refi 6,0%→5,0%, QĐ 418/QĐ-NHNN ký 16/03, hiệu lực 17/03) | **2020-03-17** | [SBV official](https://www.sbv.gov.vn/en/web/sbv_portal/w/sbv407519) | **+7 ngày** | **+6 ngày** |
| Global equity bottom (S&P 500) | 2020-03-23 | phổ biến công khai | +1 ngày | **0 ngày (TRÙNG)** |
| **Chỉ thị 16 (lockdown toàn quốc) ban hành** | 2020-03-31 | [Tilleke & Gibbins / YKVN](https://www.tilleke.com/insights/vietnam-issues-strict-social-distancing-measures-combat-covid-19/) | **−7 ngày (SAU đáy)** | **−8 ngày (SAU breadth peak)** |
| Chỉ thị 16 hiệu lực (giãn cách 01-15/04) | 2020-04-01 | như trên | −8 ngày | −9 ngày |

**Phát hiện #1 — mốc lag ngắn nhất KHÔNG PHẢI hành động chính sách VN nào cả, mà là ĐIỂM ĐẢO CHIỀU
TÂM LÝ RỦI RO TOÀN CẦU** (S&P 500 bottom 23/03), trùng CHÍNH XÁC ngày breadth panic VN đạt đỉnh. SBV cắt
lãi suất (17/03) đến TRƯỚC đáy 7 ngày — gần hơn nhiều so với 2009 (5 lần cắt lãi suất KHÔNG có phản ứng
ngay, lag 64 ngày), nhưng vẫn đến SAU điểm breadth đã bắt đầu tăng tốc panic (18-20/03 đã 24-27%
oversold trước khi SBV cắt). **Chỉ thị 16 — hành động nội địa "đúng nghĩa" nhất nhắm vào bản chất khủng
hoảng (kiểm soát dịch) — đến SAU CẢ đáy giá lẫn đỉnh breadth panic**, giống vai trò QĐ443/gói $8B của
2009 (xác nhận, không phải trigger). **Lý do cấu trúc**: 2020 là cú sốc THUẦN NGOẠI SINH không có
"nguồn gốc trong nước cụ thể" để nhắm hành động chính sách vào (khác 2009's tín dụng nội địa, khác
2022's SCB cụ thể) — nên không có ứng viên LEAD-3 kiểu "targeted domestic action" nào cho case này; thị
trường bám theo nhịp rủi ro TOÀN CẦU thay vì chờ 1 quyết định trong nước.

### 2022

| Mốc | Ngày | Nguồn | Lag → đáy giá (=breadth peak, 15/11) |
|---|---|---|---|
| Tân Hoàng Minh hủy 9 lô TP (shock_origin) | 2022-04 | registry | +7,5 tháng (~228 ngày) — quá xa, chỉ là gốc, không phải trigger phục hồi |
| **SBV nâng lãi suất lần 1** (+100bp, refi 4,0%→5,0%) | **2022-09-22** | [FocusEconomics/WMBD-Reuters](https://wmbdradio.com/2022/09/22/vietnam-central-bank-raises-policy-rates-by-100-bps/) | +54 ngày |
| **SCB "kiểm soát đặc biệt"** | **2022-10-08** | registry (CNBC/AsiaFinancial) | +38 ngày |
| **SBV nâng lãi suất lần 2** (+100bp, bảo vệ tỷ giá) | **2022-10-24/25** | [Reuters/US News](https://money.usnews.com/investing/news/articles/2022-10-24/vietnam-cenbank-raises-policy-rates-by-100-bps) | **+22 ngày** |
| Nghị định 08/2023 (nới TPDN) | 2023-03-05 | registry (Allens/KPMG) | **−110 ngày (SAU đáy)** |

**Phát hiện #2 — mốc lag ngắn nhất là ĐỢT NÂNG LÃI SUẤT LẦN 2 (bảo vệ tỷ giá, 24/10), KHÔNG PHẢI hành
động kiểm soát SCB có mục tiêu cụ thể (08/10, lag dài hơn 16 ngày).** Điều này KHÁC với kỳ vọng đơn
giản "targeted luôn thắng blanket" rút từ 2009 — nhưng có lý do cấu trúc rõ: 2022 là khủng hoảng ĐA
NHÁNH thật sự (3 nhánh độc lập: TPDN/Tân Hoàng Minh, SCB bank-run, Fed-hiking/FX — đúng như Bobby đã
phân tách), và thị trường KHÔNG bottom cho đến khi nhánh CUỐI CÙNG còn treo (áp lực FX/Fed, giải quyết
bằng đợt hike thứ 2) cũng đã hành động — dù bản thân đợt hike 2 là hành động BLANKET/vĩ mô, nó vẫn là
mốc GẦN NHẤT với đáy vì nó là nhánh rủi ro SAU CÙNG được giải toả. SCB containment (08/10) tuy là hành
động có mục tiêu cụ thể và tức thời (nhắm đúng 1 ngân hàng, "kiểm soát đặc biệt NGAY" theo Bobby), nó
CHỈ giải quyết ĐƯỢC 1/3 nhánh rủi ro — thị trường còn chờ nhánh Fed/FX xong mới bottom. Nghị định 08
(TPDN, thường được coi là "giải cứu" quan trọng nhất về mặt truyền thông) xác nhận đến SAU đáy tới 110
ngày — khớp đúng dự đoán trong dispatch, cùng vai trò "xác nhận không trigger" như QĐ443/2009.

## Bước 3 — Breadth panic & volume/turnover inflection

### Breadth oversold (%mã D_RSI<0,30, universe_pit PIT)

| Episode | Ngày đỉnh breadth | %oversold đỉnh | So với ngày đáy giá | N universe |
|---|---|---|---|---|
| 2009 (đối chứng) | 24/02/2009 | 47,6% | TRÙNG NGÀY | 228-375 |
| **2020** | **23/03/2020** | **32,9%** | **T-1 (1 ngày trước đáy giá)** | 1.160-1.170 |
| **2022** | **15/11/2022** | **48,68%** | **TRÙNG NGÀY** | 1.246-1.254 |

Cả 2020 (T-1) và 2022 (T0) đều xác nhận lại pattern 2009: **breadth panic peak khớp SÁT hoặc TRÙNG ngày
đáy giá** — capitulation kinh điển giữ vững qua cả 3 episode, KHÔNG phụ thuộc phân loại Loại-1/Loại-2.
Đây là mảnh ROBUST nhất trong toàn bộ framework.

### Phát hiện #A (mới, quan trọng) — baseline oversold KHÔNG cố định, phải chuẩn hoá theo universe size

Tính %oversold trung bình trong 1 giai đoạn THỊ TRƯỜNG BÌNH THƯỜNG (calm) ngay trước mỗi episode:

| Episode | Baseline calm (%oversold trung bình) | Peak panic | Excess (peak−baseline) |
|---|---|---|---|
| 2009 (04-05/2009, sau khi đã hồi phục) | 0,64% | 47,6% | 47,0pp |
| 2020 (01-20/02/2020, trước COVID) | 15,17% | 32,9% | 17,7pp |
| 2022 (01-02/2022, trước decline) | 6,29% | 48,68% | 42,4pp |

**Baseline "bình thường" của 2020 (15,17%) CAO HƠN 20 LẦN baseline 2009 (0,64%)** — không phải vì thị
trường 2020 xấu hơn, mà vì universe_pit N lớn hơn ~3-5 lần (nhiều mã vốn hoá nhỏ/thanh khoản thấp hơn
churn D_RSI tự nhiên nhiều hơn). **Hệ quả trực tiếp cho LEAD-1 (đã đề xuất ở job 2009): ngưỡng tuyệt đối
"<5%" để coi là 'đã lành' KHÔNG generalize** — 2020 chưa BAO GIỜ chạm dưới 9,2% trong suốt 3 tháng sau
đáy (thấp nhất 2020-06-24: 9,22%) dù thị trường đã phục hồi mạnh và rõ ràng KHÔNG còn stress; 2022 chạm
đáy 6,54% (27/01/2023) rồi dao động lại lên 8-9% nhiều tuần liền mà không bao giờ ổn định dưới 5%.
**Sửa LEAD-1: dùng ngưỡng TƯƠNG ĐỐI (số phiên để %oversold quay lại ≤ baseline calm đo riêng từng
episode), không dùng ngưỡng tuyệt đối cố định.**

### Healing speed (LEAD-1, đã sửa dùng ngưỡng tương đối)

| Episode | Đỉnh breadth | Baseline calm | Số phiên hồi phục về ≤baseline | Excess (pp) | Phiên/pp excess |
|---|---|---|---|---|---|
| 2009 | 47,6% (24/02) | ~0,6% (dùng <5% do baseline gần 0) | **10 phiên** | 47,0 | 0,21 |
| **2020** | 32,9% (23/03) | 15,17% | **12 phiên** (chạm 14,46% ngày 09/04) | 17,7 | 0,68 |
| **2022** | 48,68% (15/11) | 6,29% | **47 phiên** (chạm 6,54% ngày 27/01/2023, rồi vẫn dao động 6,5-9,6% tới ít nhất giữa 03/2023, KHÔNG bao giờ ổn định rõ ràng) | 42,4 | 1,11 |

**Phát hiện #3 — healing speed KHÔNG map theo Loại-1/Loại-2.** Cả 2020 VÀ 2022 đều được Bobby xếp
`CONTAINABLE` (giống nhau ở trục 2), nhưng 2020 lành trong 12 phiên (nhanh, gần 2009) còn 2022 mất
**47 phiên** (chậm gấp gần 4-5 lần, kể cả sau khi chuẩn hoá per-pp-excess vẫn chậm hơn 1,6-5,3 lần).
**Giả thuyết đúng hơn CONTAINABLE/EXTERNAL_CYCLE**: healing speed tương quan với **hình dạng cú sốc**
— capitulation MỘT lần sắc nét (2009: 1 tuần bán tháo cực đoan; 2020: 1 tuần sụp toàn cầu đồng bộ) hồi
phục nhanh; stress NHIỀU ĐỢT kéo dài/lặp lại (2022: TPDN 04→SCB 10→FX-hike 09-10, 3 đợt trong 7 tháng,
đúng khớp ghi chú cũ trong `crisis_margin_framework_adaptive_20260825.md` về cụm 2022 "09-28→11-16 kéo
dài liên tục KHÔNG bao giờ hồi phục hẳn") hồi phục CHẬM — bất kể containability macro cuối cùng ra sao.

### Volume/turnover inflection

**2020: KHÔNG có điểm inflection tách biệt** — khối lượng đã tăng dần liên tục TRONG suốt panic-sell-off
(150-180tr cp/phiên giữa 02/2020 → 250-310tr cp/phiên giữa 09-19/03/2020, tức là volume tăng GẤP ĐÔI đã
xảy ra TRƯỚC đáy giá, không phải sau như 2009), rồi giữ nguyên mặt bằng cao (~200-300tr cp/phiên) suốt
cả tháng sau đáy — không tìm được ngày nào day-over-day tăng ≥1,8x sau đáy giá (mức cao nhất là
06/04 = 1,54x so với 03/04). **Kết luận: LEAD-2 (volume regime-break tách biệt khỏi bottom) KHÔNG áp
dụng được cho 2020** — cú sốc toàn cầu đồng bộ hoá volume và giá cùng lúc ngay từ đầu, không có giai
đoạn "đi ngang chờ dòng tiền" như 2009.

**2022: có điểm inflection, đến GẦN NHƯ NGAY LẬP TỨC (T+1), KHÔNG lag 2,5 tuần như 2009.** Ngày đáy
15/11 (534,3tr cp) → 16/11 (881,9tr cp, +65% ngay hôm sau, giá cùng ngày +3,4%). Volume tiếp tục leo
thang qua các tuần sau (29/11: 1.050,7tr — gần gấp đôi ngày đáy; đỉnh 06/12: 1.303,6tr cp). **Phát hiện
#4 — thứ tự nhân-quả breadth→volume của 2009 KHÔNG lặp lại ở 2022**: 2009 breadth lành TRƯỚC (LEAD-1)
rồi volume mới break (LEAD-2, cách nhau 2,5 tuần); 2022 volume break gần như NGAY LẬP TỨC tại đáy trong
khi breadth vẫn mất tới 47 phiên mới lành — tức LEAD-2 (dòng tiền cam kết) ở 2022 xảy ra TRƯỚC/ĐỒNG THỜI
với LEAD-1 (breadth healed), ĐẢO NGƯỢC thứ tự so với 2009.

## Bước 4 — Tổng hợp: so sánh lag pattern 3 episode + đánh giá lại 4 LEAD indicator

### Bảng tổng hợp lag ngắn nhất mỗi episode

| Episode | Root cause (Bobby) | Containability (Bobby) | Mốc chính sách lag ngắn nhất | Lag | Có phải "targeted domestic action"? |
|---|---|---|---|---|---|
| 2009 | MIXED | EXTERNAL_CYCLE | QĐ131 (bù lãi suất 4%, hiệu lực) | +23 ngày | CÓ — targeted tín dụng |
| 2020 | CONFIDENCE_LIQUIDITY | CONTAINABLE | S&P 500 bottom (KHÔNG phải hành động VN) | 0 ngày (trùng breadth peak) | KHÔNG — không có domestic origin để target |
| 2022 | CONFIDENCE_LIQUIDITY | CONTAINABLE | SBV nâng lãi lần 2 (bảo vệ tỷ giá, blanket) | +22 ngày | KHÔNG — targeted (SCB, +38j) lag DÀI hơn blanket lần 2 |

**Trả lời câu hỏi cốt lõi của dispatch: "mốc lag ngắn nhất có LUÔN LÀ hành động nhắm trực tiếp vào
nguồn gốc khủng hoảng?" → KHÔNG, chỉ đúng 1/3 case (2009).** Bị bác bỏ rõ ràng bởi cả 2020 (không có
domestic target khả dụng — cú sốc thuần ngoại sinh) và 2022 (targeted action tồn tại nhưng KHÔNG phải
mốc lag ngắn nhất, vì đó chỉ là 1 trong 3 nhánh rủi ro độc lập — thị trường chờ nhánh CUỐI CÙNG). **Điều
kiện đúng hơn**: mốc lag ngắn nhất = hành động giải quyết **nhánh rủi ro cuối cùng còn treo** (không
nhất thiết là nhánh "nguồn gốc" ban đầu) — với khủng hoảng đơn-nhánh (2009-kiểu, dù MIXED nó vẫn được
giải quyết chủ yếu qua 1 kênh tín dụng) thì đó trùng với targeted action; với khủng hoảng đa-nhánh
(2022) thì đó có thể là bất kỳ nhánh nào, kể cả blanket; với khủng hoảng không có domestic lever
(2020, thuần ngoại sinh) thì market bám theo catalyst TOÀN CẦU thay vì chờ VN policy.

### LEAD-1..4 — mức độ ROBUST qua N=3 case

| LEAD | Nội dung gốc (job 2009) | 2020 | 2022 | Đánh giá robust |
|---|---|---|---|---|
| **LEAD-1** | Breadth panic đỉnh TRÙNG ngày đáy giá; ngưỡng lành <5% tuyệt đối | Đỉnh T-1 (khớp gần), NHƯNG không bao giờ chạm <5% (min 9,2%) | Đỉnh TRÙNG NGÀY (khớp), min chạm 6,5% rồi dao động lại | **Phần "đỉnh trùng ngày đáy": ROBUST cả 3 case.** Phần "ngưỡng lành tuyệt đối <5%": **KHÔNG robust — phải sửa thành ngưỡng tương đối theo baseline calm riêng từng episode** (đã sửa ở Phát hiện #A). Sau khi sửa, "tốc độ lành" (phiên) vẫn hữu ích nhưng biến thiên mạnh (10→12→47 phiên) — không dùng làm ngưỡng số cứng, chỉ dùng làm chỉ báo tương đối (nhanh=capitulation 1 lần, chậm=stress nhiều đợt). |
| **LEAD-2** | Volume/turnover regime-break tách biệt khỏi breadth-heal, dùng LEAD-1 làm điều kiện CẦN | 2020: KHÔNG tách biệt được — volume tăng ĐỒNG THỜI với panic-sell, không có giai đoạn "chờ" | 2022: tách biệt RÕ nhưng đến NGAY (T+1), TRƯỚC KHI breadth lành — đảo ngược thứ tự | **KHÔNG robust ở dạng gốc.** Ý tưởng "volume break là tín hiệu dòng tiền cam kết" vẫn có giá trị QUAN SÁT (cả 2020 và 2022 đều có volume tăng mạnh quanh đáy), nhưng **giả định thứ tự "LEAD-1 điều kiện CẦN trước LEAD-2"** của job 2009 bị bác bỏ trực tiếp bởi 2022 (volume break xảy ra khi breadth CÒN XA mức lành). Sửa: dùng LEAD-1 và LEAD-2 làm 2 tín hiệu ĐỘC LẬP, không ép thứ tự. |
| **LEAD-3** | Hành động tín dụng/tài khoá CÓ MỤC TIÊU CỤ THỂ lag ngắn hơn cắt-lãi-suất-rộng | Không có domestic target — catalyst là global risk sentiment | Targeted (SCB) lag DÀI hơn blanket (hike lần 2) vì đa nhánh | **KHÔNG robust ở dạng "targeted luôn thắng blanket".** Cần sửa thành: mốc lag ngắn nhất = nhánh rủi ro giải quyết SAU CÙNG (xem bảng trên) — targeted chỉ thắng khi khủng hoảng đơn-nhánh có domestic origin rõ (đúng 1/3 case, 2009). |
| **LEAD-4** | Tripwire tín dụng/thương mại/FX cảnh báo sớm 4-5 tháng trước đỉnh giá relapse | **KHÔNG kiểm tra trong job này** (cần dữ liệu credit growth/trade balance/FX black-market theo tháng 2021, ngoài phạm vi — 2020 recovery chưa từng relapse mạnh trong khung backtest hiện có nên khó test) | **KHÔNG kiểm tra trong job này** (tương tự, cần dữ liệu 2023) | Chưa test — để mở cho job sau nếu cần. |

## Giới hạn phải mang theo

1. **N=3 vẫn rất mỏng cho suy luận thống kê** — đúng tinh thần `crisis_margin_framework_adaptive`, đây
   vẫn là MÔ TẢ chi tiết 3 case, KHÔNG PHẢI kiểm định. Không tự suy rộng ngưỡng số cứng nào (kể cả các
   con số "12 phiên"/"47 phiên") thành công thức production mà không có thêm case đối chứng.
2. Peak "2022 first clean reversal" (06/09/2023) dùng cùng phương pháp phát hiện local-peak-với-DD≥10%
   như suy luận lại từ cách 2009 định nghĩa peak (22/10/2009→SBV hike 25/11 gây -14%) — nhưng 2009 job
   gốc không formalize ngưỡng số này, nên đây là 1 lựa chọn PHƯƠNG PHÁP LUẬN của job này, không phải
   tái tạo y hệt bước đã làm cho 2009.
3. 2020 KHÔNG có 1 "peak sạch" tương đương — dùng "peak trước khủng hoảng kế tiếp" (06/01/2022) làm
   proxy, đây là lựa chọn thực dụng, không phải phát hiện 1 điểm đảo chiều chính sách rõ ràng như 2009/
   2022.
4. LEAD-4 chưa kiểm chứng cho cả 2 episode (thiếu dữ liệu credit/trade/FX theo tháng trong phạm vi job).
5. Baseline "calm" dùng để chuẩn hoá LEAD-1 (Phát hiện #A) lấy từ 1 cửa sổ ngắn (1-1,5 tháng) ngay
   trước mỗi episode — có thể tự nó chưa hoàn toàn "calm" (vd 2020 baseline 15,17% cao bất thường, có
   thể phản ánh universe_pit đã bắt đầu nhiễu sớm hơn crash chính thức 1 chút, chưa điều tra sâu).
