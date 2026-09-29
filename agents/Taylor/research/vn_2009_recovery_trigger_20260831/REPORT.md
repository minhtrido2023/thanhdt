# VN 2009 Recovery Trigger — đối chiếu timeline chính sách Bobby vs dữ liệu giá/thanh khoản thật

> Job `Taylor_20260831_033154` · 2026-08-31 · RESEARCH-ONLY, không wire production.
> Input: timeline chính sách BLIND của Bobby (`vn_macro_regime_history.md` §ADDENDUM 2026-08-31,
> `EP-2008-09`). Verdict Bobby: root cause `MIXED` (STRUCTURAL nền + external shock mới), containability
> = `EXTERNAL_CYCLE` — KHÔNG đổi ở đây, chỉ kiểm chứng bằng dữ liệu giá/thanh khoản/breadth thật.

## Nguồn dữ liệu

- Giá/khối lượng VNINDEX daily: `data/VNINDEX.csv` (ticker=VNINDEX, local, sạch hơn BQ — thử `tav2_bq.ticker`
  filter `ticker="SSI"` trước, cột `VNINDEX` mirror bị NULL rải rác cho SSI giai đoạn này nên chuyển
  sang local file, đã verify không bị lỗi NULL tương tự mà CLAUDE.md cảnh báo cho `VNINDEX_PE`).
- Breadth oversold: `tav2_bq.ticker` JOIN `tav2_mike.universe_pit` (PIT), `D_RSI < 0.30` — ĐÚNG công
  thức washout-gate của `engine_p1.py` (đã dùng trong `crisis_margin_framework_adaptive_20260825.md`).
  N ticker trong universe_pit giai đoạn này: 228 (09/2008) → 375 (12/2009), KHÔNG mỏng đến mức vô nghĩa.
- Foreign flow: **KHÔNG có cột trong `bigquery_dictionary.json`/`ticker`/`ticker_1m`** — khớp giới hạn
  Bobby đã tự khai ("FII/portfolio flow theo quý KHÔNG xác minh được vòng này"). Bước 4 của dispatch
  KHÔNG thực hiện được bằng dữ liệu định lượng trong BQ; chỉ có định tính từ addendum Bobby (FDI đăng
  ký 7 tháng 2009 ~US$10,1 tỷ, giải ngân ~US$4,6 tỷ).

## Bước 1 — Xác định chính xác đáy và peak (KHÔNG giả định)

| Sự kiện | Ngày | Close VNINDEX |
|---|---|---|
| **Đáy tuyệt đối cửa sổ 2008-09→2009-12** | **2009-02-24** | **235,50** |
| Đáy tháng gần nhất trước đó bị hiểu lầm phổ biến (cuối 2008) | 2008-12-31 | 315,62 (KHÔNG phải đáy) |
| Peak sau phục hồi | 2009-10-22 | 624,10 |
| Đảo chiều rõ (SBV nâng lãi suất 25/11/2009, ngoài cửa sổ hỏi) | 2009-11-30 | 504,10 (−14% trong tháng) |

**Phát hiện quan trọng #1**: đáy thật là **24/02/2009**, KHÔNG PHẢI cuối 2008 như nhiều giả định phổ
biến. VNINDEX tiếp tục rơi **suốt** giai đoạn SBV cắt lãi suất 5 lần (11/2008→12/2008, 14%→8,5%) —
347,05 (31/10) → 314,74 (30/11) → 315,62 (31/12) → 303,21 (31/01/2009) → đáy 235,50 (24/02/2009).
Bottom→peak: **+165,0%** trong 240 ngày lịch (~8 tháng).

## Bước 2 — Độ trễ (lag) từng mốc chính sách → đáy giá & → điểm inflection thanh khoản

Điểm inflection thanh khoản xác định ở Bước 3 = **2009-03-17** (volume nhảy vọt, xem chi tiết dưới).

| Mốc chính sách | Ngày | Lag → đáy giá (24/02) | Lag → inflection thanh khoản (17/03) |
|---|---|---|---|
| Lehman sụp đổ | 15/09/2008 | +162 ngày | +183 ngày |
| Rate-cut sequence hoàn tất (QĐ3161, 10%→8,5%) | 22/12/2008 | +64 ngày | +85 ngày |
| QĐ131 **ký** (gói bù lãi suất 4%) | 23/01/2009 | +32 ngày | +53 ngày |
| **QĐ131 hiệu lực** | **01/02/2009** | **+23 ngày** | **+44 ngày** |
| Lãi suất cơ bản chạm đáy 7%/năm | ~02/2009 | +23 ngày | +44 ngày (cùng mốc) |
| QĐ443 (mở rộng bù lãi suất trung-dài hạn) | 04/04/2009 | **−39 ngày** (SAU đáy) | **−18 ngày** (SAU inflection) |
| Công bố quy mô đầy đủ gói kích thích ~8 tỷ USD | ~giữa 04/2009 | **−50 ngày** (SAU đáy) | **−29 ngày** (SAU inflection) |

**Phát hiện #2 — mốc có lag NGẮN NHẤT và rõ ràng nhất: QĐ131 hiệu lực (01/02/2009) + lãi suất chạm
đáy 7% cùng tháng.** Đáy giá xảy ra 23 ngày sau, đúng trong khung "vài tuần transmission" hợp lý cho
một gói tín dụng trực tiếp. Ngược lại:
- **5 lần cắt lãi suất (10-12/2008) KHÔNG tạo phản ứng ngay** — chỉ số RƠI XUYÊN SUỐT toàn bộ chuỗi
  cắt lãi suất và còn rơi tiếp 2 tháng sau khi cắt xong. Cắt lãi suất NGÂN HÀNG-RỘNG (blanket) không
  phải trigger, chỉ là điều kiện nền.
- **QĐ443 và công bố quy mô đầy đủ gói kích thích (04/2009) đều đến SAU khi đáy VÀ đà phục hồi thanh
  khoản đã xác nhận** — đây là hành động XÁC NHẬN/MỞ RỘNG một xu hướng đã bắt đầu, KHÔNG PHẢI trigger
  khởi phát. Tại thời điểm QĐ443 ban hành (04/04), VNINDEX đã ở 322,40 (07/04), tăng +37% từ đáy.

## Bước 3 — Breadth panic & thanh khoản: dòng tiền DẪN DẮT hay ĐUỔI THEO giá?

### Breadth oversold (%mã D_RSI<0,30, universe_pit PIT) quanh đáy

| Ngày | %oversold | Ghi chú |
|---|---|---|
| 18-20/02/2009 | 27,8%→29,8% | tăng tốc panic |
| 23/02/2009 | 40,9% | |
| **24/02/2009** | **47,6% (ĐỈNH breadth panic)** | **TRÙNG CHÍNH XÁC ngày đáy giá (235,50)** |
| 25/02/2009 | 23,0% | rơi mạnh — panic đã xả xong |
| 05-06/03/2009 | 6,3-6,7% | gần hết oversold |
| 10-20/03/2009 | 2,0-3,1% | breadth panic ĐÃ CHỮA LÀNH HOÀN TOÀN, ~2,5 tuần trước inflection giá |

**Phát hiện #3**: breadth panic đạt đỉnh ĐÚNG CÙNG NGÀY với đáy giá (24/02) — capitulation kinh điển
(giá + độ rộng thị trường bottom cùng lúc, khối lượng ngày đó 10,27 triệu cp, cao hơn hẳn nền ~5-9
triệu của 2 tuần trước). Đây CHÍNH LÀ công thức `washout_gate=0.30` đã dùng trong `engine_p1.py` của
CAPIT — bằng chứng cơ chế này bắt ĐÚNG NGÀY ở episode gốc 2009, dù engine hiện tại chỉ có audit window
từ 2014 (Phần 1 file framework 08-25 không có bằng chứng trực tiếp 2009 — job này bổ sung bằng chứng
lịch sử độc lập rằng chính công thức đó khớp thời điểm capitulation thật của 2009).

### Volume/turnover: khối lượng "dẫn" hay "đuổi" giá?

Sau đỉnh breadth panic (24/02), thị trường đi ngang 240-255 điểm suốt gần 3 tuần (25/02→16/03) với
khối lượng bình thường (~7-12 triệu cp/phiên, TV_MA20 ổn định quanh 2,0-2,1 nghìn tỷ). Sau đó:

| Ngày | Volume | Close | Ghi chú |
|---|---|---|---|
| 16/03/2009 | 10,71 triệu | 254,56 | mức nền, chưa đổi |
| **17/03/2009** | **20,66 triệu (gần gấp đôi)** | **263,20 (+3,4%)** | **inflection thanh khoản** |
| 18-19/03/2009 | 25,9-32,0 triệu | 273,39→267,04 | duy trì cao |
| 07/04/2009 | 41,8 triệu | 322,40 | tiếp tục leo |
| 14-17/04/2009 | 43,7-67,7 triệu | 334-347 | bùng nổ |
| 06-22/05/2009 | 43-78 triệu | 350-412 | đỉnh khối lượng giai đoạn |

**Phát hiện #4 (trả lời trực tiếp câu hỏi bước 3): khối lượng KHÔNG dẫn giá theo kiểu "smart money vào
trước rồi giá mới tăng"** — dữ liệu cho thấy khối lượng và giá bứt phá **CÙNG NGÀY** (17/03: cả hai
nhảy vọt đồng thời), sau đó khối lượng **tăng dần theo cùng nhịp với giá tăng** trong 2 tháng tiếp
(self-reinforcing, không phải leading-lagging tách bạch). Điều DẪN DẮT rõ ràng nhất trong dữ liệu là
**sự HỒI PHỤC CỦA BREADTH** (24/02→10/03, ~2,5 tuần) **ĐI TRƯỚC** sự bùng nổ khối lượng/giá (17/03) —
đây là trình tự nhân-quả quan sát được: panic xả xong (breadth) → thị trường ổn định 2-3 tuần (không
volume) → dòng tiền mới cam kết (volume) → giá leo dốc.

## Bước 4 — Dòng vốn ngoại

**Không có dữ liệu định lượng trong BQ** (không có cột foreign buy/sell trong `ticker`/`ticker_1m`/
`bigquery_dictionary.json`). Chỉ có định tính từ addendum Bobby: FDI đăng ký 7 tháng đầu 2009 ~US$10,1
tỷ (53% dự án mới, 46% vốn bổ sung), giải ngân ~US$4,6 tỷ cùng kỳ — không tách được theo tháng để đối
chiếu lag với ngày 17/03. **Giới hạn phải mang theo**: không thể xác nhận/bác bỏ giả thuyết "khối
ngoại là động lực chính" bằng dữ liệu định lượng trong phạm vi job này.

## Bước 5 — Tổng kết: đâu là TRIGGER thật (bằng chứng thời gian, không suy diễn)

**Không có MỘT trigger đơn lẻ "sạch" (clean single trigger)** — bằng chứng thời gian cho thấy **tổ hợp
2 lớp cách nhau ~3 tuần**, khớp đúng với nhãn `MIXED` của Bobby (không phải ngẫu nhiên trùng hợp với
kết luận macro độc lập — đây là 2 đường bằng chứng khác nhau hội tụ):

1. **Lớp 1 — Capitulation kỹ thuật + hỗ trợ chính sách tín dụng trực tiếp (24/02/2009)**: breadth
   panic đỉnh CÙNG NGÀY giá đáy, xảy ra 23 ngày sau khi QĐ131 (gói bù lãi suất 4%) có hiệu lực và cùng
   tháng lãi suất cơ bản chạm đáy chu kỳ 7%. Đây là ứng viên lag-ngắn-nhất trong 7 mốc, nhưng **KHÔNG
   PHẢI single-action trigger rõ ràng** — không có tin tức/quyết định CỤ THỂ đúng ngày 24/02 tương ứng;
   nhiều khả năng là điểm hội tụ của (a) panic-selling tự nhiên đã xả kiệt (breadth 47,6%) + (b) nền
   chính sách đã đủ nới lỏng để chặn đà rơi tiếp (rate floor + QĐ131 đã có hiệu lực ~3 tuần).
2. **Lớp 2 — Dòng tiền cam kết thật (17/03/2009)**: khối lượng bùng nổ + giá bứt phá đồng thời, sau
   ~2,5 tuần breadth đã hồi phục hoàn toàn. Đây là điểm "dòng tiền kéo thị trường tăng mạnh" đúng nghĩa
   câu hỏi gốc — nhưng KHÔNG trùng với bất kỳ mốc chính sách nào trong 7 mốc đã cho (QĐ443 và công bố
   quy mô gói kích thích đều đến SAU, không phải trước). Có thể liên quan phục hồi rủi ro toàn cầu
   (DJIA/S&P bottom nổi tiếng 09/03/2009, 8 ngày trước) nhưng **KHÔNG kiểm chứng được bằng dữ liệu VN
   nội bộ trong job này** — nêu như một giả thuyết mở, không phải kết luận.
3. **QĐ443 + công bố $8 tỷ (04/2009) là XÁC NHẬN, không phải TRIGGER** — đến sau khi cả đáy giá lẫn
   bùng nổ thanh khoản đã xảy ra, phù hợp vai trò "mở rộng/duy trì" hơn "khởi phát".

**Kết luận cho khung Loại-1/Loại-2 (không đổi verdict Bobby, chỉ làm rõ thêm bằng dữ liệu)**: dữ liệu
giá/thanh khoản/breadth ủng hộ đọc `MIXED` — có đủ dấu hiệu domestic policy support (QĐ131, rate floor)
tại đúng lúc đáy, NHƯNG lag 3 tuần đến bùng nổ dòng tiền thật + việc QĐ443/gói $8B đến SAU sự kiện cho
thấy chính sách trong nước KHÔNG PHẢI single-shot trigger sạch kiểu Loại-2 CONTAINABLE (vd SCB 2022:
policy response CÙNG NGÀY bank-run). Đây là recovery từ từ, đa lớp — khớp với việc Bobby xếp trục 2 =
`EXTERNAL_CYCLE` chứ không `CONTAINABLE`.

## Bước 6 — 4 TÍN HIỆU LEAD INDICATOR cụ thể cho margin crisis sleeve tương lai

Đúng tinh thần `crisis_margin_framework_adaptive_20260825.md` Phần 3 (adaptive, N nhỏ, không calib
cứng) — 4 tín hiệu này BỔ SUNG vào bảng "Observable indicators" đã có, dùng số liệu THẬT đo từ 2009,
không phải giả định lý thuyết:

### LEAD-1: Breadth panic-exhaustion + healing speed (đã có hạ tầng, dùng lại `washout_gate=0.30`)
- **Đo được**: %mã universe_pit có D_RSI<0,30, cuối mỗi phiên — 0 lag.
- **Bằng chứng 2009**: đỉnh 47,6% (24/02) → hồi phục xuống <5% chỉ trong **10 phiên giao dịch** (~2,5
  tuần lịch). Tốc độ hồi phục NHANH này (không phải mức đỉnh) là tín hiệu — nếu breadth đỉnh cao nhưng
  DAI DẲNG (không hồi phục nhanh), đó là dấu hiệu panic chưa xả hết, khác hẳn 2009.
- **Cách dùng đề xuất**: sau khi trigger dd52≤−20% (đã có, `capit_margin_lever`), theo dõi tốc độ
  breadth-healing (số phiên để %oversold rơi từ đỉnh xuống <5%) làm điều kiện ARM bổ sung — healing
  nhanh (≤3 tuần như 2009) là tín hiệu ủng hộ escalate; healing chậm/dao động lặp lại (như cụm 2022
  09-28→11-16 đã ghi trong Phần 1 framework 08-25, kéo 7 tuần liên tục KHÔNG bao giờ hồi phục hẳn) là
  tín hiệu cảnh báo, KHÔNG phải điều kiện đủ để escalate ngay.

### LEAD-2: Turnover/volume regime-break (điểm "dòng tiền cam kết", tách biệt khỏi bottom giá)
- **Đo được**: Volume hoặc Trading_Value ngày, so với MA20/MA60 trước đó — 0 lag.
- **Bằng chứng 2009**: bùng nổ ngày 17/03 = **gần gấp đôi** volume ngày trước liền kề (10,7tr→20,7tr),
  xảy ra SAU khi breadth đã lành (LEAD-1) khoảng 2,5 tuần, và giá bứt phá CÙNG NGÀY với volume (không
  tách biệt được thứ tự trong-ngày, nhưng breadth dẫn trước cả hai theo tuần).
- **Cách dùng đề xuất**: dùng LEAD-1 (breadth healed) làm điều kiện CẦN, LEAD-2 (volume regime-break,
  vd Volume/MA20_trước_đó ≥1,8x) làm điều kiện XÁC NHẬN để tăng size/mở rộng thêm — tránh escalate
  ngay khi vừa thấy breadth lành (có thể vẫn đi ngang nhiều tuần như 2009 đã cho thấy, 25/02→16/03).

### LEAD-3: Xếp hạng độ trễ theo LOẠI chính sách, không phải SỐ LƯỢNG hành động
- **Bằng chứng 2009**: hành động tín dụng CÓ MỤC TIÊU CỤ THỂ (QĐ131 — bù lãi suất trực tiếp cho vay,
  gắn với 1 quyết định/1 ngày hiệu lực rõ) có lag tới đáy giá **23 ngày** — ngắn hơn ĐÁNG KỂ so với
  chuỗi 5 lần cắt lãi suất cơ bản trải dài 2 tháng (lag đến đáy **64 ngày TÍNH TỪ KHI CẮT XONG**, và
  chỉ số còn RƠI XUYÊN SUỐT lúc đang cắt).
- **Cách dùng đề xuất**: khi Bobby/Winston báo tin chính sách phản ứng 1 khủng hoảng tương lai, ưu
  tiên neo ngày ARM/theo dõi vào **quyết định tín dụng/tài khóa có mục tiêu cụ thể VÀ có ngày hiệu lực
  rõ ràng** (giống QĐ131) hơn là đếm số lần cắt lãi suất cơ bản — số lần cắt không tự nó là tín hiệu
  timing tốt (case 2008 Q4 chứng minh: 5 lần cắt, thị trường vẫn rơi xuyên suốt).

### LEAD-4 (RỦI RO/THOÁT, không phải VÀO): tripwire tái cấu-trúc sớm trong lúc rally đang diễn ra
- **Đo được** (đều real-time, KHÔNG hindsight, đã ghi cụ thể trong addendum Bobby 31/08): (a) tăng
  trưởng tín dụng SBV công bố định kỳ vs mục tiêu ban đầu (lag ~1 tháng), (b) cán cân thương mại GSO/
  Hải quan đảo dấu (lag 2-4 tuần), (c) premium tỷ giá chợ đen (lag 0, quan sát hàng ngày).
- **Bằng chứng 2009**: cả 3 tín hiệu bắt đầu XẤU ĐI từ **Q2/giữa năm 2009** (tín dụng vượt mục tiêu
  21-23% giữa năm, thương mại đảo thâm hụt từ Q2, premium chợ đen nới) — TẠI THỜI ĐIỂM ĐÓ VNINDEX vẫn
  đang ở vùng 411-448 điểm (tháng 05-06/2009), và **còn tăng tiếp +39% nữa đến đỉnh 624,1 (22/10/2009)
  — tức là các tín hiệu này đến TRƯỚC đỉnh giá thật khoảng 4-5 tháng**, không phải tín hiệu đảo chiều
  ngay lập tức mà là CẢNH BÁO SỚM để giảm dần đòn bẩy/kỷ luật chặt hơn, không phải tín hiệu thoát toàn
  bộ ngay. Đảo chiều giá thật xảy ra sau khi SBV nâng lãi suất trở lại (25/11/2009, ngoài cửa sổ hỏi,
  đã ghi ở file Phases) — tháng đó VNINDEX rơi −14% (587,10→504,10).
- **Cách dùng đề xuất**: một sleeve margin Loại-2 KHÔNG NÊN giữ nguyên size/đòn bẩy giả định "rally sẽ
  còn kéo dài theo hình dạng Loại-2 CONTAINABLE" xuyên suốt — 3 tín hiệu này là "đồng hồ đếm ngược" cho
  khả năng episode chuyển hoá về STRUCTURAL relapse (đúng những gì Bobby đã cảnh báo: gói kích thích
  2009 "bôi thêm dầu vào lửa" cho Wave 2 2009-2012). Khi ≥2/3 tín hiệu xấu đi ĐỒNG THỜI trong lúc sleeve
  đang có lãi, đó là điều kiện ĐỦ để bắt đầu trim/de-risk dần, không chờ giá tự đảo chiều.

## Giới hạn phải mang theo

1. Bước 4 (dòng vốn ngoại) không thực hiện được định lượng — thiếu cột dữ liệu trong BQ.
2. LEAD-2 (volume regime-break) và giả thuyết "global equity bottom 09/03 góp phần" chưa kiểm chứng
   chéo với dữ liệu quốc tế (DXY/EEM/SPX theo ngày) trong job này — chỉ nêu như quan sát mở.
3. N=1 episode (2009) cho toàn bộ phân tích lag — đúng tinh thần framework 08-25, đây là bằng chứng
   MÔ TẢ chi tiết 1 case, KHÔNG PHẢI kiểm định thống kê; không tự suy rộng thành ngưỡng số cứng cho
   episode tương lai mà không có ít nhất 1-2 case đối chứng khác (vd lặp lại phân tích này cho 2022
   post-SCB, đã có 1 phần trong `crisis_margin_framework_adaptive_20260825.md` Phần 1, để so lag).
4. Điểm inflection 17/03/2009 xác định bằng ngưỡng trực quan (volume gần gấp đôi), chưa formalize
   thành công thức ngưỡng số (vd "Volume/MA20 ≥ X") — cần thêm case đối chứng trước khi hardcode X.
