# MVC — DD redo mùa BCTC Q3/2026 (05/11/2026, job Taylor_20261105_014135)

**Kết luận (số từ `calc/mvc_redo_out.txt`):** tâm (kỳ vọng trọng số 3 trạng thái biên) **15.082 đ/cp SAU chiết khấu thanh khoản** (16.482 trước; CK **8,49%** cho 5 tỷ — thanh khoản mỏng nhất trong 3 mã). Lưới chuẩn hoá 2.187 ô có trọng số: **P10 11.941 · P50 14.424 · P90 20.989** sau CK (trước: 13.049 / 15.763 / 22.937). Giá **04/11/2026 = 13.800** ⇒ −8,5% so tâm, +15,6% so P10, −34,3% so P90 ⇒ **TRONG vùng, dưới tâm** (40,3% trọng số lưới < giá). Tâm không đổi so với sổ 03/11 (15.100, −0,1%).

Nguồn: BCTC hợp nhất + riêng Q3/2026 + giải trình (`dd_MVC_20261103/src/`, `txt/`) — đã có, không tải lại; BCTN 2025. Mô hình = MVC r9 (`r9/calc/model_r9.py` → `nnc_model_r6` + `r8/calc/model_r8.py`, import không sửa; md5 `calc/LOCK_upstream_md5.txt`). Sector read: `kb/data_registry/market-state/sector_read_da_xay_dung_nam_bo_20261030.md` (chung với NNC). Số BCTC chép từ `investor_report/MVC_DD_investor_report_20261103.md` (qua skeptic R7) — không đọc lại PDF.

## 1. Giả thuyết
"Mỏ đá Tân Lập hưởng giá đỉnh + 44% NNC; giá dưới tổng tài sản sinh lời" — **nửa đúng**: kỳ vọng = Tân Lập ≈4.800 + cổ phần NNC ≈5.900 + hai mỏ mới theo vốn đã chi ≈3.900 + khác ≈3.100 − nợ ròng ≈1.200 (đ/cp, trước CK, bản 03/11). Nhưng đang mở rộng gấp đôi công suất bằng vay ngắn hạn, và biên ở đỉnh.

## 2. Chất lượng lợi nhuận
| tỷ đ | 9T/2025 | 9T/2026 |
|---|---|---|
| Doanh thu | 525,3 | 659,4 (+26%) |
| LN gộp · biên | 128,0 · 24,4% | 251,2 · 38,1% (gồm hoàn nhập tồn kho 4,9 một lần) |
| LNST hợp nhất | 104,1 | 231,8 (lãi liên kết 59,1 + cổ tức liên kết 10,6) |
| CFO · capex | 116,6 · 19,1 | 155,1 · 445,0 |
- ≈30% LNST là lãi liên kết theo vốn chủ (ít về tiền: cổ tức nhận 9T 10,6 tỷ). LNST riêng có hoàn nhập đầu tư 39,0 tỷ (phi tiền). FCF ≈−290 tỷ, tài trợ bằng rút tiền gửi 144 + vay ròng 205.

## 3. Bảng cân đối / net cash thật (30/09/2026)
Nợ ròng **116,6 tỷ**, đối ứng ≈438 tỷ đã chi cho hai mỏ mới (dở dang — **ghi theo giá vốn, NPV 0**, luật 03/11; 1.062 tỷ còn phải chi đối ứng giá trị tương đương). Dư nợ BIDV 452 tỷ > hạn mức 350 tỷ hợp đồng đã công bố. Lộ trình nợ ròng ước ≈610 tỷ cuối 2027, ≈1.070 tỷ cuối 2028 (r8, lãi suất giả định 7%, ước lượng). Tạm ứng 60,6 tỷ chưa thuyết minh đối tượng.

## 4. Ghi nhận doanh thu
Bán đá/gạch/xăng giao ngay; thu phí BOT ĐT743 (≈55 tỷ/năm). Không POC/backlog.

## 5. Cổ đông / thanh khoản
- Thanh Lễ 25%, bà Phạm Kim Oanh 24,9%, NNC 10,3%, ông Nguyễn Xuân Thuận 9,6% ⇒ free float ≈30,2% (ước). UPCOM.
- Thanh khoản (BQ `tav2_bq.ticker`, 250 phiên 03/11/2025–04/11/2026): ADV trung vị **0,44 tỷ** (60 phiên **0,19 tỷ**), σ 2,52%. Thoát 5 tỷ: **113 / 57 phiên** ở 10% / 20% ADV. CK (0,5/1,0/1,5): 1 tỷ 1,9/3,8/5,7% · **5 tỷ 4,2/8,5/12,7%** · 10 tỷ 6,0/12,0/18,0%. Theo ADV 60 phiên, CK 5 tỷ = 12,98% (độ nhạy). Vị thế thực tế nên ≤1 tỷ.

## 6. Pháp lý / quản trị — WARNING (không loại, không vào base)
Chủ tịch HĐQT MVC đồng thời Chủ tịch Thanh Lễ và NNC; trưởng BKS MVC là TGĐ Thanh Lễ; sở hữu chéo MVC 44,07% NNC ↔ NNC 10,3% MVC (MVC lên 51% NNC có thể buộc NNC thoái — Luật DN 2020 Đ.195, cần xác minh); giao dịch bên liên quan. Chưa thấy xử phạt/khởi tố.

## 7. Định giá
**Khung.** SOTP dòng tiền hữu hạn theo đời mỏ/hợp đồng, không terminal; V_NNC giải đồng thời trong từng trạng thái (60.606 trước CK — lệch −0,2% so NNC r6 60.702 vì bản vá Tân Lập r8 đi qua cổ phần MVC trong NNC; đã có từ r9). Mỏ mới + cụm CN + mua NNC 51%: NPV 0. Trạng thái: STRUCTURAL 0,20 → 23.267 · ADMIN_GATED 0,45 → 15.020 · CYCLICAL 0,35 → 14.485 (trước CK).

**r.** `deposit_rate_vn` asof 04/11 = **7,40%** (cctg_12m 02/11) = điểm neo ⇒ **r 13,5%** (Ke nội địa, không CRP).

| Lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| β=1,0 (tâm trước CK) | 16.931 (+2,7%) | 16.702 (+1,3%) | 16.270 (−1,3%) | 16.066 (−2,5%) |
| β=0,5 | 16.702 (+1,3%) | 16.591 (+0,7%) | 16.375 (−0,6%) | 16.270 (−1,3%) |

**Lưới chuẩn hoá.** 2.187 ô = trạng thái (0,20/0,45/0,35) × chi phí Tân Lập 0,85/1,0/1,15 × REL 0,88/0,91/0,95 × đường giá 70-30/50-50/30-70 × sản lượng năm thường 3 mức × hạn GP Tân Lập 2035/W/2045 × ánh xạ ADMIN 3 mức; r cố định 13,5%. Biên chu kỳ Tân Lập 25%/30% (CHƯA KIỂM; chỉ chiều xuống) để ở độ nhạy: tâm 15.377 / 15.907 trước CK.

| | P10 | P50 | P90 | Tâm |
|---|---|---|---|---|
| Trước CK | 13.049 | 15.763 | 22.937 | 16.482 |
| **Sau CK 8,49%** | **11.941** | **14.424** | **20.989** | **15.082** |
| So sánh: lưới r9 "kỳ vọng từng ô" r13,5 (n=39.366, trước CK) | 14.442 | 16.481 | 19.342 | |

Kiểm chéo ngược chiều (r9): Gordon ROE chuẩn hoá trộn 10,1% ⇒ ≈10.400 (thấp hơn giá). Kịch bản = trạng thái biên; trọng số là nhận định của Bobby (ước lượng).

## 8. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)
| Mốc | Thời điểm | Tích cực hơn nếu | Tiêu cực hơn nếu |
|---|---|---|---|
| BCTC Q4/2026 | ~01/2027 | Biên gộp quý ≥35%; nợ ròng theo lộ trình | Biên <28% khi DT đi ngang |
| Giá đá công bố Sở XD Đồng Nai | Q2/2027 | Tăng >7% | Giảm >7% |
| Giấy phép khai thác 2 mỏ mới / tổng vốn | 2027 | Cấp đúng hạn, vốn ≤1.500 tỷ | Trễ; vốn >1.950 tỷ |
| Hợp đồng tín dụng mới; nợ ròng | Q4/2026–2027 | Vay dài hạn thay ngắn hạn | Nợ ròng vượt lộ trình >150 tỷ (cuối 2027 >≈760 tỷ) |
| Giá cổ phiếu | — | < P10 11.941 ⇒ DƯỚI vùng | > P90 20.989 ⇒ TRÊN vùng |

## Phụ lục — cái gì ĐỔI so với DD cũ (sổ mức giá MVC rev8, 03/11/2026: 14.000 / 15.100 / 16.500)
- **Tâm sau CK 15.100 → 15.082 (−0,1%)**: tâm trước CK = pin r9 16.482 (lệch +0,0); CK 5 tỷ 8,4% → 8,49% (ADV 0,45 → 0,44 tỷ khi cửa sổ trượt tới 04/11).
- **Vùng đổi định nghĩa**: cũ = P25–P75 lưới "kỳ vọng từng ô" sau CK (14.000–16.500); mới = P10–P90 lưới có trạng thái là trục (11.941–20.989). Cận trên +27%, cận dưới −15% — **>10%, nguyên nhân chính: định nghĩa lưới** (trạng thái STRUCTURAL 20% kéo đuôi trên; CYCLICAL + chi phí cao kéo đuôi dưới).
- Giá 13.300 (03/11) → 13.800 (04/11). Nhãn cũ "RẺ CÓ ĐIỀU KIỆN" → "TRONG vùng".

## Open issues
Biên chu kỳ mảng đá Tân Lập chưa kiểm (không có báo cáo bộ phận); hạn giấy phép Tân Lập và BOT chưa công bố; free float ước; xác suất trạng thái là nhận định. Chưa qua fundamental-skeptic vòng này.
