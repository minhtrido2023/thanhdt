# Breadth của prior-rally (không phải return chỉ số) — kiểm định tinh chỉnh giả thuyết 2018 vs 07/2026

> Job `Taylor_20260831_054906` · 2026-08-31 · RESEARCH-ONLY, không wire production, không đổi
> DT5G/CAPIT. Tinh chỉnh trực tiếp từ job vừa bị bác bỏ (`Taylor_20260831_053055`,
> `vn_prior_trend_meanreversion_hypothesis_20260831`) — job đó đo bằng RETURN CHỈ SỐ VNINDEX và kết
> luận 2018 với 07/2026 "giống hệt nhau" (48% vs 65% return 12 tháng). Job này đo BREADTH: bao
> nhiêu % mã trong `ticker_prune` thực sự tham gia đà tăng, tách biệt với con số chỉ số có trọng số
> vốn hoá. Nguồn: BigQuery `tav2_bq.ticker_prune` (Close), joined lấy giá tại đỉnh và tại các mốc
> lùi (12 tháng / 133 ngày / YTD).

## Tóm tắt 1 dòng

**Giả thuyết ĐÚNG một phần hẹp (breadth ngắn hạn trước đỉnh 2026 thực sự tệ hơn 2018), nhưng CƠ CHẾ
CỤ THỂ mà user đề xuất — "nhóm cổ phiếu đầu tư công/hạ tầng được nhà nước chỉ định kéo chỉ số" —
bị BÁC BỎ TRỰC TIẾP bằng dữ liệu**: cổ phiếu nhóm hạ tầng/EPC đầu tư công (CII, VCG, HHV, LCG,
FCN, C4G, CTD, CTR, DPG, HBC, G36, VC7, NHA, HID) **KÉM HƠN** trung vị toàn thị trường trong cả 2
cửa sổ dẫn tới đỉnh 18/05/2026 (12 tháng: cohort +5,26% vs trung vị toàn universe +10,05%; 133 ngày:
cohort -6,20% vs trung vị -3,12%) — nhóm này không hề "kéo" chỉ số, nó còn tệ hơn thị trường chung.
Đợt nhóm này THỰC SỰ outperform mạnh là **2022** (median +130,1% trong 133 ngày trước đỉnh 06/01/2022
vs +28,15% toàn universe) — đúng như lịch sử "chủ đề đầu tư công" đã biết, nhưng đó là chu kỳ TRƯỚC,
không phải 2026.

---

## Bước 1 — Breadth 12 tháng trước đỉnh, N=6 episode (khớp method job trước)

Universe: `ticker_prune` tại đúng ngày đỉnh, join giá tại ngày gần nhất ±12 ngày quanh mốc đỉnh−365
ngày. Loại `VNINDEX`/`VN30` (pseudo-ticker trong bảng) khỏi thống kê cổ phiếu, dùng riêng cho cột
VNINDEX.

| Episode (đỉnh) | N mã | % mã return dương | Median return 12mo | VNINDEX return 12mo | Gap (VNINDEX − median) |
|---|---|---|---|---|---|
| 2007-03-12 | 9 | 100,0% | +132,29% | +175,80% | +43,51pp |
| 2009-10-22 | 93 | 95,7% | +92,93% | +66,47% | **-26,46pp** |
| 2018-04-09 | 170 | 71,2% | +24,67% | +65,01% | **+40,33pp** |
| 2020-01-22 | 153 | 51,6% | +2,35% | +9,37% | +7,02pp |
| 2022-01-06 | 274 | 93,4% | +67,26% | +33,71% | **-33,55pp** |
| **2026-05-18** | 230 | 68,7% | +10,05% | +48,73% | **+38,68pp** |

**Quan sát then chốt Bước 1**: trên cửa sổ 12 tháng cố định, gap của 07/2026 (+38,68pp) và 2018
(+40,33pp) **GẦN NHƯ GIỐNG HỆT NHAU** — cùng dấu hiệu "rally hẹp/index-led" ở mức độ tương đương.
Đây là bằng chứng NGƯỢC với giả thuyết user ở đúng thước đo user đề xuất ban đầu (12 tháng): nếu chỉ
nhìn 12 tháng, 2018 **CŨNG** là một rally hẹp, không phải "đa phần cổ phiếu đều tăng mạnh" như user
mô tả. `%mã dương` cũng gần bằng nhau (71,2% vs 68,7%). 2009 và 2022 (gap ÂM lớn, tức median mã tăng
MẠNH HƠN chỉ số — rally RỘNG thật sự) mới là 2 case khớp mô tả "broad-based" của user, không phải
2018.

## Bước 1b — Cửa sổ NGẮN khớp độ dài với YTD 2026 (133 ngày, apples-to-apples)

Vì "133 ngày" (khoảng cách 05/01/2026 → 18/05/2026) ngắn hơn nhiều so với 12 tháng, so 2 cửa sổ khác
độ dài trực tiếp là không công bằng. Lặp lại đúng cùng phương pháp Bước 1 nhưng lùi 133 ngày (thay
vì 365) từ mỗi đỉnh, để so sánh "chặng cuối trước đỉnh" giữa các episode trên cùng thang thời gian.

| Episode | N mã | % mã return ÂM | Median return 133d | VNINDEX return 133d | Gap |
|---|---|---|---|---|---|
| 2007-03-12 | 16 | 0,0% | +131,79% | +128,47% | -3,32pp |
| 2009-10-22 | 111 | 14,4% | +35,61% | +22,06% | -13,54pp |
| **2018-04-09** | 194 | **45,4%** | +3,15% | +28,31% | **+25,16pp** |
| 2020-01-22 | 168 | 54,8% | -2,03% | +2,29% | +4,31pp |
| 2022-01-06 | 319 | 9,1% | +28,15% | +17,48% | -10,67pp |
| **2026-05-18** | 231 | **57,1%** | -3,12% | +7,80% | +10,92pp |

**Quan sát Bước 1b — kết quả TRÁI CHIỀU tuỳ thước đo**:
- **% mã ÂM**: 2026 (57,1%) > 2018 (45,4%) — **ủng hộ** giả thuyết user, chặng cuối trước đỉnh
  07/2026 có breadth tệ hơn 2018 thật.
- **Gap tuyệt đối (pp)**: 2026 (+10,92pp) < 2018 (+25,16pp) — **ngược** với "trực giác" narrow-
  rally, vì VNINDEX tự nó tăng ÍT HƠN NHIỀU trong cửa sổ 2026 (+7,80% vs +28,31% của 2018) nên
  khoảng cách tuyệt đối tính bằng pp nhỏ hơn dù thị trường "phân hoá" nhiều hơn.
- **Diễn giải đúng**: 2018 là "chỉ số tăng MẠNH, đa số mã tăng ít hơn nhưng vẫn phần lớn DƯƠNG"
  (54,6% mã dương) — kiểu narrow-nhưng-vẫn-broad-participation. 2026 là "chỉ số tăng NHẸ, nhưng
  ĐA SỐ mã (57,1%) thực sự ÂM" — kiểu khác hẳn: không phải "hẹp nhưng vẫn tham gia", mà là "phần
  lớn thị trường ĐÃ RÚT LUI trong khi 1 nhóm nhỏ giữ chỉ số không sập". **% mã âm là thước đo phù
  hợp hơn gap tuyệt đối để phân biệt 2 case này** — gap tuyệt đối bị nhiễu bởi biên độ tăng khác
  nhau của chính VNINDEX.

## Bước 2 — Xác minh trực tiếp claim YTD 2026 (05/01/2026 → 18/05/2026, lịch, không lùi 133 ngày)

Dùng đúng 2 ngày giao dịch đầu/cuối cửa sổ (05/01/2026 phiên đầu năm sau nghỉ Tết dương, 18/05/2026
= ngày đỉnh):

- **N = 231 mã** trong `ticker_prune`
- **57,1% mã có return ÂM** so với đầu năm (132/231 mã)
- **42,9% mã dương**
- **Median return toàn universe: -3,12%**
- **VNINDEX cùng kỳ: +7,80%**
- **Gap: +10,92pp**

**Đây là bằng chứng TRỰC TIẾP xác nhận phần "breadth xấu" của giả thuyết user**: đúng là hơn một
nửa số mã trong `ticker_prune` giảm giá từ đầu năm 2026 đến đỉnh chỉ số 18/05/2026, trong khi
VNINDEX vẫn dương gần 8%. Số liệu này khớp method Bước 1b (57,1% cùng con số, do 05/01 gần trùng mốc
133-ngày-lùi).

## Bước 3 — Nhóm "cổ phiếu đầu tư công/hạ tầng nhà nước chỉ định" có thực sự kéo chỉ số? **BÁC BỎ**

**Xác định cohort**: tra `ICB_Code` thật trong BQ (không đoán) — nhóm Xây dựng & Vật liệu
(`ICB_Code=2357`) giao với `ticker_prune` tại 18/05/2026 cho 32 mã; lọc còn lại **14 mã** là các
nhà thầu EPC/hạ tầng lớn, tên quen thuộc với chủ đề đầu tư công VN 2021-2022 và 2025-2026:
**CII, VCG, HHV, LCG, FCN, C4G, CTD, CTR, DPG, HBC, G36, VC7, NHA, HID** (loại các mã vật liệu xây
dựng thuần — xi măng/đá/nhựa như BMP, HT1, VCS, NNC, KSB, DHA, VGC — vì đó là câu chuyện khác, nhà
cung ứng chứ không phải EPC/chủ đầu tư dự án công). Lưu ý: **PC1 nằm trong nhóm ICB 2357 nhưng
KHÔNG đưa vào cohort test này** vì đã BANNED vĩnh viễn (CLAUDE.md) — loại để tránh trộn 1 case đã
có lý do loại trừ riêng vào phép đo cơ chế thị trường.

| Episode | Cửa sổ | N mã cohort có mặt | Median cohort | Median toàn universe | VNINDEX |
|---|---|---|---|---|---|
| 2018-04-09 | 12mo | 6 | +27,57% | +24,67% | +65,01% |
| 2018-04-09 | 133d | 7 | -0,96% | +3,15% | +28,31% |
| 2020-01-22 | 12mo | 7 | -2,38% | +2,35% | +9,37% |
| 2020-01-22 | 133d | 9 | -9,76% | -2,03% | +2,29% |
| **2022-01-06** | **133d** | 13 | **+130,10%** | +28,15% | +17,48% |
| **2026-05-18** | 12mo | 13 | **+5,26%** | +10,05% | +48,73% |
| **2026-05-18** | **133d** | 14 | **-6,20%** | -3,12% | +7,80% |

**Kết quả rõ ràng, không mơ hồ**: ở đúng episode 07/2026 mà user nghi ngờ có cơ chế "nhóm hạ tầng
kéo chỉ số" — cohort này **KÉM HƠN** trung vị toàn thị trường ở CẢ HAI cửa sổ (12mo: +5,26% <
+10,05%; 133d: -6,20% < -3,12%), và kém RẤT XA so với VNINDEX (+48,73%/+7,80%). Chi tiết từng mã
133d-2026: DPG +11%, G36 +6%, CTR +5%, CTD +3%, VC7 -2%, VCG -4%, HHV -4%, LCG -8%, FCN -9%,
CII -10%, HBC -17%, C4G -18%, HID -18%, NHA -20% — phân bố ÂM chiếm đa số (9/14 mã âm), không hề
là nhóm "được chọn lọc kéo lên". **Đợt cohort này THỰC SỰ dẫn dắt là 2022** (median +130,1% trong
133 ngày trước đỉnh 06/01/2022, gấp 4,6 lần trung vị thị trường +28,15%) — khớp đúng lịch sử "chủ đề
đầu tư công 2021-2022" đã biết, không phải chu kỳ 2026.

**Vậy cái gì thực sự kéo VNINDEX lên trong 133 ngày trước đỉnh 07/2026?** Top-20 mã tăng mạnh nhất
(133d, `ticker_prune`): BSR +105,9%, TCO +74,5%, ~~VVS~~ +62,9% (VVS nằm trong BANNED list, loại
khỏi mọi diễn giải cơ chế), GVR +52,6%, OIL +51,8%, BFC +47,7%, PVC +44,8%, PVP +43,4%, HCM +38,4%,
PET +36,8%, LPB +36,7%, DCM +34,9%, PVT +34,6%, GMD +31,5%, VIC +30,0%. Đây là **nhóm dầu khí họ
PVN (BSR/OIL/PVC/PVP/PVT/DCM), phân bón (BFC/DCM), + mega-cap VIC + GVR (cao su/KCN nhà nước)** —
KHÁC hẳn nhóm EPC hạ tầng công user đề xuất. Đây là quan sát PHỤ (không phải câu hỏi chính của job),
chưa kiểm định thống kê, chỉ ghi lại để tránh để trống câu hỏi "vậy là gì".

## Bước 4 — So sánh index-breadth gap 2026 vs 2018: có khác biệt định tính không?

**Có, nhưng KHÔNG theo hướng "chỉ số học được nhờ 1 nhóm hẹp trong khi 2018 broad-based"** như user
mô tả ban đầu — 2018 CŨNG là rally hẹp ở cửa sổ 12 tháng (gap +40,33pp, gần bằng 2026's +38,68pp).
Khác biệt THẬT nằm ở góc nhìn khác: **tốc độ suy yếu breadth trong CHẶNG CUỐI trước đỉnh** — 2026 có
57,1% mã âm trong 133 ngày cuối (đa số thị trường đã rút lui), 2018 chỉ có 45,4% mã âm (đa số vẫn
dương, dù tăng chậm hơn chỉ số). Và cơ chế "nhóm nào kéo chỉ số" ở 2026 KHÔNG PHẢI nhóm hạ tầng đầu
tư công như user đoán — mà nghiêng về dầu khí/PVN + mega-cap, một giả thuyết cơ chế KHÁC cần dữ liệu
riêng để kiểm định (ngoài phạm vi job này).

## Bước 5 — Tổng hợp, kỷ luật N nhỏ, đề xuất

**Tautology-trap check**: "%mã âm trong 133 ngày trước đỉnh" và "gap 12 tháng" là 2 con số ĐO
BREADTH TRỰC TIẾP TỪ CHÍNH GIAI ĐOẠN ĐANG XÉT (không phải suy luận vòng từ outcome ngược lại input)
— khác với bẫy đã cảnh báo ở job trước (dùng return sau đỉnh để giải thích return trước đỉnh). Đây
là phép đo hợp lệ về mặt phương pháp.

**N cảnh báo**: chỉ N=6 episode, và bản thân "% mã âm 133 ngày" cũng chỉ có nghĩa thống kê yếu ở
N=6 — kết luận "57,1% > 45,4%" là 1 quan sát mô tả (2 con số cụ thể của 2 case cụ thể), KHÔNG phải
ngưỡng đã kiểm định qua nhiều case độc lập. Không dựng ngưỡng % cứng (vd ">50% mã âm = cảnh báo")
từ N=1 cặp so sánh.

**Kết luận 2 tầng, không gộp làm một**:
1. **Phần "breadth thị trường xấu hơn 2018 ở chặng cuối"**: có bằng chứng thật (57,1% vs 45,4% mã
   âm, đo trực tiếp, không tautology) — đáng ghi nhận như một quan sát mô tả, KHÔNG đủ N để thành
   ngưỡng production.
2. **Phần cơ chế "nhóm hạ tầng đầu tư công nhà nước chỉ định kéo chỉ số"**: **BÁC BỎ RÕ RÀNG** bằng
   dữ liệu ICB thật — nhóm này underperform thị trường chung ở cả 2 cửa sổ dẫn tới đỉnh 2026. Nếu
   có cơ chế "nhóm hẹp kéo chỉ số" ở 2026, nó không phải nhóm mà user chỉ định; dữ liệu gợi ý nhóm
   dầu khí PVN + mega-cap nhưng đây là quan sát phụ chưa kiểm định.

**Không đề xuất chỉ báo mới đưa vào production** từ job này — cả 2 lý do: (a) N=6 quá mỏng, (b) cơ
chế cụ thể user đề xuất để giải thích SỰ KHÁC BIỆT (nhóm hạ tầng) đã bị bác bỏ bằng chính dữ liệu,
nên không có "công thức cụ thể" nào để wire — quay lại kết luận job trước: 3-archetype framework
(external_flag + điều gì xảy ra SAU cluster) vẫn là công cụ chính; breadth 133-ngày có thể dùng làm
**quan sát bổ trợ mô tả**, không phải ngưỡng cứng.

## Giới hạn phải mang theo

1. N=6 episode, N còn nhỏ hơn nữa cho cohort hạ tầng (chỉ 6-14 mã tuỳ episode do nhiều mã chưa niêm
   yết ở các đỉnh cũ — 2007 cohort = 0 mã, loại khỏi bảng Bước 3).
2. Universe `ticker_prune` mỏng ở 2007 (N=9-16 mã cho episode đó) — số liệu 2007 chỉ mang tính tham
   khảo, không dùng để kết luận (đúng bẫy CLAUDE.md đã ghi).
3. Cohort hạ tầng được chọn thủ công dựa trên `ICB_Code=2357` giao `ticker_prune` + loại trừ vật
   liệu xây dựng thuần — đây là lựa chọn CHỦ QUAN có căn cứ (khớp tên quen thuộc với chủ đề đầu tư
   công VN), không phải danh sách chính thức từ nguồn dữ liệu (BQ không có cột "được nhà nước chỉ
   định dự án công" trực tiếp).
4. Quan sát "dầu khí + mega-cap kéo chỉ số 2026" (Bước 3, đoạn top-20 gainers) là MÔ TẢ, chưa kiểm
   định qua cross-section đầy đủ (chưa tính weighted contribution thực sự vào VNINDEX, chỉ liệt kê
   return đơn lẻ) — không trích dẫn như kết luận đã verify, chỉ nêu để không bỏ trống câu hỏi.
5. VVS xuất hiện trong top gainers 133d-2026 nhưng là mã BANNED (CLAUDE.md) — loại khỏi mọi diễn
   giải cơ chế, giữ trong bảng chỉ để minh bạch dữ liệu thô.
6. Recovery/outcome sau đỉnh 07/2026 vẫn right-censored (đã ghi ở job trước) — không ảnh hưởng job
   này (chỉ đo breadth TRƯỚC đỉnh, không đo outcome).

## Artifact

- `breadth_12mo_raw.csv`, `breadth_133d_raw.csv`, `breadth_ytd2026_raw.csv` — dữ liệu thô từ BQ
  `tav2_bq.ticker_prune` (Close tại đỉnh + tại mốc lùi, per ticker per episode).
- `compute_breadth.py` — script tính % dương/âm, median, gap từ CSV thô (chạy `python3`, không cần
  scipy/pandas).
- Queries chạy trực tiếp qua `bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9`
  (xem lệnh đầy đủ trong lịch sử job, không lưu file `.sql` riêng do job ngắn).
