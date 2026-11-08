# DD — DCM (PVCFC) · as-of 08/11/2026 · **r6 = DD redo vòng 3** (áp đính chính fundamental-skeptic 08/11) · job `Taylor_20261108_142018`

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ. Không phải khuyến nghị. Không đặt lệnh, không sửa `kb/dd_price_zones.json`, không email/PDF. `REPORT_r5.md` và các bản trước giữ nguyên; phần không nhắc ở đây (nguồn hợp đồng, lịch giá khí, §1–3 r5) **không đổi**.
> **Trung thực về thứ tự:** tôi đã biết giá (33.000 → 32.100) và nhãn TRÊN vùng từ r1–r5. Hàm định giá trong `calc/model_r6.py` không nhận giá; hằng `PRICE` chỉ dùng ở khối so sánh cuối. Mỗi đính chính được kiểm bằng calc trước khi áp (§1).
> Số: `calc/model_r6_out.txt/.json` (chạy 2 lần trùng byte), `../dd_redo_20261105/DCM/SUMMARY.json`. Khoá: `calc/LOCK_r6_md5.txt`.

## 0. Kết luận
- **Tâm 24.822 đ/cp** (kỳ vọng 1.620 kết cục, sau CK 5 tỷ 0,57%; trước CK 24.964). **P10 20.827 · P50 24.824 · P90 28.808** (mức kết cục, `_shared/wpct.py`). r5: 24.326 (+2,0%).
- **Giá 32.100 (đóng cửa 06/11, BQ) cao hơn tâm +29,3%, cao hơn P90 +11,4% ⇒ TRÊN vùng (>P90).** 99,5% trọng số kết cục nằm dưới giá; kết cục cao nhất 34.093.
- **Nhãn giữ ở MỌI biến thể song song** (§3): P90 cao nhất là lưới biên rộng 98–260 = 30.914, vẫn < 32.100.
- **Câu dẫn đầu (sửa theo C2):** giá 32.100 hàm ý biên urê–khí dài hạn **≈282 USD/t** (259–319 tuỳ cửa sổ hồi quy) khi base không chứa nhận định chính sách. Mức này nằm **trên dải bền 180–260** (Bobby) và trên biên thực 2025 (257), bằng khoảng 1,6× TB 2016–25 (179). Con số "297" của r5 bỏ: nó có nhánh STRUCT vĩnh viễn.
- **Không đủ điều kiện sleeve fear-buy §2.5:** DN không có sự kiện sợ hãi/khủng hoảng; GPM TB4Q thấp hơn DPM 8/10 năm 2016–25 (`SUMMARY_5F_r2.json`); giá trên P90. Moat NARROW, không bền ⇒ **không cộng**.

## 1. Kiểm từng đính chính (đo bằng `model_r6`)
| # | Đính chính skeptic | Kiểm | Kết quả | Áp |
|---|---|---|---|---|
| C1 | P10/P90 r5 là phân vị của kỳ vọng từng ô; tính lại mức kết cục; đưa trục khí vào lưới | Control: hàm r6 tái lập `r5.ev_r5()` = 24.325,589, **lệch 0,000000**. Lưới r6: mỗi ô là một kết cục tất định; trục khí A-V1/A-V2/B-V1 × I_C 20/22/25 nằm trong lưới | **Đúng.** Số sym3 của skeptic (19.817/29.210) **không tái lập trùng byte**, vì cách tách kết cục khác. Theo quy ước r5 (policy .55, STRUCT 20%, phong toả 50%), mức kết cục của r6 ra **19.089 / 29.220** (sau CK) | Áp |
| C2 | "297 ngoài dải bền" là do STRUCT; chỉ CYC thì ~253, sau sửa hồi quy 237–249, trong dải | Biên hàm ý tại 32.100, sau CK: CYC **không chính sách** 266,1 (hồi quy r5) / 259,3 (2016–25) / 305,7 (2016–25 trừ 2022) / 319,2 (2021–25 trừ 2022). Headline (TB 4 hồi quy) **281,8**. Khi **giữ** P(thuế XK 0%)=0,55: 254,9 (r5) / 247,2 (2016–25), tức đúng số của skeptic | **Đúng một phần.** Đúng: 297 là sản phẩm của STRUCT. **Sai:** ~253 và 237–249 vẫn chứa P(thuế XK 0%)=0,55, chính khoản skeptic yêu cầu rút ở C4. Hai cửa sổ bỏ 2022 có độ dốc thấp (4,7–6,3), nên **đẩy** biên hàm ý lên chứ không kéo xuống | Áp phần đúng; câu dẫn đầu dùng số nhất quán **≈282 (259–319), ngoài dải bền** |
| C3 | Hồi quy n=5 bị 2022 kéo; LNST@179: 2016–25 = 1.367, bỏ 2022 = 1.388 vs 1.265 | Đo: 2021–25 **1.266,8**; 2016–25 **1.368,2**; 2021–25 trừ 2022 **1.389,0**; **2016–25 trừ 2022 1.260,9** | **Đúng**, nhưng thiếu biến thể thứ tư (2016–25 trừ 2022) kéo theo chiều xuống | Áp: cả **4 cửa sổ là một trục trong lưới**, trọng số đều (ước lượng). Không chọn cửa sổ theo chiều |
| C4 | P(thuế XK 0%) 0,55 (+1.034) và STRUCT vĩnh viễn (−996) ra khỏi base; skeptic ra 25.723 | Bỏ policy: 24.326 → 23.292 (**−1.034**). Bỏ STRUCT: → 24.288 (**+996**). Điểm theo từng cửa sổ hồi quy: 24.288 / 25.449 / 24.058 / 25.477; TB **24.818** | **Đúng** cả hai khoản. **25.723 không tái lập**: điểm cao nhất của r6 là 25.477 (2021–25 trừ 2022) | Áp |
| C5 | Rủi ro giảm chưa vào base | Đo ở §4 | **Đúng** (2035+ −7.606, khớp −7,6k) | Độ nhạy |
| C6 | §2.5, HARD ABANDON, CK sleeve, LOCK CSV, SĐBS 12 dự thảo, bên liên quan | — | **Đúng** | Áp (§0, §5, §6, §7) |
| (tự rà) | STANDARD_r2 điều 3: lưới r5 gán 50% cho trừ 332 tỷ tiền gửi hạn chế, không có cơ sở (BCTC và KT2025 Deloitte không trích lập) | Δ điểm −627 nếu trừ đủ | Base theo sổ sách | Độ nhạy + biến thể V_restricted_half |

## 2. Cầu nối r5 → r6 (đ/cp)
| Bước | Giá trị | Δ | Lý do |
|---|---|---|---|
| r5 (điểm; policy .55, STRUCT 20%, hồi quy 2021–25) | 24.326 | | control tái lập lệch 0 |
| bỏ P(thuế XK 0%)=0,55 | 23.292 | −1.034 | nhận định, không dữ liệu (C4) |
| bỏ STRUCT 125 @20% vĩnh viễn | 24.288 | +996 | nhãn 2–4 quý, không cơ sở vĩnh viễn (C2/C4) |
| hồi quy = TB 4 cửa sổ | 24.818 | +530 | C3 |
| điểm → kỳ vọng lưới mức kết cục | 24.964 | +146 | C1 (I_C lồi, r lồi, trục khí) |
| CK thanh khoản 5 tỷ (0,57%) | **24.822** | −142 | STANDARD_r2 điều 6 (r5 ghi ≈0) |

Nhánh tại tham số trung tâm: không còn CYC/ADMIN/STRUCT. Trong base chỉ còn biên TB chu kỳ đo được.

## 3. Headline và biến thể song song (sau CK, mức kết cục; giá 32.100)
| Biến thể | n | Tâm | P10 | P50 | P90 | % trọng số < giá |
|---|---|---|---|---|---|---|
| **H — headline** (4 hồi quy × r × biên 138/179/220 × năm 1 × khí A/B × I_C) | 1.620 | **24.822** | **20.827** | **24.824** | **28.808** | 99,5% |
| chỉ hồi quy 2021–25 (r5) | 405 | 24.301 | 19.817 | 24.290 | 28.981 | 99,4% |
| chỉ 2016–25 | 405 | 25.456 | 21.173 | 25.437 | 29.903 | 98,7% |
| chỉ 2016–25 trừ 2022 | 405 | 24.061 | 20.677 | 24.054 | 27.606 | 100% |
| chỉ 2021–25 trừ 2022 | 405 | 25.469 | 22.653 | 25.432 | 28.432 | 99,8% |
| + P(thuế XK 0%) 0,55 | 1.620 | 25.852 | 21.824 | 25.851 | 29.849 | 98,4% |
| + STRUCT 100/125/150 @20% | 6.480 | 24.038 | 19.729 | 24.000 | 28.401 | 99,6% |
| quy ước r5 ở mức kết cục | 1.080 | 23.947 | 19.089 | 23.606 | 29.220 | 99,8% |
| + phong toả 332 @50% | 3.240 | 24.510 | 20.506 | 24.496 | 28.509 | 99,6% |
| biên DH 98/138/179/220/260 | 2.700 | 24.820 | 18.617 | 24.852 | **30.914** | 94,4% |
| khí Nam Du 30/44,8/54/60,5% × V1/V2 | 4.320 | 24.310 | 19.713 | 24.244 | 28.955 | 98,3% |
| Brent 67,8/82/90/103 (chỉ chiều lên) | 2.160 | 24.081 | 19.997 | 24.189 | 28.251 | ~100% |

Tâm (kỳ vọng) ≈ P50; P90 không bị một nhánh nhỏ quyết định.

## 4. Độ nhạy (Δ so với điểm base 24.818, trước CK; `model_r6_out.txt` mục 5)
- **Phía tăng:** P(thuế XK 0%) 0,55 **+1.033**; nghị định ban hành chắc chắn **+1.879**. Nam Du 30% + V1 **+3.962** (cận trên, chưa tính chi phí bao tiêu). r −100bp **+958**. I_C 25 **+731**.
- **Phía giảm, chưa vào base (C5):**
  - **2035+** khí 10,39 phẳng **−7.606**; nếu leo thang **−11.364**.
  - Nam Du 60,5% + V2 **−3.484**.
  - STRUCT 125 @20% **−788**. Trừ đủ tiền gửi hạn chế **−627**.
  - **Thuế hiệu dụng lịch sử 5%** (ước lượng: giai đoạn giảm 50% của ưu đãi 10%; chưa kiểm FY2021–24) **−981**.
  - r +100bp **−816**. I_C 20 **−487**.
  - **Capex thay thế:** **−1.233 cho mỗi 100 tỷ/năm** FCF mất vĩnh viễn. Đây là đơn vị, không phải số đo; nhà máy đã khấu hao gần hết.
  - **Hụt khí 2028–29:** **−262 cho mỗi 10% sản lượng** (LNST DH @179 TB 4 hồi quy = 950 tỷ). Đây cũng là đơn vị, chưa có dữ liệu mức hụt.
- **Cộng đủ mọi khoản phía tăng cũng không đưa tâm tới giá.** Lấy +1.879 (chính sách chắc chắn) + 3.962 (Nam Du 30% + V1) + 958 (r −100bp), cộng thẳng lên điểm, ra ≈31.617. Đây là phép cộng, không chạy chung. Kết quả vẫn dưới 32.100.

## 5. Thanh khoản (STANDARD_r2 điều 6)
ADV trung vị 250 phiên **93,2 tỷ**, 60 phiên **82,4 tỷ**; σ ngày 2,46% (2025-11-05..2026-11-06, `calc/bq_liq_r6_out.csv`).
- CK ở cỡ 5 tỷ (5,4% ADV, trong vùng hiệu chỉnh luật căn bậc hai): **0,57%** theo ADV250, **0,61%** theo ADV60.
- CK ở cỡ sleeve thật: 10 triệu **0,026%**, 40 triệu **0,051%** (ADV250).

Nhãn như nhau ở mọi cỡ.

## 6. Mốc đổi nhận định (hai chiều) + HARD ABANDON
- **NÂNG (chạy lại khi xảy ra):**
  - Nghị định thuế XK 0% ban hành (+1,0…+1,9k).
  - SĐBS 12 bản ký và giá/khối lượng khí bổ sung PM3 từ 2028 theo kịch bản rẻ (V1), hoặc Nam Du ≤ 30% (tới +4,0k).
  - Biên urê–khí thực ≥ 280 USD/t bền 4 quý với Brent ≤ 80.
  - Văn bản xác nhận giá khí sau 2032 ≤ PM3.
- **HẠ:**
  - Không có khí ≤ giá PM3 sau 2032 (−7,6…−11,4k).
  - Nam Du ≥ 60,5% + V2 (−3,5k).
  - Công bố hụt khí 2028–29 (−262 mỗi 10% sản lượng).
  - Thuế lịch sử 2021–24 xác nhận ≈5% (−1,0k).
  - Capex thay thế lớn (−1,2k mỗi 100 tỷ/năm).
  - VND mất giá (mọi nguồn khí tính bằng USD).
- **HARD ABANDON:**
  - Không mở vị thế khi giá > P90 sau CK (**28.808**).
  - Dừng và làm lại định giá từ đầu nếu xảy ra một trong ba: dừng máy/hụt khí công bố > 60 ngày; PVN thoái vốn kèm thay đổi HĐ khí; bản ký SĐBS 12 khác dự thảo về giá Nam Du.

## 7. Pháp lý / quản trị — WARNING (không vào base)
Mang đủ mọi cờ của r3–r5 §7:
- ⚠️ **Hợp đồng khí là giao dịch bên liên quan khép kín:** PVN → PV GAS → DCM (PVN 75,56%). ĐHĐCĐ uỷ quyền HĐQT sửa "nội dung cơ bản" của HĐ, nên thay đổi giá khí có thể **không qua cổ đông thiểu số** [BB25 p5].
- ⚠️ **SĐBS 12 mới là DỰ THẢO.** NQ/biên bản ĐHĐCĐ 23/9/2026 chưa thấy ở nguồn gốc (tra 05/11; **r6 không tra lại**).
- ⚠️ Tiền gửi 332 tỷ bị hạn chế tại MBV (TM5), chưa có tiến độ xử lý.
- ⚠️ Thù lao HĐQT/BĐH/BKS 9T/26 tăng ×3,25 (56,56 so với 17,39 tỷ) [TM38(4)].
- ⚠️ Phải thu PVN tăng 163,6 → 261,0 tỷ [TM8].
- ⚠️ Sau 24/4/2032 không còn khối lượng cam kết.
- ⚠️ Nhân sự: TGĐ mới; PTGĐ nghỉ (nguồn báo chí).
- "Chưa thấy xử phạt/khởi tố DCM": theo tra cứu 04–05/11 (REPORT_r3–r5), **không tra lại 08/11**.

## 8. Giả định khoá (đủ ở `SUMMARY.json → assumptions`, mỗi cái có cơ sở)
- **Biên DH:** TB 2016–25 = 179 (WB, BQ).
- **Hồi quy:** 4 cửa sổ, trọng số đều (ước lượng).
- **Năm 1:** biên 222.
- **Thuế:** 20% từ 2027 (BCTC tr.17).
- **KTPL:** trích 5,97% LNST và trừ số dư (TM37/CĐKT).
- **Net cash và tiền hạn chế:** theo sổ.
- **Thuế XK:** 5% giữ (luật hiện hành).
- **Khí:**
  - Cách đọc A/B, trọng số 0,5/0,5 (ước lượng); I_C 20/22/25 (ước lượng).
  - 2035+: 50/50 @13,7% Brent (ước lượng).
- **Chiết khấu:** r 13,5%.
- **Tăng trưởng:** g thực 0, RONIC = r; không cộng moat.

## 9. Sản phẩm & khoá
- `calc/model_r6.py`; output `_out.txt/.json`, chạy 2 lần trùng byte.
- `calc/write_summary_r6.py` ghi `../dd_redo_20261105/DCM/SUMMARY.json` (chạy 2 lần trùng byte) và `SUMMARY_r2.json` (ảnh chụp r5 dựng lại từ `model_r5_out.json`, vì trước đây chưa có SUMMARY chuẩn).
- `calc/bq_liq_r6.sql` → `bq_liq_r6_out.csv`.
- `calc/LOCK_r6_md5.txt` gồm mọi file engine và dữ liệu mà script đọc: model.py, model_r2.py, model_r5.py, wpct.py, 3 CSV, các output.
