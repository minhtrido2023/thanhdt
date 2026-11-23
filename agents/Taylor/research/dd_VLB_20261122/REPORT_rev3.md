# DD — VLB (CTCP Xây dựng và SX VLXD Biên Hòa, UPCoM) · rev3 · 23/11/2026 · job `Taylor_20261123_001052`

> Bản rev3 dựng lại theo verdict skeptic r1 (INCONCLUSIVE, 22/11, `skeptic/r1.json`). KHÔNG ghi đè rev trước
> (`REPORT.md` = r2 nội bộ; `investor_report/VLB_DD_investor_report_20261122.md` = bản skeptic r1 đã đọc).
> Chỉ là nghiên cứu: không khuyến nghị, không đặt lệnh.
> Mô hình: `model/dcf_vlb_r3.py` (md5 `affb2d84af055ff9eeb6163bf2809e9a`) · output `model/output_r3.txt`.
> File khoá giả định: `assumptions_VLB_r3.json` (md5 `bedb196bd81a6db23cc2087a456b14d0`). `dd_assumptions_lint` cho 0 vi phạm, chỉ có ghi chú D5.
> Nguồn: [Q3 p.x] = `src/BCTC_Q3_2026.pdf` · [H1 p.x] = `src/BCTC_BanNien_2026.pdf` · [NQ p.x] = `src/nhan_su_0617.pdf`
> · [BV26 p.x] = `src/BVSC_VLB_update_202602.pdf` · [BV25 p.x] = `src/BVSC_VLB_initiation_202503.pdf` · [FP p.x] = `src/FPTS_VLB_update_20260406.pdf`.
> **Mù giá:** mọi giả định giá trị (đời mỏ, LN, r, kịch bản) được khoá trước bước so giá ở §8. Giới hạn: rev trước đã có giá 20/11, nên tính
> mù trong rev này là theo quy trình (giả định đổi vì có nguồn mới về giấy phép), không phải vì người viết không biết giá. Ghi rõ để skeptic soi.

## 0. Kết luận

- **Tâm giá trị** (kỳ vọng trọng số 3 kịch bản, sau chiết khấu thanh khoản Q = 5 tỷ):
  - **45.300 đ/cp** theo cơ sở 30/9/2026.
  - **42.800 đ/cp** theo cơ sở ex-div, sau khi trừ cổ tức tạm ứng 2026 2.500 đ (GDKHQ 19/11/2026). Đây là cơ sở so với giá và ghi sổ.
  - So với r2: **48.735 → 42.800 (−12,2%)** cùng cơ sở ex-div.
- **Vùng** (ex-div, sau chiết khấu): xấu **32.084** · cơ sở **43.537** · tốt **52.042**.
- **Nguyên nhân chính khiến tâm giảm:** có bảng giấy phép từng mỏ [BV26 p7]. Giấy phép Tân Cang 1 và Thạnh Phú 1 hết hạn **1/2038**, Thiện
  Tân 2 hết **8/2041**, Soklu 2 hết **11/2031**, Soklu 5 hết **8/2029**. Như vậy đời mỏ bình quân theo tỷ trọng lợi nhuận là **11,2 năm**,
  không phải 14 năm như r2 (r2 suy đời mỏ từ trữ lượng báo chí). Trữ lượng không phải ràng buộc chặt: hạn giấy phép đến trước, trừ Thiện Tân 2.
- **Lợi nhuận gốc giảm 330 → 310 tỷ** để xử lý điểm skeptic nêu: 330 nằm trên mức chuẩn hoá. 310 là trung điểm của LN lõi năm 2025 (264,8)
  và LN lõi 12 tháng gần nhất (357,3, ước lượng), cả hai đã loại lãi tiền gửi và thu nhập khác.
- **Kịch bản tốt** không còn ghép "sản lượng cao hơn + đời dài hơn": các mỏ đã chạy sát công suất giấy phép [FP p4]. Kịch bản tốt bây giờ là
  **gia hạn GP Thạnh Phú 1 tới 7/2042**, tức hết hạn thuê đất theo QĐ 1537/QĐ-UBND.
- **Moat NARROW / LOCATION** (tái dùng tag 2026-06-05). Đồng hồ cắt hào rõ hơn: phần lớn giấy phép hết 1/2038.
- **Pháp lý:** chỉ ở mức WARNING (tiền cấp quyền từng bị đảo chiều 2022↔2026; rà soát Soklu; đất theo Kiểm toán NN). Không đưa vào base.
- **`audited_fy_missing = true`:** BCTC 2025 đã kiểm toán vẫn KHÔNG tải được (§7). Chỉ có số LNTT/LNST 2025 đã kiểm toán, lấy từ NQ ĐHĐCĐ 2026.

## 1. Đính chính so với rev trước (từng hạng mục skeptic r1 → xử lý)

Phân loại: **(a)** = định lượng, đưa vào base (có nguồn độc lập) · **(b)** = chỉ đưa vào kịch bản/độ nhạy · **(c)** = không kiểm chứng được, ghi ảnh hưởng ước lượng.

| # | Hạng mục skeptic r1 | Xử lý rev3 | Loại | Tác động |
|---|---|---|---|---|
| 1 | Bảng giấy phép (số GP, hạn, công suất, cote) TP1/TT2/TC1 vắng | Tìm được bảng 5 mỏ [BV26 p7, nguồn "VLB, Sở Xây dựng tỉnh Đồng Nai, BVSC tổng hợp"]: công suất 1,5/1,5/1,8/0,4/0,5 tr m³/năm; **hạn TC1 1/2038, TT2 8/2041, TP1 1/2038, SK2 11/2031, SK5 8/2029**; cote −80 m; trữ lượng "hết 2023" [BV25 p5]. Đời từng mỏ = min(hạn GP, trữ lượng ÷ sản lượng) | (a) | Đời bình quân 14 → **11,2 năm**; tâm −12% (gộp các điều chỉnh) |
| 1b | Số hiệu GP và văn bản gốc | Vẫn KHÔNG có số GP hay bản quét. Bảng trên là **bán-sơ cấp** (CTCK tổng hợp từ VLB + Sở XD), không phải báo chí | (c) | Nếu hạn thật khác: mỗi ±1 năm hạn TC1+TP1 ≈ ±4% cơ sở (ước lượng theo độ nhạy TP1 +4,5 năm = +4,0%) |
| 2 | Tân Cang 1: >22 ha "hết hạn 2/2025" vẫn đếm đủ trong base | Bảng GP 2/2026 ghi TC1 **63 ha, hết 1/2038** [BV26 p7], tức còn hiệu lực. Ràng buộc thật của TC1 là **cote −80 m sắp chạm đáy + đất bóc tầng phủ chưa được phép tiêu thụ** [FP p4]. Đời TC1 trong base là 11,25 năm (theo hạn GP); trữ lượng cho 13,5 năm | (a)+(b) | Độ nhạy: trữ lượng TC1 −20% ⇒ **−0,5%** (vì hạn GP đến trước). Phần 22 ha báo chí nêu nhiều khả năng là diện tích ngoài GP hiện hành — **không kiểm chứng được** (c) |
| 3 | BCTC 2025 kiểm toán (ý kiến, thuyết minh GP/tiền cấp quyền) chưa đọc | Đã thử: website bbcc.com.vn (mục CBTT chỉ còn tin 2026; 8 slug đoán đều 404-mềm), 24hmoney, vietstock, FPTS, WebSearch ×4. **Không có PDF.** Có số kiểm toán từ NQ ĐHĐCĐ 2026: **LNTT 376,993 · LNST 301,437 tỷ**, kiểm toán A&C [NQ p2] | (c) | `audited_fy_missing=true`. Ý kiến kiểm toán 2025 chưa biết. Soát xét H1/26 của A&C chấp nhận toàn phần, không nhấn mạnh [H1 p7] ⇒ giảm (không loại) rủi ro ngoại trừ |
| 4 | Quyết định phê duyệt tiền cấp quyền (nghĩa vụ còn lại, R) | Không tìm được văn bản. Có: công thức NĐ 67/2019 = trữ lượng × giá tính × 0,9 × R 3% [BV25 p6]; 5 TB của Thuế Đồng Nai (29/5 và 02/6/2026) [Q3 p19] | (c) | Đảo chiều/khoản mới được mô hình bằng kịch bản xấu: khoản bù trừ = 0 (−150 tỷ ≈ −3.215 đ/cp cơ sở). Nghĩa vụ mới nếu cấp lại trữ lượng: chưa định lượng được |
| 5 | Capex cam kết / đền bù đất để khai thác trữ lượng còn lại | NQ ĐHĐCĐ 2026 có 14 nội dung, **không có hạng mục đầu tư hay đền bù** [NQ p2-4]. Capex 9T/26 1,13 tỷ [Q3 p6]. Đền bù đất mỏ đã trả 271,5 tỷ nằm trong CP trả trước DH, đang phân bổ [Q3 p18]. NQ HĐQT riêng lẻ: chưa đọc | (a) không có khoản ra mới; (c) phần NQ HĐQT | Base: không trừ thêm. Nếu phải đền bù mở rộng: chưa có số |
| 6 | Base LN 330 > mức chuẩn hoá (290/301) | Base **310** = trung điểm lõi FY25 **264,8** ((376,993 − DTTC 31 − khác 15) × 0,8; DTTC/khác từ [BV26 p2], lãi tiền gửi 30,1 [FP p5]) và TTM **357,3** (ước lượng, có op 9T/25 ước lượng). Lưu ý "290/301" của r2 gồm cả lãi tiền gửi; so cùng định nghĩa thì lõi FY25 là 264,8 | (a) | Cơ sở −20 tỷ ⇒ ≈ −2.170 đ/cp cơ sở. Độ nhạy: np1 265 ⇒ −10,3%; 290 ⇒ −4,6%; 357 ⇒ +10,8% |
| 7 | Kịch bản tốt ghép sản lượng cao + đời dài (mâu thuẫn trữ lượng cố định) | Bỏ giả định sản lượng cao vì mỏ đã sát công suất GP (TC1 ~97% [FP p4]; tổng tiêu thụ 2025 7,59 tr m³ thành phẩm ≈ công suất 7,9 [FP p2]). Tốt = LN 370 + **gia hạn TP1 tới 7/2042** (hạn thuê đất) | (b) | Tốt 56.214 trước CK (r2: 67.885) |
| 8 | Đời mỏ theo run-rate Q3 ≈ 13 năm, không phải 14 | Đã thay bằng ràng buộc GP: 11,2 năm bình quân | (a) | — |
| 9 | Khoản bù trừ 329 tỷ chiết khấu 13,5% là quá cao | Chiết khấu ở **lãi huy động 12T 7,4%** (khớp kỳ hạn). Rủi ro đảo chiều đã nằm riêng ở kịch bản xấu (= 0), nên không trừ hai lần. Mức sử dụng ∝ tỷ trọng 3 mỏ chính còn hoạt động | (a) | PV cơ sở 150,2 tỷ (r2: 119,4 @13,5%). Độ nhạy @13,5%: **−1,4%** tâm |
| 10 | Dư bù trừ khi hết đời mỏ tính bằng 0 | Base vẫn = 0. Dư bây giờ là **97,6 tỷ** vì đời ngắn hơn. Có được hoàn lại hay không: NĐ 193/2025 Đ139 k8 chỉ nói "bù trừ kỳ sau" | (c) | Nếu được hoàn khi đóng mỏ: **+802 đ/cp** (KHÔNG vào base) |
| 11 | Ký quỹ PHMT vượt dự phòng 22,7 tỷ chưa đếm | Đưa vào base: (38,88 − 16,22) = 22,66 tỷ nhận lại khi đóng mỏ (năm 11,25), PV @13,5% = **5,5 tỷ** [Q3 p16, p21] | (a) | +118 đ/cp |
| 12 | Phương án trích quỹ 12,4% | Giữ 14,84% (thực tế 2025 [NQ p1]) làm base; 12,4% là độ nhạy. NQ 2026: ĐTPT 10% (vẫn thuộc cổ đông), KTPL ≤ 3 tháng lương [NQ p3] | (b) | +2,1% |
| 13 | Soklu 2/5 "có dấu hiệu ngừng" (r2 §5) | **Đính chính:** cả hai đã được gia hạn (SK5 theo QĐ 473/QĐ-UBND, hoạt động lại từ Q3/2025 [FP p6]; hạn SK2 11/2031, SK5 8/2029 [BV26 p7]). Tỷ trọng 8,7% sản lượng 2025 | (a) | Đưa vào base theo hạn GP (đời 5,1 và 2,8 năm) |

## 2. Net cash thật 30/9/2026 — GIỮ r2 (skeptic r1 đã tính lại khớp)

812,584 (tiền 27,576 + HTM 785,008) − quỹ KTPL 107,466 − thuế phải nộp 61,748 − phần giá vốn của khách ứng trước 51,54 (76,938 × (1 − 33,0%))
− WC ròng 67,06 − khoản trích quỹ tạm 9T 35,93 = **488,84 tỷ = 10.463 đ/cp** [Q3 p2-3, p22]. Không vay. 20,5 tỷ HTM đang cầm cố bảo lãnh
[Q3 p15], tính đủ. Con số này đã gồm cổ tức tạm ứng 2026 2.500 đ/cp (≈116,8 tỷ, trả 17/12/2026).

## 3. Khoản 343,93 tỷ tiền cấp quyền: quyền bù trừ, không phải tiền mặt (giữ r2, đổi lãi chiết khấu)

- Ghi vào thu nhập khác Q2/26. Theo các TB của Thuế TP Đồng Nai (29/5 và 02/6/2026), khoản này được bù trừ vào nghĩa vụ tiền cấp quyền các kỳ sau
  [Q3 p19 V.17, p24 VI.6]. Thuế TNDN trên khoản này nộp bằng tiền.
- Số dư 30/9: **329,36 tỷ** (dòng 163). Tốc độ cấn trừ: **19,42 tỷ/năm** (dòng con 9,710 → 14,565 [H1 p30/Q3 p19]).
- rev3: chỉ cấn trừ khi 3 mỏ TC1/TP1/TT2 còn GP. PV @7,4% = **150,2 tỷ (3.215 đ/cp)**, dư **97,6 tỷ** khi hết đời (tính bằng 0).
- Rủi ro đảo chiều: tiền lệ 2022 phải nộp bổ sung >270 tỷ (báo chí). Mô hình hoá bằng kịch bản xấu = 0 (w 0,25).

## 4. Giấy phép, trữ lượng, đời mỏ (MỚI — thay r2 §4)

| Mỏ | Công suất GP (tr m³ ng.khối/năm) | Hạn GP | Trữ lượng (tr m³) | Tiêu thụ 2025 (tr m³ thành phẩm) [FP] | Khai thác ng.khối/năm (ước lượng) | Trữ lượng 30/9/26 (ước lượng) | Đời = min(hạn, trữ lượng) | Tỷ trọng LN |
|---|---|---|---|---|---|---|---|---|
| Tân Cang 1 | 1,5 | 1/2038 | 24,44 (hết 2023) | 2,43 | 1,500 (chặn ở công suất) | 20,3 | **11,25** (hạn) | 32,0% |
| Thạnh Phú 1 | 1,8 | 1/2038 | 37,13 (hết 2023) | 2,30 | 1,659 | 32,6 | **11,25** (hạn) | 30,3% |
| Thiện Tân 2 | 1,5 | 8/2041 | 24,23 (hết 2023) | 2,20 | 1,500 | 20,1 | **13,40** (trữ lượng) | 29,0% |
| Soklu 2 | 0,4 | 11/2031 | 2,30 | 0,29 (chia 4:5) | 0,212 | 2,0 | **5,08** (hạn) | 3,9% |
| Soklu 5 | 0,5 | 8/2029 | 1,72 | 0,37 | 0,265 | 1,4 | **2,83** (hạn) | 4,8% |

- Nguồn: [BV26 p7] (công suất, hạn, trữ lượng, cote −80 m; nguồn "VLB, Sở Xây dựng tỉnh Đồng Nai"); mốc "hết năm 2023" lấy từ [BV25 p5];
  tiêu thụ từng mỏ lấy từ [FP p4, p6]. Quy đổi thành phẩm/nguyên khối = 7,9/5,7 = 1,386 [FP p2]. Phép kiểm chéo độc lập: phí BVMT 9T 44,85 tỷ ⇒
  ≈ 9,95 tr tấn ≈ 5,56 tr m³ thành phẩm 9T [Q3 p19-21, p28]. Mức này khớp năm hoá ~7,4 tr m³, tức sát công suất GP.
- Tỷ trọng LN chia theo sản lượng 2025 (ước lượng: chưa có biên từng mỏ).
- **Đời bình quân theo tỷ trọng LN: 11,2 năm** (r2: 14). Sau 1/2038 chỉ còn Thiện Tân 2 (29%) tới ~2/2040.
- Thạnh Phú 1 còn **~13,8 tr m³** khi GP hết 1/2038, và đất thuê tới 31/7/2042 (QĐ 1537/QĐ-UBND, báo chí). Gia hạn GP để khai thác hết trữ lượng
  được Luật Địa chất & Khoáng sản 2024 / NĐ 21/2026 Đ63 cho phép về nguyên tắc, nhưng **chưa có văn bản** ⇒ chỉ vào kịch bản tốt.
- Độ nhạy: cơ sở + gia hạn TP1 tới 2042: **+4,0%**. Cơ sở + gia hạn cả 3 mỏ chính tới hết trữ lượng: **+8,7%**.

## 5. Vị thế cạnh tranh (5F) — TÁI DÙNG tag 2026-06-05 (<12 tháng), kiểm nhanh

`data/moat_tags.csv`: **NARROW / LOCATION**, ROIC_Min5Y 22,6%. Rủi ro số 1: giấy phép/trữ lượng hữu hạn. Giữ nguyên, không thưởng, không trừ.

Kiểm nhanh rev3:
- Đồng hồ cắt hào bây giờ có ngày cụ thể: **1/2038** cho 62% LN [BV26 p7].
- Soklu đã được gia hạn ngắn hạn (đính chính r2).
- Vị thế: 26% thị phần Đồng Nai [FP p2]; công suất mỗi mỏ cao nhất trong cụm (26–50% công suất cụm [BV25 p5]).
- **Kết luận: không đổi tầng.** Mô hình không có tham số moat. Đời mỏ hữu hạn, không có terminal.
- Độ nhạy NONE: cơ sở dùng LN lõi FY25 265 thay 310 ⇒ **−10,3%**.

## 6. Định giá (MÙ giá thị trường) — `model/dcf_vlb_r3.py`

**V1 — r:** 13,5% tại neo. Lãi huy động 12T hiệu dụng **7,4%** (cctg_12m 02/11; Big-4 online 6,8% 16/11; `deposit_rate_vn`,
last_update 16/11/2026) bằng mức tại neo ⇒ Δ = 0, r giữ **13,5%**. β = 1 (β 0,5 trong ngoặc).

| Lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| Tâm trước CK | 48.309 (+3,5%; β0,5 47.483) | 47.483 (+1,7%) | 45.924 (−1,6%) | 45.187 (−3,2%; β0,5 45.924) |

Dải Ke nội địa (D4, báo kèm): 12,3% ⇒ 48.648 (+4,2%); 13,4% ⇒ 46.845 (+0,3%).

**Kịch bản** (giữ trọng số r1/r2, không re-tune). Dòng tiền = LN vận hành × (1 − 14,84% quỹ) × tỷ trọng mỏ còn hoạt động. Không có terminal.
Thuế TNDN 20% đã nằm trong LN sau thuế.

| Kịch bản | w | LN năm 1 (tỷ, sau thuế, trước trích quỹ) | g | Đời | Bù trừ | PV vận hành | PV bù trừ | Ký quỹ | **đ/cp (30/9, trước CK)** |
|---|---|---|---|---|---|---|---|---|---|
| Xấu | 0,25 | 250 | 0% | theo GP | 0 (đảo chiều) | 1.171,0 | 0 | 5,5 | **35.645** |
| Cơ sở | 0,50 | 310 | 2% | theo GP | có | 1.572,4 | 150,2 | 5,5 | **47.448** |
| Tốt | 0,25 | 370 | 2% | TP1 tới 7/2042 | có | 1.973,4 | 161,0 | 3,1 | **56.214** |
| **Tâm kỳ vọng** | | | | | | | | | **46.689** |

**V3 — Thanh khoản** (sau khoá; `model/px_vlb.csv`):
- ADV trung vị 250 phiên 1,14 tỷ (68 phiên 0,92); σ 1,34%; spread CS 0,35%.
- Chiết khấu: d(1 tỷ) **1,43%** · d(5 tỷ, tham chiếu) **2,98%**. Thoát 5 tỷ ở 20% ADV mất 21,8 phiên.
- Free float thực ≈ 18,5% (Dofico 49,08%, KSB 21,95%, Hóa An 10,05% [Q3 p22]).

| Sau CK Q = 5 tỷ | Xấu | Cơ sở | Tốt | **Tâm** |
|---|---|---|---|---|
| Cơ sở 30/9/2026 | 34.584 | 46.037 | 54.542 | **45.300** |
| **Ex-div (−2.500, so với giá/ghi sổ)** | **32.084** | **43.537** | **52.042** | **42.800** |

**Độ nhạy khác** (tâm trước CK 46.689):
- Bù trừ chiết khấu @13,5% thay vì 7,4%: −1,4%.
- Quỹ 12,4%: +2,1%.
- Cơ sở g = 0: −5,4%.
- Cơ sở np1 265 / 290 / 357: −10,3% / −4,6% / +10,8% (so với cơ sở).
- Gia hạn TP1 tới 2042: +4,0%. Gia hạn 3 mỏ tới hết trữ lượng: +8,7%.
- TC1 trữ lượng −20%: −0,5%.
- Dư bù trừ được hoàn: +802 đ/cp.

**V6 (chỉ hiển thị):** V_ngắn (Gordon vô hạn, LN 310, g 2%, tái đầu tư 5%, + net cash) = 57.143; V_dài (mô hình hữu hạn, cơ sở) = 47.448;
D = 0,186 < ln2 ⇒ không có cờ. V_ngắn cao hơn vì Gordon ngầm giả định mỏ vô hạn — không áp được cho mỏ có hạn GP. Dòng C4/D2: không tính trong
rev3 ("chưa qua tiêu chí khoá trước, chỉ theo dõi").

**V4:** không có dự án tăng trưởng nào được công bố (NQ ĐHĐCĐ 2026), nên không cần NPV = 0. Capex tuân thủ duy nhất là hoàn nguyên môi trường:
đã trích dự phòng 16,22 tỷ, phần ký quỹ thừa 22,66 tỷ được thu hồi (§1 #11).

**V5:** 5F tái dùng (<12 tháng), §5.

## 7. Hạng mục không kiểm chứng được (ghi thẳng)

1. **BCTC 2025 kiểm toán**: không tải được (đã thử website công ty, 24hmoney, vietstock, FPTS, WebSearch). Ảnh hưởng: chưa biết ý kiến/đoạn nhấn
   mạnh về tiền cấp quyền. Soát xét H1/26 chấp nhận toàn phần. Nếu kiểm toán 2025 có ngoại trừ ⇒ HARD ABANDON (§9). Không định lượng vào tâm.
2. **Số hiệu và bản gốc giấy phép**: hạn/công suất/trữ lượng lấy từ bảng CTCP tổng hợp [BV26 p7], không phải bản quét GP. Trữ lượng là mốc
   cuối 2023. Ảnh hưởng ước lượng: ±1 năm hạn TC1+TP1 ≈ ±4% cơ sở.
3. **Quyết định phê duyệt tiền cấp quyền** (R, nghĩa vụ còn lại, nghĩa vụ mới nếu cấp lại trữ lượng): không có. Ảnh hưởng nằm trong kịch bản xấu.
4. **Dư bù trừ 97,6 tỷ có được hoàn hay không**: +802 đ/cp nếu được hoàn; base = 0.
5. **NQ HĐQT về đầu tư/đền bù**: chưa đọc (chỉ có NQ ĐHĐCĐ). Ảnh hưởng: chưa định lượng.
6. **Biên lợi nhuận từng mỏ**: chưa có; LN chia theo sản lượng.

## 8. Pha SAU KHOÁ — so giá

- Giá tham chiếu **48.100 đ** (20/11/2026, đã không hưởng cổ tức 2.500 đ từ 19/11; lấy từ entry sổ rev2, không truy vấn mới).
- **Giá/tâm ex-div = 1,12** ⇒ giá TRÊN tâm 12%, nằm trong vùng ±15% của tâm (36.380–49.220). Giá dưới cận tốt 52.042 và trên cơ sở 43.537.
- **Nhãn:** "Trong vùng hợp lý, nghiêng đắt". Giá đang hàm ý kịch bản giữa cơ sở và tốt, tức gia hạn GP Thạnh Phú 1 hoặc LN giữ quanh mức TTM.
- **Không đủ điều kiện vào sleeve:** ngưỡng 0,85 × tâm = **36.380 đ**.
- **Sizing V8:** chuẩn 2–4% NAV/mã. Thanh khoản ràng buộc: ở Q = 5 tỷ cần ~22 phiên để thoát (20% ADV). Mọi đề xuất >5 tỷ cần user duyệt riêng
  về rủi ro thoát lệnh. Hiện không đề xuất vào.

## 9. Mốc khoá trước + điều kiện đổi nhận định (CẢ HAI chiều) — khoá 23/11/2026 (rev3)

| Mốc | Ngày chấm | Ngưỡng |
|---|---|---|
| M1 BCTC Q4/2026 | ~20/01/2027 | Sản lượng đá Q4 ≥ 1,85 tr m³ **và** DT/m³ ≥ 215.000 đ |
| M2 Dòng con "tiền cấp quyền khai thác chính" [thuyết minh 17] | ~20/01/2027 | Cấn trừ ~4–6 tỷ/quý; không có TB phải nộp bổ sung |
| M3 BCTC kiểm toán 2026 (+ tải được 2025) | ~31/03/2027 | Chấp nhận toàn phần; không ngoại trừ/nhấn mạnh về 343,93 tỷ |
| M4 Hồ sơ gia hạn/điều chỉnh GP TC1/TP1 | bất kỳ CBTT | Có văn bản ⇒ đánh giá lại đời mỏ |

- **Đổi LÊN:**
  - Văn bản gia hạn GP TP1 tới ≥ 2042: +4,0% cơ sở. Gia hạn cả 3 mỏ tới hết trữ lượng: +8,7%.
  - Mỗi +10 tỷ LN vận hành cơ sở ⇒ ≈ +1.085 đ/cp cơ sở (+543 tâm; đo theo độ nhạy np1 290→310).
  - Xác nhận dư bù trừ được hoàn: +802 đ/cp.
  - Lãi huy động −100bp ⇒ +3,5%.
- **Đổi XUỐNG:**
  - TB truy thu hoặc huỷ khoản bù trừ ⇒ −3.215 đ/cp cơ sở (= HARD ABANDON nếu phải nộp bổ sung).
  - Rà soát/thu hồi GP lan sang 3 mỏ chính (HARD ABANDON).
  - Hạn GP thực tế sớm hơn bảng BVSC.
  - Sản lượng Q4 < 1,6 tr m³ (cầu Tân Cang giảm sau Long Thành GĐ1 [BV26 p3]).
  - Ý kiến kiểm toán có ngoại trừ (HARD ABANDON).
  - Lãi huy động +100bp ⇒ −3,2%.

## 10. Pháp lý / quản trị — chỉ WARNING (giữ r2 §7, cập nhật)

- ⚠️ Tiền cấp quyền: tiền lệ đảo chiều 2022 (nộp bổ sung) ↔ 2026 (nộp thừa).
- ⚠️ Thanh tra CP ⇒ rà soát GP Soklu 1/2/5. Rủi ro đã giảm một phần: SK5 được gia hạn theo QĐ 473/QĐ-UBND [FP p6].
- ⚠️ Kiểm toán NN kiến nghị xử lý đất sử dụng sai mục đích (báo chí 11/2025).
- **Scandal di cư:** chưa thấy lan sang TC1/TP1/TT2.
- Quản trị chéo Dofico–KSB–Hóa An–DRH: không có giao dịch bán hàng với bên liên quan [Q3 p23].
- Nhân sự BKS thay 16/6/2026 [NQ p4].
- Không đưa vào base.

## 11. Cho Mike ghi sổ

`LEDGER_PROPOSAL_VLB.json` (cùng thư mục):
- Tâm **42.800** (ex-div, sau CK); vùng **32.084–52.042**; center_alt (cơ sở) **43.537**.
- `audited_fy_missing = true`.
- `skeptic_final` theo kết quả skeptic r2 (không tự nâng nhãn).
