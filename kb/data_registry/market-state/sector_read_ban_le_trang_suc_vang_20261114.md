---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-14. KHÔNG được biết mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về doanh nghiệp trang sức cụ thể. Có rò rỉ danh tính, ghi trung thực ở §0.
blind: YES
as_of: 2026-11-14
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành bán lẻ và sản xuất trang sức vàng bạc đá quý VN (chuỗi bán lẻ toàn quốc + bán buôn + kinh doanh vàng miếng/vàng nhẫn 24K, quy mô niêm yết trung bình-lớn). Gồm pipeline cầu, quản lý nhà nước về vàng (NĐ 24/2012 → NĐ 232/2025 → NĐ 390/2026), cấu trúc cạnh tranh, rủi ro nguồn cung đá quý/kim cương, phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED theo 2 tầm, FORECAST khoá trước có ngày chấm, checklist DD.
---

# SECTOR READ: Bán lẻ và sản xuất trang sức vàng bạc đá quý VN, as-of 14/11/2026 (Bobby, real-time BLIND)

Bản đọc này không phải episode VNINDEX và không vào N_effective. Nhãn trong file: **[DK]** là dữ kiện có nguồn + ngày.
**[UĐ]** là ước đoán hoặc suy luận của Bobby. **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này, phải KIỂM trước khi dùng làm số.
File chị em: `sector_read_ngan_hang_20261031.md` (chi phí vốn, tín dụng), `vn_macro_regime_history.md` regime read #3
(10/11/2026, nền STRUCTURAL_ACCUMULATION nhẹ, CPI tăng).

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Đã mở:** đúng 1 file snapshot caller chỉ định (`agents/Taylor/research/dd_PNJ_20261114/macro_snapshot_20261114_for_bobby.md`),
  file mẫu `sector_read_thuy_dien_20261112.md`, `index.md` và phần đầu/cuối `vn_macro_regime_history.md` trong registry này.
  Không mở file nào khác trong thư mục dispatch, không liệt kê thư mục đó.
- **Lãi suất PIT:** `deposit_rate_vn.effective_deposit_rate('2026-11-14')` trả Big-4 12M 6,8% (cập nhật 09/11), CCTG 12M 7,4% (02/11).
- **Rò rỉ không chủ ý (ghi trung thực):**
  1. **Đường dẫn snapshot caller đưa có chứa mã cổ phiếu.** Vì vậy danh tính doanh nghiệp DD là suy ra được. Tôi không tra giá,
     BCTC hay tin riêng của mã đó.
  2. Context fleet tự bơm vào phiên (current_ops) có nêu trạng thái loại/không loại của mã đó khỏi rổ và mốc xem lại. Đó là
     thông tin vận hành, không phải forward return. **Tôi không dùng** cho phân loại hay forecast.
  3. Tóm tắt kết quả tìm kiếm có (a) bảng giá vàng nhẫn có tên một chuỗi và (b) một vụ án buôn lậu kim cương năm 2026, trong đó
     giám đốc công ty giám định thuộc một chuỗi trang sức niêm yết bị khởi tố. Tôi chạy thêm **1 truy vấn** về vụ này để lấy ngày
     và quy mô, vì đây là sự kiện thực thi pháp luật lớn nhất năm 2026 về nguồn cung kim cương của **cả ngành**. Ở §3c tôi chỉ ghi
     ở mức ngành. Theo luật user ngày 27/09: vụ pháp lý chỉ là WARNING, không phải cổng chặn. **Không vụ việc nào ở đây làm đổi
     xác suất phân loại ngành.**
  - Không thấy số giá cổ phiếu, KQKD hay forward return nào trong các nguồn đã đọc.
- **Không có số lượt này (ghi "không có số", không suy):** số cặp kết hôn VN 2025-2026; thu nhập bình quân lao động Q3/2026 (NSO);
  WGC Vietnam bar & coin Q3/2026; giá vàng bình quân Q3/2026; thị phần chuỗi vs tiệm nhỏ; biên gộp ngành theo mảng; hạn mức nhập
  khẩu vàng nguyên liệu 2027; toàn văn NĐ 390/2026 (đọc qua báo).

## 1. Snapshot vĩ mô: chỉ báo hợp với ngành này
Bảng ánh xạ trong snapshot cho "Bán lẻ" 3 chỉ báo: retail, CPI, CPI lõi. Tôi thêm lương, tỷ giá, lãi suất Mỹ và DXY (kéo giá vàng
thế giới), cán cân thương mại và dự trữ (quyết định NHNN có dư địa cấp hạn mức nhập vàng hay không).

| Chỉ báo (snapshot, TE UNVERIFIED) | Giá trị | Δ3T / Δ12T | Đọc cho trang sức vàng |
|---|---|---|---|
| Bán lẻ YoY | 14,7% (T10) | +0,2 / +7,5pp | Danh nghĩa mạnh. NSO: bán lẻ hàng hoá 10T +12,9%, tổng mức giá so sánh T10 +7,7% [DK, NSO 11/2026] |
| CPI YoY | 5,09% (T10) | +0,64 / +1,84pp | Lạm phát đang lên. Lãi tiền gửi thực mỏng lại, hỗ trợ nhu cầu tích trữ vàng [UĐ] |
| CPI lõi YoY | 4,45% (T9) | −0,18 / +1,15pp | Lõi chững lại. Chưa phải lạm phát cầu kéo tự củng cố |
| Lương | 9,20 tr/tháng (T9) | +2,2% / +10,0% | Lương thực khoảng +5% YoY [UĐ: 10,0 − 5,1]. Sức mua tăng nhưng không bùng nổ |
| Ô tô bán | 22.806 (T10) | −9,7% / −28,4% | Hàng xa xỉ giá trị lớn đang yếu. Tín hiệu trái chiều với retail chung [UĐ] |
| Khách quốc tế | 1,85 tr (T10) | +11,3% / +7,0% | Hỗ trợ nhỏ cho kênh bán lẻ ở điểm du lịch |
| USD/VND | 25.725 | −1,6% / −2,4% | VND lên giá, làm giá vàng thế giới quy đổi ra VND thấp hơn |
| US 10Y / DXY | 5,18% / 103,2 | +0,48pp, +3,6% (3T) | Lợi suất thực Mỹ và USD tăng là lực cản giá vàng thế giới [UĐ] |
| Cán cân TM / Dự trữ NH | +7,31 tỷ USD (T10) / 82,7 tỷ USD (T8) | dự trữ −0,2% / +3,0% | Có dư địa ngoại tệ cho NHNN cấp hạn mức nhập vàng nếu muốn [UĐ]. Dự trữ là số T8, cũ 75 ngày |

### 1b. Chi phí vốn: bảng 5 tầng
Ngành này giữ tồn kho vàng và kim cương lớn, tài trợ phần lớn bằng vay ngắn hạn ngân hàng [NỀN]. Lãi tiền gửi đồng thời là
**tài sản cạnh tranh** với vàng trong túi tiết kiệm của hộ gia đình.

| Tầng | Proxy | Số | Ghi chú |
|---|---|---|---|
| A. Niêm yết hành chính | Big-4 12M (cao nhất online/quầy) | **6,8%** (09/11, đi ngang từ 03/10) | Tách online/quầy: không có số (series lưu MAX). Big-4 6M: không có số |
| B. Bán hành chính | CCTG 12M Big-4 (cao nhất) | **7,4%** (02/11) | Spread CCTG − tiết kiệm 12M = **+0,6pp**. Từng NH, sự kiện mở/rút kỳ hạn: không có số |
| C. Ngoài Big-4 | 12M NH tư nhân, lãi "ẩn", số NH ≥7% | không có số | |
| D. Thị trường | LNH 3M | **6,33%** (11/11; −0,62pp/3T, +0,14pp/12T) | OMO/tín phiếu, trúng thầu TPCP, USD tự do: không có số |
| D. | TPCP 10Y | 4,57 (chỉ tin Δ: +0,03 / +0,57pp) | |
| E. Lượng | Tín dụng vs huy động YTD, LDR | không có số | |

**Đồng thuận/phân kỳ [UĐ]:**
- HƯỚNG: A và B đi ngang, D giảm trong 3T. Không proxy nào báo chi phí vay ngắn hạn đang tăng.
- MỨC: chi phí biên (CCTG 7,4%) cao hơn số niêm yết khoảng 0,6pp.
- **Lãi thực:** tiết kiệm 12M − CPI = **+1,7pp**, CCTG − CPI = **+2,3pp**, đều mỏng dần khi CPI tăng (CPI tăng +1,84pp trong 12T).
  Lãi thực càng mỏng thì vàng càng hấp dẫn so với gửi tiết kiệm. Đây là lực kéo cầu **tích trữ**, không phải cầu trang sức.
- Kill-switch A (>7,5%) đang CLEAR. Độ tin cậy trung bình, vì thiếu tầng C và E.

## 2. Pipeline cầu
Cầu của ngành có 3 dòng với động lực khác nhau. Không gộp chúng làm một.

### 2a. Vàng tích trữ (vàng miếng + vàng nhẫn 24K): CYCLICAL theo giá vàng, ADMIN theo nguồn cung
- **Giá vàng thế giới:** đỉnh khoảng **5.589 USD/oz tháng 1/2026** (UOB qua báo, 09/2026, [DK cấp 2]). Đóng quý 3 ở **4.155,6 USD/oz**
  (COMEX 30/09; Topi 13/10/2026). Ngày 11/11 khoảng **4.030-4.053 USD/oz** [DK, bbw.vn 11/11/2026]. Như vậy giá đã **giảm khoảng 27%
  từ đỉnh** [UĐ, tự tính].
- **Trong nước:**
  - Ngày 12/01/2026: SJC bán khoảng 162-163 tr/lượng; vàng 9999 thương hiệu ngân hàng cùng vùng giá [DK, VnEconomy 13/01/2026].
  - Ngày 11/11/2026: SJC 136,5/139,5 tr (mua/bán, chênh 3 tr). Nhẫn 9999 các thương hiệu khoảng 134,7-135,3/138,9-139,3 tr (chênh
    4-4,2 tr). Giá thế giới quy đổi khoảng 126,5 tr, nên **premium vàng miếng khoảng 13 tr/lượng, khoảng +10%** [DK, bbw.vn 11/11/2026].
  - Đầu tháng 11, premium dao động **12-17 tr** [DK, bbw.vn 04/11 và 10/11/2026].
  - ⇒ Giá VND đã giảm khoảng 14% từ tháng 1, ít hơn mức giảm USD vì premium còn rộng và VND lên giá ngược chiều [UĐ].
- **Chênh mua-bán 3-4 tr/lượng (khoảng 2-3%)** là biên gộp của mảng vàng 24K. Mảng này biên mỏng nhưng quay vòng nhanh [UĐ + NỀN].
- **WGC:** Q1/2026 tổng cầu vàng VN khoảng 9 tấn (−24% YoY). Giá trị trang sức Q1 đạt kỷ lục 472 triệu USD, do người mua chuyển từ
  vàng miếng sang nhẫn vì nguồn cung vàng miếng hạn chế và premium rộng [DK, VietNamNet 07/05/2026].
  - Cách WGC xếp nhẫn trơn VN vào "trang sức" hay "bar & coin": [NỀN, PHẢI KIỂM]. Đây là điểm mấu chốt khi đọc số WGC cho VN.

### 2b. Trang sức (cưới hỏi, quà tặng, thời trang): CYCLICAL, đang ở pha yếu về khối lượng
- **WGC Q3/2026:** trang sức VN **1,4 tấn, −39% YoY, −24% QoQ**, yếu nhất trong các thị trường lớn của khu vực. ASEAN đều yếu
  (Indonesia −18%, Malaysia −21%, Thái −10%). Thế giới 312,9 tấn (−17%), quý 3 thấp nhất từ năm 2000, nhưng **giá trị +2%**
  (43 tỷ USD). Người tiêu dùng chuyển sang hàng nhẹ cân và hàm lượng thấp [DK, WGC Gold Demand Trends Q3 2026, 03/11/2026].
- ⇒ [UĐ] **Khối lượng giảm mạnh, giá trị gần đi ngang.** Đây là đặc trưng "giá cao kìm khối lượng". Chuỗi lớn bán theo giá trị và
  phí gia công, nên doanh thu trang sức có thể chịu được nếu dịch chuyển sang hàng 14-18K, bạc và thiết kế [UĐ]. Tiệm nhỏ bán theo
  trọng lượng 24K chịu nặng hơn.
- **Giá vàng hạ từ đỉnh** (−27% USD, −14% VND) là **thuận** cho khối lượng trang sức trong 2-4 quý tới, nếu giá ổn định. Lịch sử
  cho thấy cầu trang sức phản ứng với giá ổn định và giảm, không phản ứng với giá tăng dốc [NỀN].
- **Cưới hỏi:** số cặp kết hôn: không có số. TFR 1,91 (2024) và 1,93 (2025) [DK, Cục Thống kê qua VietnamPlus 2025-2026]. Tuổi kết
  hôn lần đầu tăng [DK, Bộ Y tế 21/12/2025]. ⇒ Cầu cưới hỏi là **gió ngược cấu trúc nhẹ**: lượng cưới đi ngang hoặc giảm chậm, tác
  động 1-2%/năm chứ không phải vài chục phần trăm [UĐ].
- **Mùa vụ [NỀN]:** Q4-Q1 là mùa cưới và Tết. Ngày Thần Tài (mùng 10 tháng Giêng) năm 2027 rơi khoảng giữa T2/2027. Q1 thường là
  quý cao nhất về vàng 24K.
- **Thu nhập:** lương +10% danh nghĩa, khoảng +5% thực. Bán lẻ thực khoảng +7-8%. Nhưng ô tô −28% YoY là cảnh báo hàng giá trị lớn
  đang yếu [UĐ]. Tôi đọc cầu trang sức nền là **trung tính, hơi yếu về khối lượng**.

### 2c. Bạc: CYCLICAL, dòng phụ đang nổi
Giá bạc thế giới khoảng 60-69,5 USD/oz trong T8/2026. Bạc thỏi trong nước khoảng 60-64 tr/kg (T8). Có cảnh xếp hàng mua bạc tích
trữ [DK, vnbusiness/các bản tin giá bạc T8/2026, cấp 2, số không nhất quán giữa các bài]. ⇒ Bạc là sản phẩm thay thế giá thấp
cho người mua bị giá vàng đẩy ra. Quy mô doanh thu nhỏ so với vàng [UĐ]. Giá bạc T9-T11: không có số.

## 3. Quản lý nhà nước và cấu trúc cạnh tranh
### 3a. Khung pháp lý vàng: đổi nhanh trong 13 tháng (ADMIN_GATED là trục chính)
| Văn bản | Ngày | Nội dung chính | Tác động ngành [UĐ] |
|---|---|---|---|
| **NĐ 232/2025** sửa NĐ 24/2012 | ký 26/08/2025, **hiệu lực 10/10/2025** | Bỏ độc quyền Nhà nước sản xuất vàng miếng. NHNN cấp phép sản xuất vàng miếng (vốn điều lệ ≥1.000 tỷ, có giấy phép mua bán vàng miếng, không bị phạt). Nhập khẩu vàng nguyên liệu theo **hạn mức năm + giấy phép từng lần**, hàm lượng ≥99,5%. Phải có giấy phép sản xuất vàng miếng **trước** khi xét nhập khẩu [DK, VnBusiness 29/12/2025, LSVN, VnEconomy] | Mở đường cho người chơi lớn có vốn. Chưa đổi cung thực tế |
| Tiến độ cấp phép | 29/12/2025: 9 hồ sơ. 14/04/2026: 11 hồ sơ. 26/07/2026: "thận trọng xem xét" | **Chưa thấy nguồn xác nhận giấy phép sản xuất vàng miếng hay hạn mức nhập nào đã cấp** tới as-of. Hạn nộp hồ sơ hạn mức năm sau: **15/11**. NHNN xét khoảng **15/12** [DK, VnBusiness, VNBA, LSVN] | Cung vàng miếng mới vẫn bị chặn. Premium khoảng 10% còn tồn tại |
| **Luật Thuế TNCN sửa đổi** (Luật 109/2025/QH15) | thông qua 10/12/2025, hiệu lực 01/07/2026 | Thuế **0,1% trên giá chuyển nhượng vàng miếng**, không áp cho vàng nguyên liệu và trang sức. Chính phủ quy định ngưỡng và **thời điểm bắt đầu thu**. Bộ Tài chính: **hiện CHƯA thu** (NĐ 253/2026, 30/06/2026) [DK, thuvienphapluat, Báo Pháp luật 07/2026] | Khi bắt đầu thu: chi phí giao dịch vàng miếng tăng nhẹ, có lợi tương đối cho nhẫn và trang sức [UĐ] |
| Bỏ thuế khoán hộ kinh doanh (NQ 198/2025/QH15) | **01/01/2026** | Hộ kinh doanh kê khai theo doanh thu thực, hoá đơn điện tử từ máy tính tiền kết nối cơ quan thuế [DK, nhiều nguồn hướng dẫn thuế 2026] | Đẩy tiệm vàng nhỏ vào minh bạch doanh thu. Chi phí tuân thủ tăng |
| **NĐ 390/2026** sửa NĐ 24 + NĐ 232 | ký và **hiệu lực 16/10/2026** | (1) **Bãi bỏ toàn bộ điều kiện sản xuất, gia công, mua bán vàng trang sức mỹ nghệ.** Bỏ Giấy chứng nhận đủ điều kiện của NHNN. (2) **Giao dịch vàng ≥5 triệu đồng/ngày phải thanh toán không dùng tiền mặt** (trước là ≥20 tr). (3) DN trang sức có hợp đồng gia công với nước ngoài được xét giấy phép nhập vàng nguyên liệu theo hợp đồng. Xét hằng năm theo năng lực và báo cáo xuất khẩu năm trước. Nhà nhập khẩu được **bán vàng nguyên liệu nhập khẩu cho DN sản xuất trang sức**. (4) Nghĩa vụ hệ thống thông tin, báo cáo NHNN về nhập-xuất-tồn vàng nguyên liệu. (5) Bộ KH&CN ban hành tiêu chuẩn quốc gia và kiểm định phương tiện đo [DK, LSVN 19-20/10/2026, VOV, Tạp chí Công Thương] | Xem 3b |
| Sàn giao dịch vàng | CĐ 12/CĐ-TTg 08/02/2026 yêu cầu hoàn thiện hồ sơ. 06/2026: phương án thí điểm 3 giai đoạn. 08/2026: "nghiên cứu lộ trình" | Giai đoạn 1 là vàng vật chất, làm kênh phân phối vàng nguyên liệu nhập khẩu hợp lệ [DK, Saigon Times 25/06/2026, VCCI, doanhnghiephoinhap 03/08/2026] | Chưa vận hành. Nếu có sẽ nén premium và nén biên mua-bán vàng 24K |

**Đọc NĐ 390 [UĐ], đây là sự kiện cấu trúc lớn nhất của lượt đọc:**
- Ngưỡng 5 tr tương đương khoảng **0,36 chỉ** ở giá 139,5 tr/lượng (1 chỉ khoảng 13,95 tr). Gần như **mọi giao dịch từ 1 chỉ trở lên
  phải chuyển khoản**. Dòng tiền mua vàng (và **bán lại vàng cũ**) của dân gần như toàn bộ bị ngân hàng ghi vết.
- Cộng với hoá đơn điện tử bắt buộc từ 01/01/2026 và thuế theo doanh thu thực, **lợi thế "tiền mặt, không hoá đơn" của tiệm nhỏ gần
  như mất**. Tiệm nhỏ phải gánh chi phí tuân thủ và mất khách muốn ẩn danh. Khách muốn ẩn danh thì không còn kênh hợp pháp nào.
- ⇒ Hướng tác động là **chính thức hoá, dịch chuyển thị phần từ tiệm nhỏ sang chuỗi** (chuỗi đã có POS, hoá đơn, KYC). Cùng lúc,
  **tổng cầu tích trữ vàng có thể co lại** ở nhóm khách tránh ghi vết. Hai tác động này ngược chiều nhau về tổng thị trường nhưng
  cùng chiều về thị phần của chuỗi.
- Bỏ điều kiện kinh doanh trang sức thì **rào cản gia nhập giảm**. Nhưng rào cản này vốn yếu [NỀN], nên tác động thực tế nhỏ. Rào
  cản thật của chuỗi là thương hiệu, độ phủ, kiểm định và vốn lưu động.
- Kênh nhập vàng nguyên liệu cho **gia công xuất khẩu** mở ra. Cho **bán lẻ nội địa** thì vẫn phụ thuộc hạn mức NHNN (chưa cấp).
  ⇒ Cung vàng nguyên liệu cho trang sức nội địa **vẫn chủ yếu là vàng mua lại từ dân** (vàng cũ) [NỀN + UĐ]. Trước NĐ 390, một bài
  báo nêu doanh nghiệp cần ít nhất 3,5 tấn nguyên liệu/năm và phải mua vàng trôi nổi, kéo theo rủi ro pháp lý [DK cấp 2, Báo Đầu tư].
  NHNN từ chối mở nhập khẩu cho khoảng 7.000 doanh nghiệp [DK, doanhnghiephoinhap 26/06/2026].
- **Rủi ro pháp lý của nguồn vàng cũ:** khi mọi giao dịch ≥5 tr đều có chứng từ ngân hàng, đầu vào vàng cũ được hợp thức hoá tốt
  hơn (bảng kê + chuyển khoản). Nhưng dữ liệu lịch sử trước 16/10/2026 thì không [UĐ]. DD phải kiểm.

### 3b. Cấu trúc cạnh tranh [NỀN, chưa kiểm trong lượt này, PHẢI KIỂM bằng số]
- **38 doanh nghiệp/ngân hàng** có phép kinh doanh mua bán vàng miếng. Chỉ một số đầu ngành có vốn ≥1.000 tỷ [DK cấp 2, tóm tắt
  tìm kiếm]. Hàng nghìn tiệm vàng hộ gia đình bán trang sức 24K/18K và nhẫn trơn.
- **Chuỗi lớn vs tiệm nhỏ:** chuỗi thắng ở trang sức thiết kế, kim cương, kiểm định, trả góp, mua lại. Tiệm nhỏ thắng ở vàng 24K
  theo trọng lượng (chênh mua-bán thấp, quan hệ địa phương). Thị phần chuỗi có tổ chức: không có số. Theo [NỀN], vẫn là thiểu số
  của thị trường trang sức VN.
- **Biên gộp từng mảng** [NỀN, PHẢI KIỂM trên BCTC thuyết minh của DN]:
  - Trang sức bán lẻ: cao nhất, khoảng vài chục phần trăm (phí gia công, thiết kế, kim cương).
  - Trang sức bán buôn: khoảng 1 chữ số đến thấp 2 chữ số.
  - Vàng miếng/vàng nhẫn 24K: khoảng 1-3%, đúng bằng chênh mua-bán.
  - ⇒ **Cơ cấu doanh thu quyết định biên gộp hợp nhất nhiều hơn giá vàng.** Năm "sốt vàng", doanh thu 24K phình lên và biên hợp
    nhất bị pha loãng. Năm trang sức hồi, biên hợp nhất tăng [UĐ].
- **Ngân hàng làm vàng miếng** (2 NH đã có thương hiệu 9999, 01/2026) là đối thủ mới ở mảng 24K biên mỏng, không phải ở trang sức [DK
  VnEconomy 13/01/2026 + UĐ].

### 3c. Rủi ro nguồn cung đá quý / kim cương
- **Nhập khẩu chính ngạch:** kim cương 2025 là **241,2 triệu USD**. 6T/2026 là **121,5 triệu USD**, đi ngang so với nhịp 2025. Ấn Độ
  là nguồn lớn nhất [DK, Cục Hải quan qua Tạp chí Thuế-Hải quan 11/07/2026 và Viettimes].
- **Thuế:** HS 7102.31 MFN 0%, thông thường 5% [DK cấp 3, trang tra mã HS. PHẢI KIỂM biểu thuế gốc]. Còn VAT nhập khẩu [NỀN].
- **Thông tư 48/2026/TT-BCT** (ký 05/09/2026, hướng dẫn NĐ 292/2026): kim cương thô chỉ được giao dịch với thành viên **Kimberley
  Process**, cần chứng nhận KP từng lô, niêm phong, lưu hồ sơ ≥3 năm [DK, VietnamFinance 11/09/2026]. Áp cho **kim cương thô**, không
  áp trực tiếp cho kim cương đã mài.
- **Buôn lậu (WARNING ngành):** ngày **02/07/2026**, Công an Thanh Hoá công bố phá đường dây xuyên quốc gia (đầu mối người nước ngoài
  ở Hồng Kông). Từ 2024, đường dây thực hiện **141 lượt** đưa **hơn 28.000 viên** kim cương vào VN, doanh thu khoảng **280 tỷ đồng**.
  Thu giữ 1.100 viên, khởi tố 22 bị can (nguồn khác nêu 38). Thủ đoạn gồm **mài số GIA rồi khắc lại mã và cấp giấy kiểm định của một
  phòng giám định trong nước**. Kim cương lậu chào giá rẻ hơn khoảng 1/3 [DK, Bộ Công an qua Báo Văn hoá, Tạp chí Thuế-Hải quan
  03/07/2026, VTC 23/07/2026].
  - Quy mô so với chính ngạch: khoảng 110 tỷ/năm, tức khoảng **2%** giá trị nhập chính ngạch [UĐ, tự tính, chỉ một đường dây]. Thị
    trường lậu thật có thể lớn hơn.
  - ⇒ Tác động ngành [UĐ]: (i) **độ tin cậy giấy kiểm định trong nước bị tổn hại**, khách chuyển sang đòi GIA/IGI gốc. (ii) Hải quan và
    công an siết truy xuất nguồn gốc với mọi nhà bán kim cương. (iii) Kim cương lậu giá rẻ hơn 1/3 là **cạnh tranh giá không lành mạnh**
    với hàng chính ngạch. Siết lậu là thuận cho chuỗi tuân thủ, nhưng chỉ với điều kiện chuỗi đó sạch.
- **Kim cương nhân tạo (LGD):** chỉ số giá bán lẻ 1,00ct LGD **−30,1%** từ 03/2025 tới 06/09/2026, kim cương tự nhiên −3,5% [DK cấp 2,
  TheDiamondPrice.com]. De Beers cắt giá thô **10-15%** tháng 01/2026. Rapaport: chỉ số giá thô hiệu dụng 2025 −25% [DK cấp 2,
  Jing Daily 20/01/2026, Yahoo/AOL]. ⇒ [UĐ] Có 2 rủi ro: **giảm giá trị tồn kho kim cương tự nhiên** và **nén giá bán/biên** khi LGD
  phổ biến. Với chuỗi, LGD cũng là dòng sản phẩm biên cao nếu định vị đúng. Nhưng đây là rủi ro cấu trúc với giá trị kim cương tự
  nhiên trong tồn kho.

## 4. Phân loại (2 trục + 3 nhãn)
**Trục 1, nguyên nhân gốc của bối cảnh hiện tại:**
- Khối lượng trang sức giảm sâu (−39% YoY Q3) chủ yếu do **giá vàng thế giới tăng vọt rồi biến động mạnh** (ngoại sinh, CYCLICAL).
  Đây không phải co cầu tiêu dùng nội địa: bán lẻ chung vẫn +13% danh nghĩa.
- Cung vàng miếng bị khoá hành chính, nên premium khoảng 10% tồn tại (ADMIN).
- Khung pháp lý đang **chính thức hoá nhanh** (thuế khoán, hoá đơn điện tử, ngưỡng 5 tr, KYC, truy xuất kim cương). Đây là STRUCTURAL
  về thị phần, đi cùng gió ngược nhẹ về nhân khẩu học (kết hôn muộn) và giảm phát giá kim cương do LGD.

**Trục 2, có tự giới hạn không:**
- Phần CYCLICAL (giá vàng) chạy theo **lịch toàn cầu** (Fed, USD, NHTW mua vàng: Q3/2026 mua ròng 321 tấn, +42% YoY). VN không kiểm soát.
- Phần ADMIN chạy theo **lịch NHNN**, có mốc cụ thể: xét hạn mức khoảng 15/12/2026, thời điểm thu thuế 0,1%, sàn vàng. Nó có thể mở
  trong vài tháng, hoặc kéo dài nhiều năm (2012-2025 là 13 năm độc quyền).

| Tầm | CYCLICAL | ADMIN_GATED | STRUCTURAL | Lý do |
|---|---|---|---|---|
| **12 tháng** | **0,40** | **0,40** | 0,20 | KQKD 12T do giá vàng (khối lượng trang sức, doanh thu 24K, lãi/lỗ tồn kho) và cửa ngõ hành chính (hạn mức nhập, cấp phép vàng miếng, ngưỡng 5 tr vừa áp từ 16/10, thuế 0,1%) quyết gần ngang nhau. Chính thức hoá mới bắt đầu thể hiện |
| **36 tháng** | 0,25 | 0,30 | **0,45** | Giá vàng trung bình hoá. Dịch chuyển thị phần từ tiệm nhỏ sang chuỗi (thuế, hoá đơn, không tiền mặt, tiêu chuẩn, KYC) là xu hướng nhiều năm. Kèm 2 gió ngược cấu trúc: LGD và nhân khẩu học. ADMIN còn lại là nhịp cấp phép/nhập khẩu và rủi ro đảo chính sách |

**Độ tin cậy: ambiguous khoảng 55/45.** Nhãn 12T là hai nhãn ngang nhau (CYCLICAL ≈ ADMIN). Nhãn 36T nghiêng STRUCTURAL, nhưng
chiều tác động lên chuỗi lớn **chưa chắc**: chính thức hoá có lợi thị phần, nhưng có thể co tổng cầu tích trữ.
**Pha [UĐ]:**
- Khối lượng trang sức: **gần đáy chu kỳ** (Q3/2026 thấp nhất WGC từ 2000 ở cấp toàn cầu), với giá vàng đã hạ 27% từ đỉnh.
- Cung vàng 24K: **trước cửa mở**, chưa mở.
- Chính thức hoá: **năm 1 của nhịp nhiều năm**.

## 5. FORECAST khoá trước (2026-11-14)
Bobby không tự chấm. Mike hoặc người chấm đọc nguồn chính thức (WGC, NSO, NHNN, Chính phủ/Công báo, Hải quan) vào ngày chấm.
ĐÚNG/SAI theo ngưỡng trong bảng. Nguồn không công bố trước ngày chấm thì chấm "không chấm được", không tính.

| # | Mệnh đề | Ngày chấm | P |
|---|---|---|---|
| F1 | WGC Gold Demand Trends FY2026: **trang sức VN Q4/2026 (tấn) < Q4/2025** | 2027-02-15 | 0,70 |
| F2 | WGC FY2026: **trang sức VN cả năm 2026 giảm ≥15% YoY** về tấn | 2027-02-15 | 0,70 |
| F3 | WGC Q1/2027 (công bố khoảng cuối T4/2027): **trang sức VN Q1/2027 (tấn) ≥ Q1/2026**, tức đáy khối lượng đã qua | 2027-05-15 | 0,45 |
| F4 | NHNN công bố **≥1 giấy phép sản xuất vàng miếng** cho tổ chức ngoài thương hiệu Nhà nước hiện hữu | 2027-03-31 | 0,45 |
| F5 | NHNN công bố **cấp hạn mức nhập khẩu vàng nguyên liệu năm 2027** (bất kỳ lượng nào) cho ≥1 DN/NH, không tính giấy phép theo hợp đồng gia công xuất khẩu | 2027-03-31 | 0,40 |
| F6 | Premium SJC (chiều bán) so với thế giới quy đổi, theo báo chí ngày chấm, **≤10 tr/lượng** (hiện khoảng 13 tr) | 2027-03-31 | 0,40 |
| F7 | Chính phủ ban hành văn bản ấn định **ngày bắt đầu thu thuế TNCN 0,1% chuyển nhượng vàng miếng** | 2027-06-30 | 0,35 |
| F8 | **Sàn giao dịch vàng** (bất kỳ giai đoạn thí điểm) chính thức vận hành giao dịch | 2027-06-30 | 0,15 |
| F9 | NHNN/Chính phủ **nới** (nâng) ngưỡng 5 tr thanh toán không tiền mặt cho vàng | 2027-06-30 | 0,15 |
| F10 | NSO: bán lẻ hàng hoá **cả năm 2026 danh nghĩa ≥ +12,0%** (10T: +12,9%) | 2027-01-10 | 0,80 |
| F11 | NSO: **CPI YoY T12/2026 ≥ 4,5%** (T10: 5,09%) | 2027-01-10 | 0,65 |
| F12 | Vàng giao ngay (LBMA PM hoặc COMEX settle) ngày 31/03/2027 **≥ 4.000 USD/oz** (11/11: khoảng 4.050) | 2027-03-31 | 0,55 |
| F13 | Hải quan: nhập khẩu kim cương (HS 7102) **cả năm 2026 ≥ 241,2 triệu USD** (bằng 2025) | 2027-03-31 | 0,50 |
| F14 | Bộ Công an hoặc Hải quan công bố **≥1 vụ khởi tố mới** về buôn lậu, hợp thức hoá kim cương/đá quý/vàng có liên quan DN kinh doanh trang sức hoặc phòng giám định (vụ khác vụ công bố 02/07/2026) | 2027-06-30 | 0,45 |
| F15 | CCTG 12M Big-4 cao nhất (`cctg_rate_vn`) ngày 2027-05-14 **≤ 7,4%** | 2027-05-14 | 0,55 |

Lập luận [UĐ]:
- F1 và F2 dựa trên quán tính Q1-Q3 và Q4/2025 là nền giá còn thấp hơn.
- F3 đặt dưới 0,5: Q1/2026 có giá trị trang sức kỷ lục và chuyển dịch sang nhẫn, nên nền cao. Ngưỡng 5 tr áp từ 16/10 có thể làm mùa
  Tết/Thần Tài 2027 trầm hơn ở kênh tiền mặt.
- F4 và F5 thấp hơn 0,5 vì 13 tháng sau NĐ 232 vẫn chưa thấy cấp phép. NHNN nhấn "thận trọng", USD/VND còn nhạy, và chính quyền đang
  ưu tiên kiểm soát dòng tiền (NĐ 390) hơn là mở cung.
- F6 phụ thuộc F4/F5. F9 thấp vì NĐ 390 vừa siết có chủ đích.

**Điều làm tôi đổi phân loại:**
- (i) NHNN cấp hạn mức nhập vàng 2027 đáng kể và premium về ≤5 tr ⇒ ADMIN 12T hạ xuống khoảng 0,25. Biên 24K và doanh thu tích trữ
  trở về thuần CYCLICAL.
- (ii) Số liệu 2-3 quý sau 16/10 cho thấy tổng cầu vàng VN (WGC) co mạnh hơn khu vực, trong khi giá ổn định ⇒ ngưỡng 5 tr đang **co tổng
  thị trường**, không chỉ chuyển thị phần ⇒ hạ phần "STRUCTURAL thuận cho chuỗi" và nâng ADMIN 36T.
- (iii) Vụ khởi tố mới (F14) chạm tới mắt xích bán lẻ hoặc phòng giám định lớn ⇒ thêm nhãn ADMIN/pháp lý cho mảng kim cương 36T.
- (iv) Giá vàng thế giới lập đỉnh mới >5.600 USD/oz trước 30/06/2027 ⇒ CYCLICAL 12T lên khoảng 0,55 (khối lượng trang sức lại đáy mới).

## 6. DD cần kiểm gì: chuỗi trang sức niêm yết (kiểm bằng số)
1. **Cơ cấu doanh thu và biên gộp theo mảng** (thuyết minh BCTC, ≥12 quý): trang sức bán lẻ / bán buôn / vàng 24K (miếng + nhẫn) /
   bạc / khác. Biên gộp từng mảng. Tách tác động cơ cấu khỏi tác động giá vàng lên biên hợp nhất.
2. **Khối lượng, không chỉ doanh thu:** số lượng sản phẩm, trọng lượng vàng bán ra, giá trị đơn hàng bình quân, SSSG theo quý. So với
   WGC VN (−39% Q3) để biết DN lấy thị phần hay chỉ hưởng giá.
3. **Tồn kho:** cơ cấu (vàng kg, kim cương/đá quý theo giá trị), số ngày tồn kho, phương pháp giá xuất kho (bình quân gia quyền?), lãi/lỗ
   tồn kho khi giá vàng −27% từ đỉnh, dự phòng giảm giá. VN không có công cụ phòng hộ giá vàng chính thức [NỀN]. Hỏi chính sách
   "khớp vị thế" (mua lại vàng cũ bù bán ra) nếu có.
4. **Nguồn vàng nguyên liệu:** % mua lại từ dân / từ NH và DN được phép / nhập khẩu. Chứng từ đầu vào (bảng kê, hoá đơn) trước và sau
   16/10/2026. Rủi ro thuế với nguồn mua không hoá đơn lịch sử. Có hợp đồng gia công xuất khẩu để xin nhập vàng theo NĐ 390 không.
5. **Vàng miếng:** giấy phép mua bán vàng miếng, **đã nộp hồ sơ sản xuất vàng miếng / hạn mức nhập 2027 chưa** (hạn 15/11), trạng thái
   xét duyệt. Doanh thu và biên mảng này nhạy thế nào với kịch bản premium co lại (F6).
6. **Kim cương và đá quý:** % nhập chính ngạch (tờ khai, nước xuất xứ, chứng nhận KP cho đá thô), % mua trong nước và từ ai, tỷ lệ đá
   có GIA/IGI gốc so với giấy kiểm định nội bộ. Kiểm soát nội bộ của phòng giám định (độc lập với kinh doanh?). Quan hệ bên liên quan.
   **WARNING pháp lý** theo luật user 27/09: phân tích bình thường trên BCTC, ghi tình trạng pháp lý (vụ việc, tiến trình tố tụng, phạm vi
   pháp nhân bị liên đới, hoàn thuế/phạt tiềm năng, uy tín thương hiệu) thành WARNING tường minh, có nguồn.
7. **LGD:** có bán LGD không, tỷ trọng, định giá, chính sách công bố cho khách (phân biệt LGD/tự nhiên). Giá trị tồn kho kim cương tự
   nhiên so với chỉ số giá thô 2025-2026 (−25% Rapaport).
8. **Không tiền mặt và tuân thủ:** % giao dịch qua POS/chuyển khoản trước và sau 16/10. Chi phí phí thẻ. Hệ thống báo cáo NHNN. Hoá đơn
   điện tử từng giao dịch. AML/KYC.
9. **Chuỗi cửa hàng:** số cửa hàng, mở/đóng ròng, doanh thu/m², phân bố vùng, kênh online. Thị phần ước so với tiệm nhỏ (nếu có nguồn độc lập).
10. **Vốn lưu động và nợ:** vay ngắn hạn, lãi suất (biên trên lãi huy động 12M?), ngày phải thu bán buôn, khả năng gia hạn hạn mức tín
    dụng khi giá vàng biến động.
11. **Mùa vụ:** tỷ trọng Q1 (Tết, Thần Tài giữa T2/2027) và Q4 (mùa cưới). Kế hoạch 2027 DN tự đặt.
12. **Bán buôn:** khách bán buôn là ai (tiệm nhỏ?). Nếu NĐ 390 làm tiệm nhỏ co lại, bán buôn có bị ảnh hưởng không. Rủi ro tín dụng của khách.
13. **Bạc và dòng giá thấp:** tỷ trọng doanh thu, biên gộp, xu hướng.
14. **Thuế 0,1% vàng miếng:** độ nhạy doanh thu 24K nếu Chính phủ ấn định ngày thu (F7).

## 7. Tự kiểm và giới hạn
- **Tốt hơn tôi nghĩ:**
  - Giá vàng đã hạ khoảng 27% từ đỉnh, thuận cho khối lượng trang sức.
  - Bán lẻ chung và lương còn tăng.
  - NĐ 390 nghiêng thị phần về phía chuỗi tuân thủ.
  - Chi phí vốn không tăng (LNH 3M −0,62pp/3T).
- **Xấu hơn tôi nghĩ:**
  - Trang sức VN −39% YoY Q3, yếu nhất khu vực.
  - Hàng giá trị lớn yếu (ô tô −28%).
  - Ngưỡng 5 tr có thể co tổng cầu ở nhóm tiền mặt.
  - Cung vàng miếng vẫn khoá sau 13 tháng.
  - Kim cương có 2 rủi ro: lậu (niềm tin giấy kiểm định) và LGD giảm phát giá.
- **Chưa biết:** số kết hôn, thị phần chuỗi, biên ngành, cách WGC xếp nhẫn trơn, toàn văn NĐ 390, giá vàng bình quân Q3, hạn mức 2027.
- Snapshot vĩ mô là bản TE UNVERIFIED, không có vintage. Mọi số báo chí là cấp 2 so với văn bản gốc. Ngày đăng của một số trang tổng
  hợp không đáng tin. Tôi đã loại các số có dấu hiệu thuộc năm 2025 hoặc sau ngày 14/11/2026.
- Rò rỉ danh tính ở §0 làm bản đọc này **không hoàn toàn mù về danh tính**. Nó vẫn mù về giá cổ phiếu, BCTC và forward return.

## Nguồn (một số URL có tên DN/tổ chức trong đường dẫn — người đọc blind sau có thể bỏ qua)
- Snapshot: `agents/Taylor/research/dd_PNJ_20261114/macro_snapshot_20261114_for_bobby.md` (BQ `tav2_bq.macro_indicator`, as-of 14/11/2026). Lãi suất: `deposit_rate_vn.effective_deposit_rate('2026-11-14')` (Big-4 6,8% @09/11; CCTG 12M 7,4% @02/11).
- WGC Gold Demand Trends Q3 2026 — Jewellery, 03/11/2026: https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-q3-2026/jewellery
- VietNamNet, cầu vàng VN Q1/2026, 07/05/2026: https://vietnamnet.vn/en/vietnam-s-gold-demand-falls-to-lowest-level-in-southeast-asia-2513264.html
- Giá vàng 11/11/2026: https://bbw.vn/sjc-mat-14-trieu-dong-chenh-lech-voi-vang-the-gioi-vuot-13-trieu-61472.html ; 04/11 và 10/11: https://bbw.vn/vang-trong-nuoc-tang-chenh-lech-voi-the-gioi-17-trieu-dong-61324.html , https://bbw.vn/sjc-tang-300000-dong-chenh-lech-voi-vang-the-gioi-van-tren-12-trieu-61444.html
- Vàng quý 3/2026 (COMEX 30/09), 13/10/2026: https://topi.vn/vang-ket-thuc-quy-3-2026-lai-suat-usd-va-nhu-cau-du-tru-dang-dinh-hinh-thi-truong.html
- Vàng miếng thương hiệu ngân hàng, 13/01/2026: https://vneconomy.vn/hai-ngan-hang-ra-mat-vang-mieng-4-so-9-thuong-hieu-rieng.htm
- NĐ 232/2025 và tiến độ cấp phép: https://vnbusiness.vn/9-ong-lon-dau-tien-sap-duoc-cap-phep-san-xuat-vang-mieng.html (29/12/2025) ; https://vnbusiness.vn/da-co-11-ho-so-xin-cap-phep-san-xuat-vang-mieng-than-trong-xem-xet-nhap-khau-vang-nguyen-lieu.html (04/2026) ; https://vnba.org.vn/vi/ngan-hang-nha-nuoc-dang-xem-xet-9-ho-so-xin-cap-phep-san-xuat-vang-mieng-20315.htm (26/07/2026) ; https://lsvn.vn/ngan-hang-nha-nuoc-du-kien-cap-han-muc-nhap-vang-truoc-15-12-hang-nam-a163952.html ; https://luatvietnam.vn/thuong-mai/nghi-dinh-232-2025-nd-cp-sua-doi-quan-ly-kinh-doanh-vang-theo-nghi-dinh-24-2012-nd-cp-409841-d1.html
- NĐ 390/2026 (16/10/2026): https://lsvn.vn/quy-dinh-moi-mua-ban-vang-trong-ngay-tu-5-trieu-dong-phai-thanh-toan-khong-dung-tien-mat-a181112.html (20/10) ; https://lsvn.vn/sua-doi-quy-dinh-ve-xuat-nhap-khau-vang-nguyen-lieu-a181115.html (19/10) ; https://vov.vn/kinh-te/tu-1610-mua-ban-vang-tu-5-trieu-dong-phai-thanh-toan-khong-tien-mat-post1342302.vov ; https://tapchicongthuong.vn/tu-16-10-2026--mua--ban-vang-tu-5-trieu-dong-ngay-phai-thanh-toan-khong-dung-tien-mat-558821.htm ; https://lsvn.vn/chinh-thuc-vang-trang-suc-khong-con-la-nganh-nghe-kinh-doanh-co-dieu-kien-a181143.html ; dự thảo 03/06/2026: https://lsvn.vn/du-kien-bo-giay-phep-con-doi-voi-vang-trang-suc-a173570.html
- Nhập vàng nguyên liệu, 7.000 DN: https://doanhnghiephoinhap.vn/khong-the-mo-cua-nhap-khau-vang-nguyen-lieu-cho-gan-7000-doanh-nghiep-141107.html (26/06/2026) ; https://baodautu.vn/hoa-giai-rui-ro-cho-doanh-nghiep-vang-trang-suc-d304299.html
- Thuế 0,1% vàng miếng (Luật 109/2025/QH15; chưa thu): https://vneconomy.vn/quoc-hoi-chot-thu-01-thue-chuyen-nhuong-vang-mieng.htm ; https://doanhnhan.baophapluat.vn/chua-thu-thue-doi-voi-hoat-dong-chuyen-nhuong-vang-mieng-tu-ngay-01-7-2026.md ; https://thuvienphapluat.vn/ma-so-thue/phap-luat-thue/tu-01072026-mua-ban-vang-co-phai-dong-thue-khong-227350.html
- Bỏ thuế khoán 01/01/2026: https://www.sapo.vn/blog/thue-khoan-ho-kinh-doanh ; https://nongnghiepmoitruong.vn/huong-dan-ho-kinh-doanh-ke-khai-theo-luat-thue-moi-d794487.html
- Sàn vàng: https://thesaigontimes.vn/ngan-hang-nha-nuoc-se-thi-diem-san-giao-dich-vang-theo-3-giai-doan/ (25/06/2026) ; https://vcci.com.vn/tin-tuc/thu-tuong-yeu-cau-hoan-thien-ho-so-lap-so-san-giao-dich-vang ; https://doanhnghiephoinhap.vn/ngan-hang-nha-nuoc-nghien-cuu-lo-trinh-thanh-lap-san-giao-dich-vang-115601.html (08/2026)
- Bán lẻ 10T/2026 (NSO): https://www.vietnamplus.vn/tong-muc-ban-le-hang-hoa-va-doanh-thu-dich-vu-tieu-dung-10-thang-tang-135-post1146090.vnp ; https://www.nso.gov.vn/wp-content/uploads/2026/11/Thang-10.2026_VN-final.pdf
- TFR, kết hôn muộn: https://www.vietnamplus.vn/bai-toan-sinh-du-hai-con-ngay-cang-cap-thiet-doi-voi-cong-tac-dan-so-post1141111.vnp ; https://www.vtcnews.vn/gioi-tre-ngai-cuoi-luoi-sinh-bo-truong-y-te-neu-giai-phap-thao-go-ar994198.html
- Bạc: https://vnbusiness.vn/bac-doi-song-gia-tien-sat-moc-86-trieu-dongkg.html ; https://nhandan.vn/post-933621.html
- Kim cương (TT 48/2026, nhập khẩu, buôn lậu): https://vietnamfinance.vn/bo-cong-thuong-ra-quy-dinh-moi-ve-xuat-nhap-khau-kim-cuong-d150454.html (11/09/2026) ; https://thuehaiquan.tapchikinhtetaichinh.vn/tu-vu-buon-lau-28-000-vien-kim-cuong-viet-nam-nhap-khau-kim-cuong-nhieu-nhat-tu-nuoc-nao-161277.html (11/07/2026) ; https://baovanhoa.vn/phap-luat/triet-pha-duong-day-buon-lau-hon-28000-vien-kim-cuong-doanh-thu-280-ti-dong-242527.html (07/2026) ; https://thuehaiquan.tapchikinhtetaichinh.vn/triet-pha-duong-day-buon-lau-28000-vien-kim-cuong-160725.html (03/07/2026) ; https://www.vtcnews.vn/kim-cuong-gia-re-bat-thuong-len-loi-vao-thi-truong-the-nao-ar1030055.html (23/07/2026, không mở được, chỉ qua tóm tắt) ; HS 7102.31: https://caselaw.vn/chi-tiet-ma-hs/71023100
- LGD/giá kim cương: https://thediamondprice.com/diamond-price-index/ (06/09/2026) ; https://jingdaily.com/intels/2026-01/20/de-beers-slashes-rough-diamond-prices-by-10-15 ; https://www.aol.com/finance/price-diamonds-crashes-lowest-level-151700514.html
- NHTW mua ròng 321 tấn Q3/2026: https://doanhnhan.baophapluat.vn/ngan-hang-trung-uong-tiep-tuc-gom-vang-nhu-cau-toan-cau-quy-iii-gan-nhu-di-ngang.html
