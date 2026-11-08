# PVT — DD làm lại VÒNG 3 (08/11/2026, job `Taylor_20261108_153736`) — áp đính chính fundamental-skeptic 08/11

> NGHIÊN CỨU nội bộ, không phải khuyến nghị. Đính chính: `../TOP5B_CORRECTIONS_20261108.md` mục PVT (user duyệt áp). Chuẩn: `../STANDARD_r2.md`.
> Số: `calc_r3/pvt_r3.py` → `pvt_r3_out.json` (giả định khoá ở `calc_r3/assumptions_r3.json`; `calc_r3/LOCK_md5.txt` chốt TRƯỚC khi đọc giá) → `calc_r3/pvt_r3_compare.py` → `SUMMARY.json` (bản r2: `SUMMARY_r2.json`).
> Hai script đều chạy 2 lần, output trùng byte (`run1.md5`=`run2.md5`, `cmp1.md5`=`cmp2.md5`). Mô hình FCFE cổ đông mẹ của r1/r2 giữ nguyên; chỉ đổi giả định.

## 0. Kết luận
| Ba con số (đ/cp) | Trước CK | Sau CK (cỡ tham chiếu 5 tỷ, 0,67%) |
|---|---|---|
| **Tâm** (kỳ vọng trọng số lưới kết cục) | 18.968 | **18.841** |
| **P50 kết cục** | 18.958 | **18.830** |
| **Giá trị tại tham số trung tâm** (cơ sở, m=1, Δr=0, không mua thêm tàu) | 18.958 | 18.830 |
| **P10 / P90 kết cục** | 13.997 / 24.370 | **13.903 / 24.207** |

- n = **90 kết cục**; min 10.792, max 28.432. Giá **đóng cửa 06/11/2026: 20.550** (BQ `tav2_bq.ticker`) ⇒ so tâm **+9,1%**, **67,1% trọng số dưới giá** ⇒ **TRONG vùng** (giữa P50 18.830 và P75 21.705). r2: TRONG — nhãn không đổi.
- Cỡ sleeve thật (10–40 triệu): CK 0,03–0,06% ⇒ giá trị ≈ tâm trước CK **18.968** (Q/ADV 0,01–0,04%, ngoài vùng hiệu chỉnh luật căn bậc hai, chỉ là cận trên). Nhãn không đổi theo cỡ.
- So r2: tâm **17.675 → 18.841 (+1.166, +6,6%)**; P10 12.533 → 13.903; P90 23.135 → 24.207. Cầu từng bước ở §6.
- Lưới đối xứng ⇒ tâm, P50 và giá trị tại tham số trung tâm gần trùng nhau. P10/P90 do tổ hợp nhiều trục quyết định (không có nhánh trọng số nhỏ nào chi phối riêng).
- **Giá ngụ ý:** 20.550 ⇔ ROE giữa chu kỳ **14,20%** vĩnh viễn (base 13,15% = trung vị 2015–25; trung vị 2018–25 = 14,48%) **hoặc** r **12,60%** (lãi huy động 12T ngụ ý 6,50% so với 7,40%). Nói cách khác: giá đang trả cho một chu kỳ không có lại đáy 2015–17.
- Bản song song duy nhất cho TRÊN vùng: neo kế hoạch 5 năm của HĐQT (tâm 12.079). Bản "ROE bỏ lãi tiền gửi" của r2 (14.219, TRÊN) **bị bỏ** vì là kiểm chéo một chiều (§4).

## 1. Kiểm từng đính chính (calc, không chép)
| # | Đính chính skeptic | Kết quả kiểm | Áp? |
|---|---|---|---|
| 1 | Trọng số 0,35/0,45/0,20 + hệ số ROE 0,85/1/1,1 là nhận định Bobby lệch xuống, chồng lên trung vị cả chu kỳ ⇒ đếm chu kỳ hai lần | Tái lập **trùng** cả 3 số skeptic: chỉ đối xứng trọng số **18.212**, chỉ hệ số **18.050**, cả hai **18.506**. Với trọng số đối xứng, NPV tàu kỳ vọng = **0,00 đ** (r2 −86 đ biến mất). Trung vị 13,15% đã gồm đáy 2015–17 nên hệ số 0,85 ở nhánh xấu là phạt lần hai | **Áp**: base đối xứng 0,275/0,45/0,275 và 0,9/1/1,1; bản Bobby sang độ nhạy (`bobby_asym` 18.005) |
| 2 | LN mẹ 2027 cơ sở 1.250 mâu thuẫn lý do "biên như Q3" (Q3 năm hoá ≈1.500); đề xuất 1.200/1.450/1.700 | Đúng: LNST mẹ Q3/2026 375,1 tỷ × 4 = **1.500** (BQ NP_P0 2026Q3 = BCTC 375,13). Tái lập 1.450 → **18.774** (trùng). Mức −50 của skeptic không có cơ sở từ run-rate Q3 ⇒ base lấy đúng số quan sát **1.500 ±250**; tuy nhiên TT99 làm biên 2026 thiên lệch tăng (cận dưới: hoàn nhập dự phòng phi tiền mặt 85,4 tỷ/9T, §5), khoản trừ tương ứng ~73 tỷ/năm phần mẹ kéo tâm về ~**18.743** (−98 đ; số từ skeptic, chưa chạy lại) — ghi như độ nhạy, không đổi base (1.250/1.500/1.750) | **Áp một phần**: 1.500; bản 1.450 là độ nhạy (−67 đ); độ nhạy TT99 ~73 tỷ/năm: ~−98 đ (từ skeptic, chưa chạy lại) |
| 3 | Bản "ROE bỏ lãi tiền gửi" chỉ trừ lãi gửi, giữ lãi vay ⇒ một chiều | Đúng: 9T lãi tiền gửi, cho vay **251,0** < chi phí lãi vay **345,6** ⇒ lãi RÒNG phần mẹ **−81 tỷ/năm**. Bỏ lãi ròng ⇒ ROE **13,98%** (không phải 10,97%); trừ thêm nợ ròng phần mẹ ⇒ tâm **19.228** | **Áp**: bản r2 bỏ khỏi §0; bản lãi ròng chỉ để kiểm chéo |
| 4 | Thiếu WARNING PVT Logistics chào bán thêm cổ phần; ý kiến kiểm toán 2025 treo 2 vòng | Đúng: PDV chào bán ~56,9 tr cp @10.000 cho cổ đông hiện hữu (~569,5 tỷ, tàu tối đa 29 tr USD, Q4/2026–Q2/2027). Câu r2 "chưa có đợt cụ thể" sai ở cấp công ty con. Ý kiến kiểm toán: **chưa kiểm được** (§5) | **Áp** (warning + đóng thành "chưa kiểm") |
| 5 | Giá tham chiếu 20.550 (06/11), % dưới giá r2 = 72,2% | BQ Price 06/11 = **20.550**; % trọng số r2 dưới 20.550 = **72,2%** (trùng) | **Áp** |
| 6 | Provenance 9.855,6 và 251,0 chỉ truy về REPORT 29/10 | Kiểm trên **text** BCTC HN Q3: VCSH 12.862.928.406.161 − CĐKKS 3.007.359.354.829 = **9.855,569 tỷ** (dòng 933/1005); lãi tiền gửi, cho vay 9T **250.953.803.131** (dòng 4249); lãi vay 9T 345.641.490.397 (dòng 1171). **PDF gốc vẫn chưa mở** (không có bản local; pymupdf không chạy được) | **Áp** — đã kiểm từ text; PDF: chưa kiểm |

## 2. Lưới r3 + giả định khoá
| Trục | Điểm (trọng số) | Chiều | Cơ sở |
|---|---|---|---|
| LN mẹ 2027 / chu kỳ cước | 1.250 / **1.500** / 1.750 (0,275/0,45/0,275); hệ số ROE theo kịch bản 0,9/1,0/1,1 | hai, đối xứng | Q3/2026 × 4 (dữ liệu); biên độ ±250 [UL] |
| ROE giữa chu kỳ | 0,8…1,2 × 13,15% (trung vị `ROE_Trailing` Q4 2015–25, BQ) | hai | dữ liệu + hệ số [UL] |
| Lãi huy động 12T | −50/0/+50bp (0,25/0,5/0,25) | hai | r = 13,5% + 1,0×(7,40% − 7,40%) = **13,5%** (06/11) |
| Mua tàu phần capex 2026 còn lại | mua 2.465 tỷ / không (0,5/0,5 [UL]) × NPV −30/0/+30% theo kịch bản [UL] | hai; kỳ vọng 0 | ĐHĐCĐ 2026 3.445 tỷ; 9T đã tăng nguyên giá 979,6 [TM12] |

Giả định [UL] khác: g 3%; NCI 19,6% (9T/26). Đầy đủ từng giả định + cơ sở: `SUMMARY.json → assumptions`.
**Base so với sổ sách:** không có khoản lệch nào. Nợ ròng 619,3 đã nằm trong LN sau lãi vay và VCSH (không trừ lần nữa); tàu mới NPV kỳ vọng 0.

## 3. Headline và các biến thể song song (sau CK 5 tỷ, giá 20.550)
| Bản | Tâm | P10 / P90 | % dưới giá | Nhãn |
|---|---|---|---|---|
| **HEADLINE r3** | **18.841** | 13.903 / 24.207 | 67,1% | TRONG |
| np27 1.450 (skeptic) | 18.774 | 13.840 / 24.136 | 67,1% | TRONG |
| np27 1.250 (r2), trọng số/hệ số đối xứng | 18.506 | 13.591 / 23.852 | 67,1% | TRONG |
| Bobby lệch xuống (trọng số + hệ số r2) | 18.005 | 12.839 / 23.482 | 72,2% | TRONG |
| chỉ trọng số lệch xuống | 18.383 | 13.768 / 23.482 | 71,4% | TRONG |
| chỉ hệ số ROE lệch xuống | 18.545 | 13.451 / 24.207 | 67,8% | TRONG |
| NPV tàu = 0 mọi kịch bản | 18.841 | 14.414 / 23.668 | 67,8% | TRONG |
| Kiểm chéo: ROE bỏ lãi RÒNG + trừ nợ ròng | 19.228 | 13.990 / 24.925 | 64,3% | TRONG |
| Neo kế hoạch 5 năm NQ HĐQT (LN mẹ 933 tỷ/năm, ROE 9,46%) | 12.079 | 8.573 / 15.907 | 100% | **TRÊN** |

Độ nhạy r (tâm sau CK): −100bp **20.755** · −50bp 19.750 · 0 18.841 · +50bp 18.015 · +100bp 17.262. Chỉ khi lãi huy động giảm 100bp thì tâm mới vượt giá (khi đó chỉ cao hơn ~1%).
Ghi chú độ nhạy (không đổi số base, chưa chạy lại): (a) RONIC = Ke thay RONIC = ROE (ROE giữa chu kỳ 13,15% < Ke) ⇒ tâm **18.989** (+148); (b) hai trục chu kỳ (kịch bản LN/ROE và hệ số ROE giữa chu kỳ) cùng nhân ROE terminal nên dải P10–P90 rộng hơn so với nếu chỉ một trục; (c) nhãn TRONG chỉ chịu ±1pp ROE giữa chu kỳ (giá 20.550 ≈ ROE 14,2% vĩnh viễn).
Neo kế hoạch: không đưa vào base vì mục tiêu ban điều hành thường thận trọng (KH 2026 LNST HN 1.200 so với 9T thực 1.581,8), nhưng đây là dữ liệu quan sát được kéo xuống nên vẫn báo cạnh nhãn.

## 4. Cross-check Gordon/ROE (điều 10)
BVPS mẹ 19.066. ROE 13,15% (gồm cả lãi gửi lẫn lãi vay) ⇒ P/B Gordon 0,967 ⇒ **18.433 đ/cp**. Bỏ lãi RÒNG (−81 tỷ/năm phần mẹ) ⇒ ROE 13,98%: ROE **tăng**, không giảm, vì PVT trả lãi vay nhiều hơn nhận lãi gửi. Bản r2 (10,97% / 14.467 Gordon / 14.219 lưới) chỉ trừ lãi gửi nên lệch một chiều ⇒ bỏ. Cả hai biến thể đúng đều < giá 20.550.

## 5. Pháp lý / quản trị — WARNING
- **MỚI — PVT Logistics (PDV, công ty con)** chào bán ~56,9 tr cp @10.000 cho cổ đông hiện hữu (~569,5 tỷ), đầu tư tàu dầu/hoá chất + hàng rời tối đa 29 tr USD, Q4/2026–Q2/2027 (doanhnhan.baophapluat.vn, tra 08/11/2026; `calculated_fear_state_backstop.md`: xin ý kiến 05/10). Rủi ro: mua tàu ở đỉnh giá + pha loãng NCI nếu PVT không mua đủ quyền (PVT có đăng ký mua hay không: **chưa kiểm**). HOSE từng nhắc nhở PDV chậm công bố thương vụ mua tàu PVT Opal. Không định lượng vào base (quyền mua theo tỷ lệ = phân bổ vốn, NPV0).
- **Ý kiến kiểm toán BCTC 2025 / soát xét H1/2026: CHƯA KIỂM ĐƯỢC** — WebSearch 08/11/2026 không ra văn bản ý kiến; text BCTC Q3 không chứa. Nếu có ngoại trừ liên quan dry-dock/TT99 thì tác động gần với độ nhạy np27 1.250 (**−335 đ/cp**).
- Thay TGĐ 2 lần trong 4 tháng (Trần Ngọc Nguyên miễn nhiệm 01/07; Nguyễn Thanh Bình từ 03/08/2026), lý do không công bố.
- Bên PVN 22,4% DT 9T (Q3 31,7%); phải thu đơn vị PVN 1.144,7 tỷ (+130%).
- TT99/2025 + TT43/2026: ngừng trích trước sửa chữa lớn từ 01/01/2026 ⇒ biên 2026 thiên lệch tăng, độ lớn chưa xác định (cận dưới thấy được: hoàn nhập dự phòng 85,4 tỷ/9T phi tiền mặt).
- Phải thu cũ liên quan Huỳnh Thị Huyền Như 73,1 tỷ đã dự phòng 100%; Chủ tịch đăng ký bán 200.000 cp rồi không bán (03–04/2026).
- Chưa thấy khởi tố/xử phạt: DD 29/10, WebSearch 05/11 và 08/11/2026.

## 6. Cầu r2 → r3 (tâm sau CK)
| Bước | Tâm | Δ | Lý do |
|---|---|---|---|
| r2 công bố | 17.675 | — | tái lập center_pre 17.794 trùng (control) |
| Giá 21.000 → 20.550; CK theo ADV tới 06/11 (0,6707% → 0,6711%) | 17.675 | 0 | chỉ đổi nhãn/% dưới giá: 78,3% → 72,2% |
| + trọng số đối xứng 0,275/0,45/0,275 | 18.212 | +537 | đính chính 1a |
| + hệ số ROE đối xứng 0,9/1/1,1 | 18.506 | +294 | đính chính 1b |
| + LN mẹ 2027 cơ sở 1.500 ±250 | **18.841** | +335 | đính chính 2 (lấy số quan sát) |

## 7. Thanh khoản
| | ADV 250 phiên (05/11/25–06/11/26) | ADV 60 phiên |
|---|---|---|
| GTGD trung vị | 94,60 tỷ | 127,93 tỷ |
| CK 5 tỷ (nhãn) | **0,67%** (Q/ADV 5,3%, trong vùng hiệu chỉnh) | 0,50% |
| CK sleeve 10 / 20 / 40 triệu | 0,03% / 0,04% / 0,06% (ngoài vùng hiệu chỉnh) | 0,02% / 0,03% / 0,04% |

## 8. Mốc đổi nhận định
- **Xấu đi** (sang TRÊN vùng): giá > P90 24.207; LNST mẹ Q4/2026 < 300 tỷ; tác động TT99 > 150 tỷ; mua tàu lớn ở đỉnh trước 31/12/2026 mà không có hợp đồng đầu ra; PVT không mua quyền PDV và NCI bị pha loãng ở giá dưới book; ý kiến kiểm toán có ngoại trừ; Bobby F2 (30/09/2027): LN mẹ 9T/27 ≤ 900.
- **Tốt lên** (sang DƯỚI vùng): giá < P10 13.903; Bobby F1 (31/03/2027): BDTI ≤4.200 mà biên vận tải Q1/27 vẫn ≥20%; công bố ≥60% ngày tàu TC dài hạn tới 2028.
- **Giá hợp lý hơn nhưng CHƯA sang DƯỚI vùng**: lãi huy động −100bp (tâm 20.755, chỉ cao hơn giá ~1% — vẫn TRONG vùng; DƯỚI vùng cần giá < P10).
- **HARD ABANDON**: kiểm toán lộ doanh thu/tài sản bị thổi phồng; phát hành cổ phiếu dưới book để mua tàu; PVN ép giao dịch liên quan bất lợi.
- Tranche: không áp dụng. **Sleeve fear-buy §2.5: KHÔNG đủ điều kiện** — không có khủng hoảng, LN ở đỉnh chu kỳ, drawdown từ đỉnh 52 tuần < ngưỡng T1 35%. (Đính chính câu r2 "P/B 1,10 > trung vị 0,91": tính cùng gốc VCSH gồm NCI thì P/B ≈ 0,86 theo skeptic 29/10 §14.1 ⇒ bỏ lý do P/B, kết luận NON không đổi.)

## 9. Còn mở / lưu ý skeptic chưa kiểm được
- Ý kiến kiểm toán 2025 / soát xét H1 — chưa kiểm; độ nhạy ~−335 đ (§5).
- PDF gốc BCTC Q3 (11,8MB) — chưa mở; số đã kiểm khớp từ text đến từng đồng.
- PVT có đăng ký mua quyền PDV hay không — chưa kiểm; tác động lên giá trị PVT chưa đo (nếu PVT bỏ quyền: pha loãng phần sở hữu ở công ty con; nếu mua đủ: phân bổ vốn, NPV0).
- Định lượng TT99; tỷ trọng TC/spot + đáo hạn hợp đồng; số/ngày NQ kế hoạch 5 năm; room ngoại.

## 10. LOCK + tái lập
`calc_r3/LOCK_md5.txt` (chốt trước khi so giá): outputs `pvt_r3_out.json/.txt`, `grid_pvt_r3.csv`; upstream `pvt_r3.py`, **`assumptions_r3.json`**, `px_pvt_r3.sql`, `px_pvt_r3_20261106.csv`, `calc/model.py`, `calc/bq_hist_out.csv`, `calc/model_r2_out.json`, `_common_014127/common.py`, `_shared/wpct.py`, `deposit_rate_vn.py`, `cctg_rate_vn.py`, `data/deposit_rate_vn_events.csv`, `data/cctg_rate_vn_events.csv`, `dd_PVT_20261029/src/q3_pvt_hopnhat_text.txt`, `dd_PVT_20261029/REPORT.md`, `TOP5B_CORRECTIONS_20261108.md`, `STANDARD_r2.md`. `pvt_r3_compare.py` kiểm lại md5 từng dòng trước khi đọc giá.
`cd calc_r3 && $DNA_PYEXE -I pvt_r3.py && $DNA_PYEXE -I pvt_r3_compare.py`.
`ADDENDUM_5F.md` / `SUMMARY_5F.json` đã đồng bộ headline r3 (giữ banner `final_convention_20261108`; số 5F bên trong là độ nhạy trên mô hình r2).
