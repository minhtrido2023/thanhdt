# DD HPG — Vòng 2: đào các điểm yếu còn mở · as-of 31/10/2026 · job `Taylor_20261031_100839`

> NGHIÊN CỨU READ-ONLY, trung dung. KHÔNG sửa `REPORT.md` (fundamental-skeptic đang phản biện song song). Pháp lý/quản trị ⇒ WARNING (luật 27/09).
> **Nguồn mới vòng này:**
> - **[KT25]** BCTC hợp nhất 2025 kiểm toán: TM15 (tr.33), TM23 (tr.37–39), TM37 (tr.50), TM40 (tr.52). Ảnh: `src/png/gaps/kt25_p*.png`.
> - **[BN]** BCTC soát xét 6T/2026: TM6 (tr.35), TM9 (tr.37), TM17 (tr.43), TM34 (tr.59), TM39 (tr.60), TM40 (tr.61). Ảnh: `src/png/gaps/bn_p*.png`.
> - **[HN-Q3]** VI.4 (tr.17).
> - **[CBTT]** NQ HĐQT gốc (bản scan) trong `src/gaps/cbtt_raw/`. Tóm tắt: `src/gaps/web_tlsh_governance.md`.
> - **[WEB]** Thông cáo gốc hoaphat.com.vn, Federal Register, MOIT, stockanalysis. Tất cả nằm ở `src/gaps/web_output_ad_peers.md` + `src/gaps/raw2/`.
> - **[BQ]** `calc/gaps_beta.py`, `calc/gaps_peers_vn_out.txt`.
>
> Số BCTC đọc từ ẢNH trang (pymupdf, zoom 1,4–1,6). Hai file web do subagent (Sonnet) viết. Mục nào gắn [báo] là chưa thấy bản gốc. Số tự tính có nhãn **(ước lượng)**.

## TL;DR — vòng 2 đổi gì

1. **TLSH đã giải xong phần số học, nhưng cờ quản trị nặng thêm.**
   - 9.915 tỷ = **1.920 tỷ TIỀN MẶT** mua 15% TLSH trong H1 + **7.995 tỷ cổ phần BĐS HP** mang góp ở Q3 [BN TM6b].
   - Giá định giá BĐS HP trong NQ 10 (22/07) là **32.000 đ/cp**, cho ~250 tr cp. NQ 13 (30/09) đổi thành **778,4 tr cp cho CÙNG 7.995 tỷ**, tức ~10.271 đ/cp **(ước lượng)** [CBTT]. Như vậy HPG giao lượng BĐS HP gấp ~3,1 lần để đổi lấy cùng một số cổ phần TLSH. Không văn bản nào giải thích.
   - HPG còn chuyển **1.600 tỷ** cho đối tác liên danh dự án Đại lộ cảnh quan sông Hồng (BT) [BN TM9]. Số dư 30/9 chỉ còn 100 tỷ. Không có thuyết minh 1.500 tỷ đi đâu.
   - Giao dịch TLSH **không được công bố là giao dịch bên liên quan**. Thuyết minh bên liên quan của KT25 và BN chỉ có thù lao.
2. **β đo được thấp hơn giả định.**
   - β tuần 2 năm **0,84**, 3 năm **0,89**; Blume **0,90–0,93** (vòng 1 giả định 1,1) [BQ].
   - Ke tương ứng 11,3–12,4%. RI trọng số tăng lên **18.800–22.800 đ** (vòng 1: 16.300–19.200).
   - Nhưng ưu đãi thuế không vĩnh viễn: nếu terminal chịu đủ 20%, RI giảm ~2.300–2.700 đ/cp. Hai hiệu ứng **gần như triệt tiêu nhau**.
   - ⇒ **Vùng 17–23k, trung tâm ~20k GIỮ NGUYÊN (ước lượng)**. Biên không chắc chắn nằm ở thuế và Ke, không phải ở lợi nhuận Q3.
3. **Comp có số.**
   - P/E lõi 7,7x so với trung vị peers VN 13,4x và khu vực 13,5x ⇒ thấp hơn ~**42–43%**.
   - EV/EBITDA lõi 5,1x so với VN 11,1x và khu vực 7,8x ⇒ thấp hơn **35–54%**.
   - P/B 1,19x **cao gấp ~2 lần** trung vị (0,57–0,67), nhưng ROE ~19,5% so với 4–8%.
   - ⇒ HPG rẻ trên lợi nhuận đỉnh chu kỳ, không rẻ trên tài sản. Khớp đọc vòng 1: thị trường chiết khấu "lợi nhuận đỉnh".
4. **Phòng vệ thương mại: sửa số hiệu.**
   - AD HRC TQ theo **QĐ 1959/QĐ-BCT (04/07/2025)**, mức 23,10–27,83%, hiệu lực **06/07/2025 → ~07/2030 (ước lượng 5 năm)**. "QĐ 1917" (Bobby F8) **không tồn tại** cho vụ này.
   - Chống lẩn tránh tạm thời theo QĐ 612 (02/04/2026).
   - Rà soát hành chính lần 1 theo QĐ 1902 (27/07/2026). **Đây là rủi ro thực trước 31/03/2027**: mức thuế có thể bị điều chỉnh.
   - Mỹ AD thép cây chốt **128,53%** (cash deposit 123,49%) + CVD 6,80%.
   - EU AD HRC với HPG **0%**.

---

## 1. TLSH / BĐS — ⚠️ WARNING

| Câu hỏi | Kết luận | Nguồn |
|---|---|---|
| 9.915 tỷ gồm gì | **15% TLSH mua bằng 1.920.000.000.000 VND tiền** tại 30/6/2026, khi vốn TLSH là 12.800 tỷ (15% × 12.800 = 1.920 ✓). Có ảnh hưởng đáng kể qua đại diện HĐQT. Q3: góp thêm 799,5 tr cp = 7.995 tỷ bằng cổ phần BĐS HP. Tổng 9.915 = 25,13% × 39.450 ✓. Mâu thuẫn "chênh 1.920" ở vòng 1 và trong file web **đã giải**. | [BN TM6b tr.35]; [CBTT NQ 10, NQ 13] |
| 32.000 hay 10.270 đ/cp | **Cả hai đều đúng, nhưng là HAI phương án.** NQ 10/NQHP-2026 (22/07): giá 32.000 đ/cp, ~250 tr cp, HPG giữ 76,41% BĐS HP. NQ 13/NQHP-2026 (30/09): góp 778.405.218 cp, giữ 26,55% (281.394.782 cp), không nêu giá ⇒ 7.995 / 778,4 tr = **10.271 đ/cp (ước lượng)**. Tổng cp BĐS HP ≈ 1.059,8 tr ở cả hai phương án ⇒ giá trị ngầm của toàn bộ BĐS HP rơi từ ~33.900 tỷ xuống ~10.900 tỷ **(ước lượng)** trong 10 tuần. Lý do: **không công bố**. Tổ chức thẩm định giá: **không nêu** (NQ 10 chỉ giao TGĐ ký "biên bản định giá"). | [CBTT] `src/gaps/cbtt_raw/` |
| Hệ quả kế toán | Q3 chỉ ghi lãi đầu tư thuần 4,3 tỷ ⇒ giao dịch xấp xỉ giá trị sổ, **không thổi P&L**. Tách 12.664 tỷ liên kết: TLSH 9.915 + BĐS HP 26,55% ≈ **2.749 tỷ** (= 12.664 − 9.915, **ước lượng**; ngầm 9.770 đ/cp, khớp mức ~10.271). Phần lãi liên kết 9T chỉ 1,99 tỷ. Rủi ro giảm giá nằm ở khoản TLSH: ghi theo mệnh giá 10.000 đ/cp, vào một DN 1 năm tuổi có 26.650 tỷ vốn góp bằng "tài sản khác" [báo]. | tự tính; [HN-Q3 tr.9]; [WEB nguoiquansat 03/08] |
| Ai sở hữu TLSH | Sáng lập (14/11/2025, 1.500 tỷ): Trần Đăng Khoa 40%, Lê Thị Minh Châu 20%, Phạm Đức Anh 15%, Trần Hữu Trung 15%, Trần Hữu Pháp 10% [báo]. Ông Khoa là CT Đại Quang Minh (hệ THACO) [báo]. Vốn: 1.500 → 9.200 (02/26) → 12.800 (06/26, tiền) → 39.450 tỷ (03/08/26). Ai góp 18.655 tỷ còn lại: **chưa tìm được**. **Không thấy** quan hệ gia đình/sở hữu với nhóm ông Trần Đình Long trong nguồn đã đọc. Đây là "không tìm thấy", không phải "đã xác minh". | `web_tlsh_governance.md` |
| Có phải giao dịch bên liên quan / cần ĐHĐCĐ | CBTT gốc **không dùng chữ "bên liên quan"**. Chỉ HĐQT thông qua, không có NQ ĐHĐCĐ. TM40 [KT25] và TM42 [BN] chỉ thuyết minh thù lao. Ngưỡng ĐHĐCĐ theo Điều lệ/LDN với giao dịch ~9,9k tỷ (~5–6% tổng tài sản): **chưa kiểm**, cần Wendy. | [CBTT]; [KT25 tr.52] |
| Nghĩa vụ góp thêm/bảo lãnh | NQ 10 và NQ 13: **không có** điều khoản bảo lãnh/góp thêm/mua lại. **Mới:** phải thu dài hạn **1.600 tỷ** "tiền đã chuyển cho đối tác liên quan đến thoả thuận liên danh số 02/2026/TTLD ngày 08/05/2026" về Dự án Đại lộ cảnh quan sông Hồng (PPP, hợp đồng BT) tại 30/6 [BN TM9(ii)]. Tại 30/9 dòng này còn **100 tỷ** [HN-Q3 VI.4]. 1.500 tỷ chênh lệch có thể đã hoàn, chuyển vào TLSH/BĐS HP rời hợp nhất, hoặc phân loại lại: **chưa kiểm được** (Q3 không có thuyết minh). Đây là nghĩa vụ ngầm cần theo dõi. | [BN tr.37]; [HN-Q3 tr.17] |
| Dự án | KĐT Thư Lâm–Đông Anh 696 ha, TMĐT 60.558 tỷ, tiến độ Q1/2026–Q3/2029. Hà Nội giao ~429,5 ha tới cuối 09/2026 [báo]. Pháp lý gốc từng dự án: chưa đọc. | `web_tlsh_governance.md` |
| Bên mua các cty con BĐS H1 (lãi 4.929) | Bán 99,9% CTCP PT đô thị Mỹ Hào và 70% CTCP PT khu đô thị xanh [báo, dẫn thuyết minh]. Q1 có lãi chuyển nhượng ~3.800 tỷ liên quan Phân khu A KĐT Phố Nối [báo], khả năng nằm trong 4.929. **Bên mua, giá: chưa tìm được.** Không có bằng chứng bên mua là TLSH/BĐS HP. | [BN TM34]; `web_tlsh_governance.md` |

**Đọc:** giao dịch không thổi lợi nhuận (ghi theo sổ). Rủi ro nằm ở **chất lượng tài sản**:
- 12.664 tỷ (8,5% VCSH) cộng ≤1.600 tỷ ứng cho dự án BT, tổng **~9,5% VCSH** gắn vào một hệ sinh thái dự án đất lớn Hà Nội;
- giá chuyển nhượng đổi ×3 không giải thích;
- không công bố là giao dịch bên liên quan.

Mất 50% khoản TLSH = −4.958 tỷ ≈ −590 đ/cp **(ước lượng)**. Đây là đuôi trái, không thay đổi trung tâm. Mốc H7 vòng 1 giữ nguyên. **Thêm mốc H9**: BCTC kiểm toán 2026 thuyết minh được số phận 1.500 tỷ ứng liên danh và nêu rõ (có/không) bảo lãnh cho TLSH; P 0,6; chấm 2027-04-15.

## 2. Thuế ưu đãi

- **BCTC không công bố chi tiết.** TM37 [KT25] và TM39 [BN] chỉ ghi "Tập đoàn 20%; các công ty con … hưởng ưu đãi theo GCN đầu tư". Không có tên công ty, thuế suất, thời hạn.
- Đo được:
  - ETR hợp nhất 2025 = 2.574,2/18.040,6 = 14,3%; 6T/26 = 14,4%; Q3/26 = 9,3%.
  - **Phân khúc thép 6T/26: thuế 1.451,3 / LNTT 22.160,5 = 6,5%** [BN seg tr.55]. ⇒ Thép gần như đang ở chế độ miễn/giảm. Phần BĐS (gãi thoái vốn) chịu ~19,4% (1.030,2/5.323,2).
- Khung pháp lý [WEB]:
  - Dự án mới trong khu kinh tế (Dung Quất): 10% trong 15 năm, miễn 4 năm, giảm 50% 9 năm tiếp theo (nhadautu 24/09/2018).
  - CV 377/TCT-CS (30/01/2024): Tổng cục Thuế yêu cầu xác định **DQ2 là dự án MỚI hay MỞ RỘNG**. Kết luận **chưa tìm được**.
- Suy luận **(ước lượng)**:
  - DQ1 có thu nhập chịu thuế từ ~2019–2020 ⇒ đang ở pha giảm 50% (~5%) tới ~2031–2032, rồi 10% tới ~2034.
  - Nếu DQ2 là dự án mới ⇒ miễn tới ~2028–2029.
  - Nếu là mở rộng ⇒ ưu đãi chỉ theo phần còn lại của DQ1. ETR hiện tại có thể không bền.
- **Độ nhạy** (`calc/gaps_ri_sens_out.txt`, ETR gốc 12%):
  - LNST lõi TTM 22.943 về ETR 20% ⇒ **−2.086 tỷ/năm** (−9,1%). Lấy ETR Q3 9,3% làm gốc ⇒ −2.707 tỷ.
  - RI trọng số (Ke 12,3/13,0/13,4%):

| Kịch bản | Ke 12,3% | Ke 13,0% | Ke 13,4% |
|---|---|---|---|
| Không đổi thuế (vòng 1) | 19.176 | 17.278 | 16.338 |
| Chỉ terminal (2030+) chịu 20% | 16.501 | 14.886 | 14.086 |
| Từ 2027 | 16.012 | 14.438 | 13.658 |
| Từ 2028 | 16.193 | 14.604 | 13.817 |
| Từ 2029 | 16.352 | 14.750 | 13.956 |

  ⇒ **Năm hết ưu đãi chỉ lệch ~±300–500 đ/cp. Biến lớn là giả định terminal** (~−2.400–2.700 đ/cp). Vòng 1 ngầm giả định ETR ~12% **vĩnh viễn**. Đây là thiên lệch lạc quan cần nêu.

## 3. Vay, lãi vay vốn hoá, bảo đảm

- **Vay 31/12/2025** [KT25 TM23]: NH 64.695,0 (gồm DH đến hạn 8.826,2); DH 36.305,4 (trả >12 tháng 27.479,2). Tổng 101.000,4.
  - LS ngắn hạn VND 4,2–6,6%, USD 3,3–4,2%; DH 3,55–7,48%.
  - Vay USD 3.575 tỷ (31/12/25) → **12.612 tỷ (30/6/26)**. LS 30/6: VND 6,2–8,3%, USD 3,6–4,9% [BN TM25].
  - DH chủ yếu từ VCB: 30.016 tỷ (83%).
- **Bảo đảm** (31/12/25):
  - vay NH có bảo đảm 47.816 tỷ VND + 3.378 tỷ USD (2024: 44.119 + 2.496);
  - tài sản bảo đảm: HĐ tiền gửi, phải thu, HTK, đất trả trước, TSCĐ, BĐSĐT, XDCB, **và "cổ phiếu của CTCP Tập đoàn Hòa Phát do các cá nhân sở hữu"** [KT25 tr.37];
  - tiền gửi có kỳ hạn dùng thế chấp 6.809 tỷ (31/12/25) → **8.294 tỷ** (30/6/26) [BN TM6a]; XDCB thế chấp ~4.827 tỷ [BN TM17].
  - **Số lượng / % cổ phiếu HPG cá nhân cầm cố: KHÔNG công bố**, cả trong BCTC lẫn CBTT đã quét. ⚠️ WARNING giữ nguyên: giá HPG giảm sâu có thể kéo yêu cầu bổ sung tài sản bảo đảm, đan xen với nhóm cổ đông lớn.
- **Covenant: không thuyết minh** trong KT25/BN. Không thấy cờ vi phạm/phân loại lại nợ.
- **Lãi vay vốn hoá:**

| Kỳ | Vốn hoá | Vào P&L | Tổng | Tỷ lệ vốn hoá |
|---|---|---|---|---|
| 2024 | 1.310 | 2.287,4 | 3.597 | — |
| 2025 | **1.877** | 3.114,9 | 4.992 | 38% |
| 6T/25 | 1.261 | — | — | — |
| H2/25 (ước lượng) | 616 | — | — | — |
| 6T/26 | **162** | 2.853,0 | — | 5% |

  Nguồn: [KT25 TM15 tr.33; BN TM17 tr.43].
  - XDCB Dung Quất 60.108 (đầu 2025) → 6.301 (cuối 2025) ⇒ **DQ2 chuyển TSCĐ chủ yếu trong 2025**, vốn hoá dừng gần hết từ H2/2025.
  - ⇒ Xác nhận vòng 1: "vách lãi vay + khấu hao" **đã đi qua P&L**. Q3/26 không còn lợi nhuận "ẩn" nhờ vốn hoá.
  - XDCB DQ lại tăng 6.301 → 11.146 (30/9) cho hạng mục mới. Vốn hoá 2027+ nhỏ.

## 4. Sản lượng / thị phần / công suất [WEB: thông cáo gốc hoaphat.com.vn — bảng 8 quý đầy đủ ở `src/gaps/web_output_ad_peers.md` §1]

| Quý (nghìn t) | Tổng bán | XD+CLC | HRC | Ống | Tôn |
|---|---|---|---|---|---|
| Q1/25 | 2.380 | 1.192 | 993 | 186 | 89 |
| Q2/25 | 2.600 | ~1.300 | ~1.170 | 216 | 110 |
| Q3/25 | 2.500 | >1.000 | >1.200 | 225 | 120 |
| Q4/25 | 3.000 | 1.300 | 1.600 | 221 | 103 |
| Q1/26 | 3.000 | 1.400 | >1.400 | 241 | 106 |
| Q2/26 | 3.500 | 1.300 | 1.900 | 212 | 83 |
| Q3/26 | 3.800 | >1.300 | >2.000 (XK 24,6%) | 228 | 118 |
| **9T/26** | **10.300 (+39%)** | **>4.000 (+15%)** | **5.470 (+59%)** | 681 | 307 |

Phôi 9T 811k. Q4/2024 chỉ suy từ %; xem file.
- **Công suất**: HRC toàn tập đoàn **9 tr t/năm** (thông cáo 06/2026); DQ2 thiết kế 5,6 tr t HRC; thép thô **16 tr t/năm** (vòng 1 dùng 14–15 ⇒ sửa).
  - Lò cao DQ2 số 1 chạy thử cuối 03/2025; số 2 ra gang 04/09/2025 [báo]; HRC2 bán từ cuối 09/2025.
  - Hiệu suất: HRC 9T quy năm 7,3 / 9 = **~81% (ước lượng)** (vòng 1: 85%). Thép thô 10,7 × 4/3 = 14,3 / 16 = **~89% (ước lượng)**.
- **Thị phần thép XD**: HPG tự công bố 36% (Q1 và H1/2026). Thông cáo 9T không nêu. Số 35% của vòng 1 đến từ Bobby/VSA; VSA 9T theo vùng của HPG **chưa tìm được**.
  - Tính chéo **(ước lượng)**: HPG XD+CLC >4,0 tr t / ngành bán thép XD 11,64 tr t = **≥34,4%**. Khớp vùng 35–36%.
  - HRC 2025: 60% thị phần.
- **Giá bán/tấn từng nhóm**: BCTC không tách DT theo sản phẩm ⇒ **không tính được bằng số gốc**. Chỉ có bình quân thô của vòng 1 (~15,9 tr đ/t). XK theo nước Q3: chưa có.

## 5. Phòng vệ thương mại [WEB gốc MOIT/Federal Register — `src/gaps/web_output_ad_peers.md` §3]

| Vụ | Văn bản | Mức | Hiệu lực / mốc |
|---|---|---|---|
| VN AD HRC Trung Quốc (AD20) | Tạm thời QĐ 460/QĐ-BCT 21/02/2025 [báo]; **chính thức QĐ 1959/QĐ-BCT 04/07/2025** | 23,10–27,83% | 06/07/2025, 5 năm ⇒ ~07/2030 **(ước lượng)**. Ấn Độ: chấm dứt điều tra (<3% nhập khẩu) |
| Chống lẩn tránh | Điều tra QĐ 3176/QĐ-BCT 27/10/2025; **tạm thời QĐ 612/QĐ-BCT 02/04/2026** | 27,83% cho HRC TQ rộng 1.880–2.300 mm | QĐ chính thức: chưa thấy |
| **Rà soát hành chính lần 1** | **QĐ 1902/QĐ-BCT 27/07/2026** | có thể đổi mức | **Rủi ro nằm trong cửa sổ H4 (31/03/2027)** |
| Mỹ AD thép cây | Federal Register (đọc gốc) | HPG cuối **128,53%** (cash deposit 123,49%); toàn quốc 136,57%; sơ bộ 121,97% | Order ~18/09/2026; ITC khẳng định thiệt hại (báo Commerce 11/09/2026) |
| Mỹ CVD thép cây | Federal Register | cuối **6,80%** (sơ bộ 1,08%) | cùng đợt |
| EU AD HRC | Implementing Decision 2025/1919 (26/09/2025) [báo] | **HPG 0%** (DN VN khác 12,1%) | — |
| EU safeguard | vĩnh viễn từ 01/07/2026 [ngành] | ngoài hạn ngạch 50%, hạn ngạch tổng −47%, melt-and-pour từ 01/10/2026 | Hạn ngạch VN, tấn HPG xuất EU: chưa tìm được |
| CBAM | BCTN 2025: đã kiểm kê phát thải hàng xuất EU theo phụ lục CBAM với TÜV | **tCO₂/t: không công bố** | Phơi nhiễm: EU 3,6% DTT H1 [BN] ⇒ nhỏ |
| Vụ mới 2026 | Úc AD tôn mạ (Hoa Sen, Nam Kim); Ukraine/Thổ/Đài Loan mở vụ thép VN | — | **Chưa thấy vụ mới nhắm HPG** ngoài thép cây Mỹ |

**Xác minh F8 (Bobby):** mức 27,83% **ĐÚNG**. Số hiệu "QĐ 1917" **SAI**, đúng là **1959/QĐ-BCT**. Hết hạn không phải rủi ro trước 2030. Rủi ro gần là **kết quả rà soát hành chính QĐ 1902** và QĐ chính thức chống lẩn tránh. ⇒ H4 nên đổi chữ: "mức thuế AD HRC TQ áp cho nhà sản xuất chính sau rà soát hành chính ≥ 20%". P giữ 0,85–0,9 **(ước lượng)**.

## 6. Comp ngành có số

**Peers VN** [BQ `tav2_bq.ticker` 30/10/2026; ROE = `ticker_financial.ROE_Trailing` quý gần nhất]:
- HSG, NKG **BANNED**, chỉ tham chiếu. POM loại vì VCSH âm.
- Tính: `calc/gaps_peers_vn_out.txt`. Trung vị n=9: **P/E 13,35 · P/B 0,67 · EV/EBITDA 11,12 · ROE 8,0% (n=7)**.

| Mã | P/E | P/B | EV/EBITDA | ROE TTM |
|---|---|---|---|---|
| HSG (ref) | 13,3 | 0,74 | 8,1 | 5,6% |
| NKG (ref) | 24,1 | 0,75 | 16,8 | 3,1% |
| SMC | 2,1 (méo bởi lãi Q4/25) | 0,67 | 7,3 | 27,5% (méo) |
| TLH | 31,2 | 0,30 | 11,1 | 0,9% |
| TVN | 8,4 | 0,61 | 13,8 | 8,0% |
| VGS | 4,9 | 0,89 | 10,0 | 18,9% |
| HMC | 7,1 | 0,72 | 16,1 | 9,8% |
| **HPG** | **6,46 báo cáo / 7,7 lõi** | **1,19** | **5,1 lõi** (BQ rỗng) | **19,5%** báo cáo / ~16–17% lõi |

Bẫy: PE/EVEB của BQ dùng LN trễ, peers nhỏ thanh khoản mỏng ⇒ trung vị chỉ là chỉ báo.

**Peers khu vực** [WEB stockanalysis.com, giá 30/10/2026, một aggregator, tin cậy TRUNG BÌNH; bảng 8 hãng ở `web_output_ad_peers.md` §4]:
- Trung vị: **P/E trailing 13,48 (n=6) · forward 11,98 · P/B 0,57 · EV/EBITDA 7,79 · ROE 4,1% · biên gộp 9,6%** (7,2% nếu bỏ JSW/Tata; ROE 31,9% của JSW nghi sai dữ liệu).

**Kết luận (ước lượng):**
- HPG **rẻ hơn ~42–43% trên P/E lõi** và **~35–54% trên EV/EBITDA**.
- **Đắt hơn ~1,8–2,1 lần trên P/B**. Tỷ lệ P/B ÷ ROE của HPG 0,061 so với khu vực 0,138, tức rẻ hơn trên đơn vị ROE.
- Biên gộp 19% so với 7–10% của peers.
- Cách đọc: thị trường định giá HPG như thép toàn cầu đang ở đáy chu kỳ (P/E ~13 trên ROE ~4–8%), còn HPG ở ROE đỉnh nhờ AD + DQ2. Chiết khấu P/E ~40% tương đương kỳ vọng ROE HPG trôi về ~11–12%, khớp kịch bản cơ sở vòng 1 (ROE dài hạn 12,5%). ⇒ **Comp không đổi nhận định "xấp xỉ hợp lý"**. HPG không rẻ một cách hiển nhiên khi đã trừ lợi nhuận đỉnh.

## 7. β và chi phí vốn [BQ; `calc/gaps_beta.py` → `calc/gaps_beta_out.txt`]

| Đo (Close điều chỉnh, HPG vs VNINDEX, đến 30/10/2026) | β | 95% CI | Blume | corr |
|---|---|---|---|---|
| Tuần, 2 năm (n=104) | **0,844** | 0,65–1,04 | 0,896 | 0,64 |
| Tuần, 3 năm (n=156) | **0,894** | 0,74–1,05 | 0,929 | 0,67 |
| Ngày, 2 năm (n=496) | 0,880 | — | — | — |

- β < 1,1 có ý nghĩa thống kê ở cận trên CI (1,04–1,05).
- Lưu ý: HPG ~10% rổ VN30 nên β bị kéo về 1 (tự bao hàm). β ngành thép toàn cầu thường >1 (chưa đo). Khung user nói "β ~1,1 (Blume, kèm β peer)". **β peer VN chưa đo**: thanh khoản mỏng, β thấp giả.
- **Ke** (rf 6,75%; ERP nội địa 5,0–6,1%):

| β | Ke | RI trọng số (đ/cp) |
|---|---|---|
| 0,84 | 10,95–11,87% | 20.500–24.100 |
| Blume 0,90 | 11,25–12,24% | 19.400–22.800 |
| Blume 0,93 | 11,40–12,42% | 18.800–22.200 |
| 1,1 (vòng 1) | 12,25–13,46% | 16.200–19.300 |

  Nguồn: `calc/gaps_ri_sens_out.txt` (ước lượng).
- **Kết hợp với §2** (terminal chịu 20% thuế, trừ ~2.400–2.700): Blume 0,9–0,93 + thuế đầy đủ ≈ **16.400–20.400**, gần đúng vùng vòng 1 (16.300–19.200).
- **Đề xuất cho REPORT vòng sau (KHÔNG sửa vòng này):** báo Ke theo β đo **0,90–0,93 (Blume) ⇒ 11,3–12,4%** và đồng thời đưa thuế 20% vào terminal. Hai sửa đổi phải đi CÙNG nhau; chỉ sửa β sẽ thổi giá trị lên +3.000 đ/cp.
- Phép thử RONIC ≥ Ke: ROE dài hạn sau thuế 20% ≈ 11,4% ≈ Ke 11,3–12,4% ⇒ tăng trưởng gần như trung tính giá trị. Giữ g 5%, không nâng.

## 8. Room ngoại / thanh khoản

- **Sở hữu nước ngoài 30/10/2026: 21,8%**; room còn **2.296.677.911 cp = 27,2%** KLCP; trần 49% [WEB 24hmoney, báo]. Vòng 1 "26,4% còn lại / NN ~22,6%" (ACBS 04/2026) ⇒ NN **giảm nhẹ** ~0,8 pp **(ước lượng)**.
- Quỹ ngoại:
  - VanEck VNM: HPG **5,01% NAV, 29,49 tr cp** (29/10/2026).
  - Fubon: ~9–10% (snapshot cũ, không ngày).
  - Dragon Capital: số gần nhất 4,97% (29/03/2022), cũ.
  - BCTN 2025: không quỹ ngoại nào >5%.
- **ADV** [BQ, Price × Volume]:

| Kỳ | Bình quân (tỷ/phiên) | Trung vị (tỷ/phiên) |
|---|---|---|
| 3 tháng | **410** | 370 |
| 6 tháng | 474 | 426 |
| 10/2026 | 401 | 317 |

  Vòng 1 ghi 393 cho 10/2026, lệch nhỏ do cách tính.

## 9. Quản trị / nhân sự — ⚠️ WARNING

- **Cổ tức "15%"**: [WEB] nói 15% là **cổ tức năm 2025** (10% CP + 5% tiền 500 đ/cp, ĐHĐCĐ 21/04/2026), **không phải kế hoạch 2026**. Vòng 1 ghi "KH 2026 = 15% [BN TM28]" (notes_bs dòng 101). **Hai nguồn lệch, chưa đọc lại ảnh TM28** ⇒ cần kiểm lại trước khi dùng.
- **Thù lao HĐQT** [KT25 TM40 tr.52; BN TM42]:

| Kỳ | Thù lao HĐQT (tỷ) |
|---|---|
| 2024 | **244,7** |
| 2025 | **83,2** |
| 6T/26 | **207,7** |

  - Ngoài ra trích 180 tỷ thù lao/thưởng từ LNCPP trong 9T.
  - ĐHĐCĐ 2026 trích từ LNST 2025: quỹ KTPL 155 + thù lao HĐQT 155 + thưởng BĐH 25 = 331,7 tỷ [báo]. 2026: quỹ KTPL ≤5% LNST, thưởng BĐH ≤5% phần vượt kế hoạch [báo].
  - ⇒ Thù lao **biến động theo lợi nhuận**, 2024 còn cao hơn. "Tăng mạnh" ở vòng 1 đúng nhưng **không phải bất thường mới**.
  - Hệ quả EPS: BN trích quỹ & thù lao tạm tính **2,16% LNST** khi tính EPS [BN TM40 tr.61] ⇒ EPS lõi TTM ~2.717 × 0,978 ≈ **2.658 đ**; P/E lõi ~**7,9x** **(ước lượng)**.
- **ESOP/phát hành riêng lẻ**: không thấy. BN TM40: "không có cổ phiếu phổ thông tiềm năng".
- **Kiểm toán**: KT25 Deloitte; BCTC 2024 do "một công ty kiểm toán khác" kiểm toán [KT25]. Tên hãng cũ (KPMG?) và lý do đổi: **chưa xác nhận** (tờ trình ĐHĐCĐ 2025 không nêu tên).
- **Giao dịch nội bộ** [CBTT/báo]:
  - Trần Vũ Minh: đợt 1 mua 33.296.500 cp; đợt 2 đăng ký 50 tr cp (07/10–05/11/2026), trước giao dịch 230.652.290 cp = 2,732%; nhóm gia đình 35,455%.
  - Doãn Thị Bích Ngọc (chị Phó CT Doãn Gia Cường) bán xong 350.000 cp (14/10).
  - TV độc lập Đặng Ngọc Khánh đăng ký bán 100.000 cp (04/11–03/12).
- **Tin tiêu cực 2025–2026**: **không tìm thấy** xử phạt UBCKNN, truy thu thuế, khởi tố, vi phạm môi trường lớn. Gần nhất là QĐ 244/QĐ-XPHC 11/05/2022, phạt 125 tr vì thiếu TV HĐQT độc lập. Chưa quét trực tiếp ssc.gov.vn/gdt.gov.vn. "Không tìm thấy" ≠ "sạch".
- Cờ thuế mềm: CV 377/TCT-CS (2024) đề nghị cơ quan thuế xác định DQ2 mới/mở rộng và có thể kiểm tra thực tế. Có rủi ro **truy thu nếu DQ2 bị xếp "mở rộng"** mà đã hưởng ưu đãi dự án mới. Kết quả chưa tìm được (§2).

## 10. Chất lượng lợi nhuận — kiểm lại lõi 9T 19.243

- **Thuế trên khoản lãi thoái vốn**:
  - **1.030,2** là thuế TNDN phân khúc BĐS trên P&L H1 [BN seg]. **1.083** [HN-Q3 VI.13] là số dư thuế phải nộp của các công ty con **rời hợp nhất** (khoản BCĐKT), **không phải** chi phí P&L.
  - ⇒ Vòng 1 dùng 1.030 là **đúng**.
  - Thuế suất ngầm: 1.030,2 / LNTT BĐS 5.323,2 = 19,4%. Áp 20% riêng cho lãi 4.929,1 ⇒ thuế ~986 **(ước lượng)**.
- **Hai cách bóc** **(ước lượng)**:
  - (a) Vòng 1: bỏ TOÀN BỘ LNST BĐS 9T (4.497,9) + Q3 phi cốt lõi ⇒ **19.243**. Dùng cho dự phóng vì BĐS đã rời hợp nhất.
  - (b) Chỉ bỏ lãi thoái vốn sau thuế 20%: 4.929,1 × 0,8 = 3.943, cộng Q3 phi cốt lõi ~108 ⇒ 23.745,9 − 3.943 − 108 ≈ **19.695**. Giữ lợi nhuận BĐS vận hành ~555.
  - ⇒ Lõi 9T **19.200–19.700**, vòng 1 đứng ở đầu thận trọng ✓.
- **Q1 một lần**: DTTC Q1 5.938,3 so với Q2 616,7 ⇒ toàn bộ 4.929,1 nằm ở Q1. Lõi Q1 ≈ 9.055,9 − 4.929,1 + 1.030,2 − BĐS vận hành Q1 (~200–300, không tách được theo quý) ≈ **4.860–4.960 (ước lượng)**. Vòng 1 ghi "~5,2k" ⇒ **hơi cao ~250–350**.
  - Chuỗi lõi đúng hơn: Q1 ~4,9k → Q2 ~6,3k → Q3 ~8,0k. Gia tốc Q3 **rõ hơn**.
  - TTM lõi đổi rất ít (Q1 nằm trong TTM): ~22.943 → ~22.650 **(ước lượng)**, EPS sau trích quỹ ~2.625, P/E lõi ~8,0x.
- Không có lãi vay vốn hoá đáng kể nâng lợi nhuận 2026 (162 tỷ/6T, §3). Không có hoàn nhập dự phòng HTK. CFO 9T 1,09x LNST lõi ✓ (vòng 1).

---

## Bảng tổng hợp điểm yếu

| # | Điểm yếu | Trạng thái | Đổi hướng nhận định? |
|---|---|---|---|
| 1 | TLSH / BĐS | **Đóng phần số học** (1.920 tiền + 7.995 CP; 32.000 → ~10.271 là 2 phương án). **Mở**: lý do hạ giá ×3, thẩm định giá, ai góp 18.655 tỷ còn lại, 1.500 tỷ ứng liên danh, bên mua cty con H1, ngưỡng ĐHĐCĐ (Wendy) | Không đổi trung tâm. **Cờ quản trị NẶNG HƠN** (thêm H9) |
| 2 | Thuế ưu đãi | **Chưa đóng**: BCTC không công bố. Đo được ETR thép 6,5%; DQ2 mới/mở rộng chưa có kết luận | **Có, chiều xuống** cho mô hình: vòng 1 ngầm ETR 12% vĩnh viễn (−2.400–2.700 đ/cp nếu terminal 20%) |
| 3 | Vay / vốn hoá | **Đóng phần lớn**: vốn hoá 2025 1.877 → 6T/26 162; bảo đảm có CP HPG cá nhân. **Mở**: số lượng CP cầm cố, covenant (không công bố) | Không. Xác nhận "vách lãi vay đã qua" |
| 4 | Sản lượng / thị phần | **Đóng**: 8 quý gốc, công suất 16 tr t thép thô / 9 tr t HRC. **Mở**: VSA theo vùng, XK theo nước, giá/tấn theo SP | Không |
| 5 | AD / CBAM / PVTM | **Đóng**: QĐ 1959 (không phải 1917), Mỹ 128,53% + CVD 6,80%, EU AD 0%. **Mở**: kết quả rà soát QĐ 1902, QĐ chính thức chống lẩn tránh, tCO₂/t | Không. **Đổi chữ H4** sang rủi ro rà soát |
| 6 | Comp | **Đóng** (VN từ BQ, khu vực từ aggregator tin cậy trung bình) | Không: rẻ trên P/E vì lợi nhuận đỉnh, đắt trên P/B |
| 7 | β / Ke | **Đóng**: β 0,84–0,89, Blume 0,90–0,93 | Lên +2.000–3.600 đ/cp nếu chỉ sửa β; **triệt tiêu** khi sửa cùng thuế (§2) |
| 8 | Room ngoại / ADV | **Đóng**: NN 21,8%, room còn 27,2%, ADV 3M 410 tỷ | Không |
| 9 | Quản trị | **Đóng một phần**: thù lao có lịch sử (2024: 244,7); không ESOP; tin tiêu cực không thấy. **Mở**: tên KTV 2024 + lý do đổi, cổ tức 15% là 2025 hay 2026 | Không. WARNING giữ |
| 10 | Chất lượng LN | **Đóng**: 1.030 đúng; lõi 9T 19,2–19,7k; Q1 lõi ~4,9k | Không. Gia tốc Q3 rõ hơn |

**Kết luận vòng 2:** vùng **17.000–23.000, trung tâm ~20.000 đ GIỮ NGUYÊN (ước lượng)**, nhưng cấu phần đổi:
- β thấp hơn kéo lên;
- thuế không vĩnh viễn kéo xuống;
- TLSH thêm đuôi trái ~−600 đ/cp (ước lượng) và cờ quản trị.

## Số vòng 1 cần SỬA (cho REPORT vòng sau — KHÔNG sửa trong vòng này)

1. §1/§7, β: "β ~1,1, chưa đo" → **β đo 0,84 (2y tuần) / 0,89 (3y), Blume 0,90–0,93**. Sửa Ke đi kèm thuế terminal 20% (§2, §7 file này).
2. §3d/§10#17, thuế: "thời hạn chưa kiểm được" → BCTC **không công bố**. ETR thép 6T/26 **6,5%**; DQ2 mới/mở rộng chưa có kết luận (CV 377/TCT-CS). Mô hình phải nêu giả định ETR terminal.
3. §5/§9 H4/§10#15, AD HRC: số hiệu **QĐ 1959/QĐ-BCT (04/07/2025)**, hiệu lực 06/07/2025 → ~07/2030. Thêm rà soát hành chính **QĐ 1902 (27/07/2026)** và chống lẩn tránh **QĐ 612 (02/04/2026)**. Báo Bobby F8: "QĐ 1917" sai số hiệu.
4. §5/§10#14, Mỹ: "121,97%" là sơ bộ → **cuối 128,53%** (cash deposit 123,49%) + **CVD 6,80%**.
5. §5, EU: thêm AD HRC EU với HPG **0%**. CBAM: HPG đã kiểm kê (TÜV), không công bố tCO₂/t.
6. §5/§10#3, công suất: thép thô **16 tr t/năm**, HRC **9 tr t/năm** ⇒ hiệu suất HRC **~81%** (không phải 85%).
7. §4, cổ tức: "KH 2026 = 15%" **mâu thuẫn** với nguồn web (15% = cổ tức 2025). Đọc lại ảnh BN TM28 trước khi dùng.
8. §3b/§4, EPS lõi: trừ trích quỹ & thù lao ~2,16% LNST [BN TM40] ⇒ EPS lõi TTM ~**2.625–2.660**, P/E lõi **~7,9–8,0x** (không phải 7,7x).
9. §3b, chuỗi lõi Q1: "~5,2k" → **~4,9k (ước lượng)**.
10. §6, TLSH:
    - "9.915 tỷ" = **1.920 tiền (15% tại 30/6) + 7.995 CP BĐS HP**;
    - 32.000/10.270 là **hai phương án NQ 10 vs NQ 13**, không phải hai nguồn báo sai;
    - thêm **phải thu liên danh Đại lộ sông Hồng 1.600 tỷ (30/6) → 100 tỷ (30/9)**;
    - thêm "không công bố là giao dịch bên liên quan; chỉ HĐQT thông qua".
11. §6, thù lao HĐQT: thêm bối cảnh **2024 244,7 · 2025 83,2 · 6T/26 207,7**.
12. §8: room ngoại còn **27,2%**, NN **21,8%** (30/10/2026); ADV 3M **410 tỷ**.
13. §7, comp: "chưa kiểm được" → trung vị VN P/E 13,35 / P/B 0,67 / EV/EBITDA 11,1; khu vực P/E 13,5 / P/B 0,57 / EV/EBITDA 7,8.
14. §10#11, lãi vay vốn hoá: "chưa kiểm được" → **2025: 1.877 tỷ; 6T/26: 162 tỷ**.

## Đã thử nhưng chưa tìm được

- Bên mua các cty con BĐS H1 và giá.
- Tổ chức thẩm định giá BĐS HP; lý do hạ giá ×3.
- Ai góp 18.655 tỷ vào TLSH; cơ cấu cổ đông TLSH sau tăng vốn.
- Số CP HPG cá nhân cầm cố; covenant.
- Kết luận DQ2 dự án mới hay mở rộng; ngày hết ưu đãi từng nhà máy.
- VSA thị phần 9T theo vùng của HPG; XK theo nước Q3.
- Hạn ngạch EU riêng VN; tấn HPG xuất EU.
- Dragon Capital/DCVFM 2026.
- Tên KTV 2024 và lý do đổi.
- β peer VN (không đo: thanh khoản mỏng).

Truy vấn và URL đã thử: `src/gaps/web_*.md` mục "chưa tìm được".
