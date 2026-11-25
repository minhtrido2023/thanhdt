# SAS (SASCO, UPCoM) — DD rev3 đầy đủ theo luật B5 + D4 (25/11/2026, job Taylor_20261125_063648)

Bản làm lại đầy đủ của **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/SAS/REPORT_r3.md`, sổ rev2, 31.658), theo HANDOFF đợt 4 phương án (a) (user duyệt 25/11 13:3x). Bước 0 w3 (`dd_recheck_20261125w3/SAS/SUMMARY.md`) phát hiện r3 dùng RONIC terminal ngầm = ∞ trong khi moat NARROW ⇒ D4 bắt buộc.
- **Khoá trước khi chạy:** `PREREG_rev3.md` + `calc/assumptions_rev3.json` (kế thừa nguyên `assumptions_r3.json` md5 `5c7097bb…`) + nguồn mới `src_ocr/` ⇒ `LOCK_rev3_md5.txt` (script assert md5 trước khi tính).
- **Calc:** `calc/model_sas_rev3.py` chạy `model_sas_r3.py` đã khôi phục (`git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105/{SAS,_common,_common_020021,_shared,TOP5B_CORRECTIONS_20261108.md}` → `/tmp/ddrestore_w4sas`) NGUYÊN VĂN, chỉ bỏ assert md5 của `data/deposit_rate_vn_events.csv` (file đã append sự kiện sau 08/11; assert r = 13,5% vẫn giữ). **CONTROL:** tái lập headline r3 31.658 (assert). Chạy 2 lần: `run1.txt` = `run2.txt` md5 `71b97115…`; `model_sas_rev3_out.json` md5 `ab6617b6…`.
- **Nguồn số mới:** OCR thuyết minh BCTC gốc Q3/2026 + soát xét H1/2026 (`src_ocr/README.md`, đối chiếu tổng). Không có BCTC mới hơn Q3/2026 (Q4 hạn 31/01/2027). BCTC năm 2025 đã kiểm toán: có (DD 26/10) ⇒ `audited_fy_missing=false`.
- Mù giá: mô hình không đọc giá/ADV mới; giá 34.200 (06/11) + CK kế thừa r3 chỉ dùng cho nhãn ở §6.

## 0. Kết luận

**TÂM (base rev3, r 13,5%, D4 RONIC = Ke, sau CK 5 tỷ 5,93%): 27.477 đ/cp — vùng P10–P90 22.430–32.420** (trước CK 29.208; P50 27.384). Δ so với r3: **−13,21%**.
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 29.113 đ/cp (+5,95% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (N hiệu dụng thấp, 1.99)** — phân vị [fade 2, hold 2], 118 tháng, N hiệu dụng ≈ 2.0 ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=2.36)
Tâm kỳ vọng điều chỉnh: 26.803 đ/cp (dải 25.459–28.287; −2,45% so với tâm base); căn cứ 4 hạng mục bậc B/C+ (N0 đỉnh biên −, phải thu DH dự án −, thuế GTGT/VLĐ +, mùa vụ Q4 +) — chi tiết `ADJ_CENTER.md`

- Thay đổi base so với r3 (chỉ 2): **B1 D4** TV₂₀₂₇ = E₂₀₂₈/r (r3: E₂₀₂₈/(r−g), g 2–4%, không trích tái đầu tư) ⇒ −4.232 đ; **B2** cộng lãi tiền gửi Q4/2026 (lãi Q3 10,45 tỷ × 0,8 × 0,883, chiết khấu 55 ngày = 7,24 tỷ) ⇒ +51 đ (đóng r3 §10.1).
- Nhãn (sau khoá; §6): ở cỡ 5 tỷ **TRÊN vùng** (giá 34.200 > P90 32.420); cỡ sleeve 40 tr TRONG sát mép trên (P90 34.279). Luật 4 KHÔNG đạt.
- Cờ ĐỈNH LỢI NHUẬN: đã định lượng (§3). NPM 23,1% của 9T/26 GỒM cổ tức đầu tư 140,6 tỷ + lãi tiền gửi — mô hình KHÔNG đưa thu nhập tài chính vào N0. Biên VẬN HÀNH (LNTT − TC ròng)×0,8/DT = **15,42%** (9T/26) vs **12,57%** (9T/25) ⇒ N0 cao hơn mức 9T/25 khoảng 22,7%, không phải +60%.

## 1. Bảng thay đổi

| # | Luật / hạng mục | r3 | rev3 | Δ tâm sau CK |
|---|---|---|---|---|
| 1 | D4 terminal RONIC = Ke | E/(r−g), g {2;3;4}% ⇒ RONIC ngầm ∞ | TV = E₂₀₂₈/r (lưới 45 ô: Δ × N0 × r) | −4.232 (31.658 → 27.426) |
| 2 | Lãi Q4/26 trên tiền gửi | bỏ trống (§10.1) | +7,24 tỷ | +51 |
| 3 | E15 / dải Ke / E16 | chưa có | §0, §2 | 0 |
| 4 | Hạng mục mở r3 §9 | chưa kiểm | đọc thuyết minh: phải thu DH, thuế GTGT, bên trả cổ tức, HTK (§3) | 0 ở base (E17) |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình rev3, chỉ đổi r
r tại neo 03/11 = 13,5% (lãi huy động 12T hiệu dụng 7,40% `cctg_12m(2026-11-02)`; đọc lại 25/11 vẫn 7,40%, last_update 16/11) ⇒ Δ = 0. β = 1 (giả định).

| r | Tâm sau CK | Δ |
|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 29.113 | +5,95% |
| 12,5% (−100bp) | 28.819 | +4,88% |
| 13,0% (−50bp) | 28.122 | +2,35% |
| 13,4% (đầu trên dải Ke) | 27.602 | +0,46% |
| **13,5% BASE** | **27.477** | 0 |
| 14,0% (+50bp) | 26.879 | −2,18% |
| 14,5% (+100bp) | 26.322 | −4,20% |

[LUẬT, chỉ hiển thị] Nếu giữ RONIC ngầm ∞ của r3 trên base rev3: 31.709 (+15,40%) — bị D4 cấm vì moat NARROW.

## 3. Hạng mục mở r3 §9 — đã đọc thuyết minh (nguồn `src_ocr/`)
1. **Phải thu dài hạn 242,0 tỷ (V.5b)** — KHÔNG phải ký quỹ mặt bằng: ký quỹ 14,3; còn lại **227,8 tỷ là tiền ứng cho dự án đứng**: ứng đền bù GPMB khu du lịch sinh thái Bắc Vũng Bàu (Phú Quốc) 162,4 · vốn góp BCC Tracimexco 30,0 · BCC Nhà Phú Nhuận 16,7 (suy từ tổng; OCR hỏng) · phí cấp GCN QSDĐ 13,0 · ứng đền bù KS Sasco Nha Trang 5,6. Số cuối quý = đầu năm (không thu hồi trong 9T). Base giữ theo sổ (V4a: dự án NPV 0 tại giá sổ); rủi ro ⇒ E17 #2 (tiền lệ: LD Nhà Việt ~292 tỷ trích ~251 tỷ = 86%; thuyết minh 23 xoá sổ Viethaus).
2. **Thuế GTGT được khấu trừ (mã 162)**: 199,4 (31/12/25) → 226,5 (30/06) → 240,6 (30/09) — tăng liên tục, chưa thu hồi. r3 coi là VLĐ vận hành (giá trị 0 trong N0). Chiều lên ⇒ E17 #3.
3. **Bên trả cổ tức đầu tư** (đóng WARNING r3 §6 mục 3): H1/26 nhận 92,8 tỷ, gần hết từ **CTCP TM Xăng dầu Tân Sơn Nhất** (liên kết 38,03%, giá gốc 149,4 tỷ) — KHÔNG thuộc nhóm IPP; Q3/26 thêm 47,8 tỷ. Cổ tức 9T/25 chỉ 9,6 tỷ ⇒ 2026 bất thường. Base giữ đầu tư DH theo sổ 253,8; vốn hoá cổ tức ⇒ độ nhạy C hai chiều (§4).
4. **Đỉnh lợi nhuận** — biên vận hành 15,42% (9T/26) vs 12,57% (9T/25). Cơ chế có số: giá vốn hàng miễn thuế Q3 150,6 tỷ vs 224,2 tỷ (DT 224,5 vs 285,8) — biên gộp miễn thuế 32,9% vs 21,6%; mua hàng từ IPP Group H1/26 0,5 tỷ vs H1/25 387,1 tỷ (ngừng mua qua IPP, tự nhập: HTK hàng hoá 57 → 191 tỷ). Một phần là cấu trúc (đổi nguồn hàng), nhưng Chủ tịch nói tự vận hành "không thể kéo dài" ⇒ có thể về mô hình đối tác. V5 cấm ép biên về TB ngành ở pha dự báo ⇒ base giữ N0; rủi ro neo vào biên CỦA CHÍNH SAS 9T/25 ⇒ E17 #1.
5. **HTK 204,3 tỷ** (đầu năm 68,9) chưa trích lập — C.
6. **Thầu Long Thành** — đã trong lưới Δ (−55…+5%), không thêm.
7. **Truy thu tiền thuê đất** — đã hạch toán Q4/2025; thuyết minh thuế q3_32: phải nộp tiền thuê đất 27,4 (đầu năm) → phát sinh 22,0 → đã nộp 38,6 → còn 10,7 tỷ (trong VLĐ) ⇒ không thêm khoản. **20 lô đất** — pháp lý, WARNING (chưa kiểm bản gốc). Soát xét H1/2026 Deloitte (14/08/2026): kết luận chấp nhận, không đoạn nhấn mạnh (h1_09).
8. **Cổ tức tiền 2026 chưa GDKHQ**: tìm 25/11 chỉ thấy đợt 2/2025 4.024 đ/cp (GDKHQ 03/08/2026, đã trả trong 9T, 537,0 tỷ) ⇒ không có điều chỉnh cơ học.

## 4. Tâm kỳ vọng điều chỉnh (E17) — sau skeptic r1 (PREREG_rev3 §B + `PREREG_rev3_addendum_r1.md`, khoá trước khi chạy)
`calc/calc_adj_rev3.py` (chạy 2 lần trùng byte `adj_run1.txt` = `adj_run2.txt` md5 `7491a6a3…`; out `calc_adj_rev3_out.json` md5 `901bedf0…`). Tổ hợp chạy qua MÔ HÌNH.

| # | Hạng mục | Bậc | p [dải] | m (% tâm) [dải m] | p×m |
|---|---|---|---|---|---|
| 1 | N0 về biên vận hành 9T/25 (12,57% vs 15,42% ⇒ N0 −18,49%) | B, nhánh ngược | 0,35 [0,15;0,55] | −11,69% [−5,85; −11,69] | −4,09% |
| 2 | Phải thu DH dự án đứng 227,8 tỷ — giá trị thời gian (cận bảo thủ 1 năm; 3 năm) | C+ | 0,50 [0,25;0,75] | −0,69% [−0,69; −1,85] | −0,35% |
| 3 | Thuế GTGT khấu trừ / VLĐ ròng ngoài tiền 130,3 tỷ thu hồi được | B, nhánh ngược | 0,35 [0,15;0,55] | +3,34% [+1,67; +3,34] | +1,17% |
| 4 | Mùa vụ Q4: DT Q4/TB Q1–Q3 = 1,104 / 1,118 / 1,252 (2023–25) ⇒ N0 × (3+s)/4 | B, nhánh ngược (LN Q4/23 < TB) | 0,35 [0,15;0,55] | +2,50% [+1,64; +3,98] | +0,87% |
| | **Σ** (tuyến tính −2,40%; mô hình tổ hợp) | | | | **−2,45%** |

**Tâm kỳ vọng điều chỉnh 26.803 đ/cp; dải 25.459–28.287** (cực trị p×m từng hạng mục, qua mô hình).
Độ nhạy C / LUẬT (không vào tâm, % so với tâm base): q trượt thầu Long Thành — Δ −10pp −7,45% (25.430) / +10pp +7,45% (29.524) · hợp đồng thuê hữu hạn ~27 năm (ước lượng từ cam kết thuê h1_45) −1,72% (27.004) · biên vận hành ~10% (ước lượng) −22,23% (21.370) · vốn hoá cổ tức đầu tư 12,8 / 71 / 100 tỷ/năm −4,36% / +5,43% / +10,31% · HTK −10% −0,52% · bỏ toàn bộ phải thu DH −6,21% · [LUẬT] E15 +5,95%; chặt-3C biên ngành (ADDENDUM_5F_r1, nền r2) 17.438 — V5 cấm, chỉ hiển thị.

## 5. Soát luật B5
- **D3 capex tuân thủ:** không nhận diện hạng mục chi bắt buộc-không-tạo-doanh-thu; XDCB 118,0 + BĐS ĐT 32,2 theo sổ (V4a). Truy thu tiền thuê đất = pháp lý (WARNING), không phải capex. Cam kết vốn TSCĐ đã ký chưa hạch toán 103,5 tỷ (30/06, h1_45) = V4a NPV 0; khấu hao trong N0 thay capex duy trì. Cam kết thuê không huỷ ngang 30/06: ≤1 năm 29,3 · 2–5 năm 108,8 · >5 năm 642,1 tỷ ⇒ hợp đồng thuê dài hạn (≈27 năm, ước lượng) — độ nhạy §4. Cần kiểm chứng: thời hạn/điều khoản hợp đồng khai thác mặt bằng TSN với ACV (chưa có văn bản).
- **D4:** áp (B1). **V1:** r 13,5%, Δ 0. **E15/E16:** §0.
- **V3:** kế thừa r3 (ADV250 06/11 0,61 tỷ, σ 2,07%): CK 5 tỷ 5,93% (ngoài vùng hiệu chỉnh, 823% ADV); 40 tr 0,53% ⇒ tâm 29.053, P90 34.279. Free float ~4,4%.
- **V5:** NARROW LOCATION/REGULATORY, `moat_durable=false`, rủi ro số 1 = đồng hồ Long Thành (03/2027–03/2028) — ADDENDUM_5F_r1 (07/11, <12 tháng) tái dùng. Kiểm nhanh 25/11: biên vận hành tăng có cơ chế nguồn hàng (§3.4) — KHÔNG phải bằng chứng hào bền (ROIC đỉnh chu kỳ ≠ hào).
- **V6 (chỉ hiển thị):** `dd_blend_20261111/out/apply_dd.csv` (as-of 10/11, khôi phục `3750ca176^`): V_ngắn 54.673 / V_dài 42.122, D = 0,261 < ln2 ⇒ không cờ. Caveat: r của engine dd_blend, NI chuẩn hoá 463,9 tỷ gồm thu nhập TC; không chạy lại ở 13,5%/D4; chưa qua tiêu chí khoá trước, chỉ theo dõi.
- **V7:** không dùng snapshot vĩ mô. **V8:** đề xuất ≤2% NAV nếu user xét (free float 4,4%, ADV 0,61 tỷ; 40 tr ≈ 6,6% ADV250) — hiện không có lý do mua (§6).

## 6. Sau khoá — nhãn (giá 34.200, BQ 06/11/2026, kế thừa r3)
- Cỡ 5 tỷ: giá/tâm +24,5%; 95,6% trọng số kết cục dưới giá ⇒ **TRÊN vùng (>P90 32.420)**. r3: TRONG (nửa trên).
- Cỡ sleeve 40 tr: tâm 29.053, P90 34.279 ⇒ TRONG sát mép trên.
- Luật 4 (giá < 0,85×tâm = 23.355): KHÔNG đạt. §2.5 fear-buy: không đủ điều kiện.

## 7. WARNING (giữ r3 §6, cập nhật mục 3)
Mặt bằng ACV giao không đấu thầu (KL TTCP 2017), truy thu tiền thuê đất 2015–2024; 20 lô đất (chưa kiểm bản gốc); bên liên quan IPP 46,5% (nay gần như ngừng mua hàng qua IPP; phải thu IPP 194 tỷ đã thu); bên trả cổ tức = Xăng dầu TSN (liên kết, ngoài nhóm IPP) — ĐÓNG; free float 4,4%; TGĐ mới 08/2026. Pháp lý chỉ WARNING.

## 8. Mốc đổi nhận định (hai chiều)
| Mốc | Ngày | Lên | Xuống |
|---|---|---|---|
| BCTC Q4/2026 + năm 2026 kiểm toán | 31/01/2027 – 03/2027 | biên vận hành Q4 ≥ 15% ⇒ #1 p 0,35→0,15 (tâm_adj +2,34%) ; GTGT được hoàn ⇒ #3 bậc A p 0,9 (tâm_adj +1,83%) ; Q4 cao cả DT lẫn LN ⇒ #4 p→0,55 (+0,50%) | biên về ~12,6% ⇒ #1 p→0,55 (−2,34%) ; trích lập hết phải thu DH ⇒ bậc A thay #2 (−5,24%) |
| Thầu Long Thành | trước 03/2027 | trúng miễn thuế/phòng chờ ⇒ Δ +5…−10% | trượt ⇒ Δ −40…−55% |
| Đối tác vận hành miễn thuế mới (điều khoản) | chưa lịch | giữ biên tự vận hành | chia doanh thu ⇒ #1 bậc A |
| Cổ tức 2026 của Xăng dầu TSN | BCTC năm | đều ≥ 70 tỷ/năm ⇒ #4 thành B lên (m +5,43%; p 0,5 ⇒ tâm_adj +2,7%) | về ~10 tỷ ⇒ #4 B xuống (m −4,36%; p 0,5 ⇒ −2,2%) |

## 9. Phạm vi đề nghị cho phản biện (§E4, DD_GENERAL)
(i) D4 áp đúng chưa (TV = E₂₀₂₈/r có khớp value-driver với RONIC = Ke); (ii) đỉnh lợi nhuận: N0 = 9T/26 năm hoá có phải đỉnh không; E17 #1 nhánh p "ngược" có hợp lý; (iii) cân bằng hai chiều: #3 thuế GTGT, #4 cổ tức đầu tư; (iv) thiếu hạng mục: phải thu DH dự án, HTK, nghĩa vụ mặt bằng ACV, lương/phải trả NLĐ 141 tỷ trong VLĐ; (v) bảng độ nhạy r.

## Phụ lục E (nội bộ) — phản biện và đính chính
- `skeptic/r1.json`: **INCONCLUSIVE (medium)**, 1,09 USD, report_md5 `39d46756…` (bản trước đính chính). Cơ học: skeptic tự tính tâm điểm giữa 29.159/≈27.430 vs 29.208/27.477 (chênh do lồi theo r) — khớp; D4 đúng; biên vận hành khớp; số CP khớp.
- Áp: E17 #2 bỏ hệ số 86% (tiền lệ khác bản chất) → C+ giá trị thời gian; E17 #3 bù trừ VLĐ (130,3 thay 240,6); thêm #4 mùa vụ Q4 (chiều lên); thêm độ nhạy q Long Thành ±10pp, hợp đồng thuê hữu hạn, biên 10%; đóng truy thu thuê đất + ý kiến soát xét (§3.7); cam kết vốn/thuê (§5).
- Bác: "OCR cột Q3 sai" — §3.4 dùng thuyết minh 24/26 (q3_35), tổng DT Q3 779,65 = BQ.
- Giữ (luật house, không vào Σ): trọng số lưới Δ Long Thành (q ngầm 0,5) là tham số r3 kế thừa — chỉ báo độ nhạy ±10pp; thời hạn hợp đồng ACV không có văn bản ⇒ C.
- Tâm base KHÔNG đổi (27.477, 0%), nhãn không đổi ⇒ không phản biện lại (B2); `skeptic_final` = REFUTED_OPEN (không tự nâng).
