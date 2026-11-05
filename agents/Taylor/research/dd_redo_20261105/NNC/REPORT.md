# NNC — DD redo mùa BCTC Q3/2026 (05/11/2026, job Taylor_20261105_014135)

**Kết luận (số từ `calc/nnc_redo_out.txt`):** tâm (kỳ vọng trọng số kịch bản) **58.497 đ/cp SAU chiết khấu thanh khoản** (60.702 trước; CK 3,63% cho vị thế 5 tỷ). Lưới chuẩn hoá 243 ô có trọng số: **P10 44.917 · P50 56.395 · P90 85.649** (sau CK; trước CK 46.610 / 58.521 / 88.878). Giá đóng cửa **04/11/2026 = 46.900** ⇒ −19,8% so tâm, +4,4% so P10, −45,2% so P90 ⇒ **TRONG vùng, sát cận dưới** (17,6% trọng số lưới cho giá trị < giá). Nhãn cũ "RẺ (dưới P10)" đổi thành "TRONG vùng" vì **định nghĩa lưới** đổi (mục 7), không phải vì cơ bản: tâm không đổi.

Nguồn chính: BCTC riêng Q3/2026 (`dd_NNC_20261026/src/NNC_Baocaotaichinh_Q3_2026.pdf`, ký 19/10/2026) — đã có, không tải lại; BCTC 2025 kiểm toán AASCs; BCTN 2025; mô hình `dd_NNC_20261030/r6/calc/nnc_model_r6.py` (import, không sửa; md5 ở `calc/LOCK_upstream_md5.txt`). Sector read: `kb/data_registry/market-state/sector_read_da_xay_dung_nam_bo_20261030.md` (Bobby, mù). Số BCTC dưới đây chép từ báo cáo 03/11 (`dd_NNC_20261030/investor_report_v3/NNC_DD_investor_report_20261103.md`, Phụ lục A, đã qua skeptic R4) — không đọc lại PDF trong phiên này.

## 1. Giả thuyết
"Mỏ đá có giấy phép tới 2043, bán ở giá đỉnh chu kỳ; phần lớn giá trị nằm ngoài biên đỉnh" — **nửa đúng**: ≈25.300 đ/cp là tiền ròng sau nghĩa vụ (10.200), 10,3% MVC (7.800), Tam Lập 1 khu II theo vốn đã chi (3.400), phần khác (3.800); mỏ Mũi Tàu ≈35.500 trong tâm. Biên ở đỉnh 15 năm là rủi ro chính.

## 2. Chất lượng lợi nhuận (BCTC riêng Q3/2026)
| tỷ đ | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|
| Doanh thu | 149,49 | 100,27 | 402,20 | 261,89 |
| LN gộp | 86,54 | 50,67 | 218,52 | 128,34 |
| DT tài chính (lãi tiền gửi ~348 tỷ) | 6,07 | 7,60 | 15,60 | 13,48 |
| LN khác | −0,00 | −1,88 | −19,29 | −4,18 |
| LNST | 69,29 | 42,56 | 160,08 | 93,95 |
- Tăng trưởng gần như hoàn toàn từ GIÁ đá (sản lượng chạm trần giấy phép từ 2025). Biên gộp 31,6% (2024) → 49,4% (2025) → 57,9% (Q3/26).
- LN khác 9T −19,3 tỷ = truy thu/một lần (không bền). CFO 9T 109,3 tỷ = 0,68× LNST (nộp thuế 2025 + truy thu); hai năm ≈0,96×.
- Bên liên quan NHC: 16% phần tăng DT Q3; 61% phải thu.

## 3. Bảng cân đối / net cash thật (30/09/2026)
Tiền 25,47 + tiền gửi có kỳ hạn 322,44 − vay 5,00 + 69,89 − dự phòng truy thu 22,37 − quỹ KTPL 16,78 − cổ tức phải trả 5,89 − dự phòng môi trường 4,50 = **tiền ròng sau nghĩa vụ 223,6 tỷ (≈10.200 đ/cp)**. Không có tiền ứng trước khách hàng phải tiêu cho hợp đồng. XDCB dở dang Tam Lập 1 khu II 83,51 tỷ. Vốn chủ 655,73 tỷ (BVPS 29.915).

## 4. Ghi nhận doanh thu
Bán đá giao ngay tại mỏ (ghi nhận khi giao hàng), không có POC/backlog. Q4 thường mùa cao điểm xây dựng; mô hình ước LNST Q4/2026 60 tỷ (ước lượng).

## 5. Khách hàng / cổ đông / room / thanh khoản
- MVC 44,07%, CTCP Đầu tư Thái Bình 15,93%; free float ≈36,3% (ước từ cổ đông lớn 63,7%, FPTS 07/01/2026).
- Thanh khoản (BQ `tav2_bq.ticker`, 250 phiên 03/11/2025–04/11/2026): ADV trung vị **2,10 tỷ** (60 phiên: 1,39 tỷ), σ ngày 2,35%. Thoát 5 tỷ: 24 / 12 phiên ở 10% / 20% ADV. CK (hệ số 0,5/1,0/1,5): 1 tỷ 0,8/1,6/2,4% · **5 tỷ 1,8/3,6/5,4%** · 10 tỷ 2,6/5,1/7,7%. Theo ADV 60 phiên, CK 5 tỷ = 4,46% (độ nhạy). Sizing tiền lệ ≤0,5–1,0% NAV.

## 6. Pháp lý / quản trị — WARNING (không loại, không đưa vào base)
- Sở hữu chéo MVC↔NNC (MVC ≥51% có thể buộc thoái cổ phần MVC — cần ý kiến pháp lý).
- Bên liên quan NHC (phải thu tập trung), định hướng bất động sản với tiền giữ lại; cổ tức tiền 2025 chỉ ≈15% LNST.
- Phạt hành chính nhỏ (0,63 tỷ 2024; 0,04 tỷ 2025). Kiểm toán 2025: chấp nhận toàn phần. Rủi ro "scandal di cư": thấp (chưa thấy).

## 7. Định giá
**Khung.** PV NOPAT Mũi Tàu 2027–2043 (không terminal, thuế 20%) + cho thuê Núi Nhỏ + tiền ròng + cổ phần MVC (giải đồng thời) + Tam Lập 1 khu II **theo vốn đã chi (NPV = 0, luật 03/11)**. Từ 2028 trộn 3 trạng thái biên của Bobby: STRUCTURAL 0,20 → 88.878 · ADMIN_GATED 0,45 → 54.522 · CYCLICAL 0,35 → 52.547 (trước CK).

**r.** Lãi huy động 12T hiệu dụng `deposit_rate_vn` asof 04/11/2026 = **7,40%** (cctg_12m 02/11/2026) = điểm neo ⇒ r = 13,5% + 1,0×0 = **13,5%**. Ke nội địa, không cộng CRP.

| Lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| β=1,0: r · giá trị (trước CK) | 12,5% · 62.675 (+3,3%) | 13,0% · 61.666 (+1,6%) | 14,0% · 59.780 (−1,5%) | 14,5% · 58.898 (−3,0%) |
| β=0,5 | 13,0% · 61.666 (+1,6%) | 13,25% · 61.179 (+0,8%) | 13,75% · 60.236 (−0,8%) | 14,0% · 59.780 (−1,5%) |

Độ nhạy thấp (≈1,5%/50bp) vì mỏ có hạn 2043 và >40% giá trị là tiền/cổ phần/vốn đã chi.

**Lưới chuẩn hoá (định nghĩa liên mã).** 243 ô = trạng thái biên (trọng số 0,20/0,45/0,35) × K chi phí 0,87/0,97/1,07 × sản lượng năm thường 3 mức × đường giá g2031/real 70-30/50-50/30-70 × ánh xạ ADMIN 3 mức; trọng số ô = xác suất trạng thái × đều; r cố định 13,5%. Phân vị có trọng số. TB lưới 62.393 (≠ tâm 60.702 vì trục ADMIN/sản lượng lệch nhẹ về phía tăng). P90 = 88.878 trùng nhánh STRUCTURAL (nhánh này không phụ thuộc trục sản lượng/ADMIN ⇒ khối 20% trọng số ở cùng một số). `cap_basis 1,40` (chỉ chiều xuống, −3.335) để ở độ nhạy, không vào lưới đối xứng.

| | P10 | P50 | P90 | Tâm |
|---|---|---|---|---|
| Trước CK | 46.610 | 58.521 | 88.878 | 60.702 |
| **Sau CK 3,63%** | **44.917** | **56.395** | **85.649** | **58.497** |
| So sánh: lưới r6 "kỳ vọng từng ô" (r 13,5%, n=1.458, trước CK) | 52.755 | 63.040 | 74.160 | |

**Kịch bản xấu/cơ sở/tốt (trọng số Bobby, giả định của Bobby = ước lượng):** CYCLICAL 52.547 (0,35) / ADMIN_GATED 54.522 (0,45) / STRUCTURAL 88.878 (0,20). Stress đường giá danh nghĩa phẳng: 48.310 (trước CK). Kiểm chéo ngược chiều: Gordon ROE chuẩn hoá 17,2% ⇒ 40.480 (thấp hơn giá).

## 8. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)
| Mốc | Thời điểm | Tích cực hơn nếu | Tiêu cực hơn nếu |
|---|---|---|---|
| BCTC Q4/2026, Q1/2027 | ~20/01, ~20/04/2027 | Biên gộp ≥55% | Biên <45% khi doanh thu đi ngang |
| Giá đá công bố Sở XD | Q2/2027 | Cao hơn Q3/2026 >7% | Thấp hơn >7% |
| Vành đai 4 / giấy phép mỏ đấu giá trong cụm | tới 30/06/2027 | ≥20% khối lượng; mỏ mới chậm | <20%; mỏ mới cấp sớm |
| Lãi huy động 12T | liên tục | −50bp ⇒ +1,6% | +50bp ⇒ −1,5% |
| Giá cổ phiếu | — | < P10 44.917 ⇒ DƯỚI vùng | > P90 85.649 ⇒ TRÊN vùng |

## Phụ lục — cái gì ĐỔI so với DD cũ (sổ mức giá NNC rev4, 03/11/2026: 55.000 / 58.500 / 66.900)
- **Tâm sau CK: 58.500 → 58.497 (−0,0%)** — không đổi: r giữ 13,5% (lãi huy động hiệu dụng không đổi 7,40%), ADV 250 phiên 2,10 tỷ như cũ, BCTC Q3 như cũ. Chân đối chứng: tâm trước CK tái lập pin r6 60.702 (lệch −0,0).
- **Vùng: đổi định nghĩa** từ P25–P75 của lưới "kỳ vọng từng ô" sang P10–P90 của lưới có trạng thái là một trục (yêu cầu job). Cận trên mới 85.649 lệch +28% so cận trên cũ 66.900; cận dưới 44.917 lệch −18% so 55.000 — **>10%, nguyên nhân chính: định nghĩa lưới** (lưới cũ trộn 3 trạng thái trong mỗi ô ⇒ phân tán bị nén; lưới mới để trạng thái biên quyết định phân tán).
- Giá 46.100 (03/11) → 46.900 (04/11).
- Nhãn: RẺ (dưới P10 lưới cũ 50.400 sau CK) → TRONG vùng (P10 mới 44.917).

## Open issues
Thời hạn hợp đồng thuê Núi Nhỏ (−2,0k…−3,4k/cp); bản chất trả trước dài hạn CNBP 59,2 tỷ (+2,1k); Tam Lập 1 khu II chưa có giấy phép; xác suất 3 trạng thái là nhận định, không phải tần suất. Chưa qua fundamental-skeptic vòng này (Mike chạy).
