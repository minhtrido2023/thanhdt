---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-01. Không được cung cấp mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của ai về doanh nghiệp cụ thể, và không đi tìm chúng.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ nhóm CNTT Việt Nam gồm 3 khối. (1) Xuất khẩu dịch vụ phần mềm/outsourcing (Nhật, Mỹ, châu Âu, APAC) và chuyển đổi số nội địa (khu vực công, ngân hàng). (2) Viễn thông băng rộng cố định và trung tâm dữ liệu/cloud. (3) Giáo dục tư nhân (đại học, phổ thông, đào tạo CNTT). Có pipeline cầu, cạnh tranh và biên điển hình, rủi ro cấu trúc, phân loại chế độ từng khối, FORECAST khoá trước và checklist DD cho doanh nghiệp đa ngành loại này.
as_of: 2026-11-01 (tin web ≤ 2026-10-31; không truy vấn BQ cấp DN, không đọc BCTC)
---

# SECTOR READ: CNTT, viễn thông/TTDL, giáo dục tư nhân Việt Nam, as-of 01/11/2026 (Bobby, real-time BLIND)

File này không phải episode VNINDEX và không tính vào N_effective. Nhãn: **[DK]** là dữ kiện có nguồn và ngày. **[UĐ]** là ước đoán
hoặc suy luận của Bobby. **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này, có thể sai, không dùng làm số pin. **(ước lượng)** là
số Bobby tự tính hoặc không kiểm chứng được.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Đã đọc nội bộ:** `sector_read_xe_tai_thuong_mai_vn_20261101.md` (lấy định dạng), `vn_macro_regime_history.md` mục SECTOR READ 14/10
  "Định giá lại nhóm CNTT niêm yết" và mục xe tải 01/11. **Khai trung thực:** mục 14/10 là đọc của chính tôi, có chứa diễn biến giá
  1 năm, P/E và số 6T/2026 của 3 DN CNTT niêm yết (đều là dữ kiện trước as-of, PIT-knowable). Tôi **không chép** bất kỳ số cấp DN nào
  từ đó vào file này. Chỉ dùng lại phần cấp ngành (peer toàn cầu, JPY, lãi vay). Không đọc `kb/projects/*`, `agents/Taylor/*`, báo cáo DD.
  Không truy vấn `ticker`/`ticker_financial`.
- **Không tra:** giá cổ phiếu, BCTC, khuyến nghị CTCK của DN CNTT/viễn thông/giáo dục VN nào.
- **Rò thông tin cấp DN qua web (khai trung thực):**
  (a) Tin về giá điện TTDL nêu tên 5 nhà vận hành trong nước kiến nghị (Viettel, VNPT, FPT Telecom, VNG, CMC) và số "chi phí điện tăng hơn
  50% sau 3 kỳ hoá đơn" của **một** nhà vận hành có tên trong bài. Tôi dùng số này như bằng chứng cấp ngành về tác động Thông tư 60.
  (b) Tin cam kết đầu tư TTDL (VietnamNews 12/09/2026) nêu tên một liên doanh có một tập đoàn CNTT niêm yết trong nước. Tôi chỉ dùng tổng
  cam kết của ngành.
  (c) Tin ký kết đào tạo nhân lực cho Nhật giữa một DN CNTT trong nước và một SIer Nhật (VietnamNet 27/01/2026). Dùng như dấu hiệu mô hình
  giao hàng, không dùng số.
  (d) Kết quả tìm kiếm "tỷ lệ sinh viên tư thục" trả về một bài phỏng vấn lãnh đạo một đại học tư (số liệu 1999-2019). Dùng làm số nền cũ.
  **Ghi chú cho Mike (không phải phán đoán của tôi):** hình dạng "đa ngành CNTT xuất khẩu + băng rộng/TTDL + giáo dục" khớp với ít nhất 2 tập
  đoàn CNTT niêm yết VN. Tôi không xác định DN mục tiêu và không đọc BCTC của DN nào.

## 1. Khối 1: Xuất khẩu dịch vụ phần mềm và chuyển đổi số nội địa

### 1a. Cầu toàn cầu: tổng chi IT tăng mạnh, phần DỊCH VỤ bị hạ dự báo liên tục [DK]
| Chỉ tiêu | Số | Nguồn |
|---|---|---|
| Gartner, chi IT toàn cầu | 2026 khoảng 6,39 nghìn tỷ USD; **2027 7,35 nghìn tỷ (+15%)**; phần mềm 2027 +14,6%; hệ thống TTDL 2027 **+55,5%** | Gartner 21/10/2026 |
| Gartner, **IT services** | **2026: 1.557 tỷ USD, +4,4%; 2027: 1.633 tỷ, +4,9%**. Cùng chỉ tiêu 2026 ở các bản trước: 8,7% (T2), 9,0% (T4), 5,3% (T7) | Gartner 21/10/2026; phân tích thứ cấp (softwarestrategiesblog 19/10) cho các bản trước, chưa đối chiếu Databook |
| Infosys Q2 FY27 | DT cc **+1,5% YoY**; **hạ guidance FY27 còn 1-2% cc** (từ 1,5-3%); large deal 5,2 tỷ USD (có 1 deal > 2 tỷ); AI 10,5% DT; biên 20-22% giữ | báo chí Ấn Độ 23/10/2026 |
| TCS Q2 FY27 | DT cc **+2,8% YoY**, +0,5% QoQ; TCV 9,6 tỷ USD (năm trước 10 tỷ); AI quy năm 3,1 tỷ USD; DT Ấn Độ −10,3% QoQ | báo chí Ấn Độ 09-10/10/2026 |
| HCLTech Q2 FY27 | **Nâng đáy** guidance FY27 lên 2,5-4,0% cc (dịch vụ 3-4%); deal mới 3,26 tỷ USD; biên EBIT guidance 17,5-18,5% | báo chí 12/10/2026 |
| Cognizant Q3/2026 | DT +4,6% YoY (cc +4,8%); **hạ guidance 2026 cc còn 4,0-4,4%** (từ 4,0-5,5%); Q4 dự kiến +3,0-4,5% gồm khoảng 2pp M&A; biên điều chỉnh khoảng 16,1% | 8-K SEC 29/10/2026 |
| Cognizant, bình luận giá (T3/2026) | áp lực AI ở hợp đồng hiện hữu thể hiện qua **giảm khối lượng đơn vị**, không phải giảm đơn giá; dự án AI TCV 8-12 tr USD so với deal truyền thống 200-500 tr USD | MarketBeat 09/03/2026 (tóm tắt cuộc gọi) |
| Accenture Q4 FY26 | FY26 DT +5% LC; bookings Q4 22,2 tỷ USD, book-to-bill managed services 1,4; **FY27 guidance +3-6% LC** | 8-K SEC / newsroom 25/09-01/10/2026 |
| EPAM (Đông Âu gốc) | FY26 tăng hữu cơ cc 2-3% (guidance 06/08/2026); chưa thấy KQ Q3 | 8-K SEC 06/08/2026 |
| Kotak (CTCK Ấn Độ) | kịch bản cơ sở **xói mòn giá do AI khoảng 3,5%**, lộ trước ở hợp đồng tái ký nhiều năm | Tribune/NewKerala (chưa đọc báo cáo gốc) |

**Đọc [UĐ]:**
1. **Ngân sách IT đang chuyển từ "người" sang "máy".** Tổng chi IT 2027 +15% nhưng dịch vụ chỉ +4,9%, và dịch vụ bị hạ dự báo ở hầu hết
   các bản 2026. Đây là tái phân bổ (TTDL, chip, phần mềm AI) chứ không phải cắt tổng ngân sách. Với nhà cung cấp dịch vụ thuê ngoài, cái
   bánh lớn lên chậm hơn GDP danh nghĩa toàn cầu.
2. **Peer chia hai, chưa đồng nhất.** Infosys và Cognizant hạ; HCLTech nâng đáy; Accenture giữ 3-6%; TCS đi ngang. Điểm chung: tăng trưởng
   cc của nhóm lớn nằm trong **1-5%**, so với khoảng 8-12% thời 2021-2022 [NỀN]. Bookings vẫn cao (large deal Infosys 5,2 tỷ, TCV TCS 9,6
   tỷ), tức là **hợp đồng vẫn được ký nhưng chuyển hoá thành doanh thu chậm hơn và mỏng hơn trên mỗi đô la TCV** [UĐ].
3. **Cơ chế giảm phát AI** theo lời Cognizant là giảm số đơn vị (người-tháng) chứ chưa phải giảm đơn giá. Với mô hình T&M tính theo
   người-tháng, đó vẫn là giảm doanh thu. Với mô hình fixed-price/outcome, nhà cung cấp có thể giữ phần năng suất nếu định giá tốt.

### 1b. Thị trường Nhật: cầu nội tại tốt, gió ngược tỷ giá [DK trừ khi ghi khác]
| Chỉ tiêu | Số | Nguồn |
|---|---|---|
| BOJ Tankan T9/2026, kế hoạch FY2026 "phần mềm, R&D, đầu tư cố định trừ đất" | DN lớn mọi ngành **+11,0% YoY** (+0,2pp so với T6); DN lớn phi sản xuất **+15,0%**; mọi DN +9,3%. Bảng BOJ không tách riêng phần mềm. Nguồn thứ cấp nói riêng phần mềm, mọi DN, **+10,3%** | BOJ 01/10/2026; tóm tắt thứ cấp |
| Giả định tỷ giá FY2026 của DN Nhật | **154,23 JPY/USD** (T6: 152,57) | BOJ Tankan 01/10/2026 |
| USD/JPY | dao động khoảng 157-159 trong T10, 156,81 ngày 26/10; vùng "Tokyo bảo vệ 160" | roboforex 26/10; tradingnews (10/2026) |
| BOJ | nâng lên **1,25%** ngày 18/09/2026 (cao nhất từ 1995). Họp 29-30/10: dự kiến giữ, thị trường định giá 75-88% khả năng nâng T12. **Không tìm được kết quả họp 30/10** | Nation Thailand; tmgm/mitrade 13-14/10/2026 |
| Thiếu hụt kỹ sư IT Nhật | METI dự báo thiếu tới **790.000** người vào 2030 | Nikkei dẫn METI (qua tóm tắt) |
| Vị trí VN | VN khoảng **6-7%** thị trường thuê ngoài phần mềm của Nhật (> 30 tỷ USD/năm), là đối tác thứ 2; > 300 DN VN phục vụ Nhật | VINASA qua VietnamNet/MIC (chưa kiểm độc lập) |
| Mô hình | Japan ICT Day 04/02/2026: VINASA/JISA đề xuất chuyển từ "outsourcing theo nhân lực" sang "đối tác năng suất dùng AI"; một phần khách Nhật muốn đồng phát triển onsite | VietnamNet 02/2026; MOIT dẫn VietnamNet |

**Đọc [UĐ]:**
1. **Cầu Nhật là phần ít bị AI giảm phát nhất trong ngắn hạn.** Ba lý do: (i) kế hoạch đầu tư phần mềm DN Nhật FY2026 vẫn +10-11%; (ii) thiếu
   người là ràng buộc cung, không phải ràng buộc cầu; (iii) Nhật có lượng lớn hệ thống cũ cần chuyển đổi, cộng hạn chót bảo trì chính của
   SAP ECC cuối 2027 [NỀN, chưa kiểm lịch SAP 2026]. AI giúp làm migration nhanh hơn, nên số người-tháng mỗi dự án giảm, nhưng số dự án làm
   được tăng.
2. **Tỷ giá là gió ngược định lượng được.** DT tính bằng JPY quy sang USD/VND bị cắt khi JPY yếu. DN Nhật lập kế hoạch ở 154; spot 157-159.
   Nếu BOJ nâng T12 và Fed ngừng nâng, JPY có thể mạnh lên, đảo chiều thành gió thuận. Đây là biến số CYCLICAL, không phải cấu trúc.
3. **Cạnh tranh ở Nhật:** Trung Quốc (Đại Liên) là đối thủ truyền thống ở mảng tiếng Nhật [NỀN]; khách Nhật đa dạng hoá khỏi TQ vì địa chính
   trị [UĐ]; Ấn Độ yếu ở tiếng Nhật [NỀN]. Lợi thế VN ở Nhật là lợi thế **ngôn ngữ và quy trình**, khó bị AI xoá nhanh hơn lợi thế "giá rẻ thuần".

### 1c. Mỹ, châu Âu, APAC [phần lớn UĐ/NỀN]
- **Mỹ:** Fed nâng lãi 16/09/2026 (lần đầu từ 07/2023), giữ 3,75-4,00% ngày 28/10 (một nguồn blog giao dịch, chưa đối chiếu
  federalreserve.gov), thị trường định giá khả năng nâng T12 (Admiral Markets 10/2026). Chu kỳ nâng lãi làm DN Mỹ siết chi tiêu tuỳ ý (dự án
  mới, consulting) trước, chi tiêu vận hành (managed services) sau [NỀN]. Book-to-bill managed services của Accenture 1,4 so với consulting
  1,0 khớp với mô hình này.
- **Châu Âu:** EPAM tăng hữu cơ 2-3%; HCLTech có deal lớn với một hãng xe Đức. Tôi không có số chi IT châu Âu 2026 riêng.
- **APAC (ngoài Nhật):** không có số. Hàn Quốc, Singapore, Úc là thị trường nhỏ hơn với DN VN [NỀN].
- **Cạnh tranh giá:** Accelerance (2026) nói giá thuê ngoài châu Á, Đông Âu, Mỹ La-tinh đều nhích xuống; giá junior châu Á **24-31 USD/giờ**
  (blog ngành, độ tin cậy trung bình). Ấn Độ có quy mô và đang bán gói AI; Đông Âu đắt hơn và đang tăng trưởng chậm; VN cạnh tranh ở tầng
  giá giữa với Ấn Độ ở thị trường Mỹ/EU [UĐ].

### 1d. Cung lao động và AI thay thế lập trình [DK + UĐ]
- ITviec Q1/2026: tin tuyển **AI/Data/ML +96,6% YoY** (DK, marketing.itviec.com). TopDev 2025 (qua CareerLink) ước VN thiếu 150-200 nghìn kỹ sư
  CNTT 2025-2027, tập trung AI/dữ liệu/an ninh mạng (DK thứ cấp).
- Không có số chính thức VN về **tuyển fresher giảm do AI**. Nguồn quốc tế (blog ngành) nói nhiều DN outsourcing tuyển ít kỹ sư mới hơn 2 năm
  trước, và giá junior/mid mềm đi trong khi giá senior biết giám sát AI tăng. Độ tin cậy thấp-trung bình.
- **Đọc [UĐ]:** AI không thay toàn bộ lập trình viên trong cửa sổ 2026-2028, nhưng nó **bẻ cong hình kim tự tháp nhân sự**: cần ít junior hơn
  trên mỗi senior. Mô hình outsourcing VN dựa vào đáy kim tự tháp rộng (nhiều junior lương thấp, biên kiếm từ chênh lệch giá). Đây là rủi
  ro STRUCTURAL thật. Tốc độ: chậm ở Nhật (quy trình, ngôn ngữ, khách bảo thủ), nhanh hơn ở Mỹ.

### 1e. Chuyển đổi số nội địa: khu vực công và ngân hàng [DK]
| Chỉ tiêu | Số | Nguồn |
|---|---|---|
| NQ 57-NQ/TW | tối thiểu **3% tổng chi NSNN** cho KHCN, ĐMST, CĐS từ 2025 | nhiều nguồn |
| Kinh phí 2026 | Quốc hội phê chuẩn **65.020 tỷ** (30.720 thường xuyên + 34.300 ĐTPT) theo VnEconomy; có nguồn nêu **95.000 tỷ**. Hai số chưa rõ cùng phạm vi, **không trộn** | VnEconomy; TC KT-TC (2026) |
| Cơ cấu | khoảng 60% KHCN, 1,5% công nghệ chiến lược, 1,5% ĐMST, **38,5% chuyển đổi số** (một nguồn) | TC KT-TC (2026, tóm tắt) |
| **Giải ngân** | đến **26/10/2026: 41,18%** của 52.680 tỷ dự toán được dùng; địa phương 38,49% (còn 17.243 tỷ chưa giải ngân). Trung ương suy ra khoảng 44% (ước lượng) | Báo Pháp Luật 27/10/2026, dẫn Vụ KH-TC Bộ KH&CN |
| Chỉ đạo | CT 29/CT-TTg (16/07/2026) đòi giải ngân hết trong năm; TB 510/TB-VPCP (01/10/2026) cho điều chuyển vốn chậm; hội nghị tháo gỡ tài chính 19/05/2026 | Báo Pháp Luật; VJST |
| Ngân hàng | QĐ 826/QĐ-TTg (11/05/2026) đề án dữ liệu dân cư, định danh điện tử 2026-2030; NHNN QĐ 1906/QĐ-NHNN (24/08/2026) kế hoạch ngành; khảo sát Finastra đầu 2026: khoảng 9/10 tổ chức tài chính dự định nâng cấp core/hạ tầng trong năm tới | SBV; Vietstock 02/2026 |
| Khung pháp lý | Luật AI 134/2025/QH15 hiệu lực **01/03/2026**; NĐ 142/2026/NĐ-CP (30/04, hiệu lực 01/05/2026) hướng dẫn; TT 05/2026/TT-BKHCN khung đạo đức AI. Luật Dữ liệu (hiệu lực 01/07/2025), Luật BVDLCN (hiệu lực 01/01/2026), Luật Công nghiệp công nghệ số (hiệu lực 01/01/2026) [NỀN về ngày, chưa kiểm lại] | VnEconomy; luatvietan; luatvietnam (2026) |

**Đọc [UĐ]:**
1. **Tiền có, giải ngân là nút thắt.** 41% tại cuối T10 nghĩa là khoảng 31 nghìn tỷ phải giải ngân trong 2 tháng nếu muốn hết dự toán (ước
   lượng). Thực tế nhiều khả năng một phần lớn bị chuyển nguồn hoặc huỷ. Với nhà thầu CNTT, điều này nghĩa là **hợp đồng ký dồn Q4, nghiệm
   thu và thu tiền trễ sang 2027**, phải thu khu vực công phình ra.
2. Sáp nhập tỉnh và chính quyền 2 cấp (từ 01/07/2025) [NỀN] buộc làm lại hệ thống hành chính, cơ sở dữ liệu cấp tỉnh/xã. Đây là cầu một lần,
   cao điểm H2/2025-2026, sẽ nhạt dần 2027-2028 [UĐ].
3. Ngân hàng: cầu ổn định hơn khu vực công, nhưng cạnh tranh bởi vendor nước ngoài (core banking) và đội IT nội bộ ngân hàng [NỀN]. Các luật
   dữ liệu/BVDLCN/AI tạo cầu **tuân thủ** (an ninh, quản trị dữ liệu, kiểm toán AI). Cầu này nhỏ nhưng có biên tốt hơn phần cứng [UĐ].
4. Phần **cung cấp phần cứng/tích hợp** trong hợp đồng chuyển đổi số có biên thấp (pass-through). Doanh thu nội địa tăng nhanh có thể chủ yếu
   là phần cứng. Mục DD #A9.

### 1f. Số ngành VN: cảnh báo phạm vi
- "Công nghiệp công nghệ số" 9T/2026 **5,38 triệu tỷ đồng (+32,1%)**, T9 770.766 tỷ (+36%) (Bộ KH&CN, Báo Pháp Luật 30/09/2026). Năm 2025
  khoảng 215 tỷ USD (một nguồn) hoặc 224 tỷ USD (nguồn khác), trong đó phần cứng điện tử khoảng 172-199 tỷ USD. **Hơn 90% là phần cứng điện
  tử FDI** [UĐ từ cơ cấu]. Con số này **không đo** xuất khẩu phần mềm. Không dùng nó để suy cầu outsourcing.
- Số phần mềm gần nhất tôi đọc được là năm 2023: DT sản xuất phần mềm khoảng 4,3 tỷ USD, xuất khẩu khoảng 4 tỷ USD, tăng 4-8% (VnEconomy
  13/05/2024). **Không có số xuất khẩu phần mềm 2025 hay 9T/2026 cùng phạm vi.** Khoảng trống dữ liệu.

## 2. Khối 2: Viễn thông băng rộng cố định và trung tâm dữ liệu/cloud

### 2a. Băng rộng cố định (FTTH) [DK]
| Chỉ tiêu | Số | Nguồn |
|---|---|---|
| Hộ dùng cáp quang | **87,6%** (báo cáo cuối 2025 của Bộ KH&CN) | Phong Vũ 06/03/2026 (dẫn Bộ) |
| Thuê bao FTTH | khoảng **25 triệu** (02/2026), phủ 85% hộ | TelecomLead (độ tin cậy thấp, văn phong quảng cáo) |
| Thị phần | Viettel khoảng 44%, VNPT khoảng 33% (TelecomLead); GlobalData (dự báo cũ 2022-2024) cho VNPT dẫn đầu. **Hai nguồn mâu thuẫn**. Nhà cung cấp lớn thứ 3 là một DN tư nhân [NỀN] | TelecomLead; GlobalData |
| **Giá** | Đầu T3/2026 3 nhà mạng lớn **tăng gói thấp nhất**: 180.000 → **195.000** (2 nhà mạng) và **190.000** đ/tháng (1 nhà mạng), tức **+5,6% đến +8,3%**; nội thành HN/TP.HCM gói thấp nhất 235-255 nghìn. Lý do: nâng cấp XGS-PON, giá bộ nhớ trong router tăng (Counterpoint: chip nhớ +600%) | Phong Vũ 06/03/2026 |
| Tốc độ | Ookla 01/2026: 284,99 Mbps, hạng 10; 08/2026: 301,48 Mbps, hạng 8 | Phong Vũ; VnEconomy 2026 |
| Dự báo DT | GlobalData: DT băng rộng cố định tăng **2,3%/năm** 2025-2030 | TelecomLead dẫn GlobalData |
| Cạnh tranh mới | Starlink được cấp phép thí điểm 5 năm (02/2026), trần **600.000** thuê bao | VnEconomy 2026 |
| Sự cố hạ tầng | Cuối T8/2026 **4/8 tuyến cáp biển** quốc tế cùng sự cố (AAE-1 hỏng từ T2/2026; SJC2, AAG, IA), ảnh hưởng tới khoảng 30% lưu lượng quốc tế | VOV/VTC 27-28/08/2026; VietnamPlus |
| Di động (bối cảnh) | 5G 27,2 triệu thuê bao (08/2026, +94%); tắt 2G từ 16/09/2026 | VnEconomy 2026 |

**Đọc [UĐ]:**
1. **Thị trường bão hoà về số lượng** (87,6% hộ). Tăng trưởng đến từ **giá (ARPU) và nâng gói**, không từ thuê bao mới. Lần tăng giá đồng loạt
   đầu 2026 là dấu hiệu **kỷ luật giá của độc quyền nhóm** (2 DN nhà nước dẫn giá, 1 DN tư nhân theo). Đây là tín hiệu tốt cho biên, ngược với
   giai đoạn đua giảm cước trước 2020 [NỀN].
2. **Rủi ro giá ở phía nhà mạng nhà nước.** Nếu một nhà mạng nhà nước dùng FTTH làm sản phẩm bán kèm (gói gia đình di động + cố định + TV),
   giá FTTH thực sau khuyến mãi có thể giảm dù giá niêm yết tăng. **Giá niêm yết ≠ ARPU thực.** Mục DD #C2.
3. Starlink với trần 600.000 thuê bao là đối thủ nhỏ, chủ yếu vùng xa. Không đe doạ FTTH đô thị trong 2026-2028 [UĐ].
4. Sự cố cáp biển lặp lại làm tăng giá trị của **nội dung, CDN và TTDL đặt trong nước** (giảm phụ thuộc băng thông quốc tế) [UĐ]. Đồng thời
   tăng chi phí thuê kênh quốc tế cho ISP nhỏ không sở hữu cáp.

### 2b. Trung tâm dữ liệu và cloud [DK]
| Chỉ tiêu | Số | Nguồn |
|---|---|---|
| Công suất | Vận hành khoảng **100 MW** cuối 2025; **42 TTDL, khoảng 373 MW thiết kế** (05/2026, Bộ KH&CN), gấp hơn 4 lần 2021 | VietnamNews 12/09/2026 |
| Ước khác | BMI: khoảng 148 MW vận hành, 79 MW đang xây, > 870 MW công bố/kế hoạch | technode 20/07/2026 |
| 2030 | gần **600 MW** (một lãnh đạo TTDL của một nhà mạng nhà nước) | VietnamNews 12/09/2026 |
| Cam kết mới 2026 | 4 dự án nêu tên: 2 tỷ USD (T2), khoảng 2,1 tỷ USD TTDL AI (T3), 480 triệu và 509 triệu USD (T4), đều ở phía Nam | VietnamNews 12/09/2026 |
| Dự án lớn | một campus hyperscale 140 MW của nhà mạng nhà nước khởi công 04/2025, hoàn thành trước 2030; một DN tư nhân dự kiến khởi công 2026 TTDL tới 120 MW | VietnamNet; Tuổi Trẻ 27/03/2026 |
| Mở cửa vốn ngoại | Luật Viễn thông 2023 (hiệu lực 01/07/2024; phần TTDL/cloud/OTT từ 01/01/2025): **bỏ trần sở hữu nước ngoài** với dịch vụ TTDL, cloud; vẫn hạn chế nếu TTDL kèm dịch vụ kết nối mạng; là ngành nghề kinh doanh có điều kiện | lsvn; vision-associates; JLL (qua tóm tắt) |
| **Giá điện** | TT 60/2025/TT-BCT (hiệu lực 02/12/2025): TTDL cung cấp dịch vụ ra ngoài áp **giá kinh doanh** thay giá sản xuất; điện là 40-50% chi phí vận hành; một nhà vận hành báo chi phí điện **+50%** sau 3 kỳ hoá đơn. BCT hướng dẫn EVN 13/02 và **22/04/2026**; dự thảo sửa TT 60 lấy ý kiến 26/05-06/06/2026 (CV 3694/BCT-ĐL). Đến **21/09/2026**: phần lớn công ty điện lực đã ký áp **giá sản xuất** cho hệ thống kỹ thuật TTDL theo văn bản 2818, nhưng **EVN HCMC và một số đơn vị con vẫn áp giá kinh doanh**; Bộ KH&CN gửi văn bản lần thứ 3 ngày 15/09 | KTSG/Tuổi Trẻ 18/02/2026; VCCI; MOIT dự thảo; VietnamNet EN 21/09/2026 |
| Điện | Viện Năng lượng cảnh báo **thiếu điện có thể từ 2027** nếu không thêm nguồn nền; TTDL dùng khoảng 0,5% điện cả nước | VietnamNews 12/09/2026 |

**Đọc [UĐ]:**
1. **Cầu TTDL là thật và đến từ 3 nguồn:** (i) AI/GPU (cầu mới, mật độ điện cao); (ii) cloud và nội địa hoá dữ liệu (luật dữ liệu, BVDLCN, quy
   định lưu trữ trong nước [NỀN: NĐ 53/2022]); (iii) giảm phụ thuộc cáp biển. Nguồn (ii) và (iii) là STRUCTURAL. Nguồn (i) gắn với chu kỳ capex
   AI toàn cầu (CYCLICAL ở biên).
2. **Cung đang chạy nhanh hơn cầu đã ký** [UĐ]. Công suất thiết kế (373 MW) gấp khoảng 3 lần vận hành (100-148 MW), và hàng tỷ USD cam kết mới
   từ nhà đầu tư ngoại sau khi Luật Viễn thông bỏ trần sở hữu. Nhà vận hành trong nước sẽ cạnh tranh với vốn ngoại rẻ hơn ở phân khúc
   hyperscale/wholesale. Lợi thế còn lại của nhà vận hành trong nước: khách hàng chính phủ/ngân hàng (yêu cầu nội địa), quan hệ điện lực, và
   kết nối mạng sở hữu (phần vốn ngoại vẫn bị hạn chế).
3. **Điện là cổng hành chính quyết định biên.** Một biến số (giá sản xuất vs kinh doanh) đổi chi phí điện hơn 50%. Tại 21/09 phần lớn đã về giá
   sản xuất, nhưng TP.HCM, nơi tập trung dự án mới, vẫn áp giá kinh doanh. Văn bản sửa TT 60 chưa ký (tìm kiếm 01/11). Cùng lúc, nguy cơ
   thiếu điện 2027 làm **cấp điện mới cho TTDL lớn** trở thành ràng buộc lượng, không chỉ giá.
4. Biên điển hình [NỀN, chưa kiểm]: TTDL colocation trưởng thành EBITDA 40-55%, nhưng 2-3 năm đầu lấp đầy thấp, khấu hao lớn, lợi nhuận kế toán
   âm hoặc mỏng. Capex khoảng 8-12 triệu USD/MW IT load ở châu Á [NỀN]. Dự án AI mật độ cao đắt hơn.

## 3. Khối 3: Giáo dục tư nhân

### 3a. Quy định và học phí [DK]
| Chỉ tiêu | Số | Nguồn |
|---|---|---|
| **Miễn học phí phổ thông công lập** | NQ 217/2025/QH15 (26/06/2025), từ năm học 2025-2026: công lập **miễn**; dân lập/tư thục được **hỗ trợ** theo mức HĐND tỉnh, **không vượt học phí trường tư thu** | SGGP; lsvn 25/08/2026 |
| Mức hỗ trợ học sinh tư | Hà Nội: 155.000-217.000 đ/tháng (tối đa gần 2 triệu/năm, dự thảo 2025-2026); TP.HCM: tương đương học phí công lập cùng cấp (NQ 40-41/2025 HĐND); TP.HCM tiếp tục miễn công lập 2026-2027 | Tuổi Trẻ; daibieunhandan; baomoi |
| Khung học phí phổ thông (tham chiếu) | 2025-2026, nghìn đ/tháng: mầm non/tiểu học 50-540; THCS 50-650; THPT 100-650. Từ 2026-2027 đến 2035-2036 trần điều chỉnh **≤ 7,5%/năm** | lsvn 25/08/2026 (NĐ 238/2025) |
| NĐ 238/2025/NĐ-CP | ban hành 03/09/2025, thay NĐ 81/2021 và NĐ 97/2023 | thuvienphapluat; Tiền Phong |
| Học phí ĐH công lập chưa tự chủ 2026-2027 | **1,71-3,5 triệu đ/tháng** tuỳ nhóm ngành | thuvienphapluat (2026) |
| Dự thảo sửa NĐ 238 (08/2026) | giữ ổn định trường chưa tự chủ (trừ răng-hàm-mặt lên 3,5 triệu); **gộp 2 nhóm tự chủ, trần tối đa 2,5 lần** trường chưa tự chủ; người học chọn trường tư/chất lượng cao chỉ nhận mức hỗ trợ của Nhà nước, tự trả phần chênh. **Là dự thảo** | lsvn 24/08/2026 |
| Ví dụ lộ trình | một ĐH kinh tế công lập lớn tăng tối đa 10%/năm (chương trình chuẩn 20-28 triệu/năm); một học viện tăng không quá 15%/năm | Đại Đoàn Kết (2026) |
| Luật GDĐH 125/2025/QH15 | thông qua 10/12/2025, hiệu lực **01/01/2026**; mở rộng tự chủ (Điều 14); bỏ hội đồng trường ĐH công lập | thuvienphapluat; Nhân Dân |
| NQ 71-NQ/TW (22/08/2025) | chi NSNN cho GD-ĐT tối thiểu 20% tổng chi; theo một bài bình luận của hiệu trưởng trường tư: miễn tiền sử dụng đất, giảm tiền thuê đất cho cơ sở giáo dục trong nước, **không thu thuế TNDN với cơ sở công lập và tư thục không vì lợi nhuận** (chưa đối chiếu nguyên văn NQ). QĐ 1472/QĐ-TTg (03/08/2026) kế hoạch triển khai; năm học 2026-2027 là "năm đầu triển khai cụ thể" | daibieunhandan 15/09/2025; lsvn 2026 |
| Chỉ đạo 15/06/2026 | xã hội hoá **không được thành khoản đóng góp bắt buộc**; công khai thu chi; siết dạy thêm; nghiên cứu mô hình quản trị chung trường công/tư cùng địa bàn; chuyển trụ sở công dư thừa thành trường học | Tiền Phong 15/06/2026 |
| Tuyển sinh | Quy chế mới TT 06/2026/TT-BGDĐT (áp dụng 15/02/2026): **siết xét học bạ**, giảm nguyện vọng/phương thức, giảm lợi thế chứng chỉ ngoại ngữ; dự thảo tối đa 5 phương thức/trường | luatvietnam; huongnghiep.hocmai (2026) |
| Quy mô thí sinh | thi tốt nghiệp THPT 2026: 1.241.914 đăng ký, khoảng 1,2 triệu dự thi; **874.811 thí sinh đăng ký nguyện vọng** (2025: 849.544, **+3,0%**) | lsvn/daibieunhandan (07/2026) |
| Nhu cầu ngành CNTT/AI | ngành AI một ĐH công lập phía Nam 30/30 (2025: 29,6); > 53% thí sinh đăng ký nhóm STEM | VietnamPlus/hocmai (08/2026) |

### 3b. Nhân khẩu [DK]
- Tổng tỷ suất sinh **1,93** con/phụ nữ (2025), 1,91 (2024), 1,96 (2023), 2,1 (2021). Nhóm 0-14 tuổi **22,8%** (2025) từ 23,5% (2024). Tỷ suất sinh
  thô 13,7‰ (NSO, điều tra 01/04/2025).
- Mục tiêu GDĐH: > 3 triệu người học vào 2030 (khoảng 260 SV/vạn dân), từ khoảng 2,1 triệu (khoảng 230/vạn dân, chưa rõ năm) (SGGP, VOH).
- Tỷ lệ SV tư thục: **15,67%** năm học 2017-2018 (267.530/1.707.025); mục tiêu quy hoạch cũ 22,5% vào 2025, **không có số xác nhận 2025**.

### 3c. Đọc [UĐ]
1. **Phổ thông tư thục chịu một cú sốc hành chính một chiều.** Từ 2025-2026, khoảng cách giá giữa trường công (0 đồng) và trường tư rộng thêm
   đúng bằng học phí công lập cũ. Phần hỗ trợ học sinh trường tư ở Hà Nội tối đa khoảng 2 triệu/năm, nhỏ so với học phí trường tư tầm trung
   [NỀN: thường vài chục đến trăm triệu/năm]. Phân khúc bị ép là **trường tư giá thấp và trung bình**, nơi khách chủ yếu chọn vì thiếu chỗ ở
   trường công chứ không vì chất lượng. Phân khúc cao cấp/quốc tế ít bị ảnh hưởng. **Không có số** chuyển trường tư sang công 2025-2026.
2. Nhà nước đồng thời cam kết **xây đủ trường công** (chỉ đạo 15/06/2026, chuyển trụ sở dư thừa thành trường). Đó là cung công lập tăng, cạnh
   tranh thêm với phân khúc tư giá thấp ở đô thị đông dân [UĐ]. Nhân khẩu: TFR dưới mức thay thế, nhóm 0-14 giảm, nên **cầu tiểu học co dần
   từ cuối thập kỷ** [UĐ], trong khi THPT và ĐH vẫn được đỡ bởi các lứa sinh 2008-2010 [NỀN].
3. **Đại học tư có gió thuận hành chính về giá.** Trần học phí công lập tự chủ dự thảo lên tới 2,5 lần mức chưa tự chủ, và luật mới mở rộng
   tự chủ học phí. Khi trường công đắt lên, khoảng cách giá với ĐH tư hẹp lại [UĐ]. Cầu tổng: số thí sinh đăng ký +3,0% năm 2026, tỷ lệ đi
   học ĐH vẫn thấp so với khu vực, mục tiêu 3 triệu người học 2030. Rủi ro: (i) siết học bạ làm khó tuyển với trường tư dựa vào xét học bạ;
   (ii) trường công tự chủ mở rộng chỉ tiêu ngành "nóng" (CNTT, AI, bán dẫn); (iii) quy định "không vì lợi nhuận" có thể đi kèm điều kiện về
   chia cổ tức [NỀN, chưa kiểm Luật 125/2025].
4. **Đào tạo CNTT gặp nghịch lý AI.** Cầu đầu vào ngành AI/CNTT rất cao (điểm chuẩn 30/30), nhưng **cầu tuyển junior** ở outsourcing có thể
   giảm (mục 1d). Nếu sinh viên CNTT ra trường 2027-2029 khó xin việc, đó là rủi ro uy tín và tuyển sinh có độ trễ 2-4 năm cho trường gắn với
   ngành CNTT [UĐ]. Chưa có số tỷ lệ việc làm sau tốt nghiệp 2026.
5. Biên điển hình [NỀN, chưa kiểm]: giáo dục tư nhân EBITDA 25-40% khi lấp đầy cao; **học phí thu trước** làm CFO thường > LNST; capex khu học
   xá lớn và dài, thường gắn với đất.

## 4. Lãi suất, tỷ giá, tín dụng (chỉ phần liên quan)
| Tầng | Số as-of | Nguồn |
|---|---|---|
| Lãi huy động effective của team (max Big-4 12M và CCTG) | **7,4%** (12/10) | MACRO UPDATE 14/10 |
| Lãi cho vay BQ giao dịch mới | **9,12%** (30/09), +1,03pp YTD | sector read ngân hàng 31/10 |
| USD/VND niêm yết | Vietcombank 25.620-26.030 (mua-bán), BIDV 25.650-26.030, ngày 26/10/2026; tỷ giá trung tâm "đi ngang" | thitruongtaichinhtiente 26/10/2026 |
| USD/JPY | khoảng 157-159 (T10), 156,81 (26/10) | mục 1b |
| Fed | 3,75-4,00%, giữ 28/10 sau nâng 16/09 | mục 1c |

**Đọc [UĐ]:** khối 1 nhạy với **JPY và USD**, ít nhạy lãi vay VN (tài sản nhẹ). Khối 2 (TTDL, cáp quang) và khối 3 (khu học xá) nhạy với **lãi
vay VN** vì capex lớn: mặt bằng cho vay +1pp YTD làm tăng chi phí vốn của dự án TTDL mới đúng lúc cạnh tranh với vốn ngoại. Chênh lệch "lãi vay
VN 9,12% vs chi phí vốn USD của quỹ hạ tầng ngoại" là một lý do cấu trúc khiến nhà vận hành trong nước khó thắng phân khúc hyperscale [UĐ].
Không dùng bảng 5 tầng đầy đủ ở đây vì không khối nào phụ thuộc chủ yếu vào chi phí huy động; xem `sector_read_ngan_hang_20261031.md`.

## 5. Phân loại chế độ từng khối

### Khối 1a. Xuất khẩu dịch vụ phần mềm
| Nhãn | P | Lý do |
|---|---|---|
| **STRUCTURAL** (bất lợi) | **0,45** | AI làm giảm số người-tháng mỗi dự án (Cognizant), xói mòn giá khi tái ký (Kotak khoảng 3,5%), Gartner hạ dịch vụ trong khi nâng tổng chi IT. Mô hình kim tự tháp junior bị bẻ cong. Không đảo ngược khi chu kỳ hồi |
| **CYCLICAL** | **0,45** | Fed đang nâng lãi, DN Mỹ siết consulting; JPY yếu cắt DT quy đổi; bookings vẫn cao (Infosys, TCS, Accenture) nên một phần là trễ chuyển hoá. Cầu Nhật (Tankan +11%) và thiếu người METI là lực ngược chiều giảm phát |
| **ADMIN_GATED** | **0,10** | Ít cổng hành chính: thuế/ưu đãi DN phần mềm VN [NỀN], quy định thị thực/onsite ở thị trường đích [NỀN], luật dữ liệu ở thị trường khách |

- **Phân hoá [UĐ]:** mảng **Nhật** nghiêng CYCLICAL (tỷ giá + thiếu người, AI giảm phát chậm). Mảng **Mỹ/EU** nghiêng STRUCTURAL (khách nhanh áp AI,
  cạnh tranh giá Ấn Độ trực tiếp). DN có tỷ trọng Nhật cao sẽ chịu tỷ giá nhiều hơn giảm phát AI trong 2026-2027.
- **Confidence: `ambiguous` (~50/50 giữa STRUCTURAL và CYCLICAL).** Nhất quán với SECTOR READ 14/10 (nghiêng cấu trúc ở bội số ~55/45).

### Khối 1b. Chuyển đổi số nội địa
| Nhãn | P | Lý do |
|---|---|---|
| **ADMIN_GATED** | **0,60** | Cầu do NSNN quyết (NQ 57 tối thiểu 3%, 65.020 tỷ 2026), giải ngân 41% tại 26/10, chỉ thị CT 29 và TB 510; đề án dữ liệu dân cư QĐ 826; luật AI/dữ liệu/BVDLCN tạo cầu tuân thủ |
| **STRUCTURAL** (thuận) | **0,25** | Số hoá hành chính, ngân hàng, định danh điện tử là xu hướng nhiều năm |
| **CYCLICAL** | **0,15** | Cầu ngân hàng/DN tư nhân đi theo lợi nhuận ngân hàng và tín dụng |
- **Confidence: `clean` về nhãn trội (ADMIN_GATED), `ambiguous` về thời điểm chuyển hoá doanh thu.**

### Khối 2a. Băng rộng cố định
| Nhãn | P | Lý do |
|---|---|---|
| **STRUCTURAL** (bão hoà, độc quyền nhóm) | **0,55** | 87,6% hộ đã có cáp quang; tăng trưởng DT khoảng 2-3%/năm (GlobalData); tăng trưởng chỉ đến từ giá và nâng gói |
| **ADMIN_GATED** | **0,30** | 2 nhà mạng nhà nước dẫn giá; cấp phép (Starlink trần 600.000); cáp biển do nhà mạng lớn sở hữu |
| **CYCLICAL** | **0,15** | Ít nhạy chu kỳ; chi tiêu hộ có thể làm chậm nâng gói |
- **Confidence: `clean` (~70/30).**

### Khối 2b. Trung tâm dữ liệu/cloud
| Nhãn | P | Lý do |
|---|---|---|
| **ADMIN_GATED** | **0,45** | Giá điện (TT 60, giá sản xuất vs kinh doanh, TP.HCM chưa thống nhất), cấp điện mới (rủi ro thiếu điện 2027), mở cửa vốn ngoại, nội địa hoá dữ liệu |
| **STRUCTURAL** (thuận về cầu, bất lợi về cạnh tranh) | **0,40** | Cầu AI/cloud/nội địa hoá dài hạn; nhưng cung thiết kế gấp khoảng 3 lần vận hành và vốn ngoại rẻ hơn vào phân khúc hyperscale |
| **CYCLICAL** | **0,15** | Chu kỳ capex AI toàn cầu |
- **Confidence: `ambiguous` (~55/45).**

### Khối 3. Giáo dục tư nhân
| Nhãn | P | Lý do |
|---|---|---|
| **ADMIN_GATED** | **0,55** | Miễn học phí công lập (NQ 217/2025), khung trần ≤ 7,5%/năm, dự thảo trần ĐH tự chủ 2,5 lần, luật GDĐH 2025, quy chế tuyển sinh siết học bạ, NQ 71 (đất, thuế cho không vì lợi nhuận), chỉ đạo chống thu bắt buộc |
| **STRUCTURAL** | **0,35** | TFR 1,93 dưới thay thế, 0-14 tuổi giảm (bất lợi phổ thông dài hạn); tỷ lệ đi học ĐH còn thấp, mục tiêu 3 triệu (thuận ĐH); nghịch lý AI với đào tạo CNTT |
| **CYCLICAL** | **0,10** | Thu nhập hộ; ít nhạy |
- **Phân hoá [UĐ]:** **phổ thông tư giá thấp-trung** = ADMIN_GATED bất lợi. **ĐH tư** = ADMIN_GATED thuận về giá, STRUCTURAL thuận về quy mô,
  rủi ro ở quy chế tuyển sinh và việc làm ngành CNTT. **Phổ thông cao cấp/quốc tế** = ít bị ảnh hưởng.
- **Confidence: `ambiguous` (~60/40).**

### Tổng hợp cho DN đa ngành [UĐ]
- Ba khối có **ba đồng hồ khác nhau**: khối 1 theo peer toàn cầu và JPY (quý); khối 2 theo văn bản điện và capex (năm); khối 3 theo năm học và
  văn bản học phí (năm). Một DN đa ngành có thể có khối 2-3 ổn định đỡ khối 1 khi khối 1 bị giảm phát AI, nhưng khối 2 (TTDL) cần vốn lớn đúng
  lúc khối 1 tạo ít tiền hơn.
- **Liên hệ nền vĩ mô:** REGIME READ #2 / MACRO UPDATE giữ Loại-1 STRUCTURAL_ACCUMULATION BĐS, ambiguous. Nhóm này ít phơi nhiễm trực tiếp với BĐS,
  trừ phần đất khu học xá/TTDL và tín dụng. Nhân tố nước ngoài (khối ngoại bán nhóm CNTT, FTSE 21/09) đã đọc ở SECTOR READ 14/10.

## 6. FORECAST KHOÁ TRƯỚC (lập 2026-11-01; chấm bằng nguồn công bố đầu tiên ≤ ngày chấm; không có nguồn ⇒ ghi "không chấm được", không suy)

| # | Mệnh đề | P | Ngày chấm | Nguồn chấm |
|---|---|---|---|---|
| F1 | Bản dự báo chi IT kế tiếp của Gartner: **IT services 2027 tăng ≤ 5,5%** (bản 21/10: 4,9%) | 0,80 | 2027-03-15 | Gartner newsroom |
| F2 | Cùng bản F1: **tổng chi IT toàn cầu 2027 tăng ≥ 10%** (bản 21/10: 15%) | 0,85 | 2027-03-15 | Gartner newsroom |
| F3 | Infosys: **tăng trưởng DT cc thực tế FY27 (kết thúc 31/03/2027) ≤ 2,5%** (guidance 1-2%) | 0,85 | 2027-04-30 | Infosys KQ Q4 FY27 |
| F4 | Accenture KQ Q1 FY27: **đáy guidance FY27 giữ ≥ 3% LC** (không hạ đáy dưới 3%) | 0,70 | 2026-12-31 | Accenture 8-K/newsroom |
| F5 | BOJ Tankan T12/2026: kế hoạch FY2026 "software, R&D, fixed investment excl. land", **DN lớn mọi ngành ≥ +9,0% YoY** (T9: 11,0%) | 0,75 | 2026-12-20 | boj.or.jp |
| F6 | **USD/JPY ngày 2027-03-31 ≥ 148** (giá đóng cửa/fixing công bố) | 0,70 | 2027-04-02 | Fed H.10 hoặc BOJ |
| F7 | Fed: **cận trên lãi suất mục tiêu ngày 2027-03-31 ≥ 4,00%** | 0,60 | 2027-03-31 | federalreserve.gov |
| F8 | Tỷ lệ giải ngân kinh phí KHCN-ĐMST-CĐS **năm ngân sách 2026** (số công bố gần nhất sau 31/12/2026, cùng phạm vi 52.680 tỷ) **< 80%** | 0,70 | 2027-02-28 | Bộ KH&CN / Bộ TC / báo dẫn. Phạm vi khác ⇒ không chấm được |
| F9 | Quốc hội phê chuẩn **chi KHCN-ĐMST-CĐS dự toán 2027 ≥ 65.020 tỷ** (cùng phạm vi số 2026 VnEconomy) | 0,80 | 2026-12-15 | Nghị quyết dự toán NSNN 2027 |
| F10 | Bộ Công Thương **ký ban hành** thông tư sửa đổi TT 60/2025 có quy định riêng giá điện TTDL | 0,55 | 2027-06-30 | moit.gov.vn / Công báo |
| F11 | **Không có** nhà mạng nào trong 3 nhà mạng FTTH lớn hạ giá niêm yết gói thấp nhất (ngoại thành) xuống **dưới 180.000 đ/tháng** | 0,85 | 2027-06-30 | biểu giá công bố / báo chí |
| F12 | Bộ KH&CN (hoặc báo dẫn Bộ) công bố công suất thiết kế TTDL cả nước **≥ 450 MW** (05/2026: khoảng 373 MW) | 0,50 | 2027-06-30 | Bộ KH&CN |
| F13 | Nghị định sửa NĐ 238/2025 được ký, có **trần học phí ĐH công lập tự chủ ≤ 2,5 lần** trường chưa tự chủ | 0,55 | 2027-03-31 | Chính phủ / Công báo |
| F14 | Tuyển sinh 2027: **số thí sinh đăng ký nguyện vọng ≥ 874.811** (2026) | 0,65 | 2027-07-31 | Bộ GD&ĐT |
| F15 | Năm học 2027-2028: **miễn học phí phổ thông công lập vẫn áp dụng** (NQ 217/2025 không bị bãi bỏ/hoãn) | 0,93 | 2027-09-30 | Quốc hội / Bộ GD&ĐT |

Lý do chính: F1-F3 dựa trên chuỗi hạ dự báo dịch vụ và guidance Infosys thấp. F4: Accenture vừa ra guidance 3-6% ngày 25/09; hạ đáy ngay quý sau
là hiếm [NỀN]. F5: kế hoạch DN lớn T12 thường không giảm mạnh so với T9 [NỀN]. F6-F7: BOJ nghiêng nâng, Fed nghiêng nâng; JPY về dưới 148 cần
BOJ nâng nhanh và Fed đảo chiều cùng lúc. F8: 41% tại 26/10. F9: NQ 57 yêu cầu tối thiểu 3% và tổng chi NSNN tăng. F10 là đồng xu: dự thảo đã
lấy ý kiến từ 06/2026 mà chưa ký, nhưng áp lực từ Bộ KH&CN lặp lại 3 lần. F11: vừa tăng giá đồng loạt T3/2026. F12: phụ thuộc thời điểm công
bố. F13: dự thảo 08/2026, thường mất 3-9 tháng. F14: tỷ lệ đi học tăng, lứa sinh 2009 không nhỏ hơn đáng kể lứa 2008 [NỀN]. F15: chính sách
vừa ban hành, có ngân sách.

## 7. Chỉ báo dẫn dắt (theo dõi tháng/quý)
1. KQ quý và guidance của Accenture (T12, T3), TCS/Infosys/HCLTech (T1, T4), Cognizant/EPAM (T2); bình luận về giá và "unit consumption".
2. Gartner IT spending (T1-T2, T4, T7, T10): dòng IT services.
3. BOJ Tankan (T12, T3/T4), USD/JPY, quyết định BOJ (T12) và Fed (09/12).
4. Bộ KH&CN: giải ngân KHCN-ĐMST-CĐS hằng tháng; dự toán 2027 (Quốc hội T11-T12); văn bản hướng dẫn Luật AI, Luật Dữ liệu, BVDLCN.
5. TT 60/2025: thông tư sửa đổi; áp giá của EVN HCMC; kế hoạch cấp điện cho TTDL lớn; giá điện bán lẻ bình quân.
6. Bộ KH&CN: thuê bao FTTH, DT viễn thông, công suất TTDL; biểu giá FTTH; sự cố/sửa chữa cáp biển; các tuyến cáp mới.
7. Giáo dục: nghị định sửa NĐ 238; nghị quyết HĐND về hỗ trợ học phí học sinh tư; quy chế tuyển sinh 2027; số nhập học ĐH 2026 (Bộ GD&ĐT);
   số liệu việc làm sinh viên CNTT.

## 8. DD cần kiểm gì (DN đa ngành CNTT xuất khẩu + viễn thông/TTDL + giáo dục bất kỳ ở VN; số từ BCTC, BCTN, thuyết minh, tài liệu IR)

**A. Xuất khẩu dịch vụ phần mềm và chuyển đổi số**
1. **Cách đọc "doanh thu ký mới":** định nghĩa của DN là TCV (toàn hợp đồng nhiều năm) hay ACV (giá trị năm)? Gồm gia hạn hay chỉ mới? Có gồm hợp
   đồng khung không cam kết khối lượng? Không có định nghĩa ⇒ không so được với peer. Tính **ký mới / doanh thu cùng kỳ (book-to-bill)** theo
   thị trường 4-8 quý. Book-to-bill < 1,0 hai quý liền ở một thị trường là cờ vàng. Ký mới tăng > 20% mà DT tăng < 10% kéo dài 3-4 quý: hoặc hợp
   đồng dài hạn hơn (TCV phồng), hoặc chuyển hoá chậm. Hỏi **thời hạn bình quân** hợp đồng ký mới.
2. **Backlog (DT chưa thực hiện):** có công bố không; tỷ lệ backlog chuyển thành DT trong 12 tháng tới; backlog / DT 12 tháng qua. Phân phối quy mô
   hợp đồng (số HĐ > 5 triệu, > 10 triệu USD) và tỷ trọng top 10/top 20 khách hàng.
3. **Utilization:** giờ tính phí / tổng giờ có sẵn của nhân sự giao hàng (loại trừ người mới đào tạo). Mức điển hình ngành 75-85% [NỀN]. Tăng
   mạnh khi tuyển dụng chững = tối ưu ngắn hạn; giảm kèm headcount tăng = bench phình (chi phí trước DT).
4. **Doanh thu / kỹ sư (FTE giao hàng), theo thị trường và theo ĐỒNG TIỀN GỐC** (JPY cho Nhật, USD cho Mỹ). Giảm trong khi headcount tăng = dấu hiệu
   giảm phát giá hoặc dịch xuống phân khúc rẻ. So **tăng trưởng headcount vs tăng trưởng DT cc**: DT tăng nhanh hơn headcount có thể là AI năng
   suất (tốt nếu giữ được giá) hoặc thầu phụ (kiểm chi phí thuê ngoài).
5. **Tăng trưởng theo tỷ giá cố định:** DT Nhật tính bằng JPY tăng bao nhiêu? Chênh giữa tăng trưởng VND và cc = phần tỷ giá. Chính sách phòng
   ngừa tỷ giá, lãi/lỗ tỷ giá thực hiện/chưa thực hiện.
6. **Cơ cấu hợp đồng:** T&M vs fixed-price/managed services vs outcome-based. Tỷ trọng DT "AI" và định nghĩa (dịch vụ AI bán thêm hay dự án cũ đổi
   tên). Có hợp đồng nào chủ động giảm giá/khối lượng khi tái ký vì AI không (thuyết minh, Q&A ĐHCĐ).
7. **Onsite vs offshore** theo thị trường; chi phí nhân sự onsite (Nhật, Mỹ) / DT; thị thực.
8. **Biên gộp và biên EBIT theo khối** 8-12 quý. Tham chiếu peer [DK]: biên EBIT/hoạt động guidance HCLTech 17,5-18,5%, Infosys 20-22%, Cognizant
   điều chỉnh khoảng 16,1%, EPAM non-GAAP 15,5-16,5%. Biên DN VN cao hơn peer Ấn Độ đáng kể thì hỏi vì sao (chi phí phân bổ, ưu đãi thuế).
9. **Nội địa:** tỷ trọng phần cứng/bản quyền pass-through trong DT chuyển đổi số; biên gộp tách phần dịch vụ; **phải thu khu vực công theo tuổi nợ**
   (> 180 ngày, > 365 ngày), dự phòng; **tài sản hợp đồng / DT chưa lập hoá đơn** tăng nhanh hơn DT > 10pp hai quý liền = cờ vàng (DT ghi nhận theo
   tiến độ chưa nghiệm thu).
10. **DSO** toàn khối; DSO > 90 ngày ở xuất khẩu hoặc > 150 ngày ở nội địa là cờ vàng [NỀN về ngưỡng].
11. **Tăng trưởng hữu cơ vs M&A:** DT/LN từ công ty mua mới; lợi thế thương mại và kiểm tra suy giảm; giá mua / DT.
12. Ưu đãi thuế TNDN phần mềm: thời hạn còn lại, thuế suất thực tế, rủi ro hết ưu đãi.

**B. Băng rộng cố định**
13. **Thuê bao thuần tăng (net adds)** theo quý và theo vùng; churn tháng.
14. **ARPU thực** (DT băng rộng / thuê bao bình quân) so với giá niêm yết; mức tăng ARPU 2026 so với mức tăng giá gói thấp nhất (+5,6% đến +8,3%).
    ARPU tăng ít hơn mức tăng giá = khuyến mãi/bán kèm ăn mất; ARPU tăng nhiều hơn = nâng gói thật.
15. Tỷ trọng DT từ gói kèm (truyền hình, camera, dịch vụ gia đình); DT doanh nghiệp (kênh thuê riêng) vs hộ.
16. **Capex / DT** và cơ cấu capex (XGS-PON, mở rộng tuyến, thiết bị đầu cuối cấp miễn phí). Thiết bị đầu cuối cấp miễn phí hạch toán thế nào
    (capex khấu hao hay chi phí). Giá bộ nhớ tăng làm chi phí đầu cuối tăng.
17. EBITDA margin khối viễn thông; khấu hao/DT; chi phí thuê kênh quốc tế và tác động sự cố cáp biển; quyền sử dụng cáp biển sở hữu/thuê.

**C. Trung tâm dữ liệu/cloud**
18. **MW IT load đã xây / MW đã bán (ký) / MW đang dùng**; tỷ lệ lấp đầy theo từng TTDL và tuổi TTDL. Lấp đầy < 60% sau 24 tháng vận hành là cờ vàng
    [NỀN]. Số rack, DT/rack/tháng, DT/MW.
19. Hợp đồng: thời hạn, take-or-pay hay theo sử dụng, khách hàng lớn nhất / DT TTDL, khách hyperscale/GPU, điều khoản chuyển giá điện cho khách.
20. **Giá điện áp cho từng TTDL** (sản xuất hay kinh doanh), theo địa bàn; chi phí điện / DT TTDL trước và sau 12/2025; PUE; công suất điện được
    cấp vs công suất thiết kế; cam kết cấp điện cho giai đoạn mở rộng.
21. **Capex/MW** và nguồn vốn (vay VND, vay ngoại tệ, đối tác); lãi vay vốn hoá; thời điểm bắt đầu khấu hao; IRR/thời gian hoàn vốn giả định.
22. Cloud: DT cloud tách khỏi colocation; tỷ trọng bán lại cloud nước ngoài (biên thấp) vs cloud tự xây; khách chính phủ/ngân hàng.
23. Cấp phép: giấy phép dịch vụ TTDL/cloud, đất, PCCC, đánh giá an ninh mạng; đối tác nước ngoài và cấu trúc sở hữu (có kèm kết nối mạng không).

**D. Giáo dục tư nhân**
24. **Số học sinh/sinh viên** theo cấp và theo cơ sở; **nhập học mới / chỉ tiêu (tỷ lệ lấp đầy)**; số tốt nghiệp; tỷ lệ bỏ học. Năm học 2025-2026
    và 2026-2027 so với 2024-2025 ở phổ thông (tác động miễn học phí công lập).
25. **Học phí bình quân/người học** và tăng trưởng; tỷ trọng học bổng/miễn giảm (giảm trừ DT hay chi phí); so với trần 2,5 lần (nếu ban hành).
26. **Doanh thu chưa thực hiện (học phí thu trước)** và biến động theo mùa; tỷ lệ hoàn học phí. Học phí thu trước giảm cùng kỳ là chỉ báo tuyển sinh
    sớm nhất.
27. Tình trạng **vì lợi nhuận / không vì lợi nhuận** của từng pháp nhân giáo dục; giới hạn chia lợi nhuận về công ty mẹ; thuế TNDN thực tế; ưu đãi
    đất (NQ 71).
28. Đất và capex: khu học xá sở hữu/thuê, thời hạn thuê, tiền thuê đất; capex/học sinh; tỷ lệ sử dụng cơ sở vật chất.
29. Kiểm định chất lượng, tỷ lệ giảng viên/sinh viên, ngành mới mở; **tỷ lệ có việc làm sau tốt nghiệp ngành CNTT** (theo năm tốt nghiệp).
30. Phụ thuộc phương thức tuyển sinh: tỷ trọng nhập học qua học bạ (bị siết từ TT 06/2026).

**E. Cấp tập đoàn**
31. **CFO / LNST theo khối và hợp nhất**, 4-8 quý, và lũy kế 3 năm. Kỳ vọng [NỀN/UĐ]: dịch vụ phần mềm 0,8-1,0; viễn thông > 1,3 (khấu hao lớn);
    giáo dục > 1,1 (thu trước). Hợp nhất < 0,8 ba năm liền = cờ đỏ (LN không thành tiền: tài sản hợp đồng, phải thu công).
32. **FCF = CFO − capex** theo khối; khối nào tạo tiền, khối nào tiêu tiền; capex TTDL tài trợ bằng tiền của khối phần mềm hay bằng nợ.
33. Báo cáo bộ phận: định nghĩa khối có đổi qua các năm không; phân bổ chi phí chung; giao dịch nội bộ (khối giáo dục mua dịch vụ IT nội bộ,
    TTDL cho khối phần mềm thuê).
34. Lợi ích cổ đông không kiểm soát theo khối (LN thuộc cổ đông mẹ ở khối nào thấp hơn); cổ tức từ công ty con lên mẹ.
35. Pha loãng: cổ tức cổ phiếu, ESOP (chi phí ESOP có ghi nhận không), phát hành riêng lẻ; ý kiến kiểm toán; chênh LN trước/sau kiểm toán.
36. Kiểm tra chéo bằng số ngành: tăng trưởng DT xuất khẩu của DN so với peer (1-5% cc ở peer lớn); nếu DN tăng gấp nhiều lần peer thì nguồn tăng là
    gì (M&A, một vài HĐ lớn, thị trường Nhật, tỷ giá).

## 9. Điều gì làm tôi sai
- **Khối 1 tốt hơn tôi nghĩ:** peer lớn nâng guidance liên tiếp ở các quý tới (Accenture nâng đáy, Infosys thôi hạ); Gartner nâng lại IT services;
  JPY mạnh lên nhanh (BOJ nâng T12, Fed đảo chiều); bằng chứng DN thuê ngoài **giữ được giá** nhờ AI (DT/kỹ sư tăng).
- **Khối 1 xấu hơn:** Accenture hạ đáy dưới 3%; TCS/HCL quay sang âm cc; dấu hiệu khách Nhật cũng đòi giảm người-tháng vì AI; Fed nâng tiếp nhiều lần.
- **Khối 2:** sửa TT 60 theo hướng giá kinh doanh cho mọi TTDL dịch vụ (xấu); thiếu điện thật năm 2027 làm hoãn dự án (xấu cho cung mới, có thể tốt
  cho TTDL đang chạy); một nhà mạng nhà nước đánh giá FTTH (xấu).
- **Khối 3:** Nhà nước mở rộng hỗ trợ học phí học sinh tư lên ngang chi phí thật (tốt); dừng hoặc hạn chế tự chủ học phí ĐH công (trung tính với ĐH
  tư); quy định không vì lợi nhuận siết chia cổ tức (xấu).
- **Lỗi dữ liệu có thể có:** Gartner các bản trước (8,7%, 9,0%, 5,3%) chỉ qua nguồn thứ cấp; kết quả Fed 28/10 chỉ một nguồn; kết quả BOJ 30/10 không tìm
  được; số FTTH 25 triệu và thị phần từ nguồn độ tin cậy thấp và mâu thuẫn; kinh phí KHCN 2026 có 2 số khác phạm vi (65.020 vs 95.000 tỷ); số xuất
  khẩu phần mềm VN chỉ có tới 2023; NQ 71 về thuế/đất đọc qua bài bình luận; ngày hiệu lực các luật dữ liệu/BVDLCN/CNCNS là [NỀN].

## Nguồn (ngày công bố)
- Gartner, "Worldwide IT Spending to Grow 15% in 2027, Totaling $7.35 Trillion" — 21/10/2026: https://www.gartner.com/en/newsroom/press-releases/2026-10-21-gartner-forecasts-worldwide-it-spending-to-grow-15-percent-in-2027-totaling-7-point-35-trillion
- Gartner, bản 22/04/2026 và 27/07/2026: https://gartner.com/en/newsroom/press-releases/2026-04-22-gartner-forecasts-worldwide-it-spending-to-grow-13-point-5-percent-in-2026-totaling-6-point-31-trillion-dollars ; https://www.gartner.com/en/newsroom/press-releases/2026-07-27-gartner-forecasts-worldwide-it-spending-to-grow-14-point-2-percent-in-2026-totaling-6-point-37-trillion
- softwarestrategiesblog (phân tích thứ cấp số Gartner) — 19/10/2026: https://softwarestrategiesblog.com/2026/10/19/
- Infosys Q2 FY27 (Morung Express; Free Press Journal) — 23/10/2026: https://morungexpress.com/infosys-posts-flat-pat-at-rs-7823-crore-trims-fy27-revenue-growth-guidance ; https://www.freepressjournal.in/business/infosys-q2-fy27-results-net-profit-rises-62-to-7823-crore-revenue-jumps-107-to-49244-crore
- TCS Q2 FY27 (Free Press Journal; IIFL) — 10/2026: https://www.freepressjournal.in/business/tcs-net-profit-up-025-to-13884-crore-in-q2-fy27-revenue-rises-to-73188-crore ; https://www.indiainfoline.com/news/companies/tcs-share-price-jumps-5-46-after-q2-fy27-results-net-profit-rises-4-qoq-to-13884-crore
- HCLTech Q2 FY27 investor release — 12/10/2026: https://www.hcltech.com/sites/default/files/document/open/quarter-results/2026-10/hcltech-Q2-fy27-Investor-release.pdf
- Cognizant 8-K Q3/2026 — 29/10/2026: https://www.sec.gov/Archives/edgar/data/0001058290/000105829026000039/exhibit9919302026.htm
- MarketBeat, Cognizant 2026 outlook/AI deal shifts — 09/03/2026: https://www.marketbeat.com/instant-alerts/cognizant-maps-2026-growth-4-65-outlook-ai-deal-shifts-and-margin-levers-in-focus-2026-03-09/
- Accenture Q4 FY26 8-K / newsroom — 09/2026: https://www.sec.gov/Archives/edgar/data/0001467373/000146737326000037/q4fy26earnings8-kexhibit.htm ; https://newsroom.accenture.com/content/4q-full-fy26-earnings/accenture-reports-fourth-quarter-and-full-year-fiscal-2026-results.pdf
- EPAM 8-K Q2/2026 — 06/08/2026: https://www.sec.gov/Archives/edgar/data/0001352010/000135201026000043/exhibit99_q2x2026.htm
- Tribune India / NewKerala, Kotak "AI deflation" (tóm tắt): https://www.tribuneindia.com/news/business/it-services-growth-to-stay-range-bound-at-3-per-cent-as-ai-deflation-pressures-margins-mid-tiers-better-placed-says-kotak/ ; https://www.newkerala.com/news/a/it-services-growth-stay-range-bound-per-cent-as-890.htm
- Accelerance, 2026 outsourcing rate trends: https://www.accelerance.com/blog/2026-outsourcing-rate-trends-asia-europe-latam
- Brilworks, software outsourcing trends 2026: https://www.brilworks.com/blog/software-outsourcing-trends-in-2026/
- BOJ Tankan T9/2026 — 01/10/2026: https://www.boj.or.jp/en/statistics/tk/yoshi/tk2609.htm
- roboforex USD/JPY — 26/10/2026: https://roboforex.com/ph/beginners/analytics/forex-forecast/currencies/usd-jpy-forecast-2026-10-26/
- tmgm / mitrade, BOJ trước họp T10 — 13-14/10/2026: https://www.tmgm.com/es/analysis/market-news/article/yen-trails-the-majors-as-the-boj-is-said-to-lean-against-a-hike-202610132241 ; https://www.mitrade.com/insights/news/live-news/article-1-2160426-20261014
- Nation Thailand, BOJ nâng 1,25% ngày 18/09: https://www.nationthailand.com/news/world/40071184
- Admiral Markets, FOMC T10/2026: https://admiralmarkets.com/analytics/traders-blog/fomc-october-2026-fed-holds-rates
- VietnamNet EN, kỹ sư VN cho Nhật / Japan ICT Day 2026: https://vietnamnet.vn/en/vietnam-s-software-engineers-power-japan-s-digital-backbone-2488048.html ; https://vietnamnet.vn/en/cmc-partners-with-ntt-data-to-expand-high-quality-it-talent-for-japan-2486261.html
- MIC EN, VN đối tác thứ 2 của Nhật về thuê ngoài phần mềm: https://english.mic.gov.vn/vn-second-largest-partner-of-japan-in-software-outsourcing-197136646.htm
- ITviec Market Insights Q1/2026: https://marketing.itviec.com/insightreport ; CareerLink dẫn TopDev: https://www.careerlink.vn/cam-nang-viec-lam/?p=20378
- Báo Pháp Luật, công nghiệp công nghệ số 9T +32,1% — 30/09/2026: https://baophapluat.vn/cong-nghiep-cong-nghe-so-tang-32-1-sau-9-thang.html
- VnEconomy, diện mạo công nghiệp công nghệ số đến 2030: https://vneconomy.vn/dien-mao-nganh-cong-nghiep-cong-nghe-so-den-nam-2030.htm
- VnEconomy, 1.500 DN công nghệ số ra nước ngoài (số 2023) — 13/05/2024: https://vneconomy.vn/hon-1-500-doanh-nghiep-cong-nghe-so-viet-nam-ra-nuoc-ngoai-mang-ve-7-5-ty-usd.htm
- Báo Pháp Luật, giải ngân 41,18% kinh phí KHCN — 27/10/2026: https://doanhnhan.baophapluat.vn/giai-ngan-41-18-kinh-phi-khoa-hoc-cong-nghe-ap-luc-tang-toc-cuoi-nam.html
- VnEconomy, ba đầu tàu công bố chi KHCN 2026; ưu tiên chi công nghệ chiến lược: https://vneconomy.vn/ba-dau-tau-kinh-te-cong-bo-chi-ngan-sach-cho-khoa-hoc-cong-nghe-trong-nam-2026.htm ; https://vneconomy.vn/uu-tien-nguon-luc-tang-ti-trong-chi-phat-trien-cong-nghe-chien-luoc-cong-nghe-loi.htm
- VCCI, tháo gỡ giải ngân NQ 57 — 25/06/2026: https://vcci.com.vn/tin-tuc/thao-go-diem-nghen-giai-ngan-khoi-thong-nguon-luc-hien-thuc-hoa-nghi-quyet-57-nq-tw
- SBV, QĐ 826/QĐ-TTg và kế hoạch ngành ngân hàng: https://sbv.gov.vn/en/w/nga%CC%80nh-ng%C3%A2n-ha%CC%80ng-tri%E1%BB%83n-khai-quy%E1%BA%BFt-%C4%91%E1%BB%8Bnh-s%E1%BB%91-826/q%C4%91-ttg-c%E1%BB%A7a-th%E1%BB%A7-t%C6%B0%E1%BB%9Bng-ch%C3%ADnh-ph%E1%BB%A7-ph%C3%AA-duy%E1%BB%87t-ch%C6%B0%C6%A1ng-tr%C3%ACnh-%C4%91%E1%BB%81-%C3%A1n-06
- Vietstock EN, khảo sát Finastra — 02/2026: https://en.vietstock.vn/2026/02/finastra-research-viet-nams-financial-sector-accelerates-ai-adoption-but-security-and-legacy-systems-remain-barriers-37-629294.htm
- VnEconomy, Luật AI hiệu lực 01/03/2026; luatvietan, NĐ 142/2026: https://vneconomy.vn/luat-tri-tue-nhan-tao-se-co-hieu-luc-tu-ngay-132026.htm ; https://luatvietan.vn/nghi-dinh-142-2026-nd-cp-huong-dan-luat-tri-tue-nhan-tao.html
- Phong Vũ, giá cước cáp quang tăng đồng loạt — 06/03/2026: https://phongvu.vn/cong-nghe/gia-cuoc-internet-cap-quang-viet-nam-tang/
- TelecomLead, FTTH VN 2026 (độ tin cậy thấp): https://telecomlead.com/broadband/best-isp-in-vietnam-2026-viettel-leads-ftth-market-with-11-million-subscribers-and-1-gbps-rollout-126543
- VnEconomy, 5G 27,2 triệu thuê bao: https://vneconomy.vn/viet-nam-da-co-272-trieu-thue-bao-5g.htm
- VOV / VTC, 4 tuyến cáp biển sự cố — 27-28/08/2026: https://vov.vn/xa-hoi/bon-tuyen-cap-quang-bien-ket-noi-internet-viet-nam-di-quoc-te-cung-gap-su-co-post1328173.vov ; https://vtcnews.vn/bon-tuyen-cap-quang-bien-ket-noi-internet-viet-nam-di-quoc-te-cung-gap-su-co-ar1036887.html
- VietnamPlus, nhà mạng ứng phó sự cố cáp biển: https://www.vietnamplus.vn/nha-mang-ung-pho-ra-sao-khi-hang-loat-tuyen-cap-quang-bien-dang-gap-su-co-post1133115.vnp
- VietnamNews, "Data centre boom courted, but power must keep pace" — 12/09/2026: https://vietnamnews.vn/economy/1799380/data-centre-boom-courted-but-power-must-keep-pace.html
- technode, BMI về TTDL VN — 20/07/2026: https://technode.global/2026/07/20/vietnam-emerges-as-seas-next-data-center-contender-amid-regional-capacity-shift-bmi/
- Tuổi Trẻ News, TTDL VN tăng công suất — 27/03/2026: https://news.tuoitre.vn/vietnam-eyes-data-center-investment-boom-as-capacity-ramps-up-103260327173940053.htm
- VietnamNet EN, khởi công TTDL > 100 MW (04/2025): https://vietnamnet.vn/en/vietnam-breaks-ground-on-first-data-center-exceeding-100mw-2394651.html
- lsvn, lưu ý đầu tư TTDL tại VN: https://lsvn.vn/can-luu-y-gi-khi-dau-tu-vao-linh-vuc-trung-tam-du-lieu-tai-viet-nam-a169345.html
- KTSG Online / Tuổi Trẻ, BCT yêu cầu EVN rà soát giá điện TTDL — 18/02/2026: https://tuoitre.vn/saigontimes/bo-cong-thuong-yeu-cau-evn-ra-soat-gia-dien-cho-trung-tam-du-lieu/
- VCCI, loạt "ông lớn" công nghệ kiến nghị giá điện: https://www.vcci.com.vn/tin-tuc/loat-ong-lon-cong-nghe-kien-nghi-xem-xet-lai-cach-ap-gia-dien
- Bộ Công Thương, dự thảo sửa TT 60/2025 (lấy ý kiến 26/05-06/06/2026): https://moit.gov.vn/du-thao-van-ban/lay-y-kien-ve-du-thao-thong-tu-sua-doi-bo-sung-mot-so-dieu-cua-thong-tu-so-60-2025-tt-bct-ngay-02-12-2025-cua-bo-truong-.html
- VietnamNet EN, Bộ KH&CN đề nghị thống nhất giá điện TTDL — 21/09/2026: https://vietnamnet.vn/en/vietnam-tech-ministry-presses-for-uniform-data-center-power-rates-2557367.html
- lsvn, học phí mầm non/phổ thông 2026-2027 — 25/08/2026: https://lsvn.vn/quy-dinh-ve-hoc-phi-doi-voi-giao-duc-mam-non-pho-thong-nam-hoc-2026-2027-a177323.html
- lsvn, Bộ GD&ĐT đề xuất học phí ĐH (dự thảo) — 24/08/2026: https://lsvn.vn/bo-gd-dt-de-xuat-muc-hoc-phi-dai-hoc-a177479.html
- SGGP, học sinh công lập miễn học phí từ 2025-2026: https://www.sggp.org.vn/hoc-sinh-cong-lap-toan-quoc-duoc-mien-hoc-phi-tu-nam-hoc-2025-2026-post801236.html
- daibieunhandan, TP.HCM hướng dẫn miễn/hỗ trợ học phí 2025-2026: https://daibieunhandan.vn/tp-ho-chi-minh-huong-dan-mien-giam-ho-tro-hoc-phi-tu-nam-hoc-2025-2026-10395922.html
- Tuổi Trẻ PLO, Hà Nội hỗ trợ học phí học sinh trường tư: https://tuoitre.vn/plo/ho-tro-hoc-phi-tag46662.html
- thuvienphapluat, trần học phí ĐH công lập: https://thuvienphapluat.vn/phap-luat/muc-tran-hoc-phi-doi-voi-co-so-giao-duc-dai-hoc-cong-lap-tu-bao-dam-chi-thuong-xuyen-duoc-xac-dinh--932464-235364.html
- Đại Đoàn Kết, học phí ĐH tăng theo lộ trình: https://daidoanket.vn/hoc-phi-dai-hoc-se-tiep-tuc-tang-theo-lo-trinh.html
- thuvienphapluat, Luật GDĐH 125/2025/QH15 hiệu lực: https://thuvienphapluat.vn/hoi-dap-phap-luat/luat-giao-duc-dai-hoc-2025-luat-so-1252025qh15-co-hieu-luc-khi-nao-138075598.html
- Nhân Dân, mở rộng tự chủ ĐH từ 01/01/2026: https://nhandan.vn/post-934475.html
- daibieunhandan, "Nghị quyết 71: đường băng mới cho giáo dục tư thục" — 15/09/2025: https://daibieunhandan.vn/nghi-quyet-71-duong-bang-moi-cho-giao-duc-tu-thuc-10386646.html
- Tiền Phong, chỉ đạo chuẩn bị năm học 2026-2027 — 15/06/2026: https://tienphong.vn/tong-bi-thu-chu-tich-nuoc-to-lam-khong-de-xa-hoi-hoa-giao-duc-tro-thanh-khoan-dong-gop-bat-buoc-post1851548.tpo
- lsvn, năm học 2026-2027 / NQ 71: https://lsvn.vn/nam-hoc-2026-2027-phai-la-nam-hoc-moi-ve-tu-duy-cach-lam-va-chat-luong-a178310.html
- luatvietnam, 8 thay đổi quy chế tuyển sinh 2026 (TT 06/2026): https://luatvietnam.vn/linh-vuc-khac/thay-doi-trong-quy-che-tuyen-sinh-dai-hoc-2026-883-106928-article.html
- daibieunhandan, mốc tuyển sinh ĐH 2026 (số thí sinh): https://daibieunhandan.vn/tuyen-sinh-dai-hoc-2026-moc-thoi-gian-then-chot-thi-sinh-khong-duoc-bo-lo-10415772.html
- VietnamPlus, top 15 ngành điểm chuẩn cao nhất 2026: https://www.vietnamplus.vn/tuyen-sinh-dai-hoc-2026-top-15-nganh-hoc-co-diem-chuan-cao-nhat-post1129209.vnp
- NSO, tình hình dân số 2025: https://www.nso.gov.vn/?p=59530
- SGGP, mục tiêu > 3 triệu người học ĐH 2030: https://www.sggp.org.vn/den-nam-2030-viet-nam-dat-quy-mo-tren-3-trieu-nguoi-hoc-dai-hoc-post784107.html
- Đại học Duy Tân, 25 năm đại học tư thục (số 2017-2018): https://duytan.edu.vn/news/uploads/files/25-nam-hinh-thanh-phat-trien-dai-hoc-tu-thuc-ngay-cang-dong-vai-tro-quan-trong.pdf
- thitruongtaichinhtiente, tỷ giá 26/10/2026: https://thitruongtaichinhtiente.vn/ngay-26-10-ty-gia-trung-tam-di-ngang-86561.html
- Nền lãi suất/tín dụng: `sector_read_ngan_hang_20261031.md`; nền vĩ mô: `vn_macro_regime_history.md` MACRO UPDATE 14/10; đọc cấp ngành CNTT trước: `vn_macro_regime_history.md` SECTOR READ 14/10.
