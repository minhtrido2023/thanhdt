# DD — TTA rev 4 · 2026-11-23 · job `Taylor_20261122_234424` (dựng lại sau skeptic DD_GENERAL r1 = REFUTED, 22/11/2026)

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua. Không đặt lệnh, không email, **không ghi `kb/dd_price_zones.json`** (đề xuất sổ: `LEDGER_PROPOSAL_TTA.json`).
> Bản cũ giữ nguyên: REPORT.md / REPORT_r2.md / REPORT_r3.md, `model/dcf_tta_r3.py`. Mô hình rev 4: `model/dcf_tta_r4.py` → `model/out_r4.json`; mọi số dưới đây đọc từ file này trừ khi ghi nguồn PDF.
> Khoá giả định: `assumptions_TTA_r4.json` (schema `dd_assumptions_v1`, `bin/dd_assumptions_lint.py`: 1 cảnh báo L14 — ngày quan sát lãi huy động 02/11 cách 21 ngày; chuỗi kiểm lại 16/11 vẫn 7,40%, xem §6).
> Mù giá: các đính chính K1–K5 lấy từ BCTC / quyết định giá điện / tệp tỷ giá; KHÔNG truy vấn giá TTA mới trong phiên này. Giá 10.250 đ (đóng cửa 19/11/2026) đã nằm trong r3, chỉ dùng ở §7 (pha sau khoá).

## 0. Kết luận rev 4

| Mục (V1 bù trừ ngay, trọng số A/B/B′/C = 0,15/0,25/0,35/0,25 — giữ nguyên r2/r3, không re-tune) | đ/cp |
|---|---|
| A / B / B′ / C (trước TK) | 16.201 / 12.006 / 8.058 / 2.201 |
| **Tâm có trọng số TRƯỚC chiết khấu thanh khoản** | **8.802** (r3: 6.342, +38,8%) |
| Chiết khấu thanh khoản d(5 tỷ) (giữ phương pháp r3) | 2,89% (ADV 250 phiên); 3,87% (ADV 68 phiên) |
| **Tâm SAU thanh khoản (expected_weighted)** | **8.548** (ADV 68 phiên: 8.462) |
| Vùng cùng nền sau TK: dưới ≤ 0,85× · hợp lý · trên > 1,15× | **≤ 7.266 · 7.266 – 9.830 · > 9.830** |
| Giá 19/11 10.250 / tâm | **1,20× sau TK** · 1,16× trước TK ⇒ vẫn **TRÊN vùng hợp lý**, nhưng sát ngưỡng (ngưỡng trên 9.830) |

Hướng giữ (TRÊN vùng hợp lý), mức số đổi lớn: tâm sau TK 6.159 → **8.548 (+38,8%)**. Nguyên nhân chính là sửa thiên lệch QUÁ THẤP mà skeptic chỉ ra (K1–K3). Chiều ngược lại (K4–K5) làm giảm nhỏ. Kết luận **không còn bền với mọi trọng số**: lưới P(A)×P(C) sau TK có 2/30 ô vượt giá (§3).
Vì tâm dịch >5% ⇒ theo B2 phải phản biện lại đầy đủ (§10).

**Phân rã r3 → rev 4 (tâm trước TK, đ/cp; chạy thêm bằng `model/dcf_tta_r4.py`, cố định từng bước):**
| Bước | Tâm |
|---|---|
| r3 | 6.342 |
| Cấu trúc r3 + K4 (VAT + phải thu vượt đo lại) + K5 (C: BIDV 70 = 0, Phương Mai −50%) + mức tỷ giá đầu kỳ TB 2026 (26.189 thay 25.755), giữ thuỷ điện 330 phẳng, FX phẳng | 5.968 |
| + K2 nền thuỷ điện 373 (từ 330) | 7.263 |
| + K1 chỉ số hoá thuỷ điện + giá sau FIT 1%/năm | 8.200 |
| + K3 tỷ giá FIT +1,8%/năm | **8.802** |

## 1. Đính chính so với rev trước — từng hạng mục skeptic r1 (`skeptic/r1.json`, md5 báo cáo `c2d3ac79…`)

| # | Hạng mục skeptic | Bằng chứng độc lập tìm được | Xử lý | Ảnh hưởng tâm trước TK |
|---|---|---|---|---|
| 1 | DT thuỷ điện phẳng danh nghĩa 330 tới 2060, chi phí +3%/năm | Biểu giá chi phí tránh được (BGCPTĐ) miền Bắc, giá điện năng: QĐ 226/QĐ-BCT 2019 mùa khô 663–671 đ/kWh; QĐ 650/QĐ-BCT 2021 725–726 (mùa mưa 702–704); QĐ 392/QĐ-BCT 2026 702–726 (r1 §3). ⇒ 2019→2026 ≈ **+1%/năm**; 2021→2026 ≈ 0 | **(a) base**: chỉ số hoá 1%/năm (K1) cho DT thuỷ điện và giá sau FIT; độ nhạy 0/2% | +937 (K1) |
| 1b | Cơ sở thuỷ văn "năm thuận" | **Ngược chiều skeptic nêu**: KT25 tr.45 bộ phận Yên Bái 2025 = **379,06** tỷ (đo); 2021–2024 ước lượng = DT điện (BQ / KT25 tr.46) − DT mặt trời quy theo tỷ giá: 2021 353,7 · 2022 494,4 · 2023 335,5 · 2024 384,0. Trung bình cắt (bỏ 2022 cao nhất, 2023 thấp nhất) **372,3**; trung vị 379,1. Nền r3 330 thấp hơn mọi năm trừ 2023 (El Niño). 9T/2026 279,8 vs 9T/2025 262,3 (= 542,4 − 280,12) | **(a) base**: nền 373 (K2). Độ nhạy 330/350/379 | +1.295 (K2) |
| 1c | Cơ chế giá Ngòi Hút 2 (48 MW) "chưa kiểm" | Không có PPA trong BCTC/CBTT; >30 MW không thuộc BGCPTĐ | **(c) không kiểm chứng được**; áp cùng chỉ số 1% (giả định). Nếu NH2 phẳng danh nghĩa: ảnh hưởng ≈ 48/82 công suất × (8.802 − 7.865) ≈ **−550** (ước lượng tuyến tính) | — |
| 2 | FIT theo USD nhưng tỷ giá tương lai khoá 25.755 | QĐ 13/2020 Đ5: giá FIT quy đổi theo tỷ giá USD/VND. Tệp `data/macro_usdvnd.csv`: TB năm 2016 22.015 → 2025 25.987 = **CAGR 1,86%**; 2019→2025 1,92%; 2011→2025 1,75%. TB 2026 (đến 29/4) 26.189 | **(a) base**: tỷ giá = 26.189 × 1,018^(t−2026) (K3); độ nhạy 0 / 2,5% | +602 (K3) |
| 3 | Phải thu vượt 330 gồm VAT, bù trừ với hồi tố chưa VAT | Phải thu EPTC 399,63 (Q3/26 tr.18) − mức 31/12/2024 77,11 (KT25 tr.24) = **322,52 gộp VAT** | **(a) base**: phải thu vượt 322,52 (đo, thay "~330"); bù trừ theo giá trị gộp VAT = 1,08 × hồi tố (K4). Phần VAT 8% có thể được giảm thuế đầu ra khi lập hoá đơn điều chỉnh: **không kiểm chứng được**, không vào base (+0,08 × hồi tố: B +31 tỷ, B′ +54, C +84) | trong −374 (bước 1) |
| 3b | Nếu phải thu vượt không bao giờ thu được | — | **(b) độ nhạy**: phải thu vượt = 0 ⇒ tâm 6.996 (−20,5%) | — |
| 4 | Phương Mai 99,4 tỷ (≈557 đ/cp) ở giá sổ, không có BCTC | Không tìm được BCTC Phong điện Phương Mai; dự phòng tăng 1,3 tỷ trong 9T/2026 (Q3/26 tr.20) = dấu hiệu lỗ | Base A/B/B′ giữ giá sổ (kiểm toán chấp nhận toàn phần); **(b) kịch bản C −50%** (ước lượng). Độ nhạy = 0 mọi kịch bản: 8.315 (−487). **Không kiểm chứng được** giá trị thật | trong bước 1 |
| 5 | Tiền gửi BIDV 70 tỷ cầm cố cho hạn mức bảo lãnh | Q3/26 tr.18: HĐ tiền gửi BIDV là tài sản bảo đảm hạn mức bảo lãnh 70 tỷ; BCTC không nêu bảo lãnh cho ai | Tài sản vẫn thuộc công ty, nghĩa vụ là tiềm tàng ⇒ base A/B/B′ giữ; **(b) kịch bản C = 0**. Độ nhạy = 0 mọi kịch bản: 8.508 (−294) | trong bước 1 |
| 6 | Bầu Ngứ chưa có giấy phép hoạt động theo Luật Thuỷ lợi | Chỉ có nguồn báo (nongnghiepmoitruong.vn, r1); không có quyết định xử phạt/đình chỉ | **(c) không kiểm chứng được** xác suất; **(b) độ nhạy**: Bầu Ngứ dừng cả năm 2027 ⇒ 7.976 (−826). Thêm **HARD ABANDON #6** (§8) | — |
| 7 | Vốn chủ phải góp thêm cho Phước Hoà (19,9 tỷ trong 9T) | Không có chủ trương đầu tư, không công bố tổng mức/tỷ lệ góp (NQ ĐHĐCĐ 2026, NQ HĐQT 29/06/2026, BCTC Q3/26 — đã tra) | Luật V4(a): dự án tăng trưởng ⇒ base NPV = 0 tại sổ sách (90,7); khoản góp thêm sau này có giá trị tương đương ⇒ không đổi base. Rủi ro tài trợ (DSCR B′ 1,10) ⇒ **HARD ABANDON #7** (§8). Độ nhạy Phước Hoà = 0: 8.055 sau TK | 0 |
| 8 | Thời hạn HTKD; giấy phép nước/đất thuỷ điện tới 2060 | Không có trong BCTC (KT25, Q3/26); BCTN chưa có | **(c) không kiểm chứng được**. Độ nhạy: dòng tiền thuỷ điện dừng 2050 ⇒ 8.237 (−565). HTKD hết hạn sớm = chiều tăng (r1 M3: +300–500 đ, ước lượng) | — |
| 9 | Dòng tiền Q4/2026 bị bỏ | Lịch trả gốc Q4/2026 không tách được từ BCTC | **(b) độ nhạy, không vào base**: skeptic ước −113…+121 đ/cp; nhỏ (≤1,4% tâm) | — |
| 10 | Trọng số chốt = bộ thấp nhất trong 3 bộ thử (flip-flop: pass có điều kiện) | — | Giữ nguyên bộ trọng số r3 để không chỉnh theo kết quả; báo đủ đường thử + lưới (§3) | 0 |

Giả định −15% giá thuỷ điện sau 2036 (hết PPA, TT 54/2025) vẫn là **ước lượng r1**, giữ trong base; độ nhạy bỏ cắt giảm: 9.301 (+499).

## 2. Đầu vào mô hình — nguồn

| Tham số | rev 4 | r3 | Nguồn |
|---|---|---|---|
| DT thuỷ điện 2026 | 373 tỷ, +1%/năm | 330 phẳng | KT25 tr.45; BQ `ticker_financial` Revenue_P0; QĐ 226/2019, 650/2021, 392/2026 |
| Chi phí tiền thuỷ điện | 80 +3%/năm (giữ) | như nhau | KT25 tr.45: chi phí bộ phận Yên Bái 175,94 − khấu hao 91,97 = 83,97 (2025) — khớp |
| Tỷ giá FIT | 26.189 × 1,018^t (2030: 28.126; 2039: 33.024) | 25.755 phẳng | `data/macro_usdvnd.csv` |
| Giá chuyển tiếp | 1.184,90 đ/kWh phẳng (giá trần quy định bằng VND) | như nhau | r1 |
| Giá sau FIT | 1.100 đ (2026) +1%/năm | 1.100 phẳng | ước lượng r1 + chỉ số K1 |
| Phải thu EPTC vượt | 322,52 gộp VAT; bù trừ 1,08 × hồi tố | 330, bù trừ ex-VAT | Q3/26 tr.18; KT25 tr.24 |
| Hồi tố (ex-VAT) | B 384,7 · B′ 674,4 · C 1.052,7 | như nhau | tỷ giá TB năm lịch sử |
| Phần cộng | tiền 34,9 + tiền gửi 116 (C: 46) + Phương Mai 99,4 (C: 49,7) + cho vay 15 + Phước Hoà 90,7 | không có khác biệt theo kịch bản | Q3/26 tr.18–20 |
Các tham số khác (sản lượng 98/85 GWh, nợ 1.554,5, lãi 8,4%, lịch gốc, thuế, HTKD 12%, quỹ 6% + 2) giữ như r3 (`model/dcf_tta_r3.py`).

## 3. Trọng số, lưới, độ nhạy (sau TK 2,89% trừ khi ghi)

Đường thử (V1 trước TK): 0,20/0,25/0,35/0,20 → 9.502 · 0,15/0,25/0,40/0,20 → 9.095 · **chốt 0,15/0,25/0,35/0,25 → 8.802**. Biến thể bù trừ: H 8.921 / V2 9.009 trước TK.
Bộ khác (sau TK): lạc quan 0,25/0,30/0,30/0,15 **10.099** · r1-style 10.297 · A/B′/C 8.380 · đều 9.339 · bi quan 0,10/0,15/0,35/0,40 **6.916** · 0/0/0,5/0,5 4.981.
Lưới P(A) × P(C) ∈ {0,10; 0,20; 0,25; 0,30; 0,40} (B:B′ = 1:1,4): P(A)=0: 8.695…6.509 · 0,15: 9.641…7.456 · 0,25: **10.272**…8.087 · 0,35: **10.903**, 10.175…8.718. ⇒ **2/30 ô > 10.250** (P(A) ≥ 0,25 cùng P(C) = 0,10).
Nếu chỉ cân A/B (loại B′/C): mọi tổ hợp ≥ B 12.006 > 10.555 (= 10.250/0,9711) ⇒ giá dưới tâm. Kết luận "trên vùng" phụ thuộc việc B′/C (Núi Một 1 cũng bị hạ giá) có xác suất ≥ ~0,5.

Độ nhạy tâm TRƯỚC TK (một tham số mỗi lần): thuỷ điện g 0% **7.865** / 2% **9.856** · nền thuỷ điện 330 **7.434** / 350 8.070 / 379 8.995 · tỷ giá g 0% **8.200** / 2,5% 9.056 · thuỷ điện dừng 2050 8.237 · bỏ cắt −15% sau 2036 9.301 · Bầu Ngứ dừng 2027 7.976 · Phương Mai = 0 8.315 · BIDV 70 = 0 8.508 · phải thu vượt = 0 6.996.

## 4. DSCR 2027 (sau thuế + HTKD, trước hồi tố)
A **1,37** · B **1,24** · B′ **1,10** · C **0,80** (r3: 1,25/1,12/1,00/0,73). EBITDA B′ 530,3; lãi 130,6; gốc 280. Tăng do nền thuỷ điện 373.

## 5. Vị thế & lợi thế cạnh tranh (5F) — tái dùng (V5)
5F đầy đủ làm 20/11/2026 (REPORT.md §5, < 12 tháng) ⇒ tái dùng: **moat_tier NONE**, rủi ro số 1 = tính lại giá FIT hồi tố. Kiểm nhanh: không có dữ kiện mới đổi hào; phát hiện K1 (giá chi phí tránh được gần như đứng yên 2021–2026) củng cố "không có quyền định giá". Không thưởng, không trừ; dòng tiền hữu hạn ⇒ terminal không áp dụng.

## 6. Chi phí vốn (V1/V2)
r = **13,5%**; neo 03/11/2026 = lãi huy động 12T hiệu dụng 7,40%; hiện tại `deposit_rate_vn.consumer_deposit_rate_detail()` = **7,40%** (cctg_12m quan sát 02/11/2026, Big-4 6,80%, chuỗi cập nhật 16/11/2026) ⇒ Δ = 0, r giữ 13,5% (β = 1; β 0,5 cho cùng kết quả vì Δ = 0). Hai đầu dải Ke nội địa 12,3–13,4% báo kèm (D4).
Độ nhạy tâm sau TK: −100bp **9.240** (+8,1%) · −50bp 8.884 (+3,9%) · 0 **8.548** · +50bp 8.231 (−3,7%) · +100bp **7.931** (−7,2%). Dòng tiền hữu hạn tới 2060, không terminal Gordon.

## 7. Pha SAU KHOÁ — thanh khoản (V3) + so giá
Phương pháp r3 giữ nguyên (`liquidity()`): σ ngày 1,626% · ADV trung vị 2,20 tỷ (250 phiên) / 1,13 tỷ (68 phiên) · spread Corwin-Schultz 0,88% ⇒ d(5 tỷ) **2,89%** (cận dưới 3,87%); số phiên thoát @20% ADV: 11,3 / 22,2. Free float ước ~17–20% (r3 §6, ước lượng).
Giá 10.250 (19/11/2026, `model/data/px_tta.csv`) = 1,20× tâm sau TK, 1,16× trước TK ⇒ **trên vùng hợp lý** ở cả hai nền, cách ngưỡng trên 9.830 khoảng 4%.
Sizing (V8): chuẩn 2–4% NAV/mã. Giá đang trên vùng ⇒ **không đề xuất mua**; nếu về vùng hợp lý thì tối đa 2% NAV (cận dưới, vì rủi ro FIT hai chiều + thanh khoản 22 phiên thoát cho 5 tỷ ở ADV 68 phiên).

## 8. Điều kiện đổi nhận định (hai chiều) + HARD ABANDON
- Chiều tăng: FIT của Núi Một 1 được xác nhận giữ (loại nhánh B′/C) ⇒ tâm về phía A/B (≥ 11.659 sau TK) ⇒ giá dưới vùng. EPTC trả lại > 70% hoá đơn hai quý liên tiếp. PPA Ngòi Hút 2 có điều khoản chỉ số hoá giá.
- Chiều giảm: quyết định hồi tố/hạ giá cả hai nhà máy; phải thu EPTC tiếp tục tăng > 450 tỷ; BGCPTĐ 2027 giảm danh nghĩa.
- HARD ABANDON (giữ 5 điều kiện r2/r3, #3 = DSCR 2027 sau thuế + HTKD < 1,00 hoặc vi phạm covenant / giãn-hoãn nợ / tái cấp vốn), thêm:
  **#6** Có quyết định đình chỉ/thu hồi/không cấp giấy phép vận hành Bầu Ngứ theo Luật Thuỷ lợi.
  **#7** Công bố cam kết vốn chủ cho Phước Hoà > 300 tỷ (≈ 12% VCSH, ước lượng ngưỡng) trước khi vụ FIT có kết luận.

## 9. Hai nền (V6 — chỉ hiển thị)
| V_ngắn (r1: LN cổ đông chuẩn hoá 186,6 × (1 − 2%/7,4%) / (13,5% − 2%)) | V_dài (DCF tâm trước TK) | D = \|ln(V_ngắn/V_dài)\| |
|---|---|---|
| 6.632 | 8.802 | 0,283 < ln2 — không cờ |
Tâm/vùng vẫn từ mô hình DD; không trộn.

## 10. Hạng mục còn thiếu / không kiểm chứng được
Cơ chế giá + PPA Ngòi Hút 2 · BCTC Phương Mai · bên được bảo lãnh của hạn mức BIDV 70 tỷ · giấy phép Thuỷ lợi Bầu Ngứ · tổng mức/tỷ lệ góp vốn Phước Hoà · thời hạn HTKD · thời hạn giấy phép nước/đất thuỷ điện · lịch gốc Q4/2026 · khả năng thu hồi VAT trên phần hồi tố · DT thuỷ điện 2021–2024 tách theo bộ phận (đang ước lượng từ tổng trừ mặt trời quy tỷ giá).
Phản biện lại: bắt buộc (tâm dịch +38,8% > 5%) — `skeptic/r2.json`.

## Khai md5
assumptions_file = `agents/Taylor/research/dd_TTA_20261120/model/dcf_tta_r4.py` · **assumptions_md5 = `11c5bef8b136a2c73a1ac5f13a4ab326`** · output `model/out_r4.json` md5 `83c9596372c0b6917813cf32a19cf984` · khoá schema `assumptions_TTA_r4.json` md5 `6980d135ce488d7846be29abc7ed7dab` (đo `md5sum`).
Tái lập: `cd dd_TTA_20261120 && /home/trido/thanhdt/wc_venv/bin/python -I model/dcf_tta_r4.py`.

Nguồn quyết định giá điện: [QĐ 226/QĐ-BCT 2019](https://thuvienphapluat.vn/van-ban/Tai-chinh-nha-nuoc/Quyet-dinh-226-QD-BCT-2019-bieu-gia-chi-phi-tranh-duoc-407012.aspx?tab=3) · [QĐ 650/QĐ-BCT 2021](https://luatvietnam.vn/tai-chinh/quyet-dinh-650-qd-bct-bieu-gia-chi-phi-tranh-duoc-nam-2021-198589-d1.html) · [QĐ 392/QĐ-BCT 2026](https://luatvietnam.vn/dien-luc/quyet-dinh-392-qd-bct-2026-ban-hanh-bieu-gia-chi-phi-tranh-duoc-cho-nha-may-thuy-dien-nho-431541-d1.html).
