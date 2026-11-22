# DD — VLB (CTCP Xây dựng và SX VLXD Biên Hòa, UPCoM) · 2026-11-22 · job `Taylor_20261122_094500`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua; không đặt lệnh, không wire. **Chưa qua fundamental-skeptic** (bước 5 skill — Mike gọi).
> Nguồn: **[Q3 p.x]** = `src/BCTC_Q3_2026.pdf` (BCTC riêng, không soát xét, duyệt 19/10/2026; số trang = trang PDF);
> **[H1 p.x]** = `src/BCTC_BanNien_2026.pdf` (soát xét A&C); **[NQ]** = `src/nhan_su_0617.pdf` (TB nhân sự + NQ ĐHĐCĐ 01/2026);
> **[HA]** = `src/HoaAn_thay_doi_so_huu.pdf`; **[BQ]** = `tav2_bq.ticker_financial` / `tav2_bq.ticker`; báo chí ghi rõ cạnh số.
> Sổ đọc chi tiết từng trang: `notes_raw.md`. Mô hình: `model/dcf_vlb.py` (chạy `python3 -I model/dcf_vlb.py`).
> Số không đo được gắn **(ước lượng)**. Định giá MÙ giá thị trường; giá 48.100 (20/11) chỉ dùng cho thanh khoản và so sánh cuối (§8).

## 0. Kết luận

**Nhận định (chưa qua skeptic): giá trị nội tại tâm ≈ 61.800 đ/cp sau chiết khấu thanh khoản (63.700 trước CK), vùng [42.300; 83.000].**
Giá 48.100 ở **dưới 0,85 × tâm (52.500) ⇒ nhãn RẺ theo quy ước**, nhưng vẫn **trên** kịch bản xấu (42.300), và biên an toàn phụ thuộc
một giả định chưa kiểm được: **mỏ còn ~12–18 năm khai thác** (chưa có bảng giấy phép).

Những gì sai trong số báo chí Mike đã đọc:
- **"Hoàn nhập ~344 tỷ" không phải tiền mặt.** Đó là tiền cấp quyền **nộp thừa** giai đoạn 2014→6/2025 (Thuế TP Đồng Nai xác định, thông báo 29/5
  và 02/6/2026). Khoản này được **bù trừ vào tiền cấp quyền các kỳ sau**, theo điểm c khoản 8 Điều 139 NĐ 193 [Q3 p19 V.17; p24 VI.6].
  Nó nằm ở mã 163 với số dư **329,36 tỷ**. Theo tốc độ cấn trừ Q3, khoản này dùng hết sau khoảng **6,9 năm**; giá trị hiện tại (PV) là
  **206 tỷ ≈ 4.400 đ/cp**. Thuế TNDN 20% tính trên khoản này (~68,8 tỷ) **đã nộp bằng tiền**.
- **"Tiền nhàn rỗi >800 tỷ" đúng về số tổng, sai về bản chất**: tiền 27,6 + tiền gửi HTM 785,0 = **812,6 tỷ**, không có nợ vay.
  Net cash **THẬT** chỉ **527,5 tỷ ≈ 11.290 đ/cp**, sau khi trừ: quỹ khen thưởng phúc lợi 107,5; thuế phải nộp 61,7; phần giá vốn của tiền
  khách ứng trước 51,5; vốn lưu động ròng 64,3. Trong đó **20,5 tỷ tiền gửi đang cầm cố** để bảo lãnh dự án [Q3 p15].
- **Cổ tức 1.900 đ/cp không chia từ khoản hoàn nhập.** Đây là đợt 2 của **cổ tức 2025, tổng 4.900 đ/cp = 228,9 tỷ**, lấy từ LNST 2025 đã
  kiểm toán là 301,4 tỷ [Q3 p22 23d; NQ p2-3]. Kế hoạch cổ tức 2026 là **tối thiểu 3.500 đ/cp** [NQ p3].
- Không có mảng vận tải, xây dựng hay bán lẻ đáng kể: **đất và đá chiếm 99,9% doanh thu 9T** [Q3 p23].

Các số báo chí **khớp** BCTC: Q3 DT 442,08 (+34,8%), LNST 117,41 (+86,2%), biên gộp 34,6% vs 25,1% [Q3 p5].
Phần sai là cách hiểu khoản 344 tỷ. Q2/26 LNST 374,4 tỷ [BQ], khớp H1 448,56 − Q1 74,1.

**Pháp lý: WARNING, không có vụ án** (§7). Vấn đề lớn nhất là **rủi ro đảo chiều/hồi tố khoản tiền cấp quyền**. Lịch sử của chính khoản này
đã đảo chiều một lần: năm 2022 VLB phải nộp bổ sung khiến Q3/22 lỗ 224 tỷ; năm 2026 cơ quan thuế lại xác định VLB nộp thừa.
Ngoài ra: Thanh tra Chính phủ và Kiểm toán Nhà nước từng có kết luận về giấy phép Soklu và về đất.

## 1. Chất lượng lợi nhuận — Q3 và 9T

| Tỷ đồng | Q3/26 | Q3/25 | 9T/26 | 9T/25 | Nguồn |
|---|---|---|---|---|---|
| Doanh thu thuần | 442,08 | 328,02 | 1.233,93 | 1.075,37 | [Q3 p5] |
| GVHB | 289,05 | 245,55 | 826,61 | 785,03 | [Q3 p5] |
| LN gộp (biên) | 153,04 (34,6%) | 82,47 (25,1%) | 407,32 (33,0%) | 290,34 (27,0%) | [Q3 p5] |
| DT tài chính (lãi tiền gửi) | 17,81 | 7,84 | 25,19 | 14,48 | [Q3 p5, p23] |
| BH + QLDN | 27,09 | 22,17 | 76,56 | 67,58 | [Q3 p5] |
| Thu nhập khác ròng | 3,04 | 10,72 | 351,66 | 13,76 | [Q3 p5] |
| — trong đó nộp thừa tiền cấp quyền | 0 | 0 | **343,93** | 0 | [Q3 p24] |
| LNST | 117,41 | 63,05 | 565,97 | 200,71 | [Q3 p5] |
| **LNST lõi** (bỏ 343,93 × 0,8) | 117,41 | 63,05 | **290,83** | 200,71 | tính |

- **Sản lượng × giá:** sản lượng đá tiêu thụ Q3/26 là **1.991.462 m³**, so với 1.671.923 m³ cùng kỳ (**+19,1%**) [Q3 p28 giải trình].
  DT/m³ ≈ **221.990 đ** vs 196.200 (**+13,1% yoy**; tính trên toàn bộ DT, gồm cả đất san lấp).
  - **H1 khác hẳn Q3:** DT H1 chỉ +6%. Đất các loại đạt 435.411 m³, tăng 10,6 lần (+1.057%) [H1 p42] ⇒ cơ cấu bán dịch sang đất trong H1.
  - DT Q3 (442,1) gần như đi ngang so với Q2 (440,3) [BQ]. Sản lượng tăng cùng kỳ là chính; giá tăng là phần phụ.
  - Kết quả này **nhất quán** với số của Bộ XD (giá đá Q3 +3,9 đến 5,8% qoq, bình quân cả nước). Tuy vậy, DT/m³ của VLB tăng 13% yoy,
    nhanh hơn ⇒ một phần nhờ cơ cấu sản phẩm (chưa tách được).
- **Biên gộp +9,5pp yoy:** 9T GVHB chỉ +5,3% trong khi DT +14,7%. Theo thuyết minh, các cấu phần chi phí 9T [Q3 p19-21, p25 VI.9]:
  - thuế tài nguyên 123,7 tỷ (10%, tính trên phần giá bán bình quân vượt giá quy định QĐ 62/2025/QĐ-UBND);
  - phí BVMT 44,8 tỷ (4.507,8 đ/tấn); thuê đất 33,8; tiền cấp quyền chính 14,6.
  - Cần kiểm: **tiền cấp quyền hạch toán theo NĐ 193 (theo sản lượng thực) có thấp hơn mức phân bổ cũ không?** Nếu có, một phần biên mới
    là "rẻ hơn về thể chế", không phải giá. Chưa tách được vì thiếu thuyết minh cấu phần GVHB theo quý.
- **Doanh thu tài chính:** 9T = 25,19 tỷ, toàn bộ là lãi tiền gửi có kỳ hạn [Q3 p23]. Q3 riêng 17,81 tỷ trên số dư HTM ~785 tỷ ≈ **9%/năm**,
  cao bất thường so với lãi huy động. Chỉ tiêu lãi dự thu giảm từ 7,37 xuống 0,01 tỷ [Q3 p15] ⇒ có khả năng **dồn lãi khi đáo hạn**.
  Run-rate bền khoảng 5–6% × 785 ≈ 40–47 tỷ/năm (ước lượng). Mô hình KHÔNG đếm lãi này, vì đã cộng tiền mặt theo mệnh giá.
- **LN bền và một lần:**
  - TTM lõi = Q4/25 100,73 [NQ: 301,44 − 9T/25 200,71] + 9T/26 lõi 290,83 = **391,6 tỷ** (EPS lõi ≈ 8.380 đ).
  - Bỏ lãi tiền gửi sau thuế (~24 tỷ, ước lượng) ⇒ LN vận hành TTM ≈ **367 tỷ**.
  - Một lần: 343,93 trước thuế (275,1 sau thuế), ghi nhận Q2/26.
- **Lịch sử LNST năm [BQ]:** 2017 149 · 2018 142 · 2019 131 · 2020 182 · 2021 161 · **2022 −51** (Q3/22 −224, CFO −250: nộp bổ sung tiền cấp
  quyền 2014-2021, >270 tỷ theo nguoiquansat) · 2023 143 · 2024 218 · 2025 301 · TTM lõi 392.
  ⇒ Mức hiện tại là **đỉnh lịch sử**, gấp ~2,5 lần trung vị 2017–2023.

## 2. Tiền cấp quyền khai thác — nghĩa vụ, hạch toán, rủi ro

- **Hạch toán [Q3 p19 V.17 chú thích (i); p24 VI.6 chú thích (**)]:**
  - Khoản nộp thừa 343,93 tỷ phát sinh từ quyết toán 2014→6/2025, căn cứ các TB 9521/9522/9530/TB-DON (29/5/2026) và 9722/9725/TB-DON
    (02/6/2026) của Thuế TP Đồng Nai.
  - Được bù trừ vào nghĩa vụ các kỳ sau (điểm c khoản 8 Điều 139 NĐ 193/2025). Ghi Nợ 163 / Có thu nhập khác.
  - 9T đã cấn trừ 14,57 tỷ tiền cấp quyền chính ⇒ số dư **329,36 tỷ** (30/6: 341,26 [H1 p8]) ⇒ tốc độ cấn trừ Q3 là **11,9 tỷ/quý ≈ 47,6 tỷ/năm**.
- **Cơ sở pháp lý:** NĐ 193 Điều 139 quyết toán theo **sản lượng thực khai thác** (Bobby §2.5). Sản lượng thực giai đoạn 2014–6/2025 thấp
  hơn trữ lượng cấp phép đã tính tiền ⇒ nộp thừa. Đây là văn bản hành chính của cơ quan thuế, có số hiệu; **kiểm toán soát xét bán niên
  chấp nhận toàn phần, không nhấn mạnh** [H1 p7].
- **Rủi ro đảo chiều (WARNING, không đưa vào base):**
  - (a) Khoản này **chưa qua kiểm toán năm** (BCTC 2026 kiểm toán dự kiến ~03/2027).
  - (b) Tiền lệ đảo chiều: năm 2022 VLB phải nộp **bổ sung**, năm 2026 lại được xác định nộp **thừa** cho cùng giai đoạn ⇒ phương pháp tính
    đã đổi một lần, có thể đổi lần nữa khi Kiểm toán Nhà nước hoặc Thanh tra rà soát.
  - (c) Phần "trữ lượng chưa khai thác được duyệt lại" (Đ139) có thể sinh nghĩa vụ mới khi điều chỉnh giấy phép hoặc hạ cote.
  - (d) Thuế TNDN 68,8 tỷ đã nộp bằng tiền; nếu khoản này bị huỷ thì có thể xin hoàn, nhưng chậm (ước lượng).
- **Không có số trong BCTC:** nghĩa vụ tiền cấp quyền **còn lại** theo quyết định phê duyệt, mức R áp dụng, ký quỹ đóng cửa mỏ đầy đủ
  ⇒ **cần BCTC năm 2025 kiểm toán + quyết định phê duyệt tiền cấp quyền** (chưa tải được, §9).
- **Phí BVMT và hoàn nguyên:**
  - Ký quỹ cải tạo PHMT 5 mỏ: 38,88 tỷ [Q3 p16 V.5b]; dự phòng hoàn nguyên 16,22 tỷ [Q3 p21 V.22]. Ký quỹ lớn hơn dự phòng 22,7 tỷ, mô hình
    không cộng phần chênh này.
  - Soklu 2 và Soklu 5 **không trích thêm dự phòng trong 9T** ⇒ nhiều khả năng không còn khai thác (suy luận).

## 3. Bảng cân đối, CFO, tài sản bảo đảm [Q3 p2-6]

| Tỷ đồng, 30/9/2026 | |
|---|---|
| Tiền 27,58 + HTM 785,01 | 812,59 |
| − Quỹ khen thưởng phúc lợi (tiền của NLĐ) | −107,47 |
| − Thuế phải nộp | −61,75 |
| − Giá vốn phần khách ứng trước (76,94 × (1 − 33,0%)) | −51,5 |
| − Vốn lưu động ròng (phải trả NB 37,56 + NLĐ 54,21 + khác 0,38 − tồn kho 20,13 − phải thu 2,76 − trả trước 4,16 − phải thu khác 0,79) | −64,3 |
| **Net cash THẬT** | **527,5 (11.290 đ/cp)** |
| Khoản bù trừ tiền cấp quyền (163), phi tiền mặt | 329,36 → PV 205,7 (@13,5%) / 254,2 (@7%) |
| Vay | 0 |

- **Phải thu nhà thầu gần như bằng 0:** phải thu KH 2,76 tỷ, không có nợ quá hạn [Q3 p16-17]. Khách ứng trước tăng 37,1 → 76,9 tỷ, gồm
  TCT XD Trường Sơn 28,8, TCT 319 BQP 5,1, KCN Xuân Quế 5,3, KCN Tân Hiệp 4,1 [Q3 p19 V.15].
  ⇒ **VLB bán thu tiền trước**: vị thế đàm phán tốt, trái với rủi ro "phải thu nhà thầu" Bobby nêu (mục C14).
- **CFO 9T: 264,3 tỷ** [Q3 p6]:
  - Dòng "tăng phải thu" −314,6 tỷ là bút toán đối ứng khoản bù trừ phi tiền mặt.
  - Thuế TNDN đã nộp 137,8 tỷ, gồm ~68,8 tỷ thuế trên khoản một lần ⇒ CFO lõi ≈ **333 tỷ**, so với LNST lõi 290,8 ⇒ **CFO/LN ≈ 1,15**.
  - Capex chỉ 1,13 tỷ; khấu hao 8,0. Chi phí mỏ thật đi qua **chi phí trả trước dài hạn (đền bù đất mỏ) 286,8 tỷ**: Thạnh Phú 1 81,0,
    Tân Cang 1 83,4, Thiện Tân 2 107,1 [Q3 p18].
  - Cổ tức đã trả 228,9 tỷ.
- **Tài sản bảo đảm:** chỉ có 20,5 tỷ HTM cầm cố bảo lãnh thực hiện dự án [Q3 p15]. Không có vay ⇒ không có quyền khai thác nào đem thế
  chấp (Bobby mục E24: **đạt**).

## 4. Giấy phép, trữ lượng, đồng hồ cắt hào

**BCTC KHÔNG có bảng giấy phép.** Số dưới đây lấy từ báo chí, chưa đối chiếu văn bản gốc:

| Mỏ | Trữ lượng nguyên khối còn lại 1/1/2025 | Tình trạng | Nguồn |
|---|---|---|---|
| Thạnh Phú 1 (Vĩnh Cửu) | 35,59 tr m³ | Đất thuê tới 31/7/2042 (QĐ 1537/QĐ-UBND 12/5/2025); có bến thủy nội địa + băng tải [Q3 p17] | stockbiz |
| Thiện Tân 2 (Vĩnh Cửu) | 22,7 tr m³ | Đang khai thác (trích dự phòng 9T) | stockbiz |
| Tân Cang 1 (Biên Hòa) | 22,65 tr m³ (GĐ nói >24 tr, 2/2025) | Đang xử lý >22 ha diện tích **đã hết hạn** (2/2025) | stockbiz |
| Soklu 2, Soklu 5 (Thống Nhất) | ? | Soklu 2 gia hạn lên >12 năm kể từ 23/3/2011 (⇒ ~2023); Thanh tra CP ⇒ Đồng Nai rà soát GP 2 mỏ Soklu; không trích dự phòng 9T | thoibaotaichinh, stockbiz |

- **Ước tính số năm còn khai thác (ước lượng):**
  - Phí BVMT 9T 44,85 tỷ ÷ 4.507,8 đ/tấn ≈ 9,95 tr tấn ≈ 3,8 tr m³ nguyên khối (tỷ trọng ~2,6 t/m³) ⇒ khai thác **~5,1 tr m³/năm**.
  - Tổng trữ lượng 1/1/2025 ~81 tr m³ − 2 năm khai thác ⇒ còn **~71 tr m³ ⇒ ~14 năm** ở tốc độ hiện tại.
  - Hợp đồng thuê đất 2015–2047 (báo chí). Mô hình: xấu 12 / cơ sở 15 / tốt 18 năm.
- **Công suất được phép vs thực tế:** chưa có số từng mỏ. Báo chí ghi tổng công suất ~4 tr m³/năm (không rõ là nguyên khối hay thành phẩm).
  VLB **đề nghị không nâng 50% công suất** vì giới hạn thiết bị. Như vậy "hạn chế công suất khai thác" là ràng buộc thật, nhưng một phần
  do chính VLB chọn.
- **NĐ 21/2026 (Điều 63 cho cấp lại GP sau hết hạn nếu còn trữ lượng):** có lợi trực tiếp cho Tân Cang 1. Chưa thấy VLB dùng cơ chế này
  (cần CBTT).

## 5. Vị thế cạnh tranh (5F) — TÁI DÙNG tag 2026-06-05 (<12 tháng)

`data/moat_tags.csv`: **VLB = NARROW / LOCATION** (asof 2026-06-05, 5f_validated_compet): 6 mỏ Đồng Nai cụm Tân Cang, ROIC_Min5Y 22,6%.
Rủi ro số 1 là trữ lượng hữu hạn và trần gia hạn giấy phép của tỉnh. **Giữ nguyên, không thưởng, không trừ.**

Kiểm nhanh (từ BCTC đang đọc, không nghiên cứu mới):
- **Hào hẹp lại:** Soklu 2/5 có dấu hiệu ngừng (không trích dự phòng 9T) ⇒ còn **3 mỏ chủ lực**, tức tập trung hơn.
- **Hào rộng ra:**
  - Khách ứng trước tiền, phải thu ≈ 0 ⇒ vị thế bán mạnh.
  - Có bến sà lan Thạnh Phú/Thiện Tân ⇒ với tới được ĐBSCL.
  - NĐ 21/2026 Điều 63 cho cấp lại giấy phép.
  - Khoản bù trừ 329 tỷ làm giảm chi phí tiền mặt khoảng 7 năm.
- **Đồng hồ:** ~14 năm (ước lượng). **Kết luận: không đổi tầng.**

Độ nhạy theo moat (base 64.744 trước CK):
- **WIDE:** không đổi, vì mô hình không có tham số moat.
- **NONE** (đời mỏ −3 năm / lợi nhuận siêu ngạch fade sớm): **60.071 (−7%)**.

Giả định ngầm cần ghi: base giữ LN vận hành phẳng thực trong 15 năm, tức ROIC ≫ Ke suốt đời mỏ. Đây là **tô vị trí của trữ lượng hiện
có**, không phải thưởng moat. Không có terminal value, và mỏ mới có NPV = 0.

## 6. Cổ đông, thanh khoản, sizing, cổ tức

- **Cổ đông [Q3 p22 23b, p26]:**
  - **Dofico (TCT Công nghiệp Thực phẩm Đồng Nai, vốn tỉnh) 49,08%**.
  - **Cty TNHH ĐTPT Công nghiệp KSB 21,95%** (103,0 tỷ mệnh giá).
  - **CTCP Hóa An (= DHA, peer niêm yết) 10,05%**.
  - Khác 18,92%, gồm 201.040 cổ phiếu quỹ.
  - Bên liên quan cùng thành viên quản lý chủ chốt: DRH Holdings và CTCP Khoáng sản & XD Bình Dương (KSB) [Q3 p26].
  - ⇒ **Free float thực ≈ 18,5%** (~8,6 tr CP).
- **Hóa An [HA]:** mua 68.900 CP ngày 20/8/2026, nâng sở hữu từ 9,94% lên **10,09%** (cùng người liên quan 10,15%), lý do "tăng tỷ lệ
  sở hữu". Đây là tín hiệu tích luỹ của một cổ đông trong ngành.
- **"KSB đầu tư 610 tỷ" — KHÔNG kiểm được từ BCTC VLB** (BCTC chỉ cho mệnh giá 103,0 tỷ). Giá vốn khoản đầu tư nằm trong BCTC KSB, chưa đọc.
- **Room ngoại:** chưa kiểm. Cổ đông trong nước nắm ~81% ⇒ room không ràng buộc thực tế.
- **Thanh khoản [BQ, `model/px_vlb.csv` md5 e2e14c30…]:**
  - ADV trung vị Price×Volume = **1,14 tỷ** (250 phiên) / **0,92 tỷ** (68 phiên); σ ngày 1,34%; spread Corwin-Schultz 0,35%.
  - Chiết khấu thanh khoản theo quy ước fleet (SCL r3/TTA r3): d(0,5 tỷ) **1,06%** · d(1 tỷ) **1,43%** · **d(5 tỷ, tham chiếu) 2,98%**.
  - Số phiên thoát ở 20% ADV: 2,2 phiên (0,5 tỷ) / 4,4 (1 tỷ) / 21,8 (5 tỷ).
  - **Sizing:** ≤0,5–1,0% NAV theo tiền lệ; vị thế >2–3 tỷ đã cần >10 phiên để thoát.
- **Cổ tức:** 2025 trả 4.900 đ/cp, bằng 76% LNST 2025, từ LN lõi [Q3 p22]. Kế hoạch 2026 tối thiểu 3.500 đ.
  - EPS lõi TTM ≈ 8.380 đ và net cash thật 11.290 đ/cp ⇒ khả năng chia **5.000–6.500 đ** cho 2026 (ước lượng, theo payout 60–75%).
  - **Khoản hoàn nhập không tạo ra tiền để chia** (phi tiền mặt). Cổ tức bền dựa trên LN lõi, không chia dồn.

## 7. Pháp lý / quản trị — chỉ WARNING (luật 2026-09-27)

- ⚠️ **Tiền cấp quyền:** tiền lệ đảo chiều 2022↔2026 (§2). Kiểm toán năm 2026 chưa có.
- ⚠️ Thanh tra Chính phủ ⇒ Đồng Nai rà soát gia hạn GP Soklu 1, 2, 5. Kiểm toán Nhà nước kiến nghị xử lý nhiều khu đất sử dụng không đúng
  mục đích (vnbusiness; chưa đọc văn bản gốc, chưa rõ năm).
  **Scandal di cư:** chưa thấy vụ việc lan sang 3 mỏ chủ lực. Rủi ro cần theo dõi: rà soát giấy phép mở rộng sang Tân Cang 1 (phần diện
  tích đã hết hạn).
- ⚠️ **Quản trị chéo** Dofico–KSB–Hóa An–DRH: cùng thành viên quản lý chủ chốt. **Không có giao dịch bán hàng với bên liên quan** [Q3 p23
  VI.1b]; giao dịch duy nhất là cổ tức [Q3 p27]. Rủi ro chuyển giá chưa thấy trong số liệu.
- ⚠️ Dofico 49% là vốn tỉnh: thoái vốn có thể là chất xúc tác theo **hai chiều** (giá đấu giá; người mua chiến lược có thể là KSB/DHA).
- **Nhân sự:** BKS Nguyễn Thị Thanh Trúc từ nhiệm vì "lý do cá nhân", thay bằng Trương Nguyễn Ngọc Hòa từ 16/6/2026 [NQ p1]. GĐ và 1 PGĐ
  tái bổ nhiệm 23/7/2026 [H1 p5]. Chưa thấy dấu hiệu bất thường.
- Thù lao HĐQT/BĐH/BKS 9T: 8,36 tỷ (+28% yoy) [Q3 p25].
- **Kiểm toán:** A&C (Baker Tilly). Soát xét H1/26 chấp nhận toàn phần [H1 p7]. **Ý kiến BCTC 2025 kiểm toán: CHƯA đọc** (không tải được, §9).
  NQ ĐHĐCĐ chỉ ghi "được kiểm toán bởi A&C" [NQ p2].
- Nợ khó đòi đã xoá sổ 5,59 tỷ, ghi ngoại bảng [Q3 p23].

## 8. Định giá (MÙ giá thị trường) — `model/dcf_vlb.py`

**Chi phí vốn:**
- r = **13,5%** (Ke nội địa, điểm neo). Lãi huy động 12T hiệu dụng **7,4%** tại điểm neo 03/11 và 18/11 (CCTG 12M; DD POW 18/11).
- `deposit_rate_vn` Big-4 12M online = **6,8%** (mốc 16/11/2026, `data/deposit_rate_vn_events.csv`) < CCTG ⇒ hiệu dụng không đổi ⇒ **r giữ 13,5%**.
- Độ nhạy theo lãi huy động (β = 1; β = 0,5 trong ngoặc): **−100bp ⇒ +4,6%** (66.621; 65.124) · −50bp ⇒ +2,2% · +50bp ⇒ −2,2% ·
  **+100bp ⇒ −4,2%** (61.011; 62.323).

**Khung định giá:** giá trị = PV(LN vận hành sau thuế, **đời mỏ hữu hạn, không terminal**) + PV khoản bù trừ tiền cấp quyền + net cash thật.
- FCFE ≈ LN vận hành, vì capex ≈ khấu hao rất nhỏ và CFO/LN ≈ 1,15.
- Mỏ mới / mở rộng / hạ cote = **NPV 0** (luật 11-03).

| Kịch bản (xác suất) | LN vận hành năm 1 (ước lượng) | Đời mỏ / g | Khoản bù trừ | Giá trị đ/cp |
|---|---|---|---|---|
| **Xấu (25%)** | 250 tỷ: sản lượng −15% khi Long Thành/VĐ3 rút; tỉnh khống chế giá (G9); ≈ mức 2024–25 | 12 năm / 0% | **Đảo lại = 0** | **42.255** |
| **Cơ sở (50%)** | 330 tỷ: −10% so với TTM 367, chuẩn hoá cầu; giữa 2025 (~290) và run-rate Q3 (~410) | 15 năm / 2% | 205,7 | **64.744** |
| **Tốt (25%)** | 400 tỷ: giá +1%/tháng tiếp diễn, VĐ4/Bắc–Nam; Tân Cang 1 cấp lại theo NĐ 21 | 18 năm / 3% | 205,7 | **83.026** |
| **Tâm có trọng số** | | | | **63.693 trước CK · 61.798 sau CK (Q = 5 tỷ) · 62.784 (Q = 1 tỷ)** |

- **Cơ sở dữ liệu cho mọi khoản giảm trừ trong base:**
  - LN −10% so với TTM: TTM là đỉnh lịch sử, gấp 2,5 lần trung vị 2017–23 [BQ]; Bobby §2.6 cho thấy dư cầu đá đang thu hẹp (Ban GT
    TP.HCM, 30/10/2026).
  - Đời mỏ 15 năm: trữ lượng báo chí ÷ sản lượng suy từ phí BVMT (§4).
  - Không có giảm trừ nào khác trong base. Rủi ro hồi tố chỉ nằm ở kịch bản xấu.
- **PE / PB / comp (giá peer chỉ để so sánh bội số, không suy giá trị VLB):**
  - Tâm sau CK ngụ ý **PE lõi TTM 7,4x**; bỏ net cash và khoản bù trừ thì **5,9x** LN vận hành.
  - Peer BQ 20/11/2026, PE TTM (gồm một lần nếu có): **NNC 4,9x / PB 1,6** · **DHA 5,9x / 1,57** · KSB 6,8x / 0,48 (KSB có mảng BĐS/KCN,
    không thuần đá).
  - ⇒ Tâm VLB cao hơn nhóm khoảng 1–2x PE. Lý do: (i) net cash lớn; (ii) phải thu ≈ 0; (iii) khoản bù trừ.
  - Nhóm mỏ đá niêm yết đang được định giá **thấp đồng loạt** (4,9–5,9x). Tức là thị trường chiết khấu đời mỏ hữu hạn mạnh hơn mô hình này.
  - PB trên VCSH lõi (1.181,7 − 275,1 = 906,6 tỷ): tâm tương ứng ~3,2x. ROE lõi ~40%.
- **Hai nền giá trị (HIỂN THỊ, không đổi tâm):**

  | Nền | đ/cp | Ghi chú |
  |---|---|---|
  | V_ngắn (LNST chuẩn hoá = trung vị {2024 218,0; 2025 301,4; TTM lõi 391,6} = 301,4; tái đầu tư g/ROE = 0,02/0,40; vĩnh viễn) | 53.299 | Vĩnh viễn ⇒ không phản ánh đời mỏ hữu hạn |
  | V_dài (DCF FCFE kịch bản cơ sở) | 64.744 | |
  | **D = \|ln(V_ngắn/V_dài)\| = 0,195** < ln2 | — | Không cờ phân kỳ |
  | V theo C4 = CFO3 (TB 2024, 2025, TTM lõi = 322,8) − min(capex 2, KH) | 59.707 | "chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi" |
  | V theo D2 = CFO3 − 11,26% (capex/DT trung vị 4 mã đá 12 quý [BQ]) × DT TTM 1.614 | 26.246 | "chưa qua tiêu chí khoá trước (0/9 nền qua…), chỉ theo dõi". **Lệch mạnh vì VLB ghi chi phí mỏ qua đền bù/trả trước, không qua capex** (NNC 20%, KSB 30% là mua mỏ mới) ⇒ D2 phạt nhầm |

- **Vùng giá (sau CK, Q = 5 tỷ):** RẺ ≤ **52.500** (0,85 × tâm) · trung tính 52.500–71.000 · đắt > ~71.000 (1,15 × tâm) (ước lượng quy ước).
  Cận xấu **42.300**, cận tốt **83.000**.
- **So sánh sau cùng:** giá 48.100 (20/11) = **0,78 × tâm** ⇒ ở vùng RẺ, cao hơn cận xấu 14%.
- **Điều thị trường chưa tính (theo đọc của tôi; chưa kiểm định):**
  - (1) Khoản bù trừ 329 tỷ là **tiền tiết kiệm thật ~7 năm** chứ không phải "lãi ảo một lần". Báo chí gọi là "hoàn nhập một lần" ⇒ dễ bị
    loại hẳn khỏi giá trị.
  - (2) Phải thu ≈ 0 và khách ứng trước tiền ⇒ chất lượng LN cao hơn nhóm peer.
  - (3) Bến sà lan ⇒ với tới ĐBSCL, nơi thiếu đá tại chỗ.
  - Bối cảnh vĩ mô (snapshot 22/11, chỉ dòng `ok`, chỉ hiển thị): IIP +15,0% yoy (T10), GDP +9,95% (Q3), FDI luỹ kế +13,05% yoy.
    GDP xây dựng: **STALE, chưa có số**. Không đổi giá trị theo vĩ mô.

## 9. Mốc khoá trước + điều kiện đổi nhận định (CẢ HAI chiều) — khoá 2026-11-22

| Mốc | Ngày chấm | Ngưỡng |
|---|---|---|
| M1 BCTC Q4/2026 | ~20/01/2027 | Sản lượng đá Q4 ≥ 1,85 tr m³ **và** DT/m³ ≥ 215.000 đ |
| M2 Số dư 163 cuối 2026 | ~20/01/2027 | Giảm 8–16 tỷ so với 329,36 (đúng tốc độ cấn trừ); không có khoản phải nộp bổ sung tiền cấp quyền |
| M3 BCTC kiểm toán 2026 | ~31/03/2027 | Chấp nhận toàn phần; không ngoại trừ/nhấn mạnh về 343,93 tỷ |
| M4 Cổ tức 2026 (ĐHĐCĐ 2027) | ~06/2027 | Tổng ≥ 5.000 đ/cp |

- **Đổi LÊN** (tâm tăng):
  - Tân Cang 1 / Thiện Tân 2 được gia hạn hoặc cấp lại / hạ cote với thời hạn ≥ 10 năm (đời mỏ cơ sở 15 → 18 năm ⇒ cơ sở 64.744 → 68.136, tâm +1.696 đ/cp; đo bằng `dcf_vlb.value`).
  - Giá đá Q4/26 > +3% qoq (Bobby G1) và M1 vượt.
  - Mỗi +10 tỷ LN vận hành cơ sở ⇒ **+743 đ/cp tâm**.
  - Lãi huy động −100bp ⇒ +4,6%.
- **Đổi XUỐNG:**
  - Thông báo truy thu, hoặc kiểm toán/Kiểm toán Nhà nước huỷ khoản bù trừ ⇒ −4.400 đ/cp (base), xấu hơn nếu phải nộp bổ sung.
  - Rà soát giấy phép lan sang 3 mỏ chủ lực.
  - Sản lượng Q4 < 1,6 tr m³.
  - Văn bản khống chế giá bán đá tại mỏ (G9).
  - Lãi huy động +100bp ⇒ −4,2%.
  - Ý kiến kiểm toán 2025/2026 có ngoại trừ.
- **CHƯA CÓ (đã thử, không bịa):**
  - BCTC 2025 kiểm toán và các năm trước: không tải trong phiên này. Mike đã thử bbcc.com.vn và FPTS IR; tôi chỉ tìm được NQ ĐHĐCĐ xác nhận
    LNST 2025 = 301,44 tỷ.
  - Bảng giấy phép (số, ngày hết hạn, công suất, cote): không có trong BCTC.
  - ⇒ **Hai việc ưu tiên trước khi user xét mua:** (1) BCTC năm 2025 kiểm toán (ý kiến + thuyết minh tiền cấp quyền/giấy phép); (2) quyết
    định phê duyệt tiền cấp quyền + giấy phép 3 mỏ từ Sở NN&MT Đồng Nai.

## 10. Cho Mike ghi sổ (sau skeptic)
- `assumptions_file`: `agents/Taylor/research/dd_VLB_20261122/model/dcf_vlb.py`, **md5 `f80cd48a61c74b09b66807e6bc14f59f`**
  (dữ liệu thanh khoản `model/px_vlb.csv` md5 `e2e14c30822583579cd6957df127d318`).
- Đề xuất zone: tâm **61.798** (sau CK, Q = 5 tỷ) · RẺ ≤ 52.500 · cận xấu 42.255 · cận tốt 83.026.
- Không ghi v_short / v_long / D vào sổ (luật 11-11).

## Phụ lục — nguồn web (chưa đối chiếu văn bản gốc)
- Nộp thừa 310 tỷ / 3 mỏ (29/5/2026): https://24hmoney.vn/news/cuc-thue-xac-dinh-vlb-nop-thua-hang-tram-ty-tien-cap-quyen-khai-thac-khoang-san-co-phieu-tang-nong-c1a2789578.html ; https://doanhnhan.baophapluat.vn/vat-lieu-xay-dung-bien-hoa-vlb-nop-thua-hon-310-ty-dong-tien-cap-quyen-khai-thac-khoang-san.html
- 2022 nộp bổ sung >270 tỷ / kế hoạch lỗ: https://nguoiquansat.vn/san-xuat-vat-lieu-xay-dung-ptag.html ; https://baodauthau.vn/vat-lieu-xay-dung-bien-hoa-bat-ngo-dat-ke-hoach-lo-trong-nam-2022-post125002.html
- Trữ lượng 3 mỏ, đất Thạnh Phú 1: https://stockbiz.vn/tin-tuc/vlb-vua-bao-lai-khung-nam-2024-vlb-duoc-go-vuong-mo-da-thanh-phu-1/32384948
- Rà soát GP Soklu (Thanh tra CP): https://thoibaotaichinhvietnam.vn/dong-nai-tien-hanh-ra-soat-giay-phep-2-mo-da-cua-vlb-sau-ket-luan-cua-thanh-tra-chinh-phu-138881.html ; https://stockbiz.vn/tin-tuc/tinh-dong-nai-yeu-cau-ra-soat-lai-viec-gia-han-giay-phep-khai-thac-cac-mo-da-soklu-1-2-va-5/21304273
- Kiểm toán NN về đất: https://vnbusiness.vn/khong-su-dung-dung-muc-dich-nhieu-khu-dat-cua-vlb-bi-kien-nghi-xu-ly.html
- Ngành: `kb/data_registry/market-state/sector_read_da_xay_dung_dnb_20261122.md` (Bobby, blind).
