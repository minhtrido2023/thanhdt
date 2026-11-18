# DD — POW (Tổng công ty Điện lực Dầu khí Việt Nam – CTCP, HOSE) · 2026-11-18 · job `Taylor_20261118_041402` · **VÒNG 2 (sau fundamental-skeptic vòng 1: REFUTED mức văn bản/giả định, nhãn ĐẮT đứng — xem Phụ lục E)**

> Chỉ nghiên cứu. Không đặt lệnh, không sửa production, không gửi email. Đơn vị: tỷ đồng, trừ khi ghi khác.
> Nguồn chính **[BCTC]**: BCTC hợp nhất Q3/2026 (`src/Q3_2026_BCTC_hopnhat.pdf`, ký 27/10/2026, công bố 30/10/2026) — bảng cân đối tr.2-3,
> KQKD tr.5, LCTT tr.7, thuyết minh 6/20/21/23/24-29. **[GT-Q3]** giải trình LNST Q3 (`src/Q3_2026_giaitrinh.pdf`). **[KT25]** BCTC hợp nhất
> kiểm toán 2025 (Deloitte, ký 12/03/2026). **[CBTT]** `src/cbtt/<ngày>_<id>/`. **[BCTN]** BCTN 2025. **[BQ]** `tav2_bq.ticker_financial` / `ticker`
> (lịch sử, giá đến 17/11/2026). **[Bobby]** `kb/data_registry/market-state/sector_read_phat_dien_20261118.md` (đọc MÙ).
> Mô hình: `model/calc.py` + `model/assumptions_POW_20261118_rev2.json` (**assumptions_md5 = `721c5f28a97867749da9499ca68fa20e`**; r1 giữ nguyên để đối chiếu: `assumptions_POW_20261118.json` md5 `c1054c74…`, output r1 `model/calc_output.txt`), output r2 `model/calc_output_rev2.txt`.
> Số không đo được gắn **(ước lượng)**.

## 0. Kết luận

- **Giá trị nội tại, tâm = 9.792 đ/cp** (sau chiết khấu thanh khoản 1%; trước: 9.891). **Vùng [7.166; 12.419]** (xấu → tốt, trọng số 25/50/25).
  r = 13,5%, **g = 0** (g 2% chỉ là độ nhạy: 9.074). Ở tâm P/B = 0,70 (BVPS mẹ 14.060). (Vòng 1: 8.806, vùng [5.551; 12.060].)
- **So giá (bước cuối):** giá 13.250 đ (17/11/2026, BQ) = **1,35 × tâm**, trên cận trên vùng (12.419). Theo mô hình: **ĐẮT** (nhãn giữ nguyên sau tính lại).
  Giá hiện tại ngầm định ROE mảng di sản **12,6%/năm vĩnh viễn** (calc) — gần mức lợi nhuận *cốt lõi* 2026 trên vốn di sản (~12%, §8a). 2026 có thể là đỉnh chu kỳ
  theo cơ chế Bobby, nhưng **lịch sử POW không cho thấy El Niño ⇒ ROE cao** (ROE thấp nhất 3,1–3,2% rơi vào El Niño 2023-24; 2025 La Niña ~10% điều chỉnh vốn XDCB);
  lợi nhuận 2026 còn đến từ FMP ~1.500 vs 1.143, cú sốc năng lượng, NT3&4 vào vận hành và hồi tố — phần cấu trúc chưa tách được. Bobby: "năm El Niño 2026-27 không nên ngoại suy làm năm chuẩn".
- **9T/2026 rất đẹp nhưng ~40% LNTT là một lần:** LNST hợp nhất 9T **6.898,6** (+216%), công ty mẹ **6.434,5** (+247%).
  Khoản hồi tố/hoàn nhập ≈ **2.755 tỷ LNTT** (H1: chênh lệch tỷ giá VA1 2019-21 1.103 + quyết toán giá khí/tiền điện Cà Mau 991 + giảm trích O&M 381 —
  CBTT 03/08/2026; Q3: hoàn nhập dự phòng phải thu O&M Cà Mau ~280 (ước lượng) — GT-Q3). **LNST mẹ cốt lõi 9T ≈ 3.980–4.063** (= 6.434,5 − một lần×(1−10,9%); dải theo khoản hoàn nhập Q3 280…187,1; thuế hiệu dụng của khoản hồi tố chưa biết — ước lượng).
- **Lợi nhuận chưa thành tiền:** CFO 9T chỉ **2.739** (< 9T/25: 3.414) vì phải thu EPTC/EVN **+9.827 → 23.880 tỷ**. Hồi tố đang nằm ở phải thu.
- **Bảng cân đối ổn:** nợ ròng thật **7.368** (vay 37.525 − tiền 10.609 − tiền gửi HTM 19.548), ND/VCSH mẹ 0,17. Nhưng vay ngắn hạn tăng
  9.365 → 17.391 trong khi giữ 19.548 tiền gửi — đòn bẩy carry, không phải thiếu tiền.
- **Số cp dùng định giá: 3.067.845.688** (TM23; +281.024.592 cp chào bán 10.000 đ, thu 2.810 tỷ, kết quả 30/01/2026; trước đó cổ phiếu thưởng/cổ tức 12/2025).
- **Pháp lý/quản trị: WARNING nhẹ, không có vụ việc.** Deloitte chấp nhận toàn phần FY2025, nhấn mạnh **chưa phê duyệt quyết toán cổ phần hoá**.
  PVN 79,94%. Nhiều giao dịch bên liên quan (PVN, PV GAS, PV OIL, PVPS) — giá trị không đọc được trong lượt này.
- **Moat: NONE (kinh tế)** — rào cản cấu trúc (giấy phép, vị trí hệ thống) có thật nhưng ROE_Min5Y 3,4%, ROIC_Min5Y 2,0% [BQ] < Ke mọi năm ⇒ không chuyển thành lợi nhuận siêu ngạch (§7). Không thưởng, không trừ.
- **Điểm yếu lớn nhất của báo cáo:** (1) tâm nhạy với ROE di sản chuẩn hoá (8% trên vốn chủ mẹ, ước lượng) — ±2pp mọi kịch bản ⇒ 8.291 / 11.293; (2) vốn chủ NT3&4
  9.000 (ước lượng, 7.000–10.000 ⇒ tâm 9.529–9.924); (3) r 13,5% là Ke chung, utility β thấp hơn có thể đúng hơn (r 11% ⇒ 11.157; cận lạc quan chồng cả g 0, vốn dự án mới 5.000,
  NT3&4 10.000, r 11% ⇒ 11.443 — vẫn < giá). Upside chưa ghi nhận ngoài base: CLTG VA1 còn ~490 tỷ (≈ +142 đ/cp, §5).

## 1. Phương pháp + minh bạch đọc mù

- Đọc ngành (tầng a) do Bobby làm MÙ trước; tôi đọc sector read SAU khi Bobby ghi. **Bobby tự báo 1 vi phạm blind nhẹ**: tên thư mục dispatch chứa mã POW
  và brief của Mike nhắc cụm LNG Nhơn Trạch 3&4; kết quả tìm kiếm trả về (không mở) mẩu "Q1/2026 cụm LNG Qm thấp hơn Qc". Bobby khẳng định chỉ dùng ở mức
  cơ chế, phân loại không bị ảnh hưởng. Tôi ghi nhận và **không** dùng phân loại của Bobby làm trọng số định giá; chỉ dùng checklist §6 và nhãn chu kỳ.
- Snapshot vĩ mô (`macro_snapshot_20261118.md`): chỉ display-only, không đổi giá trị nội tại (§9).
- Định giá MÙ giá thị trường: tâm/vùng tính trước, so giá ở bước cuối.

## 2. Đối chiếu BQ với BCTC gốc

| Mục | BCTC | BQ | Lệch |
|---|---|---|---|
| LNST mẹ Q3/26 | 1.859,6 | NP_P0 1.859,6 | khớp |
| LNST mẹ Q3/25 | 809,3 | 809,3 | khớp |
| LNST mẹ 9T/26 | 6.434,5 | Q1+Q2+Q3 = 6.577,8 | **+143,3** (Q2 BQ 3.518,6; dùng BCTC ⇒ Q2 = 3.375,3) |
| CFO 9T/26 | 2.739,0 | Q1+Q2+Q3 = 8.556,7 | **cột CF_OA_P0 không tin cậy** (Q3 BQ 5.682,5 vs suy từ BCTC −135,2) |
| Số cp | 3.067,85 tr | OShares 3.067,8 | khớp |
| PE trailing | — | 5,8 | gồm hồi tố, không dùng |

## 3. Chất lượng lợi nhuận — Q3 và 9T/2026 [BCTC tr.5, TM24-29; GT-Q3]

| | Q3/26 | Q3/25 | YoY | 9T/26 | 9T/25 | YoY |
|---|---|---|---|---|---|---|
| Doanh thu thuần | 16.772,2 | 7.855,2 | +113,5% | 49.405,5 | 25.404,3 | +94,5% |
| LN gộp | 2.311,2 | 1.290,8 | +79,1% | 8.701,3 | 3.274,5 | +165,7% |
| Biên gộp | 13,8% | 16,4% | | 17,6% | 12,9% | |
| DT tài chính | 549,5 | 222,9 | | 1.200,6 | 637,3 | |
| CP tài chính (lãi vay) | 523,1 (616,1) | 295,1 (153,7) | | 1.594,2 (1.569,0) | 869,3 (411,0) | |
| CP QLDN | **−78,4** | 211,8 | hoàn nhập | 563,3 | 715,9 | |
| LNTT | 2.414,0 | 1.011,8 | +138,6% | 7.743,5 | 2.332,1 | +232% |
| LNST hợp nhất | 2.073,1 | 948,4 | +118,6% | 6.898,6 | 2.182,0 | +216% |
| LNST mẹ | 1.859,6 | 809,3 | +129,8% | 6.434,5 | 1.856,8 | +246,5% |

Tách nguồn:
- **Một lần (≈2.755 LNTT 9T):** VA1 chênh lệch tỷ giá 2019-21 **1.103**; Cà Mau quyết toán chênh lệch tiền điện/giá khí **991**; giảm trích O&M **381**
  (CBTT 03/08/2026: "hồi tố ~2.475,6 tỷ = >59% LNTT công ty mẹ H1"); Q3 hoàn nhập dự phòng phải thu O&M Cà Mau — dòng "chi phí dự phòng" 9T **−187,1** (TM28),
  QLDN Q3 âm; tôi ước **~280** (ước lượng). ⇒ **LNTT cốt lõi 9T ≈ 4.989–5.081; LNST mẹ cốt lõi ≈ 3.980 (hoàn nhập Q3 280) … 4.063 (187,1)** = LNST mẹ 6.434,5 − một lần×(1−10,9%) (ước lượng). Các khoản hồi tố nằm
  ở cấp **công ty mẹ** (CBTT 03/08: VA1, Cà Mau là chi nhánh) ⇒ 100% thuộc mẹ, **không nhân tỷ lệ mẹ 93,3%** (vòng 1 nhân ⇒ 4.145, sai chiều NCI). Thuế hiệu dụng của chính khoản hồi tố chưa biết.
  Hoàn nhập Q3: dải **187,1 (BCĐKT: dự phòng khó đòi giảm 9T) – ~280** (GT-Q3 nói QLDN giảm ~290). Q3 cốt lõi mẹ ≈ **1.58–1.67 nghìn tỷ** (1.859,6 − 187…280×0,891; ước lượng).
- **Doanh thu tài chính:** lãi tiền gửi 947,2 + PVcomBank 103,3 trên số dư tiền+HTM ~19–30 nghìn tỷ (≈5%/năm, hợp lý); cổ tức 53,4; lãi tỷ giá
  đánh giá lại **91,4** (một lần theo VND lên giá). Lỗ tỷ giá phát sinh 24,3. Liên doanh liên kết chỉ 2,6 (Sông Hồng, LNG Quảng Ninh).
- **Chi phí NT3&4 vào KQKD:** lãi vay 9T 1.536 (vs 410) và khấu hao 2.915 (vs 2.133, +782) — NT3&4 COD 21/11 & 17/12/2025 [BCTN], lãi vay hết vốn hoá.
- **Sản lượng → lợi nhuận:** 9T sản lượng 18.954 tr kWh (+41%; VA1 5.709 +20%, CM1&2 4.245, NT3&4 3.757, NT2 3.184 +48%, NT1 1.014) [CBTT 13/10];
  FMP H1 ~1.500 đ/kWh vs 1.143 cùng kỳ [CBTT 03/08]. LN gộp cốt lõi/kWh ≈ (8.701 − 2.094 hồi tố doanh thu)/18.954 ≈ **349 đ/kWh** (ước lượng — giả định
  hai khoản VA1/Cà Mau ghi qua doanh thu/giá vốn; chưa xác minh dòng hạch toán).
  ⚠️ CBTT 10/11 "14.955 tr kWh, +55,3%" là **5 nhà máy/7 tổ máy** (định nghĩa khác, không cộng được với 18.954; nhóm đã vận hành cùng kỳ +14,8%).
  Hội thảo 12/11: sản lượng thương phẩm 19.329 tr kWh (+44%). Ba con số khác định nghĩa — **chưa đối chiếu được**.
- **Không tách được LN theo nhà máy** — BCTC hợp nhất không có báo cáo bộ phận theo nhà máy; thông cáo tháng có biểu đồ doanh thu theo đơn vị
  nhưng text trích xuất lỗi (không dùng).
- **Kế hoạch 2026 điều chỉnh (NQ 90, 10/11/2026):** LNST toàn TCT **4.973**, mẹ 4.317 — **thấp hơn 9T thực hiện (6.899)**. Căn cứ tờ trình 14/8 và 14/9 ⇒
  kế hoạch lạc hậu so với thực tế, **không** đọc là dự báo Q4 lỗ. Q4 mục tiêu sản lượng ~5,7 tỷ kWh [CBTT 13/10] (Q3 ≈ 5,9 tỷ: 18.954 − 13.034 H1).
- 2027 kế hoạch sản lượng thương mại 25.024 tr kWh (+37,3% vs KH 2026) [CBTT 10/11] — mục tiêu, không phải hợp đồng.

## 4. LNG Nhơn Trạch 3&4 (mảng rủi ro cao nhất)

- 1.624 MW, TMĐT **32.487 tỷ** [BCTN]; COD 21/11/2025 (NT3), 17/12/2025 (NT4).
- **PPA:** tháng 8/2026 ký **sửa đổi bổ sung số 02** với EVN/EPTC, Qc tối thiểu dài hạn **65%** (NĐ 100/2025) [CBTT 13/10]. Không công bố mẫu số 65% (của
  sản lượng thiết kế hay khả dụng), thời hạn áp dụng cụ thể, pass-through trễ bao lâu ⇒ **chưa có số**.
- **Thực phát 9T 3.757 tr kWh** ⇒ hệ số công suất ≈ 35% (ước lượng: 1.624 MW × 6.552 giờ). Bobby (cơ chế): LNG biến đổi 3.100–5.550 đ/kWh ≫ trần SMP 1.725
  ⇒ chỉ chạy nhờ Qc/ràng buộc hệ thống.
- **Nhiên liệu:** 9T nhận 8 chuyến 23,8 tr MMBtu tại Thị Vải; **hợp đồng LNG định hạn lần 1 ký 16/7/2026: 20,7 tr MMBtu/năm 2027-2031** [CBTT 13/10]
  ≈ 3,2 tỷ kWh/năm (ước lượng, suất hao 6.543 BTU/kWh) — **thấp hơn** nhịp thực phát 2026 (~5 tỷ kWh/năm) ⇒ phần còn lại vẫn mua giao ngay/tender.
  Điều khoản take-or-pay và công thức giá (JKM/Brent): **không công bố** ⇒ mismatch Qc điện ↔ ToP LNG **chưa kiểm được**. HĐ mua bán khí LNG tái hoá
  sửa đổi số 01 (NQ 13/02/2026) — nội dung chưa đọc.
- **Nợ dự án:** vay dài hạn Citibank & ING **11.261,9** + SMBC Singapore **4.035,6** (TM21) — khả năng cao là khoản vay ngoại tệ/ECA của NT3&4
  (CBTT cũ: "hợp đồng tín dụng hơn nửa tỷ USD cho NT3&4"); đồng tiền và lãi suất không có trong TM21 ⇒ **chưa có số**. Tổng vay dài hạn 20.134,7,
  đến hạn 12T 2.047,6.
- **Định giá theo luật NPV=0**: NT3&4 ghi theo sổ sách, vốn chủ **9.000 (ước lượng; dải 8.000–10.000)**. Cơ sở (thay TMĐT×30% của vòng 1): BCĐKT FY2025 TSCĐ nguyên giá 70.535 → 94.835 (+24.300), XDCB 19.759 → 909 (−18.850) ⇒ chi phí NT3&4 vốn hoá ~23–25 nghìn tỷ − nợ dự án Citi&ING+SMBC 15.298 ⇒ ~7.700–9.700. Không đủ cơ sở độc lập để lệch (Qc 65% có, nhưng ToP/giá LNG không có số).
- **Tiền chào bán 2.810 tỷ (báo cáo tiến độ 27/07/2026, số 1619/BC-ĐLDK):** đã dùng 1.730,1 (EPC NT3&4 1.729,2 + phí 0,9); **chưa dùng 1.080,1 gửi có kỳ hạn** ⇒ phần đã chi nằm trong tài sản NT3&4, phần chưa dùng nằm ở tiền — cả hai ghi theo sổ.
- **Đồng hồ rủi ro:** (i) KH vận hành 2027 giao Qc NT3&4 (Bobby F13: trước 15/01/2027); (ii) giá LNG giao ngay (JKM 27,6 USD/MMBtu 16/11, gấp ~2× hợp đồng);
  (iii) quyết toán dự án NT3&4 (đang làm) — rủi ro ghi giảm/điều chỉnh TSCĐ; (iv) Qc 75%/15 năm (dự thảo) nếu áp cho dự án đã vận hành ⇒ tích cực.

## 5. Bảng cân đối, dòng tiền, vốn [BCTC 30/9/2026]

| Mục | 30/9/26 | 1/1/26 |
|---|---|---|
| Tiền + tương đương | 10.609,4 | 6.764,6 |
| Tiền gửi HTM ngắn hạn | 19.548,3 | 12.708,4 |
| Vay ngắn hạn (gồm đến hạn) | 19.438,3 | 11.249,6 |
| Vay dài hạn | 18.087,1 | 17.637,5 |
| **Nợ ròng thật** | **7.367,7** | **9.414,1** |
| Phải thu KH ngắn hạn (EPTC/EVN) | 23.964,3 (23.879,9) | 14.197,0 (14.053,2) |
| Dự phòng phải thu khó đòi | 355,6 | 542,7 |
| XDCB dở dang | 1.659,6 | 909,2 |
| VCSH mẹ / NCI | 43.134,5 / 3.241,8 | 34.215,1 / 3.000,8 |

- **Phải thu EPTC:** tăng 9.827; DSO ≈ 149 ngày trên doanh thu TTM 58.307 (ước lượng; đầu năm ≈150 ngày trên DT 2025 34.306 [BQ]) — tỷ lệ ngày không xấu đi,
  nhưng số tuyệt đối gồm khoản hồi tố chưa thu. **Đây là điểm kiểm cốt lõi Q4/26–Q1/27.**
- Phải thu bên liên quan nhỏ: Đạm Cà Mau 58,9; PVN 1,1 (TM6). Phải trả PVN 728,2 (TM16 FY2025: LNST từ chênh lệch tỷ giá VA1 2016-17, trước CPH, phải nộp PVN — **không phải cổ tức**). Phải trả ngắn hạn khác PVN 14,0 (TM19).
- **CFO 9T 2.739** (LNTT 7.744 + KH 2.915 − tăng phải thu 10.695 + tăng phải trả 4.485 − lãi trả 686 − thuế 527 …). Capex 9T 2.880.
  Gửi tiền HTM ròng −6.607 (chi 17.086, thu 10.479). Vay ròng +9.332.
- **Tài sản tiềm tàng CLTG VA1 (không nhét vào base):** BCTN FY2025 TM36 (tr.184-185): chênh lệch tỷ giá VA1 phát sinh đến 2025 **ước tính ~1.596 tỷ**, ghi nhận khi được duyệt; 2026 mới ghi **1.103** (2019-21) ⇒ còn **~490 tỷ** chưa ghi nhận (≈ 490×(1−10,9%)/3.067,85 ≈ **+142 đ/cp**, ước lượng) + cơ chế tương tự NT2/Đakđrinh + điều chỉnh giá đầu tư VA1 trong giá điện khi quyết toán TMĐT (**hai chiều**: có thể làm giảm). Upside hai chiều, ngoài tâm.
- **Capex dự án mới:** KH 2026 công ty mẹ giải ngân 6.477 (VCSH 5.049), góp vốn đơn vị thành viên 1.883 [NQ 90]. Quỳnh Lập LNG 1.500 MW (GCNĐT, khởi công hạ tầng
  18/5/2026), Vũng Áng III LNG 1.500 MW (liên danh với B.Grimm–LILAMA, MoU khí PV GAS 28/7) [CBTT 13/10]. Theo luật NPV=0: **ghi theo giá vốn (số sổ), không trừ, không cộng** — vòng 2 tách `e_new_projects_book` = XDCB 1.659,6 + tiền chào bán chưa dùng 1.080,1 = **2.740**, khỏi vốn di sản (không còn định giá ở bội số di sản 0,52×). Vốn chủ mẹ KH 2026 cho dự án (5.049, NQ 90) chưa đo được phần giải ngân ngoài XDCB ⇒ độ nhạy 5.000 (tâm 10.089).
  Vốn phát hành 2.810 tỷ: NQ 19 (12/3/2026) cho đổi mục đích phần chưa dùng (<50% số thu); đến 27/7 vẫn 1.080,1 chưa dùng (báo cáo tiến độ 27/7).
- **Tỷ giá:** vay từ ngân hàng ngoại (Citi/ING, SMBC, BOC HK 837,8, Citibank NH 1.999,1, HSBC 1.400, SCB 151,3) ≈ 19,7 nghìn tỷ — đồng tiền không ghi
  ⇒ độ nhạy ±1% USD/VND ≈ ±150–200 tỷ đánh giá lại **nếu** toàn bộ là USD (ước lượng, cận trên). Cơ chế EVN trả chênh lệch tỷ giá trễ nhiều năm (VA1 2019-21
  mới thu 2026) ⇒ dòng thu ADMIN, lumpy.
- Dự phòng phải trả (bảo trì CM1&2, NT1, VA1) 3.505,4 không đổi trong 9T.

## 6. Trả lời 13 điểm "DD cần kiểm gì" của Bobby

| # | Điểm | Trả lời bằng số | Trạng thái |
|---|---|---|---|
| 1 | Danh mục theo nhà máy | VA1 than 1.200 MW (COD 2015, TMĐT 33.651); CM1&2 khí 1.500 MW (2008); NT1 450 MW (2009); NT2 (cty con); NT3&4 LNG 1.624 MW (2025); thuỷ Hủa Na, Đakđrinh 125 MW, Nậm Nơn; NLTT nhỏ [BCTN]. Tỷ trọng LN theo nhiên liệu: **không có** | Nửa |
| 2 | Qc từng nhà máy | Không công bố Qc/Qm; chỉ sản lượng 9T (§3). FMP H1 ~1.500 | Chưa có số |
| 3 | LNG | Qc 65% (PPA SĐBS 02, T8/26); LNG định hạn 20,7 tr MMBtu/năm 27-31; ToP/công thức giá/DSCR: không công bố; nợ Citi&ING+SMBC 15.297,5 | Nửa |
| 4 | Khí nội địa | Chương trình giao khí CM1&2 2026-27 được duyệt (NQ 06/3/2026); thoả thuận khí + LNG tái hoá Tây Nam Bộ (NQ 83, 13/10). % MFO/sàn: không có | Chưa có số |
| 5 | Than & thuỷ | VA1 nhận 2,7 tr tấn than 9T (110% KH); thuỷ: không có mực nước hồ | Nửa |
| 6 | Tỷ giá | Hồi tố VA1 2019-21 1.103 (2026); vay NH ngoại ~19,7 nghìn tỷ, đồng tiền không ghi; lãi đánh giá lại 91,4 | Nửa |
| 7 | Người mua | Phải thu EPTC 23.879,9 (+9.827), DP 333,0; DSO ~149 ngày | Có |
| 8 | Giá cố định & đồng hồ PPA | CM1&2 18 năm tuổi, NT1 17 năm; năm hết khấu hao/PPA: **không có** | Chưa có số |
| 9 | Khả dụng | 6/7 tổ máy đạt/vượt định mức, 6 tổ >94% (CBTT 10/11); 2027: 8 kỳ BDSC, đại tu CM1 + thay hệ thống điều khiển | Có |
| 10 | Capex & dự án mới | KH 2026 giải ngân mẹ 6.477; Quỳnh Lập, Vũng Áng III (chưa PPA) ⇒ NPV=0 | Có |
| 11 | Carbon | Gói thầu tư vấn đáp ứng QCVN 19:2024 khí thải (nhiệt điện); hạn ngạch: không có | Chưa có số |
| 12 | Cổ đông NN | PVN 79,94% (TM23); cổ tức 2025 bằng cổ phiếu (12/2025); thoái vốn công ty con chưa đại chúng "khó khăn" [BCTN] | Có |
| 13 | Độ nhạy | ±10% Qm nhiệt ≈ ±660 tỷ LN gộp/năm (cận trên, 349 đ/kWh × ~1,9 tỷ kWh, ước lượng); EVN trễ +30 ngày ≈ 4.790 tỷ vốn lưu động ≈ 240 tỷ lãi/năm @5% (ước lượng); ±1% USD/VND ±150–200 tỷ (cận trên); FMP/Qc/giá khí: không đủ số | Nửa |

## 7. Vị thế & lợi thế cạnh tranh (5F tầng b)

Tra cứu: `data/moat_tags.csv` không có POW; `kb/projects/` chỉ nhắc POW trong `dcf-earning-power-upgrade.md` (không phải audit 5F); không có REPORT DD POW cũ ⇒
**làm đầy đủ lần đầu (asof 2026-11-18)**.

- **Loại hình:** genco đa nhiên liệu, bán cho người mua duy nhất (EVN/EPTC), đầu vào phần lớn từ tập đoàn mẹ (khí PV GAS, LNG qua PV GAS LNG) hoặc nhập (than VA1, LNG giao ngay).
- **5 lực:** (1) người mua — EVN độc quyền mua, giá trần do BCT duyệt ⇒ quyền lực người mua **rất cao**; (2) nhà cung cấp — khí/LNG từ bên liên quan, giá gắn dầu/JKM,
  pass-through một phần ⇒ **cao**; (3) thay thế — than rẻ hơn khí trong merit order, tái tạo ưu tiên ban ngày ⇒ **trung bình**; (4) gia nhập — vốn lớn, giấy phép/PDP8,
  18 dự án LNG mới chỉ 2-3 khởi công ⇒ rào cản **cao** nhưng không độc quyền; (5) cạnh tranh nội ngành — điều độ theo giá biến đổi ⇒ **trung bình**.
  **Lực thứ 6 (nhà nước):** quyết định Qc, khung giá, chênh lệch tỷ giá, giá bán lẻ (−2% từ 01/11/2026) ⇒ **chi phối**.
- **Bằng chứng định lượng:** ROE theo [BQ] LNST mẹ / (BVPS×cp = VCSH **tổng gồm NCI**): 2019 8,4% · 2020 7,1% · 2021 5,5% · 2022 5,7% · 2023 3,1% · 2024 3,2% · 2025 6,5%.
  Trên VCSH **mẹ** (skeptic tính lại; kiểm 2025 = 2.426,6/34.215,1 = 7,1%): 9,3/7,8/6,1/6,3/3,4/3,5/7,1%, TB 6,2%. **ROE_Min5Y 3,4%, ROIC_Min5Y 2,0%, ROIC5Y 5,0%** — luôn < Ke 13,5% (và < Ke 11% cho utility).
  Tự chủ nhiên liệu: **không** (mỏ khí suy giảm, LNG giao ngay). Quy mô: ~10% nhu cầu điện toàn quốc ngày 14/4/2026 (100 tr kWh/ngày) [CBTT 13/10]; vai trò nguồn biên miền Nam.
- **Kết luận: moat_tier = NONE (kinh tế); rào cản cấu trúc có thật (giấy phép dự án, vị trí hệ thống, quy mô) nhưng người mua độc quyền (EVN) + nhà nước (Qc, khung giá) chiếm thặng dư ⇒ ROIC < Ke mọi năm.**
  Tiền lệ `moat_tags.csv`: QTP NARROW dựa trên ROIC floor 12–16%; POW không có. Rủi ro số 1: **Qc/ToP LNG + giá nhiên liệu không pass-through đủ** (ADMIN). Đồng hồ: mỏ khí nội suy giảm, CM/NT1 già, PPA bước giảm giá cố định.
- **Tham số moat trong mô hình: KHÔNG** (trượt (i)). Không trừ: ROE di sản lấy từ lịch sử chính POW, không ép về ngành.
- **Độ nhạy:** các con số dưới **không phải giả định moat** mà là kịch bản ROE di sản: tốt (11,5%) ⇒ **12.419**; xấu (4,5%) ⇒ **7.166**; cơ sở (8%) ⇒ 9.792 (tâm).
- **Đề xuất dòng `moat_tags.csv`** (KHÔNG sửa file): `POW,NONE,"structural barriers (license, system position) do not convert to ROIC>Ke; EVN single buyer + state price control",2026-11-18,"ROE_Min5Y 3.4% ROIC_Min5Y 2.0% ROIC5Y 5.0% < Ke every year; fuel not self-sufficient",Taylor_20261118_043309`

## 8. Định giá — MÙ giá thị trường (giá chỉ so ở bước cuối)

### 8a. Khung
Thu nhập thặng dư trên VCSH mẹ, tách ba phần:
**Giá trị = E_di sản × ROE_di sản/r  (g = 0)  + E_NT3&4 (sổ sách) + E_dự án mới (sổ sách)**; E mẹ 43.134,5; E_NT3&4 = 9.000 (ước lượng, §4); E_dự án mới = 2.740 (§5) ⇒ **E_di sản = 31.394,5**.
- **r = 13,5%**: lãi huy động 12T hiệu dụng 7,4% (CCTG 12M 02/11, `deposit_rate_vn` ngày 03/11 và 18/11) = điểm neo ⇒ r không đổi.
- **g = 0 (base)**: ROE di sản 8% < r 13,5% ⇒ giữ lại g×E tái đầu tư vào mảng di sản **phá giá trị** (luật user 03/11: không "đầu tư mới ⇒ giảm giá trị"); đội máy già, PPA bước giảm; tăng trưởng mới đến từ dự án mới NPV=0 (ghi sổ). g 2% chỉ là độ nhạy "tái đầu tư vào di sản ở ROE di sản" (9.074; g −2% ⇒ 10.325).
- **Chuẩn hoá chu kỳ:** không dùng 2026. LNST mẹ cốt lõi 9T/26 ≈ 3.980–4.063 ⇒ năm hoá 5.307–5.417 = **ROE ~13,7–14,0% trên VCSH mẹ bình quân 9T** (38.675), ~12,3–12,6% trên VCSH mẹ cuối kỳ,
  ~12% trên vốn di sản (trừ lãi r×vốn NT3&4+dự án mới) — mẫu số ghi rõ (vòng 1 viết "12–13%" không nêu mẫu số). Đây có thể là **đỉnh chu kỳ**, nhưng lịch sử POW không cho thấy El Niño ⇒ ROE cao (xem §0); phần cấu trúc chưa tách được.
- **Cơ sở ROE di sản base 8% (ước lượng)** — phép tính trên VCSH **mẹ** (BQ chia theo VCSH tổng gồm NCI nên thấp hơn ~0,5pp): chuỗi mẹ 2019-25 9,3/7,8/6,1/6,3/3,4/3,5/7,1% ⇒ TB **6,2%** (skeptic tính lại; 2025 tự kiểm 7,1%).
  Điều chỉnh (i) bỏ vốn NT3&4 đang XDCB khỏi mẫu số các năm 2023-25 (XDCB 31/12/24 = 19.759) — nâng ROE 2023-25 lên rõ rệt; (ii) cộng lại phần hồi tố thuộc các năm trước bị dồn sang 2026 ⇒ **7–8%**; chọn 8% (cận trên dải, nghiêng lạc quan — độ nhạy −2pp ⇒ 8.291).

| Kịch bản | ROE di sản | Cơ sở | Giá trị/cp |
|---|---|---|---|
| Xấu (25%) | 4,5% | ≈ 2023–2024 (3,4–3,5% trên VCSH mẹ; ~4,5% nếu loại vốn NT3&4 đang XDCB): khí huy động thấp, NT3&4 Qm<Qc, EVN chậm trả | 7.238 |
| Cơ sở (50%) | 8,0% | TB 2019–2025 trên vốn mẹ 6,2%, điều chỉnh XDCB + hồi tố ≈ 7–8% (ước lượng) | 9.891 |
| Tốt (25%) | 11,5% | đỉnh 2019 + thiếu nguồn 2027-30 (BCT: thiếu 4.256 MW 2027), FMP cao | 12.544 |
| **Có trọng số** | | | **9.891 trước TK / 9.792 sau TK 1%** |

### 8b. Độ nhạy (calc_output_rev2.txt)
- Lãi huy động ±50bp (β=1): 10.023 / 9.578 (+2,4% / −2,2%); ±100bp: 10.272 / 9.378 (+4,9% / −4,2%); β=0,5: ±1,2% / ±2,2%.
- g −2% / 0% / 1% / 2% / 3% / 4%: 10.325 / **9.792** / 9.462 / 9.074 / 8.613 / 8.054 (g>0 = tái đầu tư vào di sản ở ROE 8% < r ⇒ giảm giá trị).
- E_NT3&4 7.000 / 8.000 / 9.000 / 10.000: 9.529 / 9.661 / **9.792** / 9.924. E_dự án mới 0 / 1.660 / 2.740 / 5.000: 9.432 / 9.650 / **9.792** / 10.089.
- r 11% / 12% (β utility thấp — chỉ độ nhạy): 11.157 / 10.543. Cận lạc quan chồng (g 0, dự án mới 5.000, NT3&4 10.000, r 11%): 11.443.
- ROE cả 3 kịch bản −2pp / +2pp: 8.291 / 11.293. Chỉ ROE cơ sở 10% (đổi nhận định LÊN, §11): 10.542.
- Thanh khoản: ADV trung vị 62 phiên **63,3 tỷ/phiên** [BQ]; vị thế ≤30 tỷ thoát ≤5 phiên ở 10% tham gia; chiết khấu 1% (ước lượng), 0–3%.
- Giá thị trường ngầm định ROE di sản **12,6%** (calc).
- **Upside ngoài base:** CLTG VA1 còn ~490 tỷ chưa ghi nhận ≈ +142 đ/cp (§5), hai chiều (điều chỉnh giá đầu tư VA1 khi quyết toán). Cộng vào tâm ⇒ ~9.934, vẫn < giá.

### 8c. Hai nền giá trị (chỉ hiển thị, không đổi tâm)
| Nền | Giá trị | Ghi chú |
|---|---|---|
| V_ngắn (LNST chuẩn hoá = trung vị TTM mẹ Q4/23–Q3/26 = 1.444; ROE 3,35%; g = 0 ⇒ không tái đầu tư, V = NP/r) | **3.487** (r1: 1.648 với g 2%) | trung vị bị neo vào giai đoạn trước NT3&4 và năm khí huy động thấp 2023-24 |
| V_dài (FCFE = CFO 3.779 − capex 7.323/năm) | **âm (−8.558)** | **FCFE ≤ 0 ⇒ chỉ V_ngắn**: capex/CFO 1,94 do xây NT3&4 (2024 capex 9.793) + phải thu EVN phình 2026 |
| V theo C4 = CFO − min(capex, KH ~2.933) | 2.042 | chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi |
| V theo D2 = CFO − 1,8% × DT 58.307 | 6.590 | chưa qua tiêu chí khoá trước (0/9 nền qua…), chỉ theo dõi; capex/DT trung vị ngành 1,8% (9 peer BQ) |

D giữa V_ngắn và D2 = 0,64 < ln3 (chỉ tham khảo vì V_dài âm). Hai nền đều **thấp hơn** tâm — không có nền nào ủng hộ giá 13.250. Dòng tiền âm là do
chu kỳ đầu tư NT3&4 và vốn lưu động (hồi tố chưa thu), **không** tự động là cảnh báo đắt; nhưng cũng chưa có bằng chứng dòng tiền ủng hộ.

### 8d. Bội số & comp (BQ `ticker` 17/11/2026, trailing — peers cũng đang trong năm đỉnh nhiệt điện)
| Mã | PE | PB | EV/EBITDA |
|---|---|---|---|
| POW | 5,8 (gồm hồi tố) | 0,88 (BQ, trên tổng VCSH) | 5,43 |
| NT2 | 4,77 | 1,29 | 5,09 |
| PGV | 4,33 | 1,30 | 3,97 |
| QTP | 3,74 | 0,77 | 2,22 |
| HND | 8,41 | 0,66 | 2,58 |
| PPC | 8,89 | 0,58 | 8,62 |
| REE | 10,98 | 1,15 | 8,31 |
| VSH | 11,34 | 1,97 | 6,85 |
| HDG | 8,50 | 0,79 | 5,68 |
| GEG | 10,44 | 0,63 | 6,50 |
| GAS (khí) | 11,46 | 2,26 | 8,00 |
| **Trung vị 10 peer** | **8,7** | **0,97** | **~6,1** |

POW tự tính: P/B mẹ 0,94 (13.250/14.060); P/E trên LNST mẹ cốt lõi năm hoá (3.980×4/3 = 5.307 ⇒ EPS 1.730) **7,7x** (đỉnh chu kỳ; 4.063 ⇒ 7,5x);
P/E trên LN chuẩn hoá cơ sở (0,08×31.394 + 13,5%×11.740 = 4.096 ⇒ EPS 1.335) **9,9x** (ước lượng);
EV ≈ 40.649 + 37.525 + 3.242 − 30.158 = 51.258; EBITDA cốt lõi 9T ≈ 9.473 ⇒ năm hoá 12.631 ⇒ **EV/EBITDA ~4,1x** (đỉnh chu kỳ, ước lượng).
Đọc: so peer, POW **không đắt** theo bội số trailing; đắt theo mô hình vì mô hình dùng ROE chuẩn hoá chu kỳ thay vì năm đỉnh. Hai cách nhìn khác nhau đúng ở giả định
"2026 có lặp lại không".

### 8e. Vùng giá (sau chiết khấu thanh khoản)
- Tâm **9.792**; vùng **[7.166; 12.419]**; mốc 0,85×tâm = **8.323**.
- Giá 13.250 = 1,35×tâm ⇒ nhãn **ĐẮT** (theo mô hình). Kể cả r 11% (11.157), ROE cơ sở 10% (10.542), hay cận lạc quan chồng (11.443) vẫn dưới giá.

## 9. Vĩ mô (display-only, từ snapshot + Bobby — không đổi giá trị nội tại)
Sản lượng điện hệ thống 10T/2026 +9,8%, T10 +14,3%; IP T10 +15,0%; CPI 5,09% (lực cản giá bán lẻ; EVN giảm 2% từ 01/11/2026); USD/VND −2,54%/12T (giảm áp lực
tỷ giá); Brent T11 96,7 (+52% YoY, qua đỉnh T10); LNG giao ngay 27,6 USD/MMBtu 16/11 (−12% một phiên). Lãi huy động hiệu dụng 7,4% đi ngang.
Bobby: genco đa nguồn 12T **ADMIN 0,45 / CYCLICAL 0,40 / STRUCTURAL 0,15**, độ tin cậy ~60/40; khối lượng nhiệt điện ở **đỉnh chu kỳ** tới mùa khô 2027.

## 10. Pháp lý / quản trị — chỉ WARNING
- ⚠️ Kiểm toán FY2025 (Deloitte): **chấp nhận toàn phần** + nhấn mạnh: chưa phê duyệt **quyết toán cổ phần hoá** (TM02). Không ngoại trừ.
- ⚠️ Lợi nhuận phụ thuộc **quyết định hành chính** (hồi tố tỷ giá/giá khí 2026 chiếm ~40% LNTT 9T) — có thể lặp lại theo chiều ngược (EVN quyết toán giảm).
- ⚠️ Giao dịch bên liên quan dày: PVN (NQ 12/01), liên danh PV OIL (NQ 06/01), PVPS — dịch vụ kỹ thuật (NQ 13/3, 09/9, 30/9), CTCP Thương mại & Dịch vụ Dầu khí
  (22/5: chỉ là dịch vụ tổ chức hội thảo kế toán), PV GAS (khí/LNG), hoàn trả NT2 chi phí khu đất 11,64 ha cho NT3&4 (NQ 11/6). Giá trị từng giao dịch: **chưa đọc**.
- ⚠️ Nhân sự: ĐHĐCĐ 20/5/2026 bầu bổ sung HĐQT (Phan Anh Minh, Đỗ Thị Minh Hồng…); bà Nguyễn Hoàng Yến nghỉ hưu (16/6). Luân chuyển SOE, không bất thường.
- ⚠️ PVN 79,94% ⇒ free float ~20% (~615 tr cp ≈ 8.150 tỷ ở giá 13.250). Room ngoại: **chưa đo**.
- Không thấy khởi tố/xử phạt trong 83 CBTT 11/2025–11/2026 (chưa tra UBCKNN trực tiếp).

## 11. Mốc khoá trước (2026-11-18) + điều kiện đổi nhận định (hai chiều)

| # | Mệnh đề | P (ước lượng) | Chấm |
|---|---|---|---|
| T1 | LNST mẹ Q4/2026 trong [900; 2.000] tỷ | 0,60 | BCTC Q4/26 (~30/01/2027) |
| T2 | Phải thu khách hàng ngắn hạn 31/12/2026 < 20.000 tỷ (thu được hồi tố) | 0,45 | BCTC Q4/26 |
| T3 | CFO cả năm 2026 ≥ 5.000 tỷ | 0,50 | BCTC kiểm toán 2026 |
| T4 | KH vận hành 2027 giao NT3&4 Qc ≥ 65% | 0,65 | QĐ BCT (Bobby F13, trước 15/01/2027) |

**Đổi nhận định LÊN (tâm tăng):** (a) 2 quý 2027 liên tiếp ROE mẹ cốt lõi năm hoá ≥ 11% **không** có hồi tố **và** CFO ≥ LNST ⇒ nâng ROE cơ sở lên 10% ⇒ tâm 10.542 (chỉ base) – 11.293 (cả 3 kịch bản +2pp);
(b) công bố ToP/giá LNG định hạn với spread dương có Qc 65% bao phủ ⇒ thoát NPV=0 cho NT3&4; (c) EVN duyệt nốt CLTG VA1 ~490 tỷ (+142 đ/cp) / quyết toán TMĐT có lợi; (d) tách được phần cấu trúc (FMP, NĐ 100 Qc, thiếu nguồn 2027-30) khỏi chu kỳ; (e) lãi huy động −100bp ⇒ +4,9%.
**Hoặc giá về ≤ 8.323** (0,85×tâm).
**Đổi XUỐNG:** phải thu EPTC không giảm/trích lập hồi tố; NT3&4 lỗ hoặc Qc 2027 < 65%; EVN chậm trả >180 ngày; quyết toán NT3&4 ghi giảm TSCĐ; lãi huy động +100bp (−4,2%); quyết toán VA1 điều chỉnh giảm giá đầu tư.

## 12. Theo dõi
BCTC Q4/2026 (phải thu, CFO, hồi tố mới?); thông cáo NĐT tháng 10–12; KH vận hành 2027; giá JKM/Brent; Luật Điện lực sửa đổi; quyết toán NT3&4;
tiến độ Quỳnh Lập/Vũng Áng III (PPA chưa có); room ngoại (chưa đo).

## Phụ lục E — Phản biện & đính chính đã áp (vòng 2)
fundamental-skeptic vòng 1 (`skeptic_r1.md`): **REFUTED mức văn bản/giả định; nhãn ĐẮT vẫn đứng**; số BCTC khớp (A). Đã áp:

| # | Đính chính | Áp ở | Ảnh hưởng |
|---|---|---|---|
| B1 | g base 2% → **0** (ROE di sản 8% < r ⇒ g>0 phá giá trị; luật 03/11); g 2% thành độ nhạy | §0, §8a/b, assumptions rev2 | 8.806 → 9.563 (skeptic) |
| B2 | Tách vốn dự án mới theo **sổ**: XDCB 1.659,6 + tiền chào bán chưa dùng **1.080,1** (báo cáo tiến độ 27/07 — đọc scan, số kiểm chứng) = 2.740 (skeptic dùng 3.000 ước lượng); vốn mẹ KH 2026 5.049 **không** gộp (chưa đo giải ngân) ⇒ độ nhạy | §4/§5/§8 | +360 đ (E_dự án mới 0 → 2.740: 9.432 → 9.792) |
| B3 | ROE di sản trên VCSH **mẹ** (BQ dùng tổng gồm NCI); trình bày phép tính, 8% là cận trên dải 7–8% | §7, §8a | không đổi 8% |
| B4 | CLTG VA1 còn ~490 tỷ (TM36 FY2025: ~1.596, đã ghi 1.103) = upside hai chiều ≈ +142 đ/cp, **ngoài base** | §0, §5, §8b, §11 | hiển thị |
| B5 | Hạ giọng "thị trường coi năm đỉnh El Niño là chuẩn": ROE thấp nhất rơi vào El Niño 2023-24; 2025 La Niña ~10% | §0, §8a | văn bản |
| B6 | Lợi nhuận cốt lõi mẹ = 6.434,5 − một lần×(1−t) (không nhân 93,3%): **3.980–4.063**; hoàn nhập Q3 dải 187,1–280; P/E cốt lõi 7,7x | §0, §3, §8d | hiển thị (4.145 → ~3.980–4.063) |
| B7 | Moat **NONE (kinh tế)**, rào cản cấu trúc ghi riêng; "độ nhạy WIDE" đổi thành kịch bản ROE tốt | §0, §7 | không đổi định giá |
| B8a | 728,2 = LNST CLTG VA1 2016-17 phải nộp PVN, không phải cổ tức | §5 | nhãn |
| B8b | Mẫu số ROE 2026 ghi rõ (bình quân 9T ~13,7–14,0%; cuối kỳ ~12,3–12,6%) | §8a | nhãn |
| B8c | E_NT3&4 10.000 → **9.000** từ TSCĐ/XDCB FY25 − nợ dự án 15.298 (dải 8.000–10.000); bỏ cơ sở TMĐT×30% | §4, §8 | −132 đ (E_NT3&4 10.000 → 9.000: 9.924 → 9.792) |
| B8d | ROE ngầm định tại giá tính lại: 12,8% → **12,6%** | §0, §8b | |

**Kết quả vòng 2:** tâm **9.792** (r1 8.806; skeptic kỳ vọng ≈9.958 với vốn dự án mới 3.000 + NT3&4 10.000 — mô hình tính lại ra 9.792 vì dùng 2.740/9.000, không ép về số đó),
vùng [7.166; 12.419], mốc 0,85×tâm 8.323, giá/tâm **1,35×** (r1 1,50×), nhãn **ĐẮT** giữ nguyên. Chưa ghi `dd_price_zones.json` (bước của Mike). Vòng 2 chưa qua skeptic lần hai.
Chưa làm: tra UBCKNN trực tiếp (đã tự khai); vốn mẹ KH 2026 đã giải ngân ngoài XDCB (cần BCTC riêng/giải ngân từng dự án).

## Nguồn
- BCTC HN Q3/2026, giải trình Q3, BCTC KT 2025: `src/` (pvpower.vn). CBTT: `src/cbtt/` — 2026-08-03_7013 (hồi tố H1), 2026-10-13_7130 (9T sản lượng, LNG, PPA SĐBS 02),
  2026-11-10_7184 (KH 2026 điều chỉnh), 2026-11-10_7187 (14.955 tr kWh), 2026-11-16_7201 (hội thảo: LNST HN 9T 6.899), 2026-01-30_6739 (kết quả chào bán).
- BCTN 2025 (`src/BCTN_2025.pdf`) tr.24-29 (TMĐT, công suất, COD).
- BQ: `ticker_financial` (POW 2018Q1–2026Q3), `ticker` (giá/ADV đến 17/11/2026; peers). `deposit_rate_vn`.
- Bobby: `kb/data_registry/market-state/sector_read_phat_dien_20261118.md`.
