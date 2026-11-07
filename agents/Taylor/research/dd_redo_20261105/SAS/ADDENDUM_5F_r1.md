# ADDENDUM 5F — SAS (SASCO) · 07/11/2026 · job `Taylor_20261107_123136`

> Bổ sung bước 3c cho `REPORT_r2.md` (05/11). **Không làm lại DD**; mọi phần khác của REPORT_r2 giữ nguyên. Không sửa REPORT/SUMMARY cũ, không ghi `dd_price_zones`.
> Tái lập (chạy 2 lần, md5 trùng): `$DNA_PYEXE -I -B calc/sas_5f.py` → `calc/sas_5f_out.txt` md5 `17298bd9…`, `calc/sas_5f_out.json`. Chân đối chứng WIDE tái lập đúng hằng số và lưới của `model_r2.py` ⇒ tâm **31.066** khớp REPORT_r2 (lệch 0 đ).
> Số ROIC/ROE/GPM/NPM: `bq query tav2_bq.ticker_financial` 07/11/2026, **có 2026Q3**. GPM/NPM = **TTM có trọng số doanh thu** Σ(X_Pi·Rev_Pi)/ΣRev_Pi (i=0..3) lấy tại Q4 mỗi năm; 9T/2026 = Q1–Q3 có trọng số. `GPM_P0` chỉ là MỘT quý, không dùng làm số năm.
> Non-point-in-time (kiến thức LLM + tag 06/2026) ⇒ CHỈ dùng cho DD sống, cấm đưa vào backtest.

## 1. Vị thế & lợi thế cạnh tranh (5F) — **TÁI DÙNG**
**Nguồn:** `data/moat_tags.csv` dòng SAS, `asof 2026-06-05`, src `5f_validated_compet` ⇒ 5 tháng < 12 ⇒ tái dùng tier/type/risk1 (luật tần suất 06/11). Kiểm nhanh dựa trên REPORT_r2, `dd_SAS_20261026` và BQ.

| | Nội dung (tái dùng) |
|---|---|
| Loại hình DN | Kinh doanh nhượng quyền mặt bằng sân bay (bán lẻ miễn thuế, F&B, phòng chờ) tại TSN; ít tài sản, khách bị "giữ chân" trong sân bay; ACV 49,07% vừa là chủ nhà vừa là cổ đông |
| **moat_tier** | **NARROW** |
| **moat_type** | LOCATION/REGULATORY (mặt bằng TSN do ACV giao, không qua đấu thầu) |
| **Rủi ro số 1** | Long Thành: chuyến quốc tế chuyển sang 28/3/2027–25/3/2028 (lộ trình Cục HK, REPORT_r2 §2); mặt bằng Long Thành gần như chắc phải đấu thầu |

| Lực | Bằng chứng định lượng · nguồn |
|---|---|
| Cạnh tranh nội ngành | Đối thủ trực tiếp nội địa **AST** (Taseco, cùng mô hình): GPM TTM 26Q3 **64,0%** vs SAS **65,5%**; ROIC5Y AST 18,3% vs SAS 15,3% [BQ]. Thị phần tại TSN *cần kiểm chứng* |
| Đối thủ mới | Rào cản = quyền giao mặt bằng của ACV. Gói thầu Long Thành mở cửa cho người mới; kết quả thầu *cần kiểm chứng* (REPORT_r2 §8) |
| Quyền lực người mua | Khách bị giữ chân; **~57% DT Q3 gắn với khách quốc tế** (REPORT_r2 §1) ⇒ phần doanh thu này lộ hẳn ra trước Long Thành |
| Quyền lực nhà cung cấp | Chủ nhà ACV (49,07%): truy thu tiền thuê đất 2015–2024 "hàng chục tỷ" hạch toán Q4/2025 [vietstock, REPORT_r2 §6]. Nhà cung cấp hàng miễn thuế *cần kiểm chứng* |
| Sản phẩm thay thế | Miễn thuế trong nội thành / bán trực tuyến: *cần kiểm chứng* (chưa có số) |
| **Lực thứ 6** | (a) **Đồng hồ Long Thành** = cơ chế cắt hào có ngày cụ thể; (b) KL TTCP 2017: mặt bằng giao không qua đấu thầu ⇒ quyền này có thể bị đảo khi chính sách đổi; (c) Chủ tịch nói tự vận hành miễn thuế "không thể kéo dài" (REPORT_r2 §6) |

**Kiểm nhanh từ 05/06:** tier giữ nguyên. Rủi ro số 1 đã có **lộ trình ngày cụ thể** (03/2027–03/2028) ⇒ đồng hồ cắt hào nay đã rõ ràng. ROIC_Min3Y 11,2% (tag ghi "9→11% đang tăng") vẫn **< Ke 13,5%**. Có TGĐ mới từ 08/2026.

## 2. Ba điều kiện để moat được coi là BỀN — bằng chứng cả hai phía
| ĐK | Kết quả | Bằng chứng (BQ 2026Q3 và Q4 các năm, Ke 13,5%) |
|---|---|---|
| (i) Lợi nhuận siêu ngạch qua nhiều chu kỳ | **TRƯỢT trên ROIC** | Phía thuận: ROIC3Y **23,5%**, ROIC5Y 15,3% (> Ke). Phía ngược: **ROIC5Y trước COVID đã < Ke** (2016Q4 5,0% · 2017 7,5% · 2018 9,6% · 2019 10,9%); ROIC10Y **13,1% ≈ Ke**; ROIC_Min3Y 11,2%; ROIC_Min5Y = ROIC_Min10Y **−2,5%**. **ROE** (ghi riêng, không dùng thay ROIC): ROE5Y 20,5%, ROE_Min3Y 19,2%, ROE_Min5Y 2,0%; ROE vận hành (sau khi trừ tiền và tài sản) 71,2% (REPORT_r2 §3). Có thể ROIC trên BQ bị pha loãng bởi lượng tiền lớn — *cần kiểm chứng* |
| (ii) Có cơ chế rào cản gọi tên được | ĐẠT | quyền mặt bằng ACV tại TSN (vị trí + giấy phép) |
| (iii) Không có đồng hồ cắt hào | **TRƯỢT** | Long Thành 2027–28 cộng với khả năng phải đấu thầu |
⇒ **moat_durable = false** ⇒ theo luật 3c: RONIC = Ke và biên về **trung bình chu kỳ ngành**.

## 3. Moat trong mô hình — mô hình hiện hành đang **ngầm thưởng kiểu WIDE** ⇒ không nhất quán
`model_r2.py` dùng TV = E₂₀₂₈/(r−g) với g {2;3;4}% mà **không trích tái đầu tư** ⇒ RONIC ngầm = ∞ > Ke ở **mọi** ô của trục g. Đồng thời mô hình giữ N0 = LN vận hành năm hoá 9T/2026 **mãi mãi** (chỉ trừ Δ Long Thành). Mức N0 này ứng với biên đỉnh của chính SAS: GPM 9T **66,6%**, NPM 9T **23,1%**, so với NPM chu kỳ của SAS 14,5% và của AST 14,0%. Cả hai kênh (RONIC và biên) đều đang thưởng moat ngầm ⇒ dựng **BẢN CHẶT-3C** chạy song song:
- **RONIC = Ke, áp ĐỐI XỨNG cho mọi ô g**: V = E(1−g/Ke)/(r−g) = E/r. Quy ước năm 1 giữ nguyên r2 (E₂₀₂₇/(1+r), TV tính tại t=1 rồi chiết khấu thêm (1+r)).
  (cơ sở: moat NARROW LOCATION/REGULATORY, (i) và (iii) đều trượt)
- **Biên về TB chu kỳ ngành** = NPM TTM gộp SAS+AST, có trọng số DT, các năm 2017–19 và 2022–25 (bỏ 2020–21 vì sân bay đóng cửa do COVID) = **14,36%** (SAS 14,52% · AST 13,96%). Điều chỉnh LN = DT năm hoá 3.111 × (14,36% − 23,12%) = **−272,5 tỷ/năm (−52,6% N0)**. Thu nhập tài chính giữ ở mức hiện tại vì tiền đã được cộng theo sổ. Nửa điều chỉnh vào 2027, đủ từ 2028.
- **Peer**: chỉ AST cùng mô hình nên dùng làm mẫu so; NCT (ga hàng hoá), SCS (ga hàng hoá), SGN (phục vụ mặt đất), MAS (suất ăn) khác mô hình ⇒ loại khỏi mục tiêu, chỉ báo như độ nhạy (GPM trung vị 46,8% / TB 47,1%).
- **Kênh truyền dẫn biên** (bảng §4): (a) GPM về mức ngành 52,9% với SG&A cố định ⇒ −65,8% N0, đây là **cận trên mức cắt**, đã thổi phồng vì tỷ lệ SG&A/DT tăng cùng GPM (có thể do cách phân loại phí mặt bằng); (b) NPM [**HEADLINE**] −52,6%; (c) GPM về mức ngành với SG&A co giãn theo tỷ lệ ⇒ −20,6%, đây là **cận dưới mức cắt**.
- **Không đếm hai lần**: base không có khoản trừ pháp lý nào (chỉ WARNING); việc ép biên neo vào ĐK (i) và số liệu AST, không neo vào vụ việc pháp lý. Δ Long Thành (sản lượng) và biên (sức định giá) có thể chồng nhau một phần ⇒ báo thêm bản headline với Δ=0 làm cận trên.

## 4. Kết quả & độ nhạy (sau CK thanh khoản 5 tỷ 6,01%; r 13,5%; 135 kết cục; giá 34.700)
| Phương án | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn 5 tỷ | Tâm / nhãn sleeve 40 tr (CK 0,54%) |
|---|---|---|---|---|---|---|---|
| **WIDE** (= REPORT_r2) | 31.066 | 23.751 | 30.806 | 38.022 | 73,6% | TRONG | 32.875 · TRONG |
| Chỉ RONIC=Ke (giữ biên) | 26.410 | 20.776 | 26.361 | 31.892 | 96,9% | **TRÊN** | 27.947 · TRÊN |
| Chỉ biên NPM ngành (giữ RONIC ∞) | 19.647 | 15.992 | 19.488 | 23.662 | 100% | TRÊN | 20.790 · TRÊN |
| **HEADLINE NARROW chặt-3C (RONIC=Ke + NPM ngành)** *(quy ước chờ Mike/user duyệt)* | **17.438** | **14.438** | **17.414** | **20.490** | 100% | **TRÊN** | 18.453 · TRÊN |
| — mục tiêu NPM của riêng SAS / riêng AST | 17.604 / 17.031 | 14.557 / 14.149 | — | 20.689 / 20.003 | 100% | TRÊN | — |
| — kênh (c) cận dưới mức cắt (SG&A co giãn) | 22.898 | 18.617 | 22.859 | 27.263 | 100% | TRÊN | 24.231 · TRÊN |
| — kênh (a) cận trên mức cắt (SG&A cố định) | 15.182 | 12.732 | 15.165 | 17.634 | 100% | TRÊN | 16.066 · TRÊN |
| — biên bằng AST hiện tại 64,0% (kênh a) | 24.283 | 19.468 | 24.239 | 29.249 | 100% | TRÊN | 25.696 · TRÊN |
| — headline với Δ Long Thành = 0 (cận trên do chồng lấn) | 20.202 | 17.783 | 20.171 | 22.559 | 100% | TRÊN | — |
| — peer rộng (GPM trung vị / TB, kênh a) | 10.180 / 10.395 | 8.347 / 8.563 | — | 12.154 / 12.380 | 100% | TRÊN | — |
| **NONE** (chặt-3C, biên về ngành ngay từ 2027) | 16.785 | 13.875 | 16.761 | 19.766 | 100% | TRÊN | 17.762 · TRÊN |

Tách phần chênh WIDE → headline (−13.628 đ): riêng RONIC = −4.656 đ; riêng biên = −11.419 đ; hai kênh có phần tương tác nên tổng không bằng tổng hai phần. **Nhãn không nằm sát ranh giới**: mọi phương án chặt (kể cả cận dưới mức cắt, Δ=0, và chỉ RONIC) đều có P90 < giá 34.700, ở cả cỡ 5 tỷ lẫn cỡ sleeve 40 tr.

## 5. Thay đổi so với báo cáo hiện hành
**Có đổi giá trị và đổi nhãn nếu duyệt quy ước chặt-3C.** Tâm 31.066 → **17.438 (−43,9%)**; P10 23.751 → 14.438; P50 30.806 → 17.414; P90 38.022 → 20.490. Nhãn **TRONG → TRÊN vùng**, giá cao hơn tâm 99%. Kết quả này chắc ở mọi cách truyền dẫn biên và mọi lựa chọn peer. Riêng phần RONIC=Ke (không động vào biên) đã đủ đổi nhãn: P90 31.892 < 34.700. Đây là **quy ước chờ Mike/user duyệt**, chưa ghi SUMMARY/zones. Điểm yếu của headline: nếu biên đỉnh 2025–26 là **cấu trúc** (cơ cấu hàng miễn thuế, thêm phòng chờ) chứ không phải chu kỳ, thì kênh biên phạt quá tay. Khi đó cần đọc bản "chỉ RONIC" (26.410, vẫn TRÊN). Cần thuyết minh GVHB/SG&A để tách bạch chuyện này.

## 6. Đề xuất `data/moat_tags.csv`
Tag 05/06 còn hiệu lực (<12 tháng), tier không đổi ⇒ **không bắt buộc thêm dòng mới**. Nếu muốn ghi lại lần kiểm này (human-curated; `entry`=M = mức hấp dẫn cấu trúc NGÀNH: khách bị giữ chân nhưng chủ nhà ACV quyền lực và ngành bị điều tiết; `moat_upgrade` giữ Y như dòng cũ, lần này không có chủ ý đổi):
`SAS,NARROW,LOCATION/REGULATORY,M,"TSN concession (ACV-granted, no tender; ACV 49.07% landlord+shareholder). NOT durable: ROIC5Y 2016-19 5.0-10.9% < Ke, ROIC10Y 13.1% ~Ke, ROIC_Min3Y 11.2%, Min5Y -2.5%; ROE5Y 20.5%. #1 risk dated: intl flights move to Long Thanh 2027-03..2028-03, LT space likely tendered; peak NPM 9M/26 23.1% vs cycle 14.4% (SAS+AST)",2026-11-07,5f_recheck_dd,Y`

## 7. Cần kiểm chứng
Thị phần TSN và kết quả thầu Long Thành · ROIC trên BQ có tính tiền vào vốn đầu tư không · cách phân loại phí mặt bằng giữa GVHB và SG&A (để biết biên cao là cấu trúc hay chu kỳ) · NP 2025 có khoản một lần ở Q4/2025 (bù DFS, truy thu tiền thuê đất) làm lệch NPM chu kỳ không.
