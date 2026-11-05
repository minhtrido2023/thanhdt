# DD REDO — MBB (Ngân hàng TMCP Quân đội) · mùa BCTC Q3/2026 · 05/11/2026 · job `Taylor_20261105_014125`

> NGHIÊN CỨU, trung dung. Không phải khuyến nghị, không QUALIFY/NON. Khung NGÂN HÀNG (thay net cash/GPM bằng NIM/chất lượng tài sản/vốn).
> **Nguồn:** BCTC GỐC Q3/2026 hợp nhất + riêng (đã có ở `dd_MBB_20261031/src/`, KHÔNG tải lại), sổ đọc ảnh `dd_MBB_20261031/calc/notes_read.md`,
> số lịch sử `dd_MBB_20261031/calc/mbb_calc_out.txt` (DD cũ đã qua fundamental-skeptic CONFIRMED medium, 9 đính chính áp đủ).
> Sector read Bobby (mù): `kb/data_registry/market-state/sector_read_ngan_hang_20261031.md` (ADMIN_GATED 0,45 / CYCLICAL 0,35 / STRUCTURAL 0,20).
> **Tính lại:** `$DNA_PYEXE -I calc/mbb_redo.py > calc/mbb_redo_out.txt` (tất định; chạy 2 lần md5 trùng). Mọi số mục 6–8 lấy từ `calc/mbb_redo_out.txt`/`SUMMARY.json`.
> Đơn vị tỷ đồng; giả định tương lai = **(ước lượng)**.

## 1. Kết luận (số chuẩn hoá liên mã)

| Chỉ số | Giá trị |
|---|---|
| Giá 04/11/2026 [BQ `tav2_bq.ticker`] | **19.250** (P/B 1,23x BVPS 15.594; P/E TTM 5,96x) |
| r (Ke nội địa) | **13,50%** = neo 13,5% @ 7,40% (`cctg_12m(2026-11-02)`, effective 03/11) ; 04/11 vẫn 7,40% ⇒ không đổi |
| Tâm (kỳ vọng trọng số) TRƯỚC / SAU CK thanh khoản | 23.539 / **23.494** |
| P10 / P50 / P90 SAU CK | **14.456 / 23.214 / 36.126** (trước CK: 14.484 / 23.259 / 36.196) |
| Giá vs tâm / P10 / P90 | **−18,1%** / +33,2% / −46,7% |
| **Nhãn** | **TRONG vùng** (nửa dưới; dưới tâm 18%) |

Một câu: lợi nhuận tăng thật nhờ khối lượng, NIM chưa gãy, nhưng chất lượng tài sản Q3 xấu đi nhanh. Ở r 13,5% tâm RI cao hơn giá ~18%. Phần lệch này phần lớn là **chiết khấu toàn ngành** (thị trường đang ngụ ý Ke ~15%, xem 6.4). Biến số quyết định là nhóm 2 Q4/2026.

## 2. Giả thuyết kiểm chứng (từ DD 31/10, số BCTC gốc; không đổi vì chưa có BCTC mới)

| Giả thuyết | Số | Kết quả |
|---|---|---|
| "LN Q3 tăng mạnh, bền" | LNTT Q3 10.330 (+42,5%), 9T 30.518 (+31,9%; 77% KH 39.408); phần một lần (thu nợ đã xử lý + CK) = 8,6% LNTT 9T | ĐÚNG: LN chủ yếu từ lõi |
| "NIM bị nén mạnh (chi phí lãi +115%)" | NIM tự tính bỏ TG NHNN Q3 4,12% vs Q2 4,21% (−9bp) vs Q3/25 4,08% (+4bp) | NỬA ĐÚNG: YoY chưa nén, QoQ đã quay xuống |
| "Chất lượng tài sản ổn" | Nhóm 2 HN 11.990 → **17.014 (+42% QoQ)**, mẹ +67%; NPL 1,45% → 1,67%; bao phủ 93,6% → **84,7%** | SAI: Q3 là điểm gãy |

## 3. Chất lượng lợi nhuận · bảng cân đối (khung ngân hàng)
- **Cơ cấu thu nhập 9T26:** NII 49.643 (84% TOI); DV thuần 5.192; ngoại hối thuần +467 (giao ngay +1.533, phái sinh −1.066); thu nợ đã xử lý 2.080 (−29%); OPEX +15%; CIR 26,3%. DuPont: ROA 1,89%, đòn bẩy 11,2x, **ROE 21,7%**.
- **Thay "net cash thật" bằng:** tín dụng +204.109 (+18,8% YTD) được tài trợ 56% bằng GTCG (CCTG 140.830 → 248.416; chi phí GTCG BQ 6,22%), tiền gửi KKH **giảm tuyệt đối** 339.353 → 326.389. CV KH/TG KH 129,6%. Lãi dự thu +46% (dư nợ +19%) = cờ tốc độ.
- **Dự phòng:** chi phí tín dụng 9T 1,46% < hình thành NPL mới 1,73%/năm ⇒ bao phủ rơi; giữ 93,7% cần thêm ~1.940 DP (≈19% LNTT một quý).
- **BĐS:** dư nợ KD BĐS 179.756 (+48,3% YTD, 13,95%), tăng nhanh 2,6× tăng trưởng chung = cờ.
- **Ghi nhận doanh thu:** không áp (ngân hàng). Q4 mùa vụ: Q4/25 PPOP +20% QoQ, DP chỉ 2.169 ⇒ nền Q4 thấp bất thường.
- Chi tiết + trang: `dd_MBB_20261031/REPORT.md` §3–§8.

## 4. Cổ đông · room · thanh khoản (BQ, sau khoá)
- Cổ đông (thứ cấp 2024–25, chưa cập nhật sau phát hành): Viettel ~14,7%, SCIC ~9,8%, Trực thăng ~8,4%, Tân Cảng ~7,1% ⇒ free float **~60% (ước lượng)**. Room ngoại **kín**.
- **Thanh khoản [BQ, 250 phiên tới 04/11, `calc/mbb_redo_out.txt`]:** ADV trung vị **353,7 tỷ**; σ ngày 1,62%; Amihud 2,16e−05/tỷ.
  Vị thế 5 tỷ thoát trong 0,14 phiên (tham gia 10%) / 0,07 phiên (20%). **CK thanh khoản @5 tỷ = 0,19%** (1 tỷ 0,09%; 10 tỷ 0,27%; Y=1,0). Quy mô áp dụng 5 tỷ ≈ 0,5–1% NAV của quỹ 0,5–1 nghìn tỷ.
- Phương pháp CK thanh khoản: luật căn bậc hai d = Y·σ·√(Q/ADV), Y=1,0 (độ nhạy 0,5/1,5) — **cùng định nghĩa** với mọi mã của đợt redo 05/11 (`_common_014125/common.py`, chép nguyên phương pháp NNC r6/MVC r9).

## 5. Pháp lý / quản trị — WARNING (không loại)
- Kiểm toán KPMG: 2025 chấp nhận toàn phần; soát xét 6T/2026 không ngoại trừ. Thanh tra/khởi tố 2025–26: không tìm thấy (tìm không thấy ≠ không có).
- **⚠ WARNING — MBV (OceanBank cũ):** KHÔNG hợp nhất (điểm c k.1 Đ.185 Luật TCTD 2024); tới 30/09 MB chưa góp vốn [HN-Q3 tr.2]; QĐ góp 3.500 ngày 01/10/2026 [WEB]; phải thu bán nợ từ MBV 11.248 (31/12/25) [BCTN25]; lỗ luỹ kế 15.688 (2024) [WEB].
  **Theo luật dự án/cam kết vốn mới: base = giá sổ sách (NPV 0)** — khoản góp đổi tiền thành khoản đầu tư, không trừ giá trị. Không có cơ sở độc lập cụ thể (BCTC MBV 2025–26 không có) ⇒ chỉ là độ nhạy:

| Độ nhạy MBV (không vào base) | Tâm trước CK | Δ đ/cp |
|---|---|---|
| góp 3.500 mất trắng | 23.043 | −496 |
| góp 5.000 mất trắng | 22.831 | −708 |
| phải thu bán nợ mất 30% | 23.061 | −478 |
| bù toàn bộ lỗ luỹ kế 2024 (cận trên thô) | 21.318 | −2.221 |

## 6. Định giá
### 6.1 Mô hình
RI 3 giai đoạn (2027–29 tường minh + terminal Gordon RI), BV0 = VCSH mẹ cuối 2026 theo kịch bản, trả tiền 30%, chiết khấu 57 ngày (04/11 → 31/12/2026). **r = 13,50%.** Kịch bản và giả định giữ nguyên DD 31/10 (đã qua skeptic; không có BCTC mới sau Q3) — toàn bộ **(ước lượng)**:

| | XẤU (w 0,35) | CƠ SỞ (w 0,45) | TỐT (w 0,20) |
|---|---|---|---|
| LNTT Q4/26 (PPOP/DP) | 8.500 (16.000/7.500) | 12.000 (17.500/5.500) | 14.500 (18.700/4.200) |
| LNTT 2026 | 39.018 (99% KH) | 42.518 (108%) | 45.018 (114%) |
| ROE 2027–29 → terminal / g | 13→15% → 14% / 6% | 18,5→17% → 16% / 7% | 22→20% → 18% / 8% |
| **Giá trị RI @13,5%** | **17.092** (P/B 1,10x; TV 6%) | **24.114** (1,55x; TV 25%) | **33.527** (2,15x; TV 41%) |

Kỳ vọng trọng số **23.539** trước CK ⇒ **23.494** sau CK (−0,19%).
Kịch bản ánh xạ Bobby: XẤU ≈ CYCLICAL (chi phí tín dụng 2,2% = hình thành NPL hiện tại + xây lại bao phủ, NIM −45bp); CƠ SỞ ≈ ADMIN_GATED (room + ép lãi); STRUCTURAL thể hiện qua ROE terminal thấp hơn lịch sử (Basel III/LCR).

### 6.2 Lưới P10–P90
Lưới có trọng số **n = 45** = 3 kịch bản (w 0,35/0,45/0,20) × dịch ROE 2027–29 + terminal **−3/−1,5/0/+1,5/+3 pp** × dịch g terminal **−1/0/+1 pp** (đều trong mỗi kịch bản); r cố định 13,5%. **Terminal: ô nào ROE_T < r thì RI terminal không tăng (g_RI = 0 — vốn tăng thêm NPV 0, luật 03/11; không giả định tái đầu tư phá giá trị vĩnh viễn)**; chỉ ảnh hưởng các ô dịch ROE âm (P10), không đổi tâm. File ô: `calc/grid_mbb.csv`.

| | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|
| TRƯỚC CK | 14.484 | — | 23.259 | — | 36.196 |
| SAU CK | **14.456** | 16.986 | **23.214** | 29.721 | **36.126** |

Lưới rộng vì ±3pp ROE kéo theo ±1pp g làm terminal nhạy. Biên ±3pp ≈ độ phân tán ROE5Y giữa các NH niêm yết (14,7–23,8%, BQ 30/10). Lưới đăng ký trước khi so giá, không thu hẹp sau.

### 6.3 Độ nhạy r theo lãi huy động 12T (`sens_r`)

| Δ lãi huy động | β = 0,5 | β = 1,0 |
|---|---|---|
| −100bp | r 13,00% → 25.704 (+2.165; +9,2%) | r 12,50% → **28.281 (+4.742; +20,1%)** |
| −50bp | 13,25% → 24.576 (+1.037; +4,4%) | 13,00% → 25.704 (+2.165; +9,2%) |
| +50bp | 13,75% → 22.581 (−958; −4,1%) | 14,00% → 21.694 (−1.845; −7,8%) |
| +100bp | 14,00% → 21.694 (−1.845; −7,8%) | 14,50% → **20.223 (−3.316; −14,1%)** |

(trước CK; giá trị kỳ vọng trọng số)

### 6.4 Đối chiếu (không vào tâm)
- Tâm sau CK ⇔ **P/B 1,51x** BVPS 30/09. Theo comps BQ 30/10 (DD cũ): trung vị P/B 11 NH 1,17x (≈18,3k), hồi quy P/B~ROE5Y cho MBB 1,45x (≈22,6k; R² 0,13, yếu); P/B lịch sử MBB 2023–26 1,06–1,39x.
- Ở Ke ~15% (mức thị trường đang ngụ ý cho cả ngành) RI trọng số ≈ 18,7k (DD cũ) ≈ giá. Nghĩa là nhãn "dưới tâm 18%" chủ yếu đo **khoảng cách giữa khung r nội địa 13,5% và Ke ngụ ý của thị trường** cho mọi NH VN, không phải lợi thế riêng của MBB.

## 7. Mốc khoá trước + điều kiện đổi nhận định (HAI chiều)
Giữ nguyên bộ M1–M8 của DD 31/10 (P đã khoá, chấm 15/02/2027 bằng BCTC Q4/26): M1 nhóm 2 HN 31/12 ≥ 17.014 (P 0,55); M2 NPL trong [1,5%; 2,0%] (0,70); M3 bao phủ ≥ 85% (0,45); M4 LNTT 2026 ≥ 39.408 (0,70); M5 NIM bỏ TG NHNN Q4 ≤ 4,12% (0,65); M6 TG KH ≥ +12% YTD (0,40); M7 CAR HN ≥ 10,5% (0,60, 30/04/2027); M8 phát hành 200 triệu CP riêng lẻ trước 30/06/2027 (0,50).
- **Xấu đi** (w 0,45/0,35/0,20 ⇒ tâm trước CK **22.837**): nhóm 2 HN Q4 > 20.000 hoặc nhóm 2–5 > 3,5%; bao phủ < 75%; Tier1 riêng lẻ < 8,5%; NIM Q4 bỏ TG NHNN < 3,85%; MB phải trích lập/hỗ trợ MBV > 5.000; lãi huy động 12T hiệu dụng +100bp (−3.316 đ/cp ở β 1).
- **Tốt lên** (w 0,25/0,40/0,35 ⇒ tâm trước CK **25.653**): nhóm 2 HN < 13.000 (chuyển ngược về nhóm 1) **và** bao phủ ≥ 90%; KKH tăng lại; phát hành riêng lẻ/cấp 2 ở P/B ≥ 1,3x; LNTT Q4 ≥ 14.000 với DP ≥ 5.000; lãi huy động 12T −100bp (+4.742 đ/cp ở β 1).
- Nhãn đổi sang DƯỚI vùng nếu giá < 14.456; TRÊN vùng nếu > 36.126 (các ngưỡng này dịch theo r).

## 8. Phụ lục — ĐỔI gì so với DD cũ (31/10) và vì sao

| Mục | Cũ (31/10) | Mới (05/11) | Lý do |
|---|---|---|---|
| Ke / r | dải 12,3–13,4% (khung 30/10), tâm @13,4% | **13,50%** gắn lãi huy động (luật 03/11) | luật mới |
| Tâm | **22.000** = 0,5·RI@13,4% + 0,25·hồi quy comps + 0,25·P/B lịch sử 1,25x | **23.494** = kỳ vọng RI thuần sau CK | định nghĩa tâm chuẩn hoá liên mã; comps → đối chiếu |
| Lệch tâm | | **+6,8%** (< 10%) | cầu nối: 22.000 → RI thuần @13,4% (giá 04/11, chiết khấu 57 ngày) 23.944 → @13,5% 23.539 (−405) → sau CK 23.494 (−45) |
| Vùng | 18.000–26.000 (tham chiếu tự chọn) | P10–P90 lưới n=45: 14.456–36.126 | định nghĩa lưới chuẩn hoá; rộng hơn vì có trục ROE/g |
| Nhãn | TRONG vùng, nửa dưới (giá 19.300 @30/10) | TRONG vùng (giá 19.250 @04/11), −18,1% vs tâm | |
| CK thanh khoản | ≈0, không định lượng | 0,19% @5 tỷ (luật căn bậc hai, ADV 353,7 tỷ) | luật 03/11 |
| MBV | WARNING ngoài bảng, độ nhạy BV | base = sổ sách (NPV 0), độ nhạy −496 … −2.221 đ/cp | luật dự án mới 03/11 |
| Terminal RI | g áp cả khi ROE_T < Ke | ROE_T < r ⇒ g_RI = 0 (vốn mới NPV 0) | luật 03/11; không đổi tâm MBB (mọi kịch bản ROE_T ≥ 13,5%) |
| Kịch bản / giả định | | giữ nguyên | không có BCTC/sự kiện mới; không quét tin 01–04/11 |

## 9. Lỗ hổng mở
CAR/CET1 30/09 chưa có số gốc; nhóm 2 Q3 của ngành chưa có để so; CASA chuẩn MB Q3 chưa kiểm; không quét tin mới 01–04/11/2026; free float 60% là ước lượng; BCTC MBV 2025–26 không có (độ nhạy MBV chỉ là cận thô). Chưa qua fundamental-skeptic vòng này (Mike sẽ chạy).
