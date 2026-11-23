# DD — DCM (PVCFC) · as-of 23/11/2026 · **rev9** · áp verdict fundamental-skeptic r3 (23/11, REFUTED) · job `Taylor_20261123_100914` (vòng 3 — cuối)

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ, không phải khuyến nghị. Không đặt lệnh, không email, không ghi `kb/dd_price_zones.json` (đề xuất sổ: `LEDGER_PROPOSAL_DCM.json`).
> rev9 **thay** `REPORT_rev8.md` (skeptic r3), `REPORT_rev7.md`, `REPORT_r6.md` và báo cáo NĐT `investor_report/DCM_DD_investor_report_20261105.md`.
> **Giữ nguyên rev8, có dẫn nguồn:** hợp đồng khí 3918 / SĐBS 12 dự thảo, lịch giá khí 2026–34, trục khí 2035+, capex duy trì M, D&A 2018–22 từ BQ, thanh khoản, V6, 5F.
> **Thứ tự mù giá — trung thực:**
> - Giá DNSE 30.400 đã biết từ pha rev7. Sửa đổi rev9 (T1–T3) là đính chính do skeptic r3 nêu; mỗi cái có nguồn độc lập; `calc/model_r9.py` không đọc giá.
> - Khoá `calc/LOCK_r9a_pre2023_md5.txt` → chạy `compare_px_r9` lần 1 (tâm 27.208). Sau đó tìm được BCTC KT 2024 gốc (số 2023) ⇒ thêm vào, **khoá lại** `calc/LOCK_r9_md5.txt` rồi chạy lại. Hướng sửa thứ hai do dữ liệu gốc, không do giá; kết quả lần 1 lưu ở `calc/compare_px_r9a_pre2023_out.json`.
> **Nguồn BCTC:** mới nhất HN Q3/2026 (15/10/2026). BCTC năm đã kiểm toán: FY2025, Deloitte, chấp nhận toàn phần ⇒ `audited_fy_missing = false`. Mới thêm: BCTC HN KT 2024 (`src/web/DCM_Baocaotaichinh_2024_Kiemtoan_Hopnhat.pdf`, static2.vietstock.vn, md5 `14e9746f135e2fb47360dc8d33bd39f8`).

## 0. Kết luận
- **Tâm 27.393 đ/cp sau CK thanh khoản** (27.554 trước CK), kỳ vọng lưới 2.430 kết cục.
  - **P10 22.065 · P25 24.385 · P50 27.441 · P75 30.479 · P90 32.564** (sau CK, mức kết cục).
  - So với rev8 (26.780): **+2,3%**, cầu nối ở §2. Skeptic r3 ước +0,95…+2,49k; rev9 ra **+613** sau CK vì (i) khoản trích thực tế nhỏ hơn giả định của skeptic (TB 2023–25 = 6,23% LNTT, = 87–106 tỷ/năm ở biên 179 tuỳ cửa sổ hồi quy và M, không phải 200–250), (ii) áp đúng thuế suất kỳ trích 20% từ 2027 và độ trễ giải phóng tiền tới 5 năm, (iii) cùng quy tắc đó làm số dư mất 22,1% thay vì 11%.
- **Giá 30.400 (đóng cửa 20/11/2026, DNSE) ⇒ TRONG vùng P10–P90.**
  - Giá cao hơn tâm **+11,0%** và thấp hơn P90 6,6%. 74,5% trọng số kết cục nằm dưới giá.
  - Nhãn **không đổi** so với rev8 (TRONG vùng).
- **Luật sổ giá (giá ≤ 0,85×tâm = 23.284): KHÔNG đạt.** Giá không rẻ.
- **Giá hàm ý biên urê–khí dài hạn ≈ 211 USD/t**, trong dải bền 180–260 (Bobby), 1,18× TB 2016–25 (179).
- **Rủi ro lớn nhất nằm ngoài base: giá khí 2035+.**
  - Biến thể trục 2035+ khai trọng số (§3): tâm **22.574**, P10 **13.902**, P90 31.086 ⇒ giá vẫn TRONG vùng nhưng sát P90.
  - Vùng đọc mở rộng **[13.902 … 32.564]**. **"Không rẻ" đúng ở mọi biến thể.**
- **Sizing (V8, chuẩn 2–4% NAV/mã):** hiện **0%** (không đạt luật 0,85×tâm). Nếu giá ≤ 23.284, xét tranche đầu 2% NAV, chờ user duyệt. HARD ABANDON khi giá > P90 sau CK (32.564).
- Không đủ điều kiện sleeve fear-buy §2.5. Moat NARROW (ADDENDUM_5F 08/11).

## 1. Đính chính so với rev trước
### 1a. Hạng mục skeptic r3 (`skeptic/r3.json`, `skeptic/r3_raw.md`) → xử lý ở rev9
| # | Hạng mục skeptic r3 | Bằng chứng (nguồn độc lập) | Xử lý | Tác động (điểm, đ/cp trước CK) |
|---|---|---|---|---|
| T1 | **Quỹ KH&CN xử lý hai kiểu** (missing_items 1, killer objection): số dư mất 11%, dòng trích hằng năm trong LNST hồi quy mất 100% | **Số trích theo năm, BCTC gốc:** TM25 BCTC HN KT 2025 (`png_r7/kt25_p37.png`): 2024 **44,78** / 2025 **187,99**; sử dụng 39,50 / 75,82; chuyển TSCĐ 11,80 / 13,51. TM QLDN KT 2025 (`kt25_p43`) cũng 187,99. KT 2024 (`png_r9/kt24_p37.png`, cột năm trước): 2023 **108,89**. TM34 Q3/26 (pdf p40): 9T/26 **249,63**, 9T/25 95,41 (số "95,0" mà REPORT_r3 gọi là của năm 2025 thực ra là 9T/25). LNTT (KQKD): 2023 1.254,81 / 2024 1.522,06 / 2025 2.207,43 / 9T/26 2.562,94 ⇒ tỷ lệ trích trên LNTT trước trích **7,98% / 2,86% / 7,85%** (9T/26 8,88%). **Pháp lý:** Luật 67/2025/QH15 Đ17 k2 (thu hồi thuế theo **thuế suất kỳ trích** + lãi **TPKB 5 năm, tính 2 năm**); NĐ 320/2025 Đ22 k2 (cùng lãi suất, kể cả hoàn nhập trước hạn); NĐ 265/2025 Đ13 k5 điểm a, c (được mua máy móc thiết bị đổi mới công nghệ) — nguồn luatvietnam.vn qua legal-vn 23/11 | **(a) Vào base, MỘT quy tắc cho cả số dư và dòng:** mỗi đồng trích gộp có giá trị cho cổ đông **v = (1 − t_kỳ trích×(1+2×Y5)) × ((1+d)/(1+r))^L**. Y5 = 3% (ước lượng), d = 7,40% (lãi huy động neo V1), L = số năm tới khi tiền được giải phóng (tối đa 5 năm theo Đ17 k2). Phần chi cho thiết bị/KH&CN = V4a NPV=0, tức không kém v ⇒ v là cận thận trọng. **Số dư:** tiền quỹ 1.031,63 (= 1.059,37 mã 344 − 27,74 đã hình thành TSCĐ, TM25) × (1 − v(10%, L=2,49, r)); L bình quân theo lớp trích FIFO (2026: 4,75 năm; 2025: 3,75; 2024: 2,75; ≤2023: 1,0 ước lượng) ⇒ mất **22,1%** @r 13,5%. **Dòng:** hồi quy lại trên LN **trước trích** (A 2023–25 từ BCTC KT; 2016–22 ước lượng 6,23% LNTT); tương lai trích 6,23% LNTT trước trích, LNST báo cáo trừ A×(1−t), cổ đông nhận lại A×v(20%, 5 năm, r) = **0,598A** | Số dư: 11% → 22,1% (có độ trễ) **−224**. Dòng: **+744**. Biến thể không độ trễ +476; cách đọc rev7 (mất 100% cả hai) −2.392 |
| T2 | **Đối chiếu chi từ quỹ với capex LCTT mã 21** (trừ trùng với M) | TM25: phần quỹ chuyển sang TSCĐ 13,51 (2025) / 11,80 (2024) — nhiều nhất là phần capex có thể vừa nằm trong M vừa được tài trợ bởi quỹ | **(c) Không đối chiếu được từng dòng** (LCTT không tách nguồn quỹ). Trần ảnh hưởng: 13,5 tỷ/năm × 10,40 đ/cp mỗi tỷ/năm = **≤ +141** trên nhánh M=540 (nhánh M 342/401 là D&A, không phải capex) ⇒ **≤ +47 ở tâm**. Không vào base | ≤ +47 |
| T3 | **D&A lấy từ BQ, không từ BCTC gốc** (data_provenance) | BCTC HN KT 2024, LCTT mã 02, cột năm trước: **D&A 2023 = 1.083,38** (BQ suy 1.063). Chênh +1,9% ⇒ kiểm chéo cho chuỗi BQ 2018–22 | 2023 dùng số gốc. 2018–22 vẫn là BQ (KT 2021–23 vẫn không tải được) | +77 |
| T4 | **NĐ 320/2025, TT 20/2026 chưa kiểm từ nguồn gốc** | legal-vn 23/11 trích nguyên văn (luatvietnam.vn, khớp nguồn thứ cấp TC Kinh tế Tài chính): **NĐ 320/2025/NĐ-CP ngày 15/12/2025 có tồn tại**, Đ22 k2 như T1. **TT 20/2026/TT-BTC ngày 12/3/2026 có tồn tại**, Đ9 chỉ về TSCĐ từ quỹ chuyển sang SXKD; không có điều buộc chi cho hạng mục không tạo giá trị. **Chưa đối chiếu Công báo.** Cảnh báo: có thể NĐ 141/2026 đã sửa NĐ 320, và có dự thảo sửa NĐ 320 (10/2026) — **không kiểm chứng được** nội dung | Cơ sở pháp lý của T1 giữ. Phần lãi đổi từ "≈1 điểm trên số dư" (rev8) sang "TPKB 5 năm × 2 năm trên số thuế" theo đúng văn bản. **Chưa kiểm chứng:** phần quỹ thu hồi có được hoàn nhập vào thu nhập cho doanh nghiệp không phải DNNN (NĐ 265/2025 Đ35 k3 chỉ quy định cho DNNN). Nếu không được hoàn nhập thì quỹ vẫn phải chi cho KH&CN/thiết bị (V4a NPV=0) ⇒ quy tắc v vẫn là cận thận trọng | Y5 0%/5%: +22/−15 |
| T5 | **Hạn thuê đất / giấy phép nhà máy Cà Mau vs chân trời vĩnh viễn** (missing_items 2) | Điều lệ (tài liệu ĐHĐCĐ bất thường 2026, `src/gas/egm2026_tailieu.txt`): thời hạn hoạt động của Tổng công ty **vô thời hạn** (là thời hạn pháp nhân, không phải thời hạn đất). BCTC KT 2024: GCNĐT số 61101000153 ngày 04/12/2012 (UBND Cà Mau) được miễn/giảm tiền thuê đất; tiền thuê đất nộp năm 2024 1,03 tỷ; TM nợ tiềm tàng nhắc "hoàn trả mặt bằng vào cuối thời hạn thuê" nhưng **không nêu ngày**. Mốc 2058 trong BCTC là đất KVF (KCN Hiệp Phước), **không phải** nhà máy Cà Mau | **(c) Không kiểm chứng được** năm hết hạn thuê đất. Ảnh hưởng ước lượng qua độ nhạy vòng đời: dừng 2042 **−1.873**, dừng 2047 **−994** (không giá trị cuối, không gia hạn). Base giữ chân trời vĩnh viễn g=0 vì đất KCN thường gia hạn được và nhà máy đã có nguồn khí PM3 tới 2047 | −0,99…−1,87k (ngoài base) |
| T6 | **Tin pháp lý/quản trị sau 05/11** | Tra 05–23/11 (cafef, vietstock, tinnhanhchungkhoan, nguoiquansat, vneconomy, thanhtra; **chưa mở trực tiếp** hose.vn/pvcfc.com.vn): 05/11 CBTT NQ HĐQT 04/11 nâng kế hoạch 2026 (LNTT 1.320 → 2.419 tỷ, LNST 1.182 → 2.168); 19/11 thông cáo tiêu thụ urê T10 70,4 nghìn tấn, kế hoạch T11 48 nghìn tấn. **Không thấy** thanh tra, vụ án, kỷ luật, đổi nhân sự chủ chốt, SĐBS HĐ khí mới, dừng máy, PVN thoái vốn | Không đổi base (kế hoạch năm 2026 đã nằm trong dữ liệu 9T/26 và trục năm 1). WARNING §9 giữ | — |
| T7 | Hồi quy 2021+ dự báo cao năm KT 2025; tung độ gốc có thể hơi cao | Phần dư mới (LN trước khấu hao, trước trích): r5_2021_25 2024 **+66** / 2025 **−373**; reg_ex22 2024 **−119** / 2025 **−207** tỷ | Không đổi cấu trúc. Rủi ro dự báo cao vẫn còn ⇒ thể hiện qua biến thể M=540/738 và độ nhạy biên | — |

### 1b. Hạng mục skeptic r1/r2 — giữ từ rev7/rev8
- K1 chế độ D&A (+2.833), K1b 2 cửa sổ 2021+, K2 capex duy trì M 342/401/540 (−1.040/100 tỷ/năm), K4 khôi phục tệp đầu vào, S1 dòng BQ 2021Q4 chép (+186), S3 khí 2035+ là biến thể song song, S4 VAT 5% không cộng vào base: **giữ nguyên** (chi tiết `REPORT_rev8.md` §1).
- S2 (quỹ KH&CN trừ 11% số dư) **được thay** bằng quy tắc T1.
- S5 thuyết minh TSCĐ / lịch đại tu: vẫn **chưa đọc** (KT 2025 dạng scan; đã OCR TM25 nhưng chưa đọc TM TSCĐ). Ảnh hưởng qua trục M và độ nhạy vòng đời.

## 2. Cầu nối (đ/cp; điểm tham số trung tâm, trước CK; `calc/model_r9_out.txt` mục 2)
| Bước | Giá trị | Δ |
|---|---|---|
| rev8 điểm (control tái lập 26.776,034) | 26.776 | |
| số dư quỹ: lãi theo luật (TPKB 5 năm × 2 năm), không độ trễ | 26.790 | +14 |
| số dư quỹ: độ trễ giải phóng L = 2,49 năm | 26.566 | −224 |
| T3 D&A 2023 = 1.083,38 (KT 2024) | 26.643 | +77 |
| T1 dòng trích: hồi quy trước trích + trích 6,23% LNTT, nhận lại 0,598A | **27.387** | +744 |
| điểm → kỳ vọng lưới 2.430 kết cục | 27.554 | +167 |
| CK thanh khoản @5 tỷ (0,585%) | **27.393** | −161 |

## 3. Headline + biến thể (sau CK 0,585%; giá 30.400; `calc/compare_px_r9_out.json`)
| Biến thể | Tâm | P10 | P90 | % trọng số < giá | Nhãn |
|---|---|---|---|---|---|
| **H — headline** (2 cửa sổ × M3 × r5 × biên 138/179/220 × năm1 170/222/285 × khí A/B × I_C 20/22/25; quỹ KH&CN quy tắc T1) | **27.393** | **22.065** | **32.564** | 74,5% | **TRONG** |
| trục khí 2035+ 0,5/0,25/0,25 (S3) | 22.574 | 13.902 | 31.086 | 87,3% | TRONG (sát P90) |
| quỹ KH&CN cách đọc rev7 (mất 100% cả số dư lẫn dòng) | 25.009 | 19.891 | 30.011 | 92,1% | TRÊN |
| cách xử lý lai rev8 (control) | 26.780 | 21.662 | 31.782 | 80,4% | TRONG |
| T1 không độ trễ | 27.865 | 22.481 | 33.118 | 70,8% | TRONG |
| chỉ M = 540 | 26.230 | 20.973 | 31.241 | 84,0% | TRONG (sát) |
| M = 738 (toàn bộ capex quan sát) | 24.178 | 18.940 | 29.122 | 96,0% | TRÊN |
| chỉ M = 342 | 28.282 | 23.023 | 33.364 | 67,1% | TRONG |
| 4 cửa sổ (trục r6) | 29.405 | 23.675 | 34.648 | 58,1% | TRONG |
| + P(thuế XK 0%) 0,55 | 28.423 | 23.088 | 33.620 | 66,4% | TRONG |

**Đọc:** ở mọi biến thể giá > tâm và giá > 0,85×tâm ⇒ **"không rẻ" chắc chắn**. "TRONG vùng" phụ thuộc giả định quỹ KH&CN (cách đọc rev7 ⇒ TRÊN) và capex duy trì cao (M=738 ⇒ TRÊN).

## 4. Độ nhạy (Δ so điểm base 27.387, trước CK; `model_r9_out.txt` mục 5)
- **V1 r gắn lãi huy động:** r = 13,5% tại lãi huy động 12T hiệu dụng 7,40% (`deposit_rate_vn`, cctg_12m 2026-11-02, cập nhật 16/11, đọc 23/11) ⇒ Δ = 0.
  - β=1: ±50bp **−559 / +604**; ±100bp **−1.077 / +1.258**. β=0,5: +100bp −559.
  - Hai đầu dải Ke 12,3–13,4%: **+1.535 / +117**.
- **Quỹ KH&CN (T1):** không độ trễ +476 · tỷ lệ trích 2023/2024/2025/9T26: −69 / +132 / −63 / −103 · tỷ lệ 2016–22 0% / 10%: −23 / +15 · trích 20% (trần luật mới) −592 · Y5 0% / 5%: +22 / −15 · bỏ phần dòng −743 · cách đọc rev7 −2.392.
- **Tăng:** thuế XK 0% P=0,55 +1.033 · 4 cửa sổ +2.024 · trần trừ trùng quỹ–capex ≤ +47.
- **Giảm (ngoài base):** khí 2035+ phẳng −7.606, leo thang −11.364 · vòng đời/đất dừng 2042 −1.873, 2047 −994 · phong toả 332 −627 · capex duy trì **−1.040 mỗi 100 tỷ/năm** · D&A 2023 theo BQ −76.

## 5. Thanh khoản (V3) — không đổi rev8
- DNSE OHLC 1D 2025-11-19..2026-11-20 (`calc/dnse_ohlc_r7.csv`): ADV trung vị 250 phiên **89,0 tỷ**, 60 phiên 73,7 tỷ; σ ngày 2,47%.
- CK căn bậc hai: 5 tỷ **0,585%** (ADV60 0,643%); 2 tỷ 0,37%; 1 tỷ 0,26%. Thoát 5 tỷ @15% tham gia: 0,37 phiên. Nhãn như nhau ở mọi cỡ sleeve 2–4% NAV.

## 6. V6 — hai nền (CHỈ HIỂN THỊ; không đổi rev7)
- V_ngắn 27.422 (LNST trung vị 2024/2025/TTM 1.959,8 tỷ; g=0) · V_dài 2.196 (FCFE TB 3 kỳ 156,9 tỷ) · D = 2,53 > ln3 ⇒ phân kỳ mạnh do vốn lưu động 2025 + capex tăng trưởng. Không đọc là cảnh báo đắt.
- Lưu ý T1: chi từ quỹ KH&CN (75,8 tỷ năm 2025) là dòng tiền ra không qua P&L; đã nằm trong CFO/capex của V6.

## 7. Vị thế & lợi thế cạnh tranh (V5 — 5F)
- Tái dùng `ADDENDUM_5F.md` (07–08/11, dưới 12 tháng): **NARROW · COST/LOCATION · không bền**. Terminal RONIC = Ke, g thực = 0.
- Kiểm 23/11 (T6): không có dữ kiện mới đổi 5F.

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON
- **NÂNG:** thuế XK 0% (+1,0…+1,9k); SĐBS 12 bản ký theo kịch bản rẻ / Nam Du ≤ 30% (tới +4,0k); văn bản giá khí sau 2034 ≤ công thức Đ9.1; lãi huy động 12T −100bp (+1,3k); DCM dùng quỹ KH&CN đúng hạn cho thiết bị (bỏ độ trễ, +0,5k).
- **HẠ:** khí sau 2034 theo giá Nam Du (−7,6…−11,4k); capex duy trì > 540/năm (−1,04k mỗi 100 tỷ/năm); kế hoạch dừng/đại tu lớn hoặc hạn thuê đất Cà Mau trước 2047 (−1,0…−1,9k); văn bản sửa NĐ 320 buộc chi quỹ cho hạng mục không tạo giá trị (tới −2,4k); Nam Du ≥ 60,5% + V2 (−3,5k).
- **HARD ABANDON:** không mở vị thế khi giá > P90 sau CK (**32.564**). Làm lại định giá nếu: dừng máy/hụt khí > 60 ngày; PVN thoái vốn đổi HĐ khí; SĐBS 12 bản ký khác dự thảo về giá Nam Du.
- **Hết hạn DD:** BCTC Q4/2026 hoặc dd_date + 120 ngày.

## 9. Pháp lý / quản trị — WARNING, không vào base
- Giữ rev8 §9: HĐ khí bên liên quan khép kín PVN → PV GAS → DCM, ĐHĐCĐ uỷ quyền HĐQT sửa nội dung cơ bản; SĐBS 12 mới là dự thảo; 332 tỷ bị hạn chế tại MBV; thù lao ×3,25; phải thu PVN tăng; sau 24/4/2032 không còn khối lượng cam kết.
- **Tra lại 05–23/11 (T6):** không thấy sự kiện pháp lý/quản trị bất lợi mới.
- Quỹ KH&CN 1.059,4 tỷ: chi 2024 51,3 / 2025 89,3 / 9T26 ≈ 47,5 tỷ so với trích 44,8 / 188,0 / 249,6 ⇒ lớp ≤2023 (≈ 549 tỷ, ước lượng FIFO) có nguy cơ bị thu hồi thuế trong 1–2 năm — đã phản ánh qua v.

## 10. Khoá + sản phẩm
- **Khoá giả định:** `assumptions_r9.json` (dd_assumptions_v1; lint **0 vi phạm**), `calc/LOCK_r9_md5.txt` (bản trước `LOCK_r9a_pre2023_md5.txt`).
- **Mô hình:** `calc/model_r9.py` (dựng trên `model_r8.py` khoá LOCK_r8, không sửa file khoá). Output `model_r9_out.txt/.json` chạy 2 lần trùng md5 `7f8fc1c76a7cea6dc1d3b1eff1d99991`; threads=1. Control tắt T1 tái lập điểm rev8 **26.776,034**.
- **Pha giá:** `calc/compare_px_r9.py` → `compare_px_r9_out.json`.
- **Trang BCTC đã đọc thêm:** KT 2025 p12 KQKD, p37 TM25 quỹ KH&CN, p43 TM QLDN; Q3/26 pdf p08 KQKD, p40 TM34; KT 2024 p12, p13, p37, p43 (`png_r9/`).
- **Không kiểm chứng được:** năm hết hạn thuê đất Cà Mau (T5); hoàn nhập quỹ thu hồi cho doanh nghiệp không phải DNNN (T4); NĐ 141/2026 / dự thảo sửa NĐ 320; đối chiếu Công báo; D&A gốc 2018–22; thuyết minh TSCĐ / lịch đại tu; giá khí sau 2034; lợi suất TPKB 5 năm (Y5 = 3% ước lượng).
