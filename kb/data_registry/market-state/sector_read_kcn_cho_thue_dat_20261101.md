---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-01. Không được cung cấp mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của ai về doanh nghiệp KCN cụ thể, và không đi tìm chúng.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành khu công nghiệp (KCN) cho thuê đất và hạ tầng VN, trọng tâm miền Nam (TP.HCM mở rộng gồm Bình Dương và Bà Rịa-Vũng Tàu cũ; Đồng Nai gồm Bình Phước cũ; Tây Ninh gồm Long An cũ), kèm nhóm công ty KCN gắn doanh nghiệp nhà nước/tổng công ty. Có pipeline cầu (FDI, thuế Mỹ, chuỗi cung ứng, nhà xưởng xây sẵn), giá thuê, lấp đầy, quỹ đất và nút thắt, bảng 5 tầng chi phí vốn, cấu trúc cạnh tranh, ghi nhận doanh thu (TT 200 → TT 99/2025), phân loại chế độ, FORECAST khoá trước, checklist DD.
as_of: 2026-11-01 (tin web ≤ 2026-10-31; CSV lãi huy động/CCTG nội bộ tới 2026-10-26; không truy vấn ticker/ticker_financial, không đọc BCTC)
---

# SECTOR READ: Khu công nghiệp cho thuê đất & hạ tầng, miền Nam VN, as-of 01/11/2026 (Bobby, real-time BLIND)

File này không phải episode VNINDEX và không tính vào N_effective. Nhãn: **[DK]** là dữ kiện có nguồn và ngày. **[UĐ]** là ước đoán
hoặc suy luận của Bobby. **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này, có thể sai, không dùng làm số pin. **(ước lượng)** là
số Bobby tự tính hoặc không kiểm chứng được.

**Địa giới:** từ 01/07/2025 [NỀN, khớp cách Cushman & Wakefield chia thị phần cung] TP.HCM = TP.HCM cũ + Bình Dương + Bà Rịa-Vũng Tàu;
Đồng Nai = Đồng Nai + Bình Phước; Tây Ninh = Tây Ninh + Long An. Số liệu môi giới 2026 dùng địa giới mới. **Không so trực tiếp với chuỗi
tỉnh cũ trước 2025.**

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Đã đọc nội bộ:** `sector_read_xe_tai_thuong_mai_vn_20261101.md` (định dạng), `sector_read_ngan_hang_20261031.md` (bảng 5 tầng),
  `sector_read_da_xay_dung_nam_bo_20261030.md` (tiến độ Long Thành, Vành đai 3-4), `vn_sector_read_rubber_20261027.md` (chỉ dòng về chuyển
  đất cao su sang KCN), `vn_macro_regime_history.md` mục MACRO UPDATE 14/10. CSV `data/deposit_rate_vn_events.csv`,
  `cctg_rate_vn_events.csv`, `cctg_rate_vn_6m_events.csv`, log `refresh_deposit_cctg_weekly_2026-10.log` (26/10). Không đọc `kb/projects/*`,
  `agents/Taylor/*`, báo cáo DD nào. Không truy vấn `ticker`/`ticker_financial`.
- **Không tra:** giá cổ phiếu, BCTC, khuyến nghị CTCK của bất kỳ DN KCN nào.
- **Rò thông tin cấp DN qua web (khai trung thực):**
  (a) Bài Cafeland 07/04/2026 về TT 99/2025 dẫn **tài liệu ĐHĐCĐ 2026 của một tổng công ty KCN nhà nước tỉnh Đồng Nai** (Sonadezi) và nêu một
  công ty con của nhóm này đang ghi nhận một lần. Tôi chỉ dùng **câu mô tả quy định**, không dùng số nào của DN.
  (b) Tóm tắt tìm kiếm về chuyển đất cao su có tên tập đoàn cao su nhà nước và 3 công ty con niêm yết, kèm ước tính doanh thu đền bù của
  CTCK cho một công ty, và tin "quyết định thu hồi đất ngày 19/5/2026" cho một KCN cơ khí. Tôi chỉ dùng **số diện tích cấp tập đoàn được
  duyệt chuyển đổi** (mức ngành), không dùng số đền bù/lợi nhuận cấp DN.
  (c) Tiêu đề The Investor 26/11/2025 "IP developers post strong earnings" và tiêu đề một báo cáo ngành KCN của một CTCK (01/2026). **Không
  mở.**
  (d) Tên các nhóm chủ đầu tư (Becamex, Sonadezi, IDICO, Tập đoàn Cao su VN, VSIP, Amata...) ở mục 2a là mô tả cấu trúc ngành theo hiểu biết
  nền [NỀN], không tra giá hay BCTC của họ.
  **Ghi chú cho Mike:** đối chiếu danh sách BANNED trong `context_pack.md`: không có mã nào thuộc nhóm KCN trong danh sách đó (theo hiểu biết
  của tôi về mã của các nhóm trên). Nếu DN mục tiêu có mã, cổng BANNED/excluded vẫn đứng độc lập với sector read này.

## 1. Pipeline cầu và thị trường

### 1a. Dòng vốn FDI [DK]
| Chỉ tiêu | 9T/2026 | So sánh | Nguồn |
|---|---|---|---|
| FDI đăng ký tổng | **50,36 tỷ USD (+76,4%)** | 2025 cả năm 38,42 tỷ (+0,5%) | Báo Đấu thầu, VietnamFinance 03/10/2026; NSO qua tìm kiếm (2025) |
| — cấp mới | **29,24 tỷ USD, ×2,4**; **3.108 dự án (+6,2%)** | | Báo Đấu thầu 10/2026 |
| — điều chỉnh | 14,15 tỷ USD (+25,1%), 948 lượt | | như trên |
| — góp vốn/mua CP | 6,97 tỷ USD (+44%), 2.335 lượt | | như trên |
| — chế biến chế tạo trong vốn đăng ký | 13,38 tỷ USD, 45,8% | 8T: 12,15 tỷ cấp mới | như trên; Báo Pháp luật 8T |
| Nguồn vốn cấp mới | Singapore 9,26 tỷ (31,7%), Hàn Quốc 5,70, Luxembourg 4,99 | 8T: Hồng Kông 2,96 (13,6%), TQ đại lục 1,93 (8,9%) | Báo Đấu thầu; Báo Pháp luật/Mekong ASEAN (8T) |
| **FDI thực hiện (giải ngân)** | **21,07 tỷ USD (+12,1%)**, cao nhất 5 năm; chế biến chế tạo 17,4 tỷ (82,6%) | 2025 cả năm **27,62 tỷ (+9%)**, chế biến chế tạo 82,8% | VietnamFinance 03/10; Báo Văn hoá; NSO (2025, qua tìm kiếm) |
| Đồng Nai | FDI 9T **2,5 tỷ USD**, 86% KH năm 3 tỷ; mục tiêu FDI vào KCN/KKT 2026 khoảng 1,5 tỷ | | VietnamPlus (qua tóm tắt tìm kiếm) |
| TP.HCM | "7T hút gần 10 tỷ USD FDI" | chỉ có tiêu đề | qua tóm tắt tìm kiếm, không mở |
| 10T/2026 | **không có số** (chưa công bố tại 01/11) | | — |

**Đọc [UĐ]:**
1. **Đăng ký tăng mạnh nhờ dự án cỡ lớn, không nhờ số dự án.** Quy mô bình quân dự án cấp mới khoảng **9,4 triệu USD** so với khoảng **4,2
   triệu USD** cùng kỳ (ước lượng: 29,24/3.108 vs 12,18/2.927). Dự án cỡ lớn (năng lượng, trung tâm dữ liệu, bán dẫn, có thể có thương vụ
   Luxembourg là một vài khoản lớn) **không chuyển thành nhu cầu đất KCN theo tỷ lệ**: nhiều dự án loại này nằm ngoài KCN tiêu chuẩn hoặc cần
   rất ít ha trên mỗi USD. Không có nguồn tách FDI theo "trong KCN / ngoài KCN" năm 2026.
2. **Giải ngân +12% là chỉ báo thật hơn của nhu cầu xây nhà máy.** Giải ngân đi trước nhu cầu đất của chính dự án đó (dự án thuê đất rồi mới
   giải ngân xây dựng) nhưng đi sau nhu cầu đất của làn sóng dự án tiếp theo khoảng 6-18 tháng [NỀN].
3. Cơ cấu nguồn: Singapore dẫn đầu thường là vốn đi qua (gồm nhà đầu tư TQ và phương Tây qua công ty mẹ Singapore) [NỀN]. **Không tách được**
   tỷ trọng thật của TQ.

### 1b. Thuế Mỹ: khung pháp lý đã đổi trong 2026 [DK]
| Mốc | Sự kiện | Nguồn |
|---|---|---|
| 02/07/2025 | Thoả thuận khung: hàng VN chịu thuế đối ứng **20%**, hàng "trung chuyển" **40%** (định nghĩa chưa công bố) | ACBS, Vietcetera 07/2025 |
| **20/02/2026** | Toà án Tối cao Mỹ (6-3): IEEPA **không cho phép** Tổng thống áp thuế. Thuế đối ứng theo IEEPA mất căn cứ | Cozen O'Connor, Perkins Coie, Thomson Reuters 02/2026 |
| 24/02-24/07/2026 | Thay bằng **Section 122**: 10% toàn cầu, 150 ngày (có nguồn nói 15%; đa số nói 10%) | như trên; Thompson Coburn 09/07/2026 |
| 11/03/2026 | USTR mở điều tra Section 301 về **dư thừa công suất cơ cấu** với 16 nền kinh tế, có VN (VN có thặng dư thương mại lớn, xi măng gần gấp đôi cầu nội địa) | Tuổi Trẻ EN 10/04/2026; Wiley, BHFS 03/2026 |
| 30/04 và 29/05/2026 | VN bị xếp **Priority Foreign Country** (Special 301); USTR mở điều tra Section 301 riêng về **sở hữu trí tuệ** với VN | DFDL 11/08/2026; Thompson Coburn |
| 03/06/2026 | Sắc lệnh ưu tiên cưỡng chế lao động cưỡng bức, khai sai mã, khai thấp giá, **trung chuyển trái phép** | DFDL 11/08/2026 |
| **24/07/2026** | Section 301 (lao động cưỡng bức), áp thêm: **VN 12,5%**, Thái Lan 12,5%, Malaysia/Indonesia/Campuchia 10%, có miễn trừ theo mặt hàng (91 Fed. Reg. 47318) | DFDL 11/08/2026 |
| tới 11/08/2026 | Điều tra dư thừa công suất và điều tra IP **chưa** sinh thêm thuế | DFDL 11/08/2026 |

**Đọc [UĐ]:**
- **Mức** thuế bổ sung chung với hàng VN giảm từ 20% (IEEPA) xuống 12,5% (Section 301). **Chênh lệch với ASEAN** gần như bằng 0 đến +2,5pp. Lợi
  thế tương đối của VN so với ASEAN không còn đến từ thuế, mà từ hệ sinh thái nhà cung cấp, logistics và quỹ đất.
- **Căn cứ** thuế giờ là các cuộc điều tra Section 301 có thể sinh thêm hành động bất kỳ lúc nào. Hai cuộc điều tra **nhắm VN** đang treo. Đây là
  rủi ro "đuôi" với quyết định thuê đất 50 năm của nhà đầu tư sản xuất hướng Mỹ. Bằng chứng gián tiếp: CBRE nói hấp thụ nhà xưởng/kho xây sẵn
  9T **−48%**, lý do chính là **thiếu các giao dịch lớn của DN Trung Quốc** (TBTCVN 15/10/2026). Đây là nhóm nhạy nhất với rủi ro trung chuyển.
- Thuế với Trung Quốc: **không kiểm lại** mức hiện hành trong lượt này. Không suy chênh lệch VN-TQ.

### 1c. Giá thuê và lấp đầy: hai nguồn môi giới, **khác phạm vi, không trộn** [DK]
**Cushman & Wakefield, Vùng KTTĐ phía Nam (TP.HCM mở rộng + Đồng Nai + Tây Ninh), đất KCN:**
| Quý | Cung (ha) | Lấp đầy | Giá chào thuê (USD/m²/chu kỳ thuê) | Hấp thụ ròng | Nguồn |
|---|---|---|---|---|---|
| Q4/2025 | 36.400 (+5,8% QoQ, gần +28% YoY); mới khoảng 2.000 ha từ GĐ1 Bàu Cạn-Tân Hiệp và Xuân Quế-Sông Nhạn (Đồng Nai) | 74% (TP.HCM 84,4 · ĐN 71,6 · TN 58,2) | **185 (+5,11% YoY)** | 45 ha | C&W 28/01/2026 |
| Q1/2026 | khoảng 36.400, không có cung mới | 74,8% (−1,3pp YoY) | 186,6 (+1,7% YoY) | khoảng 127 ha (+59% YoY) | C&W 15/05/2026 |
| **Q2/2026** | **36.063** (ghi "không đổi QoQ", lệch 337 ha so Q1: lỗi số hoặc đổi định nghĩa) | **76,3%** (+2,2pp YoY) | **186,4 (−0,5% QoQ, +1,7% YoY)** | không ghi | C&W 18/08/2026 |
| Q3/2026 | **không có số** C&W (chưa công bố hoặc không tìm thấy) | | | | — |

Theo tỉnh, Q2/2026 (C&W 18/08/2026):
| Tỉnh (địa giới mới) | Lấp đầy đất | Giá đất (USD/m²/chu kỳ) | YoY giá | Nhà xưởng xây sẵn (RBF) lấp đầy / giá USD/m²/tháng |
|---|---|---|---|---|
| TP.HCM | **86,1%** | 187,5 | **+6,8%** | 89,7% / 5,1 |
| Đồng Nai | 73,1% | 189,6 | +1,9% | 94,3% / 4,9 |
| Tây Ninh | **60,9%** | 179,6 | **−6,8%** | 93,7% / 4,6 |
| Toàn vùng | 76,3% | 186,4 | +1,7% | 92,0% / 4,9 (cung 6,85 tr m²) |

Kho xây sẵn (RBW) Q2: cung khoảng 6,6 tr m², lấp đầy 91,6-91,7% (TP.HCM 98,7%), giá khoảng 4,6 USD/m²/tháng (+5,5% YoY).

**CBRE, "thị trường cấp 1" phía Nam (phạm vi không định nghĩa trong bài):**
| Kỳ | Đất: hấp thụ / giá / lấp đầy | Xưởng/kho xây sẵn | Nguồn |
|---|---|---|---|
| H1/2025 | 55 ha (thấp hơn khoảng 1,7 lần bình quân quý Q1/2023-Q1/2025); 179 USD/m²/thời hạn còn lại; lấp đầy 89% | Hấp thụ kho 300 nghìn m², xưởng >400 nghìn m²; giá kho 4,9, xưởng 5,2 | Doanh nghiệp Hội nhập 11/07/2025 (dẫn CBRE) |
| **9T/2026** | **163 ha (+56% YoY)**; **185 USD/m² (đi ngang QoQ, +1,5% YoY)**; lấp đầy đất **không có số** | Hấp thụ **0,5 tr m² (−48%)**; Q3 cung mới >300 nghìn m² (Bình Dương, Đồng Nai cũ); lấp đầy xưởng 88%, kho 80%; giá xưởng 5,2, kho 5,0 | TBTCVN/stockbiz 15/10/2026 |

**Đọc [UĐ]:**
1. **Giá thuê đi ngang danh nghĩa, giảm thực.** Tăng giá YoY rơi từ +5,1% (Q4/2025, C&W) xuống +1,5-1,7% (Q1-Q3/2026, cả hai nguồn). Thấp hơn
   lạm phát USD [NỀN, khoảng 2,5-3%]. Đây là đỉnh phẳng (plateau), không phải giảm giá.
2. **Hấp thụ hồi từ nền thấp.** 2025 có khoảng lặng do thuế Mỹ (CBRE H1/2025 chỉ 55 ha; C&W Q4/2025 45 ha). Số +56% (CBRE 9T) và +59% (C&W Q1)
   là hồi từ nền thấp, chưa phải bùng nổ.
3. **Phân hoá lõi - vệ tinh rõ.** TP.HCM mở rộng lấp đầy 86%, giá +6,8% YoY. Tây Ninh lấp đầy 61%, giá −6,8% YoY. Cung mới đổ về vệ tinh
   (Tây Ninh, Đồng Nai xa) đang làm giá vệ tinh yếu.
4. **Hai nguồn lệch phạm vi.** CBRE (lấp đầy đất 89% năm 2025) và C&W (74-76%) đo hai rổ khác nhau. C&W tính cả KCN mới thành lập chưa có hạ
   tầng (sau sáp nhập cung tăng gần 28% YoY). **Không trừ chéo.**
5. Quy đổi: 185 USD/m² × 25.627 đ/USD (tỷ giá trung tâm 23/10, `sector_read_ngan_hang_20261031.md`) ≈ **4,74 triệu đ/m² ≈ 47 tỷ đ/ha cho cả
   thời hạn thuê** (ước lượng, giá chào, chưa VAT, chưa phí quản lý).

### 1d. Nhà xưởng xây sẵn và dịch chuyển chuỗi cung ứng [DK + UĐ]
- Hấp thụ RBF/RBW 9T **−48%** (CBRE) trong khi đất +56%. Lý do CBRE nêu: vắng giao dịch lớn của DN Trung Quốc; khách hàng hợp nhất vận hành, cân
  nhắc chi phí và thuế kỹ hơn (TBTCVN 15/10/2026).
- C&W vẫn ghi lấp đầy RBF 92%, RBW 91,7% (Q2). Hai nguồn không mâu thuẫn: tồn kho đang được giữ, nhưng **luồng thuê mới** chậm lại.
- Pipeline (C&W): RBF 2026-2028 khoảng 1,1 tr m² (TP.HCM 65%, Tây Ninh 29%, Đồng Nai 6%); RBW >680 nghìn m² (C&W 18/08/2026). 2026-2029 bản Q1:
  RBF khoảng 944 nghìn m², RBW khoảng 661 nghìn m².
- **Đọc [UĐ]:** khách thuê xưởng xây sẵn là DN nhỏ-vừa, phần lớn gốc TQ, sản xuất hướng xuất khẩu Mỹ, ra quyết định nhanh. Nhóm này là **chỉ báo
  sớm nhất** của dịch chuyển chuỗi cung ứng. −48% nói rằng làn sóng "Trung Quốc + 1" ngắn hạn đang **chững**, do rủi ro trung chuyển và điều tra
  Section 301. Khách thuê đất 50 năm (DN lớn Hàn, Nhật, Đài, Singapore, Âu-Mỹ) quyết định chậm hơn và ít nhạy với thuế ngắn hạn hơn. Hai luồng
  ngược chiều này giải thích vì sao đất hồi còn xưởng giảm.

### 1e. Quỹ đất và nút thắt
**Quỹ đất danh nghĩa không thiếu ở cấp vùng.** Đất trống theo C&W Q2/2026 ≈ 36.063 × (1 − 0,763) ≈ **8.550 ha** (ước lượng, gồm cả đất chưa giải
phóng mặt bằng (GPMB) và chưa có hạ tầng). Hấp thụ 2026 khoảng **200-400 ha/năm** (ước lượng từ CBRE 9T 163 ha và C&W Q1 127 ha, hai phạm vi). Kho
danh nghĩa bằng nhiều năm hấp thụ. **Nút thắt thật là đất sạch, có hạ tầng, ở vị trí lõi** (TP.HCM mở rộng lấp đầy 86%), không phải tổng diện tích.

Pipeline cung [DK]:
- C&W: 2026-2029 khoảng **5.347 ha** (TP.HCM 59%, Tây Ninh 24%, Đồng Nai 17%) (15/05/2026); bản Q2: Đồng Nai 3 KCN trọng điểm 2.240 ha; Tây Ninh 49
  KCN khoảng 16.000 ha (quy hoạch); TP.HCM 14 KCN mới 3.833 ha đến 2033 (HEPZA/C&W).
- Đồng Nai khởi công 19/12/2025: Long Đức 3 (244 ha, 1.600 tỷ), Bàu Cạn-Tân Hiệp (1.000 ha GĐ1, >9.250 tỷ), Xuân Quế-Sông Nhạn (1.000 ha GĐ1,
  khoảng 9.000 tỷ), gần sân bay Long Thành; đã kiểm đếm xong đất liên quan **Tổng công ty Cao su Đồng Nai** và hộ dân (KTSG 15/11/2025).

| Nút thắt | Trạng thái as-of [DK trừ khi ghi khác] | Hướng tác động [UĐ] |
|---|---|---|
| **Chủ trương đầu tư** | **Luật Đầu tư 143/2025/QH15** (thông qua 11/12/2025, hiệu lực **01/03/2026**): Chủ tịch UBND tỉnh chấp thuận chủ trương dự án hạ tầng KCN, KCX, khu công nghệ số tập trung, và dự án xin giao/thuê đất không qua đấu giá (lsvn 14/12/2025). NĐ 239/2025 (03/09/2025) sửa NĐ 31/2021 | **Nới cửa cung.** Thủ tục rút ngắn, tỉnh tự quyết. Hệ quả hai mặt: cung mới ra nhanh hơn (tốt cho chủ đầu tư có quỹ đất, xấu cho giá vệ tinh); và tỉnh vừa là người duyệt vừa là chủ sở hữu của tổng công ty KCN tỉnh |
| **Quy hoạch/chỉ tiêu đất** | **QĐ 1177/QĐ-TTg (30/06/2026)** điều chỉnh quy hoạch sử dụng đất quốc gia 2021-2030 (chưa đọc văn bản gốc, không có chỉ tiêu đất KCN miền Nam); NĐ 70/2026 về nội dung quy hoạch SDĐ quốc gia (từ 09/03/2026) | Chỉ tiêu đất KCN được nới cho giai đoạn 2026-2030 là khả năng cao nhưng **không có số** |
| **GPMB, đền bù, bảng giá đất** | Luật Đất đai 2024: bảng giá đất **ban hành hằng năm từ 01/01/2026**. TP.HCM: NQ 87/2025/NQ-HĐND áp dụng 01/01/2026, khu vực Bình Dương và BR-VT cũ tăng mạnh hơn trung tâm cũ. Đồng Nai (dự thảo): đất ở đô thị tăng bình quân **3,6 lần** (1,6-9 lần), đất nông nghiệp ven đường **1,1-2,2 lần**; chưa xác nhận đã ban hành | **Chi phí đền bù đất mới tăng**, chủ yếu ở đất nông nghiệp vệ tinh (×1,1-2,2 theo dự thảo Đồng Nai). Giá thuê đi ngang (+1,5%) trong khi chi phí đất đầu vào tăng ⇒ **biên của dự án mới bị ép** |
| **Tiền thuê đất nộp NN** | NQ 254/2025/QH15 và **NĐ 50/2026/NĐ-CP** (31/01/2026) tháo gỡ tiền sử dụng đất, tiền thuê đất; CV 1649/CT-CS và CV 1965/CT-CS (02/04/2026) hướng dẫn. Diện tích hạ tầng dùng chung trong KCN không phải nộp tiền thuê đất | Chủ đầu tư thuê đất **trả tiền hằng năm** chịu tác động của bảng giá đất hằng năm. Chi tiết theo Điều 13 NĐ 50 **chưa đọc** |
| **Luật Đất đai sửa đổi** | Dự thảo sửa khoảng 65 điều; nếu QH thông qua kỳ họp Q4/2026 thì hiệu lực **01/03/2027**; có đề xuất bỏ định giá đất cụ thể theo thị trường (23/07/2026), thu hồi dự án chậm triển khai quá 60 tháng (ACBS 05/2026, báo chí) | Nếu bỏ định giá theo thị trường thì đền bù dễ tính hơn, nhanh hơn. Rủi ro thu hồi dự án chậm triển khai với quỹ đất "treo" |
| **Hạ tầng giao thông** | **Long Thành GĐ1:** bay thử 15/12/2025, chuyến bay khai trương 19/12/2025; ACV chốt **khai thác thương mại từ 01/12/2026** (14/07/2026), vận hành thử T9-T11/2026; 01/12/2026-27/03/2027 khuyến khích bay quốc tế gồm hàng hoá; từ mùa Hè 2027 đề xuất chuyển toàn bộ quốc tế đường dài gồm hàng hoá sang Long Thành; giảm 20-50% giá dịch vụ giai đoạn đầu. **Vành đai 3:** cầu cạn 14,7 km thông xe kỹ thuật 19/12/2025, mục tiêu toàn tuyến 30/06/2026, **không xác nhận đã đạt**. **Biên Hòa-Vũng Tàu:** GĐ1 dự kiến 30/03/2026, một nguồn nói khai thác tạm từ 05/2026, đồng bộ cuối Q3/2026, **chưa xác nhận**. **Vành đai 4:** khoảng 207 km, GĐ1 khoảng 120.412 tỷ, gói qua Đồng Nai khởi công khoảng 30/09/2026, Tây Ninh 15/10/2026, mục tiêu cuối 2028 (sector read đá 30/10). Bến Lức-Long Thành: **không xác nhận** | Hạ tầng **mở hành lang mới** (Long Thành, VĐ3/VĐ4, cảng Cái Mép-Thị Vải) cho KCN Đồng Nai và TP.HCM phía Đông. Lợi ích về giá thuê đến **sau** khi tuyến thông thật. Hầu hết mốc 2026 chưa xác nhận đã đạt ⇒ phần "kỳ vọng hạ tầng" đã có trong giá chào nhưng chưa có trong hấp thụ [UĐ] |
| **Ưu đãi thuế** | Thuế tối thiểu toàn cầu áp từ 2024; Quỹ hỗ trợ đầu tư (NĐ 182/2024); Luật thuế TNDN mới (2025) [NỀN, chưa kiểm lại]. CBRE 07/2025: thay đổi ưu đãi TNDN H2/2025 có thể làm giảm sức cạnh tranh | Công cụ "miễn thuế" để hút FDI lớn yếu đi; cạnh tranh chuyển sang chất lượng hạ tầng, điện, ESG |
| **Điện, nước, lao động** | **Không có số** 2026 cho miền Nam trong lượt này | Khoảng trống dữ liệu, không suy |

### 1f. Chi phí vốn / thanh khoản: bảng 5 tầng (as-of 26-31/10/2026; tái dùng, không đo mới)
Nguồn: `sector_read_ngan_hang_20261031.md` mục 1c và CSV nội bộ tới 26/10. Không có ô nào đo mới trong lượt này.
| Tầng | Ô | Số | Nguồn · ngày |
|---|---|---|---|
| **A. Niêm yết hành chính** | Big-4 12M online / tại quầy | **6,8%** không đổi / 5,9% → 5,4% sau CV 9608 | CSV 26/10 (CafeF 24/10, VietNamNet 22/10); log 26/10 |
| | Big-4 6M online / quầy | 6,6% / 3,5% (12/10); sau 18/10 **không có số** | bank read 31/10 |
| **B. Bán-hành-chính** | CCTG Big-4 12M (BIDV/VietinBank) / VCB 6M | **7,4%** / 7,5% (12/10); sau CV 9608 **không có số** | CSV 12/10 |
| | Spread CCTG 12M − TK online 12M | +0,6pp (12/10) | tự tính |
| **C. Ngoài Big-4** | 12M thực trả BQ / tư nhân 6M / tiền gửi lớn | khoảng 8,45% / 9,5-9,7% / 10% (1 NH nhỏ); 1 nguồn | bank read 31/10 |
| **D. Thị trường** | Liên NH 22/10 | ON 4,31 · 1M 5,11 · 3M 6,93 | TBTC 24/10 |
| | OMO | hút ròng 9.868 tỷ tuần 19-23/10; lưu hành 95.065 tỷ | TBTC 24/10 |
| | TPCP 10Y | 4,43% cuối T9, phiên 07/10 dư cầu (không phải Kho bạc neo giá) | Báo Đấu thầu 10/10 |
| | USD/VND | trung tâm 25.627; VCB bán 26.020; tự do 26.000-26.080 | TBTC 24/10 |
| **E. Lượng** | Tín dụng vs huy động (NSO 28/09, cùng nguồn) | 10,89% vs 9,78% | TC KT-TC 05/10 |
| | LDR | khoảng 114% (27 NH niêm yết Q2) | Mekong ASEAN 08/2026 |
| | Văn bản | TT 50/2026 (LDR 85→95% từ 01/12), CV 9608 (18/10), CV 9736 (21/10) | bank read 31/10 |
| (bổ sung) | Lãi cho vay BQ giao dịch mới | **9,12%** (30/09), +1,03pp YTD | bank read 31/10 |

**Đọc cho KCN [UĐ]:** **hướng** chi phí vốn biên đang tăng (tầng C và D, lãi cho vay mới +1pp YTD) trong khi tầng A đi ngang do bị neo hành chính.
**Mức** vốn vay VND thật của chủ đầu tư KCN tư nhân nằm khoảng 9-11% (ước lượng, không có số hợp đồng). Ngành KCN **ít nhạy** lãi suất ở phía cầu
(khách FDI tự tài trợ, trả USD), nhưng **nhạy** ở phía cung: GPMB tốn tiền mặt VND trước 2-4 năm so với dòng tiền khách trả. Độ tin cậy trung bình.

## 2. Cấu trúc cạnh tranh, mô hình doanh thu, tính lumpy

### 2a. Người chơi ở miền Nam [phần lớn NỀN, chưa kiểm thị phần 2026]
| Nhóm | Đặc điểm | Ghi chú |
|---|---|---|
| **Tổng công ty KCN của tỉnh/TP (nhà nước giữ chi phối)** | Becamex (TP.HCM, từ Bình Dương cũ), Sonadezi và Tín Nghĩa (Đồng Nai), IPC/Tân Thuận và các đơn vị của TP.HCM cũ | Quỹ đất lớn được giao từ sớm; quan hệ với chính quyền; thường kiêm BĐS đô thị và tiện ích (nước, xử lý nước thải). Từ 01/03/2026 chính quyền tỉnh **duyệt chủ trương** cho chính tổng công ty mình sở hữu |
| **Nhóm gắn tập đoàn/tổng công ty trung ương** | Tập đoàn Công nghiệp Cao su VN và các công ty con chuyển đất cao su sang KCN; IDICO (gốc Bộ Xây dựng); Viglacera (chủ yếu phía Bắc) | Tập đoàn cao su đã được duyệt chuyển khoảng **23.500-25.000 ha** đất cao su sang đất công nghiệp, gần 11.000 ha đang triển khai ở Tây Ninh, Bình Dương, Đồng Nai, BR-VT [DK qua tóm tắt tìm kiếm, nguồn đầu 2025, không mở bài]. KCN Đồng Nai khởi công 12/2025 dùng đất của Tổng công ty Cao su Đồng Nai (KTSG 15/11/2025) |
| **Liên doanh với nhà đầu tư nước ngoài** | VSIP (Sembcorp + Becamex), Amata (Đồng Nai), các nhà phát triển Nhật/Hàn | Bán hàng bằng mạng lưới khách quốc tế; giá cao hơn bình quân |
| **Tư nhân trong nước** | Nhiều chủ đầu tư 1-3 KCN ở Long An cũ, Tây Ninh, Bình Dương cũ | Phụ thuộc vay ngân hàng cho GPMB; nhạy với lãi suất và chậm bán |
| **Nền tảng nhà xưởng/kho xây sẵn** | BW, KCN Vietnam, Logos, ESR, SLP, Frasers... | Thuê lại đất trong KCN, cho thuê theo tháng (doanh thu định kỳ, không lumpy) |

**Đọc [UĐ]:** cạnh tranh đang chuyển từ "ai có đất" sang "ai có đất sạch, có hạ tầng hoàn thiện, điện ổn định, chuẩn ESG, gần cảng/sân bay". C&W
(Q1/2026) nói thẳng: "Land availability alone is no longer sufficient to attract tenants" (The Investor 25/05/2026). Lợi thế giá rẻ ở vệ tinh (Tây
Ninh) bị bù bằng giá thuê đang giảm.

### 2b. Kinh tế của một dự án KCN [NỀN, khung chung, không có số 2026]
1. Xin chủ trương → quy hoạch 1/2000, 1/500 → thu hồi/đền bù/GPMB (chậm nhất, 1-4 năm) → giao/cho thuê đất, nộp tiền thuê đất (một lần hoặc
   hằng năm) → xây hạ tầng → ký MOU/đặt cọc với khách → ký hợp đồng thuê lại đất → bàn giao → khách xây nhà máy → phí quản lý, nước, xử lý nước
   thải suốt đời dự án (thời hạn KCN thường 50 năm, có nơi 70 năm).
2. Dòng tiền: khách thường trả **trước phần lớn** giá thuê cả chu kỳ (đặt cọc khi ký MOU/biên bản ghi nhớ, phần lớn khi ký hợp đồng, phần còn lại
   khi bàn giao). Tỷ lệ cụ thể khác nhau theo chủ đầu tư.
3. Chi phí chính: đền bù GPMB (tăng theo bảng giá đất hằng năm từ 2026), tiền thuê đất nộp Nhà nước, hạ tầng nội khu, lãi vay thời kỳ GPMB.
4. Tỷ lệ đất thương phẩm trên tổng diện tích KCN khoảng 65-75% [NỀN]. Giá chào C&W/CBRE là trên m² đất thương phẩm.

### 2c. Ghi nhận doanh thu: đã đổi từ 01/01/2026 [DK một nguồn báo + quy định chung; **chưa đọc nguyên văn điều khoản**]
- **Trước 2026 (TT 200/2014):** doanh nghiệp được chọn **ghi nhận một lần** toàn bộ tiền thuê nhận trước của hợp đồng 50 năm khi bàn giao (nếu thoả
  các điều kiện của chế độ kế toán [NỀN: bên thuê không được huỷ ngang, đã trả trước phần lớn, ước tính được giá vốn]), **hoặc phân bổ** theo thời
  hạn thuê. Phần lớn chủ đầu tư KCN chọn ghi nhận một lần tính tới 31/12/2025 (Cafeland/Đầu tư Chứng khoán 07/04/2026).
- **Từ 01/01/2026 (TT 99/2025/TT-BTC, ban hành 27/10/2025):** "doanh thu từ hoạt động cho thuê tài sản nhận trước nhiều kỳ phải được phân bổ theo
  thời hạn thuê" (bài báo trích; tài liệu ĐHĐCĐ 2026 của một tổng công ty KCN tỉnh dùng cùng cách hiểu và nói việc này "sẽ dẫn đến việc ghi nhận
  doanh thu mảng BĐS KCN" giảm mạnh, kéo LNST và **số nộp ngân sách** giảm). Hỏi đáp BTC (14/05/2026) nêu nguyên tắc chung: doanh thu phân bổ theo
  giá trị hợp lý của từng nghĩa vụ, chỉ ghi nhận khi nghĩa vụ đã thực hiện.
- **Chưa biết:** quy định chuyển tiếp cho hợp đồng ký trước 2026 và phần đã ghi nhận một lần; có ngoại lệ cho "cho thuê lại đất gắn hạ tầng" hay
  không; cách kê khai thuế TNDN (luật thuế có thể vẫn cho kê một lần [NỀN]); có công văn BTC nào trả lời kiến nghị hiệp hội (tìm kiếm 01/11 **không
  thấy**).
- **Hệ quả cơ học [UĐ]:** với hợp đồng còn khoảng 40-45 năm thời hạn, doanh thu ghi nhận mỗi năm chỉ còn khoảng **2-2,5%** giá trị hợp đồng thay vì
  khoảng 100% ở năm bàn giao (ước lượng). Tiền mặt không đổi. Doanh thu chưa thực hiện dài hạn phình ra. LNST kế toán 2026 của nhóm từng ghi nhận
  một lần sẽ **giảm mạnh theo cơ chế**, không phải do kinh doanh xấu đi. Lợi nhuận chia được (theo VAS) giảm trong khi tiền mặt dư thừa: cổ tức tiền
  bị giới hạn bởi lợi nhuận chưa phân phối chứ không bởi tiền.
- **Ghi chú cho Mike (dữ liệu, không phải khuyến nghị):** mọi chỉ báo dựa trên lợi nhuận kế toán (1/PE, ROE, tăng trưởng EPS, SUE/PEAD) của chủ
  đầu tư KCN có thể có **gãy cấu trúc từ BCTC 2026** do đổi chế độ kế toán, không do đổi kinh doanh. So sánh PE 2025 với 2026, hay xếp hạng chéo
  KCN với ngành khác, có thể sai hệ thống. Đây là phát hiện để báo, tôi không sửa gì. Độ tin cậy **trung bình** (chưa đọc nguyên văn TT 99, chưa
  biết điều khoản chuyển tiếp).

### 2d. Tính lumpy [UĐ trên nền NỀN]
- **Trước 2026:** doanh thu dồn vào quý **bàn giao** đất, không phải quý ký hợp đồng. Bàn giao phụ thuộc GPMB và lịch xây nhà máy của khách, nên doanh
  thu quý có thể dao động hàng trăm phần trăm. Số "diện tích ký mới" (MOU vs hợp đồng) mới là chỉ báo cầu, không phải doanh thu quý.
- **Từ 2026:** doanh thu mới **mượt** nhưng **nhỏ**. Phần lumpy chuyển sang **dòng tiền** (người mua trả tiền trước, doanh thu chưa thực hiện) và
  các khoản một lần khác: **đền bù khi giao đất cao su cho KCN** (nhóm gắn tập đoàn cao su), thanh lý vườn cây, chuyển nhượng dự án/cổ phần, bán đất
  nhà ở đô thị kèm KCN.
- **Hệ quả cho người đọc số:** đánh giá chủ đầu tư KCN 2026+ phải nhìn **diện tích ký mới, tiền khách trả trước, doanh thu chưa thực hiện** thay vì
  doanh thu/LNST.

### 2e. Nhóm gắn doanh nghiệp nhà nước: cơ chế riêng [DK + UĐ]
- **NQ 79-NQ/TW (06/01/2026)** về phát triển kinh tế nhà nước; Ban Chỉ đạo quốc gia (QĐ 204/QĐ-TTg, 31/01/2026); **QĐ 40/2026/QĐ-TTg** tiêu chí
  phân loại DN để cơ cấu lại vốn nhà nước, hiệu lực **05/08/2026**; kế hoạch cơ cấu lại vốn 2026-2030 phải hoàn thành **trước 31/08/2026**. Phần vốn
  nhà nước ≤ 50% vốn điều lệ được chuyển giao cho DN có chức năng đầu tư vốn nhà nước hoặc DN nhà nước cùng ngành (TBTCVN, lsvn 2026; tóm tắt tìm
  kiếm). **Không thấy** nội dung riêng cho các tổng công ty KCN.
- **Đọc [UĐ]:** (1) việc phân loại quyết định tổng công ty KCN nào nhà nước giữ chi phối, giữ dưới 50% hay thoái. Thoái vốn tạo cung cổ phiếu và
  có thể đổi chủ sở hữu thực. (2) Nhóm nhà nước tỉnh có lợi thế thủ tục từ 01/03/2026, đồng thời có **xung đột lợi ích** (tỉnh duyệt và sở hữu).
  (3) TT 99/2025 làm giảm **lợi nhuận nộp ngân sách** của nhóm này, nên có động cơ chính trị để xin ngoại lệ (nhóm có tiếng nói mạnh nhất). Đây là
  con đường khả dĩ nhất để quy định đảo lại, nhưng tôi không thấy tín hiệu nào đến 01/11 (FORECAST F9).
  (4) Nhóm gắn tập đoàn cao su có nguồn thu một lần **đền bù đất** khi bàn giao đất cho KCN (kể cả KCN của chủ đầu tư khác). Tính lumpy và
  phụ thuộc quyết định thu hồi đất của tỉnh. Có nguồn CTCK lưu ý đền bù có thể chuyển sang **hợp tác dài hạn** thay vì tiền một lần.

## 3. Phân loại chế độ ngành

Hai lớp cần tách: **thị trường vật lý** (ha, USD/m², lấp đầy) và **lợi nhuận kế toán** của chủ đầu tư niêm yết.

| Nhãn | Xác suất | Lý do |
|---|---|---|
| **ADMIN_GATED** | **0,40** | Cung, chi phí và doanh thu ghi nhận đều do văn bản quyết: chủ trương do tỉnh duyệt từ 01/03/2026 (Luật 143/2025); chỉ tiêu đất (QĐ 1177/2026); bảng giá đất hằng năm từ 2026 (đền bù, tiền thuê đất); NĐ 50/2026; **TT 99/2025 đổi cách ghi nhận doanh thu**; Luật Đất đai sửa đổi đang chờ QH; NQ 79 và QĐ 40 phân loại vốn nhà nước. Phía cầu có một cửa hành chính **bên ngoài**: Section 301 (12,5% từ 24/07/2026, hai cuộc điều tra nhắm VN đang treo). Với **lợi nhuận kế toán 2026+**, lớp này áp đảo |
| **CYCLICAL** | **0,40** | Cầu đi theo chu kỳ capex sản xuất toàn cầu và làn sóng dịch chuyển: bùng 2021-2024, chững 2025 do thuế, hồi 2026 từ nền thấp (đất +56% CBRE 9T) nhưng giá thuê đi ngang (+1,5-1,7% YoY, từ +5,1%); cung đuổi kịp (gần +28% YoY cung C&W cuối 2025, 5.347 ha pipeline 2026-2029); xưởng xây sẵn hấp thụ −48%. Với **thị trường vật lý**, lớp này áp đảo |
| **STRUCTURAL** | **0,20** | Mô hình tăng trưởng FDI-chế tạo của VN (82,6% vốn FDI giải ngân vào chế biến chế tạo; giải ngân cao nhất 5 năm). Đất lõi gần TP.HCM khan hiếm thật (86%, giá +6,8%). Phía xấu cấu trúc: lợi thế thuế so với ASEAN đã gần bằng 0; thuế tối thiểu toàn cầu làm yếu công cụ ưu đãi; chi phí đền bù tăng cấu trúc theo bảng giá đất hằng năm |

- **Pha [UĐ]:** thị trường vật lý ở **giữa chu kỳ, pha cung đuổi kịp cầu**: hấp thụ hồi, giá phẳng, cung mới dồn về vệ tinh. Không phải đỉnh như
  2022-2024. Không phải suy giảm. Lợi nhuận kế toán ở **pha gãy chế độ** (2026 là năm đầu TT 99).
- **Phân hoá [UĐ]:**
  - **Lõi TP.HCM mở rộng và Đông Đồng Nai gần Long Thành/Cái Mép**: STRUCTURAL + CYCLICAL, tốt hơn trung bình nếu có đất sạch.
  - **Vệ tinh xa (Tây Ninh gồm Long An cũ, Bình Phước cũ)**: CYCLICAL, đang chịu cung thừa (lấp đầy 61%, giá −6,8% YoY).
  - **Nhóm gắn nhà nước**: ADMIN_GATED nặng nhất (phân loại vốn, thủ tục, đền bù đất cao su, TT 99 và nghĩa vụ ngân sách).
  - **Nhà xưởng/kho xây sẵn**: CYCLICAL, nhạy nhất với rủi ro trung chuyển và DN TQ; kho logistics gắn tiêu dùng nội địa ổn định hơn.
- **Confidence: `ambiguous` (~55/45).** Phần chưa biết lớn nhất: (a) nguyên văn và điều khoản chuyển tiếp của TT 99 với cho thuê lại đất KCN; (b) kết
  quả hai cuộc điều tra Section 301 nhắm VN; (c) bao nhiêu phần FDI đăng ký tăng vọt là nhu cầu đất KCN thật; (d) số Q3/2026 của C&W và lấp đầy
  đất của CBRE.
- **Liên hệ nền vĩ mô:** REGIME READ #2 / MACRO UPDATE 14/10 giữ Loại-1 STRUCTURAL_ACCUMULATION BĐS (ambiguous). KCN liên quan **gián tiếp**: khách FDI
  không dùng tín dụng VND; nhưng chủ đầu tư vay VND cho GPMB, và nhiều chủ đầu tư kiêm BĐS nhà ở. Kịch bản B (đóng băng thanh khoản BĐS cục bộ,
  20-25%) làm hại mảng nhà ở của họ và làm vốn vay đắt hơn, không làm hại trực tiếp cầu thuê đất FDI.

## 4. FORECAST KHOÁ TRƯỚC (lập 2026-11-01; chấm bằng nguồn công bố đầu tiên ≤ ngày chấm; không có nguồn ⇒ ghi "không chấm được", không suy)

| # | Mệnh đề | P | Ngày chấm | Nguồn chấm |
|---|---|---|---|---|
| F1 | NSO: **FDI thực hiện cả năm 2026 ≥ 29,5 tỷ USD** (2025: 27,62; 9T/2026 21,07, +12,1%) | 0,80 | 2027-01-10 | NSO báo cáo KT-XH T12/2026 |
| F2 | NSO/Cục ĐTNN: **FDI đăng ký cả năm 2026 ≥ 58 tỷ USD** (9T 50,36) | 0,75 | 2027-01-10 | như F1 |
| F3 | C&W Vùng KTTĐ phía Nam, đất KCN: **giá chào thuê bình quân Q4/2026 tăng < +4,0% YoY** (Q4/2025: 185 USD/m²/chu kỳ ⇒ < 192,4) | 0,80 | 2027-02-28 | C&W MarketBeat Q4/2026 |
| F4 | C&W như F3: **lấp đầy đất KCN Q4/2026 ≥ 75,0%** (Q2: 76,3%) | 0,60 | 2027-02-28 | như F3 |
| F5 | C&W như F3: **giá đất TP.HCM (mở rộng) Q4/2026 tăng YoY cao hơn mức tăng YoY bình quân toàn vùng** (phân hoá lõi/vệ tinh giữ) | 0,65 | 2027-02-28 | như F3 |
| F6 | CBRE: **hấp thụ đất công nghiệp phía Nam (thị trường cấp 1) cả năm 2026 ≥ 200 ha** (9T 163) | 0,70 | 2027-02-28 | CBRE (qua TBTCVN/stockbiz hoặc bản gốc) |
| F7 | CBRE: **hấp thụ xưởng + kho xây sẵn phía Nam cả năm 2026 giảm YoY** (9T −48%) | 0,85 | 2027-02-28 | như F6 |
| F8 | **Long Thành GĐ1 có khai thác thương mại thường lệ** (lịch bay thương mại định kỳ, không tính bay thử/khai trương 12/2025) bắt đầu trước hoặc vào 31/12/2026 | 0,70 | 2027-01-05 | ACV / Cục Hàng không. Ghi chú: sector read đá 30/10 F1 hỏi "chuyến bay thương mại đầu tiên" P=0,65, mệnh đề khác |
| F9 | **Không có** văn bản BTC (thông tư sửa TT 99 hoặc công văn hướng dẫn chung) cho phép chủ đầu tư KCN **ghi nhận một lần** lại doanh thu cho thuê lại đất trả trước, ban hành trước 2027-06-30 | 0,75 | 2027-06-30 | BTC / thuvienphapluat |
| F10 | Quốc hội **thông qua Luật Đất đai (sửa đổi)** trước 2026-12-31 | 0,70 | 2027-01-05 | Quốc hội (quochoi.vn). Cùng mệnh đề với sector read BĐS phía Bắc 31/10 (P=0,70), giữ nhất quán |
| F11 | Mức thuế bổ sung chung của Mỹ với hàng VN (ngoài MFN, ngoài Section 232 và AD/CVD theo mặt hàng) **có hiệu lực ngày 2027-03-31 ≤ 15%** (hiện 12,5%) | 0,65 | 2027-03-31 | USTR / Federal Register / CBP |
| F12 | USTR công bố **hành động thuế** theo cuộc điều tra Section 301 dư thừa công suất **hoặc** điều tra IP, có áp lên hàng VN, trước 2027-04-30 | 0,40 | 2027-04-30 | USTR / Federal Register |
| F13 | NSO: **FDI thực hiện Q1/2027 tăng ≥ +5% YoY** (Q1/2026: 5,41 tỷ, +9,1%) | 0,70 | 2027-04-10 | NSO báo cáo Q1/2027 |

Lý do chính: F1 chỉ cần Q4/2026 ≥ 8,43 tỷ (Q4/2025 khoảng 8,82 tỷ suy từ số cả năm trừ 9T, ước lượng), tức không giảm quá khoảng 4%. F2 cần Q4 ≥ 7,6
tỷ (Q4/2025 khoảng 9,9 tỷ, ước lượng). F3 dựa trên 3 quý liên tiếp +1,5-1,7%. F4 nghiêng nhẹ: hấp thụ hồi, nhưng cung mới vệ tinh có thể kéo tỷ lệ xuống
khi được ghi nhận. F6 cần Q4 ≥ 37 ha. F7 cần Q4 bù gần 0,5 tr m², khó. F8 dựa trên mốc ACV đã chốt và các đợt vận hành thử, rủi ro là trượt vài tuần.
F9 dựa trên việc không thấy tín hiệu nào sau 10 tháng áp dụng. F11/F12 dựa trên việc thuế Mỹ hiện đi qua điều tra Section 301 (chậm, có quy trình) và hai
cuộc điều tra treo.

## 5. Chỉ báo dẫn dắt (theo dõi tháng/quý)
1. FDI tháng (Cục ĐTNN/NSO, đầu tháng sau): **giải ngân**, vốn cấp mới chế biến chế tạo, số dự án mới, nguồn TQ/HK/Singapore; FDI theo tỉnh (TP.HCM,
   Đồng Nai, Tây Ninh).
2. Báo cáo môi giới quý (C&W, CBRE, Savills, JLL): hấp thụ đất (ha), giá chào theo tỉnh, lấp đầy, cung mới; hấp thụ xưởng/kho xây sẵn.
3. Thuế Mỹ: Federal Register/USTR về Section 301 (dư thừa công suất, IP Việt Nam), quy tắc trung chuyển/xuất xứ, Section 232 mở rộng.
4. Văn bản trong nước: hướng dẫn hoặc sửa TT 99 với cho thuê lại đất KCN; Luật Đất đai sửa đổi (kỳ họp cuối 2026) và nghị định hướng dẫn; bảng giá đất
   2027 của TP.HCM, Đồng Nai, Tây Ninh (ban hành cuối 2026); quyết định chủ trương KCN mới của UBND tỉnh (từ 01/03/2026); phân loại vốn nhà nước theo
   QĐ 40/2026.
5. Hạ tầng: Long Thành khai thác thương mại 01/12/2026; xác nhận thông xe VĐ3, Biên Hòa-Vũng Tàu, Bến Lức-Long Thành; tiến độ VĐ4.
6. Tầng D/E bảng 5 tầng: lãi cho vay BQ mới, liên NH 3M; tỷ giá USD/VND (giá thuê bằng USD, chi phí bằng VND).

## 6. DD cần kiểm gì (một chủ đầu tư hạ tầng KCN bất kỳ ở miền Nam; số lấy từ BCTC/BCTN/thuyết minh/hồ sơ pháp lý)

**A. Quỹ đất (con số quan trọng nhất)**
1. **Đất thương phẩm còn lại theo từng KCN (ha)**, tách theo **trạng thái pháp lý**: (i) đã có quyết định giao/cho thuê đất và đã GPMB xong; (ii) đã có
   chủ trương, đang GPMB (tỷ lệ % đã đền bù); (iii) mới có quy hoạch. Chỉ (i) là hàng bán được trong 12-24 tháng. Không có bảng tách ⇒ ghi khoảng
   trống, không suy.
2. Vị trí từng KCN theo **lõi/vệ tinh** (TP.HCM mở rộng, Đông Đồng Nai gần Long Thành/Cái Mép, Tây Ninh/Long An cũ, Bình Phước cũ) và khoảng cách tới
   cảng, sân bay, nút VĐ3/VĐ4.
3. Lấp đầy từng KCN so với bình quân tỉnh (C&W Q2/2026: TP.HCM 86,1%, Đồng Nai 73,1%, Tây Ninh 60,9%).
4. Thời hạn còn lại của từng KCN (năm); KCN còn dưới 30 năm thì giá trị mỗi m² cho thuê mới thấp hơn.
5. Đất "treo" hoặc chậm triển khai có nguy cơ bị thu hồi (dự thảo Luật Đất đai sửa đổi: quá 60 tháng).

**B. Bán hàng và giá**
6. **Diện tích ký mới theo quý (ha)**, tách **MOU/đặt cọc** vs **hợp đồng thuê lại đất** vs **đã bàn giao**, 8-12 quý. Tỷ lệ chuyển MOU thành hợp đồng.
7. **Giá thuê thực đạt (USD/m²/chu kỳ)** của hợp đồng ký mới so với giá chào môi giới (khoảng 180-190 USD toàn vùng). Chiết khấu cho khách lớn.
8. **Cơ cấu khách thuê:** quốc tịch (đặc biệt TQ/HK/Singapore-gốc TQ), ngành, tỷ trọng sản xuất hướng xuất khẩu Mỹ; 5 khách lớn nhất / diện tích ký mới.
9. Khách huỷ MOU, chậm thanh toán, đòi giãn tiến độ trong 2025-2026 (giai đoạn thuế Mỹ).

**C. Ghi nhận doanh thu và dòng tiền (TT 99)**
10. **Chính sách kế toán** trong thuyết minh BCTC 2026: ghi nhận một lần hay phân bổ; có điều chỉnh hồi tố số liệu 2025 không; cách xử lý hợp đồng ký
    trước 2026 chưa bàn giao.
11. **Doanh thu chưa thực hiện (ngắn và dài hạn)** và **người mua trả tiền trước**: số dư và biến động quý. Từ 2026 đây là chỉ báo bán hàng chính.
12. **CFO vs LNST** 8 quý; tiền thu từ khách so với doanh thu ghi nhận. Chênh lệch lớn là bình thường dưới TT 99, phải giải thích được.
13. Kê khai thuế TNDN với tiền thuê nhận trước (một lần hay phân bổ): thuế hoãn lại, rủi ro truy thu.
14. Lợi nhuận chưa phân phối so với tiền mặt: cổ tức tiền bị giới hạn bởi lợi nhuận kế toán.

**D. Chi phí đất và vốn**
15. **Chi phí đền bù/GPMB thực tế (đ/m²)** của dự án đang làm, so với giá thuê quy đổi (khoảng 4,7 triệu đ/m² cho cả chu kỳ ở giá chào bình quân); độ nhạy
    với bảng giá đất 2026-2027 (dự thảo Đồng Nai: đất nông nghiệp ×1,1-2,2).
16. **Hình thức thuê đất với Nhà nước**: trả tiền một lần hay hằng năm; nếu hằng năm thì đơn giá điều chỉnh theo bảng giá đất hằng năm, khoản phải nộp
    tăng bao nhiêu; miễn giảm theo NĐ 103/2024 và NĐ 50/2026.
17. Ứng trước cho tổ chức phát triển quỹ đất / hội đồng bồi thường, chi phí SXKD dở dang (BĐS dở dang), tuổi của các khoản này; khoản ứng không có
    tiến độ là cờ vàng.
18. Nợ vay/VCSH, lãi suất vay thực tế, kỳ hạn; lãi vay vốn hoá; nợ đến hạn 12 tháng so với tiền và tiền khách trả trước.
19. Phải trả nhà thầu hạ tầng; capex hạ tầng còn phải làm cho phần đất đã cho thuê (nghĩa vụ chưa thực hiện).

**E. Doanh thu định kỳ**
20. Phí quản lý, cấp nước, xử lý nước thải, điện (nếu có), cho thuê xưởng/kho xây sẵn: doanh thu, biên, tỷ lệ lấp đầy xưởng (so 88-92% của thị trường).

**F. Quản trị, nhà nước, pháp lý**
21. **Cơ cấu sở hữu nhà nước** (%), DN thuộc nhóm nào theo QĐ 40/2026, kế hoạch thoái/chuyển giao vốn 2026-2030; lịch bán vốn của cổ đông nhà nước.
22. Giao dịch bên liên quan với công ty mẹ/tổng công ty/tập đoàn (mua đất, trả đền bù đất cao su, cho vay, góp vốn KCN của nhau); nghĩa vụ nộp ngân sách
    và cổ tức tối thiểu theo yêu cầu chủ sở hữu.
23. Với nhóm gắn tập đoàn cao su: diện tích đất cao su có quyết định thu hồi, **đền bù bằng tiền một lần hay hợp tác dài hạn**, tiến độ thu tiền.
24. Thanh tra, kiểm toán nhà nước, kết luận sai phạm đất đai; tranh chấp đền bù với dân; dự án bị dừng.
25. Mảng ngoài KCN (BĐS nhà ở, đô thị, hạ tầng giao thông BOT): tỷ trọng tài sản và nợ; đây là kênh lây Kịch bản B của nền vĩ mô.
26. Kiểm toán: ý kiến ngoại trừ/nhấn mạnh; chênh lệch LNST trước/sau kiểm toán; thay đổi kiểm toán viên 2025-2026.

## 7. Điều gì làm tôi sai
- **Cầu xấu hơn tôi nghĩ:** USTR áp thêm thuế từ điều tra dư thừa công suất hoặc IP lên VN; FDI giải ngân Q4/2026 giảm YoY; C&W Q3-Q4 cho giá đất toàn vùng
  giảm QoQ; lấp đầy giảm dưới 74% khi cung vệ tinh được ghi nhận.
- **Tốt hơn tôi nghĩ:** FDI đăng ký cấp mới chuyển thành hợp đồng thuê đất nhanh (hấp thụ Q4 > 100 ha theo CBRE); Long Thành và VĐ3 vận hành đúng hạn và
  kéo giá Đông Đồng Nai; BTC cho phép ghi nhận một lần lại (đảo lớp ADMIN_GATED về lợi nhuận).
- **Lỗi dữ liệu có thể có:** C&W và CBRE khác phạm vi; C&W cung Q2 lệch Q1 337 ha mà vẫn ghi "không đổi"; địa giới mới làm số 2026 không so được với chuỗi tỉnh
  cũ; nguyên văn TT 99 về cho thuê lại đất và điều khoản chuyển tiếp **chưa đọc**; thuế Section 301 12,5% chỉ từ một hãng luật (dẫn Federal Register); diện
  tích đất cao su được duyệt chuyển đổi là số đầu 2025 qua tóm tắt tìm kiếm; trạng thái thông xe VĐ3, Biên Hòa-Vũng Tàu chưa xác nhận.

## Nguồn (ngày công bố)
- TBTCVN, "Bất động sản công nghiệp phía Nam hấp thụ 163 ha đất trong 9 tháng" (CBRE) — 15/10/2026: https://thoibaotaichinhvietnam.vn/bat-dong-san-cong-nghiep-phia-nam-hap-thu-163-ha-dat-trong-9-thang-205377.html ; bản EN stockbiz: https://stockbiz.vn/en/news/southern-industrial-property-absorbs-163-hectares-of-land-in-9-months/42287840
- Cushman & Wakefield, "Southern Vietnam industrial real estate maintains stable fundamentals" (MarketBeat Q2/2026) — 18/08/2026: https://www.cushmanwakefield.com/en/vietnam/news/2026/08/southern-vietnam-industrial-real-estate-maintains-stable-fundamentals
- Cushman & Wakefield, "Industrial real estate in the South enters stabilization phase in Q1 2026" — 15/05/2026: https://www.cushmanwakefield.com/en/vietnam/news/2026/06/industrial-real-estate-in-the-south-enters-stabilization-phase-in-q1-2026
- Cushman & Wakefield, Q4 2025 Southern Vietnam Industrial MarketBeat — 28/01/2026: https://www.cushmanwakefield.com/vi-vn/vietnam/news/2026/01/q4-2025-southern-vietnam-industrial-marketbeat-report
- Doanh nghiệp Hội nhập, "Đất KCN miền Nam giá thuê tiếp tục tăng" (C&W Q1) — 15/05/2026: https://doanhnghiephoinhap.vn/dat-khu-cong-nghiep-mien-nam-gia-thue-tiep-tuc-tang-135894.html
- TBTCVN, "BĐS KCN phía Nam: cuộc đua tam mã" (C&W Q1) — 20/05/2026: https://thoibaotaichinhvietnam.vn/bat-dong-san-khu-cong-nghiep-phia-nam-cuoc-dua-tam-ma-va-su-troi-day-cua-cac-ve-tinh-moi-197651.html
- Doanh nghiệp Hội nhập, "BĐS công nghiệp miền Nam phản ứng trước thuế quan Mỹ-Việt" (CBRE H1/2025) — 11/07/2025: https://doanhnghiephoinhap.vn/bat-dong-san-co-ng-nghie-p-mien-nam-phan-ung-truoc-thue-quan-my-viet-109945.html
- The Investor, "FDI shifts 'taste', land banks lose edge..." — 25/05/2026: https://theinvestor.vn/fdi-shifts-taste-land-banks-lose-edge-as-southern-vietnams-industrial-property-market-gets-more-mature-d19155.html
- VCCI EN, "Five notable trends in Vietnam's industrial real estate" — 07/05/2026: https://en.vcci.com.vn/vcci-news/five-notable-trends-in-vietnams-industrial-real-estate-117212
- VietnamFinance, "Vốn FDI đăng ký vượt 50 tỷ USD sau 9 tháng" — 03/10/2026: https://vietnamfinance.vn/von-fdi-dang-ky-vuot-50-ty-usd-sau-9-thang-von-thuc-hien-cao-nhat-5-nam-d151508.html
- Báo Đấu thầu, "Vốn FDI thực hiện 9 tháng đạt hơn 21 tỷ USD" — 10/2026: https://baodauthau.vn/von-fdi-thuc-hien-9-thang-dat-hon-21-ty-usd-cao-nhat-5-nam-post208924.html
- Báo Văn hoá, "50,36 tỉ USD vốn ngoại đổ vào Việt Nam" — 10/2026: https://baovanhoa.vn/multimedia/5036-ti-usd-von-ngoai-do-vao-viet-nam-tien-chay-vao-dau-271918.html
- Báo Pháp luật (Doanh nhân), FDI 8 tháng 2026: https://doanhnhan.baophapluat.vn/von-fdi-dang-ky-vuot-40-6-ty-usd-giai-ngan-8-thang-cao-nhat-trong-vong-5-nam.html
- TC KT-TC, FDI 2025 vốn thực hiện +9%: https://tapchikinhtetaichinh.vn/nam-2025-von-fdi-thuc-hien-tai-viet-nam-tang-9-cao-nhat-trong-5-nam-qua-137749.html ; VnEconomy: https://vneconomy.vn/von-fdi-thuc-hien-nam-2025-lap-ky-luc-cao-nhat-trong-vong-5-nam.htm
- VietnamPlus, Đồng Nai hút vốn trong nước và FDI (tóm tắt tìm kiếm): https://www.vietnamplus.vn/dong-nai-hut-manh-dong-von-dau-tu-trong-nuoc-va-fdi-post1139703.vnp
- DFDL, "New U.S. Section 301 Tariffs on ASEAN Imports" — 11/08/2026: https://www.dfdl.com/insights/legal-and-tax-updates/us-section-301-tariffs-asean-implications/
- Cozen O'Connor, Supreme Court IEEPA ruling + Section 122 — 02/2026: https://www.cozen.com/news-resources/publications/2026/supreme-court-rules-president-lacks-ieepa-tariff-authority-president-imposes-section-122-tariffs
- Thomson Reuters, "Major shift in US trade policy: IEEPA, Section 122" — 23/02/2026: https://www.thomsonreuters.com/en-us/help/onesource-global-trade/regulatory-insights/2026/february-23rd/major-shift-us-trade-policy-ieepa-section-122
- Thompson Coburn, "Emerging tariff framework post Section 122" — 09/07/2026: https://www.thompsoncoburn.com/insights/81-july-9-2026-emerging-tariff-framework-post-section-122/
- Tuổi Trẻ EN, "US launches 2 trade probes covering multiple countries including Vietnam" — 10/04/2026: https://news.tuoitre.vn/us-launches-2-trade-probes-covering-multiple-countries-including-vietnam-103260410150034604.htm
- ACBS, thoả thuận khung Mỹ-VN — 03/07/2025: https://acbs.com.vn/acbsmedia/2025/07/20250703-Kinh-te-vi-mo_Cap-nhat-nhanh_My-va-Viet-Nam-thong-qua-thoa-thuan-khung-thuong-mai.pdf
- lsvn, "Chủ tịch tỉnh được trao thêm thẩm quyền... từ 01/3/2026" (Luật Đầu tư sửa đổi) — 14/12/2025: https://lsvn.vn/chu-tich-tinh-duoc-trao-them-tham-quyen-voi-cac-du-an-dat-dai-tu-01-3-2026-a167121.html
- thuvienphapluat, Luật 143/2025/QH15: https://thuvienphapluat.vn/van-ban/Dau-tu/Law-143-2025-QH15-on-invesment-689508.aspx ; lsvn về NĐ 239/2025: https://lsvn.vn/mot-so-diem-moi-cua-nghi-dinh-239-2025-nd-cp-sua-doi-quy-dinh-ve-dau-tu-a163403.html
- KTSG (qua Tuổi Trẻ), "Đồng Nai chuẩn bị khởi công ba KCN quy mô lớn vào ngày 19-12" — 15/11/2025: https://tuoitre.vn/saigontimes/dong-nai-chuan-bi-khoi-cong-ba-khu-cong-nghiep-quy-mo-lon-vao-ngay-19-12/
- thuvienphapluat, NQ 87/2025/NQ-HĐND bảng giá đất TP.HCM từ 01/01/2026: https://thuvienphapluat.vn/phap-luat-nha-dat/chinh-thuc-thong-qua-nghi-quyet-bang-gia-dat-tphcm-ap-dung-tu-112026-thong-tin-cu-the-ra-sao-13518.html
- VietnamFinance, "Giá đất mới tỉnh Đồng Nai năm 2026 tăng cao tới 9 lần" (dự thảo): https://vietnamfinance.vn/gia-dat-moi-tinh-dong-nai-nam-2026-tang-cao-toi-9-lan-d134241.html ; Nông nghiệp & Môi trường: https://nongnghiepmoitruong.vn/du-kien-bang-gia-dat-o-dong-nai-tang-cao-d781621.html
- ACBS, dự thảo Luật Đất đai sửa đổi — 05/2026: https://acbs.com.vn/acbsmedia/2026/05/Du-thao-Luat-dat-dai-sua-doi.pdf
- VnEconomy, quy hoạch sử dụng đất quốc gia (QĐ 1177/QĐ-TTg 30/06/2026, qua tóm tắt tìm kiếm): https://vneconomy.vn/quy-hoach-su-dung-dat-quoc-gia-mo-khong-gian-cho-tang-truong-siet-ky-luat-dat-dai.htm
- thuvienphapluat, CV 1965/CT-CS triển khai NĐ 50/2026 — 02/04/2026: https://thuvienphapluat.vn/cong-van/Thue-Phi-Le-Phi/Cong-van-1965-CT-CS-2026-thuc-hien-Nghi-dinh-50-2026-ND-CP-700232.aspx ; CV 1649/CT-CS: https://thuvienphapluat.vn/cong-van/Thue-Phi-Le-Phi/Cong-van-1649-CT-CS-2026-tien-thue-dat-698594.aspx
- Cafeland (Đầu tư Chứng khoán), "DN BĐS công nghiệp sẽ không được tính doanh thu một lần khi cho thuê đất" — 07/04/2026: https://cafeland.vn/tin-tuc/doanh-nghiep-bat-dong-san-cong-nghiep-se-khong-duoc-tinh-doanh-thu-mot-lan-khi-cho-thue-dat-150330.html
- Cổng hỏi đáp BTC (nguyên tắc ghi nhận theo nghĩa vụ): https://portal.mof.gov.vn/hoidapcstc/home/cthoidap/161918 ; Lao Động, lộ trình áp dụng TT 99: https://news.laodong.vn/kinh-doanh/bo-tai-chinh-huong-dan-lo-trinh-ap-dung-thong-tu-992025-1641116.ldo
- VnEconomy, "Long Thành chính thức đón tàu bay thương mại đầu tiên" (bay thử) — 15/12/2025: https://vneconomy.vn/cang-hang-khong-quoc-te-long-thanh-chinh-thuc-don-tau-bay-thuong-mai-dau-tien.htm
- Báo Đầu tư, "ACV chốt mốc khai thác thương mại sân bay Long Thành từ 1/12/2026" — 14/07/2026: https://baodautu.vn/acv-chot-moc-khai-thac-thuong-mai-san-bay-long-thanh-tu-ngay-1122026-d642966.html ; VOV, lộ trình ACV: https://vov.vn/xa-hoi/acv-de-xuat-lo-trinh-khai-thac-san-bay-long-thanh-va-phan-chia-voi-tan-son-nhat-post1315071.vov
- Tuổi Trẻ, Vành đai 3 thi công xuyên Tết kịp 30/4/2026 — 30/01/2026: https://tuoitre.vn/thi-cong-du-an-vanh-dai-3-tp-hcm-xuyen-tet-de-kip-moc-thong-xe-30-4-2026-20260130120012667.htm ; VietnamFinance, Biên Hòa-Vũng Tàu: https://vietnamfinance.vn/ngay-30-3-thong-xe-cao-toc-bien-hoa-vung-tau-tang-ket-noi-den-long-thanh-d141646.html
- Tạp chí Công Thương, tập đoàn cao su chuyển đổi 23.500 ha (tóm tắt tìm kiếm, đầu 2025): https://tapchicongthuong.vn/cao-su-viet-nam--gvr-da-co-23-500-ha-dat-cao-su-duoc-phe-duyet-chuyen-doi-sang-dat-cong-nghiep-126881.htm
- VnEconomy, Nghị quyết 79-NQ/TW — 01/2026: https://vneconomy.vn/ban-hanh-nghi-quyet-79-nqtw-dua-kinh-te-nha-nuoc-dan-dat-ky-nguyen-vuon-minh.htm ; TBTCVN, hạn kế hoạch cơ cấu lại vốn 31/8: https://thoibaotaichinhvietnam.vn/hoan-thanh-ke-hoach-co-cau-lai-von-nha-nuoc-tai-doanh-nghiep-giai-doan-2026-2030-truoc-ngay-31-8-201987.html
- Doanh nhân (Báo Pháp luật), TP.HCM 14 KCN mới đến 2033: https://doanhnhan.baophapluat.vn/tp-ho-chi-minh-sap-co-them-14-khu-cong-nghiep-moi-den-nam-2033.html
- Nội bộ: `sector_read_ngan_hang_20261031.md` (bảng 5 tầng, tỷ giá), `sector_read_da_xay_dung_nam_bo_20261030.md` (VĐ4), `data/deposit_rate_vn_events.csv` và `cctg_rate_vn_events.csv` (26/10, 12/10), `vn_macro_regime_history.md` MACRO UPDATE 14/10.
