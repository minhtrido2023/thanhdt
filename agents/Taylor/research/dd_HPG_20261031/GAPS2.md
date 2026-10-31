# DD HPG — Vòng 4: các điểm còn mở sau báo cáo nhà đầu tư · as-of 31/10/2026 · job `Taylor_20261031_114427`

> NGHIÊN CỨU READ-ONLY, trung dung. KHÔNG sửa `REPORT.md` / `investor_report/` vòng này. Pháp lý/quản trị ⇒ phân tích bình thường + WARNING (luật 27/09).
> **Nguồn mới** (`src/gaps2/`):
> - **[BN]** BCTC hợp nhất soát xét 6T/2026: tr.in 9–10 (LCTT), 13–18 (TM1 cấu trúc + **chuyển nhượng**), 31 (TM6), 55 (TM34). Ảnh `src/png/bn/p13–p21.png`, `src/gaps2/png/bn_p14.png`, `bn_p22.png`.
> - **[ME-Q3]** BCTC riêng công ty mẹ Q3/2026: tr.in 14 (phải thu khác), 23 (**thu nhập khác**). Ảnh `src/gaps2/png/me_p15.png`, `me_p24.png`.
> - **[HN-Q3]** tr.6 (LCTT 9T), tr.16 (VI.4). Ảnh `src/png/q3_p7.png`, `q3_p17.png`.
> - **[CBTT]** NQ 10 & NQ 13/NQHP-2026, ảnh đọc lại `src/gaps2/png/nq10_p3.png`, `nq13_p2.png`.
> - **[GỐC-web]** Điều lệ HPG 28/04/2026, BCTN 2024, tài liệu ĐHĐCĐ 2025, factsheet VOF/VEIL/VEOF: `src/gaps2/rawA/`, `rawB/`.
> - **[WEB]** hai file do subagent Sonnet viết: `src/gaps2/web_A_governance.md`, `src/gaps2/web_B_tax_export.md`. Số quan trọng tôi đã tự kiểm lại trên văn bản gốc. Chỗ nào chưa kiểm được thì gắn [báo].
> - **[BQ]** `calc/gaps2_peer_beta.py` → `calc/gaps2_peer_beta_out.txt` (dữ liệu `calc/gaps2_peers_px.csv`).
>
> Số BCTC đọc từ ẢNH trang (pymupdf, zoom 1,25–1,4). Số tự tính gắn **(ước lượng)**. Nhãn: **SỰ KIỆN** = đọc thẳng từ văn bản; **ƯỚC LƯỢNG** = tôi tự tính; **NHẬN ĐỊNH** = cách tôi đọc.

## TL;DR — vòng 4 đổi gì

1. **Giá hoán đổi BĐS HP → TLSH đã chốt bằng số gốc: xấp xỉ MỆNH GIÁ.**
   - SỰ KIỆN: BCTC riêng công ty mẹ Q3 ghi "Thu nhập khác" **210.947.820.000 đ** [ME-Q3 tr.23].
   - Con số này **khớp tới từng đồng** với 7.995.000.000.000 − 778.405.218 cp × 10.000 đ.
   - ⇒ Công ty mẹ giữ BĐS HP theo mệnh giá, đem góp với giá 10.271 đ/cp và ghi lãi 211 tỷ.
   - So với 32.000 đ/cp trong NQ 10, HPG giao **thêm 528,6 tr cp** BĐS HP cho cùng 799,5 tr cp TLSH. TLSH phát hành ở **mệnh giá 10.000** [CBTT NQ 10].
   - Lý do đổi giá và tên tổ chức định giá: **vẫn không công bố**.
2. **Bên mua hai công ty con BĐS: BCTC không nêu.**
   - SỰ KIỆN [BN tr.18]: bán **49.950.000 cp (99,9%) Mỹ Hào** và **367.500.000 cp (70%) Khu đô thị xanh**. Không có tên bên mua, không có giá.
   - Tiền thu hồi đầu tư **9.800,8 tỷ** toàn bộ nằm ở H1. Q3 không có thêm khoản thu nào [HN-Q3 tr.6].
3. **QĐ 1917/QĐ-BCT CÓ TỒN TẠI.** Đó là **QĐ chống lẩn tránh chính thức** (27,83%, HRC TQ rộng >1.880 đến ≤2.300 mm, hiệu lực 28/07/2026) [báo ×2]. Không phải QĐ AD gốc.
   - ⇒ Câu "QĐ 1917 sai số hiệu / không tồn tại" trong GAPS §5 và investor report **phải sửa**: Bobby sai ở chỗ GÁN số 1917 cho vụ AD gốc, không phải ở chỗ bịa số.
4. **Liên danh Đại lộ sông Hồng [báo]: HPG là THÀNH VIÊN**, cùng Đại Quang Minh (đứng đầu liên danh) và THACO (tuoitre 06/05/2026).
   - Khớp với khoản 1.600 tỷ "tiền chuyển cho đối tác theo thoả thuận liên danh 02/2026/TTLD" [BN TM9].
   - ⇒ Ngoài cổ phần TLSH, HPG còn **đồng hành trực tiếp trong dự án BT**.
5. **Thủ tục: HĐQT có thẩm quyền.**
   - SỰ KIỆN: Điều lệ 2026 Điều 46 k3–4 [GỐC-web] đặt ngưỡng ĐHĐCĐ ở ≥35% tổng tài sản hợp nhất.
   - ƯỚC LƯỢNG: 7.995 / 257.899 = 3,1%; cộng cả 1.920 + 1.600 thì ~4,5%.
   - ⇒ **Không vi phạm thủ tục.** Cờ quản trị nằm ở **công bố thông tin và giá**, không nằm ở thẩm quyền.
6. **Kiểm toán:** BCTC 2024 do **KPMG** kiểm toán, chấp nhận toàn phần [GỐC BCTN 2024 tr.95, 98]. ĐHĐCĐ 2025 duyệt danh sách 4 hãng và **uỷ quyền TGĐ chọn**. Deloitte được chọn, **lý do không công bố**.
7. **β peer VN (thanh khoản đủ) ≈ 0,9–1,1, cao hơn HPG 0,84–0,89.** Ke v2 (tâm 11,83%) nằm ở nửa dưới. Không đổi vùng, nhưng **không ủng hộ dời tâm lên**.
8. **Vùng 18.000–22.500 / tâm ≈20.200: GIỮ (ước lượng). WARNING quản trị: GIỮ, nặng hơn một bậc** (giá hoán đổi bằng mệnh giá + HPG là thành viên liên danh BT).

---

## 1. Bên mua các công ty con BĐS thoái H1/2026 — ⚠️ WARNING (chưa đóng)

| Mục | Kết luận | Loại | Nguồn |
|---|---|---|---|
| Đã bán gì | CTCP XD & PT Đô thị Hòa Phát (con) chuyển nhượng **toàn bộ 49.950.000 cp = 99,9%** CTCP PT Đô thị Mỹ Hào. CTCP PT BĐS Hòa Phát (con) chuyển nhượng **toàn bộ 367.500.000 cp = 70%** CTCP PT Khu đô thị xanh. Cả hai không còn là công ty con tại 30/6/2026 | SỰ KIỆN | [BN tr.in 18] |
| Mệnh giá phần bán | 499,5 + 3.675,0 = **4.174,5 tỷ** | ƯỚC LƯỢNG (cp × 10.000) | tự tính |
| Tiền thu | LCTT mã 26 "thu hồi đầu tư góp vốn vào đơn vị khác": **9.800,8 tỷ** ở 6T. **9T đúng bằng 9.800,8** ⇒ Q3 không thu thêm | SỰ KIỆN | [BN tr.in 9]; [HN-Q3 tr.6] |
| Lãi | 4.929,1 tỷ "lãi bán, thanh lý các khoản đầu tư tài chính". TM34 dẫn chiếu TM01 | SỰ KIỆN | [BN tr.in 55] |
| Giá vốn ngầm định | 9.800,8 − 4.929,1 ≈ **4.872 tỷ**, cao hơn mệnh giá ~700 tỷ. Lãi ≈ ×2 giá vốn | ƯỚC LƯỢNG (giả định mã 26 chỉ gồm hai thương vụ này) | tự tính |
| Phân khu A Phố Nối | ~3.800 tỷ lãi Q1 theo lời ông Long [báo, vòng 2]. BN **không** nhắc tên dự án. NHẬN ĐỊNH: rất có thể nằm trong 4.929 qua việc bán Mỹ Hào / Đô thị xanh, nhưng chưa xác nhận | [báo] | `src/gaps/web_tlsh_governance.md` §4 |
| **Bên mua, giá từng thương vụ** | **KHÔNG công bố** trong BN TM1/TM34 và không thấy trong CBTT HPG. Đô thị xanh lúc thành lập: BĐS HP 90%, hai cá nhân 5% + 5% [báo, Dân trí 18/07/2025]. ĐKKD sau chuyển nhượng: không tra được (cổng ĐKKD cần đăng nhập; masothue/thongtindoanhnghiep không có cổ đông) | — | `web_A_governance.md` §1 |
| Liên hệ với TLSH / ông Khoa / Đại Quang Minh | **Không có dữ kiện** theo cả hai chiều. Đây là "không tìm thấy", không phải "đã xác minh không có" | — | — |

**Đã thử:** BN TM1 (tr.in 11–18), TM34. LCTT 6T/9T. CBTT hoaphat.com.vn 01–09/2026. Tra cứu masothue/thongtindoanhnghiep. Truy vấn "Phát triển đô thị Mỹ Hào chuyển nhượng", "Khu đô thị xanh Hòa Phát cổ đông mới", "Phố Nối phân khu A nhận chuyển nhượng".

**NHẬN ĐỊNH:** khoản lãi 4.929 tỷ đến từ việc bán cho bên **không được nêu tên**, và nhóm này chiếm ~21% LNTT 9T. Đây là khoảng trống công bố thông tin. Định giá không bị ảnh hưởng vì REPORT đã bóc toàn bộ khỏi lõi. Nhưng nếu bên mua là bên liên quan, khoản lãi có thể là một **chuyển giá trị ngược chiều** (BĐS bán rẻ/đắt cho ai?). Đặt **mốc H10**: BCTC kiểm toán 2026 phải thuyết minh bên mua (hoặc HPG xác nhận bằng văn bản). P công bố ≈0,4 (ước lượng); chấm 2027-04-15.

## 2. Định giá hoán đổi BĐS HP → TLSH — ⚠️ WARNING (đóng phần số học; lý do vẫn mở)

**SỰ KIỆN (ảnh văn bản gốc):**
- **NQ 10/NQHP-2026 (22/07)** [CBTT, `nq10_p3.png`]:
  - HPG đăng ký mua **799.500.000 cp TLSH, mệnh giá 10.000 đ/cp, tổng 7.995 tỷ**, góp bằng cổ phần BĐS HP, **"Định giá cổ phần: 32.000 VNĐ/CP"**.
  - Vốn TLSH trước: 12.800 tỷ, sau: 39.450 tỷ.
  - "Hiện tại CTCP Tập đoàn Hòa Phát chưa sở hữu cổ phần tại TLSH": đúng ở cấp công ty mẹ, vì 15% khi đó do BĐS HP nắm.
- **NQ 13/NQHP-2026 (30/09)** [CBTT, `nq13_p2.png`]:
  - "Số cổ phần **đã mua**: 799.500.000; tổng giá trị 7.995 tỷ".
  - Hình thức: **góp 778.405.218 cp BĐS HP**.
  - Sau giao dịch, vốn góp của HPG tại TLSH = **9.915 tỷ = 25,13%**.
  - Cử **ông Hoàng Quang Việt (TV HĐQT HPG)** quản lý phần vốn.
  - HPG còn **26,55% BĐS HP = 281.394.782 cp**.
  - Điều 2: các nội dung của NQ 10 khác NQ 13 "được điều chỉnh tương ứng". **Không nêu lý do và không nêu giá/cp.**
- **Hạch toán công ty mẹ** [ME-Q3 tr.23]: Q3/2026 "Thu nhập khác" 210.947.820.000 đ (Q3/25: 7.020.001).

**ƯỚC LƯỢNG:**
- 778.405.218 × 10.000 = 7.784.052.180.000. Lấy 7.995.000.000.000 trừ đi được **210.947.820.000**, khớp tuyệt đối ⇒ **giá hoán đổi = 7.995 tỷ / 778,405 tr cp = 10.271,0 đ/cp BĐS HP = mệnh giá + 2,7%**.
- Tổng cp BĐS HP: 778.405.218 + 281.394.782 = **1.059.800.000** ✓ (khớp giá gốc 10.598,0 tỷ ở sổ công ty mẹ đầu năm [REPORT v2 §6]).
- **LDLK công ty mẹ 12.728,9** = TLSH 9.915 + BĐS HP 281.394.782 × 10.000 = **2.813,9** ⇒ 12.728,9 ✓.
  - ⇒ Trong Q3, công ty mẹ đã **nhận về 192 tr cp TLSH (1.920 tỷ) từ BĐS HP**, trước khi BĐS HP rời hợp nhất. Đây là giao dịch nội bộ, nên không xuất hiện trên LCTT hợp nhất.
- Nếu giữ giá 32.000 như NQ 10, chỉ cần **249,8 tr cp**. HPG đã giao thêm **528,6 tr cp = 49,9% vốn BĐS HP**.
- **Phần giá trị có thể đã chuyển ra** (kịch bản giả định: 32.000 là giá trị hợp lý và TLSH có giá trị hợp lý bằng mệnh giá):
  - 778,4 tr × (32.000 − 10.271) = 16.914 tỷ;
  - HPG thu hồi lại 25,13% qua TLSH ⇒ phần ròng sang cổ đông TLSH khác ≈ **12.660 tỷ ≈ 1.500 đ/cp HPG** (8.442,96 tr cp).
  - **Cận dưới = 0** nếu 10.271 mới là giá hợp lý, tức NAV BĐS HP ≈ mệnh giá sau khi đã bán hai dự án H1.

**Có cần ĐHĐCĐ không?** SỰ KIỆN [Điều lệ HPG 28/04/2026, Điều 46 k3–4, `rawA/dieu-le-2026.pdf` pdf tr.50–51]:
- ĐHĐCĐ chấp thuận giao dịch với người nội bộ/người có liên quan/cổ đông >10%/doanh nghiệp liên quan (Đ164 LDN) có giá trị **≥35% tổng tài sản trên BCTC hợp nhất gần nhất**, kể cả cộng dồn 12 tháng.
- **<35% thuộc thẩm quyền HĐQT.** Khoản 36 (pdf tr.36) cũng đặt ngưỡng ĐHĐCĐ ở 35% cho đầu tư/bán tài sản.

ƯỚC LƯỢNG: tổng tài sản hợp nhất 31/12/2025 = 257.899 tỷ [KT25, theo subagent A; khớp quy mô REPORT]. 7.995 = 3,1%; cộng 1.920 + 1.600 ≈ 11.515 = 4,5% ⇒ **dưới xa ngưỡng; HĐQT đủ thẩm quyền, không vi phạm thủ tục**. Đối chiếu khung LDN 2020 Đ167 (≥35% ⇒ ĐHĐCĐ): cùng ngưỡng. Văn bản luật chưa tải, tôi trích theo khung.

**Lý do đổi phương án, tổ chức thẩm định giá, giải trình 01/10: KHÔNG TÌM ĐƯỢC.**
- Đã thử: CBTT HPG 22/07–31/10 (chỉ có NQ 10, NQ 13, không có giải trình).
- Báo cáo quản trị 6T/2026 (28/07): mục giao dịch "đối tượng khác" ghi "Không có".
- vnbusiness 03/10, baophapluat, Mekong ASEAN, VietnamFinance: các báo tự ghi là không có lý do.

**NHẬN ĐỊNH:**
- Không có lãi giả thổi P&L hợp nhất: lãi đầu tư thuần hợp nhất Q3 chỉ 4,3 tỷ; 211 tỷ chỉ nằm ở công ty mẹ.
- Nhưng HPG đã đổi **73,45% một công ty con BĐS** lấy **20,27% TLSH theo mệnh giá**, ở giá **bằng 1/3** giá chính HĐQT công bố 10 tuần trước, không kèm giải thích.
- Với cổ đông thiểu số, câu hỏi đúng là "BĐS HP có NAV hợp lý > 10.271 đ/cp không?". Không có số nào để trả lời.
- ⇒ **WARNING nặng hơn một bậc.** Không trừ vào định giá: RI dựng trên sổ sách, sổ đã ghi ~mệnh giá, nên phần "giá trị ngầm" chưa bao giờ nằm trong mô hình. Đây là **chi phí cơ hội / rủi ro quản trị**, không phải lỗ kế toán.

## 3. TLSH: ai góp phần còn lại, cổ đông, dự án — chưa đóng

| Câu hỏi | Kết luận | Nguồn |
|---|---|---|
| Ai góp 18.655 tỷ còn lại (26.650 tỷ "tài sản khác" − 7.995 của HPG) | **KHÔNG TÌM ĐƯỢC** | `web_A_governance.md` §2 |
| Cổ đông TLSH sau tăng vốn, HĐQT TLSH | **KHÔNG TÌM ĐƯỢC.** Sáng lập: Trần Đăng Khoa 40% … [báo]. HPG cử ông **Hoàng Quang Việt** (TV HĐQT HPG) quản lý phần vốn [CBTT NQ 13]. Chưa có nguồn nói ông Việt ngồi HĐQT TLSH | [CBTT]; [báo] |
| Quan hệ với nhóm ông Trần Đình Long | Không thấy tên cổ đông TLSH trong danh sách người có liên quan ở thông báo giao dịch của ông Trần Vũ Minh (02/10/2026, gốc). "Không tìm thấy" ≠ "không có" | [CBTT] |
| **Liên danh Đại lộ cảnh quan sông Hồng** | [báo, tuoitre 06/05/2026; VietnamFinance]: T&T, Văn Phú, MIK rút. Liên danh còn **Đại Quang Minh (đứng đầu), THACO, Hòa Phát**; hình thức PPP–BT trả bằng quỹ đất. Thoả thuận liên danh 02/2026/TTLD ngày **08/05/2026** [BN TM9] ký **2 ngày sau** tin này ⇒ khớp thời điểm (NHẬN ĐỊNH). Văn bản thoả thuận: không công bố. QĐ 2560/QĐ-UBND 16/05/2026: chưa đối chiếu | [báo] + [BN] |
| Pháp lý Thư Lâm–Đông Anh (QĐ chấp thuận nhà đầu tư, giao đất) | **KHÔNG TÌM ĐƯỢC** số/ngày văn bản gốc. Chỉ có tin giao ~429,5 ha tới cuối 09/2026 [báo, vòng 2] | — |

**NHẬN ĐỊNH:** phơi nhiễm của HPG với hệ sinh thái Đại Quang Minh – TLSH có **ba lớp**:
1. **Cổ phần TLSH**: 9.915 tỷ.
2. **26,55% BĐS HP**: 2.749 tỷ hợp nhất.
3. **Tư cách thành viên liên danh BT** cùng 1.600 tỷ đã chuyển cho đối tác. Đây là lớp quan trọng nhất, vì liên danh BT có thể kéo theo **nghĩa vụ góp vốn / bảo lãnh** khi dự án vào giai đoạn đầu tư. BCTC chưa thuyết minh (BN TM41 chỉ nêu cam kết vốn Dung Quất và dự án khác).

Cần đưa vào H7/H9.

## 4. Dòng tiền sang TLSH / liên danh — đóng một phần

**SỰ KIỆN:**
- LCTT hợp nhất "chi góp vốn vào đơn vị khác": **6T 3.634,7** [BN tr.in 9]; **9T 4.892,9** [HN-Q3 tr.6] ⇒ Q3 **1.258,2** (ước lượng, hiệu số).
- Đầu tư tài chính tại 30/6 [BN TM6, tr.in 31]: chỉ có **liên kết TLSH 1.920**, không có khoản "đầu tư góp vốn vào đơn vị khác" nào khác.
- Phải thu khác hợp nhất [HN-Q3 VI.4 tr.16]:
  - DH "thoả thuận hợp tác liên danh" **100,0** (01/01: 0; 30/6: 1.600 [BN TM9]);
  - **ký quỹ DH 499,9** (01/01: **248,9**, tăng 251, không phải "mới 499,9");
  - ký quỹ NH 715,8 (01/01: 1.218,6).
- Phải thu khác DH công ty mẹ [ME-Q3 tr.14]: **đặt cọc/ký quỹ 361,2** (01/01: 4,2) + **phải thu hợp đồng BCC 134,6** (01/01: 0) = 495,8. Đối tác không nêu.

**ƯỚC LƯỢNG / giả thuyết** (chưa có thuyết minh xác nhận):
- (a) 3.634,7 − 1.920 (TLSH) = **1.714,7**, mà tại 30/6 không có khoản đầu tư nào tương ứng. Khớp tốt nhất: **1.600 tỷ chuyển cho liên danh đã được phân loại là "góp vốn" trên LCTT** nhưng ghi "phải thu" trên BCĐKT, còn dư ~115 tỷ.
  - ⇒ Con số "~2.973 chưa rõ đích" và "1.500 ứng liên danh" trong investor report rất có thể **chồng lên nhau ~1.500–1.600 tỷ**: đó là cùng một dòng tiền. Phần thật sự chưa truy ≈ **1.258 (Q3) + ~115 (H1) ≈ 1.370 tỷ**.
- (b) Liên danh **1.600 → 100** trong Q3: không có dòng thu hồi tương ứng trên LCTT 9T (mã 26 không đổi so với 6T).
  - Giả thuyết khớp nhất: khoản phải thu nằm ở **BĐS HP** và **rời hợp nhất cùng BĐS HP ngày 30/9**. Nếu vậy 1.500 tỷ không "mất", mà nay nằm trong BĐS HP (liên kết 26,55%). Phơi nhiễm gián tiếp của HPG giảm còn ~26,55%, đổi lại không còn kiểm soát.
  - **Chưa xác nhận.**
- (c) Q3 1.258,2: **Điện gió ngoài khơi Sông Hậu** 600 (NQ 08, 20/6) là ứng viên, nhưng không có trong danh sách liên kết 30/9. Ứng viên khác: BCC 134,6 + ký quỹ 361,2 của công ty mẹ, đã đủ ~496. **Không tách được.**

**NHẬN ĐỊNH:** đích tiền không rõ giảm từ ~4.470 tỷ (2.973 + 1.500) xuống khoảng **~1.370–1.870 tỷ** (ước lượng, tuỳ giả thuyết (a)). Quy mô ≈ 1% VCSH. Không phải biến định giá; vẫn là câu hỏi công bố thông tin.

## 5. Cổ phiếu HPG cầm cố + covenant — chưa đóng

- SỰ KIỆN [KT25 TM23, vòng 2]: vay có bảo đảm gồm **"cổ phiếu của CTCP Tập đoàn Hòa Phát do các cá nhân sở hữu"**. Số cp, tên cá nhân, ngân hàng: **không công bố**.
- **CBTT cầm cố/giải chấp** của ông Long, bà Hiền, ông Trần Vũ Minh, thành viên HĐQT giai đoạn 2024–2026: **KHÔNG TÌM THẤY** (CBTT HPG; truy vấn "cầm cố cổ phiếu HPG", "giải chấp HPG", "thế chấp cổ phiếu Hòa Phát ngân hàng").
  - NHẬN ĐỊNH: cầm cố cổ phiếu để bảo đảm khoản vay **của công ty** không nhất thiết kích hoạt nghĩa vụ CBTT giao dịch của người nội bộ. Vắng CBTT không chứng minh được gì.
- **Covenant**: không thuyết minh trong KT25/BN. Vay DH VCB 30.016 tỷ (83%) [KT25]. Không thấy cờ vi phạm hay phân loại lại nợ.
- ⇒ WARNING giữ nguyên, không có số mới.

## 6. Thuế ưu đãi & DQ2 — đóng khung, chưa đóng kết luận

- [báo, luatvietnam tóm tắt CV 377/TCT-CS 30/01/2024]: DQ2 có **QĐ chủ trương đầu tư 108/QĐ-BQL ngày 18/06/2021** (BQL KKT Dung Quất). Tổng cục Thuế yêu cầu Cục Thuế Quảng Ngãi phối hợp BQL xác định **dự án mới hay mở rộng**. **Kết luận sau đó: KHÔNG TÌM ĐƯỢC.** Toàn văn cần đăng nhập.
- **Luật Thuế TNDN 67/2025/QH15** [báo, luatvietnam + MISA; văn bản luật chưa đối chiếu]:
  - thuế suất phổ thông **vẫn 20%**, áp từ kỳ tính thuế 2025;
  - **dự án mở rộng** (tăng nguyên giá TSCĐ hoặc công suất ≥20%) hưởng ưu đãi **như dự án đang hưởng, cho phần thu nhập tăng thêm**. Nếu dự án gốc đã hết ưu đãi thì chỉ được miễn/giảm, không được thuế suất ưu đãi;
  - ưu đãi đang hưởng được **bảo lưu**.
- BCTN 2025: **không có** đoạn nào về ưu đãi TNDN (grep `src/gaps/raw2/ar2025.txt`). Ngày hết ưu đãi từng nhà máy: **không công bố ở đâu**.
- NHẬN ĐỊNH: dù DQ2 bị xếp "mở rộng", luật 2025 vẫn cho hưởng ưu đãi theo phần còn lại của DQ1 (10%, giảm 50% tới ~2031–2032, ước lượng vòng 2). Rủi ro **truy thu** chỉ thành vấn đề nếu DQ2 đã tự áp chế độ "dự án mới" (miễn 4 năm) mà bị bác.
  - Không đổi độ nhạy: REPORT v2 đã đặt terminal 20%. Năm hết ưu đãi chỉ dịch ±300–500 đ/cp (GAPS §2).
  - Rủi ro truy thu: **không định lượng được** (không biết DQ2 đang áp chế độ nào). ETR thép 6T/26 6,5% gợi ý **đang được miễn/giảm sâu** ⇒ nghiêng về "DQ2 đang hưởng như dự án mới" (NHẬN ĐỊNH).

## 7. Kiểm toán — ĐÓNG

- SỰ KIỆN [BCTN 2024 tr.95, 98, `rawA/bao-cao-thuong-nien-hpg-2024.pdf`]: "Đơn vị kiểm toán của Công ty và Tập đoàn là **Công ty TNHH KPMG**". Báo cáo kiểm toán số **22-02-00117-25-2**, ý kiến chấp nhận toàn phần, không ngoại trừ/nhấn mạnh (subagent A đọc đoạn Ý kiến; tôi kiểm tên hãng + số báo cáo).
- SỰ KIỆN [tài liệu ĐHĐCĐ 2025 pdf tr.42, `rawA/4-tai-lieu-hop.pdf`]: Tờ trình 10/TT-ĐHĐCĐ.2025 đưa danh sách **Deloitte VN, KPMG, EY VN, PwC VN** cho kiểm toán 2025–2027, chọn theo tiêu chí. ĐHĐCĐ uỷ quyền TGĐ chọn [NQ ĐHĐCĐ 2025 mục 1.10].
- BCTC 2025 do Deloitte kiểm toán, chấp nhận toàn phần, chỉ có đoạn "Vấn đề khác" về năm trước [vòng 2; subagent A].
- **Lý do đổi: không công bố.** NHẬN ĐỊNH: đổi trong nhóm Big-4 sau nhiệm kỳ nhiều năm, có quy trình ĐHĐCĐ ⇒ **không phải cờ đỏ**, chỉ để ghi nhận.

## 8. Xuất khẩu / EU / VSA — đóng một phần

| Mục | Kết luận | Nguồn |
|---|---|---|
| XK Q3/2026 | XK chiếm **24,6% sản lượng HRC** (không phải toàn tập đoàn); HRC Q3 >2 tr t ⇒ ~0,5 tr t HRC XK (ước lượng); 26 quốc gia/vùng lãnh thổ | [GỐC thông cáo 9T, vòng 2] |
| XK theo nước Q3/9T | **KHÔNG CÔNG BỐ** (thông cáo, VSA, hải quan đã thử) | — |
| Hạn ngạch EU riêng VN / phần HPG | **Không có số chính thức.** Assofermet ước XK HRC VN sang EU còn ~567 nghìn t/năm (2023: 1,113 tr t) [báo ngành, không chính thức]. EU chỉ chiếm 3,6% DTT H1 [BN] ⇒ nhỏ | `web_B_tax_export.md` §3 |
| Thị phần XD theo vùng | Số gốc mới nhất là **2024** [GỐC BCTN 2024 tr.44, VSA]: **toàn quốc 38%; XK 61%, miền Trung 51%, miền Bắc 35%, miền Nam 22%**. Bản 2025/9T-2026 theo vùng: **không tìm được**. HPG tự công bố 36% (Q1, H1/2026) | `src/gaps2/png/bctn24_p44.png` |
| Thị phần HRC | **~40%** (VEOF 07/2026 [GỐC quỹ]) so với "60%" ở vòng 2. NHẬN ĐỊNH: hai mẫu số khác nhau (40% ≈ tiêu thụ HRC VN gồm nhập khẩu; 60% ≈ sản xuất/tiêu thụ nội). Cần ghi rõ mẫu số khi dùng | `rawB/veof_jul26.pdf` |
| Giá bán bình quân theo nhóm | **Không tính được** từ số gốc (BCTC không tách) | — |

## 9. Quỹ ngoại — ĐÓNG (số đã kiểm trên factsheet)

| Quỹ | HPG % NAV | Ngày | Nguồn |
|---|---|---|---|
| VinaCapital VOF | **5,0%** (top 10) | 30/06/2026 | [GỐC] `rawB/vof_jun26.pdf` ✓ tôi kiểm |
| Dragon Capital VEIL | **3,8%** | 30/06/2026 | [GỐC] `rawB/veil_jun26.pdf` ✓ |
| VinaCapital VEOF (quỹ nội, tham khảo) | **6,1%** (#3) | 31/07/2026 | [GỐC] `rawB/veof_jul26.pdf` ✓ |
| VanEck VNM | 5,01% | 29/10/2026 | vòng 2 |
| Fubon FTSE VN | không có tỷ trọng; BSC dự kiến mua thêm ~94,9 tỷ kỳ 09/2026 (ước lượng của BSC) | — | [báo] |
| iShares, DCDS | không tìm được | — | — |

NHẬN ĐỊNH: các quỹ chủ động lớn đều nắm ở mức **trung tính đến hơi thiếu tỷ trọng** (3,8–6,1%), tức chưa phải vị thế đông người.

## 10. β peer VN — ĐÓNG (có giới hạn) [BQ, `calc/gaps2_peer_beta_out.txt`]

Tuần, Close điều chỉnh, so với VNINDEX, kết thúc 30/10/2026. Dimson = β + β(VNINDEX trễ 1 tuần), dùng để bù giao dịch mỏng. ADV = trung vị 6 tháng, tỷ/phiên.

| Mã | β 2y | β 3y | Dimson 3y | corr 3y | ADV 6M | Ghi chú |
|---|---|---|---|---|---|---|
| **HPG** | 0,846 | 0,886 | 0,744 | 0,67 | 426 | — |
| HSG (BANNED, tham chiếu) | 0,880 | 1,023 | 0,989 | 0,61 | 26 | đủ thanh khoản |
| NKG (BANNED, tham chiếu) | 0,969 | 1,087 | 1,126 | 0,55 | 19 | đủ thanh khoản |
| VGS | 1,197 | 1,383 | 1,517 | 0,56 | 2,6 | mỏng |
| TVN | 0,733 | 0,889 | 1,040 | 0,34 | 5,5 | mỏng, 17% tuần lợi suất 0 |
| SMC | 0,477 | 0,566 | 0,476 | 0,19 | 1,7 | rất mỏng |
| TLH | 0,644 | 0,851 | 1,095 | 0,39 | 0,5 | rất mỏng |
| HMC | 0,082 | 0,150 | 0,246 | 0,14 | 0,04 | vô nghĩa |

- Trung vị 3y (SMC/TVN/VGS/TLH/HMC): β **0,85**, Dimson **1,04**. Gồm cả HSG/NKG: β 0,89, Dimson 1,04.
- **Giới hạn:** chỉ HSG/NKG có thanh khoản đủ (≥19 tỷ/phiên) và cả hai là BANNED. Các mã còn lại có ADV < 6 tỷ, corr < 0,4 ⇒ β thô **bị kéo về 0**. SE 0,16–0,27.
- **NHẬN ĐỊNH:**
  - β ngành thép VN "đúng" ≈ **0,9–1,1** (HSG/NKG 3y + Dimson trung vị);
  - HPG thấp hơn vì là thành phần lớn của chỉ số. Dimson HPG < β thô ⇒ HPG **dẫn** chỉ số, không có độ trễ cần bù;
  - Ke v2 (β 0,915, tâm 11,83%) ở **nửa dưới** khung peer. Nếu dùng β 1,0: Ke ≈ 6,75% + 1,0 × 5,55% = 12,30% ⇒ RI trung lập ≈ **−1.200 đ/cp** (ước lượng tuyến tính từ v2: β 1,1/Ke 12,85% ⇒ 16.484 so với 19.221 ở 11,83%, tức ≈ −2.680 đ/cp mỗi +1pp).
  - Vẫn nằm trong vùng 18.000–22.500. ⇒ **Không đổi vùng; lập luận chống dời tâm lên.**

## 11. Các số chưa đọc gốc

| Mục | Kết luận | Nguồn |
|---|---|---|
| Thuế suất 20% áp cho đâu | Thuế suất phổ thông 20% (Luật 67/2025 Đ10) cho công ty mẹ, BĐS và các công ty con không ưu đãi. Thép DQ hưởng ưu đãi KKT. BCTC chỉ ghi chung "Tập đoàn 20%; công ty con … theo GCN đầu tư" [KT25 TM37] | [báo] + [KT25] |
| PVTM mới nhắm HPG | **Không thấy vụ mới nêu tên HPG** ngoài thép cây Mỹ. Liên quan thép VN [báo]: Úc AD tôn mạ (30/04/2026; Hoa Sen, Nam Kim); Đài Loan AD inox cán nguội (08/2026, 20 DN VN); EU AD CRC (khởi xướng ~09/2025, kết luận ~09–11/2026, chưa kiểm); Mỹ CORE AD (19/12/2025) + vòng chống lẩn tránh 25/03/2026. **Nên rà nếu HPG XK tôn mạ sang Mỹ** (tôn HPG 9T 307 nghìn t). Ấn Độ: HPG 0–10% ⇒ không áp | `web_B_tax_export.md` §5 |
| QĐ 1902 rà soát hành chính | Thời hạn kết luận: **không tìm được** (thường ≤12 tháng ⇒ ~07/2027, ước lượng). Rủi ro trong cửa sổ H4 giữ nguyên | — |
| **Chống lẩn tránh chính thức** | **QĐ 1917/QĐ-BCT**, 27,83%, HRC TQ rộng >1.880 đến ≤2.300 mm, hiệu lực **28/07/2026** [báo: SMM 30/07/2026; doanhnghiephoinhap 30/07/2026, tôi đã tự mở bài: xác nhận số QĐ và dải chiều rộng; ngày ban hành bài không nêu]. Thay cho QĐ 612 tạm thời. Văn bản gốc moit.gov.vn: chưa mở | [báo ×2] |

---

## Bảng: điểm mở → trạng thái → đổi nhận định?

| # | Điểm mở | Trạng thái | Đổi nhận định? |
|---|---|---|---|
| 1 | Bên mua cty con BĐS H1 | **Chưa đóng.** Đã có số cp (49,95 tr; 367,5 tr), tiền thu 9.800,8, giá vốn ngầm ~4.872 (ước lượng). Bên mua **không công bố** | Không đổi giá trị (đã bóc khỏi lõi). Thêm **H10** công bố bên mua |
| 2 | Giá hoán đổi BĐS HP→TLSH | **Đóng phần số học**: 10.271 đ/cp ≈ mệnh giá, khớp tuyệt đối TN khác công ty mẹ 210,95 tỷ. Thẩm quyền: HĐQT đủ (<35%). **Mở**: lý do, thẩm định giá | Giá trị: không (sổ sách). **WARNING nặng hơn**: rủi ro chuyển giá trị 0–~1.500 đ/cp (ước lượng) |
| 3 | TLSH góp 18.655 / cổ đông / pháp lý dự án | **Chưa đóng.** Mới: HPG là thành viên liên danh BT [báo]; ông Hoàng Quang Việt đại diện vốn | WARNING: thêm lớp phơi nhiễm liên danh |
| 4 | Dòng tiền TLSH/liên danh | **Đóng một phần**: ký quỹ DH tăng 251 (không phải mới 499,9); công ty mẹ BCC 134,6 + cọc 361,2; khả năng 1.600 nằm trong "góp vốn" H1 (giả thuyết) ⇒ phần chưa truy ~1.370–1.870 (ước lượng) | Không |
| 5 | Cầm cố / covenant | **Chưa đóng** (không công bố, không có CBTT) | Không. WARNING giữ |
| 6 | Thuế DQ2 | **Đóng khung pháp lý** (QĐ 108/QĐ-BQL 2021; Luật 67/2025 bảo lưu ưu đãi, mở rộng hưởng theo dự án gốc). **Mở**: kết luận CV 377, ngày hết ưu đãi | Không (v2 đã đặt terminal 20%) |
| 7 | Kiểm toán | **ĐÓNG**: KPMG 2024 sạch → Deloitte 2025 qua quy trình ĐHĐCĐ; lý do không nêu | Không. Bỏ khỏi danh sách cờ |
| 8 | XK / EU / VSA | **Đóng một phần**: XK = 24,6% HRC; vùng 2024 (Bắc 35 / Trung 51 / Nam 22 / XK 61); EU nhỏ | Không |
| 9 | Quỹ ngoại | **ĐÓNG**: VOF 5,0%, VEIL 3,8%, VEOF 6,1%, VNM 5,01% | Không |
| 10 | β peer | **ĐÓNG (giới hạn)**: peer thanh khoản 0,9–1,1 | Không đổi vùng; nghiêng **không dời tâm lên** (β 1,0 ⇒ ~−1.200, ước lượng) |
| 11 | QĐ 1917 / 1902 / PVTM mới | **Đóng 1917** (chống lẩn tránh chính thức); 1902 chưa có hạn; không vụ mới nhắm HPG | Không; **sửa chữ** trong báo cáo |

## SỐ / CÂU trong báo cáo nhà đầu tư hiện hành cần SỬA

File: `investor_report/HPG_DD_investor_report_20261031.md` (Mike quyết định sửa; Taylor không sửa vòng này):

1. **Dòng 262** ("Số hiệu quyết định AD | Sai số hiệu | QĐ 1959…") và mọi chỗ nói "QĐ 1917 sai số hiệu":
   - sửa thành "QĐ AD gốc là **1959/QĐ-BCT**; **QĐ 1917/QĐ-BCT** là QĐ **chống lẩn tránh chính thức** (27,83%, hiệu lực 28/07/2026) [báo]";
   - REPORT.md:348 và đính chính sector_read của Bobby cũng phải nói đúng như vậy.
2. **Dòng 67 và 237**: thêm QĐ 1917 (chống lẩn tránh chính thức, thay QĐ 612 tạm thời).
3. **Dòng 136 và 248** ("≈2.973 tỷ góp vốn, ≈500 tỷ ký quỹ/BCC, 1.500 tỷ ứng liên danh"):
   - nhiều khả năng **đếm trùng ~1.500–1.600 tỷ** (giả thuyết §4a);
   - ký quỹ hợp nhất **tăng 251** (499,9 so với 248,9 đầu năm), không phải 500 mới;
   - viết lại: "đích chưa rõ ≈1,4–1,9 nghìn tỷ (ước lượng); 1.600 tỷ chuyển cho liên danh BT, số dư hợp nhất còn 100 tỷ sau khi BĐS HP rời hợp nhất (chưa xác nhận)".
4. **Dòng 134**: "ghi theo giá xấp xỉ mệnh giá" → bổ sung **"10.271 đ/cp, khớp lãi 210,95 tỷ ghi vào thu nhập khác của công ty mẹ Q3"**. Nêu rõ HPG giao **thêm 528,6 tr cp (~49,9% vốn BĐS HP)** so với phương án 32.000.
5. **Dòng 185 và 248**:
   - "2024 do hãng khác kiểm toán / tên hãng 2024 chưa đọc từ bản gốc" → "**KPMG** (chấp nhận toàn phần, BC số 22-02-00117-25-2); ĐHĐCĐ 2025 uỷ quyền TGĐ chọn trong 4 hãng Big-4";
   - có thể hạ mức cờ.
6. **Mục 6 TLSH / bảng R5**: thêm "HPG là **thành viên liên danh** Đại lộ cảnh quan sông Hồng cùng Đại Quang Minh, THACO [báo]". Nghĩa vụ góp vốn/bảo lãnh tương lai là rủi ro chưa thuyết minh.
7. (Nhỏ) **Dòng 81** "HRC 2025 ≈60%": ghi rõ mẫu số. VEOF 07/2026 dùng **~40%**. Tổng tài sản dùng ở §2 đã kiểm: 257.899,2 (31/12/25), 283.449,8 (30/9/26) [`calc/notes_bs.md:18`]. Theo số 30/9, 7.995 tỷ = 2,8%.
8. (Nhỏ, NHẬN ĐỊNH) Thu nhập khác hợp nhất Q3 485,6 có thể chứa phần hoán đổi. Ảnh hưởng tối đa lên lõi 9T ≈ −211 tỷ (≈ −1%) (ước lượng). Không đổi định giá forward.

## Đánh giá tác động lên định giá và WARNING

- **Vùng 18.000–22.500, tâm ≈20.200: KHÔNG ĐỔI (ước lượng).**
  - Hoán đổi ở mệnh giá không đụng sổ sách, nên không đụng RI.
  - β peer nghiêng xuống tối đa ~−1.200 đ/cp nếu thay β 0,915 bằng 1,0. Vẫn trong vùng; **lý do để không nâng tâm, không phải để hạ**.
  - Chồng trùng dòng tiền §4 **giảm** độ lớn "tiền chưa rõ đích", tức tin tốt nhẹ.
  - Rủi ro chuyển giá trị 0–~1.500 đ/cp (ước lượng) là **chi phí cơ hội quá khứ**, không trừ vào giá trị sổ sách hiện tại.
- **WARNING quản trị: GIỮ, NẶNG HƠN một bậc.** Ba lý do:
  1. Giá hoán đổi đã chứng minh bằng số gốc là ~1/3 giá NQ 10, không giải thích.
  2. HPG có ba lớp phơi nhiễm với hệ sinh thái Đại Quang Minh (cổ phần TLSH, 26,55% BĐS HP, thành viên liên danh BT).
  3. Bên mua của khoản lãi 4.929 tỷ không được công bố.
- Kiểm toán bị **hạ** khỏi danh sách cờ.
- **Mốc mới:** **H10**: BCTC kiểm toán 2026 thuyết minh bên mua Mỹ Hào/Đô thị xanh và nghĩa vụ của HPG trong liên danh BT (P ≈0,4, ước lượng; chấm 2027-04-15). Không công bố, hoặc có nghĩa vụ góp/bảo lãnh ≥2.000 tỷ ⇒ áp đuôi trái TLSH (−590 đ/cp) vào kịch bản trung lập.

## Đã thử nhưng chưa tìm được (vòng 4)

- Tên bên mua và giá từng thương vụ Mỹ Hào / Đô thị xanh / Phố Nối: BN TM1/TM34; CBTT HPG; masothue/thongtindoanhnghiep; báo.
- Lý do NQ 10 → NQ 13; tổ chức thẩm định giá; giải trình CBTT 01/10: CBTT HPG 22/07–31/10; báo cáo quản trị 6T/2026; 5 báo.
- Bên góp 18.655 tỷ; cổ đông/HĐQT TLSH sau tăng vốn; văn bản pháp lý Thư Lâm–Đông Anh; thoả thuận 02/2026/TTLD.
- CBTT cầm cố/giải chấp cổ phiếu HPG 2024–2026; covenant.
- Kết luận CV 377/TCT-CS; GCN đầu tư DQ2 (chỉ có QĐ 108/QĐ-BQL theo [báo]); ngày hết ưu đãi.
- XK theo nước; VSA thị phần theo vùng 2025/9T-2026; hạn ngạch EU riêng VN; giá bán/nhóm.
- iShares/DCDS tỷ trọng HPG.
- Hạn kết luận QĐ 1902; văn bản gốc QĐ 1917 trên moit.gov.vn.
- Chi tiết truy vấn/URL: `src/gaps2/web_A_governance.md`, `src/gaps2/web_B_tax_export.md`.
