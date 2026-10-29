# DD — PVP (CTCP Vận tải Dầu khí Thái Bình Dương / PVTrans Pacific, HOSE) · 2026-10-29 · job `Taylor_20261029_065413`

**Verdict: AMBIGUOUS @18.750 (giá sàn DNSE 13:58 29/10). Không QUALIFY theo §2/§2.5 vì đây là ĐỈNH chu kỳ, không phải đáy. Giá trị hợp lý 12,2–23,1k (ước lượng), tuỳ phương pháp; giá hiện tại nằm GIỮA dải và không có biên an toàn. Chỉ chạy lại DD khi giá ≤ ~15.500 HOẶC khi ĐHĐCĐ bất thường (hạn ≤30/11/2026) công bố giá mua tàu.**

> Chỉ NGHIÊN CỨU. Không phải khuyến nghị mua, không lệnh, không wire. Người quyết định là user.
> **Nguồn.** **[Q3 pN]** = `src/bctc_q3_2026.pdf`, trang PDF N (scan, chưa soát xét, lập 19/10, CBTT 20/10).
> **[H1 pN]** = `src/bctc_banien_2026_kiemtoan.pdf` (bán niên 2026 **SOÁT XÉT** bởi Deloitte, không phải kiểm toán; báo cáo số 0152/VN1A-HC-BC
> ngày 14/08/2026; **kết luận chấp nhận toàn phần**, không ngoại trừ, không nhấn mạnh [H1 p6]).
> **[Q2 pN]** = `src/bctc_q2_2026.pdf`. **[CB]** = CBTT gốc trên pacificshipping.vn/tin-co-dong (`src/cb_*.pdf`).
> **[BQ]** = `tav2_bq.ticker`/`ticker_financial`. **[DNSE]** = `dnse_api` secdef/latest_trade lúc 13:58 29/10.
> **[web]** = báo chí, nguồn thứ cấp (§13). Mọi phép tính nằm trong `calc.py` → `out.txt` (**0 FAIL / 19 self-check**).
> Nền ngành lấy nguyên từ Bobby (`kb/data_registry/market-state/sector_read_oil_gas_shipping_20261029.md`), không viết lại.
> PVP là **BCTC riêng**: không có công ty con, không có công ty liên kết [Q3 p8].

## 0. Tóm tắt

**Giá.** Brief ghi "đóng cửa 28/10 = 22.900 (BQ)". **Số này SAI.** 22.900 là giá đóng cửa ngày **20/10**. Giá đóng cửa BQ ngày
28/10 là **20.150**. Phiên 29/10, giá chạm sàn **18.750** lúc 13:58 [DNSE]. Đỉnh gần nhất là **25.000** ngày 08/10 [BQ], nên giá hiện tại
thấp hơn đỉnh **25%**.

| Câu hỏi | Trả lời ngắn (số đo) |
|---|---|
| LN 9T đến từ đâu | LN gộp vận tải **292,9 tỷ, gấp 2,08 lần** 9T/25 (140,7). Phần tăng này chiếm **111%** mức tăng LN gộp toàn công ty. Mảng FSO đi ngang, mảng thương mại LPG/ủy thác lãi ≈0 |
| LN có phải một lần không | **Không có** lãi bán tàu (thu nhập khác ≈ 0). Có **2 khoản thổi phồng**: (i) theo TT99 công ty **ngừng trích dự phòng sửa chữa định kỳ**. 9T/25 trích **53,1 tỷ**, 9T/26 trích **0**, tương đương 15,2% LNTT; (ii) lãi tiền gửi **57,4 tỷ** = 16,5% LNTT |
| Vì sao Q3 giảm 50% so với Q2 | Do **doanh thu vận tải quốc tế giảm 39%** (365,5 → 224,4) và LN gộp vận tải giảm **52%** (146,5 → 70,4). **Không phải** do sửa chữa (không trích, không sử dụng dự phòng), **không phải** do tỷ giá (lỗ ròng ~4,5 tỷ). BCTC không nói rõ nguyên nhân gốc |
| 9T so với kế hoạch | LNST 278,0 tỷ = **128,7%** KH 216 tỷ. LNTT 348,9 = **129,2%** KH 270 tỷ. Mức "77,6%" báo chí đưa cho 6T là phép chia **LNST cho KH LNTT**. Đúng ra 6T LNST đã đạt **97,5%** KH LNST |
| Bảng cân đối | Tiền + tiền gửi HTM **1.734 tỷ**, vay **608,5 tỷ** (toàn VND). **Tiền ròng 1.125,6 tỷ = 10.854 đ/cp**, tức khoảng **58% giá 18.750** |
| Rủi ro lớn nhất | Kế hoạch mua tàu **116 triệu USD ≈ 3.021 tỷ = 1,55 lần vốn hoá**, đúng lúc giá tàu cũ đang ở đỉnh (Bobby §3.1). Nếu mua cả hai tàu, công ty chuyển từ tiền ròng **+1.126** sang **nợ ròng ~2.005 tỷ** (ND/VCSH 0,95) |
| Định giá | PE TTM **6,04**, PB **0,93**, EV ~928 tỷ, EV/EBITDA (9T năm hoá) **1,24 lần**. Ba neo cho 3 kết quả khác nhau: PE lịch sử ra **12,2k**, PB trung vị lịch sử ra **15,5k**, SOTP ra **23,1k** (đều ước lượng). Giá 18.750 nằm giữa dải |

## 1. Kiểm chứng điều Mike chưa kiểm

| Mike/báo chí ghi | Kiểm từ gốc | Kết quả |
|---|---|---|
| Giá đóng cửa 28/10 = 22.900 (BQ) | BQ `ticker` 28/10 Close = Price = **20.150**; 20/10 = 22.900 | ❌ **SAI**: lệch 1 tuần. Mọi định giá trong file dùng 18.750 (DNSE), có bảng độ nhạy theo cả 3 mức giá (§7) |
| BQ: Q3 DT ~838, LNST ~67,5 | [Q3 p6] DT **838,414**, LNST **67,514** | ✅ khớp tới triệu đồng |
| Q2 134,2, Q1 ~75,5, 6T 209,7 | [Q2 p17] Q2 **134,19**. [H1 p9] 6T soát xét **210,515**. BQ Q1 75,54 | ⚠️ 6T soát xét là **210,5**, không phải 209,7. Q1 suy ra từ H1 − Q2 là 76,32, lệch BQ +0,78: có thể là điều chỉnh sau soát xét, chưa kiểm |
| KH 2026: DT 2.700 / LNTT 270 / LNST 216 | [web] baophapluat 11/02/2026 (không có ĐHĐCĐ gốc trong tay) | ✅ (nguồn thứ cấp). 9T đạt **81,7% / 129,2% / 128,7%** |
| "9T ~277 vượt KH" | 9T LNST **278,03** [Q3 p6] | ✅ |
| Cổ tức tiền 10% đã chốt | [Q3 p13] "cổ tức đã công bố" 103,70 tỷ = 1.000 đ × 103,7 tr cp. Phải trả cổ tức tại 30/9 còn **109,5 tỷ** [Q3 p4]. BQ Close/Price chuyển từ 0,9488 sang 1,0 ngày **17/09** ⇒ GDKHQ ≈ 17/09 (suy luận). CBTT HĐQT 28/08 [CB] | ✅. Tại 30/9 **chưa chi**, nên vẫn nằm trong tiền. Tiền ròng sau cổ tức = 1.016 tỷ |
| ĐHĐCĐ bất thường đã gia hạn | [CB] NQ 23/NQ-TBD-HĐQT ngày **23/10/2026**: gia hạn đến **"không muộn hơn ngày 30/11/2026"**, lý do "hoàn thiện các văn kiện". Có một NQ gia hạn trước đó ngày 02/10 (chưa đọc kỹ). Họp dự kiến ban đầu 23/10, chốt quyền 28/9 [web] | ✅ đã gia hạn **2 lần**. Văn kiện ĐHĐCĐ **chưa công bố** |
| Mua Aframax thứ 3 | [H1 p34] ĐHĐCĐ 23/06/2026 duyệt **2 dự án chuyển tiếp**: (1) **Aframax số 2**, 120.000 DWT, **56,5 tr USD** (VCSH 17,08 / vay 39,42); (2) **Aframax số 3 HOẶC 2 tàu MR1/MR2** 55.000 DWT, **59,5 tr USD** (VCSH 18,11 / vay 41,39). Đến 14/08, công ty **"chưa có bất kỳ thỏa thuận nào với đối tác được ký kết"** | ⚠️ Gọi là "Aframax thứ 3" là đúng thứ tự (Apollo = Aframax #1, theo [web] là 105k DWT), nhưng hiện **CHƯA mua cả tàu #2** |
| Tin dự kiến tăng vốn | **Không thấy** trong BCTC, 5 CBTT đã đọc, hay bài báo về ĐHĐCĐ bất thường. KH vốn = **30% VCSH** (tiền có sẵn) + 70% vay | ❌ **Không xác nhận được**. Vốn chủ 35,19 tr USD ≈ **916 tỷ** < tiền ròng 1.016, nên **không cần** phát hành. Nếu văn kiện ĐHĐCĐ có mục phát hành ⇒ đổi đánh giá (§11) |
| GĐ mới Phan Công từ 23/6 | [H1 p4] Hoàng Đức Chính **miễn nhiệm** GĐ + TV HĐQT ngày 23/06. **Phan Công** bổ nhiệm GĐ + TV HĐQT 23/06, là người đại diện theo pháp luật từ **10/07**. Vũ Ngọc Khôi (PGĐ) miễn nhiệm **12/08**. CBTT bổ nhiệm PGĐ mới ngày 04/09 [CB, chưa đọc chi tiết] | ✅ WARNING quản trị (§10) |
| GD với người có liên quan | [CB] NQ 16/NQ-TBD-HĐQT 18/08/2026, phụ lục 6 đối tác **trong hệ thống PVTrans**. Nội dung: đại lý tàu/cảng cho tàu dầu thô chở cho NMLD **Dung Quất**, dịch vụ thuyền viên, văn phòng, đào tạo, thuê tàu chuyến. Giá trị ghi **"theo thực tế phát sinh"**, giới hạn trong thẩm quyền HĐQT | ⚠️ Giao dịch vận hành thông thường. **Không có trần giá trị** nên không đánh giá được tính công bằng về giá (§5) |
| Cổ đông lớn PVTrans/PVN; VIS Rating A | [H1 p28] PVTrans **64,92%**, **Lê Ngọc Anh 6,66%** (đầu kỳ 6,44%), khác 28,42%. VIS Rating **A, ổn định**, lần đầu xếp hạng 25/05/2026 [web cafef] | ✅ (VIS từ nguồn thứ cấp). Room ngoại: **chưa kiểm** |

## 2. (A) Lợi nhuận đến từ đâu — theo mảng [Q3 p13-14, Q2 p13-14, H1 p29-30]

| Mảng | Q1/26 | Q2/26 | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|---|---|
| **Vận tải** DT | 232,6 | 365,5 | 224,4 | 172,9 | 822,5 | 501,1 |
| Vận tải LN gộp (biên) | 76,0 | **146,5 (40,1%)** | **70,4 (31,4%)** | 62,5 (36,2%) | **292,9** | 140,7 |
| **FSO** DT / LN gộp | — | 59,3 / — | 59,7 / 22,6 | 60,0 / 21,9 | 177,4 / 66,3 | 182,9 / 68,5 |
| Thương mại LPG DT / LN gộp | — | 51,6 / ~0 | 272,2 / 0,06 | 451,8 / ~0 | — | — |
| Ủy thác khai thác tàu cho PVTrans DT / LN gộp | — | 244,4 / 0,8 | 280,0 / 0,66 | 147,3 / 0,9 | — | — |
| **Tổng LN gộp** | | | **93,9** | 85,3 | **362,4** | 225,9 |

- **Vận tải 100% là quốc tế.** Nguyên văn [H1 p30]: *"trong năm 2025 và 6 tháng đầu năm 2026, để tối ưu hóa hoạt động vận tải, Công ty chỉ
  thực hiện vận tải và phát sinh doanh thu ở thị trường quốc tế."* PVP vì vậy **nhạy cước quốc tế hơn hẳn PVT** (Bobby §3.5: nhãn ADMIN_GATED
  **không** áp cho phần này). Đây là khác biệt bản chất với PVT, đúng như brief cảnh báo.
- **Đội tàu sở hữu: 3 tàu dầu + 1 FSO** [Q3 p10, H1 p22]: Apollo (Aframax ~105k DWT [web], **hết khấu hao**, NBV 0, không thế chấp);
  Pacific Era (MR ~50k DWT [web], NBV 342,5, thế chấp Woori); Pacific Pride (MR ~50,7k DWT [web], NBV 495,7, thế chấp VCB); FSO Đại Hùng
  Queen (NBV 389,1, còn khoảng 2,6 năm khấu hao). Có **thuê tàu ngoài**: phải trả Signal Maritime Aframax Pool 21,7 tỷ (30/6) và
  Sokana Shipping (đầu năm) [H1 p22]. **Tuổi từng tàu: BCTC KHÔNG ghi.** [web]: Apollo 19 tuổi vào cuối 2024; Era và Pride đóng tại
  Hàn Quốc, mua 2023–24.
- [web elibook 25/05/2026, dẫn CTCK]: *Apollo tái ký hợp đồng thuê **70.000 USD/ngày**, gấp đôi giá cũ 30–35k*. Bài gán Apollo cho "PVT",
  nhưng BCTC cho thấy **PVP sở hữu Apollo**. Thời hạn hợp đồng và bên thuê **không nêu**. **Chưa kiểm**, nhưng khớp với việc biên vận tải
  Q2 nhảy lên 40%.
- **Q3 so với Q2:** DT vận tải −39%, LN gộp −52%. Chi phí nhiên liệu Q3 77,1 tỷ, gần bằng Q2 (80,7) [Q3 p14, Q2 p14], nên **không phải chi phí
  tăng mà là doanh thu giảm**. BCTC **không tách** theo tàu hay theo loại hợp đồng (TC/chuyến/pool). Các giả thuyết như tàu off-hire, thời
  điểm ghi nhận chuyến, hay tàu thuê ngoài hết hạn đều là **suy đoán, chưa kiểm**. Q3 vẫn **tăng 12,6% so với cùng kỳ** ở LN gộp vận tải.
- Giải trình Q3 của công ty [Q3 p15]: LNST giảm so với cùng kỳ *"do ảnh hưởng của thuế TNDN hoãn lại trong năm trước"* (Q3/25 có thu nhập
  thuế hoãn lại 2,34 tỷ).

## 3. (B) Chất lượng lợi nhuận

| Khoản | 9T/26 | 9T/25 | Ghi chú |
|---|---|---|---|
| Lãi thanh lý tàu | **0** | 0 | Thu nhập khác 9T chỉ 0,006 tỷ [Q3 p6]. **Mục 8 Bobby không áp dụng** |
| Lãi tiền gửi (LCTT mã 05) | 57,4 | 38,4 | **16,5% LNTT**. Q3 năm hoá = 5,3% trên tiền + HTM 1.734. **Sẽ giảm khoảng 916 tỷ số dư** nếu dùng tiền mua tàu |
| Trích dự phòng sửa chữa định kỳ (LCTT mã 03) | **0** | **53,1** | TT99/2025: *"Công ty không tiếp tục trích trước chi phí sửa chữa lớn TSCĐ từ thời điểm Thông tư có hiệu lực"*. Số dư cũ xử lý chuyển tiếp: chi phí thực tế sẽ bù trừ vào số đã trích, phần chênh lệch phân bổ [H1 p15] |
| Số dư dự phòng sửa chữa | 232,9 (toàn bộ **ngắn hạn**) | đầu năm 71,6 NH + 161,3 DH | Chuyển hết sang ngắn hạn ⇒ công ty dự kiến **sửa chữa lớn trong 12 tháng tới** (suy luận). Off-hire khi lên đà sẽ làm giảm doanh thu |
| Tỷ giá Q3 | Lãi 0,73 − lỗ đánh giá lại 4,61; CP 0,55 + 0,08 | | Ròng khoảng **−4,5 tỷ** Q3, không trọng yếu. Giữ 15,2 tr USD tiền (30/9) [Q3 p13]. Vay **toàn VND** (Woori, VCB) [Q3 p11, H1 p25] ⇒ **không có rủi ro tỷ giá trên nợ** |
| LNTT 9T nếu vẫn trích như 9T/25 (ước lượng) | 295,8 | 194,3 | Tăng trưởng "so sánh được" khoảng **+52%**, không phải +80% |

**Đọc:** LN 9T/26 là **thật về tiền**. CFO 9T **473,0 tỷ = 1,70 lần LNST**, capex 0,18 tỷ [Q3 p7]. Tuy vậy, khoảng 15% LNTT là **hiệu ứng
chuyển đổi kế toán**, và phần cước quốc tế ở đỉnh Q2 là phần **kém bền nhất**.
**FSO:** giá vốn FSO 9T 111,11 tỷ **≈ đúng bằng** khấu hao FSO 9T 111,11 tỷ, tức giá vốn gần như toàn bộ là khấu hao (bên thuê chịu chi phí
vận hành). Vì vậy dòng tiền FSO ≈ doanh thu ≈ **237 tỷ/năm**. Khi FSO hết khấu hao (~2029), LN kế toán FSO sẽ tăng khoảng 148 tỷ/năm, **nếu**
giá thuê giữ nguyên (xem rủi ro phụ lục ở §5).

## 4. (C) Bảng cân đối & dòng tiền 30/9/2026 [Q3 p3-5, p9, p11]

| | 30/9/2026 | 01/01/2026 |
|---|---|---|
| Tiền + tương đương | 718,2 | 503,9 |
| Tiền gửi HTM ngắn hạn | 1.015,9 | 818,8 |
| Vay NH / DH (VND) | 134,9 / 473,5 | 157,6 / 574,7 |
| **Tiền ròng** | **1.125,6** | 590,4 |
| Phải trả cổ tức (chưa chi) | 109,5 | 6,3 |
| Dự phòng sửa chữa định kỳ | 232,9 | 232,9 |
| Phải thu KH | 534,8: **PVTrans 299,8**, Gas Venus 131,2, khác 103,8 | 254,2 |
| VCSH | 2.099,6, **BVPS 20.246** | 1.931,3 |

- Lịch trả nợ [H1 p25]: 134,9 tỷ/năm, khoản cuối đáo hạn 2030. Lãi suất 6–6,5% hai năm đầu, sau đó thả nổi theo lãi tiết kiệm 12 tháng + 1,7–2,1%.
- Phải thu tăng 280 tỷ, chủ yếu từ **PVTrans (công ty mẹ) 299,8 tỷ**. Rủi ro tín dụng thấp (cùng hệ thống), nhưng là **WARNING vốn lưu động**.
- **Capex dự kiến** [H1 p34]: tổng **116 tr USD ≈ 3.021 tỷ** (VCB 26.040), trong đó VCSH **916 tỷ**, vay **2.104 tỷ**. Mua cả hai tàu ⇒ tiền còn khoảng
  708 tỷ, vay khoảng 2.713 tỷ, **nợ ròng khoảng 2.005 tỷ (ND/VCSH 0,95)**. Bảng cân đối vẫn sống được (vay VND, lịch dài), nhưng **mức đòn bẩy
  đổi hẳn** và quyết định mua rơi đúng vùng đỉnh giá tàu cũ (Bobby §3.1: giá tàu 15 tuổi +36% MoM trong T9; mục 7 Bobby).
  Tàu Aframax #2 dự kiến mua cũ, **≤15 tuổi**, cho thuê định hạn, treo cờ nước ngoài [web baophapluat 12/09].

## 5. (D) Khách hàng, hợp đồng, bên liên quan

- **Bên liên quan chiếm 63,3% doanh thu 6T** (865,4/1.367,3 tỷ) [H1 p38]: PVTrans 555,7 (FSO + ủy thác), **BSR (Dung Quất) 199,5**, LPG Việt Nam 94,5,
  VT Xăng dầu Phương Nam 15,7. Mua từ bên liên quan 204,1 tỷ (Hàng hải Thăng Long 99,8; Xăng dầu DK Sài Gòn 44,7; VT DK Quảng Ngãi 41,9).
  Bảng Q3 [Q3 p15] ghi doanh thu từ PVTrans **951,5 tỷ, lớn hơn cả tổng DT Q3 838,4**, nên nhiều khả năng đây là số **lũy kế 9T** (suy luận,
  không ghi rõ kỳ).
- **Hợp đồng FSO Đại Hùng Queen** [H1 p34], đọc nguyên văn: thuê 5 năm từ 17/05/2015, **gia hạn thêm mỗi lần 5 năm** từ 17/05/2021. Biên bản
  ngày **03/06/2025**: hai bên *"thống nhất về việc điều chỉnh giá cước và gia hạn hợp đồng đến ngày 31/12/2036"*. Đến 14/08/2026, công ty
  *"đang trong quá trình hoàn tất thủ tục để ký phụ lục"*. ⇒ **Phụ lục CHƯA ký; giá mới CHƯA công bố**. Doanh thu FSO Q3 (59,7) bằng Q3/25 (60,0),
  nên chưa thấy giá đổi.
  Cam kết cho thuê không hủy ngang (30/6): **1.163,7 tỷ** (≤1 năm 415,8 / 2–5 năm 542,9 / >5 năm 205,0). ⚠️ Con số ≤1 năm 415,8 **lớn hơn nhiều**
  doanh thu FSO năm khoảng 237 tỷ, và **tôi không hoà giải được** (có thể gồm hợp đồng cho thuê tàu khác, hoặc giá mới). Ghi nhận, không dùng
  để kết luận.
- **Tỷ trọng TC / chuyến / pool, ngày đáo hạn từng hợp đồng: BCTC KHÔNG có** (mục 6.A1–2 Bobby, biến quan trọng nhất, **chưa kiểm được**).
- Bobby mục 17 (trừng phạt): tàu chạy quốc tế 100% nhưng BCTC không nêu tuyến. **Chưa kiểm**.

## 6. (E) Cổ phiếu, thanh khoản, sizing

- 103.702.452 cp, không thay đổi trong năm [Q3 p13]. Tự do chuyển nhượng khoảng 28%.
- **ADV20 33,1 tỷ, ADV60 22,8 tỷ** [BQ tới 28/10]. Cuối 2025 thanh khoản chỉ **1,3–2,2 tỷ/ngày**; tăng mạnh từ T3/2026 cùng tin Hormuz ⇒ thanh khoản
  hiện tại là **thanh khoản của chu kỳ nóng**, có thể co lại khi hết chủ đề.
- Sizing theo tiền lệ 0,5–1,0% NAV: ở NAV 50–100 tỷ, vị thế 0,25–1,0 tỷ = **0,8–3,0% ADV20**, chưa có vấn đề capacity. Thoát lệnh trong 1–2 phiên.
  Nếu ADV về mức 2025 (~2 tỷ), vị thế 1 tỷ sẽ bằng **~50% ADV** ⇒ thoát chậm. Đây là kịch bản thoát cần tính trước.

## 7. (F) Định giá [out.txt §6]

| Giá | Vốn hoá | PE TTM (LNST 321,9) | PB | EV (trừ tiền ròng, cộng cổ tức phải trả) | EV/EBITDA 9T năm hoá (750,7) | DY (1.000đ) |
|---|---|---|---|---|---|---|
| **18.750** (DNSE, sàn 29/10) | 1.944 | **6,04** | **0,93** | 928 | 1,24 | 5,3% |
| 20.150 (BQ 28/10) | 2.090 | 6,49 | 1,00 | 1.074 | 1,43 | 5,0% |
| 22.900 (brief) | 2.375 | 7,38 | 1,13 | 1.359 | 1,81 | 4,4% |

PVP lịch sử 2018- [BQ]: PE p25/50/75 **4,90 / 6,33 / 8,00**; PB **0,53 / 0,77 / 0,91**. Peers 28/10 [BQ]: PVT PE 8,28 / PB 0,95 · VOS 4,83 / 0,79 ·
VTO 5,11 / 0,72 · GSP 8,76 / 0,80. Không có số đáng tin cho tanker niêm yết quốc tế trong phiên ⇒ bỏ, không đoán.
LNST bình quân 2023–25 = **196,5 tỷ** (2023: 184,0; 2024: 207,1; 2025: 198,5 [BQ, 2025 khớp TM20 H1]); TTM 321,9 = **1,64 lần mức nền**.

**Ba phương pháp cho 3 kết quả khác nhau. Đó chính là phát hiện chính, không phải nhiễu:**

| Phương pháp | Kết quả/cp | Đọc |
|---|---|---|
| **PP-A**: PE lịch sử PVP × LNST 2027 (ước lượng) + NPV tàu #2 | xấu 4.721 / cơ sở 13.231 / tốt 23.143 ⇒ **kỳ vọng 12.235** | **Đánh giá thấp** vì PE 4,9–8 áp lên LN đã gồm lãi tiền gửi: 1 đồng tiền mặt chỉ được tính khoảng 0,3–0,4 đồng. Đây là "giá thị trường quen trả", không phải giá trị |
| **PB trung vị lịch sử** 0,77 × BVPS | **15.545** | Neo thị trường trung tính. Nhưng VCSH hiện nay ~50% là tiền ròng, khác thời PB thấp |
| **PP-B SOTP** (tiền ròng + HĐ FSO + đội tàu theo EBITDA × bội số − dự phòng sửa chữa − chi phí công ty − NPV tàu #2) | xấu **15.185** / cơ sở **24.334** / tốt **34.212** ⇒ **kỳ vọng 23.107** | Cộng tài sản, nhạy với bội số đội tàu tự đặt |

Giả định PP-B (đều **ước lượng**):
- EBITDA đội tàu chuẩn hoá xấu/cơ sở/tốt **300 / 400 / 550 tỷ**. Mốc so sánh: 9T/26 năm hoá **561** (đỉnh); 2025 khoảng 380–390 (LN gộp vận tải 9T/25 140,7 năm hoá + KH).
- Bội số **3,0 / 3,5 / 4,0 lần**.
- HĐ FSO = cam kết còn lại × 0,70 (PV + thuế), nhân thêm hệ số giá thuê **0,70 / 0,90 / 1,0** cho rủi ro phụ lục giá.
- NPV tàu #2: **−30% / −10% / 0** trên 56,5 tr USD (mua ở đỉnh giá tàu cũ).
- Chi phí công ty ~52 tỷ/năm × (1 − thuế) × 5.
- Trọng số **0,35 / 0,45 / 0,20**, bám Bobby: CYCLICAL 0,55 kéo về nhánh xấu/cơ sở; K3 leo thang 0,15–0,20 cho nhánh tốt.

**Sàn tài sản:** tiền ròng + HĐ FSO kịch bản xấu − dự phòng sửa chữa, coi **đội tàu bằng 0** = **12.768 đ/cp**.
Ở giá 18.750, thị trường đang định giá 3 tàu dầu khoảng **674 tỷ, thấp hơn giá trị sổ sách 838 tỷ**, dù giá tàu cũ đang ở đỉnh. Nói cách khác:
**giá đã chiết khấu sẵn rủi ro cước 2027 và rủi ro tiền bị tiêu vào tàu đắt**. Đây là lý do verdict **không phải NON**. Nhưng biên an toàn
thì không có.

**Kết luận định giá:** dải hợp lý khoảng **15,5–23k (ước lượng)**. Giá 18.750 nằm **gần giữa dải**. Biên an toàn 15% dưới cận dưới của dải tin
cậy ⇒ vùng đáng chạy lại DD là **≤ ~15.500**: ≈ PB trung vị lịch sử, ≈ PP-B kịch bản xấu, và 1,2 lần sàn tài sản.

**Phản ứng giá (không khẳng định nhân quả):**
- 25/09: tăng trần 20.500, đúng ngày GDKHQ dự họp ĐHĐCĐ bất thường [web, BQ].
- 08/10: đỉnh **25.000**. Cùng tuần, cước giao ngay lập đỉnh 06/10 (Bobby §3.1).
- 20/10: CBTT Q3 (giá đóng cửa 22.900). 21/10: **sàn 21.300**, KL 3,84 tr cp, trong khi VNINDEX **+2,8%** cùng phiên (1.691,97 → 1.738,67).
  ⇒ phản ứng riêng của mã, trùng thời điểm Q3 giảm QoQ.
- 23/10: CBTT gia hạn ĐHĐCĐ. 28/10: 20.150. 29/10: **sàn 18.750**, cùng phiên PVT cũng giảm sàn (DD PVT) ⇒ có yếu tố bán cả nhóm vận tải dầu khí.
- Giá đầu năm 13.240–14.660 (T1/2026) [BQ].

## 8. Đối chiếu 20 mục DD của Bobby (§6)

| # | Trạng thái | Kết quả |
|---|---|---|
| 1 TC/chuyến/pool | ❌ | Không có trong BCTC. Gián tiếp: vận tải 100% quốc tế; biên vận tải dao động mạnh 24–40% theo quý ⇒ **nhạy cước cao**; có phải trả Aframax Pool (Signal) |
| 2 Lịch đáo hạn TC | ❌ | Không có. Apollo 70k USD/ngày chỉ có từ [web], chưa có thời hạn |
| 3 Khách cùng hệ thống | ✅ | 63,3% DT 6T là bên liên quan, nhưng phần lớn là FSO/ủy thác/LPG biên ≈0. Vận tải có BSR 199,5 tỷ 6T |
| 4 Nội địa vs quốc tế | ✅ | Vận tải **100% quốc tế** 2025–6T/26 [H1 p30] |
| 5 Bảng đội tàu / tuổi | ⚠️ | 4 tài sản có tên + nguyên giá + NBV [Q3 p10]. Tuổi: chỉ có [web] cho Apollo (~21 tuổi năm 2026) |
| 6 Lịch dry-dock, hạch toán | ⚠️ | Đổi hạch toán theo TT99 (§3). Dự phòng 232,9 chuyển hết sang ngắn hạn ⇒ lên đà trong 12 tháng (suy luận) |
| 7 Mua tàu ở đỉnh, VAT 31/12/26 | ⚠️ **rủi ro chính** | 116 tr USD duyệt chủ trương; chưa ký hợp đồng; ĐHĐCĐ gia hạn tới ≤30/11. Hạn miễn VAT NK tàu 31/12/2026 ⇒ **có động cơ dồn mua** (Bobby) |
| 8 Lãi thanh lý | ✅ | 0. Apollo hết khấu hao, nên nếu bán ở giá đỉnh sẽ có lãi một lần lớn (khả năng, chưa có tin) |
| 9 Khấu hao, impairment | ⚠️ | Tàu 6–14 năm [H1 p11]. Era/Pride còn khoảng 4,7–5,0 năm khấu hao. Chưa có impairment |
| 10 CII/EEXI, tàu >15–20 tuổi | ❌ | Apollo khoảng 21 tuổi ⇒ rủi ro vetting/thay thế. Đây là lý do của dự án Aframax #2 (suy luận) |
| 11 Nợ theo đồng tiền | ✅ | **Toàn VND**, lãi thả nổi sau 2 năm |
| 12 Tỷ giá | ✅ | Ròng Q3 khoảng −4,5 tỷ. Giữ 15,2 tr USD tiền |
| 13 Lãi vay/EBITDA | ✅ | Lãi vay 9T 31,6 / EBITDA 563 = 5,6%. Hiện đang tiền ròng |
| 14 Dùng LN đỉnh | ⚠️ | Tích tiền (1.734), cổ tức 10%, **định tiêu ~916 tỷ VCSH cho tàu** |
| 15 Nhiên liệu, war-risk | ⚠️ | Nhiên liệu Q3 77,1 tỷ (gấp 2,7 lần Q3/25 28,9) ⇒ công ty tự chịu nhiên liệu, tức có chạy chuyến/giao ngay (suy luận) |
| 16 Off-hire, tranh chấp | ❌ | Không nêu |
| 17 Trừng phạt | ❌ | Không có thông tin |
| 18 Cabotage | — | Không áp dụng (vận tải 100% quốc tế) |
| 19 FSO | ⚠️ | Phụ lục gia hạn đến 2036 **chưa ký**, có điều khoản "điều chỉnh giá cước" |
| 20 TA lọc dầu 2027 | ❌ | Ảnh hưởng gián tiếp qua BSR (199,5 tỷ DT 6T) |

## 9. §2 / §2.5 — áp dụng cái nào

- **§2 (scandal cá nhân): KHÔNG áp dụng.** Không có khởi tố hay điều tra. Chỉ có thay GĐ và PGĐ (§10).
- **§2.5 (chu kỳ ngành):** #1 chu kỳ ✅ (Bobby CYCLICAL 0,55). #2 sống sót ✅ (tiền ròng; kể cả sau capex, ND/VCSH khoảng 0,95, vay VND dài hạn).
  #3 dẫn đầu chi phí ⚠️ (không kiểm được; chỉ có 3 tàu dầu, 1 tàu khoảng 21 tuổi). #4 sàn tài sản PB ≲ 1 ✅ (PB 0,93; khoảng 54% là tiền).
  **"Đáy chưa tới" ❌ NGƯỢC CHIỀU:** đây là **ĐỈNH** chu kỳ lợi nhuận (Bobby: cuối đỉnh, F1/F2 dự báo BDTI giảm 41–61% tới 2027).
  Mức sụt từ đỉnh −25% < ngưỡng T1 >35%.
  ⇒ **Đây KHÔNG phải ca fear-buy.** Gò PVP vào §2.5 là sai khung. Nếu năm 2027 cước sập, LN về ≤ mức nền ~200 tỷ, giá về PB ≲ 0,75, và **tiền
  không bị tiêu vào tàu đắt** ⇒ khi đó mới là ứng viên §2.5.

## 10. Pháp lý / quản trị — WARNING (luật 27/09: phân tích bình thường, chỉ cảnh báo)

- ⚠️ **Thay GĐ 23/06/2026**, cùng ngày ĐHĐCĐ thường niên duyệt dự án tàu: Hoàng Đức Chính → **Phan Công** (đại diện pháp luật từ 10/07) [H1 p4].
  PGĐ Vũ Ngọc Khôi miễn nhiệm 12/08 (trước đó có CBTT đơn xin từ nhiệm); bổ nhiệm PGĐ mới 04/09 [CB, tên chưa đọc]. Lý do: không công bố.
  Không thấy liên quan tới khởi tố. Rủi ro: ban điều hành mới quyết capex 1,55 lần vốn hoá ngay đỉnh chu kỳ.
- ⚠️ **ĐHĐCĐ bất thường gia hạn 2 lần** (02/10 và 23/10; hạn mới ≤30/11) để "hoàn thiện văn kiện". Không suy diễn thêm. Đây là **mốc then chốt**.
- Phải thu khó đòi cũ **Huỳnh Thị Huyền Như** 73,07 tỷ (từ 2011) đã **dự phòng 100%** [Q3 p9, H1 p17]. Không ảnh hưởng LN hiện tại.
- Kiểm toán: soát xét H1/2026 Deloitte **chấp nhận toàn phần** ✅. BCTC năm 2025 kiểm toán: **không có trong tay**.
- Giao dịch bên liên quan: NQ HĐQT 18/08 không có trần giá trị ("theo thực tế phát sinh"). Không phát hiện bất thường trong số liệu,
  nhưng **không có cách kiểm giá chuyển nhượng**.

## 11. Điều kiện đổi verdict + mốc khoá trước

| Mốc | Cần thấy | Hướng |
|---|---|---|
| **ĐHĐCĐ bất thường (≤30/11/2026)** | Văn kiện: giá mua/tuổi tàu Aframax #2/#3, có phát hành cổ phiếu không | Giá ≤ ~45 tr USD cho tàu ≤10 tuổi, **hoặc** hoãn mua ⇒ nâng kịch bản (NPV tàu ≈ 0); 56,5 tr USD cho tàu 10–15 tuổi trước 31/12 ⇒ giữ NPV −30% nhánh xấu; **có phát hành pha loãng ⇒ hạ thẳng về NON** |
| Phụ lục FSO đến 2036 | Giá thuê mới | Giảm ≤15% ⇒ giữ; giảm >30% ⇒ hạ PP-B khoảng −1.500 đ/cp (ước lượng) |
| BCTC Q4/2026 (~20/01/2027) + BCTC năm 2026 kiểm toán | LN gộp vận tải Q4 so với Q3 70,4; sử dụng dự phòng 232,9 | LN gộp vận tải Q4 < 50 tỷ ⇒ nghiêng nhánh xấu |
| **Bobby F1 31/03/2027** (BDTI trung vị ~4.200; F3 Aframax ~180k) | LN gộp vận tải Q1/27 | Nếu Aframax TCE < 150k mà LN gộp vận tải ≥ 60 tỷ/quý ⇒ có TC khoá giá, nâng nhánh cơ sở |
| **Bobby F2 30/09/2027** (BDTI ~2.800) | LNST 9T/27 vs 9T/26 278,0 | ≤ 160 ⇒ đúng nhánh xấu |
| Giá | **≤ ~15.500** | Chạy lại DD (**không tự QUALIFY**). Ngược lại, giá > 23.000 mà không có tin mới ⇒ đắt so với kỳ vọng SOTP |

## 12. Điểm yếu tự nhận (cho fundamental-skeptic tấn công)

1. **Định giá phụ thuộc phương pháp, sai lệch 12–23k.** Bội số đội tàu, EBITDA chuẩn hoá, hệ số FSO, NPV tàu đều là **ước lượng tự đặt**.
   PP-B nhạy nhất với bội số × EBITDA: ±0,5 lần × 400 = ±200 tỷ = ±1.930 đ/cp.
2. **Không có dữ liệu hợp đồng thuê tàu** (TC/chuyến/pool, giá, đáo hạn). Kịch bản LN 2027 không neo được vào hợp đồng.
3. **Không hoà giải được cam kết cho thuê ≤1 năm 415,8 tỷ** so với doanh thu FSO khoảng 237 tỷ/năm.
4. Doanh thu từ PVTrans 951,5 tỷ trong bảng Q3: **giả định là lũy kế 9T**, không kiểm được.
5. Tuổi tàu và thông tin Apollo 70k USD/ngày chỉ đến từ [web], nguồn thứ cấp.
6. Q1 suy ra lệch BQ 0,78 tỷ: chưa giải thích.
7. Hiệu ứng TT99 ước tính bằng trích 9T/25 (53,1 tỷ). Chi phí lên đà thực tế 2027+ có thể khác.
8. Chưa đọc: NQ gia hạn ĐHĐCĐ ngày 02/10, CBTT bổ nhiệm PGĐ 04/09 (chi tiết), NQ cổ tức 28/08 (ngày thanh toán), tài liệu ĐHĐCĐ thường niên 2026.
   Room ngoại chưa kiểm.
9. Chưa trừ thuế khi bán Apollo, và chưa định giá **lãi bán Apollo ở đỉnh** (một quyền chọn có lợi cho cổ đông, chưa có tin).

## 13. Nguồn web (thứ cấp)

- KH 2026 + capex 116 tr USD: https://doanhnhan.baophapluat.vn/pvtrans-pacific-pvp-dat-muc-tieu-lai-truoc-thue-270-ty-dong-trong-nam-2026.html (11/02/2026)
- ĐHĐCĐ bất thường, Aframax #3: https://doanhnhan.baophapluat.vn/van-tai-dau-khi-thai-binh-duong-pvp-trieu-tap-dhdcd-bat-thuong-muon-mua-them-tau-aframax-thu-3.html (12/09/2026)
- Apollo 70k USD/ngày (dẫn CTCK): https://elibook.vn/2026/05/25/pvt-gia-cuoc-thue-tau-dau-tho-aframax-van-neo-cao-trong-quy-2-tau-apollo-tai-ky-hop-dong-70000-dola-ngay-gap-doi-gia-thue-cu/
- VIS Rating A: https://cafef.vn/pvtrans-pacific-lan-dau-duoc-xep-hang-a-trien-vong-on-dinh-boi-vis-rating-18826061617063305.chn
- Đội tàu (Era/Pride/Apollo tuổi): https://tapchicongthuong.vn/pv-trans-pacific--pvp--du-chi-112-trieu-usd-de--tre-hoa--doi-tau-139280.htm
- CBTT gốc: https://pacificshipping.vn/tin-co-dong (NQ 23/NQ-TBD-HĐQT 23/10/2026; NQ 16/NQ-TBD-HĐQT 18/08/2026)

## 14. ĐÍNH CHÍNH sau phản biện fundamental-skeptic (Mike ghi 29/10 14:1x) — ƯU TIÊN HƠN §0/§3/§7/§9/§11 nếu mâu thuẫn

**Skeptic: REFUTED phần nhãn. Verdict hiệu lực = NON / không-phải-case-§2.5 @18.750, KHÔNG phải AMBIGUOUS.** Lý do: §9 tự đánh dấu ❌ "đáy chưa tới" (đang ở ĐỈNH LN) và "KHÔNG phải ca fear-buy"; §2.5 coi một ❌ là loại. Số nền khớp trang BCTC (skeptic render lại): tiền ròng 1.125,6; LN gộp vận tải Q2 146,5 / Q3 70,4 / Q3-25 62,5; trích sửa chữa 9T/25 53,1 → 9T/26 0; capex 116 tr USD; cam kết thuê 1.163,7; giá BQ 28/10 20.150 (brief 22.900 là giá 20/10 — lỗi brief của Mike, không phải của BCTC).
Sửa còn mở (CHƯA chạy lại calc.py; số dưới là ước tính của skeptic, gắn "(ước lượng)"):
1. **SOTP lạc quan:** calc.py:124,142 chỉ trừ thiệt hại mua đắt cho tàu #2 (56,5 tr USD), bỏ dự án #2 (59,5 tr USD). Áp cùng −30/−10/0: xấu 15.185→~10.700, cơ sở 24.334→~22.840, kỳ vọng 23.107→**~20.870**/cp (ước lượng). Sàn tài sản 12.768 giả định tiền còn nguyên, nhưng kế hoạch tiêu ~916 tỷ (≈90% tiền ròng sau cổ tức). Trọng số nhánh tốt 0,20 > K3 Bobby 0,15 (≈ +950/cp).
2. **FSO đọc sai (H1 p34):** cam kết 1.163,7 là RIÊNG hợp đồng FSO Đại Hùng Queen, đã tính theo đơn giá + thời hạn mới đến 31/12/2036. Bỏ: "có thể gồm tàu khác" (:124), "+148 tỷ/năm từ 2029" (:90-91), hệ số giá ×0,70/0,90 và trigger FSO −30% (calc.py:133, :232) — trùng đếm. Lịch cam kết hàm ý doanh thu FSO giảm (năm 2-5 ~136/năm, sau đó ~37/năm so với ~237 hiện nay), nên rủi ro nằm ở dòng tiền FSO, không phải ở "phụ lục chưa ký".
3. **So sánh cùng kỳ bị thổi:** Q3 LN gộp vận tải "+12,6% YoY" chưa trừ trích sửa chữa ~17,7 tỷ của Q3/25 ⇒ cùng cơ sở ≈ **−12%** (suy luận). Apollo ngừng khấu hao từ giữa 2025 (KH Q2: 98,5→79,8; 9T 275,2→239,5) ⇒ tăng LNTT cùng cơ sở ≈ **+34%**, không phải +52% (ước lượng).
4. **% kế hoạch chưa kiểm:** KH 216/270 lấy từ báo chí tháng 2/2026, trước ĐHĐCĐ 23/06; chưa đọc NQ ĐHĐCĐ. "128,7% KH" và khẳng định "báo chí chia nhầm 77,6%" CHƯA xác nhận (209,73/270 = 77,7% cũng nhất quán nếu KH LNST thật là 270).
5. **Trigger ≤15.500 sai số học:** "biên an toàn 15% dưới cận 15,5k" = ~13.200. Điều kiện chạy lại DD phải gồm cả **chu kỳ chạm đáy** (LN ≤~200 tỷ, PB ≲0,75, hoặc Bobby F2 BDTI ≤3.500 ngày 30/09/2027, hoặc kết quả ĐHĐCĐ bất thường), không chỉ giá. Từng dòng §11 chưa gắn verdict đích.
6. **Sizing §6 dùng NAV 50–100 tỷ;** NAV thật 28/10 ≈ 0,97 tỷ (SpaceX) / 0,92 tỷ (ZaloPay) ⇒ 2–4% NAV ≈ 20–40 triệu, thanh khoản không phải vấn đề.
7. Điểm yếu #6 đã giải: chênh Q1 0,78 là điều chỉnh soát xét (6T 209,73 → 210,51).
