# DD — DCM (PVCFC) · as-of 23/11/2026 · **rev8** · áp verdict fundamental-skeptic r1 (22/11, REFUTED) + r2 (23/11, INCONCLUSIVE) · job `Taylor_20261122_234422`

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ, không phải khuyến nghị. Không đặt lệnh, không email, không ghi `kb/dd_price_zones.json` (đề xuất sổ: `LEDGER_PROPOSAL_DCM.json`).
> rev8 **thay** `REPORT_rev7.md` (23/11, skeptic r2), `REPORT_r6.md` (08/11) và báo cáo NĐT `investor_report/DCM_DD_investor_report_20261105.md` (bản skeptic r1).
> **Phần giữ nguyên r6, có dẫn nguồn:** hợp đồng khí 3918 / SĐBS 12 dự thảo, lịch giá khí 2026–34, pháp lý §7.
> **Thứ tự mù giá — trung thực:**
> - rev7 khoá giả định lúc 06:53 ICT (`calc/LOCK_r7_md5.txt`) rồi mới đọc giá DNSE 30.400.
> - rev8 sửa sau khi tôi **đã biết** giá đó. Cả 3 sửa đổi (S1–S3) là đính chính do skeptic r2 nêu, mỗi cái có nguồn độc lập và không nhận giá làm đầu vào (`calc/model_r8.py` không đọc giá).
> - Khoá rev8 nằm ở `calc/LOCK_r8_md5.txt`, ghi trước khi chạy `calc/compare_px_r8.py`.
> **Nguồn BCTC:** mới nhất là HN Q3/2026 (15/10/2026). BCTC năm đã kiểm toán: FY2025, Deloitte, chấp nhận toàn phần ⇒ `audited_fy_missing = false`.

## 0. Kết luận
- **Tâm 26.780 đ/cp sau CK thanh khoản** (26.937 trước CK), kỳ vọng lưới 2.430 kết cục.
  - **P10 21.662 · P25 23.891 · P50 26.831 · P75 29.732 · P90 31.782** (sau CK, mức kết cục).
  - So với rev7 (24.822): **+7,9%**, cầu nối ở §2.
- **Giá 30.400 (đóng cửa 20/11/2026, DNSE) ⇒ TRONG vùng P10–P90.**
  - Giá cao hơn tâm **+13,5%** và thấp hơn P90 4,4%. 80,4% trọng số kết cục nằm dưới giá.
  - **Đổi lớp nhãn so với rev7/r6** (TRÊN vùng → TRONG vùng). Nguyên nhân: sửa quỹ KH&CN theo cơ sở pháp lý (+1.781) và dòng BQ chép (+186). Giá giảm 32.100 → 30.400 cũng góp phần.
- **Luật sổ giá (giá ≤ 0,85×tâm = 22.763): KHÔNG đạt.** Giá không rẻ.
- **Giá hàm ý biên urê–khí dài hạn ≈ 219 USD/t.** Mức này nằm **trong** dải bền 180–260 (Bobby), bằng 1,22× TB 2016–25 (179).
- **Rủi ro lớn nhất nằm ngoài base: giá khí 2035+.**
  - Biến thể có trục 2035+ khai trọng số (§3) ra tâm **21.961**, P10 **13.410**, P90 30.345 ⇒ giá thành **TRÊN vùng**.
  - Vùng đọc vì vậy mở rộng thành **[13.410 … 31.782]**. **Kết luận "không rẻ" đúng ở mọi biến thể; "nằm trong vùng" thì không.**
- **Sizing (V8, chuẩn 2–4% NAV/mã):** hiện **0%**, vì không đạt luật 0,85×tâm.
  - Nếu giá ≤ 22.763, xét tranche đầu 2% NAV, chờ user duyệt.
  - HARD ABANDON khi giá > P90 sau CK (31.782).
- Không đủ điều kiện sleeve fear-buy §2.5. Moat NARROW (ADDENDUM_5F 08/11).

## 1. Đính chính so với rev trước
### 1a. Hạng mục skeptic r1 (`skeptic/r1.json`), áp ở rev7, giữ ở rev8
| # | Hạng mục | Bằng chứng (nguồn) | Xử lý | Tác động (điểm, đ/cp) |
|---|---|---|---|---|
| K1 | Nền LN trộn 2 chế độ khấu hao | **D&A KT** 2024 268,08 / 2025 342,07 (BCTC HN KT 2025 LCTT mã 02, `png_r7/kt25_p13.png`); 9T/26 301,07 (BCTC Q3/26 LCTT mã 02, `png_r7/q326_p09.png`). **2018–23 suy từ BQ** (EBITDA_P0 − EBITM_P0×DT TTM quý 4, `calc/bq_da_r7.sql`): 1.287 / 1.311 / 1.305 / **1.316** (2021, xem S1) / 1.274 / 1.063. **Kiểm khấu hao luỹ kế:** CĐKT KT 2025, TSCĐHH nguyên giá 16.958,8, hao mòn 15.220,6 (89,8%) ⇒ nhất quán với chuỗi BQ thô. Skeptic r2 cũng kiểm: tổng D&A 2016–25 ≈ 10,6–10,8 nghìn tỷ khớp luỹ kế, **bác** biến thể hiệu chỉnh ×1/0,83 | **(a) Vào base.** Hồi quy lại trên NP + D&A×(1−10,8%), trừ lại M×(1−10,8%). BCTC KT 2021–23 **không tải được** (pvcfc.com.vn chặn Cloudflare; cafef/vietstock render JS) ⇒ 2018–23 = BQ, kiểm chéo bằng luỹ kế. 2016–17 BQ nhiễu ⇒ TB 2018–20 (ước lượng; chỉ dùng ở biến thể 4 cửa sổ) | M=342: +2.833 (rev7) |
| K1b | Cửa sổ hồi quy | Sau khi cộng D&A, cửa sổ có 2016–20 cho phần dư 2024/2025 (năm KT) **−476/−678** (2016–25) và **−374/−231** (2016–25 trừ 2022) tỷ: dự báo quá cao. Cửa sổ 2021+: +98/−406 và −79/−247 (`calc/model_r8_out.txt` mục 1). `model_r5.bias_hist()` hiệu chỉnh khí trên 2021–25 | Headline = **2 cửa sổ 2021+**. 4 cửa sổ = biến thể (§3) | 4 cửa sổ: +2.044 |
| K2 | Capex duy trì / vòng đời | Capex (LCTT mã 21): 2024 791,15, 2025 694,64 (KT), 9T/26 545,94. **TM16 Q3/26:** phần tăng trưởng nhận diện được (Nhơn Trạch +31,4, khí CN +98,0, Thạnh Hoá +11,7) ⇒ duy trì ≤ 540/năm. Chắc chắn duy trì (HTS/LTS +152,4, khác +18,7) ⇒ ≥ 228/năm | FCF = LNST tại D&A = M. **Trục M ∈ {342,07; 401,4; 540}**, trọng số đều. Capex tăng trưởng NPV=0 (V4a). Vòng đời: không có cơ sở ⇒ độ nhạy | −907 (rev7). Đơn vị **−1.056 / 100 tỷ/năm**. Dừng 2042 −1.781 |
| K3 | Quỹ KH&CN 1.059 | Xem **S2** (rev8 sửa lại cách xử lý của rev7) | | |
| K4 | Tệp đầu vào mất | Khôi phục bằng `git archive 906dfecd0^` (TRIM_DD 19/11), md5 khớp LOCK_r6 | Control: `model_r7` với M=None, không trừ quỹ, tái lập điểm r6 **24.818,114** | — |
| K5 | Bản bị phản biện đã bị thay | — | rev8 thay mọi bản trước | — |

### 1b. Hạng mục skeptic r2 (`skeptic/r2.json`, INCONCLUSIVE), áp ở rev8
| # | Hạng mục skeptic r2 | Bằng chứng | Xử lý | Tác động |
|---|---|---|---|---|
| S1 | Dòng BQ 2021Q4 chép y nguyên 2021Q3 ⇒ D&A 2021 = 1.127,8 là số giả | `calc/bq_da_r7_out.csv`: 2021Q3 và 2021Q4 có cùng EBITDA_P0 2.339,136 và EBITM_P0 0,11907 | `model_r8` tự phát hiện (quý 4 trùng quý 3 ⇒ dùng quý 3): D&A 2021 = **1.316,1** | **+186** (+0,7%) |
| S2 | Cơ sở pháp lý cho việc trừ quỹ KH&CN (−2.001) chưa kiểm | **legal-vn 23/11** (thông tin tham khảo): Luật thuế TNDN **67/2025/QH15 Đ17** (hiệu lực 01/10/2025; khung cũ TT 67/2022) quy định quỹ **không phải nghĩa vụ chi 100%**. Dùng < 70% trong 5 năm hoặc sai mục đích ⇒ nộp thuế TNDN trên phần đó **theo thuế suất kỳ trích** + lãi. Quỹ được dùng mua máy móc, thiết bị đổi mới công nghệ. Kết luận định giá = (b): **chỉ mất phần thuế + lãi**. Thuế suất kỳ trích của DCM là 10% (ưu đãi tới hết 2026, BCTC Q3/26 tr.17) | **Base trừ 11% số dư** (10% thuế + ≈1 điểm lãi, ước lượng) = 116,5 tỷ. Phần ≥ 70% chi cho thiết bị/KH&CN theo V4a NPV=0. Chưa kiểm chứng: NĐ 320/2025, TT 20/2026, kỳ hạn trái phiếu tính lãi | **+1.781** so với rev7 (trừ 100%). Độ nhạy: 0% +220; 20% −180; 100% −1.781 |
| S3 | Giá khí 2035+ trong base là ước lượng không có hợp đồng; −31…−46% | **Cơ sở của base:** công thức giá HĐ 3918 Đ9.1 hiện hành (PM3 = 50% quyền nhận PVN @46% MFO + 50% phần Malaysia @13,7% Brent). Đây đúng là cấu trúc năm 2028 đã cố định trong `model_r5`. Nguồn PM3 còn tới 2047: PSC PM3-CAA gia hạn tới 31/12/2047 (`src/gas/dl_1844450.txt:435`, REPORT_r5:127). **Không có:** khối lượng cam kết sau 24/4/2032 (PL12 Đ4.1(b)) và văn bản giá sau 2034 | **Base giữ cấu trúc hợp đồng hiện hành**, cùng nguyên tắc "luật/hợp đồng hiện hành" như thuế XK 5% ở r6. **Trục 2035+ khai trọng số chạy song song:** 0,5 hiện hành / 0,25 Nam Du phẳng 10,39 / 0,25 Nam Du leo thang 2,25%/năm (ước lượng, không có cơ sở chọn) ⇒ **mở rộng vùng đọc** (§0, §3). Không vào tâm, vì giảm cần cơ sở độc lập mà trọng số là phán đoán | Biến thể: tâm **21.961** (−18%), P10 13.410. Phẳng −7.606, leo thang −11.364 |
| S4 | Chế độ VAT 5% từ 07/2025 (khấu trừ VAT đầu vào) chưa vào hồi quy | **Kiểm bằng dữ liệu:** TTM Q3/26 là 12 tháng đủ chế độ VAT 5%. LNST mẹ TTM **2.716,7** (BCTC Q3/26 + KT 2025 − 9T/25); D&A TTM 397,1. Dự báo hồi quy tại biên proxy TTM 319,1 (ước lượng, WB năm): 2.996,4 (2021–25) / 2.631,2 (2021–25 trừ 2022) ⇒ **phần dư −9,3% / +3,2%** (`model_r8_out.txt` mục 3) | Kỳ có VAT 5% **không** cho thấy biên vượt hồi quy ⇒ **không có cơ sở cộng vào base**. Không định lượng riêng, vì hiệu ứng (nếu có) đã nằm trong năm 1 | — |
| S5 | Thuyết minh TSCĐ (thời gian khấu hao còn lại, đại tu) | Chưa đọc (bản KT 2025 dạng ảnh scan) | **Không kiểm chứng được** trong phiên. Ảnh hưởng thể hiện qua trục M và độ nhạy vòng đời (−0,9…−1,8k) | — |

## 2. Cầu nối (đ/cp; điểm tham số trung tâm, trước CK; `calc/model_r7_out.txt` mục 2 + `model_r8_out.txt` mục 2)
| Bước | Giá trị | Δ |
|---|---|---|
| r6 điểm base (4 cửa sổ, control) | 24.818 | |
| 2 cửa sổ 2021+ (K1b) | 24.883 | +65 |
| + chế độ D&A, M = 342 (K1) | 27.716 | +2.833 |
| M = 401 (K2) | 27.089 | −627 |
| − quỹ KH&CN 100% (cách đọc rev7) | 25.088 | −2.001 |
| lưới M 342/401/540 = điểm rev7 | 24.809 | −280 |
| S1 sửa D&A 2021 | 24.995 | +186 |
| S2 quỹ KH&CN chỉ trừ 11% | **26.776** | +1.781 |
| điểm → kỳ vọng lưới 2.430 kết cục | 26.937 | +161 |
| CK thanh khoản @5 tỷ (0,585%) | **26.780** | −157 |

LNST dài hạn @ biên 179, M=401, TB 2 cửa sổ: r6 1.328 → rev8 **1.517 tỷ**.

## 3. Headline + biến thể (sau CK 0,585%; giá 30.400; `calc/compare_px_r8_out.json`)
| Biến thể | Tâm | P10 | P90 | % trọng số < giá | Nhãn |
|---|---|---|---|---|---|
| **H — headline** (2 cửa sổ × M3 × r5 × biên 138/179/220 × năm1 170/222/285 × khí A/B × I_C 20/22/25) | **26.780** | **21.662** | **31.782** | 80,4% | **TRONG** |
| **trục khí 2035+ 0,5/0,25/0,25** (S3) | **21.961** | **13.410** | 30.345 | 90,2% | **TRÊN** |
| quỹ KH&CN trừ 100% (rev7) | 25.009 | 19.891 | 30.011 | 92,1% | TRÊN (sát) |
| chỉ M = 540 | 25.599 | 20.537 | 30.381 | 90,2% | TRÊN (sát) |
| M = 738 (toàn bộ capex quan sát) | 23.514 | 18.428 | 28.251 | 98,3% | TRÊN |
| chỉ M = 342 | 27.683 | 22.619 | 32.525 | 72,8% | TRONG |
| 4 cửa sổ (trục r6) | 28.811 | 23.247 | 33.899 | 64,4% | TRONG |
| + P(thuế XK 0%) 0,55 | 27.810 | 22.661 | 32.828 | 72,2% | TRONG |
| quỹ KH&CN trừ 0% | 26.998 | 21.881 | 32.001 | 78,8% | TRONG |

**Đọc:**
- Ở **mọi** biến thể, giá > tâm và giá > 0,85×tâm ⇒ **"không rẻ" là chắc chắn**.
- "TRONG vùng" chỉ đúng khi giá khí sau 2035 giữ cấu trúc hợp đồng hiện hành. Biến thể 2035+, M cao và quỹ 100% đều đưa giá lên sát hoặc trên P90.

## 4. Độ nhạy (Δ so điểm base 26.776, trước CK; `model_r8_out.txt` mục 5)
- **V1 r gắn lãi huy động:**
  - r = 13,5% tại neo 03/11 (lãi huy động 12T hiệu dụng 7,40%). Nguồn: `deposit_rate_vn.effective_deposit_rate()` đọc 23/11 (cctg_12m 2026-11-02, big4 6,80%, cập nhật 16/11) ⇒ Δ = 0, r giữ 13,5%.
  - β=1: ±50bp **−497 / +538**; ±100bp **−958 / +1.122** (−3,6% / +4,2%). β=0,5: ±100bp −497 / +538.
  - **Hai đầu dải Ke 12,3–13,4% (D4):** +1.369 / +104 (báo kèm).
- **Tăng:**
  - Thuế XK 0%: P=0,55 +1.033; chắc chắn +1.879.
  - 4 cửa sổ +2.044.
  - Quỹ KH&CN trừ 0%: +220.
  - Nam Du 30% + V1: tới +4,0k (r6).
- **Giảm (ngoài base):**
  - **Khí 2035+:** phẳng −7.606, leo thang −11.364.
  - Quỹ KH&CN 100%: −1.781.
  - Vòng đời dừng 2042: −1.781; 2047: −945.
  - Phong toả 332: −627.
  - Thuế lịch sử 5% (ước lượng): ≈ −1,1k (rev7).
  - Nam Du 60,5% + V2: −3,5k (r6).
  - Capex duy trì: **−1.056 cho mỗi 100 tỷ/năm**.

## 5. Thanh khoản (V3; DNSE OHLC 1D 2025-11-19..2026-11-20, `calc/dnse_ohlc_r7.csv`)
- **Thông số:** ADV trung vị 250 phiên **89,0 tỷ**, 60 phiên 73,7 tỷ; σ ngày 2,47%.
- **Chiết khấu (luật căn bậc hai):** 5 tỷ (5,6% ADV) **0,585%** (ADV60 0,643%); 2 tỷ 0,37%; 1 tỷ 0,26%.
- Thoát 5 tỷ ở mức tham gia 15%: 0,37 phiên.
- Nhãn như nhau ở mọi cỡ sleeve 2–4% NAV.

## 6. V6 — hai nền (CHỈ HIỂN THỊ; không đổi so với rev7, `calc/model_r7_out.txt` mục 5)
| Nền | Giá trị (đ/cp) | Cơ sở |
|---|---|---|
| V_ngắn (LNST trung vị 2024/2025/TTM Q3/26 = 1.959,8 tỷ; g=0; r 13,5%) | 27.422 | |
| V_dài (FCFE TB 3 kỳ = CFO − capex = 156,9 tỷ) | 2.196 | CFO 77,5 / −775,8 / 3.572,4; capex 791,1 / 694,6 / 917,5 |
| V theo C4 — *chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi* | 8.687 | |

- **D = 2,53 > ln3 ⇒ "phân kỳ mạnh".** Luật 0,85×tâm không tự kích hoạt; cần Mike/user phán đoán.
- **Nguồn chênh:** vốn lưu động. Năm 2025 tồn kho +1.903 và phải thu +1.139 làm CFO −776 (LCTT KT 2025); 9T/26 đảo chiều. Thêm capex tăng trưởng (TM16).
- ⇒ **"FCFE thấp vì vốn lưu động + đầu tư tăng trưởng (capex)", đừng đọc là cảnh báo đắt.**

## 7. Vị thế & lợi thế cạnh tranh (V5 — 5F)
- Tái dùng `ADDENDUM_5F.md` (07–08/11, dưới 12 tháng): **NARROW · COST/LOCATION · không bền**, không thưởng, không trừ. Terminal RONIC = Ke, g thực = 0.
- **Kiểm nhanh 23/11:** không có dữ kiện mới đổi 5F. Rủi ro số 1 vẫn là đồng hồ khí 2027/2032/2035+.
- K1 xác nhận ROE/ROIC cao 2024–26 một phần do nhà máy đã khấu hao 90%, không phải rào cản.

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON
- **NÂNG:**
  - Thuế XK 0% (+1,0…+1,9k).
  - SĐBS 12 bản ký theo kịch bản rẻ / Nam Du ≤ 30% (tới +4,0k).
  - Văn bản xác nhận giá khí sau 2032/2035 ≤ công thức Đ9.1 (bỏ rủi ro 2035+).
  - Lãi huy động 12T −100bp (+1,1k).
- **HẠ:**
  - Không có khí theo công thức Đ9.1 sau 2034, mua theo giá Nam Du (−7,6…−11,4k).
  - Capex duy trì thực tế > 540/năm (−1,06k mỗi 100 tỷ/năm).
  - Kế hoạch dừng/đại tu lớn (−0,9…−1,8k).
  - Quy định mới (NĐ 320/2025, TT 20/2026) buộc chi quỹ KH&CN cho hạng mục không tạo giá trị (tới −1,8k).
  - Nam Du ≥ 60,5% + V2 (−3,5k).
- **HARD ABANDON:**
  - Không mở vị thế khi giá > P90 sau CK (**31.782**).
  - Làm lại định giá nếu: dừng máy/hụt khí công bố > 60 ngày; PVN thoái vốn đổi HĐ khí; SĐBS 12 bản ký khác dự thảo về giá Nam Du.
- **Hết hạn DD:** BCTC Q4/2026 hoặc dd_date + 120 ngày.

## 9. Pháp lý / quản trị — WARNING, không vào base
- Giữ r6 §7:
  - HĐ khí là giao dịch bên liên quan khép kín PVN → PV GAS → DCM; ĐHĐCĐ uỷ quyền HĐQT sửa nội dung cơ bản.
  - SĐBS 12 mới là dự thảo.
  - 332 tỷ bị hạn chế tại MBV.
  - Thù lao ×3,25.
  - Phải thu PVN tăng.
  - Sau 24/4/2032 không còn khối lượng cam kết.
  - Nhân sự.
- **Không tra lại tin pháp lý** từ 04–05/11.
- Quỹ KH&CN tăng 857,2 → 1.059,4 tỷ trong 9T/26: trích nhanh hơn chi ⇒ theo dõi ngưỡng 70%/5 năm.

## 10. Khoá + sản phẩm
- **Khoá giả định:** `assumptions_r8.json` (dd_assumptions_v1; lint **0 vi phạm**), `calc/LOCK_r8_md5.txt`.
- **Mô hình:** `calc/model_r8.py` (dựng trên `model_r7.py` đã khoá LOCK_r7). Output `model_r8_out.txt/.json`, chạy 2 lần trùng byte; threads=1.
- **Pha giá:** `calc/compare_px_r8.py` → `compare_px_r8_out.json`.
- **Trang BCTC đã đọc** (`png_r7/`): KT 2025 p10 CĐKT, p13 LCTT; Q3/26 p05–06 CĐKT, p08 KQKD, p09 LCTT, p29 TM16.
- **Không kiểm chứng được:**
  - D&A gốc 2021–23 (BCTC KT không tải được; BQ có kiểm chéo bằng luỹ kế).
  - Thuyết minh TSCĐ / lịch đại tu.
  - NĐ 320/2025, TT 20/2026 (quỹ KH&CN).
  - Giá khí sau 2034.
