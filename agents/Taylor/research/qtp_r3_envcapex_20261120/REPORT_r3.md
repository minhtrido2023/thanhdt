# QTP DD r3 — sửa mô hình: dự án nâng cấp hệ thống xử lý khí thải · 20/11/2026 · job `Taylor_20261120_041936`

> Chỉ NGHIÊN CỨU. Không ghi `dd_price_zones.json` (Mike làm sau skeptic), không gửi email.
> Mô hình: `qtp_model_r3.py` (md5 `278167b15b77daada385f7f645495046`), output `qtp_model_r3_out.txt`.
> Kiểm tra độc lập: `check_independent.py` (công thức annuity, không import mô hình) cho P0/cơ sở **−10.478 đ/cp, khớp từng đồng**.
> Nền r2 giữ nguyên, tái lập đúng 14.599 trước CK. r3 chỉ CỘNG phần chênh dòng tiền của dự án vào từng kịch bản r2.

## 0. Kết luận

- **Lỗi r2 là có thật, và mức độ còn LỚN HƠN ước tính thô của Mike.**
  - Mike ước −4.500…−5.400 đ/cp. Con số này chỉ gồm vốn + lãi + gốc; phần này đo được **−4.745 đ/cp**, khớp với Mike.
  - Bỏ sót **chi phí vận hành của hệ thống mới**. Theo FS gốc: O&M cố định 102,0 tỷ/năm + điện-nước-hoá chất 470,3 tỷ/năm, trong đó amoniac 317 tỷ. Tổng **572 tỷ/năm**, tương đương ~101% LNST chuẩn hoá 565 tỷ.
  - Phần opex này thêm **−5.733 đ/cp** khi không được bù.
- **Tâm mới:**
  - Trọng số P0/P50/P100 = **0,50/0,30/0,20**, chốt TRƯỚC khi chạy; cơ sở ở §3.
  - Trước CK: **7.836 đ/cp**. Sau CK thanh khoản 10%: **≈7.050 đ/cp**.
  - r2 là 14.599 / 13.139 ⇒ giảm **−6.762 đ/cp trước CK (−46%)**.
- **Vùng sau CK:** 1.150 (xấu + P0) … 16.330 (tốt + P100). Rất rộng vì cơ chế bù giá quyết định gần như toàn bộ.
- **So với giá:**
  - 10.300 (16/11) = **1,46×** tâm.
  - 10.200 (BQ, 19/11) = **1,45×** tâm.
  - ⇒ **ĐẮT** theo DCF có trọng số.
  - Giá thị trường chỉ được biện minh nếu xác suất bù đủ (P100) cao. Riêng P100 sau CK là 12.805; riêng P50 là 8.618, vẫn dưới giá.
- **Biến quyết định duy nhất:** EVN/EPTC có đưa phần tăng thêm 169,44 đ/kWh vào giá điện hay không.
  - Từ P0 lên P100 là **~10.000 đ/cp**.
  - Mọi biến khác (lãi vay ±2pp, lãi huy động ±100bp, opex lùi đến 2032) chỉ dịch tâm **±1.400 đ/cp**.
- **Cổ tức:**
  - 2027–29: cần **1.086 tỷ (2.413 đ/cp)** cho vốn chủ cộng lãi vay thời gian xây dựng. Tiền ròng 1.541 tỷ đủ trả, nên cổ tức có thể giữ ~900–1.000đ **(ước lượng)**.
  - **Vách đá 2030** khi dự án vận hành mà chưa được bù giá (P0): LNST TB 2030–39 là **−394 tỷ/năm**, cổ tức về 0.
  - P50: EPS ~307 ⇒ DY ~2–3%. P100: EPS ~1.286 ⇒ DY ~9–10%.

## 1. Số liệu dự án — nguồn GỐC (mới trong r3)

| Mục | Giá trị | Nguồn |
|---|---|---|
| TMĐT trước VAT / sau VAT | **3.484,88 / 3.799,19 tỷ** (thiết bị 2.941; dự phòng 200,8; chi phí khác 142,4 gồm lãi vay xây dựng) | BC thẩm tra FS PECC1 số 2985/TVĐ1-NĐNLM 22/5/2026, CBTT 11/06/2026 (`src_fs/…VI_BCTT_FS…pdf`, md5 2a005758…) |
| Vay | **2.787,9 tỷ = 80,0%** TMĐT trước VAT; BIDV Hạ Long 1.787,9 + VCB Quảng Ninh 1.000 | QĐ 917 (15/6/2026, đọc ảnh gốc); QĐ 1490 (21/9/2026) |
| Lãi suất, kỳ hạn, ân hạn | **KHÔNG công bố.** QĐ 1490 dẫn "theo NQ 105/NQ-NĐQN 14/9/2026", văn bản không tải được. BCTC Q3/26: vay = 0, chi phí lãi vay = 0 | ⇒ **(ước lượng)** 9% (biên 7/11%); FS dùng "lãi tiền gửi + biên 3%" theo TT 07/2024 |
| EPC | 89.756.813 USD + 901,82 tỷ VND (SEC–Pacific, trọn gói, 38 tháng). Số USD bằng chữ cả hai ngôn ngữ là 89.756.813 (chữ số tiếng Việt in 89.156.813 — lỗi đánh máy; lệch ~16 tỷ, không trọng yếu). Báo chí: EPC ≈3.271 tỷ, ký 16/10/2026 | QĐ 1710 (6/10/2026) |
| O&M cố định | **102,01 tỷ/năm** (= 15,69 đ/kWh × 6.501,57 GWh; bảng FS ghi nhầm đơn vị "tỷ/MW") | FS §3.1.7 |
| Điện-nước-hoá chất | **470,29 tỷ/năm**; amoniac 12.045 tấn × 26.350 đ/kg = 317,4 tỷ; điện 18,47 GWh | FS §3.1.7 |
| Giá đề nghị tăng thêm | **169,44 đ/kWh** = FC 81,42 + O&M cố định 15,69 + biến đổi 72,33; FIRR 11,0%, if 7,48%, NPV 156,8 tỷ; tuổi thọ kinh tế 18 năm, khấu hao 10 năm | FS + BC thẩm tra §10.2/10.4 |
| Kiểm lại FIRR | FC 529,4 tỷ/năm × **18 năm** ⇒ IRR dự án không đòn bẩy sau thuế **10,14%** (tính độc lập; FS 11,0% vì giả định thi công ngắn hơn). × 10 năm chỉ cho 5,6% ⇒ FC được thu trên 18 năm | `check_independent.py` |
| Lịch sử vướng giá | Dự án phê duyệt lần đầu 2017 (QĐ 358/QĐ-NĐQN 03/04/2017). TB 384/TB-VPCP 02/10/2018 (họp về điều chỉnh giá điện khi cải tạo khí thải). Tờ trình 4690/TTr-EVN 10/7/2020 báo cáo TTg "khó khăn, vướng mắc". ⇒ **9 năm chưa có cơ chế bù giá được áp** | FS §1.2–1.3 |

**Điểm pháp lý cần Wendy soát lại:**
- FS dẫn **TT 57/2020/TT-BCT Đ20.3**: "nhà máy đang vận hành cần cải tạo để đáp ứng QCVN môi trường ⇒ bên bán và bên mua **thoả thuận bổ sung các chi phí này vào giá điện**…".
- TT 57/2020 đã bị thay bằng TT 07/2024, rồi TT 12/2025.
- legal-vn (20/11) kết luận TT 12/2025 chỉ cho cộng chi phí cải tạo ở Đ13.4/Đ14.6 (không áp cho QTP), lối duy nhất là Đ27.3 (sửa PPA).
- **Tôi CHƯA tự đọc được văn bản gốc TT 12/2025** ⇒ chưa xác minh độc lập.
- **Câu hỏi cho Wendy:** TT 07/2024 và TT 12/2025 có giữ điều tương đương TT57 Đ20.3 không? Đây là một câu hỏi đáng ~10.000 đ/cp.

## 2. Ba kịch bản bù giá — dòng tiền FCFE chênh lệch (kịch bản r2 cơ sở, lãi vay 9%, tỷ đồng)

**Giả định chung:**
- Giải ngân TMĐT 30/45/25% trong 2027/28/29 **(ước lượng**, 38 tháng từ 10/2026), COD **01/2030 (ước lượng)**.
- Vốn chủ 20%, vay 80% giải ngân pro-rata.
- Lãi vay thời gian xây dựng (IDC) 389 tỷ trả bằng tiền, vốn hoá vào tài sản.
  - **Thận trọng:** TMĐT đã có một phần IDC theo tiến độ ngắn trong "chi phí khác", nên có thể đếm trùng ≤~100 tỷ **(ước lượng)**.
- Trả gốc đều 10 năm 2030–39 **(ước lượng)**.
- Khấu hao (TMĐT + IDC)/10 năm theo FS. Thuế 20%.
- Lá chắn thuế bị **giới hạn bởi thuế của chính QTP**, có chuyển lỗ. Nếu không giới hạn thì P0 sẽ bị thổi phồng giá trị.
- Opex chạy từ COD đến khi nhà máy dừng (2047 cơ sở, 2040 xấu). Bù giá bắt đầu từ COD, **không hồi tố** (Đ15.2đ).

| Năm | Vốn chủ | IDC | Lãi vay | Trả gốc | KH mới | Opex | Bù P0/P50/P100 | ΔFCFE P0 | ΔFCFE P50 | ΔFCFE P100 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2027 | 209 | 38 | – | – | – | – | 0 | −247 | −247 | −247 |
| 2028 | 314 | 132 | – | – | – | – | 0 | −445 | −445 | −445 |
| 2029 | 174 | 220 | – | – | – | – | 0 | −394 | −394 | −394 |
| 2030 | – | – | 238 | 279 | 387 | 572 | 0/551/1.102 | −963 | −413 | +31 |
| 2035 | – | – | 113 | 279 | 387 | 572 | 0/551/1.102 | −838 | −309 | +132 |
| 2039 | – | – | 13 | 279 | 387 | 572 | 0/551/1.102 | −738 | −229 | +212 |
| 2040–47 | – | – | – | – | – | 572 | 0/551/1.102 | −446 | −17 | +423 |

(Bảng đủ từng năm: `qtp_model_r3_out.txt` mục (1).)

**PV chênh lệch (đ/cp, r = 13,5%):**

| | P0 không bù | P50 bù 50% (FC + O&M + biến đổi) | P100 bù đủ, FIRR 11% ≤ 12% |
|---|---|---|---|
| r2 cơ sở | **−10.478** | **−4.931** | **−186** |
| r2 xấu (dừng 2040) | −10.264 | −5.298 | −927 |
| r2 tốt | −9.855 | −4.930 | −186 |
| Lãi vay 7% / 11% (cơ sở) | −10.039 / −10.917 | −4.564 / −5.312 | +181 / −552 |

- **P100 vẫn âm nhẹ** vì FIRR được trần ≤12%, thấp hơn r = 13,5%. Đúng như user nói: luật 03/11 (NPV = 0) chỉ áp khi IRR ≥ r; ở đây kể cả bù đủ cũng không đạt.
- P50 biến thể "chỉ bù 50% FC, không bù opex" (đúng chữ dispatch): **−7.652**.
- **Tách cấu phần P0 cơ sở:**
  - Vốn + lãi + gốc: −4.745 — khớp ước tính thô của Mike.
  - Opex: −5.733.
  - Nếu opex chỉ chạy từ 01/01/2032 (QCVN 19:2024 bắt buộc; trước đó vẫn áp QCVN 22:2009): **−8.951**.
  - Nếu chi phí biến đổi chỉ bằng 50% FS (huy động thấp/amoniac rẻ hơn — ước lượng): −7.951.

## 3. Trọng số kịch bản — cơ sở dữ liệu (chốt 0,50/0,30/0,20 TRƯỚC khi chạy)

- **P0 cao nhất (0,50):**
  - legal-vn: Đ13.4/14.6 không áp cho QTP; chỉ còn đàm phán sửa PPA (Đ27.3); không hồi tố; **0 tiền lệ** nhà máy than được bù.
  - Kiến nghị của EVN 29/12/2025 chưa được công nhận.
  - Dự án đã vướng giá **9 năm** (2017→2026) dù TT57/2020 từng có điều khoản thoả thuận.
- **P50 + P100 = 0,50:**
  - Bên mua (EPTC) và chủ sở hữu chi phối (EVNGENCO1 42%) **cùng thuộc EVN**.
  - Vấn đề mang tính **hệ thống**: báo chí nêu 30 tổ máy nhiệt điện của EVN cùng cải tạo; HND và PPC có dự án tương tự.
  - P0 thuần cho LNST âm ~−394 tỷ/năm 2030–39 ở một DNNN cần cho cấp điện miền Bắc (thiếu 4.256 MW năm 2027) ⇒ trạng thái khó tồn tại 18 năm. Áp lực chính sách thật, nhưng **chưa có văn bản**.
  - **P100 chỉ 0,20** vì cần đủ cả FC lẫn opex và đúng tiến độ.
- Trọng số khác (sau CK): 0,6/0,3/0,1 → 6.154 · 0,4/0,4/0,2 → 7.533 · P0 thuần → 3.813. **Giá 10.200 vẫn ĐẮT ở mọi bộ trọng số có P0 ≥ 0,4.**
- Các trọng số trên là **(ước lượng)** — phán đoán neo vào các dữ kiện vừa nêu, không phải tần suất đo được (N = 0 tiền lệ).

## 4. Quyền chọn trì hoãn tới 2031 (COD 2032)

| | COD 2030 | COD 2032 | Giá trị trì hoãn |
|---|---|---|---|
| P0 | −10.478 | −8.011 | **+2.467** |
| P50 | −4.931 | −3.823 | +1.108 |
| P100 | −186 | −260 | −75 |

- Về lý thuyết, trì hoãn có giá trị lớn khi không được bù (QCVN 19:2024 chỉ bắt buộc từ 01/01/2032).
- **Trên thực tế quyền chọn này gần như ĐÃ BỊ BỎ:**
  - Hợp đồng EPC trọn gói đã ký (QĐ 1710, 6/10/2026; báo chí 16/10).
  - Nhà tài trợ vốn đã được xếp hạng (QĐ 1490).
  - EVN chỉ đạo hoàn thành sớm (văn bản 1613/EVN-ĐTXD 23/3/2026, dẫn trong BC thẩm tra).
  - ⇒ **Trọng số 0 trong tâm**, chỉ hiển thị.
- Đòn bẩy còn lại của QTP là **vận hành SCR tối thiểu tới 2031**: giá trị tối đa ≈ chênh giữa −10.478 và −8.951, tức +1.527 ở P0.
- Rủi ro chậm COD sau 2032: mỗi năm bị hạn chế phát 50% **(ước lượng)** ≈ **−279 đ/cp**.

## 5. Tâm, vùng, nhãn

| | Trước CK | Sau CK 10% |
|---|---|---|
| r2 (pin) | 14.599 | 13.139 |
| **r3 (0,50/0,30/0,20)** | **7.836** | **7.053** |
| P0 / P50 / P100 thuần | 4.236 / 9.576 / 14.228 | 3.813 / 8.618 / 12.805 |
| Biến thể opex từ 2032 · biến đổi 50% · lãi vay 7% · lãi vay 11% | 9.221 · 9.339 · 8.244 · 7.426 | 8.299 · 8.405 · 7.419 · 6.684 |
| Vùng (xấu+P0 … tốt+P100) | 1.281 … 18.138 | 1.153 … 16.325 |

- **Độ nhạy lãi huy động** (r và lãi vay cùng dịch 1:1), sau CK: −100bp 7.433 (+5,4%) · −50bp 7.238 · +50bp 6.878 · +100bp 6.711 (−4,8%).
- **Giá/tâm sau CK:** 10.300 → **1,46** · 10.200 (19/11) → **1,45** ⇒ nhãn **ĐẮT**.
  - Kể cả biến thể thuận lợi nhất (biến đổi 50%: 8.405) thì giá/tâm vẫn = 1,21.
- **V_ngắn vs V_dài:**

| | LNST TB 2030–39 | EPS | V_ngắn |
|---|---|---|---|
| P0 | −394 tỷ | −875 | **−6.481 (âm)** |
| P50 | 138 tỷ | 307 | 2.272 |
| P100 | 579 tỷ | 1.286 | 9.526 |

- V_dài (cơ sở r3) = 8.444. Theo trọng số, V_ngắn ≤ 0 ⇒ **D không xác định ⇒ BẬT cờ phân kỳ**: tiền mặt hiện tại cao, nhưng thu nhập sau 2030 phụ thuộc vào một quyết định giá chưa có.

## 6. Đối chiếu HND (Nhiệt điện Hải Phòng)

- **Tổng mức đầu tư:**
  - Báo chí nêu TMĐT dự án khí thải HND 1&2 **>3.607,5 tỷ**, gói EPC 3.124 tỷ (baodauthau, tapchicongthuong).
  - Con số 3.298,8 tỷ trong dispatch **không tái lập được** từ nguồn tìm thấy.
- **Tiến độ:** BQ `ticker_financial` Q3/2026 cho thấy HND vay = 0 ⇒ chưa giải ngân.
- **Dự phòng/thuyết minh bù giá: KHÔNG tìm thấy** trong nguồn đã đọc. Tôi chưa tải BCTC HND, nên đây là "chưa kiểm chứng", không phải "không có".
- Đây là bằng chứng cho tính **hệ thống** (§3), không phải tiền lệ được bù.

## 7. Cổ tức 2027–29 và sau đó

- **2027–29:** chi ra 247 / 445 / 394 tỷ (vốn chủ + IDC), tổng **1.086 tỷ = 2.413 đ/cp**. Đây là dòng tiền, không đi qua LNST, vì IDC được vốn hoá.
  - Trả bằng tiền ròng 1.541 tỷ thì cổ tức theo LNST ~900–1.000đ (DY 8,8–9,8% trên 10.200) vẫn giữ được **(ước lượng)**, nhưng tiền ròng sẽ về ~0,5 nghìn tỷ.
- **Từ 2030:**

| Kịch bản | ΔLNST năm 2030 | EPS | Cổ tức / DY |
|---|---|---|---|
| P0 | −2.382 đ/cp | âm | về 0 |
| P50 | — | ~307 | ~2–3% |
| P100 | −171 đ/cp | ~1.286 (TB 2030–39) | gần như giữ nguyên |

- Kỳ vọng DY theo trọng số 2030+ ≈ 0,5·0 + 0,3·2,5% + 0,2·9,5% ≈ **2,7% (ước lượng)**.

## 8. Thay đổi cần sửa (Mike làm sau skeptic — tôi KHÔNG sửa)

1. **`dd_QTP_20261117/REPORT.md`:**
   - §0: thay tâm 13.140 / vùng 10.390–16.490 / "RẺ có điều kiện" bằng **7.050 / 1.150–16.330 / ĐẮT**.
   - §4 "Dự án khí thải": xoá câu "Luật 03/11 — NPV = 0 trong base". Thay bằng: chỉ áp cho dự án tăng trưởng IRR ≥ r; dự án tuân thủ có FIRR trần 12% < 13,5%.
   - Thêm opex 572 tỷ/năm.
   - §5 DY: thêm vách đá 2030.
   - §6: trọng số P và cờ phân kỳ BẬT.
   - §10 tín hiệu sai: mục 4 đổi thành "EVN/BCT chấp thuận bổ sung 169,44 đ/kWh" — đây là **catalyst lên**, không chỉ là rủi ro xuống.
   - §7: thêm điểm pháp lý TT57 Đ20.3.
2. **`investor_report/QTP_DD_investor_report_20261117.{md,html,pdf}`:**
   - Viết lại headline (luật 9: tiêu đề nêu cả rủi ro): "Tiền mặt dày nhưng gánh dự án khí thải 3.485 tỷ chưa có cơ chế bù giá — đắt so với giá trị có trọng số".
   - Thay bảng định giá; thêm bảng 3 kịch bản P0/P50/P100.
   - **Không nhắc "r2 sai/đính chính"** (luật 18).
3. **`dd_price_zones.json` (QTP):**
   - Rev mới `r3_20261120`, `center = 7053`, `zone_lo = 1153`, `zone_hi = 16325`, `buy_below = 0,85 × 7.053 ≈ 5.995`, `label = DAT`.
   - `assumptions_md5` = md5 của `qtp_model_r3.py` (`278167b15b77daada385f7f645495046`) + ghi rõ trọng số P 0,5/0,3/0,2 và lãi vay 9% ước lượng.
4. **Câu hỏi mở (ảnh hưởng tâm >1.000 đ/cp):**
   - (a) Wendy: TT 07/2024 / TT 12/2025 có giữ điều TT57 Đ20.3 không.
   - (b) Lãi suất/kỳ hạn thật trong NQ 105/NQ-NĐQN và hợp đồng tín dụng (CBTT sắp tới).
   - (c) Giấy phép môi trường hiện hành của QTP có buộc vận hành SCR ngay sau COD (trước 2032) không.
   - (d) BCTC HND: thuyết minh dự án khí thải.

## 9. Giới hạn đã biết

- Chuyển lỗ trong mô hình không hết hạn sau 5 năm. Ảnh hưởng nhỏ: lỗ chủ yếu đến khi P0 ở 2030–39, và chỉ được dùng lại từ 2040.
- Chi phí biến đổi không co theo sản lượng ở kịch bản xấu (huy động thấp) ⇒ P0 ở kịch bản xấu hơi bi quan.
- Không mô hình hoá thuế VAT đầu vào 314 tỷ: khấu trừ nhanh, chỉ là vấn đề thời điểm.
- Không mô hình hoá quyền từ bỏ (bỏ vận hành SCR hoặc bán): giá trị vốn chủ thực không âm vô hạn, nhưng P0 thuần vẫn dương (4.236), nên không ràng buộc.
- P0 giả định vận hành SCR đủ từ COD. Có biến thể từ 2032.
