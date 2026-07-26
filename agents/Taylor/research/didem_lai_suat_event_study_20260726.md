# "Đi đêm lãi suất huy động" — nghiên cứu sự kiện lịch sử (KHÔNG phải IC backtest)

**Job**: Taylor_20260726_135326 · **Ngày**: 2026-07-26 · **Loại**: event/historical study, n RẤT NHỎ
**Đề xuất bởi**: user (hướng #6, KHÁC 5 tín hiệu định lượng NO-GO cùng ngày)
**Không chạm production/DT5G.** Đây là QUAN SÁT LỊCH SỬ CÓ CHỦ ĐÍCH, không phải tín hiệu đã kiểm chứng thống kê.

---

## 0. Phân biệt bản chất với 5 test hôm nay (bắt buộc nêu rõ)
5 test sáng nay (adaptive-persistence, M1 divergence, breadth static+momentum, rate-signal, foreign-flow)
đều có **hàng nghìn quan sát ngày** → dùng IC / walk-forward / DSR. Test này KHÁC HẲN: hiện tượng "đi đêm
vượt trần lãi suất" chỉ xảy ra **1–2 lần trong toàn lịch sử ngành NH VN** → **n≤2**, KHÔNG thể chạy thống kê.
Kết quả dưới đây chỉ để **tham khảo bối cảnh**, KHÔNG để wire vào bất kỳ gate tự động nào.

---

## 1. Các đợt "đi đêm / vượt trần lãi suất" lịch sử tìm được

### Đợt A — 2011–2012 (CANONICAL, đúng nghĩa "đi đêm vượt trần")
- **Cơ chế**: SBV áp **trần huy động 14%/năm** (Thông tư 02/2011/TT-NHNN, hiệu lực ~03/03/2011, gồm cả
  khuyến mãi dưới mọi hình thức). Ngân hàng thiếu thanh khoản **lách trần**: cộng lãi ngoài, thưởng, quà →
  thực nhận 17–19%/năm (200tr → 18%, >1 tỷ → >19%). Cuối 06/2011 lãi suất BQ thực tế **15,6%** > trần 14%.
- **Kết thúc/xử lý**: Chỉ thị 02/CT-NHNN **07/09/2011** siết mạnh → 08–09/09/2011 các NH đồng loạt kéo về 14%.
  (Lách trần vẫn âm ỉ sang 2012 nhưng đỉnh điểm là H1–Q3/2011.)
- **Đây là đợt "đi đêm" NỔI TIẾNG NHẤT** — gần như là nguyên mẫu duy nhất khớp CHÍNH XÁC mô tả của user
  (niêm yết một đằng, thực nhận một nẻo, lách trần chính thức).

### Đợt B — 2008 (đua lãi suất, nhưng KHÁC CƠ CHẾ — không hẳn "đi đêm")
- **Cơ chế khác**: 2008 KHÔNG có trần tuyệt đối bị lách lén; SBV quản qua **lãi suất cơ bản** (trần = 150%
  LSCB). Khi LSCB nâng lên 14% (06/2008), trần cho vay = 21%, các NH đua lãi suất huy động **CÔNG KHAI** tới
  đỉnh **19,2%/năm** (SeABank kỳ 13 tháng). Đây là **cuộc đua công khai**, không phải "đi đêm lén lút".
- Xếp là đợt tham chiếu thứ 2 nhưng **có dấu sao**: bản chất pháp lý khác. Nếu chỉ tính đúng nghĩa "vượt
  trần lén" thì **n=1** (chỉ 2011–2012).

> **Kết luận mục 1: n=1 chặt (2011–12) hoặc n=2 nới (thêm 2008). Với n như vậy KHÔNG THỂ coi là quy luật.**

---

## 2. Bảng đối chiếu từng đợt (kiểm chứng trực tiếp giả thuyết lạm phát của user)

| | **Đợt A: 2011–12** | **Đợt B: 2008** | **HIỆN TẠI 2025–26** |
|---|---|---|---|
| Trần bị lách | 14% (TT02/2011) | LSCB→14% (đua công khai) | *Không có trần* — chênh niêm yết/thực nhận do cạnh tranh |
| Lãi thực nhận đỉnh | 17–19% | 19,2% | 8,5–9,05% (ACB, HDBank…) vs niêm yết 7,6% |
| **CPI cả năm** | **18,13% (2011)**, 11,75% (2010) | **19,89% (2008)** | **3,31% (2025)**, dự báo ~3,5–4,5% (2026) |
| CPI đỉnh YoY | ~23% (T8/2011) | ~28% (T8/2008) | ~3–4% |
| Chính sách SBV đồng thời | **THẮT CHẶT MẠNH** (nâng lãi suất, siết tín dụng chống lạm phát) | **THẮT CHẶT MẠNH** (LSCB 14%) | **Ổn định/nới** — refi 4,5% đứng yên, đẩy tăng trưởng |
| Nguyên nhân "đi đêm" | Thanh khoản kẹt do thắt chặt + lạm phát | Thanh khoản kẹt do thắt chặt + lạm phát | **Cấu trúc**: gap tín dụng-huy động + lệch kỳ hạn (80% vốn <6th) |

### Phản ứng VNINDEX SAU khi đợt "đi đêm" BẮT ĐẦU (không phải sau khi kết thúc)
Nguồn: BQ `tav2_bq.ticker` ticker='VNINDEX', close cuối tháng (đã verify).

**Đợt A 2011–12** (mốc = 03/2011 khi trần áp & bị lách ngay):
- +3th (T6/2011): **−6,2%** · +6th (T9): **−7,3%** · +12th (T3/2012): **−4,4%** · đáy giữa kỳ T12/2011: **−23,8%**
- (mốc siết 09/2011: +3th T12 **−17,8%**, +6th **+3,1%**, +12th **−8,2%** → sụt mạnh tới đáy T12/2011 rồi hồi)

**Đợt B 2008** (mốc T2/2008): +3th **−37,6%** · +6th **−17,4%** · +12th **−63,0%**.
⚠️ Nhưng VNI đã **đổ từ đỉnh bong bóng T10/2007 (1065)** TRƯỚC khi đua lãi suất — sụt giảm bao trùm cả
đợt, không tách được "đua lãi suất gây sụt" khỏi "vỡ bong bóng + khủng hoảng toàn cầu + thắt chặt".

> **Quan sát then chốt**: cả 2 đợt VNI đều **giảm** trong 3–12 tháng sau. NHƯNG ở CẢ HAI, "đi đêm" đi kèm
> **lạm phát 18–28% + SBV thắt chặt quyết liệt**. Đó mới là biến số vĩ mô lớn drive thị trường. "Đi đêm"
> chỉ là **TRIỆU CHỨNG của thanh khoản kẹt do thắt chặt**, không phải nguyên nhân độc lập.

---

## 3. Đối chiếu 2 con số chênh lệch tín dụng–huy động (làm rõ định nghĩa trước khi so)

- **Tiền Phong "17,8% vs 14% = 3,8pp"** = **tăng trưởng CẢ NĂM 2025**: tín dụng +17,87%, huy động +14,11%
  (số liệu chính thức, đã khớp qua search) → gap **3,76pp ≈ 3,8pp**. ✅ Con số này ĐÚNG, là gap tăng trưởng
  luỹ kế cả năm 2025.
- **VNBusiness "~2pp"** — KHÔNG có nguyên văn bài để chốt chắc, NHƯNG khả năng cao là **cửa sổ đo khác**:
  gap YTD/điểm-thời-điểm chứ không phải cả năm. VD số tôi tra được: tới **24/3/2026** tín dụng +2,15% vs
  huy động +0,44% = **1,71pp YTD-Q1/2026** (cửa sổ tích luỹ ngắn hơn nhiều). 
- **Kết luận: 2 con số KHÔNG mâu thuẫn** — nhiều khả năng chỉ khác cửa sổ đo (cả-năm-2025 vs YTD/quý).
  KHÔNG tự chọn 1 bỏ 1. Con số **3,8pp cả năm 2025 là số độc lập xác minh được**; "~2pp" cần bài gốc
  VNBusiness mới chốt được chính xác nó đo gì (chưa có → nêu là chưa xác định thay vì đoán).

---

## 4. Kỷ luật trung thực — cái này CHỨNG MINH ĐƯỢC gì và KHÔNG chứng minh được gì

**KHÔNG chứng minh được** (trả lời thẳng câu hỏi user):
- Với **n=1** (2011–12; 2008 khác cơ chế), **KHÔNG THỂ PHÂN BIỆT** giữa:
  - (H1) "đi đêm" tự nó báo trước/gây suy giảm thị trường, vs
  - (H2) "đi đêm" chỉ là **triệu chứng** của lạm phát cao + thắt chặt, và chính lạm phát/thắt chặt gây suy giảm.
- Dữ liệu ủng hộ **H2 mạnh hơn** về mặt logic (cả 2 đợt đều nằm trong regime lạm phát 18–28% + thắt chặt),
  nhưng với n nhỏ như vậy đây là **suy luận định tính**, KHÔNG phải kiểm định.

**Điểm mấu chốt cho HIỆN TẠI** (đúng trực giác user): biến số ẩn mà user nghi ngờ — **lạm phát** — lần này
**VẮNG MẶT**. CPI 2025 = 3,31%, dự báo 2026 ~3,5–4,5%, thấp hơn 2008/2011 một bậc độ lớn (18–28%). SBV
KHÔNG trong chu kỳ thắt chặt (refi 4,5% đứng yên, đang đẩy tăng trưởng). "Đi đêm" lần này do **cấu trúc**
(gap tín dụng-huy động 3,8pp + lệch kỳ hạn 80% vốn <6 tháng), KHÔNG do lạm phát ép chính sách thắt chặt.
→ **Tiền lệ 2011-style KHÔNG có cơ sở để kỳ vọng lặp lại**, vì tiền đề định nghĩa (lạm phát cao→thắt chặt)
không hiện diện. Nhưng đây cũng là n=1 → **không thể loại trừ** rủi ro, chỉ nói được "kịch bản cũ ít khớp".

---

## 5. Tổng hợp CẢ NGÀY — có tồn tại tổ hợp tín hiệu vĩ mô "vững chắc" để cải thiện DT5G không?

Sau **5 test định lượng NO-GO** (adaptive-persistence, M1 divergence, breadth static+momentum, rate-signal,
foreign-flow — đều có n lớn, đều rớt IC/OOS/DSR) **+ nghiên cứu sự kiện "đi đêm" này** (n≤2, confounded,
tiền đề vắng mặt):

**Đánh giá thẳng thắn: KHÔNG.** Chưa có tổ hợp tín hiệu vĩ mô nào đạt mức "vững chắc" để thay/bổ sung DT5G
trong việc dự báo thị trường. Lý do hội tụ qua cả ngày:
1. **DT5G đơn giản nhưng đã calibrate kỹ** (price-based, 49 transitions, fail-safe gate). Các ứng viên vĩ mô
   thay thế đều **hoặc quá ít mẫu** (đi đêm n≤2), **hoặc trễ** (breadth/flow lag giá), **hoặc không độc lập
   với giá/không qua OOS** (5 test sáng).
2. Tín hiệu vĩ mô "hấp dẫn kể chuyện" nhất (đi đêm lãi suất) khi mổ xẻ lịch sử lại **confounded với lạm phát+
   thắt chặt** và tiền đề đó **không hiện diện lần này** → không phải cảnh báo dùng được, chỉ là bối cảnh.

**Hướng CÒN MỞ (là HƯỚNG, KHÔNG phải kết quả):**
- (a) **Dữ liệu lending-rate/deposit-rate LIVE thật** (không phải fetch bài báo lẻ) — nếu có chuỗi thời gian
  lãi suất thực nhận vs niêm yết theo tuần, mới đủ để xét như 1 biến định lượng. Hiện KHÔNG có nguồn sạch.
- (b) **Theo dõi TIẾP đúng đợt "đi đêm" hiện tại** như 1 quan sát out-of-sample tự nhiên trong vài tháng tới:
  xem VNI + thanh khoản có diễn biến kiểu 2011 không, TRONG bối cảnh lạm phát thấp. Đây là cách **tăng n một
  cách trung thực** (chờ dữ liệu mới), KHÔNG phải ép kết luận từ n=1 hôm nay.

**Không wire gì. Không chạm DT5G. Giữ DT5G làm nguồn regime chính thức.**

---
### Nguồn
- [Chuyện vượt trần 2011-2012 (laisuat.vn)](https://www.laisuat.vn/tin-tuc/chuyen-vuot-tran-lai-suat-2011-2012-lai-gay-chu-y) · [Chính thức xử lý NH vượt trần (VnEconomy)](https://vneconomy.vn/chinh-thuc-xu-ly-ngan-hang-vuot-tran-lai-suat.htm) · [TT02/2011/TT-NHNN](https://luatvietnam.vn/tai-chinh/thong-tu-02-2011-tt-nhnn-ngan-hang-nha-nuoc-viet-nam-59727-d1.html)
- [Đua lãi suất 2008 đỉnh 19,2% (Vietstock)](https://vietstock.vn/2010/12/bon-nguyen-nhan-khien-lai-suat-dat-dinh-757-175041.htm)
- [Lạm phát 2011 vượt 18% (VnExpress)](https://vnexpress.net/topic/lam-phat-2011-vuot-18-16259) · [CPI 2025 = 3,31%; mục tiêu 2026 4,5% (Nhân Dân)](https://nhandan.vn/giai-bai-toan-muc-tieu-kep-2026-tang-truong-cao-lam-phat-duoi-45-post936589.html)
- [Gap tín dụng-huy động 2025 (baodauthau)](https://baodauthau.vn/khoang-lech-lon-giua-huy-dong-von-va-tang-truong-tin-dung-post191801.html) · [TD 24/3/2026 +2,15% vs HĐ +0,44% (vietnambiz)](https://vietnambiz.vn/tinh-den-243-tang-truong-tin-dung-dat-215-trong-khi-huy-dong-von-chi-tang-044-2026449331850.htm)
- VNINDEX close: BQ `tav2_bq.ticker` (ticker='VNINDEX'), verified 2026-07-26.
