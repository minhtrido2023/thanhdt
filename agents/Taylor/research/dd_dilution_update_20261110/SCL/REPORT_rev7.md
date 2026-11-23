# SCL — DD rev7 (23/11/2026, job `Taylor_20261123_120301`) · cơ sở SAU QUYỀN · thay `REPORT_rev6.md` (sổ rev6)

Rev7 sửa đúng các khoản skeptic r3 (REFUTED, medium) nêu trên rev6. Lõi kinh doanh r3 (doanh thu, biên chuẩn hoá, trọng số chế độ ngành 0,5/0,3/0,2, lưới g/ROE, thuế) và mọi tham số khác của rev6 **giữ nguyên, không re-tune**.
- **Calc:** `rev7/calc/calc_rev7.py` (md5 `25b4c14a…`) → `rev7/calc/calc_rev7_out.json` (`a479d77a…`). Chạy 2 lần trùng byte, threads=1.
- **Khoá:** `rev7/assumptions_SCL_rev7.json` (md5 **`dd499b5a84a9eeddfd2c59df26ab71ea`**). `dd_assumptions_lint` cho 0 vi phạm.
- **Thời điểm khoá:** `rev7/LOCK_rev7_md5.txt`, 19:06:57 ICT 23/11. Giá SCL chỉ được đọc sau mốc này.
- **Chân đối chứng:** tái lập headline rev6 **16.883,0**; r4 21.339,5; biến thể `par_debt` r3 khớp.
- **Nguồn:** BCTC gốc trong `rev6/src/` (md5 ở `rev6/LOCK_rev6_md5.txt`), đọc lại bằng ảnh trang `rev6/png/` (KT2025 tr.26–27, 6T/2026 tr.27, Q3 tr.2–3).

## 0. Kết luận — **TRÊN vùng**; tâm **16.237** (−3,8% so với rev6)

Bảng dưới tính trên cơ sở sau quyền, **45.516.815 cp**.

| Cỡ CK | Tâm | P10 | P50 | P90 | Giá ref | Giá / P90 | Giá / tâm | Nhãn |
|---|---|---|---|---|---|---|---|---|
| **CK 5 tỷ (cỡ ghi sổ, 4,454%)** | **16.237** | **13.251** | 15.898 | **19.507** | **24.500** (đóng cửa 23/11, DNSE ohlc) | **+25,6%** | +50,9% | **TRÊN vùng (>P90)** |
| Sleeve 40 tr (0,843%) | 16.851 | 13.752 | 16.498 | 20.244 | 24.500 | +21,0% | +45,4% | TRÊN |

- **Trước chiết khấu thanh khoản:** tâm 16.994.
- **Kết cục cao nhất** của lưới 108 điểm là 21.295 (5 tỷ), vẫn dưới giá ⇒ **100% trọng số nằm dưới giá**.
- **Biến thể:** mọi biến thể ở §3 cho nhãn TRÊN, **trừ cận trên khung nợ** (P/E có đòn bẩy): P90 24.835 > giá ⇒ TRONG. Nhãn không bền ở khung đó (như rev6).
- **Luật 0,85×tâm:** 13.802. Không đạt.
- **Hành động:** không mua. V8 (2–4% NAV/mã) không áp dụng khi giá còn TRÊN vùng.
- **Tham chiếu cơ sở cum (trước quyền, 38,84 tr cp):** tâm 17.185 (5 tỷ) / 17.834 (40 tr).
- **Đổi nhãn?** Không. Rev6 là TRÊN, rev7 vẫn TRÊN.

## 1. Đính chính so với rev trước (rev6) — từng hạng mục skeptic r3

| # | Hạng mục skeptic r3 | Xử lý rev7 | Loại | Ảnh hưởng tâm (5 tỷ) |
|---|---|---|---|---|
| 1 | **Chiều đắt:** k = 10% bỏ qua ESOP từ LNST 6,8 tỷ. Tổng phần chia cho NLĐ 17–21% ⇒ tâm −9 đến −11% | **Sửa base.** Mới đọc thêm một dòng trong BCTC soát xét 6T/2026 tr.27 V.19.1: **"Chuyển quỹ thưởng ban điều hành về LNSTCPP (3.600.000.000)"**. Số này khớp tổng thưởng BĐH đã trích năm 2024 (3,072) + 2025 (0,531) = 3,603 (KT2025 tr.27). Nghĩa là thưởng BĐH chưa từng chi ra. Gán số hoàn về đúng năm gốc ⇒ tổng phần chia cho NLĐ (KTPL + BĐH + ESOP từ LNST theo mệnh giá): 2024 **14,54%**, 2025 **15,00%**, 2026 **20,57%** (gồm ESOP 6,8 tỷ). **k = TB 3 năm = 16,70%**, áp cho cả trích hằng năm lẫn phần trích tạm trên LNST 9T. **Không đếm hai lần:** 680k cp ESOP-2 nằm trong mẫu số là khoản chia **của năm 2026** (từ LN 2025). k áp cho LN từ 2026 trở đi | (a) | **−1.274** |
| 1b | Cách tính k khác (độ nhạy) | Trừ khoản hoàn vào năm 2026 (cách skeptic) ⇒ k 17,77% ⇒ 16.036. Gộp thô, không trừ hoàn ⇒ k 19,63% ⇒ 15.681. Rev6 10% ⇒ 17.511. **ESOP tính theo mệnh giá là cận thấp** của chi phí thật (cp phát hành miễn phí có giá trị bằng giá trị nội tại, không phải mệnh giá). Nếu định ESOP ở giá trị nội tại thì k 2026 cao hơn, nhưng làm vậy thì vòng lặp tâm↔k phải giải; chỉ nêu chiều (xuống) | (b) | −201 / −556 / +1.274 |
| 2 | **Chiều rẻ:** khung nợ mệnh giá thiếu lá chắn thuế, +4 đến +10% | **Sửa base (APV).** Cộng PV lá chắn = D·i·t / Ke = 416,46 × 4,963% × 20,04% / 13,5% = 4,142 tỷ/năm / 13,5%. Lãi vay đúng là được khấu trừ thuế: thuế 9T 23,662 / LNTT 118,031 = 20,05% (Q3 tr.3). **Giữ nợ ở mức 30/9, không tăng theo g**, vì công ty phát hành cổ phần để **trả** nợ: năm 2025 8 tr cp @10.000 "thanh toán các khoản nợ vay Ngân hàng" (KT2025 tr.26); năm 2026 75 tỷ trả BIDV (NQ 1191). Nên chọn quy ước thấp nhất trong ba quy ước skeptic nêu | (a) | **+644** |
| 2b | Quy ước lá chắn (độ nhạy) | Không lá chắn (rev6) 15.593 · nợ sau khi trả 75 tỷ 16.121 · Ke, nợ tăng g 16.553 · MM t×D 17.345 | (b) | −644 … +1.108 |
| 3 | Pha loãng do huy động vốn lặp lại để trả nợ chưa lượng hoá | **Kịch bản (không vào base).** Lịch sử: 2024 không tăng vốn bằng tiền (KT2025 tr.27 16.3); 2025 quyền 8 tr @10.000 (100 tỷ); 2026 quyền 6 tr @12.500 (75 tỷ) ⇒ 2/3 năm. Lặp một đợt như 2026 (6 tr @12.500) ⇒ **15.737 (−500)**; như 2025 (8 tr @10.000) ⇒ **15.238 (−999)**. Tính cho cổ đông **không** mua thêm; người mua đủ phần quyền thì trung tính (giá trị quyền bù phần giảm). Không có kế hoạch 2027 công bố, nên không vào base. Tần suất 2/3 chỉ là tỷ lệ lịch sử, không phải xác suất đã kiểm chứng: kỳ vọng ≈ −333 (ước lượng) | (b) | 0 trong base; −500 / −999 |
| 4 | Biến thể "bỏ thu nhập khác" trừ số gộp 4,763 thay vì số ròng | **Sửa biến thể:** trừ số ròng **1,515 tỷ** (Q3 mã 40 = 4,763 − 3,248) ⇒ **16.069**. Base không đổi (như rev6) | (b) | −168 (biến thể) |
| 5 | Cổ tức phải trả 0,76 tỷ chưa trừ | **Sửa base:** trừ 0,764 tỷ (Q3 mã 313) | (a) | **−16** |
| 6 | HĐ nguồn tro/thạch cao Phả Lại, Vĩnh Tân (thời hạn, giá) | **KHÔNG KIỂM CHỨNG ĐƯỢC.** Không có trong BCTC Q3, 6T, KT2025. Kịch bản rev6 giữ nguyên, tính lại trên base mới: biên ròng lõi −2 / −4 điểm ⇒ **13.585 / 10.933**; stress gộp ⇒ **5.942**. Không vào base | (c) | −2.652 / −5.304 |
| 7 | Capex còn lại của dây chuyền Vĩnh Tân | **KHÔNG KIỂM CHỨNG ĐƯỢC** (không công bố). Dự án tăng trưởng ⇒ V4a NPV = 0. Phần đã chi 0,916 tỷ (V.9) quá nhỏ để đổi tâm | (c) | ≈ 0 |
| 8 | ADV120 2,35 tỷ và β = 1 tái dùng từ r3, chưa kiểm lại | CK thanh khoản tái dùng (V3 §5). Đổi ADV chỉ ảnh hưởng tâm qua CK; khoảng giữa 40 tr và 5 tỷ = 614 đ cho thấy độ nhạy. β = 1 vẫn là giả định (V1 §4) | — | 0 |
| 9 | Chi phí phát hành quyền (rev6 #9, còn mở) | **Có tiền lệ:** đợt quyền 2025 thu 100 tỷ, chi phí phát hành chỉ **20.800 đồng** (KT2025 tr.26) ⇒ chi phí không đáng kể | (a) | ≈ 0 |

Loại xử lý: (a) đưa vào base, có nguồn độc lập; (b) để ở kịch bản/độ nhạy; (c) không kiểm chứng được.

**Bridge rev6 → rev7** (cơ sở sau quyền, CK 5 tỷ; mỗi bước đổi một thứ):

| Bước | Tâm | Δ | P10 | P90 |
|---|---|---|---|---|
| C0 headline rev6 — đối chứng | 16.883 | — | 13.652 | 20.415 |
| C1 k = tổng chia NLĐ TB 3 năm 16,70% | 15.609 | −1.274 | 12.623 | 18.879 |
| C2 lá chắn thuế D·i·t/Ke | 16.253 | +644 | 13.267 | 19.523 |
| **C3 trừ cổ tức phải trả (headline)** | **16.237** | −16 | 13.251 | 19.507 |

- **Chiều đổi tâm:** XUỐNG 646 đ (−3,8%).
  - Đắt hơn do k (−7,5%, cơ sở: BCTC phân phối LN 3 năm).
  - Rẻ hơn do lá chắn thuế (+4,1%, cơ sở: thuế 20% trên LNTT đã trừ lãi + hành vi trả nợ bằng vốn cổ phần).
- **Hai lỗi skeptic nêu nay đều đã sửa trong model**, không còn dựa vào việc chúng triệt tiêu nhau. Chênh với ước lượng của skeptic (−9 đến −11%) vì thưởng BĐH 3,6 tỷ đã hoàn và được gán về năm gốc.

## 2. Sự kiện + số cổ phiếu (không đổi so với rev6)
- **Quyền mua** (NQ 1191 + NQ 1363): 6.000.000 cp @12.500, GDKHQ 09/11, nộp tiền 17/11–08/12. Base giả định bán đủ.
  - Độ nhạy bao phủ: 50% ⇒ 16.540; 0% ⇒ 16.889.
- **Số cp:** 38.836.815 + 6.000.000 + 680.000 (ESOP-2) = **45.516.815**.

## 3. Biến thể (không vào base) — tâm / P10 / P90, CK 5 tỷ

| Biến thể | Tâm | P10 | P90 | Nhãn @24.500 |
|---|---|---|---|---|
| **Headline** | **16.237** | 13.251 | 19.507 | TRÊN |
| Khung r3 có cộng lại lãi dự án | 16.628 | 13.611 | 19.892 | TRÊN |
| Khung không cộng lại | 15.268 | 12.249 | 18.525 | TRÊN |
| Niên kim cộng lại lãi ở Ke | 16.049 | 13.031 | 19.307 | TRÊN |
| **Cận trên khung nợ (P/E có đòn bẩy)** | **21.578** | 18.559 | **24.835** | **TRONG** |
| Bội số một tầng | 17.224 | 14.063 | 20.808 | TRÊN |
| k 10% (rev6) / 0% | 17.511 / 19.410 | | 21.043 / 23.334 | TRÊN |
| k 17,77% / 19,63% | 16.036 / 15.681 | | 19.264 / 18.837 | TRÊN |
| Lá chắn: không / sau trả nợ / Ke+g / MM | 15.593 / 16.121 / 16.553 / 17.345 | | 18.863 / 19.391 / 19.827 / 20.615 | TRÊN |
| ESOP-2 đã nằm trong số cp | 16.484 | 13.452 | 19.803 | TRÊN |
| Đối xứng (+TROUGH 0,2) | 15.249 | 12.515 | 18.602 | TRÊN |
| Huy động lặp 6 tr @12.500 / 8 tr @10.000 | 15.737 / 15.238 | | 18.626 / 18.020 | TRÊN |
| Phả Lại suy giảm 50% / 100% | 14.236 / 12.234 | | 17.506 / 15.504 | TRÊN |
| Lỗ phải thu Vincons 20 / 50 / 100% | 16.009 / 15.668 / 15.098 | | 19.279 / 18.938 / 18.368 | TRÊN |
| Bỏ thu nhập khác RÒNG 1,515 tỷ | 16.069 | 13.079 | 19.338 | TRÊN |
| Tái đấu giá tro: biên −2 / −4 điểm | 13.585 / 10.933 | | 16.846 / 14.185 | TRÊN |

- **Năm khung định giá nợ:** 15.268 / 16.049 / **16.237 (headline)** / 16.628 / 21.578 (cận trên).
- Cận trên giữ lý do loại khỏi base như rev6 §3: lãi 4,96% coi là vĩnh viễn, không nâng Ke theo đòn bẩy, mà nợ được trả bằng tiền thật.
- Các khung r3, "không cộng lại" và cận trên dùng E có đòn bẩy, nên lá chắn thuế đã nằm sẵn trong E. Rev7 chỉ thêm lá chắn vào khung nợ mệnh giá (và niên kim), không cộng trùng.

## 4. V1 chi phí vốn + D4
- **r = 13,5%** = 13,5% + 1,0 × (7,40% − 7,40%).
  - Lãi huy động 12T hiệu dụng là 7,40%: `deposit_rate_vn.effective_deposit_rate('2026-11-23')` chạy lại lúc 19:0x ICT 23/11 cho cctg_12m (02/11) 7,40%, Big-4 6,80%, last_update 16/11.
  - β = 1 là giả định.
- **Độ nhạy theo lãi huy động** (tâm, 5 tỷ):

| Δ lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| β = 1 | 17.816 (+9,7%) | 16.995 (+4,7%) | 15.535 (−4,3%) | 14.883 (−8,3%) |
| β = 0,5 | 16.995 | | | 15.535 |

- **Hai đầu dải Ke nội địa (D4):** 12,3% ⇒ 18.164; 13,4% ⇒ 16.384. Cả hai đều < giá.

## 5. V3 thanh khoản · V5 · V6 · V8
- **V3 — CK thanh khoản:** tái dùng r3 (ADV120 2,35 tỷ tới 06/11).
  - 5 tỷ: 4,454% (ngoại suy). 40 tr: 0,843%.
  - Nhãn tính trên giá trị SAU CK.
  - Phiên 23/11: KL 51.500 cp (DNSE ohlc).
- **V5 — 5F:** ADDENDUM_5F (08/11, < 12 tháng) ⇒ moat **NONE**; terminal RONIC = Ke giữ nguyên. Rủi ro số 1: tái đấu giá nguồn tro.
- **V6 — hai nền (chỉ hiển thị):** FCFE 9T = −102,2 tỷ ≤ 0 ⇒ chỉ dùng **V_ngắn** (= tâm mô hình).
- **V8:** chuẩn 2–4% NAV/mã. Không đề xuất mua.

## 6. WARNING (không vào base) + mốc hai chiều
- **Pha loãng:**
  - Quyền mua 2025 và 2026, cả hai đợt để trả nợ (§1 #3).
  - Năm 2026 có hai đợt ESOP: 920k cp trả tiền + 680k cp miễn phí.
  - ESOP lặp lại sẽ đẩy k lên trên 16,7%.
- **Vay bên liên quan:** CTCP CN-DV Cao Cường, 28 tỷ @10%.
  - Lãi vay còn chịu trần khấu trừ 30% EBITDA của NĐ 132 (có giao dịch liên kết). Lãi 9T 15,55 tỷ so với LNTT + lãi 133,6 tỷ ⇒ chưa chạm trần.
- **Phải thu Vincons** 67,9 tỷ, chưa trích dự phòng.
- **CFO yếu** so với LN; nợ vay 416 tỷ.
- **Pháp lý:** chưa thấy tin xử phạt/khởi tố (WebSearch 05/11, 08/11, 23/11).

| Mốc | LÊN nếu | XUỐNG nếu |
|---|---|---|
| Quyền mua (hạn nộp 08/12) | Bán đủ; trả nợ BIDV tháng 1–2/2027 | Không bán hết |
| BCTC Q4/2026 | CFO ≥ LNST, phải thu giảm | Biên gộp TTM < 36%, FCFE âm tiếp |
| HĐ nguồn tro / Phả Lại vận hành | Công bố HĐ dài hạn + giá | Trễ, vượt 262,9 tỷ, mất nguồn tro |
| ĐHĐCĐ 2027 | Tổng chia NLĐ ≤ 15%, không ESOP, không chào bán mới | Tổng chia > 20%, ESOP mới, quyền mua mới |

- **Ngưỡng nhãn:** về TRONG vùng khi giá ≤ **19.507** (5 tỷ) hoặc ≤ 20.244 (40 tr).
- **Luật 0,85×tâm:** ≤ 13.802.
- **HARD ABANDON** giữ như rev6.
- **Kiểm toán:** FY2025 AVA chấp nhận toàn phần; soát xét 6T/2026 không ngoại trừ ⇒ `audited_fy_missing = false`.

## 7. Còn mở
- **HĐ nguồn tro/thạch cao** Phả Lại, Vĩnh Tân: không kiểm chứng được (§1 #6).
- **Capex còn lại** dây chuyền Vĩnh Tân: không công bố (§1 #7).
- **Kế hoạch huy động vốn / ESOP 2027:** chưa có. Chỉ để ở kịch bản (§1 #3).
- **Chi phí thật của ESOP** (giá trị nội tại so với mệnh giá): chỉ nêu chiều (§1 #1b).
- **Thời điểm phát hành** 680k cp ESOP-2.
- **NQ 486 bản gốc:** chưa tải; số lấy qua BCTC soát xét.

Không ghi `kb/dd_price_zones.json`, không email, không lệnh.
