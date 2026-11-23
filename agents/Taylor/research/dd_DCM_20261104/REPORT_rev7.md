# DD — DCM (PVCFC) · as-of 23/11/2026 · **rev7** · áp verdict fundamental-skeptic DD_GENERAL r1 (22/11, REFUTED) · job `Taylor_20261122_234422`

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ, không phải khuyến nghị. Không đặt lệnh, không email, không ghi `kb/dd_price_zones.json` (đề xuất sổ ở `LEDGER_PROPOSAL_DCM.json`).
> rev7 **thay** `REPORT_r6.md` (08/11) và báo cáo NĐT `investor_report/DCM_DD_investor_report_20261105.md` (bản skeptic r1 đã phản biện). Phần không nhắc ở đây (hợp đồng khí 3918 / SĐBS 12 dự thảo, lịch giá khí, pháp lý §7 r6) **giữ nguyên** theo r6, có dẫn nguồn.
> **Thứ tự mù giá:** giả định khoá ở `calc/LOCK_r7_md5.txt` lúc **06:53:17 ICT 23/11**. `calc/model_r7.py` không đọc giá; giá DNSE chỉ đọc sau đó trong `calc/compare_px_r7.py`. Tôi đã biết các mức giá cũ (33.000 ở r1–r5; 32.100 ở r6) từ các bản trước.
> BCTC mới nhất: HN Q3/2026 (15/10/2026). BCTC năm gần nhất đã kiểm toán: FY2025, Deloitte, chấp nhận toàn phần ⇒ `audited_fy_missing = false`.

## 0. Kết luận
- **Tâm 24.822 đ/cp sau CK thanh khoản** (24.968 trước CK). Đây là kỳ vọng của lưới 2.430 kết cục. **P10 19.763 · P25 22.124 · P50 24.919 · P75 27.627 · P90 29.644** (sau CK, mức kết cục).
- Tâm trùng số với r6 (24.822) **do bù trừ, không phải không đổi**:
  - Sửa chế độ khấu hao: **+2.833**.
  - Capex duy trì: **−627**.
  - Lưới capex duy trì M: **−280**.
  - Trừ quỹ KH&CN: **−2.001**.
  - Chi tiết: cầu nối §2.
- **Giá 30.400 (đóng cửa 20/11/2026, DNSE) ⇒ TRÊN vùng (> P90 +2,6%)**, cao hơn tâm +22,5%. 94,0% trọng số kết cục nằm dưới giá.
- **Luật sổ giá (giá ≤ 0,85×tâm = 21.099): KHÔNG đạt.**
- **Giá hàm ý biên urê–khí dài hạn ≈ 243 USD/t.** Mức này nằm **trong** dải bền 180–260 (Bobby), nhưng là 1,35× TB 2016–25 (179).
- **So với r6** (giá hàm ý ≈ 282, ngoài dải bền): khoảng cách giá–giá trị **hẹp đi rõ**. Nguyên nhân là sửa D&A, cộng với giá giảm 32.100 → 30.400.
- **Nhãn không đổi lớp** (r6 cũng TRÊN vùng), nhưng bây giờ **phụ thuộc biến thể**:
  - 4 cửa sổ hồi quy (tâm 26.787, P90 31.768) ⇒ TRONG vùng.
  - Không trừ quỹ KH&CN (P90 31.634) ⇒ TRONG vùng.
  - Chiều ngược lại: chỉ M=540 (P90 28.262) ⇒ TRÊN rõ.
  - Đầy đủ ở §3.
- **Sizing (V8, chuẩn 2–4% NAV/mã):** hiện **0%**, vì giá > P90 nên HARD ABANDON. Nếu giá ≤ 0,85×tâm (21.099) thì xét tranche đầu 2% NAV, chờ user duyệt.
- Không đủ điều kiện sleeve fear-buy §2.5: không có sự kiện sợ hãi. Moat NARROW (ADDENDUM_5F, 08/11).

## 1. Đính chính so với rev trước — từng hạng mục skeptic r1 (`skeptic/r1.json`, `skeptic/r1_raw.md`)
| # | Hạng mục skeptic | Bằng chứng độc lập (nguồn) | Xử lý | Tác động (đ/cp, điểm) |
|---|---|---|---|---|
| K1 | **Nền LN trộn 2 chế độ khấu hao** (killer objection): D&A ≈1,1–1,3 nghìn tỷ 2021–23 vs ≈0,23–0,30 sau đó | **D&A kiểm toán:** 2024 **268,08** / 2025 **342,07** tỷ (BCTC HN KT 2025, LCTT mã 02, `png_r7/kt25_p13.png`); 9T/26 **301,07** (BCTC Q3/26 LCTT mã 02, `png_r7/q326_p09.png`). **2018–23 suy từ BQ:** EBITDA_P0 − EBITM_P0×DT TTM ở quý 4 (`calc/bq_da_r7.sql` → `_out.csv`), ra 1.287 / 1.311 / 1.305 / **1.128 / 1.274 / 1.063**. **Đối chiếu BQ với KT:** 2024 0,86×, 2025 0,80× ⇒ BQ đánh **thấp** D&A, nên điều chỉnh dùng BQ là cận dưới. **Kiểm chéo bằng CĐKT KT 2025:** TSCĐHH nguyên giá 16.958,8 tỷ, hao mòn luỹ kế 15.220,6 tỷ (đã khấu hao **89,8%**), nhất quán với ~1,2–1,3 nghìn tỷ/năm trong ~12 năm từ 2012 | **(a) Vào base.** Hồi quy lại trên LN trước khấu hao: NP + D&A×(1−10,8%), rồi trừ lại M×(1−10,8%) với M là mức capex duy trì (K2). **BCTC KT 2021–23 không tải được** (pvcfc.com.vn chặn Cloudflare; cafef/vietstock render bằng JS, thử 23/11) ⇒ 2018–23 là số suy từ BQ, **cần kiểm chứng**. 2016–17 BQ nhiễu (952 / 1.870) ⇒ dùng TB 2018–20 = 1.301 (ước lượng) | M=342: **+2.833** (+11,4%; skeptic ước +12%). Biến thể hiệu chỉnh BQ theo tỷ lệ KT (×1/0,83): **+934** thêm, chỉ là độ nhạy |
| K1b | (phát sinh khi sửa K1) cửa sổ hồi quy | Sau khi cộng D&A, hai cửa sổ có 2016–20 **dự báo quá cao** 2 năm đã kiểm toán: phần dư 2024/2025 = **−463/−651** (2016–25) và **−350/−162** (2016–25 trừ 2022) tỷ. Hai cửa sổ 2021+ thì −100…+121 / −374…−176 (`calc/model_r7_out.txt` mục 1). `model_r5.bias_hist()` (hiệu chỉnh chi phí khí của hồi quy) chỉ tính trên 2021–25 ⇒ hai cửa sổ có 2016–20 không nhất quán với khối khí | Headline dùng **2 cửa sổ 2021+** (2021–25; 2021–25 trừ 2022). 4 cửa sổ (trục r6) chuyển thành **biến thể song song**. Đây là điều chỉnh GIẢM, có cơ sở là phần dư trên năm kiểm toán + cửa sổ hiệu chỉnh khí; **không** chọn theo chiều giá | 4 cửa sổ: **+1.977** (độ nhạy) |
| K2 | **Capex thay thế / vòng đời nhà máy** chưa vào dòng vĩnh viễn; capex 9T/26 546 vs D&A ≈300 | Capex (LCTT mã 21): 2024 **791,15**, 2025 **694,64** (KT), 9T/26 **545,94**. **TM16 BCTC Q3/26** (XDCB dở dang): tăng trưởng nhận diện được = Nhơn Trạch +31,4, khí CN +98,0, Thạnh Hoá +11,7 ⇒ phần duy trì 9T/26 **≤ 404,8** (≤ 540/năm). Chắc chắn duy trì = HTS/LTS +152,4, công trình khác +18,7 ⇒ **≥ 228/năm** (chưa gồm mua TSCĐ trực tiếp) | **(a) Vào base:** FCF = LNST(tại D&A = M) với M = capex duy trì ở trạng thái dừng. **Trục lưới M ∈ {342,07 (D&A 2025 KT); 401,4 (D&A 9T/26 năm hoá); 540 (cận trên khung TM16)}**, trọng số đều. Capex tăng trưởng (Nhơn Trạch, khí CN, nâng công suất/NPK) theo V4a: NPV=0 ở giá sổ sách. **(b) Vòng đời:** không có cơ sở độc lập về năm dừng ⇒ chỉ là độ nhạy | M 342→401: **−627**; lưới M: **−280** thêm. Đơn vị: **−1.056 / 100 tỷ/năm**. Toàn bộ capex quan sát (M=738): tâm 21.556 (độ nhạy). Dừng 2042: **−1.763**; 2047: **−936** |
| K3 | **Quỹ KH&CN 1.059 tỷ** không trừ | **CĐKT HN Q3/26 mã 344 = 1.059,37 tỷ (nợ dài hạn)**, `png_r7/q326_p06.png`. Luật KH&CN 2013 Đ63 + TT 67/2022 (theo hiểu biết, chưa nhờ Wendy kiểm): quỹ trích trước thuế, phải dùng cho KH&CN trong 5 năm, không dùng thì hoàn thuế TNDN + lãi. Chi từ quỹ **không qua KQKD** ⇒ không có trong LN hồi quy | **(a) Vào base:** trừ khỏi net cash như quỹ KTPL. Áp V4b: chi tuân thủ, không tạo doanh thu = dòng tiền ra. r3 viết "chi cho chính DCM, không trừ"; câu đó **sai** vì phần chi đó không có trong dòng LN. Ghi nhận TTNC Thạnh Hoá (65,7 dở dang) có thể do quỹ tài trợ: **không kiểm chứng được** | **−2.001.** Độ nhạy: chỉ mất phần hoàn thuế ≈20% (ước lượng) +1.601; dùng tạo tài sản NPV=0: +2.001 |
| K4 | **Tệp đầu vào mất** (`bq_np_hist_out.csv`, `bq_commod_out.csv`), mô hình không tái lập được | Bị xoá ở commit `906dfecd0` (TRIM_DD 19/11). Khôi phục bằng `git archive 906dfecd0^`; **md5 khớp LOCK_r6** (1b4fb5fc…, 49afc18e…). `src/` và `txt/` cũng khôi phục | Control leg: `model_r7` với M=None, không trừ KH&CN, tái lập điểm r6 **24.818,114** (r6 báo 24.818). Chạy 2 lần, output trùng byte | — |
| K5 | Bản bị phản biện đã bị r6/ADDENDUM thay | — | rev7 thay cả r6 và báo cáo NĐT 05/11; skeptic r2 chạy trên **bản này** | — |
| K6 | Skeptic: chiều rẻ và chiều đắt đều vượt ngưỡng 5%, không nằm trong P10–P90 | — | Cả ba khoản đã vào base, nên dải P10–P90 phản ánh trục M. Còn ngoài base (chỉ độ nhạy): vòng đời, 2035+, hiệu chỉnh BQ D&A | §3, §4 |
| (giữ từ r6) | P(thuế XK 0%) 0,55; STRUCT 125 @20%; phong toả 332 | r6 C2/C4 + STANDARD_r2 điều 3 | Không vào base (giữ r6) | §4 |

## 2. Cầu nối r6 → rev7 (đ/cp; điểm tại tham số trung tâm, trước CK; `calc/model_r7_out.txt` mục 2)
| Bước | Giá trị | Δ |
|---|---|---|
| r6 điểm base (4 cửa sổ) — control | 24.818 | |
| chỉ 2 cửa sổ 2021+ (K1b) | 24.883 | +65 |
| + chế độ D&A, M = D&A 2025 KT 342 (K1) | 27.716 | +2.833 |
| M = D&A 9T/26 năm hoá 401 (K2) | 27.089 | −627 |
| − quỹ KH&CN 1.059,37 (K3) | 25.088 | −2.001 |
| lưới M 342/401/540 (TB) = **điểm base rev7** | **24.809** | −280 |
| điểm → kỳ vọng lưới 2.430 kết cục | 24.968 | +159 |
| CK thanh khoản @5 tỷ (0,585%) | **24.822** | −146 |

LNST dài hạn @ biên 179 (tỷ), TB 2 cửa sổ: r6 **1.328** → rev7 **1.557 / 1.504 / 1.380** tương ứng M 342 / 401 / 540.

## 3. Headline + biến thể song song (sau CK 0,585%; giá 30.400; `calc/compare_px_r7_out.json`)
| Biến thể | Tâm | P10 | P90 | % trọng số < giá | Nhãn |
|---|---|---|---|---|---|
| **H — headline** (2 cửa sổ × M3 × r5 × biên 138/179/220 × năm1 3 × khí A/B × I_C 3) | **24.822** | **19.763** | **29.644** | 94,0% | **TRÊN** |
| 4 cửa sổ (trục r6) | 26.787 | 21.415 | 31.768 | 82,8% | TRONG |
| chỉ M = 342 | 25.725 | 20.808 | 30.408 | 89,9% | TRONG (sát P90) |
| chỉ M = 540 | 23.641 | 18.669 | 28.262 | 98,2% | TRÊN |
| M = 738 (toàn bộ capex quan sát) | 21.556 | 16.553 | 26.107 | 99,9% | TRÊN |
| không trừ KH&CN | 26.811 | 21.752 | 31.634 | 81,7% | TRONG |
| + P(thuế XK 0%) 0,55 | 25.852 | 20.821 | 30.686 | 88,3% | TRONG (sát P90) |
| D&A BQ hiệu chỉnh theo tỷ lệ KT | 25.755 | 20.482 | 30.797 | 87,7% | TRONG (sát P90) |

**Đọc:** headline TRÊN vùng với biên mỏng: giá chỉ cao hơn P90 2,6%. Mọi biến thể đều giữ giá > tâm và **> 0,85×tâm**. Chỉ cần nhích một trục lên (4 cửa sổ, không trừ quỹ, chính sách) là đủ để nhãn thành TRONG. Kết luận chắc chắn là **"không rẻ"**. Chưa chắc chắn là **"đắt hơn P90"**.

## 4. Độ nhạy (Δ so điểm base 24.809, trước CK; `model_r7_out.txt` mục 4)
- **V1 — r gắn lãi huy động:**
  - r = 13,5% tại neo 03/11 (lãi huy động 12T hiệu dụng 7,40%). Nguồn: `deposit_rate_vn.effective_deposit_rate()` đọc 23/11, cctg_12m 2026-11-02, big4 6,80%, cập nhật 16/11 ⇒ Δ = 0, r giữ 13,5%.
  - β=1: ±50bp **−492 / +532**; ±100bp **−947 / +1.109** (−3,8% / +4,5%).
  - β=0,5: ±100bp **−492 / +532**.
  - **Hai đầu dải Ke 12,3–13,4% (D4):** **+1.354 / +103** (báo kèm, tâm dùng 13,5%).
- **Phía tăng:**
  - Thuế XK 0%: P=0,55 +1.033; chắc chắn +1.879.
  - Quỹ KH&CN chỉ mất phần hoàn thuế: +1.601.
  - 4 cửa sổ: +1.977.
  - D&A hiệu chỉnh BQ: +934.
  - Nam Du 30% + V1: tới +4,0k (r6, không đổi).
- **Phía giảm (không vào base):**
  - **2035+** khí 10,39 phẳng **−7.606**; leo thang **−11.364**.
  - STRUCT 125 vĩnh viễn (100%) **−4.924**.
  - Vòng đời dừng 2042 **−1.763**.
  - Thuế lịch sử 5% (ước lượng) **−1.103**.
  - Phong toả 332 **−627**.
  - Nam Du 60,5% + V2 −3,5k (r6).
  - Capex duy trì: **−1.056 cho mỗi 100 tỷ/năm**.

## 5. Thanh khoản (V3; DNSE OHLC 1D 2025-11-19..2026-11-20, `calc/dnse_ohlc_r7.csv`)
- **Thông số:** ADV trung vị 250 phiên **89,0 tỷ**, 60 phiên **73,7 tỷ**; σ ngày 2,47%.
- **Chiết khấu (luật căn bậc hai):**
  - **5 tỷ**: 5,6% ADV, **0,585%** (ADV60: 0,643%).
  - 2 tỷ: 0,37%. 1 tỷ: 0,26%.
- Thoát lệnh 5 tỷ ở mức tham gia 15% chỉ mất 0,37 phiên.
- Nhãn như nhau ở mọi cỡ vị thế sleeve 2–4% NAV.

## 6. V6 — hai nền (CHỈ HIỂN THỊ, không đổi tâm; `model_r7_out.txt` mục 5)
| Nền | Giá trị (đ/cp) | Cơ sở |
|---|---|---|
| V_ngắn (LNST trung vị 2024 / 2025 / TTM Q3/26 = 1.959,8 tỷ; g=0) | 27.422 | r 13,5% |
| V_dài (FCFE TB 3 kỳ = CFO − capex = 156,9 tỷ) | 2.196 | CFO 2024 77,5 / 2025 −775,8 / TTM Q3/26 3.572,4; capex 791,1 / 694,6 / 917,5 |
| V theo C4 (CFO3 − min(capex, D&A)) — *chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi* | 8.687 | |

- **D = 2,53 > ln3 ⇒ "phân kỳ mạnh".** Luật 0,85×tâm không tự kích hoạt; cần Mike/user phán đoán.
- **Nguồn chênh là vốn lưu động, không phải lỗ kinh doanh.** Năm 2025, tồn kho tăng 1.903 tỷ và phải thu tăng 1.139 tỷ, làm CFO −776 (LCTT KT 2025). 9T/26 đảo chiều (+570 tồn kho).
- Capex/CFO cao do có dự án tăng trưởng (TM16). ⇒ **"FCFE thấp vì vốn lưu động + đầu tư tăng trưởng (capex)". Đừng đọc cờ này là cảnh báo đắt.**
- Hai nền không nằm trong vùng đọc tâm. Tâm theo mô hình DD (FCF = LNST tại D&A = capex duy trì).

## 7. Vị thế & lợi thế cạnh tranh (V5 — 5F)
- Tái dùng `ADDENDUM_5F.md` (07–08/11, dưới 12 tháng): **moat_tier NARROW · COST/LOCATION · không bền**, không thưởng/không trừ. Terminal RONIC = Ke, g thực = 0.
- **Kiểm nhanh 23/11:** không có dữ kiện mới đổi 5F. Đồng hồ khí 2027/2032/2035+ vẫn là rủi ro số 1.
- Phát hiện K1 làm rõ thêm một điểm: ROE/ROIC cao 2024–26 **một phần do nhà máy đã khấu hao 90%**, không phải rào cản (khớp ghi chú ADDENDUM).

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON
- **NÂNG:**
  - BCTC KT 2021–23 xác nhận D&A cao hơn số BQ: tới +0,9k.
  - Thuyết minh xác nhận quỹ KH&CN dùng cho tài sản tạo doanh thu, hoặc không bắt buộc chi: tới +2,0k.
  - Nghị định thuế XK 0%: +1,0…+1,9k.
  - SĐBS 12 bản ký theo kịch bản rẻ / Nam Du ≤ 30%: tới +4,0k.
  - Lãi huy động 12T giảm 100bp: +1,1k.
- **HẠ:**
  - Capex duy trì thực tế > 540/năm (ví dụ thuyết minh FY2026 tách được): −1,06k mỗi 100 tỷ/năm.
  - Kế hoạch dừng/đại tu lớn nhà máy: −0,9…−1,8k.
  - Không có khí ≤ giá PM3 sau 2032: −7,6…−11,4k.
  - Nam Du ≥ 60,5% + V2: −3,5k.
  - Thuế lịch sử 2021–24 ≈ 5%: −1,1k.
- **HARD ABANDON:**
  - Không mở vị thế khi giá > P90 sau CK (**29.644**).
  - Làm lại định giá nếu: dừng máy/hụt khí công bố > 60 ngày; PVN thoái vốn kèm đổi HĐ khí; bản ký SĐBS 12 khác dự thảo về giá Nam Du.
- **Hết hạn DD:** BCTC Q4/2026 (dự kiến cuối 01/2027) hoặc dd_date + 120 ngày.

## 9. Pháp lý / quản trị — WARNING, không vào base
- Giữ nguyên toàn bộ r6 §7:
  - HĐ khí là giao dịch bên liên quan khép kín PVN → PV GAS → DCM; ĐHĐCĐ uỷ quyền HĐQT sửa nội dung cơ bản.
  - SĐBS 12 mới là dự thảo.
  - 332 tỷ tiền gửi bị hạn chế tại MBV.
  - Thù lao ×3,25.
  - Phải thu PVN tăng.
  - Sau 24/4/2032 không còn khối lượng cam kết.
  - Nhân sự.
- **rev7 không tra lại tin pháp lý** (lần tra cuối 04–05/11).
- **Mới ghi nhận:** quỹ KH&CN 1.059 tỷ tăng từ 857,2 (01/01/26) lên 1.059,4 (30/9/26). Tốc độ trích nhanh hơn tốc độ chi ⇒ theo dõi hạn 5 năm.

## 10. Giả định khoá + sản phẩm
- `assumptions_r7.json` (schema dd_assumptions_v1, `bin/dd_assumptions_lint.py` **0 vi phạm**), md5 **62febba3482d0109275e22208dc563a1**.
- `calc/LOCK_r7_md5.txt` (06:53:17 ICT, trước pha giá) khoá các file sau:
  - mô hình: model_r7 / r6 / r5 / r2 / model, wpct;
  - dữ liệu: 2 CSV khôi phục, bq_da_r7;
  - output và 2 PDF BCTC.
- `model_r7.py` chạy 2 lần, output trùng byte; threads=1.
- **Pha sau khoá:** `calc/compare_px_r7.py` → `compare_px_r7_out.json` (md5 02885f14…), `dnse_ohlc_r7.csv` (md5 a69b87bc…).
- **Trang BCTC đã đọc** (ảnh trong `png_r7/`):
  - KT 2025: p10 CĐKT, p13 LCTT.
  - Q3/26: p05–p06 CĐKT, p08 KQKD, p09 LCTT, p29 TM16.
- **Còn thiếu:**
  - BCTC KT 2021–23 (D&A gốc): không kiểm chứng được trong phiên.
  - Thuyết minh TSCĐ (thời gian khấu hao còn lại, TSCĐ đã khấu hao hết còn dùng) chưa đọc.
  - Ước tính ảnh hưởng nếu số gốc khác BQ: −0…+0,9k.
