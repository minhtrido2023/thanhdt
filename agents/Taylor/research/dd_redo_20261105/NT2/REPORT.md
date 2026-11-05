# DD REDO — NT2 (Điện lực Dầu khí Nhơn Trạch 2, HOSE) · mùa BCTC Q3/2026 · job `Taylor_20261105_014133` · 05/11/2026

> Chỉ NGHIÊN CỨU, không khuyến nghị. Số định giá: `calc/model.py` → `calc/model_out.txt/json`; `SUMMARY.json` sinh tự động (`_common/summary.py`).
> **Nguồn BCTC (mới tải, gốc từ website công ty)**: `src/Q3_2026_hopnhat_va_giaitrinh.pdf` — CBTT 1394/CPNT2-TCKT 19/10/2026, https://pvpnt2.vn/... (tr.1–3 công văn + giải trình dạng text; tr.4–30 scan, đọc từ ảnh `img/p06–p09` = BCTC in tr.2–5). Đây là **BCTC riêng mẫu B01a-DN** — NT2 không có công ty con nên không có bản hợp nhất. Chưa đọc thuyết minh tr.7–26.
> **Thiếu sector read** cho nhiệt điện khí (registry chỉ có `sector_read_power_consulting_20261028.md` — tư vấn điện, không áp dụng).
> **Giá 22.650 đ, đóng cửa 04/11/2026** [BQ `tav2_bq.ticker`] — **đã trừ cổ tức 1.000 đ (GDKHQ 29/10/2026**: Price 24.050 → 22.900 [BQ]). Đơn vị tỷ đồng.

## 0. Kết luận

| | đ/cp |
|---|---|
| Tâm TRƯỚC chiết khấu thanh khoản (kỳ vọng 25/50/25) | **22.837** |
| Chiết khấu thanh khoản (vị thế 5 tỷ) | 0,92% |
| **Tâm SAU chiết khấu thanh khoản** | **22.628** |
| P10 / P50 / P90 SAU (lưới n=45) | **17.594 / 22.856 / 27.529** |
| P10 / P90 TRƯỚC | 17.757 / 27.784 |
| Giá 22.650 so tâm / P10 / P90 | +0,1% / +28,7% / −17,7% ⇒ **TRONG vùng, ngay tâm** |

Giá đang ≈ giá trị kỳ vọng: không rẻ, không đắt. Tâm cũ 25.400 ⇒ mới **−10,9% (>10%)** — nguyên nhân ở Phụ lục (cổ tức đã chia + r + thu nhập tài chính theo BCTC gốc).

## 1. Giả thuyết (giữ từ DD 26/10, kiểm lại bằng BCTC gốc)
- LN Q3 tăng do sản lượng/Qc + khấu hao giảm, không do NT3&4 (thuộc POW): **ĐÚNG** — giải trình tr.2–3: LNST Q3 418,6 (+95,4%), LN gộp điện +285,2 (+139%); KH 9T **114,8** so 515,8 cùng kỳ [LCTT tr.5] ⇒ máy chính khấu hao hết là **cấu trúc**.
- Giá khí là biến số chi phối: **sai cơ chế** — biến chi phối là Qc do EVN/NSMO phân bổ hằng năm (DD 26/10 §1).

## 2. Chất lượng lợi nhuận [KQKD tr.4]
| | Q3/2026 | Q3/2025 | 9T/2026 | 9T/2025 |
|---|---|---|---|---|
| DT thuần | 2.807,2 | 1.928,2 | 7.803,4 | 5.436,2 |
| LN gộp | 489,9 (17,5%) | 204,6 (10,6%) | 1.064,9 | 615,8 |
| DT tài chính | 92,4 | 48,8 | 226,4 | 118,1 |
| CP tài chính (gần hết lãi vay) | 27,0 | 16,0 | 68,4 | 48,1 |
| LNST | 418,6 | 214,2 | **906,4** | 577,4 |
- LN khác −2,6 (Q3) — không có khoản một lần lớn. Thuế TNDN Q3 20,1% (hết ưu đãi).
- Thu nhập tài chính ròng sau thuế năm hoá **168** (từ 9T) — tách khỏi LN vận hành để không đếm hai lần với net cash.
- **CFO 9T 1.256,2 > LNST 906,4 (1,39x)** [LCTT tr.5] — LN là tiền thật. Năm 2026 là năm thuận (El Niño, Qc cao) ⇒ LN 9T không phải mức chuẩn hoá.

## 3. Bảng cân đối / net cash thật [tr.2–3]
| Khoản | 30/09/2026 |
|---|---|
| Tiền (mã 110) + tiền gửi đáo hạn ngắn hạn (mã 123) | 11,8 + 5.362,3 = **5.374,2** |
| Vay ngắn hạn (mã 321); nợ dài hạn | −1.795,8; **0** |
| Cổ tức phải trả (mã 313, đã GDKHQ 29/10) | −297,1 |
| **Net cash thật** | **3.281,3 (11.398 đ/cp ≈ 50% giá)** |
- Vốn lưu động: phải thu KH 4.252,0 − phải trả NB (PV Gas) 2.637,4 − chi phí phải trả 777,4 = +837 — phụ thuộc lịch thanh toán EVN; **không cộng** vào giá trị. Phải thu tăng 482 từ đầu năm (≤ ngưỡng cảnh báo 5.000 của DD cũ).
- VCSH 5.421,4; quỹ đầu tư phát triển 791,2 (tăng từ 226,1 — trích từ LN, gắn kỳ vọng NT5).

## 4. Ghi nhận doanh thu
Bán điện theo PPA với EVN/EPTC: phần Qc giá hợp đồng (có pass-through nhiên liệu), phần phát vượt bán giá thị trường (FMP). Không có backlog kiểu hợp đồng xây dựng; "backlog" = thời hạn PPA/GSA ~2036 (1 nguồn — mở).

## 5. Cổ đông, room, thanh khoản [`_common/liq.py`]
- POW 59,4% (chi phối). Free float thực tế ~40% (ước lượng = 100% − POW).
- **ADV trung vị 18,0 tỷ/phiên** (250 phiên 03/11/2025–04/11/2026, BQ), σ ngày 1,74%. Vị thế 5 tỷ = 1,4–2,8 phiên ở mức tham gia 20–10% ⇒ chiết khấu 0,9% (1 tỷ 0,4%; 10 tỷ 1,3%).

## 6. ⚠️ WARNING pháp lý/quản trị — không loại, không trừ vào base
1. **Xung đột lợi ích với POW** (cần tiền: NT3&4 lỗ, nợ USD, không chia cổ tức tiền mặt 2026–2030): POW quyết chia cổ tức hay giữ tiền cho Nhơn Trạch 5. Theo luật 03/11, nếu tiền đi vào NT5 thì base ghi **NPV = 0** (giá sổ) — **không** coi là mất giá trị; rủi ro chỉ ở quản trị (cổ đông nhỏ không kiểm soát việc dùng 5,4 nghìn tỷ) và ở kịch bản tiêu cực khi có rủi ro CỤ THỂ (vd. chưa có cơ chế giá/Qc cho LNG).
2. Tiền gửi tập trung SHB (báo chí; chưa đối chiếu thuyết minh).
3. Lịch sử số liệu: soát xét H1/2026 giảm LNST ~94 tỷ; đính chính BCTC 2022; phạt thuế 10,6 tỷ (2020); TTCP QHĐ VII (lịch sử). Không có vụ việc đang mở chạm tài sản lõi.

## 7. Định giá — net cash + DCF dòng tiền vận hành CÓ THỜI HẠN
**r** = 13,5% + β·(lãi huy động 12T hiệu dụng − 7,40%), β=1 (giả định). Lãi huy động hiệu dụng 04/11/2026 = **7,40%** (`deposit_rate_vn.effective_deposit_rate`: CCTG 12M 02/11/2026; Big-4 6,8%) = điểm neo ⇒ **r = 13,5%**, Ke nội địa, không CRP. (Dòng tiền có thời hạn — dùng r chung theo yêu cầu job; không có terminal Gordon.)
Giá trị = net cash 3.281,3 + PV(LNST chuẩn hoá − 168) trong 10 năm; giá trị sau 2036 = 0 (FCF ≈ LNST vận hành vì khấu hao còn ~153/năm ≈ capex duy trì; capex 9T chỉ 2,5).

| Kịch bản LNST chuẩn hoá/năm (ước lượng) | P | Neo | Trước CK TK | Sau CK TK |
|---|---|---|---|---|
| Xấu 400 | 0,25 | năm Qc thấp như 2024 (LN 83) + khấu hao đã hết (~+320) | 15.677 | 15.533 |
| Cơ sở 800 | 0,50 | gần BSC 2027 767 / VDSC [CTCK, DD 26/10] | 23.068 | 22.856 |
| Tốt 1.150 | 0,25 | lặp lại 2026 (9T 906 + Q4) | 29.536 | 29.264 |
| **Kỳ vọng** | | | **22.837** | **22.628** |

Khoản giảm trừ trong base: **không có** (NT5 = NPV 0; giá trị sau 2036 = 0 là giả định thời hạn, đưa vào lưới/độ nhạy: 8/12/15 năm ⇒ tâm sau CK 21.345/23.623/24.714).
**Lưới P10–P90** (n=45): LNST chuẩn hoá {450; 625; 800; 975; 1.150} (0,1/0,2/0,4/0,2/0,1) × thời hạn {8; 10; 12} năm × r {12,5; 13,5; 14,5}% (1/4–1/2–1/4).
Đối chiếu: giá trừ net cash = 11.252 đ/cp ⇒ **5,1x** LNST vận hành cơ sở.

## 8. Độ nhạy r theo lãi huy động (tâm trước CK)
| Δ lãi huy động | β=1,0 | β=0,5 |
|---|---|---|
| −100bp | +466 đ (+2,0%) | +230 đ (+1,0%) |
| −50bp | +230 đ (+1,0%) | +114 đ (+0,5%) |
| +50bp | −222 đ (−1,0%) | −112 đ (−0,5%) |
| +100bp | −438 đ (−1,9%) | −222 đ (−1,0%) |

## 9. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)
| Mốc | Ngày chấm | Lên | Xuống |
|---|---|---|---|
| Qc 2027 được phân bổ (EVN/BCT) | ~31/12/2026 | Qc 2027 ≥ 2026 ⇒ LNST chuẩn hoá dịch về 1.000+ ⇒ giá trị tại LNST 1.000: 26.518 (sau CK; `val(1000)`) | Qc giảm mạnh (năm La Niña/thủy điện tốt) ⇒ LNST 450–625 ⇒ 16.448–19.652 (sau CK) |
| BCTC Q4/2026 (~20/01/2027) | 31/01/2027 | LNST Q4 ≥ 150 + CFO dương | lỗ Q4 + phải thu EVN > 5.000 |
| ĐHĐCĐ 2027 (dự kiến 4/2027) | 30/04/2027 | cổ tức tiền ≥ 1.500 đ hoặc gia hạn PPA/GSA có văn bản ⇒ thêm 2 năm ⇒ tâm 23.623 (+995 đ) | dùng phần lớn tiền cho NT5 khi chưa có cơ chế giá LNG ⇒ nâng WARNING, thêm kịch bản tiêu cực có xác suất |
| Thời hạn PPA/GSA xác nhận bằng BCTN/thuyết minh | khi có | > 2036 ⇒ nhánh 12–15 năm | < 2036 ⇒ nhánh 8 năm ⇒ 21.345 (−1.283 đ) |

## Phụ lục — cái gì ĐỔI so với DD 26/10 và vì sao
| Mục | DD 26/10 | Redo 05/11 | Lý do |
|---|---|---|---|
| Nguồn BCTC | báo chí trích | **BCTC gốc** CBTT 19/10 (pvpnt2.vn) | skill bước 2 |
| r | Ke 12% (độ nhạy 14%) | **13,5%** neo lãi huy động 7,40% | luật 03/11 |
| Net cash | 3.578 (chưa trừ cổ tức phải trả) | **3.281** (trừ 297,1 cổ tức đã GDKHQ 29/10) | đọc BS gốc; giá cũ là giá cum-div |
| Thu nhập TC ròng sau thuế | 129 | **168** (năm hoá 9T BCTC gốc) | số gốc |
| CK thanh khoản | không | 0,92% (5 tỷ) | luật 03/11 |
| NT5 | "loại khỏi mọi book" nếu dùng tiền cho NT5 | NPV 0 ở base, chỉ WARNING quản trị | luật dự án mới 03/11 |
| Vùng | 3 kịch bản 17.800/25.600/32.500 | P10–P90 lưới 17.594–27.529 | không dùng min/max |
**Cầu tâm (đo bằng model.py)**: 25.360 → −1.032 (cổ tức) −711 (r 12→13,5%) −729 (thu nhập TC 129→168) ≈ 22.890, còn −50 do làm tròn/quy ước chiết khấu v1 → 22.837 trước CK → −209 CK thanh khoản → **22.628**. Lệch −10,9% so tâm cũ, nhưng so trên cùng cơ sở ex-div (25.400 − 1.032 ≈ 24.370) thì −7,1%.

Giới hạn: mọi kịch bản LNST là ước lượng; thời hạn PPA 1 nguồn; chưa đọc thuyết minh; chưa qua fundamental-skeptic (Mike chạy).
