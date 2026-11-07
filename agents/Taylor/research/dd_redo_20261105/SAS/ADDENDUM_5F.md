# ADDENDUM 5F — SAS (SASCO) · 07/11/2026 · r2 · job `Taylor_20261107_125216`

> Bổ sung bước 3c cho `REPORT_r2.md` (05/11). **Không làm lại DD**; mọi phần khác của REPORT_r2 giữ nguyên. Không sửa REPORT/SUMMARY cũ, không ghi `dd_price_zones`.
> **r2 (sau skeptic)** sửa 6 điểm: mục tiêu biên phải là biên VẬN HÀNH (trừ f) · GPM dùng thẳng dòng Q4 của GPM_P0 · ĐK (i) → INCONCLUSIVE · bỏ câu "không sát ranh giới" · khôi phục caveat Long Thành/[UL] · dòng moat_tags. Bản r1: `ADDENDUM_5F_r1.md`, `SUMMARY_5F_r1.json`, `calc/sas_5f_r1*.py/txt/json`.
> Tái lập (chạy 2 lần, trùng byte): `$DNA_PYEXE -I -B calc/sas_5f.py` → `calc/sas_5f_out.txt` md5 `ad718094…`, `calc/sas_5f_out.json` md5 `e8de5f71…`. Chân đối chứng WIDE tái lập đúng hằng số và lưới của `model_r2.py` ⇒ tâm **31.066** khớp REPORT_r2 (lệch 0 đ).
> Số liệu: `bq query tav2_bq.ticker_financial` 07/11/2026, **có 2026Q3**. `GPM_P0`/`NPM_P0` là số **TTM** (4 quý trượt) ⇒ dòng Q4 = biên cả năm, dùng thẳng, **không** lấy trung bình lại. `Revenue_P0`/`NP_P0` là số QUÝ ⇒ NPM chu kỳ = ΣNP/ΣDT theo năm.
> Non-point-in-time (kiến thức LLM + tag 06/2026) ⇒ CHỈ dùng cho DD sống, cấm đưa vào backtest.

## 1. Vị thế & lợi thế cạnh tranh (5F) — **TÁI DÙNG**
**Nguồn:** `data/moat_tags.csv:38` (SAS, `asof 2026-06-05`, src `5f_validated_compet`) ⇒ 5 tháng < 12 ⇒ tái dùng tier/type/risk1 (luật tần suất 06/11). Kiểm nhanh dựa trên REPORT_r2, `dd_SAS_20261026` và BQ.

| | Nội dung (tái dùng) |
|---|---|
| Loại hình DN | Kinh doanh nhượng quyền mặt bằng sân bay (bán lẻ miễn thuế, F&B, phòng chờ) tại TSN; ít tài sản, khách bị "giữ chân" trong sân bay; ACV 49,07% vừa là chủ nhà vừa là cổ đông |
| **moat_tier** | **NARROW** |
| **moat_type** | LOCATION/REGULATORY (mặt bằng TSN do ACV giao, không qua đấu thầu) |
| **Rủi ro số 1** | Long Thành: theo lộ trình Cục HK, chuyến quốc tế chuyển 28/3/2027–25/3/2028; đề xuất trước đó của ACV sớm hơn (từ mùa đông 2026). **Chưa xác minh được bản nào là quyết định chính thức** (`dd_SAS_20261026/REPORT.md:71–74`) — cả hai đều rơi vào 2027–28. Mặt bằng Long Thành gần như chắc phải đấu thầu |

| Lực | Bằng chứng định lượng · nguồn |
|---|---|
| Cạnh tranh nội ngành | Đối thủ trực tiếp nội địa **AST** (Taseco, cùng mô hình): GPM TTM 26Q3 (BQ `GPM_P0`) **AST 64,2% vs SAS 68,2%** (chênh ~4pp); GPM 9T/2026 của SAS theo BCTC **66,7%** (1.556,1/2.333,1). ROIC5Y AST 18,3% vs SAS 15,3% [BQ, xem cờ artifact §2]. Thị phần tại TSN *cần kiểm chứng* |
| Đối thủ mới | Rào cản = quyền giao mặt bằng của ACV. Gói thầu Long Thành mở cửa cho người mới; kết quả thầu *cần kiểm chứng* (REPORT_r2 §8) |
| Quyền lực người mua | Khách bị giữ chân; **~57% DT Q3 gắn với khách quốc tế [UL]** (ước lượng, REPORT_r2 §1) ⇒ phần doanh thu này lộ hẳn ra trước Long Thành |
| Quyền lực nhà cung cấp | Chủ nhà ACV (49,07%): truy thu tiền thuê đất 2015–2024 "hàng chục tỷ" hạch toán Q4/2025 [vietstock, REPORT_r2 §6]. Nhà cung cấp hàng miễn thuế *cần kiểm chứng* |
| Sản phẩm thay thế | Miễn thuế trong nội thành / bán trực tuyến: *cần kiểm chứng* (chưa có số) |
| **Lực thứ 6** | (a) **Đồng hồ Long Thành** = cơ chế cắt hào có khung thời gian 2027–28; (b) KL TTCP 2017: mặt bằng giao không qua đấu thầu ⇒ quyền này có thể bị đảo khi chính sách đổi; (c) Chủ tịch nói tự vận hành miễn thuế "không thể kéo dài" (REPORT_r2 §6) |

**Kiểm nhanh từ 05/06:** tier giữ nguyên. Rủi ro số 1 đã có lộ trình 2027–28 (dù bản chính thức chưa xác minh) ⇒ đồng hồ cắt hào rõ hơn. Có TGĐ mới từ 08/2026.

## 2. Ba điều kiện để moat được coi là BỀN — bằng chứng cả hai phía
| ĐK | Kết quả | Bằng chứng (BQ, Ke 13,5%) |
|---|---|---|
| (i) Lợi nhuận siêu ngạch qua nhiều chu kỳ | **INCONCLUSIVE** (dữ liệu ROIC vendor không đáng tin) | Số vendor hai phía: ROIC3Y 23,5%, ROIC5Y 15,3%, ROIC10Y 13,1%, ROIC_Min3Y 11,2%, ROIC_Min5Y = Min10Y −2,5% (26Q3); ROIC5Y Q4 2016–19 5,0→10,9%. **Cờ artifact** (BQ đã kiểm lại 07/11): 2016Q1 ROIC5Y **−1,97%**, ROE5Y **−8,6%** trong khi NPM các quý 2016–17 dương 11–17%; ROIC_Trailing **100,7%** (2019Q4) và **223%** (2026Q3) — không thể đồng thời đúng với ROIC5Y 10–15%. Tag 06/2026 cũng ghi Min5Y là "COVID-SCARRED". ⇒ không dùng phía thấp ROIC vendor để kết luận TRƯỢT. ROE (ghi riêng): ROE5Y 20,5%, ROE_Min3Y 19,2%; **ROE vận hành (trừ tiền + TS) 71,2%** (REPORT_r2 §3) ⇒ nghiêng về có siêu ngạch, nhưng trên mặt bằng do ACV giao, chưa qua chu kỳ cạnh tranh mở |
| (ii) Có cơ chế rào cản gọi tên được | ĐẠT | quyền mặt bằng ACV tại TSN (vị trí + giấy phép) |
| (iii) Không có đồng hồ cắt hào | **TRƯỢT** | Long Thành 2027–28 (cả hai bản lộ trình) + khả năng phải đấu thầu |

⇒ **moat_durable = false**, đứng nhờ **(iii)** và tag NARROW (SKILL bước 3c: có đồng hồ cắt hào ⇒ không thưởng), **không** nhờ (i). Theo luật 3c: RONIC = Ke và biên về **TB chu kỳ ngành**.

## 3. Moat trong mô hình — mô hình hiện hành đang **ngầm thưởng kiểu WIDE** ⇒ không nhất quán
`model_r2.py` dùng TV = E₂₀₂₈/(r−g), g {2;3;4}%, **không trích tái đầu tư** ⇒ RONIC ngầm = ∞ > Ke ở mọi ô g. Mô hình giữ N0 = **518,4 tỷ/năm mãi mãi** (chỉ trừ Δ Long Thành). N0 = (LN 9T 539,5 − (DT TC 195,0 − CP TC 6,7)×0,8)×4/3 ⇒ đã **LOẠI thu nhập tài chính** (tiền/đầu tư cộng riêng theo sổ) ⇒ **biên vận hành N0 = 16,67%** (NPM 9T gồm TC là 23,12%; chênh 6,46pp = thu nhập TC sau thuế). **BẢN CHẶT-3C** chạy song song:
- **RONIC = Ke, ĐỐI XỨNG mọi ô g**: V = E(1−g/Ke)/(r−g) = E/r. Quy ước năm 1 giữ nguyên r2 (E₂₀₂₇/(1+r), TV tại t=1 chiết khấu thêm (1+r)). (cơ sở: moat NARROW LOCATION/REGULATORY, (iii) trượt)
- **Biên về TB chu kỳ ngành — so cùng cơ sở VẬN HÀNH**: NPM chu kỳ gộp SAS+AST, có trọng số DT, 2017–19 + 2022–25 (bỏ 2020–21 COVID) = **14,36%** (SAS 14,52% · AST 13,96%) — số này **GỒM thu nhập TC lịch sử** ⇒ mục tiêu vận hành = **14,36% − f**. Điều chỉnh LN = 3.111 × ((14,36% − f) − 16,67%); nửa vào 2027, đủ từ 2028.
- **f (thu nhập TC sau thuế / DT, pp)**: không có chuỗi DT TC từng năm 2017–19, 2022–25 trong BQ (không có cột) hay thư mục (chỉ có BCTC H1 và Q3/2026) ⇒ *cần kiểm chứng* từng năm từ BCTC. Mốc đo được: **9T/25 = 0,8×58,2/2.339 = 1,99pp** (cận trên, chưa trừ CP TC); cả năm 2025 = 0,8×(58,2+139,8)/3.316 = 4,78pp (Q4/25 139,8 [web] có thể gồm khoản một lần); 9T/26 = 6,46pp (đỉnh, cổ tức đầu tư dồn). **Headline f = 2pp** (mốc 9T/25, kỳ không đỉnh gần nhất), **khoảng 1–3pp**; 4,78pp báo như đuôi.
- **Peer**: chỉ AST cùng mô hình ⇒ dùng làm mẫu. NCT, SCS (ga hàng hoá), SGN (mặt đất), MAS (suất ăn) khác mô hình ⇒ loại khỏi mục tiêu, chỉ báo độ nhạy (GPM_P0 26Q3 trung vị 47,3% / TB 47,5%).
- **Kênh truyền dẫn GPM** (không phụ thuộc f vì cùng là số vận hành): GPM ngành SAS+AST 2017–25 (dòng Q4 GPM_P0, trọng số DT) = 54,0% vs 9T/26 66,7%. (a) SG&A cố định ⇒ −60,9% N0 (**cận trên mức cắt**, thổi phồng vì SG&A/DT tăng cùng GPM); (c) SG&A co giãn ⇒ −19,0% N0 (**cận dưới**). Headline kênh NPM (f=2) = −133,9 tỷ/năm (**−25,8% N0**), nằm trong khoảng (a)–(c).
- **Không đếm hai lần**: base không có khoản trừ pháp lý (chỉ WARNING); ép biên neo vào AST + NPM chu kỳ, không neo vào vụ việc. Δ Long Thành (sản lượng) và biên có thể chồng nhau ⇒ báo thêm bản Δ=0 làm cận trên.

## 4. Kết quả & độ nhạy (sau CK thanh khoản 5 tỷ 6,01%; r 13,5%; 135 kết cục; giá 34.700)
| Phương án | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn 5 tỷ | Sleeve 40 tr (CK 0,54%): tâm · P90 · nhãn |
|---|---|---|---|---|---|---|---|
| **WIDE** (= REPORT_r2) | 31.066 | 23.751 | 30.806 | 38.022 | 73,6% | TRONG | 32.875 · 40.235 · TRONG |
| Chỉ RONIC=Ke (giữ biên) | 26.410 | 20.776 | 26.361 | 31.892 | 96,9% | TRÊN | 27.947 · **33.749** · TRÊN — **ranh giới** (cách giá 2,8%) |
| Chỉ biên (f=2, giữ RONIC ∞) | 25.456 | 20.107 | 25.309 | 31.127 | 97,8% | TRÊN | 26.938 · 32.940 · TRÊN (cách 5,3%) |
| **HEADLINE chặt-3C (RONIC=Ke + NPM ngành − f 2pp)** *(quy ước chờ Mike/user duyệt)* | **22.002** | **17.949** | **21.965** | **25.977** | 100% | **TRÊN** | 23.283 · 27.489 · TRÊN |
| — f = 1pp | 23.026 | 18.695 | 22.986 | 27.446 | 100% | TRÊN | 24.367 · 29.044 · TRÊN |
| — f = 3pp | 20.978 | 17.124 | 20.944 | 24.944 | 100% | TRÊN | 22.199 · 26.396 · TRÊN |
| — f = 0 (coi NPM chu kỳ là thuần vận hành) | 24.050 | 19.325 | 24.008 | 28.916 | 100% | TRÊN | 25.451 · 30.599 · TRÊN |
| — f = 4,78pp (cả năm 2025, đuôi) | 19.154 | 15.661 | 19.126 | 22.540 | 100% | TRÊN | 20.269 · 23.852 · TRÊN |
| — mục tiêu NPM riêng SAS / riêng AST (f=2) | 22.169 / 21.595 | 18.084 / 17.621 | 22.131 / 21.559 | 26.216 / 25.709 | 100% | TRÊN | — |
| — kênh (c) cận dưới mức cắt GPM | 23.162 | 18.779 | 23.122 | 27.642 | 100% | TRÊN | 24.511 · 29.251 · TRÊN |
| — kênh (a) cận trên mức cắt GPM | 16.012 | 13.385 | 15.993 | 18.756 | 100% | TRÊN | 16.944 · 19.848 · TRÊN |
| — GPM bằng AST 26Q3 64,2% (kênh a) | 24.331 | 19.498 | 24.288 | 29.319 | 100% | TRÊN | 25.748 · 31.025 · TRÊN |
| — headline với Δ Long Thành = 0 (cận trên do chồng lấn) | 26.224 | 23.788 | 26.176 | 28.563 | 100% | TRÊN | — · 30.226 · TRÊN |
| — peer rộng (GPM trung vị / TB, kênh a) | 10.549 / 10.711 | 8.718 / 8.868 | — | 12.542 / 12.712 | 100% | TRÊN | — |
| **NONE** (chặt-3C f=2, biên về ngành ngay từ 2027) | 21.681 | 17.656 | 21.644 | 25.604 | 100% | TRÊN | 22.943 · 27.095 · TRÊN |

**Tách WIDE → headline (−9.065 đ)**: riêng RONIC = −4.657 đ; riêng biên (f=2) = −5.611 đ; có tương tác nên không cộng thẳng. Theo f: biên riêng −3.003 (f=0) / −4.307 (f=1) / −5.611 (f=2) / −6.914 (f=3) đ.
**Ranh giới**: headline P90 25.977 cách giá 33,6% (sleeve 27.489, cách 26,2%) ⇒ **không sát ranh giới** ở mọi f 0–4,78pp. Các nhánh **một kênh** thì sát hơn: chỉ-RONIC cỡ sleeve 40 tr P90 33.749 (cách 2,8%) = **ranh giới**; chỉ-biên với f=0 ở cỡ sleeve còn **TRONG** (P90 36.346), f=1 sleeve P90 34.624 (ranh giới). Kết luận TRÊN vùng chỉ chắc khi áp **cả hai** kênh như luật 3c.

## 5. Thay đổi so với báo cáo hiện hành
**Có đổi giá trị và đổi nhãn nếu duyệt quy ước chặt-3C.** Tâm 31.066 → **22.002 (−29,2%)**, khoảng **20.978–23.026** theo f 3–1pp; P10 23.751 → 17.949; P50 30.806 → 21.965; P90 38.022 → 25.977. Nhãn **TRONG → TRÊN vùng** (cả 5 tỷ và sleeve 40 tr), giá cao hơn tâm 58%. r1 (17.438, −44%) **sai** vì so biên vận hành của N0 với NPM 9T gồm thu nhập TC ⇒ ép biên vận hành xuống 7,9% < chu kỳ. Đây là **quy ước chờ Mike/user duyệt**, chưa ghi SUMMARY/zones. Điểm yếu: (1) f chưa đo từng năm từ BCTC; (2) nếu biên đỉnh 2025–26 là **cấu trúc** (cơ cấu hàng miễn thuế, phòng chờ) thì kênh biên phạt quá tay ⇒ đọc bản "chỉ RONIC" (26.410; sleeve ranh giới). Cần thuyết minh GVHB/SG&A + DT TC từng năm.

## 6. Đề xuất `data/moat_tags.csv`
Tag 05/06 còn hiệu lực (<12 tháng), tier không đổi ⇒ **không bắt buộc thêm dòng mới**. Nếu muốn ghi lại lần kiểm này (human-curated; `entry`=M = mức hấp dẫn cấu trúc NGÀNH: khách bị giữ chân nhưng chủ nhà ACV quyền lực, ngành bị điều tiết; `moat_upgrade` giữ Y như dòng cũ, không có chủ ý đổi):
`SAS,NARROW,LOCATION/REGULATORY,M,"TSN concession (ACV-granted, no tender; ACV 49.07% landlord+shareholder). NOT durable via moat clock: intl flights move to Long Thanh 2027-28 (official schedule unverified, both versions 2027-28), LT space likely tendered. Excess return INCONCLUSIVE: vendor ROIC unreliable (ROIC5Y -2%/ROE5Y -9% in 2016Q1 at 11-17% NPM; ROIC_Trailing 101-223%); operating ROE ~71%. Operating NPM 9M/26 16.7% vs cycle 11.4-13.4% ex-fin-income (14.36% incl. fin minus f 1-3pp; SAS+AST)",2026-11-07,5f_recheck_dd,Y`

## 7. Cần kiểm chứng
DT/CP tài chính từng năm 2017–19, 2022–25 (để đo f thay vì proxy) · quyết định chính thức lộ trình Long Thành · thị phần TSN và kết quả thầu Long Thành · ROIC đúng (vốn đầu tư không gồm tiền) · phân loại phí mặt bằng giữa GVHB và SG&A · NP 2025 có khoản một lần Q4/2025 (bù DFS, truy thu tiền thuê đất) làm lệch NPM chu kỳ không.
