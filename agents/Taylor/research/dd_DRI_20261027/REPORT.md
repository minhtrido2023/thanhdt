# DD DRI (CTCP Đầu tư Cao su Đắk Lắk) — sleeve discretionary (job `Taylor_20261027_040314`, 2026-10-27)

> READ-ONLY. Không phải lệnh, user quyết. Giá tham chiếu **14.700 đ (đóng cửa 26/10/2026, BQ `ticker`)** ⇒ vốn hoá
> **1.076,0 tỷ** (73,2 tr CP [BCTN]). **BCTC Q3/2026 CHƯA công bố** (dự kiến 30/10; BQ `ticker_financial` mới nhất =
> 2026Q2, kiểm 27/10). Mọi số tài chính dừng ở **30/06/2026**.
> Nhãn: **[BQ]** · **[BCTC]** BCTC hợp nhất Q2/2026 gốc (dri.com.vn, duyệt 27/07/2026, bản scan, đọc ảnh trang) ·
> **[GT]** công văn giải trình LN Q2/2026 · **[BCTN]** BCTN 2025 · **[FEED]** `data/rubber_monthly.csv` ·
> **[BOBBY]** `kb/data_registry/market-state/vn_sector_read_rubber_20261027.md` · **[UL]** ước lượng của tôi
> (công thức trong `model.py` cùng thư mục — chạy lại: `python3 model.py`).

## KHỐI CHU KỲ — tham chiếu, KHÔNG chép lại, KHÔNG sửa
Đã khoá: `agents/Taylor/research/dd_blind2_DRI_20261026/CYCLE_BLOCK.md`, md5 `15bd430e6e84a75c3547d98dc7b9e075`,
12:47 ICT 26/10, `blind: yes`. Tóm tắt: **pha ĐỈNH** (biên LNST TTM 26,0% = cao nhất 2017–2026, p=100; RSS3 phân vị
10 năm 98,3); LN chuẩn hoá cách (2) ≈ 94 tỷ; PE chuẩn hoá ex-cash 10,8x; PB 1,41x vs PB đáy giá cùng loại 0,33–1,16x;
F: biên LNST mẹ Q3/26 ≥ 27% (p 0,70), LNST mẹ Q3 ≥ 50 tỷ (p 0,70). Đối chiếu ở mục H.

---

## 0. Kết luận (viết sau bước 2)

**Verdict sleeve: NON** (không phải fear-state: giá ở vùng đỉnh chu kỳ, biên đỉnh, không có cú sốc sợ hãi).
**Hành động đề xuất cho 3.800 cp còn lại: GIỮ qua BCTC Q3 (30/10), nghiêng GIẢM.**

| Tiêu chí | Phán quyết | Bằng chứng | Dùng khối chu kỳ? |
|---|---|---|---|
| Có cú sốc sợ hãi / định giá rẻ (§2 a) | KHÔNG | PB 1,41x vs PB đáy giá 0,33–1,16x; giá `Price` +14% so 03/08 (12.900) [BQ] | C, E |
| LN lõi bền? | MỘT PHẦN | 221 tỷ TTM là LN đỉnh giá; chuẩn hoá chu kỳ 67–107 tỷ [UL] | A, E |
| Giá so giá trị chuẩn hoá | ĐẮT HƠN | FV kỳ vọng **11.838 đ** (−19% so giá) [UL] | E |

- **Định giá (một dòng):** Bear 8.839 / Base 11.686 / Bull 15.142 đ, trọng số 25/50/25 ⇒ **11.838 đ** vs 14.700 [UL, `model.py`].
  Thị trường đang trả cho ~2 năm LN đỉnh. Nếu đỉnh giá kéo dài 2 năm *và* mặt bằng giá giữa chu kỳ cao (bull) thì giá hiện tại là hợp lý; không kịch bản nào cho dư địa lớn.
- **Đổi verdict khi:** giá ≤ ~11.700 (FV base) mà chỉ báo cầu của Bobby chuyển MID ⇒ xem lại GIỮ/tăng; xem mục 6.
- **Pháp lý (WARNING, không chặn):** khoản cho cổ đông lớn Dakruco vay 40 tỷ, thế chấp bằng chính cổ phiếu DRI; ~186 tỷ tiền gửi USD nằm tại ngân hàng ở Lào; thời hạn quyền đất Lào chưa thấy văn bản. Mục 7.

## 1. Giả thuyết kiểm chứng
| Giả thuyết | Kết quả |
|---|---|
| LN Q1–Q2/26 là do giá đỉnh, không phải nâng cấp bền | **Đúng một phần.** Q2/26: DT +85,45%, sản lượng tiêu thụ **+59,82%**, giá vốn +56,14% [GT] ⇒ phần lớn tăng là SẢN LƯỢNG BÁN (xả tồn), phần giá ≈ +16–18% [UL: 1,8545/1,5982]. Năng suất 1,34→1,81 t/ha (2024→2025) [BCTN] là cấu trúc, nhưng KH 2026 hạ về 1,69 t/ha, khai thác 13.800 t (−9%) [BCTN]. |
| Q4 là quý cao điểm, Q1 thấp nhất (Bobby sửa giả định) | Nhất quán với dữ liệu: Q1/26 DT 279,8 tỷ là quý cao nhất chuỗi vì **bán tồn kho** cuối năm (thành phẩm 153,2→65,0 tỷ trong H1 [BCTC 5.6]), không phải vì khai thác Q1 cao. Doanh thu ghi khi bán ⇒ lệch pha khai thác/bán tới 1 quý. |
| LNST nhạy mạnh theo giá | **Đúng** — ±10% giá ⇒ ±20–28% LNST (mục 4). |

## 2. Chất lượng thu nhập (H1/2026, BCTC gốc)
| Mục | Số | Đánh giá |
|---|---|---|
| KQKD H1/26 [BCTC] | DT 489,92 · LN gộp 203,67 (41,6%) · TC thu 19,84 / chi 4,71 · BH 14,82 · QLDN 23,61 · LN khác 1,49 · LNTT 181,85 · LNST 146,51 (mẹ 146,71) | Lõi là mủ cao su: Q2 100% doanh thu là mủ [BCTC 6.1] |
| **Thanh lý vườn cây** | Thu nhập khác H1/26 chỉ **1,55 tỷ** (Q2), H1/25 lỗ khác −1,64 [BCTC] | **Không bơm LN.** BCTN: thị trường gỗ thanh lý ở Lào "chưa hình thành", tái canh chậm ⇒ chưa có khoản một lần. Rủi ro ngược: nếu Q3/Q4 có thanh lý lớn, phải tách ra. |
| **Khoản trích trước / thưởng** | Chi phí phải trả ngắn hạn 1,62 → **0** tỷ; phải trả NLĐ 67,58 → 28,33 tỷ (lương còn lại 2025 đã chi); "tiền chi khác cho HĐKD" −15,31 tỷ [BCTC 5.18, 5.19, LCTT] | **Không thấy trích trước thưởng 2026 trong H1.** BCTN: lương trực tiếp 2025 **+51,3%**, có thưởng vượt sản lượng/3P ⇒ thưởng 2026 nhiều khả năng dồn vào Q4 ⇒ **LN H1 phóng đại tương đối, Q4 có thể gánh chi phí thưởng**. Checklist mục 1 giữ nguyên. |
| **Tồn kho** | Thành phẩm 153,18 → 64,99 tỷ; CPSXKD dở dang 6,26 → **58,45 tỷ**; NVL 16,61 → 22,27 [BCTC 5.6] | BCTC **không công bố tấn**. Quy đổi theo giá vốn 33,11 tr/t [BCTN]: thành phẩm ≈ 4.630 → 1.960 t (ước lượng). Dở dang +52 tỷ là chi phí mùa vụ chờ kết chuyển ⇒ đi vào giá vốn H2. KH 2026 bán 16.900 t > khai thác 13.800 t [BCTN] ⇒ **tồn kho đệm gần cạn**, H2 bán ≈ khai thác. |
| **CFO** | H1/26 **154,45 tỷ** vs LNST 146,51 (1,05x); H1/25 33,57 [BCTC LCTT] | Tốt — nhưng có 30,3 tỷ từ giảm tồn kho (không lặp lại) và −40,7 tỷ trả nợ phải trả. CFO lõi ≈ 1,0x LN. |
| **Vay** | Ngắn hạn 77,22 tỷ (LaoViet 36,71 LAK; VietinBank Lào 31,53 LAK/USD 11%/6,1%; VietinBank ĐL 8,99 VND 9%) + dài hạn 22,66 [BCTC 5.21] | Nhỏ so tiền. Vay bằng LAK là hedge tự nhiên cho chi phí ở Lào. Thế chấp: quyền sử dụng đất + vườn cây Nông trường 1–4. |
| **Tiền** | Tiền 61,09 + tiền gửi có kỳ hạn 303,50 (trong đó **USD 7,02 tr tại VietinBank Lào và LaoViet**, 3%/năm; 70 tỷ tại Quỹ TDND Cao su ĐL) ⇒ net cash **264,7 tỷ** [BCTC 5.1, 5.2, 5.21] | Sau cổ tức 10% (≈73,2 tỷ, ex ~22/09 theo khoảng giá BQ — ngày trả CHƯA xác minh) ⇒ ≈ **191,5 tỷ** [UL]. |
| Capex | 28,34 tỷ H1 > khấu hao 23,42 [BCTC] | Đầu tư sầu riêng (XDCB dở dang 37,84 tỷ) + tái canh. FCF ≈ 90% LN [UL]. |

**Kết luận chất lượng:** LN H1 sạch (không thanh lý, không hoàn nhập), CFO khớp; hai điểm làm LN *dễ phóng đại* là
(i) xả tồn kho (không lặp lại) và (ii) chưa trích thưởng theo quý.

## 3. Bảng cân đối & cổ tức
- VCSH mẹ 799,97 tỷ ⇒ BVPS 10.929 đ ⇒ **PB 1,35x** ở 14.700 [BCTC; blind block E].
- Chênh lệch tỷ giá luỹ kế trong VCSH −355,0 tỷ (−335,0 đầu năm) [BCTC] ⇒ LAK mất giá ăn mòn VCSH sổ sách ~20 tỷ/6 tháng.
- **Cổ tức:** 2025 10% (1.000 đ) [BCTN]; KH 2026 10% [BCTN] ⇒ **tỷ suất 6,8%** ở 14.700. Nguồn trả cổ tức của mẹ phụ
  thuộc LN chuyển về từ Daklaoruco (bị khấu trừ thuế Lào 11,17 tỷ H1 [blind block D]; LNST riêng mẹ Q2/26 55,70 tỷ giảm
  32,5% do LN chuyển về thấp hơn 39,32 tỷ [GT]). Cổ đông lớn Dakruco (45%) có nhu cầu tiền ⇒ chính sách cổ tức cao có
  khả năng duy trì, **nhưng** 10% không bảo vệ được giá nếu LN về mức chuẩn hoá (cổ tức 73 tỷ ≈ 84% LN base 86,7 tỷ).

## 4. Độ nhạy LNST theo giá bán — SỐ THẬT DRI (thay số minh hoạ của Bobby)
Calibrate [UL, `model.py`]: sản lượng bán 14.000 t/năm (2025 bán 14.007,76 t; KH khai thác 2026 13.800 t [BCTN]);
giá bán hiện tại **55,7 tr/t** (= giá 2025 47,24 [BCTN] × 1,18); giá vốn **33,11 tr/t** (2025 [BCTN]); BH+QLDN 76,9 tỷ/năm,
tài chính ròng 25,1 tỷ/năm, thuế hiệu dụng 19,4% (H1/26 [BCTC]); khác 10 tỷ. ⇒ LNST run-rate **221,6 tỷ** — khớp LN lõi
TTM 221 tỷ của blind block (kiểm chéo calibrate).

| Giá bán | (a) giá vốn/tấn cố định | (b) 30% doanh thu tăng/giảm chảy vào lương-thưởng |
|---|---|---|
| −30% (39,0 tr/t) | 33,0 tỷ (**−85%**) | 89,6 (−60%) |
| −20% (44,6) | 95,9 (−57%) | 133,6 (−40%) |
| −10% (50,2) | 158,8 (**−28%**) | 177,6 (**−20%**) |
| 0 (55,7) | 221,6 | 221,6 |
| +10% | 284,5 (+28%) | 265,7 (+20%) |
| +20% | 347,4 (+57%) | 309,7 (+40%) |
| +30% | 410,3 (+85%) | 353,7 (+60%) |
- Hoà vốn LNTT (a): **36,1 tr/t** ≈ −35% từ giá hiện tại. Bobby đúng hướng (±29%/±19% minh hoạ); số thật DRI: **±28% / ±20%** mỗi 10%.
- Vì sao (b) có trọng lượng: lương trực tiếp 2025 +51,3% khi DT cao su +43% [BCTN] — quỹ lương 3P/thưởng vượt chỉ tiêu
  CÓ đi theo kết quả. Q2/26 giá vốn/tấn phẳng YoY (−0,7%) vì chưa trích thưởng (mục 2) ⇒ (a) là cận trên của độ nhạy.
- **Theo quý (cho checklist Q3):** ở giá/giá vốn hiện tại, LNST quý ≈ 37 / 55 / 74 / 92 tỷ khi bán 2.500 / 3.500 / 4.500
  / 5.500 t [UL]. Ngưỡng checklist **< 22 tỷ** ⇔ bán < ~2.000 t, hoặc giá bán thực ≈ −15% so Q2, hoặc trích thưởng/lỗ
  tỷ giá lớn bất thường. Q3 kỳ vọng [UL]: H2 bán ≈ 16.900 − ~8.700 (H1, ước lượng) ≈ 8.200 t ⇒ Q3 ~3.500–4.000 t ⇒
  **LNST Q3 ~55–65 tỷ** (ước lượng), trừ thưởng/dở dang kết chuyển.

## 5. Định giá theo chu kỳ (KHÔNG nhân LN đỉnh)
Phương pháp [UL, `model.py`]: giá bán giữa chu kỳ = 47,24 tr/t × (RSS3 chuẩn / RSS3 2025 2,183) [FEED]; LN chuẩn hoá ×
FCF 90% × **niên kim 28 năm** (quyền đất Lào tới ~2054 — ước lượng, chưa thấy văn bản thời hạn; blind block D) + LN vượt
chuẩn trong thời gian giá còn đỉnh (chiết khấu) + net cash sau cổ tức 191,5 tỷ + 50% khoản cho Dakruco vay.

| Kịch bản (w) | RSS3 chuẩn | Giá bán | Giá vốn | LNST chuẩn | PE lõi @14.700 | r | Đỉnh kéo dài | **FV/cp** |
|---|---|---|---|---|---|---|---|---|
| Bear (25%) | 1,865 (trung vị 10y) | 40,4 | 32,0 | 66,8 | 15,0x | 14% | 0,5 năm | **8.839** |
| Base (50%) | 1,970 (giữa 5y/10y) | 42,6 | 32,5 | 86,7 | 11,2x | 13% | 1 năm | **11.686** |
| Bull (25%) | 2,075 (trung vị 5y) | 44,9 | 33,0 | 106,7 | 8,9x | 12% | 2 năm | **15.142** |
| **Kỳ vọng** | | | | | | | | **11.838** (−19%) |
- Kiểm chéo: trung vị LNST năm 2017–2025 [BQ] 74,1 tỷ; blind block chuẩn hoá 94 tỷ ⇒ base 86,7 nằm giữa.
- RSS3 Q3/26 = 2,753 [FEED] = +40% trên base. Thị trường đang trả **PE 4,9x LN run-rate 221 tỷ** — rẻ nếu đỉnh giữ, đắt nếu về giữa chu kỳ.
- Điểm yếu của định giá: niên kim 28 năm không tính gia hạn đất / tái canh sầu riêng (thiên thấp) và không tính vườn
  già giảm năng suất (thiên cao). Hai sai lệch ngược chiều; tôi không có số để tách.

## 5b. Thanh khoản & capacity
- 20 phiên 29/09–26/10/2026 [BQ]: KL trung vị **1,77 tr cp/phiên**, GTGD trung vị **27,4 tỷ** (TB 28,9).
- Vị thế 3.800 cp ≈ **55,9 tr đ** = **0,22%** KL trung vị 1 phiên ⇒ thoát toàn bộ trong 1 phiên không ảnh hưởng giá.
  Capacity không phải ràng buộc. UPCoM: biên độ ±15%, tick 100 đ.

## 6. Kịch bản GIỮ / GIẢM / THOÁT — điều kiện kích hoạt (chỉ đề xuất, user duyệt)
Neo: checklist khai trước `kb/projects/bctc-q3-checklist-fpt-tv1-dri-20261025.md` (**không sửa**) + chỉ báo Bobby §4–5.

| Kịch bản | Kích hoạt (bất kỳ dòng nào) | Hành động đề xuất |
|---|---|---|
| **THOÁT** (bán hết 3.800) | (1) Bobby → TROUGH: Brent < 85 **và** Qingdao > 70 vạn t **và** TSR20 < 220¢ hai tháng · (2) sự kiện Lào: thay đổi thuế/đất/kiểm soát chuyển LN, hoặc cấm/khó rút USD tại NH Lào · (3) Dakruco vay thêm / gia hạn / tăng khoản phải thu bên liên quan | Bán hết, không đợi BCTC |
| **GIẢM 50%** (SpaceX 2.500→1.250, ZaloPay 1.300→650) | (1) **Checklist: LNST Q3 < 22 tỷ** (luật đã khai) · (2) [đề xuất của tôi, ngoài checklist] ≥2/3 chỉ báo Bobby xấu: Qingdao tăng ≥3 tuần, lốp bán thép < 62%, TSR20 ≤ 234¢ (−8%) · (3) [đề xuất] giá ≥ 15.100 (≈ FV bull) — chốt vì đã trả đủ kịch bản tốt nhất | Bán 50% |
| **GIỮ** | LNST Q3 ≥ 50 tỷ **và** biên LNST mẹ ≥ 27% (dự báo F blind) **và** không có trích thưởng/xả tồn che LN · Bobby chuyển MID: Qingdao giảm ≥3 tuần + lốp ≥ 70% + ô tô TQ YoY dương | Giữ, nhận cổ tức 6,8% |
| Vùng giữa | LNST Q3 22–50 tỷ | Giữ theo checklist, nhưng ghi rõ: LN đang về phía chuẩn hoá sớm hơn kỳ vọng ⇒ xem lại sau BCTC Q4 |

**Đánh giá trung tâm:** Q3 nhiều khả năng ĐẠT (ước lượng 55–65 tỷ; blind p 0,70 cho ≥ 50) ⇒ checklist không kích hoạt
bán. Nhưng định giá chuẩn hoá thấp hơn giá 19% và Bobby nghiêng PEAK 60/40 ⇒ rủi ro nằm ở **2027** chứ không ở Q3.
Vị thế quá nhỏ (55,9 tr đ) để chi phí cơ hội đáng kể; đề xuất dùng dòng (3) "giá ≥ 15.100" làm điểm chốt nửa còn lại.

## 6b. Cái gì sẽ ĐỔI kết luận khi BCTC Q3 ra 30/10
| Quan sát Q3 | Ngưỡng | Đổi gì |
|---|---|---|
| LNST mẹ Q3 (chỉ tiêu 20, hợp nhất) | < 22 tỷ | → GIẢM 50% (checklist) |
| | ≥ 70 tỷ và biên ≥ 33% | Nâng LN run-rate; FV base nhích (+ ~1 năm đỉnh ≈ +1.400 đ/cp [UL]); vẫn không đổi NON |
| Thu nhập khác (thanh lý vườn) | > 10 tỷ | Tách khỏi LN lõi trước khi so ngưỡng |
| Chi phí phải trả / phải trả NLĐ | tăng > 20 tỷ | Thưởng bắt đầu trích ⇒ (b) đúng ⇒ độ nhạy thấp hơn, LN Q4 thấp hơn |
| Tồn kho thành phẩm | tăng mạnh (> 100 tỷ) khi giá đỉnh | DRI ôm hàng chờ giá ⇒ rủi ro giá giảm tồn kho; CFO yếu |
| CFO 9T | < 0,8x LNST 9T | Chất lượng LN giảm ⇒ nghiêng GIẢM |
| Khoản cho Dakruco vay / phải thu bên liên quan | tăng | → THOÁT (mục 6) |
| Chênh lệch tỷ giá VCSH | xấu thêm > 30 tỷ/quý | LAK sụt mạnh ⇒ xem lại rủi ro chuyển LN |

## 7. ⚠️ WARNING pháp lý/quản trị (chỉ cảnh báo, không chặn)
1. **Giao dịch bên liên quan:** DRI cho Dakruco (cổ đông 45%) vay 80 tỷ (22/05/2023, 9%, 60 tháng), còn 40 tỷ; TSĐB =
   6 tr CP **DRI** do Dakruco sở hữu (tài sản đảm bảo tương quan với chính rủi ro của DRI) [BCTC 5.12]. 70 tỷ gửi tại Quỹ
   TDND Cao su Đắk Lắk (DRI còn góp vốn vào quỹ này [BCTC 5.11]) — nghi liên quan hệ sinh thái Dakruco, chưa xác minh.
2. **Tiền ở Lào:** USD 7,02 tr (~185 tỷ, ước lượng theo tỷ giá ~26.300) gửi 3 tháng tại VietinBank Lào và NH Liên doanh
   Lào–Việt [BCTC 5.2] ⇒ rủi ro chuyển đổi/chuyển tiền về VN nếu Lào siết ngoại hối.
3. **Quyền đất Lào:** thoả thuận 19/11/2004, tầm nhìn tới 2054 — thời hạn cụ thể chưa thấy văn bản [blind block D];
   thuê đất 6 USD/ha/năm; CIT Lào 20% [BCTC 5.17]. Thay đổi chính sách đất/thuế Lào là rủi ro đuôi lớn nhất.
4. **EUDR** áp dụng DN lớn 30/12/2026 [BOBBY §1.7]; DRI đã bán 784,32 t chuẩn EUDR/FSC 2025 với premium 130 USD/t [BCTN] ⇒ rủi ro nhỏ.
Không có dấu hiệu sai phạm; đây là cấu trúc cần theo dõi.

## 7b. Rủi ro Nam Lào / LAK
- Chi phí (lương ~7,46 tr đ/người/tháng trực tiếp [BCTN], 2.466 lao động 30/06/26 [BCTC 1.7]) bằng LAK; doanh thu bằng
  USD ⇒ **LAK mất giá có lợi cho biên** nhưng (i) bào mòn VCSH qua chênh lệch quy đổi (−20 tỷ H1), (ii) làm khó chuyển
  LN về (khấu trừ thuế 11,17 tỷ H1; LN chuyển về 2026 thấp hơn 2025 39,32 tỷ [GT]).
- VND/LAK theo BCTC: 0,8248 (H1/25) → 0,8470 (30/06/26) [BCTC — nhãn cột "VND/LAK" nhưng độ lớn ≈ LAK/VND ⇒ LAK yếu
  ~2,7% so VND; diễn giải chiều là ước lượng].
- Vay bằng LAK (~68 tỷ) là hedge một phần.

## 8. Lệch dữ liệu giữa các nguồn
| Mục | Nguồn A | Nguồn B | Xử lý |
|---|---|---|---|
| LNST mẹ Q2/26 | BQ `NP_P0` 63,79 | BCTC 68,29 | dùng BCTC |
| CFO H1/26 | BQ `CF_OA_P0` Q1+Q2 = 136,97 | BCTC 154,45 | dùng BCTC |
| Tiền | BQ `Cash_P0` 61,09 | BCTC + 303,50 tiền gửi ĐHĐH | dùng BCTC |
| Biên gộp Q2/26 | BQ `GPM_P0` 0,392 | BCTC 44,52% | dùng BCTC |
| LNST Q2/26 | Hợp nhất 68,19 | Riêng mẹ 55,70 [GT] | checklist "< 22 tỷ" hiểu là **hợp nhất thuộc CĐ mẹ** (chỉ tiêu 20) — Mike/user xác nhận nếu khác |
| Giá BQ trước 22/09 | `Close` ≠ `Price` | hệ số không đều (0,932–0,939) | đã biết (ADJFACTOR tick_offset); dùng `Price` |

## H. Đối chiếu khối chu kỳ sau khi đọc BCTC Q2 gốc
| Mục | Khối mù nói | BCTC/dữ liệu bước 2 | Khớp / lệch | Đổi verdict? |
|---|---|---|---|---|
| A biên | TTM 26,0%, p=100 | KQKD H1 khớp; biên phóng đại nhẹ do chưa trích thưởng | Khớp | Không |
| C pha | ĐỈNH | Bobby PEAK 60/40 (độc lập) | Khớp | Không |
| E PE chuẩn hoá | 10,8x (LN 94) | 11,2x (LN 86,7, giá 14.700, net cash sau cổ tức) | Khớp (lệch do cổ tức + chọn RSS3 chuẩn thấp hơn) | Không |
- Verdict NON phụ thuộc C và E. Bỏ khối chu kỳ, verdict **vẫn NON** (PB 1,35x không phải vùng sợ hãi), nhưng mất cơ sở cho đề xuất GIẢM.

## Sổ chấm
- Dự báo F của blind block (đã khoá, chấm 2026-11-09) giữ nguyên. Không thêm dự báo mới.
- Entry: `CYC-DRI-20261026`, `blind: yes` (bước 1); bước 2 này `blind: no` (đọc Bobby + checklist).

## Nguồn
- BCTC hợp nhất Q2/2026 DRI (dri.com.vn; cache `/tmp/dri_src/2.VI_BaoCaoTaiChinh_Q2_2026_HopNhat.pdf`, ảnh trang
  `/tmp/dri_img/hn_04..22.png`): KQKD tr.3, LCTT tr.4–5, thuyết minh 5.1–5.6, 5.10–5.13, 5.18–5.21.
- Công văn giải trình LN Q2/2026 (`/tmp/dri_src/3.VI_GiaiTrinhLienQuanDenBCTC_Q2_2026.pdf`).
- BCTN 2025 (`/tmp/dri_src/ar2025.txt`): KQKD 2025, KH 2026, lương, EUDR.
- BQ `tav2_bq.ticker` (giá/KL tới 26/10/2026), `tav2_bq.ticker_financial` (tới 2026Q2) — truy vấn 27/10/2026.
- `data/rubber_monthly.csv` (WB RSS3 tới 2026-09).
- Bobby: `kb/data_registry/market-state/vn_sector_read_rubber_20261027.md`.
- Blind: `agents/Taylor/research/dd_blind2_DRI_20261026/CYCLE_BLOCK.md` (md5 15bd430e…).
- `kb/projects/dri-manual-sell-20261021.md`, `kb/projects/bctc-q3-checklist-fpt-tv1-dri-20261025.md`.
