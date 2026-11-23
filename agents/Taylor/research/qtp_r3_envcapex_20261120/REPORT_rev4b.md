# QTP DD rev4b — xử lý skeptic r1 + r2 · 23/11/2026 · job `Taylor_20261123_063644`

> Chỉ NGHIÊN CỨU. Không ghi `dd_price_zones.json`, không email. Thay thế `REPORT_rev4.md` (skeptic r2 đọc bản đó, md5 `582e5c7e…`; không đè bản cũ). Sổ: dd_date 2026-11-17, rev 4 (bản 4b).
> Mô hình `qtp_model_rev4b.py` (md5 `7fc3969b04012119de370de27be28fce`), output `qtp_model_rev4b_out.txt` (md5 `c58a317314cf0ea31eb80ac43f84c2bf`). Mô hình là bản sao r3c, chỉ THÊM tham số và hàm; với mặc định, tái lập đúng r3c 8.557/7.701, r3 7.836/7.053 và r2 14.599 (dòng 1–2 của output).
> Khoá giả định: `assumptions_QTP_rev4b.json` (md5 `91add83223d20aa7ec4880a145259334`). Khoá TRƯỚC khi đọc giá, kể cả lần khoá lại ở 4b: thay đổi ở 4b chỉ đến từ BCTC, không từ giá. `dd_assumptions_lint.py` rc=0, chế độ cảnh báo, còn cảnh báo hình dạng schema.
> **Bằng chứng ảnh, dành cho người kiểm không đọc được PDF scan:** thư mục `evidence_rev4/` gồm:
> - `kt25_p31_tm19_1.png` (TM 19.1);
> - `kt25_p35_tm23_24_chiphitaichinh.png` (TM 24);
> - `kt25_p37_tm30_eps_trich_ktpl.png` (TM 30);
> - `kt25_p8_bcdkt_nguonvon.png` (BCĐKT 31/12/2025);
> - `q3_26_p4_nguonvon.png` (BCĐKT 30/9/2026);
> - `q3_26_p42_v27_von_chu.png` (Q3/26 V.27).
>
> Ảnh render từ `../dd_QTP_20261117/src/fy2025_kt_vi.pdf` và `q3_2026_bctc_giaitrinh.pdf` (PyMuPDF).
> r = 13,5%: `deposit_rate_vn.effective_deposit_rate('2026-11-23')` = 7,40% (CCTG 12M 02/11), bằng mức neo ⇒ không điều chỉnh (V1).

## 0. Kết luận

- **Tâm rev4b: 6.294 đ/cp sau chiết khấu thanh khoản (6.993 trước CK).** r3c là 7.701, nên tâm giảm 18,3%; rev4 là 6.273, chênh +0,3%. Nhãn vẫn **ĐẮT / TRÊN vùng**.
- Cầu nối từ r3c, trước CK:
  - KTPL (trích 10,35% LNST năm trước, số dư 148,64 tỷ, đã cộng lại phần trừ trùng nwc): **−871**.
  - Trọng số P0 0,4 → 0,5 (trở về r3): **−693**.
- **Vùng biến thể đơn lẻ, sau CK: 5.159 … 7.139.** Kết hợp các biến thể: 5.010 … 7.952. Theo trọng số P0 từ 0,6 về 0: 5.670 … 9.413.
- **Hai đầu của phần dư VC 115 tỷ/năm** (FS không thuyết minh; trả lời yêu cầu skeptic r2): giữ phần dư thì 6.294 (tâm); bỏ phần dư thì 6.942. Phần dư được giữ trong tâm vì không có cơ sở độc lập để bỏ.
- **Cvlp (amoniac đi qua giá biến đổi) là upside có điều kiện, không vào tâm.** q=0,25 cho 6.804 (+8,1%); q=1 cho 8.333 (+32,4%).
- **Sau khoá giá:** giá tham chiếu là 10.200 (đóng cửa 20/11/2026, BQ `ticker`), tức 1,62× tâm. Giá này còn cao hơn cả:
  - kết hợp thuận lợi nhất 7.952 (1,28×);
  - P0 = 0, tức chắc chắn được bù, 9.413 (1,08×);
  - Cvlp q=1, 8.333 (1,22×);
  - biến thể đơn lẻ cao nhất 7.139 (1,43×).
  Ngưỡng 0,85× tâm là 5.350.
- **Sizing (V8):** không đề xuất mua vì giá ở trên mọi biến thể. Nếu có thì vẫn trong khung 2–4% NAV.
- **WARNING, không vào base:** ở P0 cơ sở, sau KTPL, dòng tiền toàn công ty 2030–39 cộng dồn −3.163 tỷ. Tiền ròng xuống **−230 tỷ năm 2039 ngay cả khi không chia cổ tức**.

## 1. Đính chính so với rev4 — hạng mục skeptic r2

| # | Hạng mục skeptic r2 | Xử lý 4b | Tác động lên tâm (sau CK) |
|---|---|---|---|
| A | **(đòn chính) 69,04 tỷ là lỗ tỷ giá TM24 (r2 `FX_AT`) chứ không phải trích KTPL?** | **Đây là HAI dòng khác nhau, hai số gần trùng nhau một cách ngẫu nhiên.** Đọc trực tiếp trên ảnh: TM24 "Lỗ chênh lệch tỷ giá phát sinh trong kỳ" **2025** = **69.037.729.222** (`kt25_p35…png`); TM 19.1 "Trích quỹ khen thưởng phúc lợi và thưởng BQL điều hành" ghi trong cột năm **2024** = **(69.036.066.415)** và năm 2025 = **(71.362.353.875)** (`kt25_p31…png`). **Xác nhận độc lập:** TM 30 (EPS) ghi "Số trích quỹ khen thưởng phúc lợi" năm 2024 = **71.362.353.875** và EPS 2024 trình bày lại 1.218 (từ 1.376) theo NQ ĐHCĐ 58/NQ-NĐQN 27/4/2025 (`kt25_p37…png`). Vậy r2 dùng 69,04 làm lỗ tỷ giá là ĐÚNG, và rev4 dùng nó làm trích KTPL cũng ĐÚNG. | 0 |
| B | Số dư 120,6 tỷ lệch mốc ngày với netcash 30/9/2026 | Đổi sang **148,64 tỷ** tại 30/9/2026 (BCĐKT Q3/26, mã 323, `q3_26_p4…png`). Mốc 31/12/2025 = 120,66. | −62 trước CK (so với 120,6) |
| C | Trừ trùng với nwc r2 (nwc trừ tổng nợ ngắn hạn, đã gồm quỹ KTPL) | Thêm hàm `nwc_addback`: khi nwc được thu hồi lúc dừng nhà máy, cộng lại PV của số dư KTPL đã trừ ở thời điểm 0. | +23 trước CK (cơ sở; skeptic ước 20–45) |
| D | KTPL theo %LNST có thể sai dạng nếu quỹ bị trần theo lương | **Dữ kiện mới, Q3/26 V.27 (`q3_26_p42…png`):** "giảm khác" của LNST chưa phân phối 9T26 = **544,58 tỷ**. Trừ cổ tức 1.000 đ/cp × 450 triệu cp = 450 tỷ ⇒ trích KTPL trên LNST 2025 **khoảng 94,58 tỷ** (**ước lượng tách**: V.27 không tách dòng). Tỷ lệ là 9,1% trên LNST 1.035,9, thấp hơn 11,4% của hai năm trước ⇒ quỹ tăng **kém tỷ lệ thuận** với lợi nhuận. Base đổi sang **tỷ lệ gộp 3 năm = (69,04 + 71,36 + 94,58) / (614,4 + 619,26 + 1.035,9) = 10,35%**. Biến thể "trần cố định 80 tỷ/năm" cho −4,6%: thấp hơn base vì ở P0 lợi nhuận thấp, mức cố định ăn vào nhiều hơn tỷ lệ. Chưa có văn bản nào xác nhận trần lương (NĐ 53/2016 và văn bản thay thế): **không kiểm chứng được**. | Tỷ lệ 11,38% → 10,35%: +; gộp B+C+D so với rev4: +21 sau CK. Độ nhạy: 8% +1,8% / 15% −3,5% / cố định 80 −4,6% |
| E | Thời hạn PPA hiện hữu và giá cố định sau khi hết khấu hao | Vẫn **không kiểm chứng được**: legal-vn 23/11 không tìm được nguồn; BCTC không nêu. Kịch bản "xấu" của r2 (dừng 2040) là cách bao rủi ro này. | Không đổi |
| F | GPMT 517 Phụ lục 2 | Vẫn **không lấy được văn bản**. | Biến thể opex SCR từ 2032: +13,4% (ngoài tâm) |
| G | Phần dư VC 115 tỷ/năm | Báo cả hai đầu (§0). | 6.294 / 6.942 |

## 2. Đính chính so với r3c — hạng mục skeptic r1 (giữ từ rev4, số cập nhật theo 4b)

| # | Hạng mục skeptic r1 | Xử lý | Loại | Tác động (sau CK) |
|---|---|---|---|---|
| 1 | Chi phí biến đổi 470 tỷ/năm qua giá biến đổi của PPA hiện hữu (đòn chính r1) | **legal-vn 23/11:** TT12/2025 (VBHN 56/VBHN-BCT) Đ7.3, cấu phần **Cvlp** "theo khối lượng và đơn giá các loại vật liệu phụ" ⇒ amoniac **nhiều khả năng** thuộc Cvlp. Nhưng **Đ18**: với PPA đã ký, nhóm "biến động khác" chỉ trượt **2,5%/năm**, không theo chi phí thực tế ⇒ phải **sửa PPA** (Đ26, Đ27.3). Không có tiền lệ 2020–2026. FS gộp 72,33 đ/kWh vào phần **xin** tăng giá. Đây là thông tin tham khảo, không phải ý kiến luật sư. | (b) kịch bản, không vào base | q=0,25 +8,1% · q=0,5 +16,2% · q=1 +32,4%; phép tính của skeptic (VC=0 mọi kịch bản) 8.843 (+40,5%) |
| 2 | Trọng số r3→r3b là đọc lại dữ kiện cũ | Trở về **0,50 / 0,30 / 0,20** (r3); xem §3. | (a) | −693 trước CK |
| 3 | Thay xúc tác SCR; FS ghi "tuổi thọ 10 năm" | FS §3.1.7 ghi tuổi thọ 10 năm, khấu hao 10 năm; giải trình thẩm tra (txt 4534–4539) ghi tuổi thọ còn lại 18 ⇒ 17 năm, "đã sửa". Không có số liệu về chu kỳ hay chi phí thay xúc tác. | (c) không kiểm chứng được | 27 tỷ/năm từ 2033: −2,2%; 54 tỷ: −4,3% (**ước lượng ngành**: ~1 m³/MW × 1.200 MW × ~5.000 USD/m³ ≈ 160 tỷ, thay một nửa mỗi 3 năm). FC chỉ thu 10 năm: −3,3% |
| 4 | Tỷ giá trên EPC 89,76 triệu USD (QĐ 1710) | VND −10% ⇒ +237 tỷ vốn chủ (tỷ giá FS 26.388) | (b) | −6,0% |
| 5 | Sản lượng huy động | FS 6.000 h; doanh thu bù và chi phí biến đổi theo tỷ lệ sản lượng; O&M cố định giữ nguyên | (b) | 5.000 h +2,9% / 6.500 h −1,5%. Hiệu ứng lên LNST nền r2 không mô hình hoá ở đây ⇒ không đọc là "huy động ít thì tốt" |
| 6 | Quỹ KTPL | Xem §1 A–D | (a) vào base | −871 trước CK (cộng chung với dự án) |
| 7 | GPMT 517 Phụ lục 2 | Không lấy được | (c) | +13,4% nếu SCR chạy từ 2032 |

## 3. Trọng số — dữ kiện MỚI tách khỏi dữ kiện cũ

Chốt **0,50 / 0,30 / 0,20**. Đây là ước lượng, N = 0 tiền lệ.

- **Dữ kiện đã có từ r3, không phải lý do để dời trọng số:**
  - EVN kiến nghị 29/12/2025 (`REPORT_r3.md:98`);
  - FS dẫn TT57 Đ20.3;
  - 9 năm chưa được bù;
  - 0 tiền lệ;
  - bên mua và chủ chi phối cùng thuộc EVN.
- **Dữ kiện mới, chiều thuận lợi:** Luật Điện lực 61/2024 Đ52.4 (còn tranh cãi; chưa đọc nguyên văn).
- **Dữ kiện mới, chiều bất lợi:**
  - không có Đ14.6;
  - TT07 đã bị TT12 bãi bỏ và TT12 không có điều tương đương;
  - PPA mẫu theo TT12 không có điều khoản "thay đổi pháp luật";
  - chỉ thị EVN 12/2025 không nói cơ chế thanh toán.
- Chiều bất lợi nhiều hơn ⇒ không có cơ sở để hạ P0. Mục "(0)" tự mâu thuẫn của r3c được xếp lại vào nhóm "dữ kiện cũ".

| P0 (P50:P100 = 60:40) | trước CK | sau CK |
|---|---|---|
| 0 | 10.458 | 9.413 |
| 0,2 | 9.072 | 8.165 |
| 0,3 | 8.379 | 7.541 |
| 0,4 | 7.686 | 6.918 |
| **0,5 (chốt)** | **6.993** | **6.294** |
| 0,6 | 6.300 | 5.670 |

Kết quả thuần theo kịch bản, trước / sau CK:
- P0: 3.528 / 3.176
- P50: 8.748 / 7.873
- P100: 13.025 / 11.722

## 4. Biến thể (trước / sau CK)

| Biến thể | Trước | Sau | Δ |
|---|---|---|---|
| **Tâm rev4b** | 6.993 | **6.294** | – |
| Bỏ phần dư 115 của VC | 7.713 | 6.942 | +10,3% |
| Opex SCR từ 2032 | 7.932 | 7.139 | +13,4% |
| Sản lượng 5.000 h / 6.500 h | 7.196 / 6.892 | 6.476 / 6.202 | +2,9% / −1,5% |
| Tỷ giá EPC, VND −10% | 6.576 | 5.919 | −6,0% |
| Xúc tác SCR 27 / 54 tỷ/năm từ 2033 (ước lượng) | 6.841 / 6.689 | 6.157 / 6.020 | −2,2% / −4,3% |
| FC chỉ bù 10 năm | 6.761 | 6.085 | −3,3% |
| Bù chậm từ 2033 | 5.732 | 5.159 | −18,0% |
| Khấu hao 18 năm | 6.870 | 6.183 | −1,8% |
| Lãi vay 7% / 11% (ước lượng 9%) | 7.390 / 6.592 | 6.651 / 5.933 | +5,7% / −5,7% |
| KTPL 8% / 15% / cố định 80 tỷ | 7.117 / 6.749 / 6.670 | 6.405 / 6.074 / 6.003 | +1,8% / −3,5% / −4,6% |
| Kết hợp thuận lợi (bỏ dư 115 + opex 2032 + lãi 7%) | 8.835 | 7.952 | +26,3% |
| Kết hợp bất lợi (bù chậm 2033 + xúc tác 27 + 5.000 h + lãi 11%) | 5.566 | 5.010 | −20,4% |

## 5. V1 · V2 · V3 · V5 · V6

- **V1:** r = 13,5% (neo 03/11; lãi huy động 7,40% tại 23/11 = neo).
  - β=1, r và lãi vay cùng dịch: −100bp ⇒ +5,7%; −50bp ⇒ +2,8%; +100bp ⇒ −5,1% (dòng +50bp có trong output).
  - β = 0,5, ±100bp: +4,2% / −4,0%.
- **V2 (báo kèm):** Ke 12,3% ⇒ 6.505 (+3,4%); 13,4% ⇒ 6.310 (+0,3%). Dòng tiền hữu hạn đến 2047, không có terminal vô hạn.
- **V3:** chiết khấu 10%, dùng lại r2 §6 (ADV trung vị và free float đọc sau khoá ở r2; vị thế 1 tỷ thoát khoảng 5,5 phiên, 3 tỷ khoảng 16 phiên ở mức tham gia 15% ADV). Nhãn tính trên giá trị sau CK.
- **V5:** dữ liệu < 12 tháng ⇒ tái dùng: NARROW, REGULATORY/COST (`data/moat_tags.csv` 2026-06-05). Kiểm nhanh: hào PPA có điều tiết không che được chi phí tuân thủ mới. Không thưởng, không trừ.
- **V6 (chỉ hiển thị):** V_ngắn = −586. Lý do: LNST nền chuẩn hoá 565 tỷ cộng delta trung bình 2030–39 (−605 tỷ) là số âm. V_dài (cơ sở) = 7.559. **D không xác định** ⇒ chỉ báo V_ngắn kèm giải thích dòng tiền âm: opex SCR/FGD chưa được bù, cộng lãi và gốc vay dự án 2030–39. Luật 0,85×tâm không tự kích hoạt; cần Mike/user phán đoán.

## 6. Điều kiện huỷ và mốc đổi nhận định

- Điều kiện huỷ (a)–(e) của r3c §6 giữ nguyên. Quan trọng nhất là **(d)**: chưa ký thoả thuận bổ sung giá PPA trước COD (~12/2029).
- Thêm **(f)**: nếu có phụ lục PPA đưa Cvlp amoniac vào giá thì chạy lại với q=1 (+32%).
- **Lên:**
  - Văn bản EVN/BCT chấp nhận bù ⇒ 8.300–9.400.
  - GPMT cho SCR chạy từ 2032 ⇒ +13%.
- **Xuống:**
  - EVN/BCT từ chối bằng văn bản ⇒ khoảng 3.200;
  - TMĐT hoặc tỷ giá EPC vượt;
  - BCTC cho thấy trích KTPL tăng tỷ lệ thuận với lợi nhuận (về mức 11–15%).

## 7. Giới hạn

- Lãi vay 9%, kỳ hạn, giải ngân và COD là **(ước lượng)**.
- Chi phí xúc tác SCR là **ước lượng ngành**.
- Mức trích KTPL 2026 (94,58) là **ước lượng tách** từ V.27 (giả định cổ tức đúng 450 tỷ).
- Trần lương của quỹ KTPL, thời hạn PPA và GPMT 517 là **không kiểm chứng được**.
- legal-vn là thông tin tham khảo; chưa đọc nguyên văn TT57 và Đ52.4.
- Giá tham chiếu 10.200 lấy từ BQ (phiên 20/11/2026), chỉ dùng để gắn nhãn.
