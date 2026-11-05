# DD REDO VÒNG 2 — NT2 (Điện lực Dầu khí Nhơn Trạch 2, HOSE) · job `Taylor_20261105_020021` · 05/11/2026

> Chỉ NGHIÊN CỨU, không khuyến nghị. Áp `../STANDARD_r2.md` (12 điều). Số: `calc/model_r2.py` → `calc/model_r2_out.txt/json`, `SUMMARY.json` (bản r1 lưu `SUMMARY_r1.json`), `calc/LOCK_r2_md5.txt`. Chạy 2 lần trùng byte (md5 của out.txt/out.json/SUMMARY/LOCK).
> Số BCTC giữ nguyên vòng 1 (`REPORT.md` §2–§3; BCTC riêng 30/09/2026 gốc `src/Q3_2026_hopnhat_va_giaitrinh.pdf`). Giá **22.650 đ** (đóng cửa 04/11/2026, đã trừ cổ tức 1.000 đ GDKHQ 29/10). Đơn vị tỷ đồng.

## 0. Kết luận (mức KẾT CỤC, sau chiết khấu thanh khoản 5 tỷ)

| | đ/cp |
|---|---|
| **Tâm** = kỳ vọng có trọng số của lưới (trước / sau CK) | 23.837 / **23.617** |
| **P50** kết cục (sau CK) | 23.669 |
| Giá trị tại tham số trung tâm (LNST 800, 10 năm, r 13,5%; sau CK) | 23.669 |
| **P10 / P90** kết cục (sau CK) | **18.386 / 28.278** |
| n kết cục · % trọng số dưới giá · kết cục thấp nhất | 45 · **37,5%** · 16.690 |
| Giá 22.650 so tâm | **−4,1% ⇒ TRONG vùng** (nhãn không đổi so vòng 1) |

Tâm vòng 1 22.628 ⇒ vòng 2 **+4,4%**, do (1) **cộng vốn lưu động ròng 837 thu hồi cuối thời hạn** (+820 đ/cp; vòng 1 bỏ khoản này ra khỏi giá trị mà không có cơ sở = lệch sổ sách, vi phạm điều 3) và (2) tâm = kỳ vọng của lưới (LNST TB 800) thay vì 3 kịch bản 400/800/1.150 (TB 787,5). So vùng cũ 26/10 (25.400, cum-div): −7,0%.
Ba con số (điều 4): tâm 23.617 ≈ P50 23.669 ≈ giá trị tại tham số trung tâm 23.669 — lưới gần đối xứng; không có nhánh trọng số nhỏ nào quyết định P10/P90.

## 1. Lưới (điều 1–2)
- 3 trục, mỗi ô = 1 kết cục tất định (không có kịch bản con trong ô) ⇒ phân vị tính thẳng trên 45 ô bằng `_shared/wpct.py`, trọng số = tích trọng số trục.
- **Có trong lưới (cả hai chiều)**: LNST chuẩn hoá {450; 625; 800; 975; 1.150} (0,1/0,2/0,4/0,2/0,1) [UL] — gộp Qc/thuỷ văn/FMP-giá khí; thời hạn dòng tiền {8; 10; 12} năm (1/4–1/2–1/4) [UL]; r {12,5; 13,5; 14,5}%.
- **Loại + cơ sở + bản song song**:

| Trục loại | Lý do | Bản CÓ trục (sau CK) |
|---|---|---|
| Gia hạn PPA >12 năm | 1 nguồn | thêm nhánh 15 năm (trọng số 8/10/12/15 = .2/.4/.2/.2): tâm 23.981, P10/P90 18.621/29.210 |
| NT5 dùng tiền NT2 | luật dự án mới 03/11 ⇒ NPV 0 ⇒ bản có trục = bản không trục | — |
| Rủi ro đối tác tiền gửi SHB | không có dữ liệu (chưa đọc thuyết minh tiền gửi theo NH) | không lượng hoá; WARNING |
| (đối chiếu) bỏ vốn lưu động = cách vòng 1 | — | tâm 22.791, P10/P90 17.594/27.529, % dưới giá 45,0% |

## 2. Khoản lệch sổ sách/NPV 0 trong BASE (điều 3) — tất cả
| Khoản | đ/cp | Cơ sở dữ liệu | Nguồn |
|---|---|---|---|
| Cổ tức phải trả 297,1 trừ khỏi net cash | −1.032 | BCTC mã 313; giá 04/11 đã ex-div | BCTC tr.3 + BQ Price |
| Vốn lưu động ròng 837,2 thu hồi cuối thời hạn (PV, 10 năm) — **MỚI r2** | +820 | phải thu KH 4.252,0 − phải trả NB 2.637,4 − CP phải trả 777,4 | BCTC tr.2–3 |
| Giá trị sau thời hạn PPA = 0 | (trục thời hạn) | PPA ~10/2036, **1 nguồn** [UL] | dd_NT2_20261026 §5 |
**Tham số tự đặt [UL]**: 5 mức LNST + trọng số; trọng số thời hạn; FCF vận hành = LNST vận hành (khấu hao còn ~153/năm ≈ capex duy trì — giả định); thuế 20% trên thu nhập tài chính; β=1 trong r.

## 3. Cross-check Gordon/ROE (điều 10) — g=0, VÔ HẠN (cận trên vì bỏ qua thời hạn PPA)
- Có lãi tiền gửi (800/r, không cộng tiền riêng): **20.585** · ROE 15,6% trên VCSH sau cổ tức.
- Không lãi tiền gửi ((800 − 168)/r + net cash): **27.649** · ROE vận hành (trừ tiền) 34,3%.
- Lưới (có thời hạn 8–12 năm) nằm giữa hai biến thể; biến thể A thấp vì vốn hoá lãi tiền gửi ở r 13,5% > lãi gửi ~6,5–7,4% (tiền đáng giá sổ, không phải 7%/13,5%).

## 4. Thanh khoản (điều 6)
| Cỡ | ADV 250 phiên (18,0 tỷ; σ 1,74%) | ADV 60 phiên (12,7 tỷ; σ 1,37%) |
|---|---|---|
| 10 / 20 / 40 triệu (sleeve thật) | 0,04% / 0,06% / 0,08% | 0,04% / 0,05% / 0,08% |
| 1 tỷ | 0,41% (Q/ADV 5,6%) | 0,38% (7,9%) |
| **5 tỷ (tham chiếu nhãn)** | **0,92% — Q/ADV 27,8%, NGOÀI vùng hiệu chỉnh ≤10%** | 0,86% (39,4%, ngoài) |
Nhãn theo cỡ 5 tỷ/ADV250. Ở cỡ sleeve thật (NAV SpaceX ≈ 0,94 tỷ ⇒ 10–40 tr) tâm sau CK 23.817–23.827 — nhãn không đổi. Vùng hiệu chỉnh ≤10% ADV là quy ước job này [UL].

## 5. Độ nhạy r theo lãi huy động (tâm trước CK; lưới đầy đủ)
β=1: −100bp +2,3% · −50bp +1,1% · +50bp −1,1% · +100bp −2,2%. β=0,5: ±1,1% / ±0,5–0,6%. Lãi huy động hiệu dụng 7,40% (CCTG 12M 02/11/2026) = neo ⇒ r 13,5%.

## 6. ⚠️ WARNING pháp lý/quản trị — mang đủ cờ (điều 5); không loại, không trừ base
1. **Xung đột lợi ích POW (59,4%)**: chia cổ tức hay giữ tiền cho NT5; quỹ đầu tư phát triển 791,2 (BCTC 30/09) gắn NT5 [elibook 22/10/2026]. NPV 0 ở base.
2. **Tiền gửi tập trung SHB** [Vietstock, DD 26/10] — chưa đối chiếu thuyết minh.
3. **Lịch sử số liệu**: soát xét H1/2026 giảm LNST ~94 tỷ; đính chính BCTC Q4/2022; phạt thuế 10,6 tỷ (2020); TTCP QHĐ VII (lịch sử); ĐHCĐ 28/05/2026 miễn nhiệm 1 TV BKS + bầu bổ sung TV HĐQT độc lập (lý do chưa rõ).
4. **Nghị quyết mới (dữ liệu)**: NQ HĐQT 08/07/2026 lấy ý kiến cổ đông bằng văn bản về **Phụ lục 13 hợp đồng mua bán khí với PV Gas** [24hmoney] — nội dung phụ lục (giá/thời hạn GSA?) **chưa đọc** ⇒ không đưa vào mô hình; là mốc xác minh thời hạn GSA (§8). Không thấy NQ HĐQT tháng 10–11/2026.
5. "Chưa thấy vụ việc pháp lý đang mở chạm tài sản lõi": nguồn = báo chí trong DD 26/10/2026 (vneconomy, baophapluat, thuongtruong) + web search 05/11/2026 (baophapluat, vietstock, 24hmoney) — không có kết quả khởi tố/xử phạt mới.
6. Rating 8L = 3 là kết quả cơ học `power_lens.csv` cũ (08-28), D/E gộp bỏ qua tiền gửi — không phải cờ chất lượng.

## 7. Tham số & giả định (điều 3) — xem §2; grid_desc đầy đủ trong `SUMMARY.json`.

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON (điều 8)
| Mốc | Ngày chấm | Lên | Xuống |
|---|---|---|---|
| Qc 2027 phân bổ | ~31/12/2026 | Qc ≥ 2026 ⇒ LNST ~1.000 | Qc giảm mạnh ⇒ LNST 450–625 |
| BCTC Q4/2026 | 31/01/2027 | LNST Q4 ≥150, CFO dương | lỗ Q4 + phải thu EVN > 5.000 |
| Phụ lục 13 GSA / BCTN: thời hạn PPA-GSA | khi đọc được | >2036 ⇒ nhánh 12–15 năm (tâm ~24.000) | <2036 ⇒ nhánh 8 năm |
| ĐHĐCĐ 2027 | 30/04/2027 | cổ tức tiền ≥1.500 đ | phần lớn tiền vào NT5 khi chưa có cơ chế giá LNG ⇒ kịch bản tiêu cực có xác suất |
**HARD ABANDON**: (a) quyết định chính thức chuyển tiền/cho POW hoặc bên liên quan vay không lãi/không bảo đảm; (b) kết luận thanh tra/khởi tố chạm pháp nhân NT2; (c) tiền gửi bị phong toả/không rút được. Cỡ sleeve 10–40 tr ⇒ không cần chia tranche.
**Sleeve fear-buy §2.5: KHÔNG đủ điều kiện** — không có khủng hoảng; giá ≈ tâm. Chỉ xét lại khi giá ≤ ~17.000–18.000 (gần P10) mà net cash ≥3.000 tỷ và không có quyết định rót vốn NT5.

## 9. Mở
Thời hạn PPA/GSA (1 nguồn; Phụ lục 13 chưa đọc) · công thức pass-through · Qc 2027 · thuyết minh tiền gửi theo NH, phải thu EPTC quá hạn. Chưa qua fundamental-skeptic (Mike chạy).

## Phụ lục — đổi so với vòng 1
| Mục | Vòng 1 | Vòng 2 | Lý do |
|---|---|---|---|
| Tâm | 3 kịch bản 25/50/25 (400/800/1.150) | kỳ vọng lưới | điều 4 |
| Vốn lưu động 837 | không cộng | +PV thu hồi cuối thời hạn (+820 đ) | điều 3: lệch sổ sách không cơ sở |
| Thanh khoản | ADV250, 1/5/10 tỷ | + ADV60, + sleeve 10–40 tr, cờ vùng hiệu chỉnh | điều 6 |
| Cross-check | PE ngầm định | Gordon 2 biến thể + ROE | điều 10 |
| Cờ | 3 | + NQ 08/07 Phụ lục 13 GSA, ĐHCĐ BKS/HĐQT, nguồn+ngày tra | điều 5 |
| LOCK | không | `calc/LOCK_r2_md5.txt` (9 file) | điều 9 |
