# DD — NNC (CTCP Đá Núi Nhỏ) cho sleeve discretionary · 2026-10-26 · job `Taylor_20261026_012529`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua. User quyết. Khung: `calculated_fear_state_backstop.md`
> §2.5 (nhóm (b) chu kỳ ngành). Không có scandal ⇒ §2 (nhóm a) chỉ dùng để quét pháp lý/quản trị.
> Nguồn: **[BCTC]** = BCTC riêng Q3/2026, ký 19/10/2026 (bản scan, `src/NNC_Baocaotaichinh_Q3_2026.pdf`, đọc
> từng trang ảnh); **[BCTN25]** = Báo cáo thường niên 2025 (`src/NNC_Baocaothuongnien_2025.pdf`);
> **[BQ]** = `tav2_bq.ticker_financial` / `tav2_bq.ticker` (CANONICAL theo `kb/data_registry/fundamentals/ticker_financial.md`;
> KHÔNG dùng `OShares` của NNC làm số CP — lấy vốn điều lệ 219,2 tỷ / 10.000 = 21,92 tr cp [BCTC V22]);
> **[VS]** = Vietstock 22/10/2026; **[AWM]** = blog AWMFund 05/06/2026 (nguồn thứ cấp, CHƯA đối chiếu CBTT);
> **[TNCK]** = Tin nhanh chứng khoán 25/03/2026. Tính toán: `calc/valuation.py` → `calc/valuation_out.txt`.
> Số không đo được gắn nhãn **(ước lượng)**. Giá tham chiếu: **47.600 đ** (đóng cửa 23/10/2026, [BQ]).

## 0. Kết luận

**Verdict: NON** đối với sleeve fear-buy. Đây **không phải ca sợ hãi**: lợi nhuận đang ở **đỉnh kỷ lục**
và PB 1,59. Về mặt giá trị thuần thì cổ phiếu **rẻ** (giá trị theo kịch bản có trọng số ≈ **62.800 đ**,
+32%), nhưng loại ý tưởng này thuộc phạm vi value/BAL (§9 playbook), không phải sleeve fear-buy.

| Tiêu chí §2.5 | Phán quyết | Bằng chứng chính |
|---|---|---|
| #1 Khủng hoảng chu kỳ/tạm thời | ❌ **Không có khủng hoảng** | Q3/26 LNST 69,3 tỷ, kỷ lục; 9T +70% YoY [BCTC]. Giá giảm 65.678 (TB 12/2025) → 38.450 (07/10/2026) rồi hồi lên 47.600 [BQ]: đó là **hạ định giá khi lợi nhuận đang TĂNG**, không phải hoảng loạn trên lõi hỏng |
| #2 Sống sót qua đáy | ✅ MẠNH | Net cash **273,0 tỷ** = 12.455 đ/cp = 26% vốn hoá; vay chỉ 74,9 tỷ (69,9 DH + 5,0 NH) [BCTC] |
| #3 Leader chi phí thấp | ✅ (cục bộ) | Biên gộp 9T/26 **54,3%**, Q3 **57,9%** [BCTC]; đá là hàng địa phương (cự ly vận chuyển quyết định thị trường [BCTN25]); mỏ Mũi Tàu bán vào TP.HCM/Đồng Nai, khu vực "cầu > cung" [BCTN25] |
| #4 Sàn tài sản thực PB≲1 | ❌ | PB **1,59** (BVPS 29.915 [BCTC/BQ]). Sàn thật nằm ở **dòng tiền mỏ + tiền mặt**, không ở book |
| Loại: mua ở đỉnh chu kỳ | ⚠️ **dính** | Giá đá ≈ +25% YoY, ≈ +50% so 2023–24 [AWM]; biên gộp 57,9% là cao nhất kể từ khi chuyển sang mỏ Mũi Tàu. PE thấp ở đỉnh chu kỳ là bẫy kinh điển (bài học HPG §8, theo chiều ngược lại) |

**Giả thuyết của user ("giống SCL, ăn theo chu kỳ VLXD đầu tư công")**: **ĐÚNG một phần.** NNC đúng là ăn theo
đầu tư công hạ tầng phía Nam (BCTN25 tự nhận đây là thị trường chính). Nhưng **SCL (Sông Đà Cao Cường) bán tro bay**
(phụ gia bê tông/xi măng, nhà máy ở Hải Dương), không bán đá. Hai mã chỉ giống nhau ở chỗ cùng chịu chu kỳ cầu
VLXD; khác nhau ở sản phẩm, vùng thị trường và loại rủi ro. Rủi ro đặc thù của NNC là **giấy phép mỏ và trần công suất**.

**Điều kiện đổi verdict** (§6): phải có **một cú sốc thật** làm giá về khoảng **≤ 30.000 đ** (PB ≲ 1,0; khoảng
giá đó vẫn ≥ net cash + MVC + dòng tiền kịch bản "deep") **trong khi** giấy phép Mũi Tàu và dự án Tam Lập còn
nguyên. Ở giá hiện tại, câu hỏi đúng là có cho NNC vào **value screen** hay không, và việc đó không thuộc DD này.

**Pháp lý: 3 WARNING, chưa thấy vụ việc nào** (§7). Đáng chú ý nhất: (i) **rủi ro sở hữu chéo NNC↔MVC** nếu MVC
lên 51%; (ii) dấu hiệu sản lượng có thể **vượt trần công suất cấp phép**, chưa xác minh.

---

## 1. Mô hình kinh doanh và mỏ — rủi ro cấu trúc

| Mỏ | Trạng thái | Số liệu | Nguồn |
|---|---|---|---|
| **Núi Nhỏ** (Dĩ An, 27,34 ha, trữ lượng gốc 17,152 tr m³, công suất 2 tr m³/năm) | **Hết giấy phép 31/12/2019**, có đề án đóng cửa mỏ (QĐ 19/QĐ-UBND 06/01/2021). Hiện **cho thuê mặt bằng** (ISA, Khang Thư, Rồng Đỏ container, Ngọc Phúc, Quang Minh, Viconship) | DT dịch vụ Q3/26 **6,17 tỷ** [BCTC VI.1]. 07/2025 được duyệt bổ sung ~5,1 tr m³ (phần trụ bảo vệ), tiền cấp quyền **20,43 tỷ** [BCTC V16 đầu năm, TNCK] | BCTN25, BCTC |
| **Mũi Tàu / "Tân Lập"** (xã Tân Lập, Đồng Phú, Bình Phước cũ, nay thuộc Đồng Nai; 51,5 ha) | **Mỏ chính, đang khai thác.** Giấy phép 01/2019: trữ lượng **22,509 tr m³**, công suất **1,0 tr m³/năm nguyên khối**, **hạn đến 2043**; chế biến 1,421 tr m³ thành phẩm/năm | DT Q3/26 > 143 tỷ [VS]. 2025 là "năm đầu tiên khai thác hết công suất cấp phép" [BCTN25] | BCTN25 |
| **Tam Lập 1 khu II** (mỏ mới) | Đang đầu tư. CIP: đền bù/chuyển nhượng QSDĐ **79,48 tỷ** + đặt trước tiền cấp quyền **4,03 tỷ** [BCTC V10a] | Trữ lượng > 11 tr m³, 1 tr m³/năm, có đá thương phẩm từ **2028**, giá trúng đấu giá ~74 tỷ [AWM — chưa đối chiếu CBTT] | BCTC, AWM |
| **NHC** (Gạch ngói Nhị Hiệp, 23,35%) | Liên kết. NNC đang đầu tư máy nghiền 350 t/giờ ghi "(Cty NHC)" **21,29 tỷ** trong CIP của NNC [BCTC V10a] | AWM: NHC 500k m³/năm từ 2027, NNC dự kiến nắm 35% | BCTC, BCTN25 |

**Trữ lượng còn lại của Mũi Tàu:** chưa có số công bố. **Ước lượng:** 22,509 tr m³ (2019) trừ khai thác 2019–26
khoảng 5–6 tr m³ (giả định 2019–24 trung bình 0,6–0,8 tr m³/năm, 2025–26 là 1,0) ⇒ còn khoảng **16–17 tr m³**. Con số này
khớp với **~17 năm** từ 2027 tới hạn giấy phép 2043 ở công suất 1 tr m³/năm. ⇒ **Đuôi rủi ro cấu trúc thấp tới
khoảng 2040**; ràng buộc thật là **TRẦN CÔNG SUẤT** (không tăng được sản lượng nếu không điều chỉnh giấy phép) và
**thời hạn 2043**. Muốn tăng trưởng phải có mỏ mới qua đấu giá (Luật Địa chất và Khoáng sản 2024): công ty tự nói
"đầu tư mỏ mới hiện nay phải thông qua đấu giá quyền khai thác khoáng sản" [VS].

**Bài học của chính NNC — chu kỳ 2019–2023 KHÔNG phải chu kỳ thuần.** LNST năm [BQ]: 2016 183 · 2017 191 · 2018 186 ·
2019 123 · 2020 124 · **2021 38,5 · 2022 39,3 · 2023 36,6** · 2024 62,6 · 2025 147,8 [BCTN25] · TTM 214,0.
Đáy 2021–23 (doanh thu ~20 tỷ/quý từ 2021Q3 tới 2023Q1) chủ yếu là **cú sốc CẤU TRÚC: mỏ Núi Nhỏ hết giấy phép**
(mỏ 2 tr m³/năm, sát TP.HCM). Mũi Tàu khi đó chưa chạy hết công suất, cộng thêm COVID 2021. Tức là rủi ro lớn nhất
của NNC đã từng xảy ra một lần: **hết mỏ ⇒ LN −80%**. Kịch bản đó sẽ lặp lại **sau 2043** nếu không có mỏ thay thế,
nên định giá phải dùng **dòng tiền có thời hạn** (§5), không dùng PE vĩnh viễn.

## 2. Kết quả Q3/2026 [BCTC] — chất lượng lợi nhuận

| Khoản mục (tỷ) | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|
| DT thuần | **149,49** | 100,27 | **402,20** | 261,89 |
| — thành phẩm đá / hàng hoá / dịch vụ | 139,97 / 3,35 / 6,17 | 91,41 / 3,89 / 4,97 | — | — |
| LN gộp | 86,54 | 50,67 | 218,52 | 128,34 |
| **Biên gộp** | **57,9%** | 50,5% | **54,3%** | 49,0% |
| DT tài chính (lãi tiền gửi) | 6,07 | 7,60 | 15,60 | 13,48 |
| Chi phí BH + QLDN | 5,14 | 4,00 | 12,87 | 14,02 |
| LN khác | −0,30 | −1,88 | **−19,29** | −4,18 |
| LNTT | 86,61 | 52,04 | 200,14 | 116,28 |
| **LNST** | **69,29** | 42,56 | **160,08** | 93,95 |

- **Một lần (9T/26):** chi phí khác 22,0 tỷ, phần lớn là truy thu nhà nước cho mỏ Núi Nhỏ đã đóng: **tiền cấp quyền
  khai thác bổ sung 15,58 tỷ + tiền thuê đất bổ sung năm 2019 là 5,95 tỷ** (đã trích lập dự phòng phải trả NH, V19a). ⇒ LN
  lõi 9T cao hơn số báo cáo khoảng 17 tỷ sau thuế (ước lượng ×0,8). TTM lõi ≈ TTM báo cáo ≈ **214 tỷ**, vì khoản cộng lại
  bù gần đúng phần lãi tiền gửi bị trừ ra.
- **CF_OA 9T/26 = 109,3 tỷ vs LNST 160,1 (tỷ lệ 0,68)** [BCTC LCTT]. Nguyên nhân chính là "tiền chi khác cho HĐKD"
  **107,2 tỷ** (9T/25: 34,0), nhiều khả năng gồm việc nộp tiền cấp quyền 20,4 tỷ đầu năm và các khoản phí/thuế tài nguyên
  (chưa tách được, **chưa đo**). Q3 tốt hơn: CF_OA ≈ 63,1 tỷ vs LNST 69,3 [BQ CF_OA_P0]. Phải thu KH tăng từ 6,79 lên 21,29 tỷ
  (~13 ngày DT), vẫn thấp. **Không có red-flag kiểu PVX** (§10.10).
- **Cấu trúc chi phí Q3/26 theo yếu tố** (58,74 tỷ): NVL 16,83 · nhân công 7,53 · khấu hao 5,56 · dịch vụ mua ngoài 14,98 ·
  chi khác bằng tiền 13,84 (gồm phí/thuế tài nguyên; số dư thuế tài nguyên phải nộp 0,97 tỷ) [BCTC VI.9, V16]. Khấu hao
  thấp (~22 tỷ/năm, ước lượng) ⇒ đòn bẩy vận hành cao theo **giá bán**: giá tăng thì phần lớn chảy thẳng vào LN, giá
  giảm thì chiều ngược lại cũng mạnh như vậy.
- **Giá hay sản lượng?** VS: "tăng nhờ sản lượng đá tiêu thụ và giá bán tăng". AWM (06/2026): giá TB **+25% YoY, +50% vs 2023–24**
  (chưa có nguồn giá gốc). DT 9T +54% YoY. Nếu giá +25% thì sản lượng ≈ **+23%** (ước lượng). Nhưng **2025 đã chạy 100% công
  suất cấp phép** [BCTN25] ⇒ xem WARNING #2, §7.

**Lệch dữ liệu phải ghi (không tự chọn im lặng):**
- `GPM_P0` [BQ] = 0,533 (Q3/26), 0,436 (Q3/25) **không khớp** biên gộp quý tính từ BCTC (57,9% / 50,5%). Lệch cùng chiều
  với ca DDV: cột này **không phải biên gộp quý**. Báo cáo này dùng BCTC.
- `Cash_P0` [BQ] = 25,5 tỷ = đúng "tiền & tương đương", nhưng **thiếu 322,4 tỷ tiền gửi giữ đến đáo hạn** (mã 123: kỳ hạn
  6 tháng 278,97 + 12 tháng 43,47). Ai đọc BQ sẽ tưởng NNC ít tiền (cùng loại bẫy với DDV).
- `LtInvest_P0` [BQ] 119,3 = giá trị sổ sách MVC 103,0 + NHC 21,67 − dự phòng 5,35. Giá thị trường cổ phần MVC = 147,3 tỷ (§5).
- `NP_P0` [BQ] khớp BCTC: 9T/26 = 39,6+51,2+69,3 = 160,1 ✓; FY2025 = 147,8 ✓ [BCTN25].
- **Kế hoạch 2026** (LNTT 120 tỷ, −35%) [TNCK] đã bị vượt 67% sau 9T (LNTT 200,1). Đây là **kế hoạch thận trọng có chủ đích**,
  không phải tín hiệu xấu. Lý do chính thức của mức kế hoạch thấp: **không tìm thấy** trong tài liệu.

## 3. Đầu tư công — giả thuyết cầu

- BCTN25: "Đầu tư công về hạ tầng giao thông và đầu tư BĐS là hai lĩnh vực sử dụng nhiều sản phẩm của công ty… thị trường
  2026 được dự báo thuận lợi do Chính phủ đang đẩy mạnh đầu tư đồng bộ hạ tầng giao thông khu vực phía Nam"; "lượng cầu về
  đá xây dựng lớn hơn cung, nên việc cạnh tranh giữa các đơn vị cùng ngành ít".
- Kế hoạch đầu tư công 2026–2030 là **8,22 triệu tỷ**, gấp hơn 2,5 lần giai đoạn trước [AWM]. Đây là con số thứ cấp, **chưa đối
  chiếu** văn bản Quốc hội.
- **Chưa xác minh được** NNC cung cấp cho tuyến cụ thể nào (Vành đai 3/4, Biên Hòa–Vũng Tàu, Long Thành): BCTN25 và BCTC
  không nêu tên khách hàng/dự án. Bán kính thị trường là TP.HCM, Đồng Nai và một phần Tây Ninh [BCTN25], nằm trong vùng các
  dự án trên **về mặt địa lý**. Vì vậy liên kết này là suy luận địa lý, chưa có bằng chứng hợp đồng.
- Giá đá bán lẻ TP.HCM 2026 trên các trang báo giá dao động **420.000–660.000 đ/m³** (đá 1x2). Nguồn bán lẻ không chính thức,
  **không dùng làm số đo**. Không có chuỗi giá đá chính thức nào trong `kb/data_registry/feeds/` (đã tra).
- **Hàm ý chu kỳ:** cầu đá Đông Nam Bộ 2026–2028 nhiều khả năng còn cao (giải ngân đầu tư công). Rủi ro chiều xuống đến từ
  (a) chậm giải ngân, (b) mỏ mới được đấu giá cấp phép làm tăng cung, (c) BĐS yếu. Ước lượng chủ quan: giá đá **không** giữ
  mãi ở mức +50% so 2023–24; mức hiện tại nên coi là **đỉnh/gần đỉnh chu kỳ**.

## 4. Bảng cân đối, cổ đông, cổ tức [BCTC 30/9/2026]

- Tổng tài sản 823,1 · VCSH **655,7** · Nợ phải trả 167,4 (vay 74,9; thuế phải nộp 27,1; dự phòng phải trả NH 22,4; ký quỹ
  phục hồi môi trường Tân Lập 4,5). Vay DH tăng từ 22,2 lên 69,9 tỷ trong 9T, khớp với đầu tư Tam Lập (CIP 108,0 từ 0).
- **Capex 9T 131,1 tỷ** (9T/25: 53,9), chủ yếu là **tăng trưởng** (Tam Lập 83,5; máy nghiền 24,5).
- **Cổ đông** [BCTC V22]: **MVC (CTCP Vật liệu & Xây dựng Bình Dương) 43,55%** · CTCP Đầu tư Thái Bình 15,93% · bà Nguyễn Thị
  Mai Phương 7,01% · khác 33,5%. Free float mỏng ⇒ thanh khoản ~1–2,7 tỷ/phiên (tháng 10/2026 [BQ]). Funnel ghi 0,96 tỷ.
- **Sở hữu chéo:** NNC nắm **10,3 tr cp MVC** (giá vốn 103 tỷ, ≈ 10,3% của 100 tr cp MVC [BQ OShares]); MVC nắm 43,55% NNC.
  AWM nói MVC định mua thêm ~7% để lên 51% (chưa đối chiếu CBTT). → WARNING #1.
- **Cổ tức:** tỷ lệ trả 2025 là **61,37% LN** (2024: 26,28%) [BCTN25]. Năm 2026 tới nay mới thấy chi 21,92 tỷ (= 1.000 đ/cp)
  [BCTC V22, LCTT]. Lịch các đợt cổ tức 2025 còn lại **chưa đối chiếu**. DY [BQ] 2,1%.

## 5. Định giá — trên LN chuẩn hoá chu kỳ, KHÔNG dùng Q3 đơn lẻ

**Phần ngoài lõi (tỷ):** net cash 273,0 + MVC theo giá thị trường 147,3 (10,3 tr × 14.300) + NHC theo book 14,1 = **434,4 tỷ
= 19.820 đ/cp (42% giá)**. Phần lõi mà thị trường đang định giá là **608,9 tỷ ⇒ PE lõi 2,85x** trên TTM 214 tỷ.
Nói cách khác, giá 47.600 chỉ hàm ý **LN ổn định ~96 tỷ/năm** cho 17 năm tới 2043 (r = 14%): bằng **45% TTM**, thấp hơn
cả LN 2025.

**DCF dòng tiền mỏ CÓ THỜI HẠN** (2027–2043, 17 năm, Mũi Tàu ở trần 1 tr m³ nguyên khối; FCF ≈ LN vì khấu hao ≈ capex
duy trì (ước lượng); không cộng lãi tiền gửi vì đã nằm trong net cash; thuế 20%; **mọi giả định giá/biên là ước lượng**):

| Kịch bản | DT/năm | Biên gộp | LN/năm | Giá trị/cp r=14% | Xác suất (chủ quan) |
|---|---|---|---|---|---|
| Deep: giá đá về mặt bằng 2023–24 (~0,67x TTM) | 360 | 35% | 83 | **44.000** | 20% |
| Bear: ~mặt bằng 2025 | 400 | 42% | 117 | 53.800 | 25% |
| Base: giá −12% từ TTM | 470 | 50% | 169 | 68.900 | 40% |
| Bull: giữ mặt bằng Q3/26 | 560 | 56% | 230 | 86.700 | 15% |
| **Trọng số** | | | | **62.800 (+32%)** | |

Độ nhạy r: 13% → 65.200 · 16% → 58.600 [calc/valuation_out.txt]. **Không tính** (đều là upside):
Tam Lập 1 khu II (ước lượng rất thô ~15.000 đ/cp nếu chạy được từ 2028, phụ thuộc số liệu AWM chưa xác minh); giá trị đất/cho
thuê Núi Nhỏ; quyền tận thu 5,1 tr m³ trụ bảo vệ Núi Nhỏ. **Rủi ro không mô hình hoá:** phạt hoặc điều chỉnh nếu sản lượng vượt
trần (§7); MVC buộc phải thoái vốn khỏi MVC ở giá xấu; chi phí đóng cửa mỏ.

**So sánh nhanh** ([BQ] 23/10/2026, PE trailing): VLB (đá Biên Hòa, cùng vùng) **3,57x**, PB 2,02 · DHA (đá Hoá An) 7,48x, PB
1,50 · KSB 7,70x, PB 0,55 · NNC 4,88x, PB 1,59. ⇒ Thị trường định giá **cả nhóm đá Đông Nam Bộ ở PE thấp**, nhất quán với việc
coi đây là đỉnh chu kỳ cộng tài sản cạn dần. NNC không rẻ bất thường so với VLB. NNC chỉ rẻ khi tách tiền mặt và MVC ra.

## 6. Điều kiện đổi verdict

- **→ QUALIFY/AMBIGUOUS (fear-buy):** có cú sốc thật (đầu tư công đình trệ, giá đá sập, hoặc sự kiện pháp lý **nhỏ và cô lập**
  về công suất/phí) đẩy giá về **≤ ~30.000 đ** (PB ≲ 1,0; ≈ deep-case trừ biên an toàn), **đồng thời** (a) giấy phép Mũi Tàu không
  bị rút hoặc giảm công suất, (b) Tam Lập vẫn đúng tiến độ 2028, (c) net cash ≥ 200 tỷ.
- **→ NON vững hơn (kể cả với value screen):** (a) có quyết định xử phạt hoặc đình chỉ vì vượt công suất kèm truy thu lớn;
  (b) Q4/26–Q1/27 biên gộp rơi về < 45% trong khi DT đi ngang (giá đá quay đầu); (c) Tam Lập trễ hoặc đội vốn đáng kể; (d) MVC
  lên ≥ 51% mà NNC buộc phải bán cổ phần MVC dưới giá trị.
- **Theo dõi:** BCTC Q4/26 (cuối 01/2027); CBTT giao dịch cổ đông lớn của MVC; giấy phép khai thác Tam Lập 1 khu II; thuyết minh
  "chi khác cho HĐKD".

## 7. Pháp lý — chỉ WARNING (luật 2026-09-27)

Không tìm thấy vụ xử phạt, thanh tra hay khởi tố nào liên quan NNC trong các tìm kiếm của job này (tìm theo tên + "xử phạt/
vượt công suất/thanh tra/truy thu"). Đây **không** phải tra cứu pháp lý chính thức; nếu Mike gọi bước tiếp thì nên nhờ legal-vn xác minh.

1. **WARNING — sở hữu chéo NNC↔MVC.** MVC nắm 43,55% NNC; NNC nắm ~10,3% MVC. Nếu MVC lên ≥ 51% (kế hoạch theo AWM, chưa
   xác minh) thì NNC thành **công ty con** của MVC. Luật Doanh nghiệp 2020 (Điều 195 khoản 2, theo hiểu biết của tôi, chưa
   được legal-vn xác nhận) **cấm công ty con sở hữu cổ phần của công ty mẹ** ⇒ NNC có thể phải thoái 147 tỷ cổ phần MVC (≈ 6.700 đ/cp
   giá trị NNC), có thể ở thời điểm/giá bất lợi. Thêm vào đó là rủi ro giao dịch bên liên quan khi cổ đông mẹ kiểm soát.
2. **WARNING — có thể vượt trần công suất (SUY LUẬN, CHƯA XÁC MINH).** Giấy phép là 1,0 tr m³/năm nguyên khối; 2025 đã đạt 100%
   [BCTN25]; DT 9T/26 +54% trong khi giá chỉ +~25% (AWM) ⇒ sản lượng ước +~23%. Các giải thích **vô hại** có thể có: chênh lệch
   tồn kho thành phẩm, cơ cấu sản phẩm (đá mi/đá 1x2 giá cao hơn), tận thu tại Núi Nhỏ theo phê duyệt 2025, hoặc giá tăng nhiều hơn
   25%. **Cần số sản lượng m³ theo quý** để kết luận. Theo NĐ 36/2020 (đang được thay thế), vượt công suất bị phạt tiền theo tỷ lệ
   vượt, có thể kèm đình chỉ.
3. **WARNING — truy thu tiền cấp quyền/tiền thuê đất.** Năm 2026 đã trích 21,5 tỷ truy thu cho mỏ Núi Nhỏ (đã đóng), nghĩa là cơ quan
   nhà nước **đang rà lại** nghĩa vụ tài chính khoáng sản. Rủi ro truy thu tương tự cho Mũi Tàu khi chuyển sang khung Luật Địa chất
   và Khoáng sản 2024 là có thể xảy ra nhưng **chưa định lượng được**.

Không thấy vấn đề kiểm toán: BCTC 2025 có ý kiến chấp nhận toàn phần [BCTN25].

## 8. Hạn chế của DD này

- BCTC Q3 là bản scan. Số trong báo cáo được đọc trực tiếp từ ảnh trang 1–6, 16–24 (chưa đọc hết trang 25–33). Chưa đọc BCTC 2025
  kiểm toán (đã tải `src/NNC_Baocaotaichinh_2025_Kiemtoan.pdf`, cũng là bản scan).
- Chưa có số **sản lượng m³ và giá bán/m³** từ nguồn công ty. Đó là input quan trọng nhất cho cả WARNING #2 lẫn định giá.
- Trữ lượng còn lại của Mũi Tàu và các số về Tam Lập/NHC lấy từ nguồn thứ cấp hoặc là ước lượng.
- Xác suất các kịch bản là chủ quan; giá trị theo kịch bản có trọng số không phải dự báo giá.
