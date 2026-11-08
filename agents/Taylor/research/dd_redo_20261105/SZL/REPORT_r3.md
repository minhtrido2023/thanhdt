# DD REDO VÒNG 3 — SZL (Sonadezi Long Thành, HOSE) · job `Taylor_20261108_164337` · 08/11/2026

Đầu vào: `TOP5C_CORRECTIONS_20261108.md` mục SZL (fundamental-skeptic, REFUTED hẹp), `STANDARD_r2.md`, `_shared/wpct.py`. Số trong file này lấy từ `calc_r3/model_r3_out.txt`. Script chạy 2 lần, ra trùng byte (md5 `d03a054d`). Giả định đã khoá ở `calc_r3/assumptions_r3.json` (md5 `51bd57e9`) trước khi so với giá. Danh sách md5 upstream: `calc_r3/LOCK_md5.txt`.

## 0. Kết luận

Tính ở mức kết cục, sau CK thanh khoản cỡ 5 tỷ (4,12%).

| | r2 | **r3** |
|---|---|---|
| Tâm (kỳ vọng lưới) | 32.391 | **29.257** (−9,7%) |
| P10 / P50 / P90 | 28.966 / 32.162 / 36.075 | **26.209 / 28.963 / 32.706** |
| Giá | 27.650 (04/11) | **27.700 (đóng cửa 06/11, BQ)** |
| Nhãn | DƯỚI vùng | **TRONG vùng** (giá thấp hơn tâm 5,3%; 29,3% trọng số kết cục nằm dưới giá) |
| Cỡ sleeve 40 tr (CK 0,37%) | DƯỚI | **TRONG** (tâm 30.401; P10/P90 27.234/33.984; 19,0% dưới giá) |

- Lưới có n=270 kết cục, kết cục thấp nhất 22.718.
- Nhãn đổi DƯỚI → TRONG là do **sửa lỗi KTPL**, không phải do đổi định nghĩa vùng (vẫn dùng P10–P90).
- **Nhãn mong manh ở cỡ 40 tr.** Các biến thể sau đều cho DƯỚI: KTPL ≤ 8%, chỉ nhánh vĩnh viễn, N0 = Q3×4, cộng BĐS đầu tư mới, ký quỹ theo PV, capex duy trì 0,5× khấu hao.
- Ngược lại, các biến thể sau vẫn giữ TRONG: holdco ≥ 10%, RONIC = Ke, N0 = mức 2025.

## 1. Kiểm từng đính chính (bằng calc)

| # | Đính chính | Kết luận | Bằng chứng / số |
|---|---|---|---|
| 1 | Quỹ KTPL | **ĐÚNG, có sửa số** | Đã đọc ảnh trang. TM18 tr.23: trích 15,778 tỷ. LNST 2025 (mã 420b, tr.4) là 140,687 ⇒ tỷ lệ 11,2%. Số dư quỹ (mã 323) 23,96 ⇒ **−477**. Skeptic áp 11,2% lên dòng tiền N0×(1−nc), ra −2.383. Nhưng KTPL được trích trên **LNST kế toán**, gồm cả phần phi tiền mặt, nên phải áp lên N0 ⇒ **−2.649**. Vì vậy tâm r3 là 29.257, không phải 29.510 như skeptic (chênh −253 đều do điểm này). Chưa tra được NQ ĐHĐCĐ 2026 ⇒ base giữ 11,2% (một năm quan sát), làm độ nhạy ở 5% và 8%. |
| 2 | Đồng hồ 2053 chỉ áp cho KCN Long Thành | ĐÚNG → **độ nhạy** | BCTC là bản scan, không có doanh thu theo từng KCN ⇒ không tách đồng hồ được trong base. Đổi trọng số thời hạn 1/2–1/2: tâm 29.637 (+380; skeptic +385). |
| 3 | Vùng hẹp; chiết khấu holdco | ĐÚNG → **độ nhạy** | Tra BQ 06/11: SNZ P/B 0,66, trong khi SZC 1,20, SZB 1,78, SZL 1,70. Đó là bằng chứng holdco discount có tồn tại ở SNZ, nhưng không ánh xạ được sang cổ phần 10,08%/8,4% của SZL ⇒ không đưa vào base. Holdco 25%: 27.039. KTPL 5% + holdco 25%: 28.507. Skeptic tính ≈28.052. Vùng hẹp là do cấu trúc mô hình (§2). |
| 4 | Lợi nhuận phi tiền mặt chỉ tính một chiều; FCF | ĐÚNG → **độ nhạy hai chiều** | Đo lại trên BQ 2019Q1–2026Q3: LNST 886,7, CF_OA 1.371,1, CF_Invest −1.703,9 (khớp skeptic). LCTT 9T/26: khấu hao 67,5 (≈90/năm), capex 309,4. BCTC không tách capex duy trì với capex mở rộng ⇒ [UL]: capex duy trì 0,5× khấu hao cho **37.366**, 1,5× khấu hao cho **21.148**. Đây là trục rộng nhất và nằm ngoài base. |
| 5 | Các trục chiều lên | ĐÚNG → **độ nhạy** | BĐS đầu tư, nguyên giá tăng 166,9 (mã 241: 1.011,9 → 1.178,8; skeptic ghi 166,2): 32.577. N0 = Q3×4 = 138,5: 30.310. Ký quỹ dài hạn tính theo PV đến 2053: 32.084 (+2.827). |
| 6 | N0 131,1 | ĐỒNG Ý | Nằm giữa 115,3 (2025 năm hoá) và 138,5 (Q3×4). |
| 7 | Giá, sleeve, cổ phiếu quỹ | ĐÚNG | Giá 27.700 khớp BQ. Ở cỡ 40 tr: P10 27.234, TRONG. Cộng thêm điểm 2: P10 27.279, vẫn TRONG; skeptic ra 27.745, DƯỚI — khác biệt là do cách áp KTPL ở điểm 1. Số cổ phiếu: vốn góp 291,1 tỷ + vốn khác 198,5 tỷ (cổ tức cổ phiếu 70%) = 48,961 tr cổ phiếu phát hành; trừ 0,7625 tr cổ phiếu quỹ còn **48,199 tr**, đúng bằng SH trong mô hình. |

## 2. Cầu nối r2 → r3

Tâm sau CK 5 ty, tính từng bước.

| Bước | Tâm | Δ | Lý do |
|---|---|---|---|
| r2 (control, tái lập bằng r2lib) | 32.391 | — | Khớp từng dòng: 32.391; P10/P50/P90 28.966/32.162/36.075 |
| Giá SZC/SZB lấy đóng cửa 06/11 | 32.370 | −22 | SZC 20.550 → 20.350; SZB 45.600 → 46.500 |
| Cửa sổ thanh khoản đến 06/11 | 32.383 | +13 | CK 5 tỷ 4,16% → 4,12% |
| Trừ số dư quỹ KTPL 23,96 | 31.906 | −477 | Skeptic #1, mã 323 |
| Trích KTPL 11,2% hằng năm | **29.257** | −2.649 | Skeptic #1, TM18 |

**Vùng hẹp do cấu trúc mô hình.** Độ rộng P10–P90 khoảng 22% của tâm. Lý do là khoảng 1/3 giá trị là phần cố định, không biến động trong lưới:
- cổ phần SZC/SZB theo giá của một ngày;
- XDCB 8.445 đ/cp;
- nợ.

Lưới **không** chứa trục capex (±8.100 đ). Vì vậy không nên đọc vùng hẹp là "ít bất định".

## 3. Biến thể song song

Tâm và P10/P90 sau CK 5 tỷ; P10 ở cỡ 40 tr.

| Biến thể | Tâm | P10–P90 | Nhãn 5 tỷ / 40 tr |
|---|---|---|---|
| **HEADLINE r3** | **29.257** | 26.209–32.706 | TRONG / TRONG (P10 27.234) |
| KTPL 0% | 31.906 | 28.480–35.592 | DƯỚI / DƯỚI |
| KTPL 5% | 30.725 | 27.385–34.306 | TRONG / DƯỚI |
| KTPL 8% | 30.017 | 26.782–33.519 | TRONG / DƯỚI |
| Thời hạn 1/2–1/2 | 29.637 | 26.253–33.530 | TRONG / TRONG |
| Chỉ 27 năm | 28.878 | 25.543–32.312 | TRONG / TRONG |
| Chỉ vĩnh viễn | 30.396 | 26.706–34.684 | TRONG / DƯỚI |
| Holdco 10% | 28.370 | 25.322–31.819 | TRONG / TRONG |
| Holdco 25% | 27.039 | 23.991–30.488 | TRONG / TRONG |
| KTPL 5% + holdco 25% | 28.507 | 25.167–32.088 | TRONG / TRONG |
| Capex duy trì 0,5× KH | 37.366 | 33.472–41.353 | DƯỚI / DƯỚI |
| Capex duy trì 1,5× KH | 21.148 | 18.191–24.183 | TRÊN / TRÊN |
| **RONIC = Ke** | **25.524** | 23.296–28.070 | TRONG / TRONG |
| + BĐS đầu tư mới 166,9 theo giá vốn | 32.577 | 29.529–36.026 | DƯỚI / DƯỚI |
| N0 = Q3×4 (138,5) | 30.310 | 27.090–33.955 | TRONG / DƯỚI |
| N0 = 2025 (115,3) | 27.017 | 24.336–30.051 | TRONG / TRONG |
| Ký quỹ dài hạn theo PV | 32.084 | 29.010–35.546 | DƯỚI / DƯỚI |

**Vì sao base chưa áp RONIC.**
- Base giữ cấu trúc Gordon của r2, tức g không bị trừ tái đầu tư.
- Skeptic TOP5C không nêu RONIC cho SZL.
- Có tiền lệ: SAS r3 (moat NARROW) giữ Gordon có g.
- Mâu thuẫn còn đó: quy tắc chung ở dòng 2 của TOP5C ("NARROW ⇒ RONIC = Ke"), và SUMMARY_5F của SZL ghi moat_durable = false. Áp đúng quy tắc đó thì tâm là **25.524**, nhãn vẫn TRONG.
- **Mike/user cần chọn.** Riêng điểm này có thể làm tâm lệch tới −3.733.

## 4. Giá ngụ ý (27.700)

Để tâm (sau CK 5 tỷ) bằng giá thị trường, chỉ cần **một** trong các điều sau đúng:
- **LN lõi:** N0 = 120,1 tỷ theo base đã trừ KTPL, tức 105,1 tỷ trước KTPL. Mức 2025 năm hoá là 115,3.
- **Quỹ KTPL:** trích 17,8% LNST.
- **Holdco discount:** 17,5%.
- **Suất chiết khấu:** r = 14,60%.

## 5. Cross-check, độ nhạy r, thanh khoản

**Cross-check Gordon** (g 3%, phi tiền mặt 10%, KTPL 11,2%, vĩnh viễn):
- A — vốn hoá LNST có gồm cổ tức SZC/SZB: 27.022.
- B — vốn hoá LN lõi rồi cộng cổ phần theo thị giá: 31.511.
- ROE: 22,5% khi tính cả thu nhập tài chính; 32,0% với ROE lõi (mẫu số đã cộng quỹ KTPL).

**Độ nhạy theo lãi huy động** (β = 1, tác động lên tâm):

| Lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| Tâm | +5,7% | +2,7% | −2,5% | −4,9% |

r = 13,50%, vì lãi 12T hiệu dụng ngày 06/11 là 7,40% (CCTG 12M, 02/11). Hệ quả: r không đổi so với r2.

**Thanh khoản:**

| Cửa sổ | ADV | Sigma | Ghi chú |
|---|---|---|---|
| 250 phiên | 0,46 tỷ | 1,25% | 5 phiên có KL = 0 |
| 60 phiên | 0,61 tỷ | 1,17% | — |

| Cỡ lệnh | CK (ADV250) | CK (ADV60) | Q/ADV250 |
|---|---|---|---|
| 10 tr | 0,18% | 0,15% | 2,2% |
| 20 tr | 0,26% | 0,21% | 4,3% |
| 40 tr | 0,37% | 0,30% | 8,7% |
| 5 tỷ | 4,12% | 3,36% | 1.084% |

Cỡ 5 tỷ nằm **NGOÀI** vùng hiệu chỉnh của luật căn bậc hai.

## 6. ⚠️ WARNING pháp lý/quản trị

Giữ nguyên các cờ của r2 §6, chưa cờ nào đóng:
1. **SNZ (công ty mẹ, 52,7%):** Trưởng BKS bị khởi tố. Đây là cá nhân ở công ty mẹ, chưa chạm tới pháp nhân SZL.
2. **Luân chuyển tiền trong hệ sinh thái Sonadezi, sở hữu chéo:**
   - trả trước người bán 72,6;
   - vay bên liên quan 23,9.
3. **Đồng Nai:** sai phạm xăng dầu/đất đai. SZL chưa bị nêu tên.
4. **Tiền thuê đất:** khoản trích bổ sung 44,3 chưa quyết toán.
5. **Thanh khoản:** free float < 25%, ADV 0,46 tỷ.

**Mới ở r3:**
- **Quỹ KTPL.** Tỷ lệ trích 11,2% lấy từ một năm quan sát. Nếu ĐHĐCĐ nâng tỷ lệ thì giá trị giảm theo: ở tỷ lệ 17,8%, tâm bằng giá.
- **Pháp lý SNZ/Đồng Nai sau 05/11 CHƯA tra lại** trong vòng này.

## 7. Giả định khoá

Bản đầy đủ ở `assumptions_r3.json` và `SUMMARY.json.assumptions`.

- **Quỹ KTPL:** 11,2%, cơ sở TM18 + mã 420b. Số dư quỹ 23,96 (mã 323).
- **Trọng số thời hạn:** 3/4–1/4 [UL].
- **Lưới N0:** trọng số [UL]; tỷ lệ phi tiền mặt 0/10/20% [UL].
- **Phần cố định:**
  - XDCB tính theo giá vốn;
  - SZC/SZB theo thị giá 06/11, trừ thuế 20% trên lãi vốn;
  - không áp holdco discount;
  - RONIC theo Gordon r2 (§3).
- **Thanh khoản:** CK theo luật căn bậc hai, Y = 1.

## 8. Mốc đổi nhận định + HARD ABANDON

Giữ các mốc của r2 §8. Thêm:

| Mốc | Lên | Xuống |
|---|---|---|
| NQ ĐHĐCĐ 2027 (phân phối LN 2026) | KTPL ≤ 8% ⇒ nhãn DƯỚI ở 40 tr | KTPL ≥ 15% |
| LCTT năm 2026 + thuyết minh TSCĐ/BĐS đầu tư | Capex duy trì < khấu hao, có số | Capex duy trì > khấu hao, hoặc LN Long Phước không đủ bù |

**HARD ABANDON:** giữ nguyên r2 §8.

**Không đủ điều kiện sleeve fear-buy §2.5.**

## 9. Mở

- Chưa có NQ ĐHĐCĐ 2026 về tỷ lệ KTPL.
- Chưa tách được capex duy trì với capex mở rộng.
- Chưa tách doanh thu theo KCN (đồng hồ 2053).
- Mốc 2053 chưa đối chiếu với giấy phép thuê đất.
- Pháp lý sau 05/11 chưa tra lại.
- Chưa chọn quy ước RONIC.

Vòng này chưa chạy lại fundamental-skeptic; Mike sẽ chạy phản biện cuối. Không sửa `kb/dd_price_zones.json`.
