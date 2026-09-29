# VN 2011-2013 (Wave 2/3 mega-crisis 2007-2012) Recovery Trigger — đối chứng N=3→N=4

> Job `Taylor_20260831_042736` · 2026-08-31 · RESEARCH-ONLY, không wire production.
> Phương pháp lặp lại y hệt `vn_2009_recovery_trigger_20260831/` (job `_033154`) và
> `vn_2020_2022_recovery_trigger_20260831/` (job `_040228`): xác định đáy/peak thật bằng dữ liệu
> (không giả định), đo breadth panic (`universe_pit` D_RSI<0,30), đo volume/turnover inflection,
> đối chiếu lag với timeline chính sách PIT.
> Input Bobby (blind, KHÔNG đổi ở đây): `EP-2009-09` = trục 1 `STRUCTURAL` (clean), trục 2
> `MULTI_YEAR_STRUCTURAL` (clean), `chain_classification: WAVE_OF:MEGA_2007_2012` (Wave 2+3).
> Cửa sổ episode Bobby: 09/2009 (tín dụng/lạm phát tái tăng tốc) → 12/2012 (CPI về <7%);
> `recovery_confirmed`: 12/2012 (CPI) và 2015-2016 (NPL/VAMC resolved). Đây là episode
> **khác hẳn về loại** so với 3 case trước (2009/2020/2022 đều `CONTAINABLE`/`EXTERNAL_CYCLE`
> hoặc `MIXED` cho riêng Wave 1) — N=4 lần này có 1 case `STRUCTURAL`/`MULTI_YEAR` thật để đối
> chứng, không chỉ thêm 1 case cùng loại.

## Nguồn dữ liệu

- Giá/khối lượng VNINDEX daily: `data/VNINDEX.csv` (cùng nguồn 3 job trước).
- Breadth oversold: `tav2_bq.ticker` JOIN `tav2_mike.universe_pit` (PIT), `D_RSI < 0,30`. **N
  universe 2011-2012: 606→628** — lớn hơn 2009 (228-375) nhưng chỉ bằng ~1/2 của 2020-2022
  (1.160-1.254), đủ để không "mỏng vô nghĩa" như CLAUDE.md cảnh báo (universe_pit đầu tư được rõ
  từ ~2008), nhưng vẫn nhỏ hơn 2 episode gần đây — giữ nguyên trong đầu khi so % trực tiếp.
  ⚠️ **Bẫy đã gặp lại đúng CLAUDE.md §BQ**: query đầu tiên bị cắt còn 100 dòng (mặc định `bq`
  CLI) — phải thêm `--max_rows=2000` mới lấy đủ 273 phiên của cửa sổ hỏi.
- Chính sách: 2 mốc đã có ngày trong timeline PIT của dispatch (Resolution 11: 24/02/2011; refi
  rate 15%: "11/2011" — CHỈ có tháng). 3 mốc còn lại xác minh ngày cụ thể qua WebSearch (Mayer
  Brown, Lexology, Central Banking, FocusEconomics — trích dưới mỗi mốc).
- **Phát hiện quan trọng về tính PIT của chính input dispatch**: "NPL 17,21% cuối Q3/2012 (SBV
  reassessment)" mà dispatch đưa **KHÔNG PHẢI số liệu PIT** — đây là con số **đánh giá lại năm
  2015** (Thống đốc công bố tháng 5/2015, hồi tố về 30/09/2012). Số liệu SBV công bố THẬT tại
  thời điểm 09/2012 là **8,82%** (SBV chính thức, tháng 9/2012). Đã sửa dùng 8,82% cho toàn bộ
  phân tích lag dưới đây — dùng 17,21% sẽ tạo ra lag SAI (nó đo lường điều nhà đầu tư 2012
  KHÔNG THỂ biết).

## Bước 1 — Xác định đáy/peak thật (KHÔNG giả định, quét toàn bộ cửa sổ 2011-2013)

| Sự kiện | Ngày | Close VNINDEX |
|---|---|---|
| **Đáy TUYỆT ĐỐI cửa sổ 2011-01-01→2013-12-31** | **2012-01-06** | **336,73** |
| Rally đầu tiên (thất bại) — peak | 2012-05-08 | 488,07 (+44,95% từ đáy tuyệt đối, 123 ngày) |
| **Đáy phụ (retest sau khi rally #1 sụp đổ)** | **2012-11-02** | **375,26** (−23,1% từ 488,07, 178 ngày) |
| **Peak đảo chiều rõ ĐẦU TIÊN từ đáy phụ** (sau đó −10,4% trong ~2,5 tuần, cùng ngưỡng "clean
  reversal" đã dùng cho 2009/2022) | **2013-06-07** | **527,97** |

**Phát hiện #1 — quan trọng nhất của job này: đáy TUYỆT ĐỐI (06/01/2012) là ĐÁY GIẢ (false
bottom), không phải điểm khởi đầu phục hồi bền vững.** Khác hẳn 2009/2020/2022 (đáy tuyệt đối =
điểm bắt đầu 1 xu hướng tăng liên tục, dù có nhịp điều chỉnh nông), ở đây đáy tuyệt đối 336,73
sinh ra 1 rally +44,95% trong 4 tháng RỒI SỤP HOÀN TOÀN (−23,1%), tạo đáy phụ THẤP GẦN BẰNG đáy
cũ (375,26 vs 336,73, chỉ cách nhau 11,4%) 10 tháng sau. Đây CHÍNH LÀ dấu ấn cấu trúc W-shape/
double-dip mà STRUCTURAL/MULTI_YEAR của Bobby dự đoán — không phải capitulation 1 lần.

**Bottom-to-peak (dùng đáy phụ 02/11/2012 → peak đảo chiều rõ 07/06/2013, comparable trực tiếp
với cách 2009/2022 định nghĩa): +40,68% trong 217 ngày lịch (~7,1 tháng).** Nếu tính từ đáy
tuyệt đối 06/01/2012 → cùng peak 07/06/2013: +56,80% trong 517 ngày (~17 tháng) — số này PHÓNG
ĐẠI vì đi qua nguyên chu kỳ rally-sụp-hồi phục, không phản ánh 1 xu hướng liên tục như số +165%
của 2009 hay +131,9%/+36,6% của 2020/2022.

## Bước 2 — Lag từng mốc chính sách → CẢ HAI đáy (không chỉ 1 đáy, vì có 2 đáy thật)

| Mốc chính sách | Ngày | Nguồn | Lag → đáy tuyệt đối (06/01/2012) | Lag → đáy phụ (02/11/2012) |
|---|---|---|---|---|
| Resolution 11/NQ-CP (cap tín dụng <20%, siết tài khóa) | 2011-02-24 | registry Bobby | +316 ngày | +617 ngày |
| **SBV refi rate chạm đỉnh chu kỳ 15%** (lần tăng thứ 5 trong năm, ĐỈNH thắt chặt) | **2011-10-10** | [FocusEconomics](https://www.focus-economics.com/countries/vietnam/news/monetary-policy/central-bank-hikes-rates-for-the-first-time-since-2011/) | **+88 ngày** | +389 ngày |
| **Quyết định 254/QĐ-TTg** (đề án tái cơ cấu TCTD 2011-2015, PHÊ DUYỆT) | **2012-03-01** | [Mayer Brown](https://www.mayerbrown.com/en/perspectives-events/publications/2012/04/vietnam-schedule-to-restructure-credit-institution) | **−55 ngày (SAU đáy)** | +246 ngày |
| **SBV cắt lãi suất LẦN 1** (bắt đầu nới lỏng, −100bp) | **2012-03-13** | [Central Banking](https://www.centralbanking.com/central-banks/monetary-policy/monetary-policy-decisions/7958248/state-bank-of-vietnam-cuts-interest-rate) | −67 ngày (SAU đáy) | +234 ngày |
| **NPL 8,82% công bố CHÍNH THỨC** (SBV, số liệu THẬT lúc đó — KHÔNG phải 17,21% hồi tố 2015) | ~2012-09 (quý III) | [tổng hợp nhiều nguồn, xem ghi chú Bước 4] | −270 ngày (SAU đáy) | **~+33 đến +63 ngày (ước lượng, xem giới hạn)** |
| Decree 53/2013/NĐ-CP (thành lập VAMC, hiệu lực) | 2013-07-09 | [Lexology](https://www.lexology.com/library/detail.aspx?g=6cb7aa2b-1da5-4fae-962d-0bd2672bd9b3) | +550 ngày | +614 ngày |
| VAMC chính thức hoạt động | 2013-10-01 | [vietnam-business-law.info](https://vietnam-business-law.info/blog/2013/8/9/more-details-about-vietnam-asset-management-company-vamc) | +634 ngày | +698 ngày |

**Phát hiện #2 — trả lời trực tiếp câu hỏi cốt lõi của dispatch: "mốc lag ngắn nhất khớp giả
thuyết nào đã rút ra?"** Câu trả lời KHÁC với cả 2009 (targeted action thắng) VÀ 2022 (nhánh rủi
ro cuối cùng thắng) — ở đây **KHÔNG CÓ mốc chính sách nào (support/resolution) đến TRƯỚC đáy
tuyệt đối cả.** Cả Quyết định 254 (phê duyệt đề án tái cơ cấu — hành động "resolution" gần nhất
với ý nghĩa targeted của 2009's QĐ131) VÀ đợt cắt lãi suất đầu tiên đều đến **SAU** đáy giá tuyệt
đối 55-67 ngày. Mốc GẦN NHẤT trước đáy tuyệt đối là **đỉnh của chính chuỗi THẮT CHẶT** (refi rate
chạm 15%, +88 ngày) — tức là thị trường bottom không phải vì có ai đó ra tay giải cứu, mà vì
**"đủ tệ đã được price-in — chu kỳ siết chặt tệ nhất đã qua"**, một cơ chế hoàn toàn khác 2 giả
thuyết cũ (targeted action / nhánh rủi ro cuối cùng). Đặt tên: **LEAD-5 mới — "peak-stressor
exhaustion"**: khi không có support action nào khả dụng/đủ nhanh, thị trường có thể bottom chỉ
dựa trên "biết chắc điều tệ nhất (chính là NGUỒN GỐC gây stress, ở đây là lãi suất 15%) đã dừng
tăng", ngay cả khi hành động SỬA chữa thật sự còn cách hàng tháng.

Với đáy phụ (02/11/2012) — đáy này MỚI thật sự dẫn tới phục hồi bền vững — mốc lag ngắn nhất là
**công bố NPL 8,82%** (~1-2 tháng), ngắn hơn nhiều so với Quyết định 254 (đã có từ 8 tháng trước
nhưng KHÔNG ngăn được rally #1 sụp đổ) và VAMC (còn 20 tháng nữa). Đây là **LEAD-5b — "uncertainty
resolution qua công bố số liệu xấu"**: bản thân con số NPL là TIN XẤU (8,82% cao), nhưng việc nó
được LƯỢNG HÓA CHÍNH THỨC (thay vì đồn đoán/che giấu trước đó) loại bỏ phần bất định "tệ đến đâu
cũng không biết" — khác hẳn cơ chế "support action" của 2009/2022 hay "global catalyst" của 2020.

## Bước 3 — Breadth panic: có đồng bộ với đáy giá như 3 case trước KHÔNG?

### Breadth oversold quanh 2 đáy (universe_pit, N=606-628)

| Đáy giá | Ngày | Đỉnh breadth GẦN NHẤT | Ngày đỉnh breadth | Lệch (đỉnh breadth vs đáy giá) |
|---|---|---|---|---|
| Đáy tuyệt đối | 2012-01-06 (18,59% oversold ngày đó) | **31,74%** | **2011-12-27** | **breadth ĐI TRƯỚC giá 9 phiên** (đến ngày đáy giá, breadth đã hồi từ 31,74%→18,59%) |
| Đáy phụ | 2012-11-02 (15,18% oversold ngày đó) | **29,52%** | **2012-08-23** | **breadth ĐI TRƯỚC giá ~71 ngày lịch (52 phiên)** |

**Phát hiện #3 (mảnh quan trọng thứ hai) — bác bỏ tính robust "breadth panic đỉnh TRÙNG ngày đáy
giá" đã xác lập từ N=3 (2009 trùng ngày, 2020 T-1, 2022 trùng ngày).** Ở CẢ HAI đáy của episode
STRUCTURAL này, đỉnh breadth panic đến RẤT SỚM trước đáy giá thật (9 phiên và 52 phiên) — thị
trường tiếp tục rơi/đi ngang một thời gian dài SAU KHI panic-selling đã xả xong, khác hẳn
capitulation-kinh-điển của 3 case CONTAINABLE trước. **Cơ chế đúng hơn cho STRUCTURAL**: đây
không phải 1 cú sốc-rồi-capitulate, mà là quá trình XÓI MÒN dần dần (grinding decline) — breadth
"mệt" (hết mã để bán tháo thêm) sớm hơn nhiều so với khi GIÁ chấp nhận đáy cuối cùng, vì giá còn
tiếp tục drift xuống bởi thiếu lực mua (không phải panic-selling mới).

### Healing speed (LEAD-1) — so với N=3 đã có

| Episode | Loại (Bobby) | Đỉnh breadth | Baseline calm | Số phiên hồi phục về ≤baseline |
|---|---|---|---|---|
| 2009 | MIXED/EXTERNAL_CYCLE | 47,6% | ~0,6% | **10 phiên** |
| 2020 | CONTAINABLE | 32,9% | 15,17% | **12 phiên** |
| 2022 | CONTAINABLE | 48,68% | 6,29% | **47 phiên** |
| **2012 leg 1** (đỉnh 27/12/2011) | STRUCTURAL | 31,74% | 4,81% | **32 phiên** |
| **2012 leg 2** (đỉnh 23/08/2012) | STRUCTURAL | 29,52% | 4,81% | **91 phiên** — CHẬM NHẤT trong 5 lần đo |

**Phát hiện #4 (mảnh CỦNG CỐ mạnh nhất cho khung LEAD-1 healing-speed) — giả thuyết "healing
speed tương quan với hình dạng cú sốc" (rút ra từ N=3, job trước) được XÁC NHẬN RÕ RÀNG bởi
episode STRUCTURAL đầu tiên đưa vào so sánh**: leg 2 của 2012 (91 phiên) chậm hơn GẤP ĐÔI so với
case chậm nhất trước đó (2022, 47 phiên) và gấp ~9 lần case nhanh nhất (2009, 10 phiên). Đây
KHÔNG phải trùng hợp ngẫu nhiên với phân loại Bobby — cả 2 leg của episode STRUCTURAL duy nhất
trong 5 lần đo đều nằm ở nửa CHẬM của phân phối (32, 91 phiên) trong khi 2/3 case CONTAINABLE đều
nhanh (10, 12 phiên), chỉ 1 case CONTAINABLE (2022, đa nhánh) chậm trung bình (47 phiên). **Kết
luận đủ mạnh để đề xuất**: healing speed >~50 phiên là tín hiệu CẢNH BÁO hợp lý cho STRUCTURAL/
multi-year chứ không phải CONTAINABLE — dù N=2 episode STRUCTURAL vẫn còn mỏng để chốt ngưỡng số.

## Bước 4 — Volume/turnover: có inflection sạch như 2009/2022 không?

**KHÔNG có 1 ngày inflection sạch.** Từ đáy phụ 02/11/2012 (volume 51,0tr, đã là 1 spike hoảng
loạn CÙNG NGÀY giá giảm mạnh — giống dạng "panic dump" hơn "dòng tiền mới"), volume duy trì nền
thấp (14-33tr cp/phiên) suốt gần 7 tuần (05/11→14/12), rồi TĂNG DẦN qua nhiều tuần (không phải 1
cú nhảy vọt): 17/12 (44,5tr) → **19/12 (64,5tr, +45% d/d, giá phá vỡ vùng cản 395-400 đã giữ từ
tháng 10)** → duy trì cao 40-70tr suốt cuối tháng 12 → bùng nổ thật sự đầu 2013 (03/01: 96,1tr;
09/01: 131,4tr, đỉnh khối lượng giai đoạn, trùng mùa cận Tết Nguyên Đán — hiệu ứng dòng tiền mùa
vụ đã biết, không tách được khỏi tín hiệu cơ bản trong job này).

**Phát hiện #5**: nếu phải chọn 1 ngày "gần nhất với inflection" theo tinh thần LEAD-2 (ngưỡng
≥1,8x volume ngày trước), KHÔNG ngày nào trong toàn bộ tháng 11-12/2012 đạt ngưỡng đó (cao nhất
là 19/12 ở 1,45x, xem file `vol_ratio` — dưới ngưỡng 2009 dùng ~1,9x và 2022's ~1,65x). LEAD-2 ở
dạng "single-day regime-break" **KHÔNG áp dụng được** cho episode STRUCTURAL — dòng tiền tích lũy
GRADUAL qua ~7 tuần, khác hẳn 3 case trước (2009: nhảy vọt 1 ngày; 2020: đồng bộ với sell-off;
2022: T+1 tức thời). Đây là dấu hiệu thứ 3 (sau breadth lệch pha, healing chậm) cho thấy
STRUCTURAL crisis KHÔNG có 1 "điểm bật" (inflection point) rõ ràng nào — recovery của nó là quá
trình, không phải sự kiện.

## Bước 5 — Bảng tổng hợp N=3→N=4 và trả lời câu hỏi dispatch

### Bảng lag ngắn nhất mỗi episode (mở rộng)

| Episode | Root cause (Bobby) | Containability (Bobby) | Mốc lag ngắn nhất tới đáy DẪN TỚI recovery bền vững | Lag | Loại cơ chế |
|---|---|---|---|---|---|
| 2009 | MIXED | EXTERNAL_CYCLE | QĐ131 (bù lãi suất, hiệu lực) | +23 ngày | Targeted domestic support |
| 2020 | CONFIDENCE_LIQUIDITY | CONTAINABLE | S&P 500 bottom | 0 ngày (trùng) | Global risk-sentiment catalyst |
| 2022 | CONFIDENCE_LIQUIDITY | CONTAINABLE | SBV nâng lãi lần 2 (bảo vệ FX) | +22 ngày | Nhánh rủi ro CUỐI CÙNG được giải quyết (kể cả blanket) |
| **2012 (đáy tuyệt đối)** | STRUCTURAL | MULTI_YEAR_STRUCTURAL | **KHÔNG có support action nào đi trước** — mốc gần nhất là chính đỉnh SIẾT CHẶT (refi 15%) | +88 ngày (từ đỉnh siết chặt, KHÔNG phải support) | **Peak-stressor exhaustion** (thị trường price-in "tệ nhất đã qua" trước khi ai sửa gì) |
| **2012 (đáy phụ, dẫn tới recovery thật)** | STRUCTURAL | MULTI_YEAR_STRUCTURAL | Công bố NPL 8,82% chính thức | ~+33-63 ngày (ước lượng) | **Uncertainty resolution qua lượng hóa tin xấu**, KHÔNG phải action sửa chữa |

**Trả lời câu hỏi cốt lõi của dispatch**: "mốc lag ngắn nhất của 2012 khớp giả thuyết nào đã rút
ra ở job trước (nhánh rủi ro CUỐI CÙNG được giải quyết, không phải nhánh gốc)?" → **KHÔNG khớp
giả thuyết nào trong 2 giả thuyết cũ (targeted-action-thắng-blanket của 2009, nhánh-rủi-ro-cuối-
cùng của 2022).** 2012 đưa ra **2 cơ chế MỚI, cả hai đều chưa xuất hiện ở N=3**:
1. Với đáy tuyệt đối (hoá ra là đáy GIẢ): không hành động support nào đi trước — thị trường
   bottom trên cơ sở "đỉnh của chính NGUỒN GỐC gây stress đã qua" (refi rate 15% là đỉnh thắt
   chặt, không phải đỉnh nới lỏng).
2. Với đáy phụ (đáy THẬT dẫn tới recovery bền vững): mốc gần nhất không phải 1 hành động SỬA
   chữa (Quyết định 254 đã có 8 tháng mà không ngăn được rally #1 sụp đổ) mà là 1 hành động
   **LƯỢNG HÓA/CÔNG KHAI mức độ tệ** (NPL 8,82%) — loại bỏ bất định, dù bản thân con số là tin
   xấu. Đây là bằng chứng cho thấy khủng hoảng STRUCTURAL không "recover" theo logic
   support-action hay giải-quyết-nhánh-cuối, mà theo logic **"đủ thông tin xấu đã ra hết, không
   còn gì bất ngờ hơn để sợ"** — closer to giả thuyết kinh điển "bad news is priced in" hơn là
   "policy fixed it."

### LEAD-1..5 — cập nhật robustness N=3→N=4

| LEAD | N=3 (job trước) | 2012 (episode STRUCTURAL đầu tiên) | Đánh giá cập nhật |
|---|---|---|---|
| LEAD-1 (breadth đỉnh TRÙNG đáy giá) | Robust cả 3 case | **BÁC BỎ RÕ RÀNG cả 2 leg** (lệch 9 và 52 phiên) | **KHÔNG robust cho STRUCTURAL** — chỉ đúng cho CONTAINABLE/cú sốc-1-lần. Cần thêm điều kiện: dùng LEAD-1 làm tín hiệu "vào" chỉ khi ĐÃ xác nhận containability, không dùng mù. |
| LEAD-1b (healing speed phân biệt loại cú sốc) | Chưa đủ N để chốt | **XÁC NHẬN MẠNH**: 2/2 leg STRUCTURAL đều CHẬM (32, 91 phiên), nằm ở nửa chậm của cả 5 lần đo | **Nâng lên MEDIUM-confidence** — ngưỡng thô ~>50 phiên đáng để dùng làm tín hiệu cảnh báo "đây có thể là STRUCTURAL, đừng dùng sizing kiểu CONTAINABLE." |
| LEAD-2 (volume regime-break 1 ngày) | Áp dụng được 2/3 case (2009 rõ, 2022 rõ, 2020 không) | **KHÔNG áp dụng** — dòng tiền tích lũy gradual ~7 tuần, không đạt ngưỡng ≥1,8x bất kỳ ngày nào | Củng cố thêm bằng chứng: LEAD-2 dạng "1 ngày" là tín hiệu ĐẶC TRƯNG của CONTAINABLE (dòng tiền dứt khoát), vắng mặt của nó CHÍNH NÓ có thể dùng như 1 tín hiệu phân loại (absence-as-signal, nhưng cần cẩn trọng theo §28 coding_guidelines — đây là quan sát mở, chưa kiểm định). |
| LEAD-3 (targeted domestic action lag ngắn nhất) | Đúng 1/3 (chỉ 2009) | **Vẫn KHÔNG đúng** — Quyết định 254 (targeted nhất) đến SAU cả đáy tuyệt đối, và không phải mốc lag ngắn nhất cho đáy phụ | Củng cố kết luận N=3: targeted-action-thắng chỉ đúng cho khủng hoảng đơn-nhánh domestic-origin rõ (2009-kiểu), KHÔNG generalize. |
| **LEAD-5 (MỚI, đề xuất từ job này)** | — | Peak-stressor-exhaustion (đáy giả) + uncertainty-resolution-qua-công-bố (đáy thật) | Giả thuyết MỞ, N=1 episode (2 sub-case) — cần thêm case STRUCTURAL khác để kiểm chứng trước khi coi là robust. |

## Giới hạn phải mang theo

1. **Ngày công bố NPL 8,82% chỉ xác định ở độ chính xác THÁNG** (~09/2012, có thể là báo cáo quý
   III hoặc phát biểu của Thống đốc Nguyễn Văn Bình vào thời điểm gần đó) — lag "+33 đến +63
   ngày" tới đáy phụ là ƯỚC LƯỢNG dựa trên khung quý (30/09/2012 → 02/11/2012 = 33 ngày; nếu công
   bố thật sự vào đầu tháng 10 thì lag ngắn hơn). Cần xác minh ngày công bố chính xác (báo chí VN
   giai đoạn đó, VnEconomy/Tuổi Trẻ archive) trước khi dùng số ngày này cho bất kỳ ngưỡng cứng
   nào.
2. **N=1 episode STRUCTURAL thật (dù có 2 sub-bottom)** — LEAD-5 (2 cơ chế mới) là giả thuyết MÔ
   TẢ, không phải kiểm định thống kê, đúng tinh thần `crisis_margin_framework_adaptive_20260825`.
   Không tự suy rộng thành ngưỡng số hay rule production.
3. Việc dùng "17,21%" (số hồi tố 2015) thay vì "8,82%" (số PIT thật 2012) trong INPUT dispatch
   ban đầu là 1 lỗi PIT thật — đã tự phát hiện và sửa trong job này, nhưng đáng lưu ý cho
   Bobby/registry: nếu `vn_macro_regime_history.md` dùng 17,21% làm mốc thời gian ở bất kỳ chỗ
   nào khác ngoài phạm vi job này, cần soát lại tương tự.
4. Baseline "calm" (4,81%, dùng khoảng Jun 1-20/2012 — giữa 2 leg của cùng episode) có thể CHƯA
   THẬT SỰ "calm" (thị trường vẫn đang trong episode STRUCTURAL dài hơi) — khác với baseline của
   2009/2020/2022 vốn lấy từ giai đoạn RÕ RÀNG trước/sau 1 crisis riêng biệt. Đây là hạn chế
   phương pháp luận cố hữu khi crisis kéo dài nhiều năm không có "khoảng nghỉ" sạch để đo baseline.
5. Đáy tuyệt đối dùng Close hàng ngày (không phải intraday Low) — nhất quán với 3 job trước,
   nhưng không loại trừ có phiên với Low intraday thấp hơn 336,73 mà Close cao hơn.
