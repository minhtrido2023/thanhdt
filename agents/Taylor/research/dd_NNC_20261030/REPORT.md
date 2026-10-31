# DD — NNC (CTCP Đá Núi Nhỏ) · bản TRUNG DUNG · as-of 30/10/2026 · job `Taylor_20261030_160612`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua/bán. Không chấm §2.5 fear-buy (theo brief). User quyết.
> Nguồn — đọc lại **độc lập từ ảnh trang** (pymupdf render, 110 dpi) trước khi mở bản 26/10:
> **[Q3]** BCTC riêng Q3/2026, ký 19/10/2026, 33 trang (`../dd_NNC_20261026/src/NNC_Baocaotaichinh_Q3_2026.pdf`; số trang ghi theo
> số in trên trang); **[GT]** CV 53/CV-NN26 giải trình LNST 19/10/2026 (tr. 32-33 cùng file); **[KT25]** BCTC 2025 kiểm toán
> AASCs, BC 48/BCKT/TC/2026 ngày 26/02/2026; **[BCTN25]** Báo cáo thường niên 2025; **[FPTS]** FPTS báo cáo lần đầu 07/01/2026
> (BÁN, giá mục tiêu 51.400; lưu `src/fpts_nnc_init_20260107.pdf`) — nguồn thứ cấp; **[BQ]** `tav2_bq.ticker` / `ticker_financial`
> (đã có Q3/2026, release 20/10/2026 — không lệch nguồn); **[Bobby]** `kb/data_registry/market-state/sector_read_da_xay_dung_nam_bo_20261030.md` (đọc mù).
> Tính toán: `calc/valuation.py` → `calc/valuation_out.txt`; `calc/px_stats.py` → `calc/px_stats_out.txt`.
> Số cổ phiếu: vốn điều lệ 219,2 tỷ / 10.000 = **21,92 tr cp** [Q3 V22] (không dùng OShares BQ). Giá tham chiếu **47.100** (đóng cửa 30/10/2026 [BQ]).
> Giả định tự đặt gắn **(ước lượng)**. Đơn vị tỷ đồng nếu không ghi khác.

## 0. Kết luận

**Verdict trung dung (1 dòng): Ở 47.100, NNC được định giá XẤP XỈ HỢP LÝ — rẻ so với lợi nhuận hiện tại (PE 4,8; EV/EBITDA ~2,3)
nhưng giá đã phản ánh khá sát rủi ro "vách" cung–cầu đá cụm Đồng Phú–Phú Giáo từ 2028; giá trị kỳ vọng ~50.300 đ/cp (+7%),
phân bố lệch hai đầu (xấu ~25.000 / tốt ~94.000).**

| Vùng giá (đ/cp) | Đọc |
|---|---|
| ≤ ~42.000 | Rẻ so với kỳ vọng (≥15% dưới 50.300) |
| ~42.000 – 58.000 | Hợp lý — kết quả phụ thuộc gần như hoàn toàn vào giá/sản lượng 2028+ |
| ≥ ~58.000 | Đắt — đòi hỏi tin kịch bản "tốt" (giá ≥ 380k/m³ và sản lượng ≥ 1,2 tr m³ kéo dài sau 2028) |

Giá trị kỳ vọng theo lãi suất chiết khấu: r 11% → 52.900 · **13% → 50.300** · 15% → 48.000 [calc]. Xác suất kịch bản là chủ quan.

**Mốc kiểm chứng khoá trước** (chấm theo CẢ HAI chiều, §9): (1) BCTC Q4/26 (~20/01/2027); (2) BCTC Q1/27 (~20/04/2027);
(3) giấy phép khai thác Tam Lập 1 khu II; (4) kết quả đấu giá các mỏ Đồng Nai + tiến độ VĐ4 tới 06/2027 (chỉ báo #2, #3 của Bobby);
(5) CBTT giao dịch cổ đông lớn của MVC.

**3 điểm yếu lớn nhất của chính báo cáo này:**
1. **Không có số sản lượng m³** (BCTC/BCTN không công bố) ⇒ tách giá × sản lượng chỉ là suy luận; câu hỏi "vượt trần công suất" và
   toàn bộ DCF 2028+ đứng trên giả định giá/sản lượng tự đặt.
2. **Cấu trúc chi phí** (biến đổi 110k/m³ + cố định 70 tỷ/năm) hiệu chỉnh trên đúng MỘT quý (Q3/26) với sản lượng giả định 0,35 tr m³;
   kiểm ngược khớp 2023 (GVHB ~128 tỷ) nhưng sai số ±20% làm kịch bản xấu đổi dấu.
3. **Giá trị MVC/NHC** dùng OShares MVC 100 tr từ BQ (chưa đối chiếu điều lệ MVC), giá NHC phiên cuối 16/09 (rất kém thanh khoản);
   trữ lượng còn lại Mũi Tàu 20,2 tr m³ lấy từ FPTS (thứ cấp).

---

## 1. Giả thuyết user: "NNC giống SCL, ăn theo chu kỳ VLXD đầu tư công" — ĐÚNG MỘT PHẦN, cơ chế khác

| Kiểm bằng số | Kết quả |
|---|---|
| Doanh thu tăng theo hạ tầng? | 9T/26 DT **402,2** vs 261,9 (**+53,6%**); Q3 149,5 vs 100,3 (+49,1%) [Q3 tr.4]. [GT]: do "sản lượng tiêu thụ **và** giá bán tăng" |
| Sản lượng có phải động lực chính? | **Không thể là chính**: 2025 đã "khai thác đạt 100% công suất cấp phép" [BCTN25 tr.20]; GP 1,0 tr m³/năm nguyên khối ≈ 1,42 tr m³ thành phẩm [BCTN25 tr.6]. FPTS 2025F tiêu thụ 1,2 tr m³ ⇒ dư địa sản lượng 2026 tối đa ~+17% (ước lượng) ⇒ phần còn lại (~+30%) là **giá** |
| Biên gộp | 2024 **31,6%** → 2025 **49,4%** [KT25 tr.9] → 9T/26 **54,3%** → Q3/26 **57,9%**; riêng đá thành phẩm Q3 **59,9%** (140,0 DT − 56,1 GV) vs Q3/25 52,2% (91,41 − 43,72) [Q3 VI.1-2] |
| So với SCL | SCL (Sông Đà Cao Cường) bán tro bay, biên gộp ~41%, rủi ro chính là phải thu tập trung VinCons 58,5% (DD SCL 29/10). NNC: **khối lượng bị trần pháp lý, tài sản hữu hạn (GP 2043), ăn chênh lệch GIÁ cục bộ** quanh cụm mỏ |

⇒ NNC **có** ăn theo chu kỳ VLXD hạ tầng phía Nam, nhưng qua kênh **giá đá cục bộ do cung nghẽn hành chính** (Bobby: ADMIN_GATED 0,45),
không qua kênh sản lượng. Hệ quả: chu kỳ của NNC nhạy với **giá đá cụm Đồng Phú–Phú Giáo** (mỏ mới Tam Lập, đấu giá, CV 2757 bình ổn giá),
nhiều hơn với tổng giải ngân đầu tư công.

## 2. Chất lượng lợi nhuận (đọc độc lập từ ảnh trang)

| | Q3/26 | Q3/25 | 9T/26 | 9T/25 | Nguồn |
|---|---|---|---|---|---|
| DT thuần | 149,49 | 100,27 | 402,20 | 261,89 | Q3 tr.4 |
| — đá thành phẩm (mỏ Tân Lập/Mũi Tàu) | 139,97 | 91,41 | n/a | n/a | VI.1, bộ phận tr.29 |
| — hàng hoá (dầu DO…) | 3,35 | 3,89 | | | VI.1 (biên ~0) |
| — dịch vụ (cho thuê mặt bằng Núi Nhỏ…) | 6,17 | 4,97 | | | VI.1 (LN gộp 2,6) |
| GVHB | 62,95 | 49,61 | 183,68 | 133,54 | |
| LN gộp | 86,54 | 50,67 | 218,52 | 128,34 | |
| DT tài chính (lãi tiền gửi) | 6,07 | 7,60 | 15,60 | 13,48 | VI.3 |
| CP BH + QLDN | 5,14 | 4,00 | 12,87 | 14,02 | |
| LN khác | −0,00 | −1,88 | **−19,29** | −4,18 | VI.8 |
| LNST | **69,29** | 42,56 | **160,08** | 93,95 | tr.4 |

- **Một lần (âm):** chi phí khác 9T 22,0 tỷ = truy thu tiền cấp quyền Núi Nhỏ **15,58** + tiền thuê đất bổ sung 2019 Núi Nhỏ **5,95** [V19a, V13];
  ghi tài sản thuế hoãn lại 4,31 trên 2 khoản này. LNST 9T loại one-off ≈ **177** (ước lượng, thuế 20%).
- **Lãi/lỗ liên kết:** BCTC riêng ghi giá gốc — không có phần lãi MVC/NHC trong KQKD; Q3 không có cổ tức M&C [VI.3].
- **Lãi tiền gửi** 15,6 tỷ/9T trên số dư tiền gửi ~300–350 tỷ (≈ 6%/năm, ước lượng) — bền chừng nào tiền còn đó.
- **TTM** (9T/26 + Q4/25 = 147,83 − 93,95 = 53,88): **LNST 214,0 · EPS 9.761**; EBIT lõi TTM 264,3; EBITDA ~300 (KH ước lượng ×4 Q3).
- **Bẫy trình bày nhỏ:** "Trong đó chi phí lãi vay" 9T in **(1,82)** (số âm) trong khi chi phí tài chính 9T +1,83 và LCTT "tiền chi trả lãi vay" 9T = 0
  [Q3 tr.4-5] — lỗi dấu/vốn hoá lãi vay chưa giải thích. Không trọng yếu (≤1% LN).
- **Kế hoạch 2026** DT 360 / LNTT 120 [BCTN25 tr.21] — 9T đã đạt 112% DT, 167% LNTT. Kế hoạch thận trọng; không có giải thích.

**Nghi vấn vượt trần công suất (Bobby #5, #12):** DT đá Q3 140,0 tỷ. Trần 1,42 tr m³ thành phẩm/năm = 0,355 tr m³/quý ⇒ **ASP hoà trần ≈ 394k/m³**.
Giá tham chiếu: Bình Phước cũ 1x2 tại mỏ 230–240k/tấn ≈ 334–360k/m³ (Bobby, quy đổi 1,45–1,5 t/m³); FPTS ASP 2025F 317,9k, 2026F 455,5k.
Cơ cấu có 0x4/hộc rẻ hơn 1x2. ⇒ ASP bình quân thực có thể nằm **dưới** 394k ⇒ sản lượng Q3 có thể **vượt** nhịp trần — **CHƯA XÁC MINH**
(cần số m³; ranh giới: ASP < 394k ⇔ vượt nhịp quý; vượt nhịp một quý chưa chắc vượt trần năm).

## 3. Net cash THẬT [Q3 tr.1-3, V1, V2, V16, V19a, V21]

| Khoản | 30/09/2026 |
|---|---|
| Tiền + tương đương | 25,47 (đầu năm 87,81) |
| Tiền gửi có kỳ hạn (HTM): 6T 278,97 + 12T 43,47 | 322,44 |
| CK kinh doanh | 0,13 |
| − Vay NH 5,00 + DH 69,89 | −74,89 (đầu năm 28,89) |
| **= Net cash thô** | **273,2 (12.461 đ/cp)** |
| − Dự phòng truy thu (CQ Núi Nhỏ 15,58 + đất 5,95 + CQ Mũi Tàu 0,84) | −22,37 |
| − Quỹ khen thưởng phúc lợi | −16,78 |
| − Cổ tức phải trả | −5,89 |
| − Dự phòng phục hồi môi trường dài hạn | −4,50 |
| **= Net cash sau nghĩa vụ ngoài vận hành** | **223,6 (10.202 đ/cp, 22% vốn hoá)** |

- **Tiền bị cầm cố:** 30 tỷ tiền gửi (Vietinbank, bảo lãnh vay dây chuyền nghiền 750 t/h) + **52,13 tỷ** (Public Bank, bảo lãnh vay đền bù Tam Lập 1 khu II) [Q3 tr.26].
  Vẫn là tiền của NNC, đã cấn trừ với vay ⇒ không trừ thêm.
- Thuế TNDN phải nộp 21,93 coi là vốn lưu động (không trừ). Tiền cấp quyền Núi Nhỏ 20,43 (đầu năm) **đã nộp** trong 9T (V16 về 0).

## 4. Dòng tiền & phải thu

- **CFO 9T/26 = 109,3** vs LNST 160,1 (**0,68x**); 9T/25 132,9 vs 94,0 (1,41x) [Q3 tr.5]. Hai năm cộng lại ~0,96x — không phải cờ đỏ.
  9T/26 bị kéo bởi thuế TNDN nộp 45,9 (gồm thuế 2025), "chi khác cho HĐKD" 107,2 (gồm tiền cấp quyền Núi Nhỏ 20,4), phải thu +14,5, tồn kho +6,9.
- **Capex 9T 131,1** (9T/25 53,9): máy nghiền 350 t/h mua của Cty NHC 21,29 + lắp đặt 3,21; Tam Lập 1 khu II 83,51 (đền bù QSDĐ 79,48 + đặt trước tiền CQ 4,03) [V10a];
  TSCĐ mới 22,9 [V10]. **FCF 9T ≈ −21,8**, tài trợ bằng vay DH +47,7 và rút tiền tương đương.
- **Phải thu KH 21,29** (đầu năm 6,79; DSO ≈ 13 ngày, ước lượng). **Không** có dấu hiệu nợ nhà thầu dự án công tồn đọng (Bobby #13: KHÔNG).
  ⚠️ Nhưng **12,92 tỷ = 61% phải thu là của NHC (bên liên quan)**: Q3 NHC mua 12,27 tỷ, chỉ trả 2,0 tỷ [Q3 tr.28]; cùng lúc NNC trả cho "Cty NHC"
  21,29 tỷ tiền máy nghiền (CIP). Dòng tiền hai chiều với bên liên quan nhỏ (NHC LNST quý ≤ 3,5 tỷ [BQ]) — **WARNING quản trị**, chưa phải bằng chứng sai phạm.
- **Cổ tức:** 2026 đã chi 21,92 tỷ = **1.000 đ/cp** cho năm 2025 [V22, LCTT] ⇒ tỷ lệ chi thực ~**15% LNST 2025**; DY 2,1%.
  BCTN25 tr.17 ghi "tỷ lệ LN trả cổ tức 61,37%" — **mâu thuẫn, CHƯA XÁC MINH** (có thể là kế hoạch chưa chi). Phân phối 2025: **264,0 tỷ vào quỹ đầu tư phát triển** [V22] ⇒ tiền giữ lại, không về cổ đông.

## 5. Giấy phép & tài sản

| Mỏ / tài sản | Số liệu | Nguồn |
|---|---|---|
| **Mũi Tàu** (Tân Lập, Đồng Phú; 51,5 ha) | GP 01/2019: trữ lượng 22,509 tr m³, **1,0 tr m³/năm nguyên khối**, hạn **2043**; chế biến 1,421 tr m³ thành phẩm. Còn **20,2 tr m³** nguyên khối, 17 năm (FPTS 01/2026, dẫn Sở TN&MT) ⇒ ràng buộc là **thời hạn GP**, không phải trữ lượng | BCTN25 tr.3,6; FPTS |
| **Núi Nhỏ** (Dĩ An, 27,34 ha) | Hết GP 31/12/2019; đề án đóng cửa QĐ 19/QĐ-UBND 06/01/2021; nay cho thuê kho bãi (DT dịch vụ 6,2 tỷ/quý). **Còn truy thu**: CQ 15,58 + thuê đất 2019 5,95 (dự phòng 2026). QĐ 1581 (5,1 tr m³) là **truy thu tiền cấp quyền trữ lượng đã khai thác**, không phải cấp thêm (FPTS dẫn đính chính DN). Thái Bình (15,93%) phối hợp xin quy hoạch đất sau đóng mỏ | BCTN25, Q3 V19a, FPTS |
| **Tam Lập 1 khu II** | CIP 83,5 (QSDĐ 79,48 + đặt trước tiền CQ 4,03); vay Public Bank. Trữ lượng, công suất, ngày GP: **chưa có CBTT** (bản 26/10 dẫn AWM: >11 tr m³, 1 tr m³/năm, 2028 — thứ cấp) | Q3 V10a, tr.26 |
| **MVC** (CTCP VL&XD Bình Dương) | NNC nắm **10,3 tr cp** (giá gốc 103,0) [V11] ≈ 10,3% (OShares BQ 100 tr, chưa đối chiếu). Giá 14.100 ⇒ **145,2 tỷ**. MVC nắm **9,659 tr cp NNC = 44,07%** (đầu năm 43,55% — **tăng 113.900 cp trong 2026**) [V22] | Q3, BQ |
| **NHC** (Gạch ngói Nhị Hiệp) | 710.242 cp, giá gốc 21,67, dự phòng 5,35 [V11] ≈ 23,35% (liên kết). 18.600 (phiên 16/09) ⇒ 13,2 tỷ | Q3, BQ |
| Ký quỹ phục hồi môi trường Tân Lập | 4,57 (tài sản) / dự phòng 4,50 (nợ) | V9, V21 |

## 6. Cổ đông, thanh khoản, kiểm toán

- MVC 44,07% · CTCP Đầu tư Thái Bình 15,93% · bà Nguyễn Thị Mai Phương 7,01% ⇒ **free float ~33%**. Nước ngoài 3,19% (11/03/2026) [BCTN25 tr.18-19]; room: CHƯA XÁC MINH (có CV UBCKNN về hồ sơ tỷ lệ sở hữu nước ngoài tối đa, ngày không rõ — tìm kiếm web).
- **ADV 20/60/120 phiên: 1,49 / 1,36 / 1,48 tỷ/phiên** (~33k cp) [BQ, calc/px_stats_out.txt] — rất mỏng.
- Ban điều hành: GĐ Phạm Thanh Liêm (từ 07/2022) **sở hữu 0 cp** [BCTN25 tr.14]. HĐQT 5 người (CT Đoàn Minh Quang), 1 độc lập [KT25 tr.1].
- **Kiểm toán 2025: AASCs, ý kiến CHẤP NHẬN TOÀN PHẦN** (không ngoại trừ, không nhấn mạnh) [KT25 tr.4-5]. BCTC Q3 không soát xét (quý).

## 7. Định giá

**Bội số** (vốn hoá 1.032,4 tỷ; EV hoạt động = vốn hoá − net cash sau nghĩa vụ 223,6 − MVC ex-vòng-tròn 98,4 − NHC 13,2 = **697,2**):

| Thước đo | Giá trị | Ghi chú |
|---|---|---|
| PE TTM | **4,83x** | LN đỉnh |
| PE ex-cash trên EBIT lõi TTM × 0,8 | 3,30x | |
| EV/EBITDA TTM | ~2,3x | KH ước lượng |
| PE ex-cash trên LN 2025 (147,8) | 4,7x | |
| PE ex-cash trên LN TB 2021→TTM (89,8) | 7,8x | gồm đáy 2021-23 khi Mũi Tàu chưa hết công suất |
| PE ex-cash trên LN trung vị 2021-25 (39,3) | 17,7x | đáy mỏ-đơn; quá khắt khe vì giá đá khi đó thấp hơn ~40% |
| PB | **1,57** (BVPS 29.915) | |

**MVC ex-vòng-tròn:** 9,66 tr cp NNC × 47.100 = 455 tỷ = 32% vốn hoá MVC ⇒ phần MVC "không phải chính NNC" = 145,2 × 68% = **98,4 tỷ (4.490 đ/cp)**.
Cộng thẳng 145,2 sẽ đếm NNC hai lần.

**DCF HỮU HẠN 2027–2043** (17 năm tới hạn GP Mũi Tàu; không terminal; capex duy trì ≈ khấu hao; thuế 20%; chi phí +3%/năm; tất cả là **ước lượng**).
Lãi suất 13% (dải 11–15%) — khớp kỳ hạn ~17 năm và rủi ro vốn cổ phần một-mỏ (Ke nội địa β1,1 dải 12,3–13,4% theo khung 30/10; cộng nhẹ vì tập trung một tài sản).
Cộng: LN Q4/26 60 (ước lượng) + net cash sau nghĩa vụ + MVC ex-vòng-tròn + NHC + CIP Tam Lập theo giá gốc (chỉ ở tốt/cơ sở).

| Kịch bản (xác suất chủ quan) | Sản lượng tr m³ (2027 / 2028-30 / 2031+) | Giá k/m³ (2027 / 2028-30 / 2031+) | NOPAT 2027 / 2028 | Giá trị/cp r=13% |
|---|---|---|---|---|
| Tốt (20%) — đỉnh kéo dài (VĐ4 + ĐBSCL) | 1,4 / 1,4 / 1,4 | 420 / 400 / 420 | 269 / 241 | **94.200** |
| Cơ sở (45%) — Bobby: trũng 2027-28 rồi bình nguyên | 1,4 / 1,1 / 1,2 | 380 / 300 / 320 | 225 / 85 | **52.000** |
| Xấu (25%) — FPTS: 0,8 tr m³ từ 2028, cung Tam Lập ép giá | 1,3 / 0,8 / 0,8 | 330 / 250 / 250 | 151 / 9 | **24.900** |
| Rất xấu (10%) — giá về mặt bằng 2023-24 từ 2027 | 0,8 / 0,8 / 0,8 | 230 / 210 / 210 | ~0 / 0 | **18.100** (≈ tiền + đầu tư) |
| **Kỳ vọng** | | | | **50.300 (+7%)** |

**Độ nhạy giá × sản lượng (áp từ 2028, r=13%, đ/cp)** [calc]:

| Sản lượng \ Giá k/m³ | 220 | 260 | 300 | 340 | 380 | 420 |
|---|---|---|---|---|---|---|
| 0,8 | 31.300 | 32.400 | 36.800 | 42.800 | 49.700 | 56.800 |
| 1,0 | 31.500 | 35.900 | 43.100 | 51.600 | 60.500 | 69.400 |
| 1,2 | 33.200 | 40.400 | 50.000 | 60.700 | 71.300 | 82.000 |
| 1,4 | 35.600 | 45.300 | 57.300 | 69.700 | 82.100 | 94.600 |

⇒ Giá 47.100 hàm ý **khoảng 1,0 tr m³ × ~320k/m³** hoặc **1,2 tr m³ × ~290k/m³** bền vững từ 2028 — tức giá đá giảm ~15–25% so với mức suy ra 2026.
(Bảng gồm cả năm 2027 ở 1,4 × 380 nên sàn ~31k cao hơn kịch bản rất xấu.)

**Không tính vào kỳ vọng** (cả hai chiều): (+) Tam Lập 1 khu II nếu được cấp GP ~1 tr m³/năm từ 2028–29: **0 đến +10.000 đ/cp (ước lượng thô)** — có thể ăn
mòn chính Mũi Tàu vì cùng cụm; (+) đất Núi Nhỏ 27 ha ở Dĩ An sau cải tạo (chưa có quy hoạch); (−) phạt/truy thu nếu sản lượng vượt trần;
(−) MVC lên ≥51% buộc NNC thoái cổ phần MVC ở giá xấu; (−) chi phí đóng cửa mỏ 2043 vượt dự phòng.

**So với thị trường:** FPTS 07/01/2026 (giá 65.200): BÁN, mục tiêu 51.400 (FCFF, WACC 12,6%, g 2%) — gần với kỳ vọng ở đây, dù FPTS dùng terminal vô hạn.

**Phản ứng giá quanh BCTC** [BQ, calc/px_stats_out.txt; giá điều chỉnh]: đỉnh 74.660 (29/12/2025) → đáy 36.950 (14/09/2026) trong khi LNST TTM tăng từ 114,6 (TTM tại 12/2025) lên 214,0 (+87%).
4 lần công bố gần nhất đều có LNST tăng mạnh YoY nhưng T+5 lần lượt −9,6% / −8,3% / −8,0% / +1,7% (Q3/26, ngày 20/10). Thị trường **không trả tiền cho LN đỉnh** —
đang định giá theo vách 2028; chỉ lần Q3/26 hết bị bán.

## 8. Checklist "DD cần kiểm gì" của Bobby (21 mục)

| # | Mục | Trả lời | Nguồn |
|---|---|---|---|
| 1 | Danh sách GP, hạn, công suất, cote đáy | **CÓ một phần**: Mũi Tàu 1,0 tr m³/năm nguyên khối, hạn 2043; Núi Nhỏ hết 2019. Số GP, cote đáy: CHƯA XÁC MINH | BCTN25 |
| 2 | Trữ lượng còn lại / số năm | **CÓ (thứ cấp)**: 20,2 tr m³ ≈ 20 năm > 17 năm GP ⇒ ràng buộc là thời hạn. Cấp 121/122: CHƯA | FPTS |
| 3 | Thuê đất đủ diện tích | **CHƯA XÁC MINH**. Có chi phí trả trước DH CNBP 59,2 tỷ (phân bổ 3,2 tỷ/quý); có truy thu thuê đất 2019 Núi Nhỏ 5,95 | Q3 V12, V19a |
| 4 | Mở rộng qua đấu giá | **CÓ**: Tam Lập 1 khu II có "đặt trước tiền CQKTKS" 4,03 — dấu hiệu đấu giá theo Luật 2024; tiến độ/GP: CHƯA | Q3 V10a |
| 5 | Lịch sử xử phạt | **KHÔNG thấy** phạt trong BCTC/BCTN; có **truy thu** (CQ 15,58 + đất 5,95 + 20,43 đã nộp). Tìm kiếm web không ra quyết định xử phạt — vắng mặt ≠ không có | Q3, web |
| 6 | Đô thị bao vây | **CÓ (đã trả giá)**: Núi Nhỏ ở Dĩ An đã đóng. Mũi Tàu ở vùng nông thôn Đồng Phú: rủi ro thấp (ước lượng) | BCTN25 |
| 7 | Khoảng cách, bến thủy | **CHƯA XÁC MINH**. Thị trường: TP.HCM, Đồng Nai, ít Tây Ninh | BCTN25 tr.13 |
| 8 | Ai trả cước | **CHƯA XÁC MINH**. NNC mua DO của MVC 7,8 tỷ/quý (≈12% GVHB Q3) và "nợ tiền thuê xe vận chuyển" ⇒ NNC chịu diesel một phần | Q3 tr.28, BCTN25 tr.18 |
| 9 | Cơ cấu sản phẩm | **CÓ (định tính)**: 1x2, 4x6, hộc, 0x4 (3 cỡ); kế hoạch thêm đá 1x1, cát nghiền. Tỷ trọng: CHƯA | BCTN25 tr.7-8, 21 |
| 10 | Tỷ trọng dự án trọng điểm / top 5 | **CHƯA XÁC MINH**. Có 2 nhà phân phối (1 là MVC) | Q3 tr.26 |
| 11 | Bị phân bổ/khống chế giá | **CHƯA XÁC MINH** | — |
| 12 | ASP thực vs giá Sở | **CHƯA** (không có m³). Hoà trần ở 394k/m³; giá Sở Bình Phước cũ ~334–360k/m³ | §2 |
| 13 | Phải thu nhà thầu dự án công | **KHÔNG** (DSO ~13 ngày). Cờ khác: 61% phải thu là NHC (liên quan) | Q3 V3, tr.28 |
| 14 | Sản lượng dồn sớm, đo khoảng trũng | **KHÔNG thấy trũng tới Q3/26**: DT Q1 120,3 → Q2 132,4 → Q3 149,5. H2 chưa đủ (Q4 chưa có) | BQ, Q3 |
| 15 | Tiền cấp quyền đã/còn nộp, truy thu | **CÓ truy thu**: Núi Nhỏ 20,43 (nộp 2026) + 15,58 (dự phòng) ; Mũi Tàu dự phòng 0,84 | Q3 V16, V19a |
| 16 | Thuế tài nguyên theo giá thật hay sàn | **CHƯA XÁC MINH** (phải nộp 0,97 tỷ) | Q3 V16 |
| 17 | Ký quỹ phục hồi môi trường | **CÓ**: 4,57 ký quỹ / 4,50 dự phòng; đủ hay không: CHƯA | Q3 V9, V21 |
| 18 | Độ nhạy diesel, hedging | **CÓ phơi nhiễm, KHÔNG thấy hedging/pass-through** | Q3 tr.28 |
| 19 | Mẹ / chuyển giá qua bên liên quan | **CÓ giao dịch liên quan đáng kể**: mua DO từ MVC; bán NHC 12,27 tỷ/quý (8,2% DT) + mua máy nghiền "Cty NHC" 21,29. Chuyển giá: CHƯA có bằng chứng | Q3 tr.28, V10a |
| 20 | Đấu giá mỏ mới: R trúng, nguồn tiền | **CÓ một phần**: Tam Lập 1 khu II, tiền từ vay Public Bank (bảo lãnh bằng 52,13 tỷ tiền gửi). R trúng: CHƯA | Q3 tr.26 |
| 21 | Tài sản ngoài mỏ | **CÓ**: đất Núi Nhỏ cho thuê kho bãi + hợp tác Thái Bình xin quy hoạch; cổ phần MVC/NHC. Giá trị đất: CHƯA | BCTN25, FPTS |

## 9. Pháp lý / quản trị — chỉ WARNING (luật 27/09)

Không phải tra cứu pháp lý chính thức; cần legal-vn nếu đi tiếp.
1. **Sở hữu chéo NNC↔MVC.** MVC 44,07% (đang tăng). Nếu MVC ≥ 51% ⇒ NNC thành công ty con; LDN 2020 Đ.195 (hiểu biết của tôi, chưa xác nhận) cấm con sở hữu chéo mẹ ⇒ có thể phải thoái 10,3 tr cp MVC.
2. **Giao dịch bên liên quan NHC**: phải thu 12,9 tỷ (61% tổng), cùng lúc mua thiết bị 21,3 tỷ từ NHC.
3. **Vượt trần công suất**: chưa loại trừ (§2). Luật 147/2025 + CV 2757: Bobby đặt trần sức định giá ở phân khúc dự án.
4. **Tiền giữ lại không về cổ đông**: 264 tỷ vào quỹ ĐTPT, chi cổ tức ~15% LN 2025; ban điều hành không sở hữu cổ phần. Rủi ro di cư vốn sang BĐS
   (ĐKKD có "kinh doanh BĐS"; BCTN25: "nghiên cứu mở rộng sang BĐS nhà ở") — Bobby #21.

**CBTT mới từ 26/10/2026:** không tìm thấy (vietstock trang mã 30/10; tìm kiếm web). Chưa có BCTC hợp nhất (NNC lập BCTC riêng), không có nghị quyết,
giải trình mới, giao dịch MVC hay kết quả đấu giá Tam Lập được công bố. Website nuinho.vn: chưa truy cập được — **lệch nguồn: kiểm tay**.

## 10. Điều kiện làm nhận định đổi — CẢ HAI chiều (khoá 30/10/2026)

**→ Nghiêng tích cực (kỳ vọng lên ≥ ~58.000):**
- BCTC Q4/26 + Q1/27: DT ≥ 130 tỷ/quý **và** biên gộp ≥ 55% (giá chưa quay đầu dù VĐ3/Long Thành rút); **hoặc**
- GP Tam Lập 1 khu II được cấp với công suất ≥ 0,7 tr m³/năm và khai thác ≤ 2028; **hoặc**
- NNC công bố sản lượng m³ cho thấy ASP ≥ 400k (loại trừ nghi vấn vượt trần).

**→ Nghiêng tiêu cực (kỳ vọng xuống ≤ ~42.000):**
- Biên gộp quý < 45% với DT đi ngang (giá đá cụm quay đầu), hoặc giá Sở XD Đồng Nai Q2/2027 thấp hơn Q3/2026 > 7% (Bobby chỉ báo #1);
- Quyết định xử phạt/đình chỉ vì vượt công suất, hoặc truy thu mới > 20 tỷ;
- MVC ≥ 51% kèm phương án thoái cổ phần MVC dưới giá; hoặc thêm giao dịch tiền lớn với NHC/bên liên quan;
- VĐ4 < 20% khối lượng tới 06/2027 (Bobby chỉ báo #3).

Không có mốc nào ở trên đã xảy ra tính tới 30/10/2026.

## 11. So với bản 26/10 (`dd_NNC_20261026/REPORT.md`)

Đọc bản cũ **sau** khi đã đọc xong ảnh trang và chạy `calc/`.

| Hạng mục | 26/10 | 30/10 | Vì sao |
|---|---|---|---|
| Số BCTC Q3 (DT, LNST, GVHB, vay, CIP, CFO) | — | **Khớp** (LNST Q3 69,29 / 9T 160,08; vay 74,89; CIP 108,0; CFO 109,3) | Đọc lại độc lập, không lệch |
| Net cash | 273,0 | **273,2 thô / 223,6 sau nghĩa vụ** | Thêm CK kinh doanh 0,13; **trừ** dự phòng truy thu 22,4, quỹ khen thưởng 16,8, cổ tức phải trả 5,9, DP môi trường 4,5 |
| MVC | 147,3 (14.300, cộng thẳng) | **98,4** (14.100, bỏ phần vòng tròn 32%) | Bản cũ đếm NNC hai lần qua MVC |
| Tỷ lệ MVC tại NNC | 43,55% | **44,07%** (+113.900 cp trong 2026) | Bản cũ dùng cột "năm trước" của V22 |
| Phải thu | không phân tích tập trung | **61% là NHC (bên liên quan)** | Mới đọc trang 28 |
| Cổ tức 2025 | "61,37% LN" (BCTN) | **~15% thực chi** (1.000 đ/cp); 61,37% = mâu thuẫn chưa giải | Đối chiếu V22 + LCTT |
| Trữ lượng còn Mũi Tàu | ~16–17 tr m³ (ước lượng) | **20,2 tr m³** (FPTS dẫn Sở) | Nguồn thứ cấp tốt hơn ước lượng |
| Vượt trần công suất | nghi vấn định tính | **ngưỡng định lượng: ASP < 394k ⇒ vượt nhịp quý** | |
| Giá trị kỳ vọng | **62.800 (+32%)**, r=14% | **50.300 (+7%)**, r=13% | Kịch bản xấu nay có **vách sản lượng** (0,8 tr m³ từ 2028, theo FPTS + Bobby trũng 2027) và **đòn bẩy chi phí cố định**; bản cũ giữ sàn "deep" NP 83 tỷ/năm suốt 17 năm (≈ 44.000) — quá lạc quan cho đáy. Thêm trừ nghĩa vụ + vòng tròn MVC (~−4.500 đ/cp) |
| Kết luận | NON (khung fear-buy) + "rẻ về giá trị thuần" | **Hợp lý, không rẻ rõ rệt** | Khung khác (trung dung, không §2.5); và định giá cũ bỏ sót rủi ro vách sản lượng |

**Kết luận đổi:** từ "rẻ ~+32%" sang "xấp xỉ hợp lý, +7% kỳ vọng với phân bố lệch hai đầu". Phần lớn chênh lệch do giả định kịch bản xấu, không do số liệu BCTC.

---

## §13 ĐÍNH CHÍNH 31/10/2026 (áp bản phản biện `SKEPTIC_20261031.md`, REFUTED medium) — **mục này THẮNG §0, §7, §8 #5, §9.3, §10, §11**

Job `Taylor_20261031_014511`. Tính toán: `calc/valuation_v2.py` → `calc/valuation_v2_out.txt` (md5 out `3cff411d…`), CSV `calc/valuation_v2_scenarios.csv`,
`calc/valuation_v2_3scen.csv`. `valuation.py` (30/10) giữ nguyên làm chân control: tái lập 50.267; đổi TỪNG giả định ra đúng số phản biện
(trọng số 55.433 · +3% từ 2031 57.644 · +3% từ 2028 64.379 · chi phí ±10% 55.142/45.804 · thuê +2.657).

### 13.1 Kiểm lại từng đính chính tại nguồn (ảnh trang, pymupdf 100 dpi)

| # | Đính chính | Kiểm tại nguồn | Kết quả |
|---|---|---|---|
| E1 | Có phạt hành chính | KT25 TM 7.8 (in tr.40, pdf p.43): "Tiền phạt vi phạm hành chính" **39,37 tr (2025) / 630,43 tr (2024)**; dự phòng tiền CQKTKS 1,735 tỷ (2025); chi phí cải tạo mỏ 0,445 tỷ (2024); tiền đền bù đất 1,0 tỷ (2025) | **Phản biện ĐÚNG.** §8 #5 cũ ("KHÔNG thấy phạt") SAI. Nội dung vi phạm: CHƯA XÁC MINH |
| E2 | Gán sai nguồn người đọc ngành | Sector read §5 bảng cầu: 2027 trũng 7–11 tr m³, 2028 8–12; §6 "đỉnh kéo dài tới 2028" là kịch bản chống; F2: P(giá Q2/27 < Q3/26 −7%) = **0,15** | **ĐÚNG.** Đường "2027 cao rồi vách 2028" là của FPTS/nhóm nghiên cứu, không phải người đọc ngành |
| E3 | FPTS không phải xác nhận độc lập | FPTS tr.1: base case 0,8 tr m³ từ 2028; tr.17: giá 479,7k (2027F) → **237,6k (2028F) → 209,8k (2029F)**, biên gộp 30,6% (2029F) | **ĐÚNG.** Cùng đường giá/sản lượng FPTS ra 51.400, mô hình này ra ~24.900 ⇒ lệch ~2 lần; câu "FPTS gần kỳ vọng" bị XOÁ |
| E4 | Giá danh nghĩa phẳng = giá thực −3%/năm, không công bố | `valuation.py` dòng `path()`: giá hằng, chi phí ×1,03^t, r danh nghĩa 13% | **ĐÚNG.** Đây là giả định số 1 (13.3). Lưu ý: "+3%/năm lịch sử" so 140–150k/tấn (≤2020, mỏ chung) với 177k (Đồng Nai cũ) – 240k (Bình Phước cũ) đầu 2026 ⇒ +3% đến +8%/năm tuỳ vùng, mốc ≤2020 không rõ năm |
| E5 | Bỏ sót LN gộp cho thuê | KT25 7.1/7.2: DT dịch vụ 18,92; GV dịch vụ 7,79 ⇒ **11,13 tỷ (2025)** | **ĐÚNG.** Cộng vào, tăng 3%/năm, dừng 2043 (thận trọng: đất Núi Nhỏ chưa có quy hoạch sau đóng mỏ) |
| E6 | Hiệu chỉnh chi phí | KT25 7.2: GV thành phẩm **178,29 (2024) / 178,59 (2025)**; DT thành phẩm 257,44 / 360,39 | **ĐÚNG.** Mô hình cũ ở 1,2 tr m³ (2025) cao hơn kiểm toán 10%; ở 1,05 tr m³ (2024) thấp 2%. Hệ số tâm 0,97 (TB 2 năm), dải ±10% (0,87–1,07) chứa hiệu chỉnh Q3/26 (1,00, đỉnh diesel). Sản lượng 2024/25 lấy từ FPTS (thứ cấp) |
| E7 | Đối thủ hết GP sớm | FPTS tr.9: thời hạn còn lại Mũi Tàu 17 năm, Tam Lập 3 **9**, Tam Lập 2 **7** | **ĐÚNG.** Đưa vào độ nhạy (xấu hồi 1,2 × 320 từ 2035), không vào tâm |
| E8 | Phía lạc quan | MVC ADV mỏng (BQ Volume_1M 41.280 cp × 14.100 ≈ 0,58 tỷ/phiên ngày 30/10; phản biện đo 0,39 tỷ/3T); giá "tốt" 420/400 không có ASP | **ĐÚNG.** MVC trình bày CẢ hai mức (0% / 30%), tâm 15%; giá "tốt" thấp hơn = độ nhạy |
| E9 | NHC trong tăng trưởng Q3 | Q3 tr.28 (pdf p.29): bán NHC **12,27 (Q3/26) vs 4,39 (Q3/25)**, đã thu 2,0; phải thu 12,92. KT25 7.1: NHC 18,41 (2025) / 12,45 (2024) | **ĐÚNG.** +7,88 = 16% phần tăng DT Q3 YoY (49,22) |
| E10 | Bỏ comp | BQ `ticker` Close 30/10 × `ticker_financial.OShares` / Σ NP_P0 Q4/25–Q3/26 | Đưa lại (13.4) |
| E11 | LN giữ lại / cổ tức | Q3 tr.3 (pdf p.4): LNST chưa phân phối kỳ này **80,04** vs LNST 9T 160,08; quỹ ĐTPT 87,27 → **353,26** | **ĐÚNG.** ~80 tỷ LN 2026 đã rời dòng 420b trong 9T — chưa có nghị quyết công bố giải thích; 61,37% (BCTN25) vẫn CHƯA XÁC MINH |
| E12 | Truy thu chạm mỏ lõi | Q3 V19a dự phòng CQ Mũi Tàu 0,84; KT25 7.8 dự phòng CQKTKS 1,735 (2025) | **ĐÚNG** — theo dõi |

Không tìm thấy chỗ phản biện sai. Một chỗ cần nói rõ hơn: E4 "+3%/năm" là cận dưới; so riêng Bình Phước cũ (vùng Mũi Tàu) thì cao hơn (≤8%/năm) nhưng mốc ≤2020 không rõ năm, khác vùng — không dùng làm tâm.

### 13.2 Bảng số cũ → mới (r = 13%)

| Hạng mục | §0/§7 cũ (30/10) | §13 mới (31/10) | Lý do |
|---|---|---|---|
| Trọng số tốt/cơ sở/xấu/rất xấu | 20/45/25/10 | **25/50/20/5** | F2 người đọc ngành P(giá Q2/27 giảm >7%) = 0,15; xấu+rất xấu giữ 25% (> 0,15) vì thêm rủi ro vách 2028 |
| LN gộp cho thuê Núi Nhỏ | không tính | **+11,13 tỷ/năm** (2025, +3%/năm tới 2043) | E5 |
| Chi phí | 110k/m³ + 70 tỷ, hiệu chỉnh 1 quý | **×0,97** (GV kiểm toán 2024–25), dải 0,87–1,07 | E6 |
| Giá danh nghĩa | phẳng (ẩn) | **4 biến thể công bố**; tâm = giữa "phẳng" và "giữ giá trị thực" | E4 |
| MVC | 98,4 tỷ (không chiết khấu) | 98,4 / 68,9 (0% / 30%), tâm 15% | E8a |
| Tốt / cơ sở / xấu / rất xấu (giá phẳng) | 94.200 / 52.000 / 24.900 / 18.100 | **99.800 / 57.300 / 27.200 / 18.600** | thuê + chi phí |
| Kỳ vọng — giá phẳng | **50.300 (+7%)** | **59.300 (+26%)** (MVC −15%) | |
| Kỳ vọng — +3%/năm từ 2031 | — | 69.100 (+47%) | |
| Kỳ vọng — +3%/năm từ 2028 | — | 76.600 (+63%) | |
| Kỳ vọng — giữ giá trị thực | — | **79.500 (+69%)** (MVC −15%) | |
| Điểm giữa phẳng…thực | — | **~69.400 (+47%)** | luật 12: cả hai chiều vào dải |
| Lưới 72 tổ hợp (4 giá × 3 chi phí × 2 MVC × 3 r) | — | min 50.700 · P10 57.600 · trung vị 70.300 · P90 84.800 · max 94.400 | |
| Chi phí ±10% (phẳng / thực) | — | 54.600–65.600 / 74.200–86.300 | |
| r 11/13/15% (phẳng) | 52.900 / 50.300 / 48.000 | 63.600 / 60.000 / 56.900 | |
| 3 kịch bản cho NĐT (25/50/25; tiêu cực = xấu:rất xấu 20:5) | — | phẳng 99.100 / 56.700 / 24.800 · thực 131.100 / 77.400 / 32.100 | |
| Định giá ngược @47.100 | "≈1,0 tr m³ × 320k" | thị trường hàm ý **P(tiêu cực) ≈ 52% (giá phẳng) – 76% (giá thực)** vs 25% ở đây | |
| FPTS 51.400 | "gần kỳ vọng" | **xoá câu**; cùng đường giá/sản lượng lệch ~2 lần với mô hình này | E3 |
| §8 #5 xử phạt | "KHÔNG thấy" | **CÓ phạt hành chính nhỏ** 0,63 tỷ (2024), 0,04 tỷ (2025); nội dung CHƯA XÁC MINH | E1 |

### 13.3 Kết luận đã đính chính (thay §0)

**Ở 47.100 (đóng cửa 30/10/2026), NNC nằm DƯỚI vùng giá trị hợp lý — nghiêng rẻ, nhưng không phải rẻ "chắc chắn".**
Vùng giá trị hợp lý ~**59.000–79.000 đ/cp** (r 13%; cận dưới = giá đá danh nghĩa đi ngang tới 2043, tức giá thực −3%/năm; cận trên =
giá giữ giá trị thực), điểm giữa ~69.000. Thị trường đang định giá xác suất kịch bản "vách cung–cầu 2028" ~52–76%, cao hơn 2–3 lần mức 25%
mà bằng chứng hiện có ủng hộ. Phân bố vẫn lệch hai đầu: tiêu cực ~25.000–32.000, tích cực ~99.000–131.000.
Kết luận không đổi ở 45.000–52.000 (P(tiêu cực) hàm ý 41–80%).

| Vùng giá (đ/cp) | Đọc (thay bảng §0) |
|---|---|
| ≤ ~57.000 | Dưới vùng hợp lý ở mọi đường giá, trừ khi tin xác suất vách 2028 > ~40% (giá phẳng) |
| ~57.000 – 80.000 | Trong vùng hợp lý — vị trí trong vùng phụ thuộc gần như hoàn toàn vào giả định giá danh nghĩa/thực |
| ≥ ~80.000 | Trên vùng — cần cả giá giữ giá trị thực LẪN kịch bản tốt kéo dài |

**Điều làm nhận định tiêu cực hơn** (giữ §10, bỏ ngưỡng cũ 42k/58k): giá công bố Q2/27 thấp hơn Q3/26 >7%; biên gộp quý < 45% với DT đi ngang;
GP mỏ mới trong cụm (F6) cấp sớm; quyết định xử phạt/truy thu > 20 tỷ; thêm dòng tiền lớn với NHC; MVC ≥51% kèm thoái MVC dưới giá.
**Điều làm tích cực hơn:** giá Q2/27 cao hơn >7% (F2 0,30); VĐ4 ≥20% khối lượng tới 06/2027; GP Tam Lập 1 khu II; công bố sản lượng m³ cho ASP ≥ 394k.

### 13.4 So sánh ngang ngành (BQ 30/10/2026, LNST 4 quý Q4/25–Q3/26)

| Mã | Vốn hoá (tỷ) | LNST TTM | PE TTM | Ghi chú |
|---|---|---|---|---|
| **NNC** | 1.032 | 214,0 | **4,83x** | LN đỉnh; 22% vốn hoá là tiền ròng sau nghĩa vụ |
| DHA (Hoá An) | 824 | 151,7 | 5,43x | Q3/26 79,6 tỷ — đột biến chưa phân tích |
| KSB | 1.459 | 204,6 | 7,13x | Q2/26 96,8 tỷ cao bất thường |
| VLB | 2.434 | 666,7 | 3,65x | gồm Q2/26 374,4 tỷ (nhiều khả năng một lần); thay bằng TB 3 quý còn lại ⇒ ~6,3x (ước lượng) |

Nhóm đá niêm yết giao dịch PE ~4–7x LN hiện tại — cả ngành đang được định giá như LN đỉnh. NNC rẻ nhẹ so với nhóm, không lệch ngoại lai.

### 13.5 Mục §8/§9 cập nhật
- §8 #5: **CÓ** phạt vi phạm hành chính 630,43 tr (2024) + 39,37 tr (2025) [KT25 7.8]; chi phí cải tạo mỏ 0,445 tỷ (2024); nội dung vi phạm CHƯA XÁC MINH.
- §9 thêm: (5) **NHC chiếm 16% phần tăng DT Q3** (7,88/49,22), chỉ thu 2,0/12,27 — tăng trưởng Q3 có phần dựa vào bên liên quan nhỏ (NHC DT 28,97–30,39 tỷ/quý Q4/25–Q2/26, LNST Q2/26 −0,27 tỷ — đo lại BQ ticker_financial 31/10).
  (6) Truy thu đã chạm mỏ lõi Mũi Tàu (dự phòng 0,84 Q3/26 sau 1,735 năm 2025).
- §4 cổ tức: LNST chưa phân phối "kỳ này" 80,04 trên LNST 9T 160,08; quỹ ĐTPT 87,27 → 353,26 — LN giữ lại được chuyển quỹ, chưa thấy nghị quyết giải thích.
- §0 điểm yếu #2 thay bằng: chi phí hiệu chỉnh trên GV kiểm toán 2024–25 (sản lượng FPTS, thứ cấp) — sai số ±10% ⇒ ±5–6k/cp.
