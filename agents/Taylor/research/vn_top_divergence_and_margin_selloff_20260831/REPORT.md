# Đỉnh thị trường: breadth-euphoria divergence + margin-forced-selloff vs fundamentals-selloff

> Job `Taylor_20260831_042737` · 2026-08-31 · RESEARCH-ONLY, không wire production, không đổi DT5G/CAPIT.
> Độc lập với hướng bottom-trigger đang chạy song song (2009/2020/2022 recovery trigger).

## Tóm tắt 1 dòng

Giả thuyết (a) breadth-mirror-tại-đỉnh: **chỉ 1/4 đỉnh lịch sử (2022-01) có divergence thật, 3/4
đỉnh (2007/2009-10/2018) breadth và giá đỉnh gần như cùng ngày** — không đủ N để coi là tín hiệu
sớm đáng tin. Giả thuyết (b)+(c) margin-forced-vs-fundamentals: case thật 07/2026 **khớp mạnh** với
margin-forced (nợ margin kỷ lục, không có cú sốc cơ bản/ngoại sinh đi kèm, hồi phục nhanh) — nhưng
đây là **N=1**, không phải kiểm định.

---

## PHẦN 1 — Breadth-euphoria mirror tại 4 đỉnh lịch sử

### Bước 1 — Ngày đỉnh giá thật (từ `data/VNINDEX.csv`, không giả định)

| Episode | Ngày đỉnh | Close |
|---|---|---|
| 2007 | **2007-03-12** | 1.170,67 |
| 2009-10 | **2009-10-22** | 624,10 |
| 2018 | **2018-04-09** | 1.204,33 |
| 2022-01 | **2022-01-06** | 1.528,57 |

### Bước 2 — Breadth overbought (`universe_pit` JOIN `ticker.D_RSI`), nhiều ngưỡng

Đã thử D_RSI>{0,60; 0,65; 0,70; 0,75; 0,80}. Đo trong cửa sổ **40 phiên trước mỗi đỉnh giá** (khớp
chỉ dẫn dispatch 20-40 phiên; cửa sổ RỘNG hơn — tới 6 tháng trước — cho kết quả SAI vì bắt trúng
đỉnh breadth của một đợt rally trước đó không liên quan, xem cảnh báo phương pháp cuối mục).

| Episode | N universe | breadth-peak-day (D_RSI>0,70) | Giá trị | Gap tới đỉnh giá (phiên) | Breadth decay (pp) từ breadth-peak → đỉnh giá | Giá đổi (%) cùng khoảng |
|---|---|---|---|---|---|---|
| 2007 | 130-132 | 2007-02-27 | 0,710 | **9** | -2,1pp | +0,28% |
| 2009-10 | 302-347 | 2009-10-21 | 0,485 | **1** | -3,0pp | +0,91% |
| 2018 | 996-1064 | 2018-04-05 | 0,139 | **2** | -0,9pp | +0,94% |
| **2022-01** | 1207-1237 | **2021-11-15** | 0,348 | **37** | **-23,6pp** | **+3,52%** |

**Kết luận Bước 2 — chỉ 1/4 case có divergence có ý nghĩa kinh tế.** 2007/2009-10/2018: breadth
đỉnh và giá đỉnh xảy ra **gần như cùng ngày** (gap 1-9 phiên, breadth chỉ suy giảm 1-3pp trước khi
giá đỉnh — nằm trong biên độ nhiễu ngày-qua-ngày, không phải một xu hướng suy yếu rõ ràng). **2022-01
là ngoại lệ rõ rệt**: breadth đạt đỉnh 15/11/2021 (0,348) rồi suy giảm liên tục **-23,6pp** trong khi
VNINDEX còn tăng thêm +3,5% trong 37 phiên (~7,5 tuần) tới đỉnh giá thật 06/01/2022. Đây khớp đúng
giai đoạn "penny-stock mania" H2/2021 đã biết trong lịch sử VN (dòng tiền đầu cơ cổ phiếu vốn hoá
nhỏ rút lui trước khi nhóm largecap/VN30 tạo đỉnh sau cùng) — có cơ chế kinh tế hợp lý, không phải
trùng hợp thống kê thuần túy, nhưng **N=1 case khớp** không đủ để tổng quát hoá.

### Bước 3 — Volume divergence

Kiểm tra ngày volume đột biến (>1,5× MA20) gần mỗi đỉnh, xem giá có "theo kịp" volume không:

| Episode | Ngày vol cao nhất trong 30 phiên trước đỉnh | vol_ratio | Return ngày đó | Diễn giải |
|---|---|---|---|---|
| 2007 | 2007-01-25 (ngoài 30 phiên gần đỉnh) | 1,52× | -2,71% | Xa đỉnh (46 phiên trước), không phải divergence-tại-đỉnh |
| 2009-10 | 2009-10-16, 2009-10-23 | 1,64×/1,69× | -1,28%/-1,43% | Xảy ra **TRÙNG/NGAY SAU** đỉnh giá (22/10), không phải cảnh báo TRƯỚC |
| 2018 | — | — | — | **KHÔNG có ngày nào** vol_ratio>1,5× trong 30 phiên trước đỉnh |
| 2022-01 | 2022-01-10 (SAU đỉnh) | 1,42× | -1,62% | Xảy ra SAU đỉnh giá, là XÁC NHẬN giảm chứ không phải divergence trước đỉnh |

**Kết luận Bước 3 — KHÔNG tìm thấy bằng chứng nhất quán cho "volume cao/giá không theo kịp trước
đỉnh" ở bất kỳ case nào trong 4 case.** 2018 hoàn toàn không có ngày volume bất thường; 2009 và 2022
có ngày volume cao nhưng đều xảy ra TẠI/SAU đỉnh giá thật (đóng vai trò xác nhận đảo chiều, giống
đúng vai trò "xác nhận không phải trigger" đã ghi nhận nhiều lần ở các job trước cho chính sách).
Giả thuyết dispatch về bearish-divergence-volume tại 2007/2009/2018/2022 **không được xác nhận** với
phương pháp đo này.

### Kết luận Phần 1

Trả lời câu hỏi cốt lõi: pattern "breadth đạt đỉnh và suy giảm trong khi giá còn leo" **CHỈ đúng
1/4 case (2022-01)** — không đủ (đúng kỷ luật N nhỏ, cần ≥3/4 hoặc cơ chế lặp lại rõ để coi là
robust). 2022-01 là ứng viên đáng chú ý RIÊNG (có cơ chế kinh tế hợp lý: xoay vòng vốn từ smallcap
đầu cơ sang bluechip trước khi cả hai cùng đảo chiều), không phải bằng chứng cho một quy luật chung.

**Cảnh báo phương pháp quan trọng** (phát hiện trong lúc chạy job): dùng cửa sổ RỘNG (6 tháng trước
đỉnh thay vì 40 phiên) làm sai lệch hoàn toàn kết quả — với 2009-10, breadth-đỉnh-toàn-cục nằm ở
2009-06-08 (giữa cơn sóng phục hồi mạnh nhất sau đáy 02/2009, momentum nóng nhất chưa phải lúc gần
đỉnh giá 10/2009), cho gap giả 97 phiên — SAI, không phải divergence thật mà là bắt nhầm cực trị
của một xu hướng khác. Bài học: khi đo "breadth peak trước đỉnh giá X phiên", PHẢI giới hạn cửa sổ
tìm kiếm hẹp quanh chính X, không tìm global max trên toàn bộ lịch sử gần đó.

---

## PHẦN 2 — Margin-forced-selloff vs fundamentals-selloff: case thật 07/2026

### Bước 1 — Chuyện gì đã xảy ra (dữ liệu + WebSearch xác nhận tin tức)

| Mốc | Ngày | Close | Ghi chú |
|---|---|---|---|
| Đỉnh 52 tuần thật | **2026-05-18** | 1.927,94 | Xác nhận qua BQ (khớp báo chí "~1.936 điểm giữa tháng 5") |
| Đáy | **2026-07-22** | 1.668,53 | dd52w = **-13,46%** (45 phiên từ đỉnh) |
| Trạng thái hồi phục (dữ liệu mới nhất) | 2026-08-28 | 1.832,12 | Hồi **63,1%** khoảng cách giảm, trong 27 phiên (~5,5 tuần) từ đáy |

`dd52w` đáy chỉ **-13,46%** — **CHƯA chạm ngưỡng -20%** dùng cho trigger `capit_margin_lever` (nằm
ngoài tập 5-episode đã audit trong `crisis-episode-clustering-reanalysis-20260830` và
`crisis_margin_framework_adaptive_20260825.md`). Đây là một đợt "wash-out" vừa phải, không phải
crisis-level theo chuẩn engine hiện tại — nhưng đủ mạnh để đáng phân tích cơ chế.

### Bước 2 — Kiểm tra "có phải fundamentals xấu đi không" — KHÔNG

| Kênh kiểm tra | Kết quả | Đọc |
|---|---|---|
| **US pillar (VIX/SPX)** | VIX 15,03-20,66 suốt 06→08/2026 (dưới ngưỡng crisis ~30); SPX drawdown từ đỉnh 1 năm tối đa chỉ **-3,86%** (29/07) | **Hoàn toàn bình thường** — không có global risk-off đồng bộ, loại trừ kênh lây lan từ Mỹ |
| **Deposit rate VN (PIT)** | Ổn định **6,80%** xuyên suốt 06→08/2026 (`data/deposit_rate_vn_events.csv`, xác nhận WebSearch 16/07 qua Winston) | Không có động thái SBV thắt chặt/nới lỏng nào — macro nền không đổi |
| **BCTC Q2/2026 (BQ `ticker_financial`)** | Đợt công bố rơi ĐÚNG lúc giá sập mạnh nhất (20/07: 122 release, 21/07: 96, 22/07: 72) — **TRÙNG THỜI ĐIỂM** nhưng median NP_R (YoY) = **+6,44%**, CAO NHẤT trong 5 quý gần đây (25Q2 +0,19% / 25Q3 +6,19% / 25Q4 -5,57% / 26Q1 +5,42%); tỷ lệ mã lợi nhuận âm 40,7% — xấp xỉ trung bình lịch sử (38,8-46,0%), không tệ hơn | **KHÔNG có bằng chứng suy giảm cơ bản đồng loạt** — mùa BCTC trùng thời điểm về mặt lịch, không phải nguyên nhân |
| **DT5G state** | Giữ nguyên **NEUTRAL (state=3)** xuyên suốt toàn bộ 06→08/2026, kể cả lúc dd52w chạm đáy | Quy mô đợt giảm nằm dưới ngưỡng mà bộ lọc DT-gate smoothed coi là stress thật sự |

### Bước 3 — Kiểm tra "có phải margin-forced không" — CÓ, xác nhận qua WebSearch tin tức thật

- **Dư nợ margin toàn thị trường cuối Q2/2026 đạt mức kỷ lục ~440.000 tỷ VND** (+35.000 tỷ vs Q1),
  tổng dư nợ cho vay margin+ứng trước ~445.000 tỷ VND (nguồn: Tuổi Trẻ "Những núi margin trên thị
  trường chứng khoán tiếp tục phình to", 17/07/2026).
- Tin tức đồng loạt mô tả **"vòng xoáy bán giải chấp", "call margin hàng loạt"** đúng giai đoạn
  20-22/07/2026 (Vietstock, BBW, YouTube chuyên đề chứng khoán 20/07/2026).
- Áp lực bán **tập trung nhóm bất động sản/thép, dẫn đầu bởi VIC/VHM** (Fili/Vietstock 16/07,
  20/07/2026) — **phân hoá ngành**, không phải bán tháo đồng loạt toàn thị trường vì lý do vĩ mô.
- Chuyên gia An Bình Securities (Nguyễn Thế Minh) nhận định call-margin "xảy ra cục bộ, chưa có dấu
  hiệu lan rộng" — khớp với việc DT5G KHÔNG kích hoạt cảnh báo state.

### Bước 4 — Chữ ký breadth/volume của một đợt margin-cascade

| Chỉ báo | Diễn biến | Đọc |
|---|---|---|
| Breadth oversold (%mã `universe_pit` D_RSI<0,30) | Từ ~16% (17/07) → đỉnh **30,3%** (22/07, TRÙNG NGÀY đáy giá) → 30,3% lại (27/07) → **10,97%** chỉ 2 phiên sau (30/07) → dưới 5% trong ~4 tuần (24/08) | **Lành RẤT NHANH** — đặc trưng của một cú sập kỹ thuật một-lần, không phải suy thoái đa-đợt (so với 2022's 47 phiên trong khung tương tự) |
| Return 2 phiên giảm mạnh liên tiếp trong 4 phiên | 20/07 **-2,46%**, 22/07 **-3,58%** (21/07 -0,74% giữa 2 phiên) | Tốc độ giảm bất thường trong khung ngắn — dấu hiệu cổ điển của chuỗi giải chấp dây chuyền |
| Volume | 20/07: 862tr, 21/07: 789tr, 22/07: 915tr — đều cao hơn hẳn TB 20 phiên trước (~650-700tr) | Volume đột biến ĐÚNG lúc giá sập nhanh nhất — khớp mô tả "giải chấp hàng loạt" |

### Kết luận Phần 2

Case 07/2026 khớp mạnh với giả thuyết **margin-forced, không phải fundamentals-driven**: không có
cú sốc ngoại sinh (Mỹ sạch), không có thắt chặt tiền tệ nội địa, kết quả kinh doanh Q2 THẬT SỰ tốt
hơn trung bình gần đây (loại trừ luôn khả năng "bán vì lo ngại KQKD"), trong khi bằng chứng độc lập
từ báo chí xác nhận trực tiếp cơ chế margin-call dây chuyền với quy mô dư nợ kỷ lục. Hình dạng hồi
phục V-shape (63% khoảng cách giảm được lấy lại trong 5,5 tuần, breadth lành trong ~1 tuần) khớp với
những case margin/liquidity-driven containable trong lịch sử (2009: 10 phiên lành, 2020: 12 phiên) —
khác hẳn case fundamentals/multi-branch kéo dài (2022: 47 phiên lành, 2018: gần như đi ngang nhiều
năm).

**Đây là N=1** — một case thật, không phải kiểm định thống kê. Case này cũng CHƯA chạm ngưỡng dd52
-20% nên nằm NGOÀI tập 5-episode đã audit trước đó trong `crisis_margin_framework_adaptive_20260825.md`
— là một data-point MỚI, ở quy mô nhỏ hơn các case crisis-level đã biết.

---

## PHẦN 3 — Tổng hợp framework

### 3 chỉ báo đề xuất (đo được, có công thức, KHÔNG wire production)

**(A) Cảnh báo sớm gần đỉnh — breadth-euphoria divergence (từ Phần 1, THẬN TRỌNG vì N=1/4):**
```
breadth_ob(t) = %mã universe_pit có D_RSI(t) > 0,70
divergence_flag = TRUE nếu: breadth_ob đạt local-max trong cửa sổ 40 phiên, RỒI suy giảm ≥15pp,
                  TRONG KHI giá VNINDEX vẫn đi ngang/tăng thêm ≥2% trong cùng khoảng
```
Ngưỡng 15pp/2% chọn dựa trên case 2022-01 (-23,6pp/+3,5%) làm mốc duy nhất đã quan sát được — **CHƯA
hiệu chỉnh (calibrate) được với N=1**, chỉ nên dùng làm CẢNH BÁO ĐỊNH TÍNH ("đáng chú ý hơn") chứ
không phải ngưỡng cứng. 3/4 case lịch sử không kích hoạt được flag này ở mức có ý nghĩa — công cụ
này có tỷ lệ bỏ sót (miss rate) cao, không nên dùng làm gate độc lập.

**(B) Phân biệt margin-forced vs fundamentals khi đang giảm mạnh (từ Phần 2):**
```
speed_flag = TRUE nếu: ≥2 phiên giảm ≥2%/phiên trong cửa sổ 5 phiên liên tiếp
             VÀ breadth_oversold(D_RSI<0,30) tăng >10pp trong CÙNG cửa sổ 5 phiên
earnings_flag = TRUE nếu: đợt công bố BCTC (nếu trùng thời điểm) có median NP_R KHÔNG xấu hơn
                trung bình 3-4 quý gần nhất — loại trừ giả thuyết "bán vì KQKD xấu"
external_flag = TRUE nếu: VIX < 25-30 VÀ SPX dd_1y > -10% đến -15% (US pillar sạch, đã có sẵn
                trong macro gate hiện tại) trong khi VN tự giảm mạnh — xác nhận cú sốc NỘI ĐỊA
```
Khi CẢ 3 flag đều TRUE → ứng viên margin-forced/technical, đặc trưng hồi phục kỳ vọng nhanh (V-shape,
breadth lành trong ~1-2 tuần). Khi speed_flag TRUE nhưng earnings_flag hoặc external_flag FALSE →
cẩn trọng hơn, có thể là suy giảm cơ bản/lây lan ngoại sinh thật, hồi phục có thể chậm hơn nhiều
(kiểu 2018/2022).

**(C) Follow-through healing-speed (đã có từ job 2009/2020/2022, tái dùng):** theo dõi số phiên để
breadth oversold quay lại ngưỡng baseline-calm riêng của giai đoạn đó (không dùng ngưỡng tuyệt đối
cố định — bài học từ Phát hiện #A của job 2020/2022) — 07/2026 lành trong ~1 tuần, XÁC NHẬN đúng
hướng dự đoán margin-forced trước khi biết trước kết quả.

### Đối chiếu với LEAD-1..4 đã có (2009/2020/2022 bottom trigger)

- **LEAD-1 (healing speed tương đối)**: 07/2026 CỦNG CỐ thêm bằng chứng — case margin/liquidity-clean
  lành NHANH (07/2026 ~1 tuần, 2009 10 phiên, 2020 12 phiên) trong khi case đa-đợt/kéo dài (2022) lành
  chậm (47 phiên). Không mâu thuẫn LEAD-1 đã sửa ở job 2020/2022.
- **LEAD-2 (volume regime-break)**: 07/2026 khớp mẫu 2022 hơn — volume break xảy ra GẦN NHƯ ĐỒNG THỜI
  với đáy/breadth panic (không lag như 2009), tiếp tục xác nhận thứ tự breadth→volume KHÔNG cố định.
- **LEAD-3 (targeted policy action lag)**: 07/2026 là case ĐẦU TIÊN trong nhóm nghiên cứu **KHÔNG có
  hành động chính sách nào cả** (SBV không cắt/tăng lãi suất, không có gói cứu trợ) — thị trường tự
  hồi phục thuần túy nhờ hết áp lực bán kỹ thuật, không chờ policy. Đây là case thứ 2 (sau 2020) cho
  thấy LEAD-3 "targeted action" không phải điều kiện CẦN cho mọi case, thêm bằng chứng nó chỉ áp dụng
  khi khủng hoảng có domestic-fundamentals origin thật.
- **LEAD-4 (tripwire tín dụng/thương mại/FX)**: KHÔNG áp dụng được — 07/2026 không phải cú sốc vĩ mô,
  mà là cú sốc CƠ CHẾ THỊ TRƯỜNG (đòn bẩy quá mức tự nó điều chỉnh) — cần một tripwire KHÁC hẳn (dư nợ
  margin/vốn hoá thị trường, đã đề xuất ở (B) trên) chứ không phải các biến vĩ mô cũ.

### Giới hạn phải mang theo

1. **Phần 1: N=4, chỉ 1/4 khớp giả thuyết** — không đủ để coi divergence-tại-đỉnh là tín hiệu đáng
   tin cậy độc lập. Volume-divergence-tại-đỉnh: 0/4 case có bằng chứng nhất quán, giả thuyết KHÔNG
   được xác nhận với phương pháp đo hiện tại.
2. **Phần 2: N=1 case thật, chưa chạm ngưỡng crisis-level (-20% dd52)** — cơ chế margin-forced được
   xác nhận qua WebSearch (bằng chứng bên ngoài độc lập, không chỉ suy luận từ giá), nhưng chỉ MỘT
   case không đủ để hiệu chỉnh ngưỡng số nào trong (B).
3. **Đây là RESEARCH-ONLY** — không đề xuất wire vào DT5G/CAPIT/production. Framework (B) có thể là
   input hữu ích cho `crisis_margin_framework_adaptive_20260825.md` (đã có sẵn cơ chế escalate
   người-quyết-định cho N nhỏ) nếu user muốn mở lại — không tự làm trong job này.
4. Chưa kiểm tra thêm case margin-forced lịch sử khác (vd có đợt call-margin cục bộ nào trước 07/2026
   không, để tăng N cho khung (B)) — nằm ngoài phạm vi 3 phần đã giao.

## Artifact

- `breadth_overbought_4peaks.csv` / `breadth_overbought_4peaks_wide.csv` — breadth overbought quanh
  4 đỉnh lịch sử.
- `vnindex_jul2026.csv`, `vnindex_dd52w_2026.csv`, `vnindex_may2026_peak.csv` — giá/volume/dd52w
  07/2026.
- `breadth_oversold_jul2026.csv` — breadth oversold 06-08/2026.
- Bus: `vn-top-breadth-divergence-4peaks-20260831`, `vn-jul2026-margin-forced-selloff-case-20260831`.
