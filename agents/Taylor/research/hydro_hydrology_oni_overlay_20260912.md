# Thủy văn (ENSO/ONI) tác động lợi nhuận nhóm thủy điện VN — 2026-09-12

**Câu hỏi của user (John):** đã có lens năng lượng (`energy_valuation_framework.md` sector #9,
screen A "mature utility" VSH/SJD/NT2/PPC/REE/POW) nhưng đó THUẦN screen tài chính
(EVEB/FCF/Debt/IC) — chưa có biến thủy văn nào. Có nên thêm không?

**Kết luận ngắn:** CÓ tín hiệu thật, hướng đúng như giả thuyết vật lý (El Nino → hạn hán → NP
thủy điện giảm; La Nina → mưa nhiều → NP tăng), nhưng **N quá mỏng để dùng làm gì hơn một earnings
NOWCAST overlay mềm** cho 2 mã thuần thủy điện (VSH, SJD). **KHÔNG đổi verdict "LENS not BOOK"**
của mature-utility screen — đây là lớp giải thích thêm cho NP thủy điện, không phải một sizing
signal, và không đủ mạnh để override screen tài chính hiện có.

## 1. Dữ liệu

### 1.1 ONI (Oceanic Niño Index, NOAA CPC)
Không fetch trực tiếp được trang gốc `origin.cpc.ncep.noaa.gov` (DNS fail từ sandbox này). Trang
redirect `www.cpc.ncep.noaa.gov/.../oni/v6/` fetch được nhưng qua WebFetch (model tóm tắt nhỏ đọc
HTML rồi trả bảng) — **không phải đọc trực tiếp file `oni.ascii.txt`**. Đã cross-check bằng trí nhớ
các đợt ENSO nổi tiếng (El Nino 2015-16 peak ONI 2.6 ✓, La Nina 2010-11 ✓, La Nina 3 năm liên tiếp
2020-23 ✓, El Nino 2023-24 peak 2.0 ✓) — khớp số liệu công khai đã biết. **Dòng 2026 (DJF→JJA) nằm
sau knowledge cutoff của model, KHÔNG verify được độc lập — loại khỏi phân tích định lượng, chỉ giữ
tham khảo.**

Lưu bản snapshot thủ công: `research/oni_index_manual_20260912.csv` (234 dòng, 2006-2025, 12 mùa
chồng lấn DJF...NDJ mỗi năm). **Đây là snapshot MỘT LẦN, không phải feed tự động** — xem §5.

### 1.2 Tài chính thủy điện (BQ `tav2_bq.ticker_financial`)
Query trực tiếp (COUNT trước = 457 dòng cho 6 mã, dùng `--max_rows=1000` để lấy hết, không bị trần
100-row mặc định). Lưu panel đã merge với ONI: `research/hydro_oni_merged_panel_20260912.csv`.

**Universe thực tế dùng được — thu hẹp so với brief:**
- **VSH** (Vĩnh Sơn - Sông Hinh, Nam Trung Bộ) — thuần thủy điện. Dùng được.
- **SJD** (Cụm Sê San, Tây Nguyên) — thuần thủy điện. Dùng được.
- **NT2, PPC** — nhiệt điện khí/than, KHÔNG phải thủy điện. Đổi vai trò: dùng làm **nhóm ĐỐI CHỨNG**
  (control) — nếu hiệu ứng ENSO chỉ xuất hiện ở VSH/SJD mà KHÔNG xuất hiện ở NT2/PPC, đó là bằng
  chứng cơ chế đúng (mưa/thủy văn), không phải trùng hợp macro chung.
- **REE** — holding đa ngành (M&E, BĐS, thủy điện, điện khác, nước) — `ticker_financial` chỉ có
  NP hợp nhất, KHÔNG tách được segment thủy điện. **Loại khỏi test định lượng**, giữ định tính.
- **POW** — gentco đa nhà máy (khí + than + thủy, khí/than áp đảo) — cùng lý do REE, NP hợp nhất
  không tách được. **Loại khỏi test định lượng.**

→ Test định lượng thực tế chỉ chạy được trên **VSH + SJD** (thuần) vs **NT2 + PPC** (đối chứng).
Đây là giới hạn thật của bảng `ticker_financial`, không phải lựa chọn chủ quan.

## 2. Phương pháp

- **Biến phụ thuộc**: `NP_R` (đã có sẵn trong `ticker_financial` = NP YoY growth, verify công thức
  đúng bằng tay trên SJD 2008Q1: NP_P0=1.71e10, NP cùng kỳ năm trước=9.65e9 → NP_R tính tay = 0.774,
  khớp giá trị lưu 0.7773).
- **Biến độc lập**: phân loại ENSO mùa theo đúng quy tắc NOAA CPC — El Nino/La Nina CONFIRMED khi
  ONI ≥0.5 (hoặc ≤-0.5) trong **≥5 mùa chồng lấn liên tiếp**; còn lại = Neutral/transitional. Tự
  code lại rule này trên chuỗi ONI, không tự gán bằng mắt.
- **Độ trễ (per yêu cầu §4 dispatch)**: dùng ONI trễ **2 quý** so với quý báo cáo tài chính — vừa
  khớp cơ chế vật lý (mưa mùa → tích nước hồ chứa → sản lượng phát điện các quý sau, không phải
  tức thời), vừa an toàn point-in-time vì ONI của 2 quý trước chắc chắn đã công bố ổn định từ lâu.
- **Point-in-time**: NOAA có revise ONI nhẹ về sau (đổi chuẩn ERSST version theo thời gian — trang
  gốc còn nói rõ "ONI table dựa trên ERSSTv5 đã được thay bằng v6"). Trễ 2 quý là đủ an toàn khỏi
  look-ahead — không dùng bản ONI "mới nhất" cho quý gần nhất.

## 3. Kết quả

### 3.1 Theo mùa/quý (pseudo-replicated — nhiều dòng cùng 1 đợt ENSO, chỉ để tham khảo)
| Nhóm | Phase (lag 2Q) | N (dòng) | Median NP YoY |
|---|---|---|---|
| VSH+SJD (thuần thủy điện) | El Nino | 39 | **-35,3%** |
| VSH+SJD | Neutral | 64 | +18,8% |
| VSH+SJD | La Nina | 45 | +19,1% |
| VSH+SJD, **chỉ Q3/Q4** (mùa mưa/tích nước) | El Nino | 14 | **-38,8%** |
| VSH+SJD, chỉ Q3/Q4 | Neutral | 43 | +20,0% |
| VSH+SJD, chỉ Q3/Q4 | La Nina | 17 | +19,1% |
| NT2+PPC (đối chứng, nhiệt điện) | El Nino | 35 | -24,1% |
| NT2+PPC | Neutral | 59 | -53,1% |
| NT2+PPC | La Nina | 36 | -13,8% |

Đối chứng NT2/PPC KHÔNG có pattern nhất quán theo phase (median âm ở cả 3 nhóm, không lệch theo
hướng El Nino tệ hơn) — phù hợp cơ chế "nhiệt điện không phụ thuộc mưa", ủng hộ hiệu ứng ở VSH/SJD
là thật chứ không phải nhiễu macro chung ăn vào mọi genco.

### 3.2 Theo ĐỢT ENSO độc lập (N đúng nghĩa, không pseudo-replicate)
Tổng cộng từ 2006 tới 2025 (theo quy tắc CPC 5-mùa-liên-tiếp): **5 đợt El Nino, 4 đợt La Nina** đã
CONFIRMED (loại các đoạn dao động ngắn không đạt ngưỡng 5 mùa). Median NP YoY (VSH+SJD) của TỪNG
đợt (1 điểm dữ liệu = 1 đợt, không phải 1 quý):

| Đợt | Năm | Phase | Median NP YoY của đợt |
|---|---|---|---|
| 1 | 2006-07 | El Nino | -48,0% |
| 2 | 2007-09 | La Nina | +71,8% |
| 3 | 2009-10 | El Nino | -25,5% |
| 4 | 2010-12 | La Nina | -4,9% |
| 5 | 2014-16 | El Nino | -3,1% |
| 6 | 2017-18 | La Nina | +28,9% |
| 7 | 2018-20 | El Nino | -52,4% |
| 8 | 2020-23 | La Nina | +18,6% |
| 9 | 2023-24 | El Nino | -29,3% |

**5/5 đợt El Nino → median NP YoY ÂM. 3/4 đợt La Nina → median NP YoY DƯƠNG** (đợt La Nina 2010-12
âm nhẹ -4,9%, ngoại lệ duy nhất). Hướng nhất quán, đúng như giả thuyết vật lý.

## 4. Giới hạn thống kê — nói rõ, không ép p-value

- **N = 9 đợt độc lập** (5 El Nino + 4 La Nina) trên gần 20 năm — đúng như ước lượng ban đầu của
  dispatch (10-15), thực tế còn mỏng hơn (9) sau khi áp đúng ngưỡng CPC 5-mùa.
- Sign-test thô trên 5/5 El Nino cùng dấu cho p một phía ≈ 0,03 nếu coi 9 đợt độc lập hoàn toàn —
  **nhưng KHÔNG báo con số này như một kết quả có ý nghĩa thống kê chính thức**: (a) các đợt ENSO
  không độc lập theo nghĩa thống kê chuẩn — chúng tự tương quan theo chu kỳ khí hậu đa năm và trùng
  lặp một phần với các chu kỳ kinh tế vĩ mô khác (2009 GFC, 2020 COVID) mà bản thân cũng ảnh hưởng
  NP; (b) không multiple-testing correction; (c) cỡ mẫu 9 quá nhỏ để tách "hiệu ứng ENSO thuần" khỏi
  các yếu tố đồng thời khác trong cùng giai đoạn.
- Điểm mạnh thực sự của kết quả là **tính nhất quán hướng (directional consistency) + cơ chế vật lý
  đã biết rõ** (El Nino gây hạn hán ở Tây Nguyên/Nam Trung Bộ — đúng nơi VSH/SJD đặt nhà máy — là
  sự kiện khí hậu học đã ghi nhận rộng rãi, không phải suy diễn mới), cộng với **đối chứng NT2/PPC
  không có pattern** → củng cố đây là tín hiệu cơ chế thật, không phải trùng hợp.
- **Không đủ N để fit một mô hình định lượng (hồi quy, ngưỡng tối ưu) hay chạy self-check 0 VND /
  DSR / PBO theo chuẩn quant-research** — N=9 sự kiện quá mỏng cho bất kỳ thủ tục nào trong số đó.
  Đây LÀ LÝ DO chính không đề xuất wire thành backtest/sizing signal.

## 5. Nguồn dữ liệu ONI — CANONICAL từ 2026-09-12 (cập nhật, xem §8)

~~Đã thêm entry `mike/kb/data_registry/feeds/oni_enso_index.md`, status **CANDIDATE-PARTIAL**~~ —
**NÂNG CẤP 2026-09-12 (job `Taylor_20260912_081906`)**: viết `oni_index_feed.py` (root
`WorkingClaude/`) fetch trực tiếp `oni.ascii.txt` (fixed-width ASCII, không qua model tóm tắt
HTML), ghi `data/oni_index.csv` (919 dòng, 1950→JJA 2026). Cross-check máy móc 234 điểm chung
2006-2025 với bản snapshot thủ công cũ: **224/234 khớp tuyệt đối (95,7%)**, 10/234 lệch đúng 0,05
(nhất quán với ghi chú NOAA revise chuẩn ERSSTv5→v6, không phải lỗi transcribe) — bản cũ ĐÃ ĐỦ TIN
CẬY cho phân tích §3.2 ở trên, không cần chạy lại. Registry `oni_enso_index.md` đã cập nhật status
→ CANONICAL. Cron tự động refresh hàng tháng ĐỀ XUẤT nhưng CHƯA CÀI (permission classifier chặn
`crontab` trong sandbox agent) — xem chi tiết + dòng cron đề xuất trong registry file.

## 8. Dose-response ONI-peak vs mức độ thiệt hại NP — bổ sung 2026-09-12 (job `Taylor_20260912_081906`)

**Câu hỏi bổ sung của user**: đợt El Nino 2026-27 đã CONFIRMED bởi NOAA CPC/WMO/KTTV VN
(Niño-3.4 ANOM tháng 8/2026 = +1,80°C, CPC dự >90% chance "very strong event", 75% chance vượt
+2,5°C — nếu đúng sẽ ngang hàng đợt kỷ lục 2015-16). Trước khi suy diễn "El Nino lịch sử lớn ⇒
thiệt hại NP lớn", test xem quan hệ liều-lượng (dose-response) này có thật trong dữ liệu VSH/SJD
hay không, dùng đúng 9 đợt ENSO độc lập đã xác định ở §3.2 (không tạo thêm biến số mới).

### 8.1 Test trên 5 đợt El Nino (ONI peak, lấy max ANOM trong khoảng năm đã gán ở §3.2, nguồn
`data/oni_index.csv` mới — xem §5)

| Đợt | ONI peak (mùa đỉnh) | \|NP YoY thiệt hại\| của đợt |
|---|---|---|
| 2006-07 | 0,88 (OND2006) | 48,0% |
| 2009-10 | 1,50 (NDJ2009) | 25,5% |
| 2014-16 | **2,59** (NDJ2015 — đợt lịch sử) | **3,1% (NHẸ NHẤT)** |
| 2018-20 | 1,05 (NDJ2018) | **52,4% (NẶNG NHẤT)** |
| 2023-24 | 1,99 (NDJ2023) | 29,3% |

**Pearson r = −0,936, Spearman ρ = −0,8 (N=5)** — tức là ONI đỉnh CÀNG LỚN thì thiệt hại NP có xu
hướng CÀNG NHỎ, **NGƯỢC** với giả thuyết ngây thơ "El Nino càng mạnh càng tàn phá". Đây chính là
quan sát user đã nêu (2015-16 ONI cao nhất nhưng thiệt hại nhẹ nhất; 2018-20 ONI thấp hơn nhưng
thiệt hại nặng nhất) — **được số liệu xác nhận, không phải cảm tính**.

**Robustness check (leave-one-out, N=4 mỗi lần bỏ 1 đợt)**: r dao động **−0,825 đến −0,969** ở cả
5 lần bỏ — quan hệ ngược dấu KHÔNG phải do 1 điểm ngoại lai (vd bỏ chính đợt 2014-16 vẫn còn
r=−0,825). Điều này củng cố quan sát là thật trong 5 điểm này, nhưng **N=5 sau leave-one-out chỉ
còn N=4 — không đủ để tuyên bố "confirmed" theo bất kỳ chuẩn thống kê nào**, chỉ là "không phải
artifact của một điểm duy nhất".

### 8.2 Test mở rộng — có phải hiện tượng chỉ trong El Nino, hay cả La Nina cũng vậy?

Gộp cả 4 đợt La Nina (dùng |ONI trough| vs |NP YoY|, N=9 tổng): **Pearson r = −0,34, Spearman
ρ = −0,3** — vẫn âm nhẹ (không có bằng chứng "biên độ ONI càng lớn thì thiệt hại càng lớn" ở cả
2 chiều gộp lại) nhưng yếu hơn nhiều so với riêng El Nino, và với N=9 hỗn hợp 2 chiều thì hoàn
toàn không có ý nghĩa thống kê. Quan hệ hướng (El Nino ⇒ âm, La Nina ⇒ dương — đã biết ở §3.2) vẫn
đúng: signed ONI vs signed NP_YoY toàn bộ 9 đợt cho r=−0,672 (đúng hướng vật lý, không phải phát
hiện mới).

### 8.3 Diễn giải — KHÔNG ép kết luận định lượng, N=5 quá mỏng

- **KHÔNG kết luận "ONI đỉnh càng cao thì thiệt hại càng nhẹ" là một QUY LUẬT** — với N=5, một
  quan hệ mạnh (kể cả robust qua leave-one-out) vẫn hoàn toàn có thể là trùng hợp của lịch sử khí
  hậu 20 năm gần đây, không phải cơ chế nhân quả. Không multiple-testing correction, không kiểm
  soát được các biến gây nhiễu đồng thời (xem dưới).
- **Giả thuyết khả dĩ (KHÔNG kiểm chứng được với dữ liệu hiện có) cho vì sao ONI đỉnh KHÔNG dự báo
  tốt mức thiệt hại**: (a) ONI đo SST Thái Bình Dương nhiệt đới — không phải lượng mưa VN trực
  tiếp; **thời điểm** El Nino đạt đỉnh so với mùa mưa Tây Nguyên/Nam Trung Bộ (Q3-Q4) có thể quan
  trọng hơn BIÊN ĐỘ đỉnh (đợt 2014-16 đỉnh vào NDJ2015 — sau mùa tích nước chính; đợt 2018-20 đỉnh
  sớm NDJ2018 — đúng lúc mùa tích nước); (b) **base effect kế toán**: NP YoY phụ thuộc NP quý cùng
  kỳ năm trước — nếu 2017 là năm nước thuận lợi bất thường (NP cao), NP YoY 2018 sẽ trông tệ hơn
  bản chất thủy văn; (c) mực nước hồ chứa TỒN KHO đầu mỗi đợt (không quan sát được trong
  `ticker_financial`) — hồ đầy sẵn từ đợt La Nina liền trước có thể đệm được một đợt El Nino ngắn
  dù ONI cao; (d) thay đổi công suất lắp đặt/cơ cấu doanh thu của VSH/SJD qua 20 năm làm NP YoY
  không so sánh được xuyên thời gian như một đại lượng cố định. **Đây là các giả thuyết CHƯA kiểm
  định, ghi lại để ai làm tiếp biết hướng đào sâu, không phải kết luận.**
- **Hệ quả thực tế cho câu hỏi gốc**: KHÔNG có cơ sở dùng độ lớn ONI dự báo hiện tại (2026, đang
  hướng tới mức lịch sử) để suy ra thiệt hại NP sẽ NHẸ (theo hướng tương quan quan sát được) hay
  NẶNG (theo trực giác ngây thơ) — dữ liệu N=5 chỉ đủ nói "không có quan hệ liều-lượng đơn điệu rõ
  ràng theo hướng trực giác", không đủ để thay thế bằng một quy luật khác.

### 8.4 Ba kịch bản NP quý VSH/SJD, Q4/2026-Q1/2027 (KHÔNG phải điểm dự báo đơn)

Neo vào 3 mốc lịch sử cụ thể trong bảng 5 đợt El Nino đã có (không suy diễn thêm biến mới):

| Kịch bản | Neo theo đợt | NP YoY dự kiến (median lịch sử của đợt) | Điều kiện hợp lý nếu |
|---|---|---|---|
| **A — Nhẹ** | 2014-16 (ONI đỉnh cao nhất lịch sử, thiệt hại nhẹ nhất) | ≈ **−3%** | Hồ chứa đầu mùa còn đầy (La Nina 2020-23 kéo dài trước đó); đỉnh El Nino rơi ĐÚNG sau mùa tích nước chính, giống 2014-16 |
| **B — Trung vị** | Trung vị 5 đợt El Nino {−48,0%; −25,5%; −3,1%; −52,4%; −29,3%} | ≈ **−29%** | Không có thông tin thêm để nghiêng về kịch bản nào — dùng làm trung tâm phân bố |
| **C — Xấu** | 2018-20 (ONI thấp hơn nhưng thiệt hại nặng nhất) hoặc 2006-07 | ≈ **−48% đến −52%** | Đỉnh El Nino rơi ĐÚNG mùa tích nước (Q3-Q4/2026, có vẻ ĐANG xảy ra theo lịch dự báo CPC/WMO — OND-2026 dự đỉnh); hồ chứa đầu mùa đã cạn do dòng chảy giảm từ tháng 5/2026 (đúng cảnh báo KTTV VN) |

**Lưu ý quan trọng**: kịch bản C có xác suất KHÔNG THẤP hơn kịch bản A chỉ vì §8.1 tìm thấy tương
quan ngược — thời điểm đỉnh dự báo OND-2026 (đúng mùa tích nước, giống kịch bản xấu 2018-20 hơn là
2014-16 vốn đỉnh vào NDJ) và cảnh báo dòng chảy giảm từ tháng 5/2026 của KTTV VN (đã nêu trong tin
CPC/WMO/VN — xem dispatch) đều là dấu hiệu ĐỊNH TÍNH hướng về kịch bản B/C, không phải A. Không
dùng biên độ ONI một mình để chọn kịch bản.

### 8.5 Không đổi kết luận §6/§7 — vẫn thuần watch-item

VSH/SJD không nằm trong bất kỳ book/sleeve đang trade (đã grep xác nhận, không phải lo vị thế hiện
tại). Không đề xuất trade action. Bổ sung §8 chỉ để nâng cấp nowcast overlay ĐỊNH TÍNH đã đề xuất ở
§6 — khi ai đó định giá/mua VSH/SJD trong giai đoạn Q4/2026-Q1/2027, tham chiếu bảng 3 kịch bản
trên thay vì coi biên độ ONI hiện tại (dù đang hướng lịch sử) là tín hiệu "chắc chắn nhẹ" hay
"chắc chắn nặng".

## 6. Trả lời câu hỏi "nowcast overlay hay sizing signal?"

**NOWCAST OVERLAY MỀM, không phải sizing signal, và ngay cả nowcast cũng nên giữ Ở MỨC ĐỊNH TÍNH
(cờ cảnh báo), không phải công thức điều chỉnh số:**
- Cải thiện được: khi biết đang ở giữa một đợt El Nino CONFIRMED (đã qua ngưỡng 5 mùa, tức là biết
  chắc, không phải đoán), có cơ sở hạ kỳ vọng NP quý tới của VSH/SJD cụ thể trước khi ra earnings —
  giống tinh thần DRI nowcast overlay nhưng CHỈ áp cho 2 mã này, KHÔNG áp cho REE/POW (không tách
  được segment) hay NT2/PPC (đối chứng, không có cơ chế).
- KHÔNG đủ cơ sở để: (a) biến thành sizing rule (N=9 quá mỏng để calibrate ngưỡng/trọng số), (b)
  override kết luận "mature utility = LENS not BOOK" của `energy_valuation_framework.md` — utility
  vẫn là defensive laggard, biết thêm ENSO không làm nó thành alpha book.
- Đề xuất cụ thể nếu muốn dùng: khi DT5G/macro-view định kỳ (Taylor's macro interpreter role) phát
  hiện một đợt El Nino/La Nina MỚI CONFIRMED (đạt ngưỡng 5 mùa) và VSH/SJD đang có vị thế/candidate
  trong sổ nào đó → ghi 1 finding cảnh báo định tính lên bus, không tự động sizing.

## 7. Không wire gì vào production

Đây là nghiên cứu khám phá theo yêu cầu, KHÔNG chạm `filter.json`, không chạm `rating_8l.py`, không
đổi `energy_valuation_framework.md` (giữ nguyên, chỉ bổ sung tham chiếu memo này). Không cần
quant-skeptic verify vì không có claim backtest/edge nào được đề xuất wire.

## 9. Bắc Bộ — bổ sung 2026-09-12 (job `Taylor_20260912_084541`)

**Câu hỏi bổ sung của user**: §1-§8 chỉ có VSH (Nam Trung Bộ) + SJD (Tây Nguyên/Sê San). Thủy điện
Bắc Bộ có chịu ảnh hưởng El Nino tương tự không?

### 9.1 Xác định universe Bắc Bộ — tra thật, không đoán

- **Hòa Bình / Sơn La / Lai Châu** (3 nhà máy lớn nhất miền Bắc, sông Đà): **XÁC NHẬN không niêm
  yết riêng lẻ** — WebSearch xác nhận rõ đây là các công ty do EVN vận hành trực tiếp ("Công ty
  Thủy điện Sơn La", "Công ty Thủy điện Hòa Bình") không phải công ty đại chúng có mã trên
  HOSE/HNX/UPCOM. Khớp với việc không tìm thấy mã nào trong số này ở `tav2_bq.ticker_financial`.
- **TBC** (CTCP Thủy điện Thác Bà, Yên Bái, sông Chảy) — niêm yết HOSE 19/10/2009 (trước đó HNX
  từ 29/08/2006). **Bắc Bộ, dùng được.**
- **HJS** (CTCP Thủy điện Nậm Mu, xã Tân Thành, Bắc Quang, **Hà Giang**) — niêm yết HNX 20/12/2006.
  WebSearch xác nhận vị trí: "nơi có lượng mưa hàng năm lớn nhất miền Bắc, trung bình 3.500mm/năm."
  **Bắc Bộ, dùng được.**
- Cả 2 mã đủ dữ liệu `NP_R` trong `ticker_financial`: TBC 67 quý (2009Q2→2025Q4), HJS 72 quý
  (2008Q1→2025Q4) — coverage tương đương VSH/SJD ở §1.2.

### 9.2 Phương pháp — giữ NGUYÊN như §2, đổi nguồn ONI sang bản CANONICAL mới

Theo đúng chỉ đạo dispatch: dùng `data/oni_index.csv` (fetch trực tiếp NOAA `oni.ascii.txt` qua
`oni_index_feed.py`, xem §5), KHÔNG dùng lại bản snapshot thủ công `oni_index_manual_20260912.csv`
của §1-§8 (dù đã biết 2 bản khớp 95,7%). Cùng rule CPC 5-mùa-liên-tiếp, cùng lag 2 quý, cùng cửa sổ
2005-2025 (loại 2026, sau knowledge cutoff — xem §1.1). Script lưu
`research/oni_bacbo_analysis_20260912.py`, panel merge lưu
`research/hydro_oni_merged_panel_bacbo_20260912.csv`, tài chính thô BQ lưu
`research/hydro_bacbo_financials_20260912.csv` — tái lập được không cần chạy lại BQ.

### 9.3 Kết quả — event-level (N=đợt ENSO độc lập, không pseudo-replicate)

Trong cửa sổ dữ liệu TBC/HJS có (từ 2008-09), chỉ phủ được **4 đợt El Nino + 4 đợt La Nina** (đợt
El Nino 2006-07 sớm hơn cả 2 mã bắt đầu có dữ liệu tài chính đủ tốt → loại, không phải bỏ sót):

| Đợt (năm) | Phase | Bắc Bộ (TBC+HJS) median NP YoY của đợt | Nam Trung Bộ/Tây Nguyên (VSH+SJD), cùng đợt |
|---|---|---|---|
| 2009-10 | El Nino | **-53,7%** | -25,5% |
| 2010-12 | La Nina | +25,2% | -4,9% |
| 2014-16 | El Nino | **+20,8%** | -3,1% |
| 2017-18 | La Nina | +13,1% | +28,9% |
| 2018-20 | El Nino | **+0,3%** | -52,4% |
| 2020-23 | La Nina | +3,3% | +18,6% |
| 2023-24 | El Nino | **-2,3%** | -29,3% |

**Bắc Bộ El Nino (N=4): 2 âm mạnh (-53,7%, -2,3%), 2 dương (+20,8%, +0,3%) — TRÁI NGƯỢC với NTB/TN
nơi 5/5 đợt El Nino đều âm (§3.2).** Median gộp 4 đợt ≈ -1,0% (gần như bằng 0), so với NTB/TN cùng 4
đợt trùng lịch là median rõ rệt âm. **Bắc Bộ La Nina (N=4): cả 4 đợt đều dương** (+3,3% đến +25,2%)
— hướng nhất quán như NTB/TN nhưng biên độ giảm dần theo thời gian, không đọc được xu hướng rõ.

### 9.4 Cơ chế khí hậu học — El Nino KHÔNG đồng nhất tác động cả nước, có trích dẫn

Đây là điểm mấu chốt trả lời câu hỏi user, không suy diễn từ dữ liệu tài chính mỏng ở trên:
nguồn khí tượng VN (dự báo mùa, tổng hợp bởi báo chí trong nước dẫn KTTV/NCHMF) ghi nhận **El Nino
gây thiếu hụt mưa 25-50% trên PHẦN LỚN cả nước (đặc biệt Nam Trung Bộ/Tây Nguyên/Nam Bộ — đúng nơi
VSH/SJD đặt nhà máy) nhưng KHÔNG đồng nhất ở Bắc Bộ** — một dự báo mùa cụ thể (El Nino 2023-24, dẫn
qua Dân Việt) ghi: *"Bắc Bộ mưa nhiều hơn... một số khu vực giảm lượng mưa tới 40%"* — tức CÙNG một
đợt El Nino, Bắc Bộ có thể lượng mưa **CAO HƠN trung bình nhiều năm 5-30%** trong khi vùng khác thấp
hơn tới 40%. Lý do vật lý (theo các nguồn dự báo mùa VN): mùa mưa Bắc Bộ (tháng 5-10, đỉnh tháng 7-8)
chịu chi phối chính bởi **hội tụ gió mùa + bão/áp thấp nhiệt đới trên Biển Đông**, không phải chỉ
teleconnection SST Thái Bình Dương như cơ chế hạn hán El Nino cổ điển ở Nam Trung Bộ/Tây
Nguyên/ĐBSCL — nên El Nino có thể vẫn có bão/front gây mưa nhiều cho Bắc Bộ ngay cả khi gây hạn nơi
khác. Đây là ghi nhận khí tượng học có nguồn, không phải giả thuyết tự suy ra từ N=4.

*Nguồn: tổng hợp dự báo mùa El Nino trên các trang tin trong nước dẫn KTTV/NCHMF, ví dụ
[danviet.vn](https://danviet.vn/bac-bo-mua-nhieu-hon-tin-du-bao-moi-nhat-mot-so-khu-vuc-giam-luong-mua-toi-40-cap-nhap-el-nino-d1436181.html)
— đọc qua WebSearch tóm tắt, KHÔNG đọc trực tiếp bản gốc KTTV/NCHMF (không truy cập được từ sandbox
này); coi là tham khảo định hướng, không phải trích dẫn khoa học chính thức.*

### 9.5 Giới hạn dữ liệu — nói rõ, không ép kết luận

- **N=4 đợt El Nino + N=4 đợt La Nina cho Bắc Bộ** — còn mỏng hơn cả N=9 (5+4) của NTB/TN ở §4,
  vốn đã bị coi là "không đủ cho bất kỳ thủ tục thống kê chuẩn nào". Không chạy sign-test/tương
  quan gì thêm trên N=4 — vô nghĩa.
- **TBC có NP_R biến động cực mạnh giữa các quý** (quan sát trực tiếp trên panel: +1171% YoY
  2011Q1, -786% 2017Q4, +831% 2020Q4 — do NP quý gốc rất nhỏ ở mẫu số, hoặc quý bảo trì/sự cố tổ
  máy) — nhiễu nền cao hơn hẳn VSH/SJD, khiến median từng đợt (dùng ở bảng 9.3) vẫn nhạy với 1-2
  quý bất thường trong đợt 6-12 quý. Đây là hạn chế CỦA DỮ LIỆU công ty nhỏ vốn hóa thấp/thanh
  khoản thấp (cả TBC lẫn HJS đều nằm trong nhóm low-liq theo `data/power_lens.md`), không phải lỗi
  phương pháp.
- **KHÔNG kết luận "Bắc Bộ miễn nhiễm El Nino"** — chỉ 2/4 đợt El Nino Bắc Bộ có NP âm, không phải
  0/4 — chỉ đủ nói quan hệ YẾU HƠN và ÍT NHẤT QUÁN HƠN so với NTB/TN, khớp hướng với cơ chế khí hậu
  học ở §9.4 (El Nino không đồng nhất gây hạn ở Bắc Bộ như ở Nam Trung Bộ/Tây Nguyên).

### 9.6 Kết luận — KHÔNG mở rộng nowcast overlay §6 sang TBC/HJS

Overlay ENSO định tính đề xuất ở §6 (áp cho VSH/SJD khi có đợt El Nino/La Nina CONFIRMED) **KHÔNG
áp dụng cho TBC/HJS** — cả cơ chế khí hậu học (§9.4, El Nino không nhất quán gây hạn Bắc Bộ) lẫn
dữ liệu tài chính (§9.3, 2/4 đợt El Nino Bắc Bộ có NP dương) đều không ủng hộ. Nếu tương lai có ai
định giá/theo dõi TBC/HJS mùa El Nino 2026-27 đang hình thành (§8.4), **không áp cùng logic "El
Nino ⇒ hạ kỳ vọng NP"** đã dùng cho VSH/SJD — thiếu cơ sở cả về cơ chế lẫn số liệu. TBC/HJS không
nằm trong bất kỳ book/sleeve đang trade (đã grep xác nhận cùng §8.5). Không đề xuất trade action,
không wire production — giữ nguyên phạm vi §7.

## 10. TV1/PECC1 — bổ sung 2026-09-12 (job `Taylor_20260912_085911`)

**Câu hỏi bổ sung của user**: TV1 (PECC1, sở hữu 100% thủy điện Sông Bung 5, 57MW, Quảng Nam) là
**vị thế thật đang giữ** (discretionary fear-buy, tranche 500cp, thesis SOTP/asset-value —
`research/tv1_pecc1_sotp_20260723.md`). El Nino 2026-27 có rủi ro gì tới NP quý tới / có lung lay
luận điểm SOTP không?

### 10.1 Dữ liệu — đủ LỊCH SỬ (65 quý) nhưng KHÔNG đủ SẠCH để test định lượng

TV1 có `NP_R` liên tục trong `ticker_financial` từ **2010Q2 đến 2026Q2** (65 quý) — không phải vấn
đề niêm yết gần đây, coverage dài hơn cả VSH/SJD/TBC/HJS. Nhưng TV1 **không phải thuần thủy điện**:
theo `tv1_pecc1_sotp_20260723.md` §1, mảng **tư vấn xây dựng điện** (doanh thu ~490-540 tỷ/năm,
biên mỏng, AR 295 tỷ phụ thuộc thu hồi từ EVN/dự án nhà nước) **lớn hơn hẳn** doanh thu thủy điện
(sản lượng thiết kế 187 triệu kWh/năm — ước revenue hydro cỡ 150-220 tỷ/năm tuỳ giá PPA, **ước
lượng, không có số tách mảng thật**) — và `ticker_financial` chỉ có NP hợp nhất, không tách được
segment. **Đây đúng loại vấn đề đã loại REE/POW ở §1.2** ("NP hợp nhất, không tách được thủy điện"),
áp y hệt cho TV1.

Chạy test (script `research/oni_tv1_analysis_20260912.py`, panel
`research/hydro_oni_tv1_panel_20260912.csv`, cùng phương pháp/nguồn ONI/lag 2 quý như §2, restrict
POST-COD ≥2013Q3 vì SB5 tổ 2 COD 19/7/2013 — trước đó hydro CHƯA vận hành):

| Phase (lag 2Q) | N quý (post-COD) | Median NP_R | Std |
|---|---|---|---|
| El Nino | 16 | **+0,529** | 2,23 |
| Neutral | 24 | +0,313 | 4,95 |
| La Nina | 11 | **−0,256** | 4,84 |

**Median NGƯỢC HƯỚNG với VSH/SJD** (El Nino dương thay vì âm, La Nina âm thay vì dương), và std
(2,2–4,9, tức 220-490%/quý) lớn hơn nhiều lần biên độ std của VSH/SJD (~biến động chục % không phải
trăm-nghìn %). Theo đợt độc lập post-COD: El Nino 2014-16 median +13,9%, 2018-20 +101,3% (nhiễu bởi
1 quý −1458%), 2023-24 **+487%** (nhiễu bởi 1 quý +1822%). Các giá trị outlier hàng nghìn %/quý chỉ
có thể đến từ **base effect kế toán ở mảng tư vấn** (NP quý gốc nhỏ, dao động mạnh theo lịch nghiệm
thu/thanh toán dự án EVN — đúng cơ chế đã nêu ở `tv1_pecc1_sotp` §1 "đây là nơi rủi ro kế toán trú"),
**không thể là tín hiệu thuỷ văn** (sản lượng phát điện không thể đổi 1000%+ giữa 2 quý liền kề).

**Kết luận dữ liệu: TV1 KHÔNG dùng được cho test định lượng ENSO — loại khỏi bảng, giống REE/POW,
lý do business-mix chứ không phải N/lịch sử.** Không ép thêm biến (vd lọc theo NP_P0 tuyệt đối thay
vì NP_R) vì đó là tạo phương pháp mới ngoài phạm vi việc được giao.

### 10.2 Quảng Nam (Sông Bung 5) — vùng khí hậu, tra thật

WebSearch xác nhận: **Đà Nẵng — Quảng Nam — Quảng Ngãi — Bình Định — Phú Yên — Khánh Hoà — Ninh
Thuận cùng một "vùng khí hậu Nam Trung Bộ"** trong phân vùng khí hậu VN chuẩn — **CÙNG vùng với
VSH** (Vĩnh Sơn-Sông Hinh, Bình Định/Phú Yên). Mùa khô tháng 1-8 (Quảng Nam cụ thể: khô tháng 2-8),
mùa mưa tháng 9-12 (Quảng Nam: tháng 10-12) — cùng chu kỳ mùa với VSH, khác hẳn Bắc Bộ (mùa mưa
tháng 5-10, đỉnh 7-8, cơ chế hội tụ gió mùa/bão Biển Đông — §9.4). Tin thời sự El Nino 2026-27 hiện
tại (WebSearch) xác nhận rõ: **"mưa giảm 25-50% từ cuối 2026, hạn hán nghiêm trọng ở Nam Trung Bộ và
ĐBSCL"** — Quảng Nam nằm TRONG vùng cảnh báo này, không phải Bắc Bộ ngoại lệ.

**Kết luận cơ chế: về mặt khí hậu học, Sông Bung 5 chịu ĐÚNG cơ chế hạn hán El Nino cổ điển như
VSH/SJD** (teleconnection SST → thiếu mưa Nam Trung Bộ/Tây Nguyên), khác hẳn TBC/HJS Bắc Bộ. Nếu
TV1 có được dữ liệu sạch để test (không có), hướng giả thuyết đúng nhất vẫn là "El Nino → hạn →
giảm sản lượng SB5" — chỉ là NP hợp nhất của TV1 không đo được hiệu ứng này vì bị mảng tư vấn che
lấp hoàn toàn.

### 10.3 Có lung lay luận điểm SOTP không? — KHÔNG, và giải thích tại sao bằng số

Thesis TV1 (`tv1_pecc1_sotp_20260723.md` §3-4) là **SOTP asset-value dài hạn**, neo vào 3 mỏ neo:
DCF hydro 30 năm (FCF ~110-140 tỷ/năm, chiết khấu 10-11% → EV 1.000-1.300 tỷ), comp M&A Nậm Nơn
(~1.824 tỷ), và giá đấu thất bại lịch sử 1.390 tỷ — **không phải earnings-timing/momentum quý**.

- Một quý (hay cả năm) NP hydro giảm mạnh vì El Nino là **1 điểm dữ liệu trong dòng tiền 30 năm**.
  Minh hoạ độ lớn (ước tính, KHÔNG phải số chính xác — không có FCF hydro tách mảng thật theo quý):
  giả sử 1 năm El Nino xấu cắt 50% FCF hydro của năm đó (biên độ ngang mức thiệt hại tệ nhất quan
  sát ở VSH/SJD, §3.2 đợt 2018-20 là −52,4%) — mất khoảng 0,5 × 125 tỷ ≈ 60 tỷ dòng tiền của ĐÚNG 1
  năm trong chuỗi 30 năm, chiết khấu về hiện tại ở năm thứ ~13-14 của đời dự án ≈ **15-20 tỷ**, so
  với EV hydro trung tâm 1.000-1.300 tỷ — dưới **2% EV**. Đây là toán minh hoạ bậc-độ-lớn để cho
  thấy tỷ lệ, không phải một con số dự báo chính xác.
- **Net debt gần 0** (LtDebt 0,4 tỷ 2026Q1, đã trả hết nợ dự án) — không có đòn bẩy khuếch đại 1 năm
  dòng tiền yếu thành rủi ro covenant/thanh khoản như một công ty còn vay dự án nặng.
- Biên an toàn SOTP hiện tại (66% ở kịch bản bảo thủ nhất, tư vấn định giá = 0) đủ dày để hấp thụ
  một cú sốc dòng tiền 1 năm cỡ vài % EV mà không đổi kết luận "deep-value asset-backed".
- **Rủi ro THẬT sự có thể lung lay thesis không phải El Nino** — mà là 2 rủi ro đã nêu ở
  `tv1_pecc1_sotp` §6: (1) overhang pháp lý/kiểm toán (Big4 từ chối FY2026, CT bị khởi tố — ảnh
  hưởng khả năng monetize/niêm yết, không phải giá trị tài sản), (2) thanh khoản (ADV ~1 tỷ/ngày,
  giới hạn quy mô/exit). Một quý NP xấu do El Nino **KHÔNG** thuộc nhóm rủi ro này.

**Kết luận rõ ràng (thông tin, không phải khuyến nghị hành động)**: El Nino 2026-27 là rủi ro NP
quý ngắn hạn hợp lý về mặt cơ chế (§10.2) nhưng **không đủ lớn để lung lay luận điểm đầu tư SOTP**
của TV1 — biến động dòng tiền 1 năm là nhiễu trong định giá 30 năm, không phải thay đổi cấu trúc.
Không đề xuất thoát vị thế hay đổi tranche/exit rule (ngoài phạm vi việc được giao) — quyết định
thuộc user.

### 10.4 Không wire gì vào production

Cùng phạm vi §7 — không chạm `filter.json`/`rating_8l.py`/tranche-exit rule của TV1. TV1 là
discretionary special-situation ngoài book V2.4 hệ thống, đã ghi rõ ở `tv1_pecc1_sotp_20260723.md`
§6. Không cần quant-skeptic verify (không có claim backtest/edge đề xuất wire).
