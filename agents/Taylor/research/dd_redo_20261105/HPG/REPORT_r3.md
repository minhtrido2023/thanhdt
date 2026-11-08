# HPG — DD REDO vòng 3 (08/11/2026, job Taylor_20261108_142020)

> Áp đính chính của fundamental-skeptic 08/11 (`TOP5_CORRECTIONS_20261108.md`, mục HPG). Mỗi đính chính đã được kiểm lại bằng calc.
> Mọi số trong file này lấy từ `calc_r3/hpg_r3_out.txt` / `hpg_r3_out.json`. Chạy 2 lần, output trùng byte (`calc_r3/LOCK_md5.txt`).
> Chưa đặt lệnh, chưa sửa `kb/dd_price_zones.json`, chưa gửi email, chưa xuất PDF.

## 1. Kết luận

| | r2 (05/11) | **r3 (08/11)** |
|---|---|---|
| Giá tham chiếu | 21.700 (04/11) | **21.200 (đóng cửa 06/11, BQ `tav2_bq.ticker`)** |
| r | 13,50% | **13,50%** (lãi huy động 12T hiệu dụng 06/11 = 7,40% = mức neo) |
| Tâm (kỳ vọng lưới, sau CK 5 tỷ) | 16.286 | **21.338** |
| P10 / P50 / P90 (mức kết cục) | 8.942 / 16.343 / 23.520 | **13.316 / 21.759 / 28.993** |
| % trọng số dưới giá | 83,6% | **46,7%** |
| Giá vs tâm | +33,2% | **−0,6%** |
| Nhãn (vùng P10–P90, CK ở cỡ 5 tỷ) | TRONG vùng | **TRONG vùng** (nhãn giữ nguyên; giá nay nằm sát tâm) |

Ba con số tách bạch: tâm (kỳ vọng lưới) 21.338; P50 21.759; giá trị tại tham số trung tâm (TRUNG LẬP, hệ số 1, dg 0, dốc 0) 21.948.
Lưới n = 135 kết cục, min 10.770, max 35.403. P10 do nhánh XẤU quyết định, P90 do nhánh TỐT.

**Đọc kết luận:** ở giá 21.200, HPG được định giá **xấp xỉ hợp lý**: không rẻ mà cũng không đắt. Theo r2, giá cao hơn tâm 33%. Gần như toàn bộ chênh lệch đó là **lỗi mô hình** (vốn giữ lại sinh lời 0%), không phải kỳ vọng lạc quan của thị trường. Skeptic cũng đã nhận định vậy: "HPG là mã duy nhất mà phần lớn độ lệch là do mô hình". Mã **không** đủ điều kiện sleeve fear-buy §2.5.

## 2. Kiểm từng đính chính (calc, không chép)

| # | Đính chính skeptic | Kết luận kiểm | Tác động lên tâm (cộng dồn theo thứ tự bridge) |
|---|---|---|---|
| 1 | Vốn giữ lại 80% sinh lời 0% ⇒ RI terminal âm vĩnh viễn, trái luật 20 | **ĐÚNG về hướng, SỬA cách làm.** Kiểm lại: ROE_T TRUNG LẬP ở r2 = 11,84% < r. Cách "capex" của skeptic cho 35.585 tỷ đầu tiên của VỐN GIỮ LẠI sinh lời = r, nhưng XDCB 16.113 tỷ đã nằm trong BV0 vẫn sinh lời 0%. Như vậy lại phạt ngầm chính dự án dở dang, đúng loại lỗi luật 20 cấm. r3 làm như sau: XDCB trong BV0 sinh lời = r từ 30/09 (NPV0 đúng nghĩa, không cần tham số thời điểm); cam kết vốn 19.472 tỷ lấy từ vốn giữ lại cũng sinh lời = r; phần còn lại hưởng lãi huy động 12T sau thuế 5,92%. | **+5.309** |
| 3 | g_RI = g ở nhánh TỐT là thưởng moat ngầm | **ĐÚNG.** Moat NARROW COST/SCALE, không bền (5F 07/11) ⇒ g_RI = 0 ở mọi nhánh. Sau sửa #1, cả nhánh TRUNG LẬP cũng có ROE_T > r, nên tác động lớn hơn mức −270 skeptic ước. | **−1.152** |
| 4 | Trục TLSH lệch xuống [UL] (kỳ vọng mất 16,5%) | **ĐÚNG.** Không có dữ liệu suy giảm ⇒ base theo sổ sách; trục r2 chuyển thành bản song song E. | **+193** |
| 2 | Thuế 20% từ 2030 chưa có nguồn mốc | **ĐÚNG MỘT PHẦN.** Mốc 2030 đúng là không có nguồn ⇒ bỏ. Nhưng "giữ ETR ~12% vĩnh viễn" cũng không làm headline được, vì ưu đãi thuế TNDN có thời hạn theo luật (khu kinh tế: 10% trong 15 năm, miễn 4 năm, giảm 50% 9 năm). Headline: phần thép chịu 20% từ **2035**, giai đoạn 2030–34 giữ ETR hiện hành. Cơ sở: khung luật cộng ước lượng DQ1 hưởng 10% tới ~2034 (GAPS §2). **Mốc 2035 là ước lượng**, vì năm doanh thu đầu tiên của DQ1 chưa kiểm từ nguồn gốc. Bản song song B (2030) và C (vĩnh viễn) báo ở §4. ⚠️ **Cảnh báo:** "ETR hiện hành" suốt 2030–34 trái GAPS.md:70 (DQ1 lên 10% từ ~2032), và hệ số TAXF 0,80/0,88 (ETR 12%) không khớp ETR phân khúc thép đo được 6,5% (REPORT_v2 §3d); chưa chạy lại, không đổi số. | **+690** |
| 5 | Quét tin pháp lý 31/10–06/11; mở bản gốc QĐ 1917 | **ĐÃ LÀM** (tra web 08/11, kết quả ở §6). Không có tin mới làm đổi mô hình. Bản gốc QĐ 1917 vẫn **chưa mở được**: chỉ có nguồn báo chí. | 0 |

**Tái lập số skeptic** (khung r2: thuế 2030, g_RI kiểu r2, trục TLSH r2, giá 06/11):
- Sàn tiền gửi: **18.430**, skeptic ra 18.558. Lệch −128, do dùng tiền gửi sau thuế 5,92% (7,40% × 0,8) thay vì 6,0%, cộng với giá/ngày 06/11.
- Capex: **20.599** theo cách đọc "35.585 tỷ đầu tiên của vốn giữ lại = r", skeptic ra 19.529. **Không tái lập được** (lệch +1.070). Cách phân bổ capex của skeptic có thể khác; đã ghi vào open_issues.

## 3. Bridge r2 → r3 (`bridge_r2_to_r3`)

| Bước | Tâm | Δ | P10 | P90 |
|---|---|---|---|---|
| 0 r2 tái lập (control, giá 04/11) | 16.286 | — | 8.942 | 23.520 |
| 1 giá + thanh khoản 06/11, đẩy ngày định giá | 16.297 | +11 | 8.948 | 23.536 |
| 2 C1 vốn giữ lại: XDCB + cam kết = r, còn lại = tiền gửi sau thuế | 21.606 | +5.309 | 12.689 | 30.893 |
| 3 C3 g_RI = 0 mọi nhánh | 20.454 | −1.152 | 12.689 | 27.481 |
| 4 C4 TLSH về sổ sách | 20.648 | +193 | 12.924 | 28.006 |
| 5 C2 thuế 20% từ 2035 | **21.338** | +690 | 13.316 | 28.993 |

Control tái lập r2 trùng số (16.286 / P10 8.942 / P90 23.520), nên Δ ở từng bước đọc được trực tiếp.
ROE terminal sau thuế 20% (r3 so với r2): XẤU 10,36% (7,85%) · TRUNG LẬP 14,33% (11,84%) · TỐT 16,66% (14,25%).

## 4. Headline và các biến thể song song (`headline_vs_alternatives`)

| Biến thể | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| **HEADLINE r3** | **21.338** | 13.316 | 21.759 | 28.993 | 46,7% | TRONG |
| A Sàn skeptic: mọi vốn giữ lại = tiền gửi sau thuế | 18.693 | 10.713 | 19.103 | 26.340 | 65,6% | TRONG |
| B Như headline, thuế 2030 | 20.648 | 12.924 | 21.051 | 28.006 | 52,2% | TRONG |
| C Như headline, ETR 12% vĩnh viễn | 22.119 | 13.759 | 22.561 | 30.110 | 43,9% | TRONG |
| D Như headline, g_RI kiểu r2 (thưởng moat ngầm) | 22.530 | 13.316 | 22.274 | 32.115 | 46,1% | TRONG |
| E Như headline, giữ trục TLSH r2 | 21.144 | 13.070 | 21.524 | 28.420 | 48,2% | TRONG |
| F Vốn giữ lại 0% (lỗi r2), thuế 2035 | 16.911 | 9.634 | 17.264 | 23.914 | 80,6% | TRONG |
| G Tái lập skeptic, sàn 6% (khung r2) | 18.430 | 10.049 | 18.144 | 27.213 | 70,6% | TRONG |
| H Tái lập skeptic, capex (khung r2) | 20.599 | 11.586 | 20.444 | 29.896 | 56,0% | TRONG |
| I Cách capex của skeptic trong khung r3 (XDCB trong BV0 = 0%) | 20.456 | 12.202 | 20.925 | 28.185 | 53,3% | TRONG |
| J Nhánh TỐT chỉ hưởng tiền gửi (chống đếm trùng capex) | 20.673 | 13.316 | 20.827 | 27.256 | 50,0% | TRONG |
| Có trục r ±1pp (0,25/0,50/0,25) | 21.403 | 13.219 | 21.756 | 29.573 | 47,4% | TRONG |

Cả 12 biến thể đều cho nhãn TRONG vùng; tâm dao động 16.911–22.530. **Lý do chọn headline:**
- Đây là bản duy nhất vừa không phạt vốn dự án (luật 20, áp cho cả XDCB đã nằm trong BV0), vừa không thưởng tăng trưởng khi moat không bền, và không dùng mốc thuế thiếu nguồn.
- Rủi ro lệch lên của headline nằm ở nhánh TỐT: đường LN 31→35 nghìn tỷ có thể đã gồm một phần lợi ích từ capex. Bản J đo rủi ro này: −665.
- **Lưu ý đếm hai lần:** phần XDCB/DQ2 còn lại bị đếm hai lần ở nhánh TỐT: nhánh TỐT đã dùng phần này để biện minh cho đường LN 31–35 nghìn tỷ, trong khi XDCB đã sinh lợi = r trong vốn giữ lại. Bản J (nhánh TỐT chỉ hưởng tiền gửi) cho tâm **20.673**. **Khoảng tâm 20.673–21.338; headline giữ 21.338.**
- **Cam kết vốn 19.472 là số tại 30/06/2026** (notes_bs.md:73, TM41), không phải HN-Q3 30/09; phần chi Q3 đã chuyển vào XDCB 30/09 nên đếm trùng khoảng −200 đ/cp ở mức r (ước lượng, chưa chạy lại, không sửa số).

Độ nhạy r (tâm): −100bp 23.213 · −50bp 22.239 · +50bp 20.501 · +100bp 19.722.

## 5. Giá ngụ ý (`implied_by_price`)

- r làm tâm = giá 21.200: **13,58%**, gần như trùng r luật 13,50%.
- Hệ số đường LN làm tâm = giá: **0,993**. Tương ứng ROE terminal TRUNG LẬP sau thuế 20% ≈ **14,27%** (ROE5Y 16,9%; trung bình 2022–25 9,6%).
- Nếu mọi vốn giữ lại sinh lời đồng đều y thì giá ngụ ý y = **12,59%** (khung r2) hoặc **13,68%** (khung r3, tức ≈ r). Skeptic ra ~11,6% (khung khác).
- ⇒ Ở 21.200, thị trường chỉ đòi HPG tái đầu tư với lợi suất bằng chi phí vốn. Không có kỳ vọng tăng trưởng giá trị, cũng không phạt.

## 6. WARNING pháp lý / quản trị (đủ, mang theo từ r2; tra web 08/11/2026)

- **Quản trị/bên liên quan (WARNING nặng).** Hệ Đại Quang Minh–TLSH phơi nhiễm ở 3 lớp:
  - Cổ phần TLSH 9.915 tỷ theo sổ sách. Theo NQ HĐQT 30/09/2026, HPG mua 799,5 triệu cp TLSH giá 7.995 tỷ, nắm 25,13% VĐL [báo: thuonghieucongluan, vnbusiness; ngày đăng chưa xác định].
  - 26,55% CTCP Phát triển BĐS Hòa Phát.
  - Liên danh đô thị sông Hồng.
  - Lãi thoái vốn BĐS 4.929 tỷ (ĐT Mỹ Hào, KĐT Xanh): **bên mua vẫn không thấy công bố**.
- **Ưu đãi thuế:** thời hạn không công bố. Cơ quan thuế chưa có kết luận DQ2 là dự án mới hay mở rộng (CV 377/TCT-CS, luatvietnam chỉ có bản tóm tắt). Có rủi ro truy thu nếu DQ2 bị xếp "mở rộng". Mốc 2035 là ước lượng.
- **AD/PVTM:**
  - QĐ 1959/QĐ-BCT (AD gốc, 04/07/2025): đang rà soát hành chính theo QĐ 1902 (27/07/2026), **chưa có kết quả**.
  - QĐ 1917/QĐ-BCT (chống lẩn tránh 27,83%, hiệu lực 28/07/2026): **chỉ có nguồn báo chí** (SMM 30/07/2026). Bản gốc trên moit/trav chưa mở được. Khổ 1.880–2.300 mm mới chỉ xác nhận cho QĐ tạm thời 612.
- Tiền gửi cầm cố 8.294 tỷ.
- Giao dịch nội bộ: Trần Vũ Minh mua 33,3 triệu cp và đăng ký thêm 50 triệu cp (07/10–05/11). TV độc lập Đặng Ngọc Khánh đăng ký bán 100 nghìn cp (04/11–03/12).
- Lịch sử: QĐ 244/QĐ-XPHC (11/05/2022) phạt 125 triệu vì thiếu TV HĐQT độc lập.
- **Không thấy** xử phạt/truy thu/khởi tố/kết luận thanh tra nào trong 31/10–08/11/2026 (tra web 08/11; không tìm thấy ≠ sạch).

## 7. Giả định khoá (`assumptions`, mỗi dòng có cơ sở; chi tiết ở SUMMARY.json)

| Giả định | Cơ sở / nguồn |
|---|---|
| r 13,50% | 13,5% + 1,0 × (7,40% − 7,40%); `deposit_rate_vn` (cctg_12m 02/11) |
| Giá 21.200 | BQ `tav2_bq.ticker` 06/11 (`calc_r3/px_hpg_r3.sql`) |
| BV0 148.795,5 tỷ; 8.442,96 triệu cp | HN-Q3/2026 |
| Đường LN 3 kịch bản (0,25/0,50/0,25), payout 20% | v3 31/10, giữ nguyên |
| XDCB 16.113 tỷ = r; cam kết 19.472 tỷ = r | HN-Q3 + luật 20 (NPV0) |
| Vốn giữ lại còn lại = 5,92% | lãi huy động 12T × (1 − 20%) |
| Thuế 20% (phần thép) từ 2035 | khung luật ưu đãi KKT + ước lượng DQ1 (GAPS §2); **ước lượng mốc** |
| g_RI = 0 | moat NARROW không bền (5F) |
| TLSH theo sổ sách | không có dữ liệu suy giảm |
| [UL] hệ số LN 0,8–1,2; dg ±1pp; dốc LN ±5%/năm (đều) | giữ nguyên r2 |

## 8. Thanh khoản

| | ADV (trung vị) | σ ngày | CK 5 tỷ | CK 10 tr | CK 40 tr | 5 tỷ / ADV |
|---|---|---|---|---|---|---|
| 250 phiên (05/11/25–06/11/26) | 589,3 tỷ | 1,63% | 0,150% | 0,0067% | 0,0134% | 0,85% |
| 60 phiên (12/08–06/11/26) | 379,8 tỷ | 1,54% | 0,177% | 0,0079% | 0,0158% | 1,32% |

- Cỡ 5 tỷ nằm trong vùng hiệu chỉnh của luật căn bậc hai.
- Cỡ sleeve thật 10–40 triệu (NAV SpaceX ≈ 0,94 tỷ) bằng 0,002–0,007% ADV, **dưới vùng hiệu chỉnh**: CK thật xấp xỉ nửa spread, chưa đo.
- Nhãn không đổi ở cả hai cỡ.

## 9. Mốc đổi nhận định (hai chiều) và HARD ABANDON

**Lên giá trị** (cần dữ liệu, không phải nhận định):
- Kết luận chính thức của cơ quan thuế xếp DQ2 là dự án mới (ưu đãi kéo dài): đẩy mốc thuế, hướng tới bản C (+781).
- LNST lõi 2027 ≥ 28 nghìn tỷ (trên nhánh TRUNG LẬP).
- QĐ 1902 giữ mức AD ≥ 20%.

**Xuống giá trị:**
- DQ2 bị xếp "mở rộng" và có quyết định truy thu.
- QĐ 1902 hạ hoặc gỡ AD.
- LNST lõi 2 quý liền dưới nhánh XẤU (~4 nghìn tỷ/quý).
- Phát sinh nghĩa vụ góp vốn/bảo lãnh cho TLSH hoặc liên danh sông Hồng (khi đó trục TLSH phải quay lại base).

**HARD ABANDON:** khởi tố/kết luận thanh tra liên quan giao dịch TLSH/Đại Quang Minh, hoặc phát hiện HPG bảo lãnh nợ cho các bên này.

## 10. Vấn đề mở

1. Không tái lập được 19.529 của skeptic (biến thể capex); cách đọc của Taylor cho 20.599. Cần skeptic nêu rõ cách phân bổ capex.
2. Nhánh TỐT có thể đếm trùng lợi ích capex: phần XDCB/DQ2 còn lại vừa biện minh đường LN nhánh TỐT, vừa sinh lợi = r trong vốn giữ lại (bản J: −665, tâm 20.673; khoảng tâm 20.673–21.338, headline giữ 21.338).
3. Mốc hết ưu đãi 2035 là ước lượng.
4. Bản gốc QĐ 1917 và kết quả QĐ 1902 chưa có.
5. Bên mua 2 công ty BĐS chưa xác định.
6. EBITDA slide lệch 361 tỷ chưa giải thích (mang từ r2).

## Tệp

- `calc_r3/hpg_r3.py`: mô hình r3, gồm control r2, bridge, 11 biến thể.
- `calc_r3/hpg_r3_out.txt` / `hpg_r3_out.json` / `grid_hpg_r3.csv`.
- `calc_r3/summary_r3_extra.json`: giả định, kết quả kiểm đính chính, WARNING.
- `calc_r3/px_hpg_r3.sql` + `px_hpg_r3_20261106.csv`.
- `calc_r3/LOCK_md5.txt`: md5 outputs và 16 file upstream.
- `SUMMARY.json` (r3); bản r2 backup ở `SUMMARY_r2.json`.
