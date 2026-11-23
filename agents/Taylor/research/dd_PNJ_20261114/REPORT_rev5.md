# DD — PNJ · REV 5 (sau fundamental-skeptic r3 REFUTED) · 2026-11-23 · job `Taylor_20261123_120259`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị, không đặt lệnh, không sửa `excluded_tickers`.
> Kế thừa `REPORT.md` (r2 14/11) cho §1–§5, §7, §9 và `REPORT_rev4.md` (md5 87db0f9b…, skeptic r3 đã đọc) cho phần nguồn; các bản cũ giữ nguyên, không ghi đè.
> Nguồn: **[HN]** BCTC HN Q3/2026 · **[SX]** soát xét HN bán niên 2026 (PwC HCM18793) · **[KT25]** BCTC HN 2025 kiểm toán (PwC HCM17725) ·
> **[TTr40]** cổ phiếu thưởng · **[TTrPH]** phát hành riêng lẻ · **[TTr607]** điều chỉnh cổ tức 2025 · **[NQ]** ĐHĐCĐ bất thường 21/10 ·
> **[IRQ3]** "Cập nhật tình hình hoạt động & tài chính Q3-2026" (tài liệu ĐHĐCĐ; `src/Cap-nhat-tinh-hinh-hoat-dong-tinh-hinh-tai-chinh-Q3-2026.pdf`, md5 dae4bffa…). Toàn bộ 14 PDF ở `src/` (md5 `src_md5.txt`), ảnh trang `src/pages/`. **[BQ]** `tav2_bq`.
> Đơn vị tỷ đồng, đ/cp. Số tự đặt gắn **(ước lượng)**. Khoá: `calc/assumptions_r5.json` (lint 0 vi phạm).

## 0. Kết luận
- **Nhận định GIỮ: NON — tiếp tục loại PNJ.** Sizing V8: **0%** (chuẩn 2–4% NAV không áp vì giá trên cả cận trên vùng).
- **Tâm = 7.395 đ/cp** = giá trị kỳ vọng của cổ đông HIỆN HỮU trên cây kết cục phát hành (§6). **Vùng 6.488–8.303** = tâm tại xác suất phát hành thành công 0,25/0,75.
  Tâm rev4 4.205 ⇒ **rev5 7.395 (+76%)**. Toàn bộ mức tăng đến từ ba lỗi phương pháp skeptic r3 nêu (bảng quy đổi §6.3), không có dữ liệu kinh doanh mới.
- Cây kết cục nay **hẹp hơn nhiều**: O1 (phát hành ở sàn BVPS) 9.210 vs O2 (không phát hành, tài trợ bằng nợ/tồn kho) 5.581 trọng số ⇒ mỗi +0,1 của p chỉ +363 đ/cp (rev4: +797).
- Pha sau khoá: giá đóng cửa 20/11 = 13.500 [BQ] (cùng mốc rev4) ⇒ **giá/tâm = 1,83**; giá trên cận trên vùng (8.303) và trên nhánh phát hành thành công (9.210) ⇒ nhãn **ĐẮT**.

## Đính chính rev5 so với rev4 — từng hạng mục skeptic r3 (REFUTED, medium)

| # | Hạng mục skeptic r3 | Xử lý rev5 | Loại | Tác động lên tâm |
|---|---|---|---|---|
| 1 | **Chí mạng: O2 phạt kép** — vừa hạ kinh tế một bậc (vì không có vốn) vừa trừ đủ 8.000×1,08 (như thể đã vay đủ) | Chọn MỘT cơ chế: **O2 = tài trợ bằng nợ và/hoặc giảm tồn kho, kinh tế GIỮ cùng kịch bản** (DN vẫn có tiền ⇒ không hạ bậc), trừ 8.000 một lần | (a) logic nhất quán; nguồn [IRQ3 p7] | 4.205 → 5.490 (+1.285) |
| 2 | 1.600 trả nợ NH bị tính như nhu cầu mới (đảo nợ là trung tính) | **Không tách — giải thích lý do.** F0 là giá trị **post-money theo KH**, và KH dùng 8.000 = 4.800 thu đổi + 1.600 vốn lưu động + 1.600 trả vay ngắn hạn [IRQ3 p7]. Vậy F0 đã giả định nợ vay thấp hơn 1.600. Nếu không phát hành, khoản 1.600 đó **vẫn còn** (đảo nợ). Nợ của O2 so với KH = 6.400 vay mới + 1.600 không trả được = **8.000**. Trừ 8.000 là trừ khoản nợ đó MỘT lần. Tách 1.600 ra sẽ thành đếm thiếu. | (a) đối chiếu bảng cân đối | 0 |
| 3 | Lãi cầu nối cộng thêm trên mệnh giá (tính trùng) | **Bỏ** ở cả O1 (phần thiếu 1.077,5) và O2. Nợ trừ theo mệnh giá. Lãi vay sau thuế 8% (vay Chủ tịch 10% [HN TM16] × 0,8) thấp hơn r 13,5% ⇒ mệnh giá đã là ước tính thận trọng của gánh nợ | (a) | 5.490 → 5.989 (+499) |
| 4 | LNST giữ lại 2027–28 bị bỏ, lấy cớ "đã nằm trong N 2029" mà không chứng minh | **Cộng PV LNST KH 2027 = 100, 2028 = 1.200** [IRQ3 p9] ⇒ PV 1.019,6 (trễ: 898,3). Lý do: với RONIC = Ke (D4), giá trị = PV phần lãi phân phối được. Đà hồi phục 2027–29 đến từ cắt lỗ/khôi phục niềm tin/tăng doanh số [IRQ3 p8], không đến từ tái đầu tư lãi giữ lại. Nhu cầu vốn của KH đã nằm trọn trong 8.000; capex 9T/2026 chỉ 57,4. Kịch bản tốt dùng đúng số KH, không nhân lên | (a) nguồn [IRQ3 p8–p9] | 5.989 → **7.395** (+1.406) |
| 5 | p=0,5 mâu thuẫn mô hình: NĐT mới trả ≥12.586 cho cp mô hình định giá thấp hơn ~40% | **Nêu thẳng trong mô hình**: ở rev5, O1 trọng số = 9.210 ⇒ NĐT mới trả cao hơn giá trị mô hình **36,7%** (`O1_premium_floor_vs_value_pct`). Bằng chứng về p là **hai chiều và không định lượng được**. Chiều giảm: đối tượng chỉ ghi là "nhà đầu tư chứng khoán chuyên nghiệp", **không có tên** [TTrPH; REPORT r2 §3], và mức trả cao hơn giá trị như trên. Chiều tăng: Chủ tịch đã cho vay cá nhân **700 tỷ** tín chấp [HN TM16; IRQ3 p4], là bằng chứng nội bộ sẵn sàng cấp vốn (≈10% của 6.923). ⇒ giữ **p = 0,5 trung tính**, vùng = p 0,25/0,75. Nay p ít quyết định tâm hơn: dải 6.488–8.303 (rev4: 2.212–6.198) | (b) | 0 (dải hẹp lại) |
| 6 | Chiều xuống neo vào KH của chính DN đang khủng hoảng, không chiết khấu (70% trọng số ≥ KH) | **Giữ trọng số r3** (khoá trước khi xem giá). Không có cơ sở độc lập để chiết khấu KH: luật user yêu cầu mọi điều chỉnh GIẢM phải có cơ sở độc lập. Hai kịch bản dưới KH đã chiếm 0,30 (trễ 1 năm, thu đổi 100%) | (b) giữ | 0 |
| 7 | Không có nhánh vỡ nợ/thanh lý; sàn 0 là áp đặt | Ở rev5 **không nhánh nào chạm sàn 0** (O2 thấp nhất 1.294). Thêm **O3 vỡ nợ/tái cấu trúc làm độ nhạy**. Bằng chứng ràng buộc vay [IRQ3 p4]: tiền giảm 3.700 → 770 (30/6→30/9, đã gồm 700 vay Chủ tịch); nợ vay NH 3.000; tồn kho kim cương 41% → 52% (thanh khoản thấp); cần 150 tỷ/tháng tài trợ hoạt động. Xác suất O3 **không có cơ sở độc lập** ⇒ không vào base (§6.4) | (b)/(c) | 0 base; −279 đến −558 ở độ nhạy |
| 8 | Pha loãng ESOP 2025/26 chưa định lượng | ESOP đã duyệt (TTr 19, 20 ĐHĐCĐ 2025), chưa phát hành tới 30/9 (VĐL 5.118,9 tỷ khớp 511,89tr cp [HN BS]). Quy mô **không có trong src ⇒ không kiểm chứng được**. Ảnh hưởng: mỗi 1% pha loãng ⇒ khoảng −1% giá trị/cp, tức −74 đ/cp (ước lượng) | (c) | 0 base |
| 9 | Pháp lý còn mở: NĐ 390, kiện tụng do thanh toán chậm, "vốn khác" 500, quỹ thưởng HĐQT 50,7 | **Không kiểm chứng được** trong phiên này. Giữ là WARNING, không vào base (luật vụ án chỉ WARNING) | (c) | 0 |
| — | Đạt ở r3 (giữ nguyên): số cp, ý kiến kiểm toán FY25 + soát xét H1, cổ tức 2025 đã chi, vay Chủ tịch, không có cam kết capex | — | — | — |

*(Bảng đính chính rev4/rev3 giữ nguyên trong `REPORT_rev4.md`.)*

## 6. Định giá rev5

### 6.1 Khung
- F0 = VCSH vận hành **post-money theo KH** tại 31/12/2026 = N/r chiết khấu từ năm đạt N (D4: NARROW ⇒ RONIC = Ke) **+ PV LNST KH 2027–28**.
- **r = 13,5%**: `deposit_rate_vn('2026-11-23')` = 7,40% (CCTG 12M 02/11; Big-4 6,80%), trùng điểm neo 03/11 ⇒ Δ = 0, β = 1. Dải Ke 12,3–13,4% báo kèm.
- Sàn giá phát hành = max(TB 30 phiên, BVPS kiểm toán/soát xét gần nhất) [TTrPH 1.8]. BVPS FY2026 (ước lượng) = (13.182,31 − 6.741,66)/511,72 = **12.586** (KH LNST 2026 −6.270, 9T 471,66).
  - **O1**: phát hành 550tr cp ở sàn ⇒ thu 6.922,5; phần thiếu **1.077,5** vay, trừ theo mệnh giá ⇒ (F0 + PV27–28 − 1.077,5)/1.061,72.
  - **O2**: không phát hành ⇒ 8.000 tài trợ bằng nợ và/hoặc giảm tồn kho, kinh tế **giữ cùng kịch bản**, trừ **8.000** một lần (§Đính chính #2) ⇒ (F0 + PV27–28 − 8.000)/511,72, sàn 0 (không ràng buộc).

### 6.2 Kịch bản × kết cục (trọng số vận hành, N, r khoá ở r3 TRƯỚC khi đọc giá; p = 0,5 trung tính)

| Kịch bản vận hành | w | Cơ sở | F0 | PV LNST 27–28 | O1 | O2 | 0,5·O1+0,5·O2 |
|---|---|---|---|---|---|---|---|
| Cơ sở | 0,50 | KH LNST 2029 = 1.600 [IRQ3 p9] | 9.200 | 1.020 | 8.611 | 4.338 | 6.474 |
| Tốt | 0,20 | (ước lượng) N=2.500 ≈ kinh tế 2023–25 [BQ] | 14.375 | 1.020 | 13.485 | 14.451 | 13.968 |
| KH trễ 1 năm | 0,20 | 1.600 đạt 2030 (ước lượng) | 8.106 | 898 | 7.466 | 1.962 | 4.714 |
| 100% thu đổi | 0,10 | cơ sở − 1.768 lỗ thêm 2027 | 7.643 | 1.020 | 7.144 | 1.294 | 4.219 |
| **Trọng số** | | | | | **9.210** | **5.581** | **TÂM 7.395** |

p = 0,25 ⇒ 6.488; p = 0,75 ⇒ 8.303 (**vùng**). Mỗi +0,1 của p ⇒ +363 đ/cp.
Ở kịch bản tốt O2 > O1 vì phát hành ở 12.586, dưới giá trị/cp, nên pha loãng cổ đông hiện hữu. Mô hình nhất quán ở cả hai chiều.
O1 đòi NĐT mới trả cao hơn giá trị trọng số của mô hình **36,7%** (12.586 vs 9.210). Đây là lý do p không thể coi là cao nếu không có NĐT chiến lược/nội bộ (§Đính chính #5).

### 6.3 Quy đổi tâm rev4 → rev5 (`calc/model_r5.py`, chạy lại từng bước)
4.205 (tái lập rev4) → bỏ hạ bậc O2 **5.490** → bỏ lãi cầu nối **5.989** → cộng PV LNST 2027–28 **7.395**.
Phương án O2 kiểu (b) của skeptic (không có vốn, hạ bậc, không trừ nợ) **không dùng**. Lý do: với kinh tế hạ bậc mà không trừ đồng nào, O2 sẽ cao hơn O1, tức không phát hành lại tốt hơn phát hành. Như vậy nghĩa vụ thu đổi 4.800 bị bỏ qua, phi lý. Đối chứng: giữ hạ bậc, bỏ cầu nối, cộng 27–28 ⇒ 5.790.

### 6.4 Độ nhạy (V1, D4) — tâm tại p = 0,5
- r −100bp 8.883 · −50bp 8.110 · +50bp 6.733 · +100bp 6.130 · Ke 12,3% 9.211 · Ke 13,4% 7.534.
- Không cộng LNST 2027–28 ⇒ 5.989 (−19%).
- **O3 vỡ nợ/tái cấu trúc** (xác suất q lấy từ O2, không có cơ sở độc lập). Giá trị thanh lý L = (6.440,65 − h × 16.626 tồn kho ròng)/511,72: h = 0,2 ⇒ 6.088; h = 0,4 ⇒ 0. Mức chiết khấu h **không kiểm chứng được**.
  - q = 0,1: 7.116 (L = 0) / 7.421 (h = 0,2).
  - q = 0,2: 6.837 (L = 0) / 7.446 (h = 0,2).
  - ⇒ tâm dịch **−279 đến −558** ở L = 0, vẫn nằm trong vùng.
- ESOP: mỗi 1% pha loãng ≈ −74 đ/cp (ước lượng).
- Chiều tăng, không vào base: biên ròng hồi phục 6,4–7,9% ⇒ N 3.693–4.558; lỗ thu đổi theo tỷ lệ thực tế TM17 (~3.867 thay 7.071).

### 6.5 V3 thanh khoản (sau khoá, không đổi so với rev4)
ADV trung vị 20 phiên **101,9 tỷ**, 60 phiên **146,2 tỷ** [BQ, tới 20/11]. Vị thế 50 tỷ (ước lượng) ở tỷ lệ tham gia 10–20% thoát trong 2,5–4,9 phiên ⇒ chiết khấu thanh khoản **0%** ⇒ giá trị trước = sau = 7.395.

### 6.6 V6 hai nền (chỉ hiển thị)
FCFE ≤ 0 (CFO TTM −2.579,5 [BQ]) ⇒ chỉ có V_ngắn = trung vị LNST 2023–25 2.112,9 / r = 15.651 tỷ (30.585 đ/cp trên 511,72tr). Đây là kinh tế trước khủng hoảng và trước nghĩa vụ thu đổi 21.000 [IRQ3 p4] ⇒ không làm neo, không tính D.

### 6.7 V5 — 5F
Tái dùng r2 14/11 (<12 tháng): **NARROW (đang suy giảm), BRAND/SCALE**. Rủi ro số 1 là niềm tin khách hàng. Kiểm 23/11: IRQ3 p4 (tồn kho kim cương 52%) và p8 (chiến lược "Build Trust") không đổi phân loại.

## 8. Vùng giá & điều kiện đổi nhận định (HAI chiều)
- Tâm **7.395**, vùng **6.488–8.303**. Giá 13.500 = 1,83× tâm ⇒ **giữ NON**.
- **Đổi lên**: (i) đợt riêng lẻ hoàn tất ≥ sàn với NĐT độc lập có tên ⇒ p → 1, tâm ≈ 9.210 (vẫn dưới giá 20/11); (ii) kiểm toán FY2026 chốt lỗ thu đổi < 7.071; (iii) LNST 2 quý liền ≥ nhịp KH 2028.
- **Đổi xuống**: phát hành thất bại/thu nhỏ trước 31/12/2027 *và* NH tiếp tục rút hạn mức (O3 thành hiện thực); tỷ lệ thực hiện thu đổi > 80%; ý kiến ngoại trừ FY2026; ESOP quy mô lớn.
- Mốc: BCTC Q4/2026 (~cuối 01/2027), kiểm toán FY2026 (~03/2027), hồ sơ chào bán.

## 10. Nguồn & khoá rev5
- `calc/assumptions_r5.json` md5 **4135406421db9dced251fda798d25d7f** · `calc/model_r5.py` 63c502145bf501b72efd28dec6738950 · `calc/model_r5_out.json` 0fba420b3b949be46274acc9aa452ad4 (`calc/LOCK_r5_md5.txt`).
- Mù giá: trọng số vận hành, N, r khoá ở r3 trước khi truy vấn giá; p đặt ở r4 sau khi đã thấy giá và **không đổi ở r5**. Ba sửa của rev5 là sửa phương pháp/nguồn, độc lập với giá. Mô hình không có biến giá. Không truy vấn giá mới trong phiên này.
- Còn mở, không kiểm chứng được: NĐ 390/2026; kiện tụng do thanh toán chậm sau 30/6; nguồn "vốn khác" 500 tỷ [HN BS 414]; nguồn quỹ thưởng HĐQT&BĐH 50,7 [HN TM15a]; quy mô ESOP 2025/26; xác suất và giá trị thanh lý nhánh O3; danh tính NĐT riêng lẻ.
