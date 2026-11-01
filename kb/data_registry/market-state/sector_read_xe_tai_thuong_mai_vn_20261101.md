---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-01. Không được cung cấp mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của ai về doanh nghiệp xe tải cụ thể, và không đi tìm chúng.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ thị trường xe tải thương mại VN, gồm xe tải nhẹ/trung/nặng, xe đầu kéo, nhập khẩu nguyên chiếc (CBU) và lắp ráp CKD, kênh đại lý/nhà phân phối, tài chính mua xe trả góp. Có pipeline cầu 2026-2028, quy định (khí thải, niên hạn, tải trọng, LEZ), cấu trúc cạnh tranh và thuế, tín dụng, phân loại chế độ, FORECAST khoá trước và checklist DD.
as_of: 2026-11-01 (tin web ≤ 2026-10-31; không truy vấn BQ cấp DN, không đọc BCTC)
---

# SECTOR READ: Xe tải thương mại Việt Nam, as-of 01/11/2026 (Bobby, real-time BLIND)

File này không phải episode VNINDEX và không tính vào N_effective. Nhãn: **[DK]** là dữ kiện có nguồn và ngày. **[UĐ]** là ước đoán
hoặc suy luận của Bobby. **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này, có thể sai, không dùng làm số pin. **(ước lượng)** là
số Bobby tự tính hoặc không kiểm chứng được.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Đã đọc nội bộ:** `sector_read_thep_20261031.md` (lấy định dạng; nền đầu tư công, thép XD), `sector_read_ngan_hang_20261031.md` (mục lãi
  suất cho vay, CV 9608, NPL tài chính tiêu dùng), `vn_macro_regime_history.md` mục MACRO UPDATE 14/10. Không đọc `kb/projects/*`,
  `agents/Taylor/*`, báo cáo DD nào. Không truy vấn `ticker`/`ticker_financial`.
- **Không tra:** giá cổ phiếu, BCTC, khuyến nghị CTCK của bất kỳ DN xe tải nào.
- **Rò thông tin cấp DN qua web (khai trung thực):**
  (a) Một kết quả tìm kiếm có tiêu đề báo cáo BSC "VVS - lợi thế dẫn đầu trong chu kỳ phục hồi của ngành xe tải" (stockbiz). Snippet nói
  VVS dẫn đầu hệ thống phân phối Howo nhờ quyền bảo hành chính hãng độc quyền. Tôi **không mở**.
  (b) Bài The Investor 22/02/2026 tôi mở để lấy số VAMA 2025. Bài có số doanh thu và LNTT 2025 của hai DN niêm yết (một nhà phân phối
  Howo, một nhà lắp ráp xe tải), và tỷ lệ chi phí bán hàng/doanh thu của 5 DN ô tô niêm yết. Tôi **không dùng** các số cấp DN này ở bất kỳ
  đâu trong file. Chỉ lấy số ngành (VAMA xe tải 2025) và câu "giao hàng xe >10 tấn bị chậm vì thiếu nguồn cung".
  (c) Tiêu đề TC Group (Hyundai Thành Công) về doanh số xe thương mại theo tháng, và số Thaco xe thương mại 9T (just-auto). Hai DN này
  **không niêm yết** theo hiểu biết của tôi [NỀN]. Tôi dùng ở mức thị phần/khối lượng.
  (d) Tin PGBank cho vay mua xe tải Foton (VNBA 24/09/2026), dùng làm bằng chứng về điều kiện tín dụng.
  **Ghi chú cho Mike (không phải phán đoán của tôi):** `context_pack.md` mục "BANNED vĩnh viễn" có liệt kê VVS. Nếu DN mục tiêu là VVS thì
  cổng BANNED vẫn đứng độc lập với sector read này.

## 1. Pipeline cầu 2026-2028

### 1a. Số tổng ngành [DK]. Cảnh báo: số VAMA có ít nhất 2 phạm vi khác nhau, không trộn được
| Chỉ tiêu | Số | Nguồn |
|---|---|---|
| VAMA 2025, **xe tải** | **70.746 xe (+24%)**, "phân khúc lớn thứ 2"; Hino và Thaco Truck tăng mạnh; giao xe >10 t chậm vì thiếu nguồn cung | The Investor 22/02/2026 |
| VAMA (phạm vi gồm cả xe nhập khẩu của DN ngoài hiệp hội), **xe thương mại** T9/2026 | **9.807 xe (+19% MoM)** | VOV 11/10/2026 |
| Như trên, lũy kế | 4T **+25%** (32.497); H1 **+28%**; **9T 85.749 xe (+17%)** | VCCI EN (4T); VietnamNet EN 11/07/2026 (H1); VOV 11/10/2026 (9T) |
| VAMA 9T/2026 toàn thị trường | 282.029 xe (+12%); CBU +22%, CKD **+2%** | VOV 11/10/2026 |
| Phạm vi khác (just-auto/GlobalData, VAMA bán buôn): **xe thương mại** | 7T 44.313 (+6%); **9T 72.733 (> +10%)**; T9 toàn thị trường 26.209 (−0,3% YoY) | just-auto 12/10/2026 |
| Thaco xe thương mại 9T/2026 | 19.297 (**−2%**) | just-auto 12/10/2026 |
| Hyundai Thành Công xe thương mại 9T/2026 | 10.687; T9 1.138 | thitruongtaichinhtiente.vn (TC Group, 10/2026) |
| Hải quan, **ô tô vận tải** nhập khẩu (HS 8704, **gồm cả bán tải**) | H1 22.668 (+83,8%); 8T 30.938 (+74,7%); **đến 15/10: 35.794 xe (+67,8%), >1 tỷ USD (+66,4%)**; 1-15/10: 1.176 (−13,6% YoY). 9T/2025 = 19.988 | TBTCVN 01/08; Thương hiệu & Công luận 24/09; TC Thuế-Hải quan 22/10/2026 |
| Nhập khẩu xe tải theo nguồn | T4: 3.262 xe, **Trung Quốc 2.610 (80%)**; T6: 4.789, TQ 2.025, Thái Lan 2.605; T8: 2.707 (−51,3% MoM), **TQ 1.627** (−10,1% MoM ⇒ T7 khoảng 1.809), Thái Lan 466 (T7 khoảng 3.642) | TBTCVN 26/05, 01/08; Thương hiệu & Công luận 24/09/2026 |
| Vận tải hàng hoá (mọi phương thức) | **9T 2.580,2 tr t (+15,8%)**; Q3 941,3 tr t (+18,1%); đường bộ 7T khoảng 1,44 tỷ t (+15,9%), H1 73,7% tổng | VCCI (dẫn Cục Thống kê) 10/2026; VnEconomy 08/2026 |
| Hàng qua cảng biển | 9T 944,18 tr t (+18%); container 27,54 tr TEU (+9%); **hàng nội địa +28%** | TBTCVN 10/2026 (một nguồn, số ước) |
| Thép XD bán 9T (cầu vật liệu chở bằng xe ben/xe tải nặng) | 11,64 tr t (+19,6%) | sector read thép 31/10 (VSA qua Người Quan Sát 26/10) |

**Đọc [UĐ]:**
1. **Giảm tốc rõ ở Q3/2026.** Cùng phạm vi VOV, tăng trưởng lũy kế xe thương mại đi từ +28% (H1) xuống +17% (9T). Suy ngược ra **Q3/2026
   khoảng −3% đến 0% YoY** (ước lượng; giả định T7 trong khoảng 8.000-9.500 xe vì không có số T7 cùng phạm vi). Thaco xe thương mại 9T −2%.
   Nhập khẩu xe tải gốc TQ giảm đều từ T4 (2.610) xuống T8 (1.627). Nửa đầu T10 nhập khẩu xe vận tải −13,6% YoY.
2. **Cầu nền vẫn tốt.** Vận tải hàng hoá Q3 +18,1%, hàng nội địa qua cảng +28%, thép XD +20%. Chênh lệch giữa "hàng hoá chạy +16-18%" và
   "xe mới bán ~0% trong Q3" cho thấy (i) đội xe đã được bổ sung mạnh năm 2025 (+24%) và H1/2026, nên năng lực chở đang đuổi kịp cầu; hoặc
   (ii) Q2 có mua trước một sự kiện chính sách (các mốc 01/03 khí thải, 01/07 Nghị định 89 niên hạn, 01/07 LEZ Hà Nội). Tôi **không có bằng
   chứng** phân biệt (i) và (ii).
3. **Số nhập khẩu "ô tô vận tải" phải đọc tách.** Dòng từ Thái Lan gần như chắc là bán tải [NỀN]. Dòng từ Trung Quốc gần với xe tải thật
   (trung, nặng, đầu kéo, xe ben). Con số +67,8% không phải "xe tải nặng tăng 68%".
4. Phạm vi just-auto (7T +6%, 9T > +10%) không khớp nội bộ với phạm vi VOV. Tôi lấy VOV làm phạm vi chính vì có chuỗi 4T/H1/9T cùng nguồn
   VAMA. **Không trừ chéo hai phạm vi.**

### 1b. Theo kênh cầu
| Kênh | Số liệu as-of [DK] | Đọc cho xe tải |
|---|---|---|
| **Đầu tư công** | Giải ngân 9T 642.962 tỷ / 62,9% KH (sector read thép). **Dự kiến 2027:** chi đầu tư phát triển NSTW khoảng **757,2 nghìn tỷ, +287,2 nghìn tỷ** so với dự toán 2026; trung hạn 2026-2030 **8,22 triệu tỷ**; giảm ≥30% số dự án NSTW; Hà Nội định hướng 2027 khoảng 404.289 tỷ (TC KT-TC; SGGP; TBTCVN 10/2026, đều là số **dự kiến**, Quốc hội chưa chốt tại 31/10) | Kênh lớn nhất cho **xe ben, xe trộn bê tông, đầu kéo chở vật liệu, xe tải nặng**. Q4/2026 là mùa giải ngân. Nếu dự kiến 2027 được duyệt thì đây là đỡ cầu mạnh cho 2027 [UĐ]. Rủi ro: đầu tư công tập trung vào ít dự án lớn hơn (đường sắt tốc độ cao, sân bay), nên cầu xe phân bố theo công trường lớn chứ không rải đều |
| **Logistics/XNK** | Cảng 9T +18%, container +9%; XK/NK 9T (MACRO UPDATE 14/10: nhập siêu 9T) | Đầu kéo container và xe tải trung chạy theo khối lượng cảng. Container +9% thấp hơn tổng hàng +18%, nên đầu kéo container tăng chậm hơn xe ben [UĐ] |
| **Xây dựng tư nhân/nhà ở** | Mở bán nhà ở đỉnh H1/2026, gãy Q3 (sector read thép, BĐS phía Bắc) | Xe ben/xe trộn cho dự án tư nhân sẽ yếu từ H1/2027 [UĐ] |
| **Bán lẻ, phân phối đô thị, thương mại điện tử** | Không có số ngành xe tải nhẹ | Xe tải nhẹ < 3,5 t (giao hàng nội đô) bị chặn bởi LEZ và giờ cấm, nhưng được đỡ bởi tiêu dùng. **Không có số** |
| **Thay thế đội xe (niên hạn, khí thải)** | Mục 1c | Cầu thay thế bắt buộc là **nhỏ và rải theo năm**, không phải cú sốc |

### 1c. Quy định đổi cầu [DK trừ khi ghi khác]
- **Khí thải xe đang lưu hành, QĐ 43/2025/QĐ-TTg** (ký 28/11/2025, hiệu lực **01/03/2026**; thay phần xe đang lưu hành của QĐ 16/2019 và
  19/2024), áp cho "xe ô tô" nói chung, bài báo không tách xe tải (VnEconomy 29/11/2025):

  | Năm sản xuất | Toàn quốc | Hà Nội, TP.HCM |
  |---|---|---|
  | Trước 1999 | Mức 1 từ 01/03/2026 | Mức 1; từ 01/01/2029 tối thiểu Mức 2 |
  | 1999-2016 | Mức 2 từ 01/03/2026 | Mức 2; từ 01/01/2029 tối thiểu Mức 2 |
  | 2017-2021 | Mức 3 từ 01/03/2026 | **Mức 4 từ 01/01/2027** |
  | Từ 2022 | Mức 4 từ 01/03/2026; Mức 5 từ 01/01/2032 | **Mức 5 từ 01/01/2028** |

  Đọc [UĐ]: mốc **01/01/2027 tại HN/TP.HCM** là mốc có tác động nhất với xe tải. Xe diesel đời 2017 có thể được chứng nhận theo chuẩn cũ
  hơn Euro 4 [NỀN: VN áp Euro 4 cho xe diesel mới từ 2018, Euro 5 từ 2022, chưa kiểm lại], nên một phần đội xe tải đời 2017-2018 chạy
  trong 2 thành phố có thể phải thay hoặc sửa. Quy mô **không có số**. Có tin một nguồn nói gần 16% xe kiểm tra không đạt ở TP.HCM, chủ yếu
  xe tải và đầu kéo (qua tóm tắt tìm kiếm, chưa mở bài gốc).
- **Xe mới:** QĐ 19/2024/QĐ-TTg giữ **Mức 5 (Euro 5)** cho xe nhập khẩu và sản xuất/lắp ráp từ 01/01/2025. **Chưa có văn bản Euro 6**
  (tìm kiếm 01/11/2026). Vì thế không có làn sóng mua trước Euro 6 trong 2026-2028 [UĐ].
- **Niên hạn:** Nghị định **89/2026/NĐ-CP** (30/03/2026, hiệu lực 01/07/2026, thay NĐ 166/2024): ô tô tải và ô tô tải chuyên dùng **25 năm**
  tính từ năm sản xuất (thuvienphapluat). Năm 2025 cả nước có **10.016 ô tô hết niên hạn, 9.925 là xe chở hàng**; TP.HCM 2.147 xe tải, Hà Nội
  1.556 (lsvn, Lao Động). Đọc [UĐ]: khoảng 10 nghìn xe tải/năm hết niên hạn, tức khoảng **14%** doanh số xe tải 2025 (70.746). Đây là cầu
  thay thế nền, nhưng một phần xe hết niên hạn vẫn chạy ở vùng xa (dữ liệu cũ 2021 nói >170.000 xe tải quá niên hạn vẫn lưu thông) [NỀN].
- **LEZ Hà Nội:** HĐND thông qua 15/06/2026, chạy từ **01/07/2026**. Giai đoạn 1 (đến 31/12/2026): cấm hoàn toàn xe tải > 3,5 t tại khu vực
  1 và 2 phường Hoàn Kiếm. Giai đoạn 2 từ **01/01/2028**: toàn Vành đai 1 (một nguồn nói lấn sang Vành đai 2). Giai đoạn 3 từ 01/01/2030: tới
  Vành đai 3 (SGGP, Đại biểu Nhân dân, Doanh nghiệp Hội nhập 14/07/2026). Đọc [UĐ]: 2026-2027 tác động nhỏ. **2030 (Vành đai 3)** mới là mốc
  đổi cơ cấu xe tải giao hàng đô thị Hà Nội (sang xe điện/xe đạt chuẩn cao), ngoài cửa sổ 2028.
- **Tải trọng:** NĐ 168/2024 (hiệu lực từ 2025) [NỀN về ngày hiệu lực]: quá tải ≤10% chưa phạt; >50% trừ 4 điểm GPLX; chủ xe cơi nới thùng
  bị phạt và có thể bị tước bằng (luatminhkhue, Znews). Địa phương xử lý thường xuyên, ví dụ Trạm CSGT Tân Lạc (Phú Thọ) >260 ca quá tải, 14 ca
  cơi nới (Doanh nghiệp Hội nhập 16/07/2026). Bộ Công an đang lấy ý kiến sửa NĐ 168; có dự thảo tăng gấp 3 mức phạt xếp hàng quá tải tại
  cảng (VietnamNews; VnEconomy, chưa rõ ngày). Đọc [UĐ]: siết quá tải làm **tăng số xe cần cho cùng khối lượng hàng**. Đây là lực cầu cấu
  trúc nhỏ nhưng một chiều, và nó do cưỡng chế quyết định chứ không do giá.

### 1d. Tuổi đội xe
- Tổng ô tô đăng ký khoảng **7,13 triệu** (DTiNews 08/07/2026), không tách xe tải. **Không có số** đội xe tải đang lưu hành 2026 hay tỷ lệ xe
  tải >15 năm. Không suy.

### 1e. Mức hồi phục và pha [UĐ]
- 2025 (+24%) và H1/2026 (+28%) là nhịp tăng mạnh. **Q3/2026 đi ngang** (ước lượng). Cầu nền (hàng hoá, đầu tư công) vẫn tăng hai chữ số.
- **2026 cả năm**: khả năng xe thương mại (phạm vi VOV) tăng khoảng **+11% đến +15%** (ước lượng), với Q4 tăng một chữ số thấp hoặc đi ngang
  so với Q4/2025.
- **2027**: hai lực ngược chiều. Đỡ: đầu tư công NSTW dự kiến +60% và mốc khí thải 01/01/2027 tại HN/TP.HCM. Kéo: nền 2025-H1/2026 cao,
  nhà ở tư nhân yếu, lãi suất cho vay đang tăng. Kịch bản trung tâm là khối lượng **đi ngang đến +5%** (ước lượng). Xe nặng/ben tốt hơn xe
  nhẹ.
- **2028**: phụ thuộc vào việc đường sắt tốc độ cao và các dự án nhóm A có thi công đồng loạt không, và vào mốc Euro 5 cho xe đời 2022+ tại
  HN/TP.HCM (01/01/2028). Không có số.

## 2. Cấu trúc cạnh tranh, giá, thuế

### 2a. Theo phân khúc (phần lớn [NỀN], chưa kiểm thị phần 2026)
| Phân khúc | Nhóm chính | Ghi chú |
|---|---|---|
| **Tải nhẹ (< 3,5 t, đến khoảng 5 t)** | **Hàn** (Hyundai Porter/N250/Mighty, Kia K-series qua Thaco), **Nhật** (Isuzu, Suzuki), Thaco (Towner/Frontier/Ollin), nhiều thương hiệu Trung-Hàn lắp ráp nhỏ (Tera, JAC, Dongben, SRM, Foton...) | Phân khúc giá nhạy nhất, nhiều xe lắp ráp CKD, khách là hộ kinh doanh, phụ thuộc trả góp. PGBank cho vay Foton Aumark 90% giá trị xe (DK, VNBA 24/09/2026) cho thấy thương hiệu TQ cũng đi kèm gói tài chính |
| **Tải trung (5-15 t)** | Nhật (Isuzu, Hino, Fuso qua Thaco), Hàn (Hyundai Mighty/New Mighty), Thaco Auman/Ollin (gốc Foton), Trung Quốc (Chenglong, Dongfeng, JAC) | Nhật thắng ở độ bền và giá bán lại; TQ thắng giá mua. Isuzu T4/2026 bán 1.102 xe (+28%), Hino 244 (+5%) (MarkLines qua tóm tắt tìm kiếm, một tháng) |
| **Tải nặng, xe ben, đầu kéo** | **Trung Quốc chiếm đa số**: Howo/Sinotruk, Chenglong (Dongfeng Liễu Châu), Dongfeng, Shacman, FAW, Thaco Auman CKD. Hàn: Hyundai Xcient/HD. Nhật: Hino 700, Isuzu Giga. Mỹ: đầu kéo đã qua sử dụng (International, Freightliner...). Châu Âu (Volvo, Scania, Mercedes, MAN) ngách | Một nguồn (tóm tắt tìm kiếm, dẫn Technavio) nói **thương hiệu TQ khoảng 80% đầu kéo**, và Sinotruk tăng từ **19% (2020) lên 66% (2025)** trong xe tải nhập khẩu. Hai số này chưa đọc từ nguồn gốc. Nhập khẩu xe tải gốc TQ T4/2026 chiếm 80% xe tải nhập (DK) |

**Đọc [UĐ]:** cấu trúc ngành là **ba tầng**. Tầng nhẹ là cạnh tranh nhiều người, biên mỏng, gắn với tín dụng hộ kinh doanh. Tầng trung là
Nhật-Hàn giữ thương hiệu. Tầng nặng là Trung Quốc thống trị về số lượng nhờ giá. Trong tầng nặng, nhà phân phối được hãng TQ trao quyền bảo hành
chính hãng (độc quyền) có lợi thế lớn hơn đại lý thường. Thời hạn và điều khoản các hợp đồng đó là rủi ro trung tâm của mô hình phân phối
(mục 6).

### 2b. Giá
- **Không có số** về giá xe tải năm 2026 theo phân khúc, và không có tin khuyến mãi/tồn kho riêng xe tải trong T10/2026 (các tin khuyến mãi đều
  là xe du lịch). Giá trung bình xe tải nhập khẩu T4/2026 khoảng **33.000 USD/xe** (107 triệu USD / 3.262 xe, ước lượng, chưa thuế); cả giai
  đoạn đến 15/10 khoảng **28.000 USD/xe** (>1 tỷ USD / 35.794, ước lượng; bị bán tải kéo xuống).
- Đọc [UĐ]: tầng nặng định giá theo **giá xe TQ cập cảng + thuế + phí**. Giá xe TQ chịu áp lực giảm phát xuất khẩu của TQ (sector read thép
  mục 3c: giảm phát công nghiệp TQ), nên biên của nhà phân phối không đến từ tăng giá bán mà từ khối lượng, dịch vụ, phụ tùng, và tài chính.

### 2c. Thuế và hàng rào [phần lớn NỀN, chưa đọc văn bản gốc]
- **Thuế nhập khẩu MFN** cho HS 8704 khác nhau theo tổng trọng lượng: xe nhẹ chịu mức cao (một bài cũ không rõ năm nêu >6 t là 50%, 10-20 t
  là 25%); xe rất nặng và đầu kéo (HS 8701) chịu mức thấp hơn nhiều [NỀN]. **ATIGA**: 0% cho xe ASEAN đủ xuất xứ (bán tải Thái Lan) [NỀN].
  **ACFTA**: biểu 2022-2027, bình quân chung khoảng 3,05%, nhưng ô tô thuộc nhóm nhạy cảm; một bài nêu ô tô TQ có thể chịu thuế **tới 49%**
  tuỳ mẫu (Doanh nghiệp Hội nhập 03/08/2026, tóm tắt). **Tôi không xác minh được mức ACFTA 2026 cho xe tải nặng/đầu kéo**. Đây là khoảng trống
  dữ liệu, DD phải đọc biểu thuế theo mã HS 8 số.
- **TTĐB:** Luật TTĐB 66/2025/QH15 hiệu lực 01/01/2026 (sửa đổi một phần bởi Luật 09/2026/QH16 thông qua 24/04/2026, chưa rõ phạm vi). Bán tải
  chở hàng cabin kép đã chịu TTĐB theo lộ trình 2026-2027, các nguồn chưa thống nhất mức (VietnamFinance, VnEconomy, Đại Đoàn Kết). **Xe tải chở
  hàng thuần không chịu TTĐB** [NỀN, chưa kiểm Điều 8 Luật 66/2025]. Đọc [UĐ]: lộ trình TTĐB bán tải có thể giải thích nhịp nhập khẩu bán tải
  Thái Lan T6-T7/2026 (mua trước mốc tăng thuế 2027). Đây là suy luận, chưa có nguồn nói vậy.
- **Chống bán phá giá/tự vệ với xe tải nhập khẩu:** tôi **không thấy** vụ nào đang có hay đang điều tra (tìm kiếm 01/11/2026). Ngược với thép,
  nơi cửa hành chính đã đóng với hàng TQ.
- **Kiểm tra chất lượng xe nhập khẩu:** NĐ 60/2023/NĐ-CP (kiểm tra theo lô, cần giấy chứng nhận kiểu loại nước ngoài). Có dự thảo bổ sung trách
  nhiệm triệu hồi xe nhập khẩu (tóm tắt tìm kiếm). Không thấy văn bản mới năm 2026 làm đổi hàng rào này.
- **Lắp ráp CKD:** ưu đãi thuế linh kiện theo NĐ 57/2020 và các bản sửa [NỀN]. CKD 9T chỉ +2% trong khi CBU +22% (toàn thị trường, VOV). Đây là
  dấu hiệu chung rằng **hàng CBU đang lấn CKD** [UĐ, số toàn thị trường không riêng xe tải].

## 3. Lãi suất, tín dụng mua xe, rủi ro nợ xấu vận tải

| Tầng | Số as-of | Nguồn |
|---|---|---|
| Lãi huy động effective của team (A/B, max Big-4 12M và CCTG) | **7,4%** (12/10) | MACRO UPDATE 14/10 |
| Lãi cho vay BQ giao dịch mới (NHNN) | **9,12%** (30/09), **+1,03pp YTD** | sector read ngân hàng 31/10 |
| Gói vay mua xe tải theo hãng | PGBank cho xe Foton Aumark: **từ 6%/năm cố định 12 tháng đầu, tài trợ tới 90%**, 01/09-31/10/2026; lãi thực tế theo thẩm định | VNBA 24/09/2026 |
| Biểu vay mua ô tô NH tư nhân | khoảng 5,9-12,5% tuỳ gói, thả nổi sau ưu đãi 6-12 tháng; một số NH ghi "từ 5,2-6,1%", kỳ hạn tới 7 năm | VPBank (ngày cập nhật không đáng tin), Topi (không ngày) |
| Chỉ thị NHNN | CV 9608 (18/10) đòi giảm lãi cho vay SXKD/ưu tiên 1,5-2pp, siết cho vay lách | sector read ngân hàng 31/10 |
| NPL công ty tài chính tiêu dùng | 7,2% (2025; đỉnh 11,2% năm 2023) | sector read ngân hàng (FiinGroup qua TC KT-TC) |
| NPL riêng cho vay xe tải/vận tải | **không có số** | — |

**Đọc [UĐ]:**
- **Hướng:** chi phí vốn biên của người mua xe đang **tăng**. Lãi ưu đãi 6% chỉ cố định 12 tháng, sau đó thả nổi theo mặt bằng cho vay đã
  +1pp YTD. **Mức:** khoảng cách giữa "lãi quảng cáo 6%" và "lãi BQ cho vay mới 9,12%" là khoảng 3pp. Người mua xe tải là hộ kinh doanh, sẽ chịu
  mức thả nổi từ năm thứ 2. Độ tin cậy thấp vì không có biểu lãi vay xe tải thực tế theo hợp đồng.
- **Rủi ro tín dụng vận tải:** chi phí nhiên liệu là biến số lớn. Diesel 0,05S khoảng **27.490-28.030 đ/lít ngày 07/05/2026** (thuvienphapluat,
  bảng giá), sau cú sốc dầu Trung Đông đầu 2026 (EP-2026-01 trong registry). Kỳ 01/10/2026 diesel **giảm 780 đ/lít**, diesel thế giới bình quân
  khoảng 167 USD/thùng (Bộ Công Thương). Không có giá bán lẻ T10. Đọc [UĐ]: chủ xe vay 90% giá trị xe, cước chưa kịp tăng theo dầu, và lãi thả nổi
  tăng sau năm đầu. Đây là bộ ba làm nợ xấu xe tải tăng với **độ trễ 4-8 quý** sau năm bán mạnh nhất (2025-H1/2026) [NỀN về độ trễ]. Vùng rủi
  ro rơi vào **H2/2027**.
- **Tác động lên nhà phân phối:** nếu nhà phân phối bảo lãnh hoặc cam kết mua lại xe cho ngân hàng (thoả thuận ba bên) thì rủi ro tín dụng của
  người mua chuyển về bảng cân đối của nhà phân phối. Đây là mục DD số 1 (mục 6C).

## 4. Phân loại chế độ ngành

| Nhãn | Xác suất | Lý do |
|---|---|---|
| **CYCLICAL** | **0,50** | Khối lượng đi theo xây dựng, đầu tư công và vận tải hàng hoá. Đã có nhịp tăng 2025 (+24%) và H1/2026 (+28%), rồi Q3 đi ngang (ước lượng). Nền cao, lãi suất cho vay tăng, nhà ở tư nhân gãy Q3. Đây là hình dạng của **pha muộn nhịp tăng** khối lượng |
| **ADMIN_GATED** | **0,30** | Cầu do văn bản quyết: giải ngân đầu tư công và kế hoạch 2027 (+287 nghìn tỷ NSTW, chưa chốt); mốc khí thải QĐ 43/2025 (01/01/2027, 01/01/2028 tại HN/TP.HCM); niên hạn NĐ 89/2026; LEZ Hà Nội; cưỡng chế quá tải NĐ 168; room tín dụng và CV 9608. Cung do văn bản quyết: thuế TTĐB bán tải, kiểm tra chất lượng NĐ 60/2023. Khác thép, **không có cửa PVTM nào chặn xe TQ**, nên cửa hành chính chủ yếu ở phía cầu |
| **STRUCTURAL** | **0,20** | Hàng hoá đường bộ tăng dài hạn theo GDP và logistics; đội xe hiện đại hoá (Euro 5, niên hạn, siết quá tải); **Trung Quốc thâm nhập tầng nặng** (Sinotruk 19% → 66% xe tải nhập khẩu 2020-2025, một nguồn). Phía xấu cấu trúc: CBU lấn CKD, giá xe TQ bị giảm phát kéo xuống |

- **Pha [UĐ]:** khối lượng **muộn nhịp tăng, chuyển sang đi ngang**; tín dụng mua xe **đắt dần**; chất lượng tín dụng vận tải **chưa xấu đi
  thấy được** (không có số) nhưng có độ trễ. Không phải khủng hoảng. Không phải đỉnh như 2025.
- **Phân hoá [UĐ]:** **xe nặng/ben/đầu kéo** = CYCLICAL + ADMIN_GATED theo đầu tư công 2027, tốt hơn trung bình. **Xe nhẹ** = CYCLICAL theo
  tiêu dùng và tín dụng hộ, cộng LEZ đô thị dài hạn, kém hơn trung bình. **Đầu kéo container** = theo XNK/cảng (container +9%), trung bình.
- **Confidence: `ambiguous` (~55/45).** Phần chưa biết lớn nhất: (a) số VAMA xe tải tách phân khúc (VAMA "xe thương mại" có thể gồm bán tải và
  xe khách [NỀN]); (b) Q3 đi ngang là "đội xe đã đủ" hay "mua trước Q2 vì chính sách"; (c) kế hoạch đầu tư công 2027 được Quốc hội chốt ở mức
  nào; (d) mức thuế ACFTA thật với xe tải nặng TQ.
- **Liên hệ nền vĩ mô:** REGIME READ #2 / MACRO UPDATE giữ Loại-1 STRUCTURAL_ACCUMULATION BĐS, ambiguous. Kịch bản B (đóng băng thanh khoản BĐS
  cục bộ, 20-25%) làm hại xe ben/xe trộn phục vụ dự án tư nhân và làm tăng nợ xấu hộ vận tải. Đầu tư công là đối trọng do Nhà nước chủ động.

## 5. FORECAST KHOÁ TRƯỚC (lập 2026-11-01; chấm bằng nguồn công bố đầu tiên ≤ ngày chấm; không có nguồn ⇒ ghi "không chấm được", không suy)

| # | Mệnh đề | P | Ngày chấm | Nguồn chấm |
|---|---|---|---|---|
| F1 | VAMA, phạm vi gồm xe nhập khẩu ngoài hiệp hội (như VOV 11/10): **xe thương mại cả năm 2026 tăng ≥ +10% YoY** (9T +17%) | 0,75 | 2027-01-20 | VAMA báo cáo T12/2026 (qua VOV/VnEconomy) |
| F2 | Cùng phạm vi F1: **xe thương mại Q4/2026 (T10-T12) tăng < +10% YoY** (tính = cả năm − 9T, hai năm cùng phạm vi) | 0,60 | 2027-01-20 | như F1 |
| F3 | Cùng phạm vi F1: **xe thương mại Q1/2027 tăng < +5% YoY** | 0,55 | 2027-04-20 | VAMA T3/2027 (lũy kế 3T) |
| F4 | Hải quan: **ô tô vận tải nhập khẩu cả năm 2026 ≥ 40.000 xe** (đến 15/10: 35.794) | 0,80 | 2027-01-31 | Cục Hải quan / TC Thuế-Hải quan |
| F5 | Hải quan: **ô tô vận tải nhập khẩu từ Trung Quốc, bình quân T10-T12/2026 < 2.500 xe/tháng** (T8: 1.627; T4: 2.610) | 0,70 | 2027-02-15 | Hải quan theo thị trường (TBTCVN/Thương hiệu & Công luận). Không có số theo nguồn ⇒ không chấm được |
| F6 | **Không có** vụ điều tra AD/CVD/tự vệ nào của VN với xe tải hoặc đầu kéo nhập khẩu (HS 8701/8704) được khởi xướng trước 2027-06-30 | 0,90 | 2027-06-30 | Cục PVTM (Bộ Công Thương) |
| F7 | Mốc QĐ 43/2025: **HN/TP.HCM áp Mức 4 với xe SX 2017-2021 từ 01/01/2027 KHÔNG bị lùi** bằng văn bản ban hành trước 2027-01-01 | 0,75 | 2027-01-05 | Chính phủ / Bộ NN&MT / Cục Đăng kiểm |
| F8 | NHNN: **lãi cho vay BQ giao dịch mới** (số công bố gần nhất trước ngày chấm) **≥ 9,0%** (30/09: 9,12%) | 0,60 | 2027-03-31 | NHNN / Bộ Tài chính họp báo |
| F9 | Cục Thống kê: **vận tải hàng hoá cả năm 2026 tăng ≥ +14% YoY** (9T +15,8%) | 0,75 | 2027-01-15 | NSO báo cáo KT-XH năm 2026 |
| F10 | Quốc hội chốt **chi đầu tư phát triển NSTW 2027 ≥ 700 nghìn tỷ** (dự kiến 757,2) | 0,70 | 2026-12-15 | Nghị quyết dự toán/phân bổ NSTW 2027 |
| F11 | **Chưa có văn bản** ấn định ngày áp Euro 6 (Mức 6) cho xe tải mới nhập khẩu/lắp ráp được ban hành trước 2027-06-30 | 0,85 | 2027-06-30 | Chính phủ (QĐ TTg) |

Lý do chính: F1 cần Q4 không tệ hơn khoảng −5% đến −10% YoY (tuỳ độ lớn Q4/2025, chưa có số cùng phạm vi), nên xác suất cao. F2/F3 dựa trên giảm tốc Q3 (ước lượng −3% đến 0%) và nền Q4/2025-Q1/2026
cao. F4 chỉ cần khoảng 1.700 xe/tháng cho 2,5 tháng còn lại (4.206 xe). F5 dựa trên xu hướng giảm đều T4-T8. F6/F11 dựa trên việc không thấy tín hiệu nào.
F7 dựa trên việc QĐ 43 đã lùi một lần so với dự thảo, nhưng thường mốc đã ký ít bị lùi; lịch kiểm định khí thải xe máy ở HN/TP.HCM từng được đề
xuất lùi (lsvn), đó là rủi ro chính. F8 dựa trên áp lực vốn (MACRO UPDATE) ngược chiều chỉ thị giảm lãi CV 9608. F10 là đồng xu nghiêng: Quốc hội
thường duyệt gần số Chính phủ trình [NỀN], nhưng số dự kiến tăng rất mạnh.

## 6. Chỉ báo dẫn dắt (theo dõi tháng/quý)
1. VAMA tháng: xe thương mại (và nếu có, tách xe tải/bán tải/xe khách); số Thaco, TC Group, Isuzu, Hino theo tháng.
2. Hải quan nửa tháng: ô tô vận tải nhập khẩu theo nguồn (Trung Quốc vs Thái Lan), cửa khẩu Lạng Sơn/Cao Bằng.
3. Giải ngân đầu tư công (tuần), nghị quyết dự toán 2027 (T11-T12/2026), khởi công đường sắt tốc độ cao.
4. Vận tải hàng hoá đường bộ (NSO tháng), hàng qua cảng (Cục Hàng hải), thép XD/xi măng bán nội địa.
5. Lãi cho vay BQ mới (NHNN), lãi thả nổi sau ưu đãi của gói vay xe; NPL công ty tài chính.
6. Giá diesel 0,05S (kỳ điều hành 7 ngày của Bộ Công Thương).
7. Văn bản: QĐ 43/2025 (mốc 01/01/2027), sửa NĐ 168 (quá tải), LEZ Hà Nội và TP.HCM, biểu TTĐB bán tải 2027, mọi động thái PVTM với xe TQ.

## 7. DD cần kiểm gì (một nhà phân phối hoặc lắp ráp xe tải thương mại bất kỳ ở VN; số lấy từ BCTC/BCTN/thuyết minh)

**A. Mô hình và phụ thuộc hãng**
1. Cơ cấu doanh thu: **xe mới / phụ tùng / dịch vụ bảo dưỡng / xe đã qua sử dụng / tài chính (hoa hồng NH, phí)**. Xe mới > 85% doanh thu là
   mô hình nhạy chu kỳ nhất.
2. Cơ cấu theo **phân khúc** (nhẹ/trung/nặng/đầu kéo/ben/chuyên dùng) và **theo hãng**. Một hãng > 50% doanh thu = phụ thuộc tập trung.
3. **Hợp đồng phân phối/đại lý với hãng**: độc quyền hay không, phạm vi địa lý, **thời hạn và điều kiện gia hạn**, quyền bảo hành chính hãng,
   điều khoản chấm dứt, mục tiêu doanh số tối thiểu, chính sách hỗ trợ giá/thưởng từ hãng (rebate). Có thể chỉ có trong BCTN hoặc thuyết minh
   "cam kết". Không có văn bản thì ghi là khoảng trống, không suy.
4. Lắp ráp CKD: công suất thiết kế vs sản lượng, **tỷ lệ nội địa hoá**, có hưởng ưu đãi thuế linh kiện không và điều kiện sản lượng tối thiểu.
5. Cơ cấu khách hàng: hộ kinh doanh vs đội xe DN vs nhà thầu xây dựng/nhà nước; **khách hàng lớn nhất / doanh thu**.

**B. Biên và chi phí**
6. Biên gộp theo quý **8-12 quý**, tách xe mới vs phụ tùng/dịch vụ nếu có. Biên xe mới tăng trong khi khối lượng ngành đi ngang là dấu hiệu
   cần giải thích (thưởng hãng? tồn kho giá cũ? đổi cơ cấu?).
7. Chi phí bán hàng/doanh thu, **khuyến mãi/hỗ trợ lãi suất cho khách** hạch toán ở đâu (giảm doanh thu hay chi phí bán hàng).
8. Tỷ giá: hàng nhập bằng CNY/USD, tỷ trọng nợ phải trả người bán ngoại tệ, lãi/lỗ tỷ giá chưa thực hiện, có phòng ngừa không.
9. Thuế: mã HS và mức thuế NK thực tế theo C/O (Form E ACFTA vs MFN); rủi ro truy thu xuất xứ; TTĐB nếu có bán tải; tranh chấp thuế.

**C. Vốn lưu động, tín dụng bán hàng, bảo hành**
10. **Tồn kho xe (ngày)**, tuổi tồn kho, xe tồn > 6-12 tháng; xe đời cũ có còn đăng ký được không khi chuẩn khí thải/kiểu loại đổi; **dự
    phòng giảm giá hàng tồn kho**. Tồn kho tăng nhanh hơn doanh thu 2 quý liền là cờ vàng.
11. **Phải thu khách hàng / doanh thu**, phải thu quá hạn, dự phòng phải thu khó đòi; phải thu từ **ngân hàng giải ngân chậm**.
12. **Thoả thuận ba bên với ngân hàng/công ty tài chính**: DN có **bảo lãnh, cam kết mua lại xe, hay ký quỹ** cho khoản vay của khách không?
    Dư nợ bảo lãnh ngoài bảng (thuyết minh "nợ tiềm tàng/cam kết"). Có thì nợ xấu vận tải chuyển về DN. **Mục quan trọng nhất.**
13. Bán trả chậm trực tiếp (DN tự cấp tín dụng): kỳ hạn, lãi suất, tài sản đảm bảo, tỷ lệ quá hạn.
14. **Dự phòng bảo hành**: chính sách bảo hành (năm/km), ai chịu chi phí (hãng hoàn lại hay DN tự chịu), số trích lập so với doanh thu xe,
    chi phí bảo hành thực tế so với dự phòng. Hãng TQ có hoàn đủ chi phí bảo hành không.
15. **Trả trước cho người bán** (đặt cọc hãng) và **người mua trả trước** (đơn hàng tồn): xu hướng là chỉ báo đơn hàng.
16. Vay ngắn hạn tài trợ tồn kho (floor-plan), nợ vay/VCSH, **CFO vs LNST** 4-8 quý. CFO âm khi doanh số tăng là bình thường một quý, nhưng âm
    liên tục là cờ đỏ.

**D. Pháp lý và hành chính**
17. Giấy chứng nhận kiểu loại, kiểm tra chất lượng lô nhập (NĐ 60/2023), các đợt **triệu hồi**; vi phạm về xe không đạt chuẩn khí thải.
18. Rủi ro chính sách: mốc khí thải QĐ 43/2025, LEZ, cưỡng chế quá tải, TTĐB bán tải; khả năng có PVTM với xe TQ (hiện không thấy).
19. Tranh chấp với khách hàng về chất lượng xe, khiếu nại bảo hành.

**E. Quản trị**
20. **Giao dịch bên liên quan**: mua xe qua công ty liên kết của cổ đông lớn, bán cho đội xe liên quan, cho vay/đặt cọc bên liên quan.
21. Đầu tư ngoài ngành (BĐS, nhà máy mới) bằng dòng tiền phân phối; capex xưởng dịch vụ/showroom so với dòng tiền.
22. Pha loãng (phát hành riêng lẻ, ESOP, cổ tức cổ phiếu); thay đổi kiểm toán; ý kiến kiểm toán ngoại trừ/nhấn mạnh; chênh LNST trước/sau
    kiểm toán.
23. Nếu DN tăng trưởng doanh thu gấp đôi trong khi thị trường xe tải +24% (2025), kiểm tra nguồn tăng: thị phần thật từ hãng/độc quyền, hay
    doanh thu bán cho đại lý cấp 2 chưa ra người dùng cuối (channel stuffing: so tồn kho đại lý cấp 2 nếu có, phải thu đại lý).

## 8. Điều gì làm tôi sai
- **Cầu xấu hơn tôi nghĩ:** Quốc hội cắt mạnh kế hoạch đầu tư công 2027; VAMA Q4/2026 âm hai chữ số; lãi cho vay mới > 10%; diesel tăng lại > 28.000
  đ/lít; nợ xấu tài chính tiêu dùng/hộ kinh doanh tăng sớm (2026Q4).
- **Tốt hơn tôi nghĩ:** Q3 đi ngang chỉ là khoảng lặng sau mua trước Q2, và Q4 bật lại > +15%; mốc 01/01/2027 tại HN/TP.HCM buộc thay xe nhiều hơn tôi
  ước; đường sắt tốc độ cao thi công đồng loạt 2027.
- **Lỗi dữ liệu có thể có:** VAMA có ít nhất 2 phạm vi không khớp (VOV 9T +17% vs just-auto 9T > +10%); "xe thương mại" VAMA có thể gồm bán tải và xe
  khách; số "ô tô vận tải" Hải quan gồm bán tải; ước lượng Q3 dựa trên giả định số T7; thị phần TQ trong đầu kéo (80%) và Sinotruk (66%) chỉ đọc qua
  tóm tắt tìm kiếm; thuế ACFTA với xe tải nặng chưa xác minh.

## Nguồn (ngày công bố)
- VOV, "Thị trường ô tô tháng 9/2026: Doanh số khởi sắc mạnh mẽ" — 11/10/2026: https://vov.vn/kho-xe/thi-truong-o-to-thang-92026-doanh-so-khoi-sac-manh-me-post1339924.vov
- just-auto, "Vietnam market falls slightly in September - VAMA" — 12/10/2026: https://www.just-auto.com/newsletters/vietnam-market-falls-slightly-in-september-vama
- just-auto, VAMA T7/2026 và T8/2026 (tóm tắt tìm kiếm): https://www.just-auto.com/newsletters/vietnam-vehicle-market-falls-5-in-july-vama ; https://www.just-auto.com/newsletters/vietnam-vehicle-market-falls-13-in-august-vama
- VietnamNet EN, "Vietnam's auto sales rise 15% in first half of 2026" — 11/07/2026: https://vietnamnet.vn/en/vietnam-s-auto-sales-rise-15-in-first-half-of-2026-2534684.html
- VCCI EN, "Car sales hit 126,800 in first four months of 2026" (tóm tắt tìm kiếm): https://en.vcci.com.vn/economic-news/car-sales-hit-126800-in-first-four-months-of-2026-117370
- The Investor, "Vietnam's auto market in 2025: Commercial vehicles gain the upper hand" — 22/02/2026 (chỉ dùng số ngành): https://theinvestor.vn/vietnams-auto-market-in-2025-commercial-vehicles-gain-the-upper-hand-d18435.html
- thitruongtaichinhtiente.vn, TC Group bán 3.872 xe T9/2026 (tóm tắt tìm kiếm): https://thitruongtaichinhtiente.vn/tc-group-ban-ra-3-872-xe-o-to-trong-thang-9-2026-86205.html
- TC Thuế-Hải quan, "Nhập khẩu ô tô vượt 203.000 chiếc..." — 22/10/2026: https://thuehaiquan.tapchikinhtetaichinh.vn/nhap-khau-o-to-vuot-203-000-chiec-nguon-cung-chu-luc-co-su-dich-chuyen-170207.html
- Thương hiệu & Công luận, nhập khẩu ô tô T8/2026 giảm 30,1% — 24/09/2026: https://thuonghieucongluan.com.vn/nhap-khau-o-to-nguyen-chiec-trong-thang-8-2026-giam-30-1-a335554.html
- TBTCVN, "Ô tô nguyên chiếc nhập khẩu tăng gần 8%, xe tải bứt tốc" — 01/08/2026: https://thoibaotaichinhvietnam.vn/o-to-nguyen-chiec-nhap-khau-tang-gan-8-xe-tai-but-toc-201584.html
- TBTCVN, "Nhập khẩu ô tô giảm hơn 33%, xe Trung Quốc áp đảo phân khúc thương mại" — 26/05/2026: https://thoibaotaichinhvietnam.vn/nhap-khau-o-to-giam-hon-33-xe-trung-quoc-ap-dao-phan-khuc-thuong-mai-197939.html
- Doanh nghiệp Hội nhập, ô tô TQ chiếm hơn 44% xe nhập khẩu đầu 2026 — 03/08/2026 (tóm tắt): https://doanhnghiephoinhap.vn/o-to-trung-quoc-nhap-khau-vao-viet-nam-tang-vot-chiem-hon-44-thi-phan-dau-nam-2026-128831.html
- VCCI, hoạt động vận tải 9T/2026 (dẫn Cục Thống kê) — 10/2026: https://vcci.com.vn/tin-tuc/hoat-dong-van-tai-9-thang-nam-2026-tiep-tuc-dap-ung-nhu-cau-di-lai-va-san-xuat-kinh-doanh-luu-thong-hang-hoa
- VnEconomy, vận tải 7 tháng 2026: https://vneconomy.vn/van-tai-7-thang-dau-nam-duy-tri-da-tang-truong-duong-bo-tiep-tuc-giu-vai-tro-chu-dao.htm
- TBTCVN, "Doanh nghiệp logistics đón sóng lợi nhuận tăng" (cảng 9T, tóm tắt): https://thoibaotaichinhvietnam.vn/doanh-nghiep-logistics-don-song-loi-nhuan-tang-204732-204732.html
- VnEconomy, "Chính thức siết khí thải ô tô: Hà Nội và TP.HCM sẽ áp mức cao từ 2027" — 29/11/2025 (QĐ 43/2025): https://vneconomy.vn/automotive/chinh-thuc-siet-khi-thai-o-to-ha-noi-va-tphcm-se-ap-muc-cao-tu-2027.htm
- thuvienphapluat, niên hạn xe cơ giới từ 01/07/2026 (NĐ 89/2026): https://thuvienphapluat.vn/hoi-dap-phap-luat/nien-han-su-dung-xe-co-gioi-tu-0172026-duoc-xac-dinh-nhu-the-nao-138085550.html
- lsvn, hơn 10.000 ô tô hết niên hạn năm 2025: https://lsvn.vn/hon-10-000-o-to-het-nien-han-su-dung-trong-nam-2025-a169846.html
- DTiNews, đăng ký phương tiện H1/2026 — 08/07/2026: https://dtinews.dantri.com.vn/vietnam-today/vietnam-registers-more-than-21-million-new-vehicles-in-first-half-20260708082318830.htm
- SGGP, lộ trình LEZ Vành đai 1 Hà Nội: https://www.sggp.org.vn/ha-noi-cong-bo-lo-trinh-va-cac-tuyen-pho-thi-diem-vung-phat-thai-thap-trong-vanh-dai-1-post849523.html
- Doanh nghiệp Hội nhập, Hà Nội mở rộng vùng phát thải thấp — 14/07/2026: https://doanhnghiephoinhap.vn/ha-noi-gap-rut-mo-rong-vung-phat-thai-thap-de-doi-pho-o-nhiem-114479.html
- Đại biểu Nhân dân, đề án LEZ Vành đai 1: https://daibieunhandan.vn/de-an-vung-phat-thai-thap-trong-vanh-dai-1-thanh-pho-ha-noi-ho-tro-truoc-han-che-theo-lo-trinh-cong-khai-minh-bach-vi-ha-noi-xanh-sach-dep-10422328.html
- Doanh nghiệp Hội nhập, Trạm CSGT Tân Lạc xử lý quá tải — 16/07/2026: https://doanhnghiephoinhap.vn/phu-tho-tram-csgt-tan-lac-xu-ly-hon-260-truong-hop-xe-qua-tai-143429.html
- luatminhkhue, mức phạt quá tải NĐ 168: https://luatminhkhue.vn/muc-xu-phat-doi-voi-xe-vuot-qua-tai.aspx
- VietnamNews, sửa NĐ 168 (Bộ Công an lấy ý kiến): https://vietnamnews.vn/society/1779767/traffic-penalties-to-be-revised-to-curb-unregistered-transport-services-public-security-ministry.html
- VNBA, PGBank ưu đãi vay mua xe tải Foton — 24/09/2026: https://vnba.org.vn/vi/pgbank-trien-khai-chuong-trinh-uu-dai-lai-suat-cho-khach-hang-mua-xe-tai-foton-23653.htm
- Bộ Công Thương, điều hành giá xăng dầu 01/10/2026: https://moit.gov.vn/tin-tuc/mot-so-thong-tin-dang-chu-y-ve-dieu-hanh-gia-xang-dau-ngay-1-10.html
- thuvienphapluat, bảng giá xăng dầu 07/05/2026: https://thuvienphapluat.vn/hoi-dap-phap-luat/cap-nhat-bang-gia-xang-dau-752026-moi-nhat-ron95-e5-dau-diesel-bao-nhieu-tien-1-lit-138089461.html
- TC KT-TC, kế hoạch đầu tư công 2027: https://tapchikinhtetaichinh.vn/ke-hoach-dau-tu-cong-nam-2027-phu-hop-kha-nang-can-doi-ngan-sach-tranh-dan-trai-159812.html
- SGGP, tổng vốn đầu tư công 2026-2030 8,22 triệu tỷ: https://www.sggp.org.vn/tong-muc-von-dau-tu-cong-5-nam-toi-la-822-trieu-ty-dong-post849647.html
- TBTCVN, Hà Nội định hướng đầu tư công 2027 hơn 404.000 tỷ: https://thoibaotaichinhvietnam.vn/ha-noi-thong-qua-dinh-huong-dau-tu-cong-hon-404-000-ty-dong-nam-2027-200751.html
- VietnamFinance, thuế phí ô tô bán tải theo quy định mới: https://vietnamfinance.vn/quy-dinh-moi-co-lam-thay-doi-thue-phi-doi-voi-o-to-ban-tai-d147279.html
- VnEconomy, "Xe bán tải sắp mất ngôi vua ưu đãi": https://vneconomy.vn/automotive/xe-ban-tai-sap-mat-ngoi-vua-uu-dai-tai-viet-nam.htm
- Bộ Công Thương / TBTCVN, ACFTA 2022-2027 (bình quân thuế): https://thoibaotaichinhvietnam.vn/854-dong-thue-trong-acfta-duoc-xoa-bo-toi-nam-2027-107693.html
- thuvienphapluat EN, NĐ 60/2023 kiểm tra chất lượng xe nhập khẩu: https://thuvienphapluat.vn/van-ban/EN/Xuat-nhap-khau/Decree-60-2023-ND-CP-certificate-of-conformity-from-inspection-for-imported-motor-vehicles/577202/tieng-anh.aspx
- Nền lãi suất/tín dụng/NPL: `sector_read_ngan_hang_20261031.md`; nền đầu tư công/thép XD: `sector_read_thep_20261031.md`; nền vĩ mô: `vn_macro_regime_history.md` MACRO UPDATE 14/10.
