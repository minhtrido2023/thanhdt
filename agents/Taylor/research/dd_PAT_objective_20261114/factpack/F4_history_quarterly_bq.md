# F4 — Chuỗi theo quý PAT từ BigQuery + giá hàng hoá sunsirs + quan hệ biên gộp (MÔ TẢ DỮ LIỆU, không định giá)

Ngày truy cập BQ: 2026-11-14. Đơn vị tiền: **tỷ đồng** trừ khi ghi khác; giá hàng hoá: CNY/tấn (P4, than cốc, lưu huỳnh, quặng P), USD/tấn (coking coal TE). Mù giá: chỉ chọn cột cơ bản (danh sách cột ở mục SQL); KHÔNG đọc cột Close/Price/PE/PB/PS/PCF/EVEB/MarketCap dù chúng có trong bảng.
Mã tái lập: `factpack/data/pat_build_quarterly.py`, `pat_analysis.py` (chạy bằng `/home/trido/thanhdt/wc_venv/bin/python`, cần scipy); dữ liệu thô `data/pat_ticker_financial_raw.csv`, `data/pat_commodity_quarterly.csv`; kết quả `data/pat_quarterly_series.csv`, `pat_identified_periods.csv`, `pat_corr_results.csv`, `pat_margin_percentiles.csv`.

## 0. TÓM TẮT (đọc trước)
1. BQ `ticker_financial` của PAT có **19 dòng, 2022Q1→2026Q3** (mỗi dòng = 1 quý; P1..P7 trong dòng khớp P0 của dòng trước, 0 chênh lệch trên toàn bộ 19 dòng). Quý 2021Q1–Q3 chỉ xuất hiện trong cột P4..P7 của dòng đầu và **KHÔNG nhất quán nội bộ** (xem mục 1.3) ⇒ không dùng.
2. **GPM_P0 / EBITM_P0 / NPM_P0 / EBITDA_P0 là số TTM (4 quý trượt), KHÔNG phải số của quý** (dictionary `bigquery_dictionary.json`, ghi chú 2026-11-08). Chỉ Revenue_P*, NP_P*, CF_OA_P*, Inventory_P* và các số dư là số quý/cuối kỳ. Tôi dựng lại GP/EBIT theo **kỳ** bằng sai phân TTM + neo từ BCTC gốc; kiểm chứng: dự báo ngược về Q3/2026 cho 63,603 (BCTC 63,604) và H1/2026 cho 186,994 (BCTC 186,994).
3. **Bậc tự do không giải được:** GP/EBIT của riêng Q1 và riêng Q2 KHÔNG xác định được từ BQ + 4 neo BCTC trong thư mục inputs (chỉ có số luỹ kế H1 và Q3). Xác định được: **H1 (Q1+Q2), Q3, Q4** từng năm 2022–2026 (Q4/2021 cũng được). Mọi phép thử biên dùng các "kỳ định danh" này (N=15).
4. **Quan hệ biên gộp ~ giá P4 KHÔNG xác định được một cách ổn định.** Toàn mẫu có Pearson +0,73…+0,81 nhưng (a) Spearman chỉ +0,35…+0,47 (p 0,08–0,22), (b) cả hai chuỗi cùng có xu hướng giảm theo thời gian (GPM~thời gian r=−0,78; P4~thời gian r=−0,71) nên tương quan mức có thể chỉ là xu hướng chung 2021→2023, (c) phép thử sai phân YoY: r=+0,35 (p=0,26, N=12), (d) **giai đoạn giá hẹp 2024–2026 (N=8) dấu ngược: r=−0,57 (p=0,14)**; riêng 2026, P4 TB +18% YoY (H1) và +22% (Q3) nhưng GPM Q3/2026 = 14,5% (thấp nhất toàn mẫu). Không kết luận nhân quả (N hiệu dụng nhỏ).
5. Biên gộp theo kỳ: cao nhất H1/2022 39,7%; thấp nhất Q3/2026 14,5%. EBIT margin (GP−CPBH−QLDN) cao nhất H1/2022 34,2%, thấp nhất Q3/2024 10,8%. 6 kỳ gần nhất (8 quý 2024Q4–2026Q3): GPM P10/P50/P90 = 16,7%/21,8%/25,1%.
6. Doanh thu có thành phần bên liên quan lớn và biến động mạnh (bán cho công ty mẹ DLC: 9T26 878,14 tỷ = 63,7% DT, so với 9T25 153,98 tỷ = 10,8%) ⇒ giá thực hiện có thể không bằng giá giao ngay sunsirs (xem mục 6).

## 1. Cách xác định quý, nhất quán và đối chiếu chéo
### 1.1 Xác định quý
- Cột `quarter` (vd `2026Q3`) = quý của số liệu P0; `time`/`Release_Date` = ngày công bố (vd 2026Q3 công bố 2026-11-02; thực tế BCTC ký 20/10/2026 theo ảnh png_q326/p07). Cột P_k = quý lùi k kỳ so với `quarter`.
- Kiểm tra trượt: với mọi dòng i và k=1..7, giá trị `Revenue_Pk`, `NP_Pk`, `GPM_Pk`, `Inventory_Pk` của dòng i == giá trị P0 của dòng i−k: **0 chênh lệch** (không có sửa số/restatement trong BQ giữa các lần công bố). Hệ quả: BQ giữ số công bố ban đầu từng quý (chưa kiểm toán) — xem mục 1.4.
- NaN: Revenue_P5..P7 và NP_P5..P7 thiếu ở 3 dòng đầu; GPM_P2..P7 thiếu ở 6 dòng đầu; EBITM_P4/NPM_P4 thiếu 3 dòng đầu; CF_OA_P1..P4 thiếu 4 dòng đầu (nên chuỗi CFO quý lấy từ P0 từng dòng).

### 1.2 Đối chiếu với BCTC gốc (ảnh), tỷ đồng
| Quý/kỳ | Chỉ tiêu | BQ | BCTC (ảnh/trang) | Kết quả |
|---|---|---|---|---|
| Q3/2026 | DT thuần | 440,032 | 440,032 (/home/trido/thanhdt/wt-1571194491489091644/agents/Taylor/research/blind_val_20261114/inputs/src/png_q326/p07.png, trang BCTC 5) | khớp |
| Q3/2026 | LNST | 59,320 | 59,320 (cùng trang) | khớp |
| Q3/2025 | DT thuần / LNST | 506,727 / 109,967 | 506,727 / 109,967 (cùng trang) | khớp |
| Q3/2026 | GP dựng từ TTM (neo Q3/2025=130,471 + ΔTTM) | 63,603 | 63,604 (cùng trang) | khớp 0,001 |
| Q3/2026 | EBIT dựng (GP−CPBH−QLDN) | 53,842 | 63,604−5,049−4,711 = 53,844 | khớp 0,002 |
| H1/2026 | DT = Q1+Q2 | 421,916+517,355 = 939,271 | 939,271 (/home/trido/thanhdt/wt-1571194491489091644/agents/Taylor/research/blind_val_20261114/inputs/src/png_bn26/p09.png, trang 8) | khớp |
| H1/2026, H1/2025 | LNST = Q1+Q2 | 156,393; 162,360 | 156,393; 162,360 (bn26/p09) | khớp |
| H1/2026 | GP dựng (neo H1/2025=216,612 + ΔTTM) | 186,994 | 186,994 (bn26/p09) | khớp |
| 9T/2025 | DT, LNST = Q1+Q2+Q3 | 1.420,835; 272,328 | 1.420,835; 272,328 (q326/p07) | khớp |
| FY2024 | GP_TTM(2024Q4), LNST, EBIT | 363,209; 264,941; 248,836 | 363,209; 264,941; 363,209−98,879−15,495 = 248,835 (/home/trido/thanhdt/wt-1571194491489091644/agents/Taylor/research/blind_val_20261114/inputs/src/png_kt25/p09.png) | khớp (kỳ này BQ = BCTC kiểm toán PwC) |
| 30/06/2026 | HTK; Tổng TS | 74,843; 1.010,601 | 74,843; 1.010,601 (bn26/p07.png, trang 6) | khớp |
| 30/09/2026 | VCSH (=TổngTS−NợNH−NợDH) | 708,446 | 708,45 (facts_extracted.md, trích tay, chưa tự đối chiếu ảnh) | khớp |

### 1.3 Chỗ KHÔNG nhất quán trong BQ
- **2021Q1–Q3**: NP·(NPM TTM) ≠ ΣNP: tại 2021Q4 ΣNP(4 quý) = 256,4 nhưng NPM_TTM×DT_TTM = 530,3; 2022Q1 588,4 vs 772,8; 2022Q2 791,4 vs 826,6. Từ 2022Q3 trở đi hai vế bằng nhau (kiểm 17 quý). ⇒ số DT/LNST Q1–Q3/2021 trong dòng 2022Q1 không đáng tin; TTM chỉ dùng từ **2022Q3**. Q4/2021 (DT 587,5; LNST 195,4) nằm trong các TTM sạch nên giữ.
- **EBITDA_P0 sớm**: 2022Q1 377,7 và 2022Q2 91,9 (nhỏ hơn EBIT TTM) ⇒ D&A suy ra âm (−404; −748); từ 2022Q3 D&A TTM suy ra = 33,8…48,3 (ổn định ~45 từ 2025; khớp khấu hao BCTC 2025 = 44,82 [facts_extracted, từ LCTT kt25]). Dùng D&A suy ra chỉ từ 2022Q3.
- Cột `Cash_P0` = mã 111 (tiền) — KHÔNG gồm đầu tư nắm giữ đến ngày đáo hạn (553,19 tại 30/06/2026 theo ảnh bn26/p07; 558,07 tại 30/09/2026 theo facts_extracted). Dùng Cash_P0 để đo "tiền ròng" sẽ sai.
- Q2/2024: DT chỉ 228,5 nhưng LNST 55,7 (biên 24,4%); Q3/2024 DT 626,6, LNST 67,4 (10,8%) — biến động giữa hai quý liền kề cho thấy dồn/dịch ghi nhận doanh thu theo quý; không có dữ liệu trong BQ để giải thích.

### 1.4 BQ = số công bố ban đầu (quý Q4 chưa kiểm toán) vs BCTC kiểm toán 2025
| FY2025 | Σ4 quý BQ | BCTC kiểm toán UHY (kt25/p09.png) | Lệch |
|---|---|---|---|
| DT thuần | 1.923,386 | 1.923,386 | 0 |
| LN gộp (GPM_TTM2025Q4×ΣDT) | 442,671 | 439,449 | +3,22 |
| EBIT (GP−CPBH−QLDN) | 343,52 | 439,449−82,151−18,160 = 339,14 | +4,38 |
| LNST | 347,493 | 343,213 | +4,28 |
| CFO | 359,14 | 370,75 [facts_extracted, LCTT kt25, chưa tự đối chiếu ảnh] | −11,6 |
Hệ quả: **Q4/2025 trong BQ (GP 95,59; LNST 75,165) là số trước kiểm toán**; số suy từ BCTC kiểm toán: GP Q4/2025 = 439,449−347,083 = 92,37; LNST Q4/2025 = 343,213−272,328 = 70,88. Cả hai cách được ghi; bảng dưới dùng cơ sở BQ để nhất quán TTM. Tương tự HTK 31/12/2025: BQ 67,571 vs BCTC 67,712 [facts_extracted]; Tổng TS BQ 1.440,37 vs 1.444,31.

## 2. Chuỗi theo quý PAT (nguồn: BQ ticker_financial; tỷ đồng)
Ghi chú cột: DT/LNST/CFO/HTK/nợ vay/VCSH/tiền là số của quý hoặc cuối quý; **GPM TTM, EBIT% TTM, D&A TTM là số TTM** (4 quý trượt). VCSH = Tổng TS − Nợ NH − Nợ DH (tự tính). Nợ vay = StDebt_P0 (vay ngắn hạn có lãi); LtDebt_P0 = 0 mọi quý. LNST% = LNST quý/DT quý (tự tính). *D&A TTM trước 2022Q3 không dùng được.
| Quý | DT thuần | LNST | LNST% | CFO | HTK | Nợ vay NH (DH=0) | VCSH | Tiền (mã 111) | GPM TTM | EBIT% TTM | D&A TTM (suy) | P4 TB | Than cốc TB | S TB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021Q4 | 587.5 | 195.4 | 33.3% | - | - | - | - | - | 38.9% | 33.5% | n/a* | 44,157 | 3,156 | 2,035 |
| 2022Q1 | 996.9 | 348.8 | 35.0% | 422.7 | 115.4 | 183.1 | 666.1 | 0.9 | 41.3% | 35.4% | n/a* | 34,559 | 2,910 | 2,411 |
| 2022Q2 | 700.5 | 226.0 | 32.3% | 257.6 | 330.1 | 230.1 | 892.2 | 4.0 | 37.4% | 32.8% | n/a* | 37,852 | 3,311 | 3,769 |
| 2022Q3 | 740.9 | 203.6 | 27.5% | 186.8 | 139.2 | 112.0 | 845.7 | 7.0 | 37.3% | 32.5% | 33.8 | 32,629 | 2,531 | 1,523 |
| 2022Q4 | 711.6 | 186.1 | 26.2% | 283.5 | 67.1 | 73.9 | 781.9 | 203.2 | 36.1% | 30.9% | 45.1 | 34,205 | 2,507 | 1,425 |
| 2023Q1 | 433.6 | 72.7 | 16.8% | 59.6 | 75.0 | 87.6 | 532.1 | 1.6 | 31.7% | 26.6% | 46.2 | 31,787 | 2,492 | 1,189 |
| 2023Q2 | 452.1 | 77.2 | 17.1% | 34.9 | 53.9 | 236.9 | 609.3 | 2.3 | 28.0% | 22.8% | 47.1 | 23,958 | 1,989 | 826 |
| 2023Q3 | 462.0 | 83.5 | 18.1% | 167.3 | 41.1 | 281.5 | 692.9 | 9.5 | 26.1% | 19.8% | 35.7 | 24,730 | 1,963 | 966 |
| 2023Q4 | 362.9 | 52.1 | 14.4% | 22.6 | 89.0 | 316.6 | 520.0 | 61.6 | 21.4% | 15.5% | 48.3 | 25,478 | 2,257 | 1,013 |
| 2024Q1 | 438.1 | 60.8 | 13.9% | 112.2 | 79.5 | 170.9 | 539.6 | 1.7 | 20.8% | 15.0% | 48.3 | 23,636 | 2,115 | 994 |
| 2024Q2 | 228.5 | 55.7 | 24.4% | 95.5 | 185.0 | 130.3 | 595.3 | 34.1 | 21.6% | 15.5% | 48.2 | 22,756 | 1,897 | 1,142 |
| 2024Q3 | 626.6 | 67.4 | 10.8% | 107.3 | 72.0 | 163.3 | 662.7 | 30.9 | 19.7% | 13.3% | 48.0 | 23,237 | 1,837 | 1,341 |
| 2024Q4 | 428.3 | 81.0 | 18.9% | 149.0 | 84.7 | 84.8 | 568.7 | 7.3 | 21.1% | 14.5% | 47.1 | 23,576 | 1,755 | 1,584 |
| 2025Q1 | 436.4 | 84.7 | 19.4% | 7.8 | 85.4 | 11.2 | 577.5 | 2.2 | 23.0% | 16.4% | 46.0 | 23,561 | 1,661 | 1,938 |
| 2025Q2 | 477.7 | 77.6 | 16.3% | -76.1 | 92.3 | 127.1 | 655.1 | 7.3 | 22.0% | 15.7% | 45.2 | 23,494 | 1,489 | 2,381 |
| 2025Q3 | 506.7 | 110.0 | 21.7% | 282.6 | 62.9 | 194.2 | 765.1 | 14.3 | 24.4% | 18.8% | 44.6 | 22,592 | 1,341 | 2,521 |
| 2025Q4 | 502.6 | 75.2 | 15.0% | 144.8 | 67.6 | 174.7 | 590.2 | 31.9 | 23.0% | 17.9% | 44.8 | 22,612 | 1,474 | 3,438 |
| 2026Q1 | 421.9 | 46.6 | 11.0% | -408.3 | 97.9 | 176.9 | 632.5 | 1.7 | 20.1% | 15.4% | 45.0 | 24,514 | 1,412 | 4,239 |
| 2026Q2 | 517.4 | 109.8 | 21.2% | 375.3 | 74.8 | 145.4 | 742.3 | 1.3 | 21.2% | 16.9% | 45.0 | 31,105 | 1,661 | 7,541 |
| 2026Q3 | 440.0 | 59.3 | 13.5% | 161.2 | 120.2 | 67.2 | 708.4 | 1.2 | 18.4% | 14.8% | 45.0 | 27,606 | 2,040 | 8,794 |
Không có trong BQ cho quý: CP bán hàng, CP QLDN, doanh thu/chi phí tài chính, EBT, thuế, khấu hao quý (BQ chỉ có EBITDA TTM). Các khoản này chỉ có ở kỳ có BCTC gốc: Q3/2026 và Q3/2025 (q326/p07), H1/2026 và H1/2025 (bn26/p09), 9T, FY2025/FY2024 (kt25/p09). Từ ảnh (tỷ đồng): Q3/2026: GP 63,604; CPBH 5,049; QLDN 4,711; DT TC 11,371; CP TC 1,467 (lãi vay 1,135); EBT 63,747; thuế 4,427. Q3/2025: GP 130,471; CPBH 20,554; QLDN 4,132; DT TC 13,819; CP TC 3,331; EBT 116,466; thuế 6,499. H1/2026 (H1/2025): GP 186,994 (216,612); CPBH 27,239 (42,638); QLDN 8,038 (8,719); DT TC 20,938 (20,929); CP TC 6,017 (6,265); EBT 166,638 (179,918); thuế 10,245 (17,558). FY2025 (FY2024): CPBH 82,151 (98,879); QLDN 18,160 (15,495); DT TC 47,584 (49,311); CP TC 14,556 (18,988); EBT 372,361 (279,158); thuế 29,148 (14,217).

## 3. Kỳ định danh được (H1 / Q3 / Q4) — GP, EBIT dựng lại từ TTM + neo BCTC
Phương pháp: GP_TTM(q) = GPM_P0(q) × ΣDT 4 quý; GP_q − GP_(q−4) = GP_TTM(q) − GP_TTM(q−1) (vì GP_TTM(q)−GP_TTM(q−1) = GP_q − GP_(q−4)). Neo: Q3/2025=130,471; Q3/2026=63,604; H1/2025=216,612; H1/2026=186,994 (ảnh). Từ đó dựng ngược/xuôi Q3, H1 mọi năm; Q4_y = GP_TTM(Q4_y) − H1_y − Q3_y. EBIT = GP − CPBH − QLDN (định nghĩa này được xác nhận vì EBITM_TTM×DT_TTM khớp: FY2024 248,836 vs 248,835; dự báo xuôi Q3/2026 53,842 vs 53,844; H1/2026 151,717 vs 151,717). SG&A cột (=GP−EBIT) là TỰ TÍNH. EBIT này KHÔNG gồm thu/chi tài chính. LNST% chịu ảnh hưởng thuế: dự án P4 miễn 4 năm 2018–2021, giảm 50% 2022–2030 [facts_extracted, TM thuế Q3/2026, chưa tự đối chiếu ảnh].
**Giới hạn:** chỉ dùng được TTM sạch từ 2022Q3 (mục 1.3). Q3_y−1 = Q3_y − [T(Q3_y)−T(Q2_y)]; H1_y−1 = H1_y − [T(Q2_y)−T(Q4_y−1)]; Q4/2021 = Q4/2022 − [T(2022Q4)−T(2022Q3)]; mọi phép trừ chỉ dùng T ≥ 2022Q3 nên kỳ sớm nhất là H1/2022, Q3/2022, Q4/2021. Q1 và Q2 riêng lẻ không xác định (1 bậc tự do/mỗi năm, chung một hằng số).

| Kỳ | DT thuần | GP | GPM | COGS/DT | SG&A (=GP−EBIT) | EBIT | EBIT% | LNST | LNST% | P4 TB (CNY/t) | P4 quý trước kỳ | Than cốc | Lưu huỳnh |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q4/2021 | 587.5 | 229.0 | 39.0% | 61.0% | 30.7 | 198.3 | 33.8% | 195.4 | 33.3% | 44,157 | 32,074 | 3,156 | 2,035 |
| H1/2022 | 1,697.4 | 673.4 | 39.7% | 60.3% | 92.1 | 581.3 | 34.2% | 574.9 | 33.9% | 36,218 | 44,157 | 3,113 | 3,095 |
| Q3/2022 | 740.9 | 226.2 | 30.5% | 69.5% | 22.5 | 203.7 | 27.5% | 203.6 | 27.5% | 32,629 | 37,852 | 2,531 | 1,523 |
| Q4/2022 | 711.6 | 238.0 | 33.4% | 66.6% | 49.6 | 188.4 | 26.5% | 186.1 | 26.2% | 34,205 | 32,629 | 2,507 | 1,425 |
| H1/2023 | 885.7 | 190.3 | 21.5% | 78.5% | 50.1 | 140.2 | 15.8% | 149.9 | 16.9% | 27,872 | 34,205 | 2,240 | 1,008 |
| Q3/2023 | 462.0 | 108.5 | 23.5% | 76.5% | 29.3 | 79.2 | 17.1% | 83.5 | 18.1% | 24,730 | 23,958 | 1,963 | 966 |
| Q4/2023 | 362.9 | 67.4 | 18.6% | 81.4% | 21.0 | 46.5 | 12.8% | 52.1 | 14.4% | 25,478 | 24,730 | 2,257 | 1,013 |
| H1/2024 | 666.6 | 145.9 | 21.9% | 78.1% | 40.4 | 105.5 | 15.8% | 116.6 | 17.5% | 23,200 | 25,478 | 2,005 | 1,068 |
| Q3/2024 | 626.6 | 112.9 | 18.0% | 82.0% | 45.3 | 67.6 | 10.8% | 67.4 | 10.8% | 23,237 | 22,756 | 1,837 | 1,341 |
| Q4/2024 | 428.3 | 104.4 | 24.4% | 75.6% | 28.7 | 75.7 | 17.7% | 81.0 | 18.9% | 23,576 | 23,237 | 1,755 | 1,584 |
| H1/2025 | 914.1 | 216.6 | 23.7% | 76.3% | 51.4 | 165.3 | 18.1% | 162.4 | 17.8% | 23,527 | 23,576 | 1,571 | 2,161 |
| Q3/2025 | 506.7 | 130.5 | 25.7% | 74.3% | 24.7 | 105.8 | 20.9% | 110.0 | 21.7% | 22,592 | 23,494 | 1,341 | 2,521 |
| Q4/2025 | 502.6 | 95.6 | 19.0% | 81.0% | 23.1 | 72.5 | 14.4% | 75.2 | 15.0% | 22,612 | 22,592 | 1,474 | 3,438 |
| H1/2026 | 939.3 | 187.0 | 19.9% | 80.1% | 35.3 | 151.7 | 16.2% | 156.4 | 16.7% | 27,835 | 22,612 | 1,541 | 5,903 |
| Q3/2026 | 440.0 | 63.6 | 14.5% | 85.5% | 9.8 | 53.8 | 12.2% | 59.3 | 13.5% | 27,606 | 31,105 | 2,040 | 8,794 |
Cột giá = trung bình các phiên T2–T6 của kỳ (sunsirs `yellow_phosphorus`, `coke` CNY/t; TE `sulfur` CNY/t), "quý trước kỳ" = trung bình quý ngay trước ngày đầu kỳ.

## 4. Giá hàng hoá `commodity_prices` — độ phủ và thiếu
Nguồn tra: `kb/data_registry/feeds/bq_commodity_prices.md`. Truy vấn lọc `EXTRACT(DAYOFWEEK) NOT IN (1,7)` (registry: 43 dòng cuối tuần của P4 lặp giá T6 phải loại).
- **P4**: `metric_key=yellow_phosphorus, source=sunsirs, cadence=daily`, CNY/t, sunsirs prodetail-708. Phủ 2020Q1→2026Q4(32 phiên tới 2026-11-13): **64–66 phiên T2–T6 mỗi quý, không quý nào thiếu**. Nhưng số giá trị khác nhau chỉ 10–32 mỗi quý (đứng giá ~69% theo registry ⇒ nhịp thực ≈ tuần). Số trùng registry: TB Q3/25 22.592; Q2/26 31.105; Q3/26 27.606 (khớp). Không có vintage/PIT (registry: fetched_at một lần).
- **Than cốc**: `coke`, sunsirs, CNY/t, 55–66 phiên/quý (2025Q1 chỉ 55); **coking coal TE** `coking_coal`, USD/t, 63–66 phiên/quý. (Hai chuỗi khác hàng khác đơn vị — registry bẫy 6b.)
- **Lưu huỳnh**: `sulfur`, TE daily, CNY/t, 64–66 phiên/quý (lọc `cadence='daily'`).
- **Quặng P**: `phosphate_rock_cny` (TE, CNY/t) chỉ từ **2022-08-19** ⇒ 13 kỳ định danh; 94% phiên đứng giá (registry).
- **Điện: KHÔNG TÌM ĐƯỢC** chuỗi giá điện trong `commodity_prices` (đã thử regex `elec|power|gas|lng|coal|coke|sulf|phosph|silic|quartz|fluor|acid|dap|ammon|yellow` trên metric_key; chỉ có khí tự nhiên/LNG quốc tế, không phải điện Việt Nam). Silic/thạch anh/than đá nhiệt không dùng. 
- Quý 2026Q4 chỉ có 32 phiên P4 tới 2026-11-13 (TB 28.191), chưa có BCTC quý này.
- Không có giá trị NULL; không có quý thiếu toàn bộ.

## 5. Thử quan hệ định lượng
Thiết kế: đơn vị quan sát = kỳ định danh (H1, Q3, Q4), **N=15** (gồm Q4/2021; N=14 khi bỏ Q4/2021 vì điểm P4 cao nhất 44.157 có đòn bẩy lớn). Biến phụ thuộc: **GPM** (=1−COGS/DT; "giá vốn/DT" chỉ là 1−GPM nên hệ số tương quan đối dấu, không phải biến thể thứ hai) và **EBIT margin** (2 biến thể đo). Biến giải thích: P4 cùng kỳ (trễ 0) và P4 quý ngay trước kỳ (trễ 1); than cốc, coking coal, lưu huỳnh, quặng P. Thống kê: Pearson (CI95 bằng Fisher z, p hai phía), Spearman, OLS đơn (CI95 hệ số góc, t-student), leave-one-out (LOO: bỏ lần lượt 1 kỳ, báo min..max). Hệ số góc = thay đổi biên (phần, 0..1) trên **1.000 đơn vị** của biến giải thích (vd +0,0098 ≈ +0,98 điểm % biên mỗi +1.000 CNY/t P4). p-value KHÔNG hiệu chỉnh cho ~30 phép thử đã chạy.
| Phép thử | N | Pearson [CI95] (p) | Spearman (p) | Hệ số góc (biên/1000 đv x) [CI95] | R² | LOO r | LOO hệ số góc |
|---|---|---|---|---|---|---|---|
| GPM ~ P4 cùng kỳ [N15 gồm Q4/2021] | 15 | +0.81 [+0.50; +0.93] (0.000) | +0.47 (0.079) | +0.0098 [+0.0055; +0.0140] | 0.65 | +0.73..+0.87 | +0.0085..+0.0109 |
| GPM ~ P4 quý trước kỳ [N15 gồm Q4/2021] | 15 | +0.66 [+0.23; +0.88] (0.007) | +0.51 (0.052) | +0.0075 [+0.0025; +0.0126] | 0.44 | +0.49..+0.77 | +0.0062..+0.0084 |
| GPM ~ than cốc sunsirs cùng kỳ [N15 gồm Q4/2021] | 15 | +0.74 [+0.38; +0.91] (0.001) | +0.42 (0.118) | +0.1016 [+0.0470; +0.1561] | 0.55 | +0.65..+0.82 | +0.0865..+0.1198 |
| GPM ~ coking coal TE cùng kỳ [N15 gồm Q4/2021] | 15 | +0.62 [+0.15; +0.86] (0.014) | +0.32 (0.243) | +0.6867 [+0.1606; +1.2129] | 0.38 | +0.38..+0.71 | +0.5311..+0.8002 |
| GPM ~ lưu huỳnh cùng kỳ [N15 gồm Q4/2021] | 15 | -0.31 [-0.71; +0.24] (0.264) | +0.01 (0.970) | -0.0107 [-0.0306; +0.0091] | 0.09 | -0.41..-0.01 | -0.0128..-0.0003 |
| GPM ~ quặng P CNY cùng kỳ [N15 gồm Q4/2021] | 13 | -0.04 [-0.58; +0.52] (0.894) | +0.13 (0.661) | -0.0450 [-0.7701; +0.6801] | 0.00 | -0.09..+0.04 | -0.1094..+0.0456 |
| EBIT margin ~ P4 cùng kỳ [N15 gồm Q4/2021] | 15 | +0.84 [+0.58; +0.95] (0.000) | +0.50 (0.058) | +0.0101 [+0.0062; +0.0139] | 0.71 | +0.79..+0.88 | +0.0089..+0.0115 |
| EBIT margin ~ P4 quý trước kỳ [N15 gồm Q4/2021] | 15 | +0.72 [+0.33; +0.90] (0.003) | +0.49 (0.066) | +0.0080 [+0.0034; +0.0127] | 0.52 | +0.57..+0.78 | +0.0071..+0.0090 |
| EBIT margin ~ than cốc sunsirs cùng kỳ [N15 gồm Q4/2021] | 15 | +0.75 [+0.38; +0.91] (0.001) | +0.39 (0.152) | +0.1008 [+0.0473; +0.1544] | 0.56 | +0.65..+0.83 | +0.0859..+0.1199 |
| EBIT margin ~ coking coal TE cùng kỳ [N15 gồm Q4/2021] | 15 | +0.61 [+0.14; +0.86] (0.016) | +0.27 (0.328) | +0.6719 [+0.1489; +1.1949] | 0.37 | +0.37..+0.72 | +0.5069..+0.7895 |
| EBIT margin ~ lưu huỳnh cùng kỳ [N15 gồm Q4/2021] | 15 | -0.17 [-0.63; +0.38] (0.547) | +0.14 (0.630) | -0.0058 [-0.0262; +0.0145] | 0.03 | -0.25..+0.08 | -0.0078..+0.0046 |
| EBIT margin ~ quặng P CNY cùng kỳ [N15 gồm Q4/2021] | 13 | -0.07 [-0.60; +0.50] (0.815) | -0.00 (0.993) | -0.0765 [-0.7807; +0.6276] | 0.01 | -0.16..+0.05 | -0.3218..+0.0505 |
| GPM ~ P4 cùng kỳ [N14 bỏ Q4/2021] | 14 | +0.73 [+0.33; +0.91] (0.003) | +0.35 (0.221) | +0.0109 [+0.0045; +0.0172] | 0.54 | +0.56..+0.82 | +0.0076..+0.0120 |
| GPM ~ P4 quý trước kỳ [N14 bỏ Q4/2021] | 14 | +0.69 [+0.25; +0.89] (0.006) | +0.45 (0.110) | +0.0068 [+0.0023; +0.0113] | 0.48 | +0.43..+0.82 | +0.0042..+0.0076 |
| GPM ~ than cốc sunsirs cùng kỳ [N14 bỏ Q4/2021] | 14 | +0.65 [+0.18; +0.88] (0.012) | +0.29 (0.311) | +0.0895 [+0.0234; +0.1556] | 0.42 | +0.37..+0.74 | +0.0502..+0.1114 |
| GPM ~ coking coal TE cùng kỳ [N14 bỏ Q4/2021] | 14 | +0.57 [+0.06; +0.85] (0.033) | +0.16 (0.573) | +0.5699 [+0.0559; +1.0839] | 0.33 | +0.08..+0.68 | +0.1020..+0.6878 |
| GPM ~ lưu huỳnh cùng kỳ [N14 bỏ Q4/2021] | 14 | -0.32 [-0.73; +0.25] (0.261) | -0.03 (0.923) | -0.0097 [-0.0275; +0.0082] | 0.10 | -0.50..-0.00 | -0.0115..-0.0001 |
| GPM ~ quặng P CNY cùng kỳ [N14 bỏ Q4/2021] | 13 | -0.04 [-0.58; +0.52] (0.894) | +0.13 (0.661) | -0.0450 [-0.7701; +0.6801] | 0.00 | -0.09..+0.04 | -0.1094..+0.0456 |
| EBIT margin ~ P4 cùng kỳ [N14 bỏ Q4/2021] | 14 | +0.79 [+0.44; +0.93] (0.001) | +0.39 (0.169) | +0.0115 [+0.0058; +0.0171] | 0.62 | +0.65..+0.85 | +0.0086..+0.0128 |
| EBIT margin ~ P4 quý trước kỳ [N14 bỏ Q4/2021] | 14 | +0.76 [+0.38; +0.92] (0.002) | +0.42 (0.135) | +0.0073 [+0.0033; +0.0113] | 0.57 | +0.55..+0.83 | +0.0052..+0.0082 |
| EBIT margin ~ than cốc sunsirs cùng kỳ [N14 bỏ Q4/2021] | 14 | +0.65 [+0.18; +0.88] (0.012) | +0.25 (0.383) | +0.0882 [+0.0235; +0.1529] | 0.42 | +0.37..+0.76 | +0.0487..+0.1110 |
| EBIT margin ~ coking coal TE cùng kỳ [N14 bỏ Q4/2021] | 14 | +0.57 [+0.05; +0.84] (0.035) | +0.10 (0.725) | +0.5528 [+0.0452; +1.0604] | 0.32 | +0.06..+0.68 | +0.0671..+0.6753 |
| EBIT margin ~ lưu huỳnh cùng kỳ [N14 bỏ Q4/2021] | 14 | -0.16 [-0.64; +0.40] (0.583) | +0.11 (0.714) | -0.0047 [-0.0230; +0.0135] | 0.03 | -0.28..+0.10 | -0.0064..+0.0049 |
| EBIT margin ~ quặng P CNY cùng kỳ [N14 bỏ Q4/2021] | 13 | -0.07 [-0.60; +0.50] (0.815) | -0.00 (0.993) | -0.0765 [-0.7807; +0.6276] | 0.01 | -0.16..+0.05 | -0.3218..+0.0505 |
| GPM ~ ln(P4 cùng kỳ) [N15] | 15 | +0.79 [+0.46; +0.93] (0.000) | +0.47 (0.079) | +294.4452 [+157.1511; +431.7394] | 0.62 | +0.70..+0.86 | +254.5958..+319.6284 |
| GPM ~ ln(P4 cùng kỳ) [N14] | 14 | +0.70 [+0.27; +0.90] (0.006) | +0.35 (0.221) | +293.8199 [+104.0288; +483.6110] | 0.49 | +0.52..+0.80 | +195.7719..+330.4115 |
| ΔGPM(YoY cùng loại kỳ) ~ ΔP4(YoY) | 12 | +0.35 [-0.28; +0.77] (0.259) | +0.43 (0.159) | +0.0055 [-0.0047; +0.0157] | 0.13 | +0.21..+0.58 | +0.0030..+0.0100 |
| ΔEBITm(YoY) ~ ΔP4(YoY) | 12 | +0.49 [-0.11; +0.83] (0.104) | +0.49 (0.106) | +0.0079 [-0.0019; +0.0177] | 0.24 | +0.39..+0.67 | +0.0056..+0.0122 |
| GPM_TTM ~ P4 TTM-mean (17 quý chồng lấn, N hiệu dụng ≈4-5) | 17 | +0.91 [+0.77; +0.97] (0.000) | +0.48 (0.054) | +0.0111 [+0.0083; +0.0138] | 0.83 | +0.87..+0.94 | +0.0102..+0.0115 |
| GPM_TTM ~ than cốc TTM-mean | 17 | +0.83 [+0.59; +0.94] (0.000) | +0.61 (0.009) | +0.0984 [+0.0626; +0.1342] | 0.70 | +0.77..+0.86 | +0.0853..+0.1050 |
| GPM ~ P4 cùng kỳ [H1/2024→Q3/2026 (N=8)] | 8 | -0.57 [-0.91; +0.22] (0.136) | -0.33 (0.420) | -0.0100 [-0.0242; +0.0042] | 0.33 | -0.68..-0.25 | -0.0158..-0.0041 |
| EBIT margin ~ P4 cùng kỳ [H1/2024→Q3/2026 (N=8)] | 8 | -0.30 [-0.83; +0.51] (0.472) | -0.17 (0.693) | -0.0045 [-0.0189; +0.0099] | 0.09 | -0.54..-0.04 | -0.0090..-0.0007 |
| GPM ~ P4 cùng kỳ [Q4/2021→Q4/2023 (N=7)] | 7 | +0.90 [+0.48; +0.99] (0.005) | +0.86 (0.014) | +0.0112 [+0.0051; +0.0172] | 0.82 | +0.89..+0.94 | +0.0100..+0.0158 |
| EBIT margin ~ P4 cùng kỳ [Q4/2021→Q4/2023 (N=7)] | 7 | +0.91 [+0.48; +0.99] (0.005) | +0.82 (0.023) | +0.0115 [+0.0053; +0.0177] | 0.82 | +0.89..+0.95 | +0.0104..+0.0164 |
| GPM ~ chỉ số thời gian (xu hướng) [N15] | 15 | -0.78 [-0.92; -0.45] (0.001) | -0.67 (0.007) | -13.2421 [-19.5617; -6.9226] | 0.61 | -0.83..-0.72 | -14.2462..-11.4201 |
| P4 ~ chỉ số thời gian [N15] | 15 | -0.71 [-0.90; -0.32] (0.003) | -0.67 (0.006) | -1000986.5568 [-1588033.3572; -413939.7564] | 0.51 | -0.79..-0.64 | -1220161.3204..-698191.4628 |
### Đọc kết quả (chỉ mô tả)
- **Toàn mẫu**: GPM~P4 cùng kỳ r=+0,81 (N=15) / +0,73 (N=14); hệ số góc ≈ +1,0 điểm % biên / +1.000 CNY/t, CI95 [+0,55; +1,40] (N=15). LOO không đổi dấu (r +0,73…+0,87). Trễ 1 quý yếu hơn (+0,66/+0,69). Spearman thấp hơn hẳn (+0,47/+0,35; p=0,08/0,22) ⇒ tương quan tuyến tính bị chi phối bởi cụm 2021–2023 (giá 24.700–44.200, biên 18–40%) so với cụm 2024–2026 (giá 22.600–27.800, biên 14,5–25,7%).
- **Giả tương quan do xu hướng**: GPM~chỉ số thời gian r=−0,78 (p=0,001); P4~chỉ số thời gian r=−0,71 (p=0,003). Hai chuỗi cùng đi xuống ⇒ tương quan mức không phân biệt được "P4 kéo biên" với "cùng chu kỳ/xu hướng".
- **Sai phân YoY cùng loại kỳ (N=12)**: ΔGPM~ΔP4 r=+0,35 [−0,28; +0,77] p=0,26; ΔEBIT%~ΔP4 r=+0,49 p=0,10 ⇒ không có ý nghĩa thống kê.
- **Giai đoạn giá hẹp H1/2024→Q3/2026 (N=8)**: GPM~P4 r=−0,57 [−0,91; +0,22] p=0,14; EBIT%~P4 r=−0,30 ⇒ không có bằng chứng quan hệ cùng chiều khi P4 dao động trong 22.600–27.800; điểm 2026 (P4 cao, biên thấp) kéo dấu âm.
- **Giai đoạn 2021–2023 (N=7)**: r=+0,90 (p=0,005), nhưng N=7 và cùng xu hướng giảm.
- **Than cốc** cho dấu DƯƠNG với biên (r +0,65…+0,75) — ngược chiều với giả thuyết "chi phí đầu vào tăng ⇒ biên giảm", nhất quán với việc cả hai cùng cao 2021–22 (đồng pha chu kỳ), không phải bằng chứng nhân quả. **Lưu huỳnh** r=−0,31 (p=0,26); **quặng P CNY** r=−0,04 (p=0,89, N=13): không có quan hệ phát hiện được.
- **Biến thể TTM (17 quý chồng lấn)**: GPM_TTM~P4 TTM-mean r=+0,91, hệ số góc +1,1 điểm %/1.000 CNY/t. Các quan sát chồng lấn 3/4 cửa sổ ⇒ N hiệu dụng chỉ ≈ 4–5 (17/4); p-value ở đây KHÔNG dùng được.
- **Cảnh báo bên liên quan**: DT PAT có thành phần bán cho công ty mẹ DLC lớn và biến động (mục 6) ⇒ giá bán thực hiện có thể không theo giá giao ngay sunsirs; chưa có chuỗi đơn giá/sản lượng nên không tách được hiệu ứng giá, lượng, cơ cấu khách, chi phí.
- **Kết luận dữ liệu cho phép**: (i) cùng chiều, mạnh trên toàn mẫu mức; (ii) KHÔNG xác lập được quan hệ ổn định/nhân quả: N hiệu dụng nhỏ, xu hướng chung, đảo dấu ở giai đoạn gần, rủi ro giá chuyển giao nội bộ. CẤM nội suy 3 điểm; tôi không đưa dự báo. Hai cách hiểu 2026 (giá P4 spot cao nhưng GPM thấp), cả hai còn mở: (A) giá thực hiện tới bên liên quan/cơ cấu bán khác giá spot; (B) giá vốn tăng nhanh hơn doanh thu (9T26: GVHB 1.128,706 so với 1.073,752 = +5,1% trong khi DT thuần 1.379,304 so với 1.420,835 = −2,9%, số từ ảnh q326/p07). Bằng chứng phân biệt: đơn giá bán và sản lượng theo khách hàng, giá vốn theo yếu tố từng quý — không có trong BQ.

## 6. Bên liên quan trong doanh thu (cảnh báo theo yêu cầu)
- Đã tự đối chiếu ảnh (/home/trido/thanhdt/wt-1571194491489091644/agents/Taylor/research/blind_val_20261114/inputs/src/png_q326/p32.png, trang 28): bán nguyên vật liệu/thành phẩm/hàng hoá cho CTY TNHH MTV Hoá chất Đức Giang Lào Cai (DLC, công ty mẹ) **9T/2026 878,140 tỷ vs 9T/2025 153,977 tỷ**; mua nguyên vật liệu từ DLC 627,916 vs 537,036 tỷ. ⇒ 878,140/1.379,304 = **63,7%** DT 9T/2026; 153,977/1.420,835 = 10,8% 9T/2025 [TỰ TÍNH].
- Từ facts_extracted.md (trích tay, CHƯA tự đối chiếu ảnh bn26/kt25): bán cho DLC H1/2026 501,85 (H1/2025 80,48) ⇒ Q3/2026 riêng 376,29/440,03 = 85,5% DT quý [TỰ TÍNH]; FY2025 163,72 (8,5%) và FY2024 313,00 (18,2%) DT.
- Hệ quả cho Mục 5: từ Q3/2026 phần lớn doanh thu là giao dịch nội bộ tập đoàn; BQ không có giá/sản lượng. Báo cáo kiểm toán/soát xét 2025 và H1/2026 có ý kiến ngoại trừ liên quan khởi tố lãnh đạo cũ (facts_extracted; không đánh giá ở đây).

## 7. Biên động 2 chiều (mô tả, không dự báo)
Biên theo kỳ định danh (GP và EBIT dựng lại) và biên LNST theo quý (số trực tiếp từ BQ, chịu ảnh hưởng thuế suất và thu/chi tài chính) và biên TTM:
| Chuỗi | N | Min (kỳ) | P10 | P50 | P90 | Max (kỳ) | TB | Độ lệch chuẩn |
|---|---|---|---|---|---|---|---|---|
| GPM kỳ định danh (toàn mẫu, 15 kỳ) | 15 | 14.5% (Q3/2026) | 18.2% | 23.5% | 36.8% | 39.7% (H1/2022) | 24.9% | 7.6pp |
| GPM kỳ định danh (8 quý gần nhất = 6 kỳ) | 6 | 14.5% (Q3/2026) | 16.7% | 21.8% | 25.1% | 25.7% (Q3/2025) | 21.2% | 4.2pp |
| EBIT margin kỳ định danh (toàn mẫu) | 15 | 10.8% (Q3/2024) | 12.5% | 17.1% | 31.3% | 34.2% (H1/2022) | 19.6% | 7.5pp |
| EBIT margin (8 quý gần nhất) | 6 | 12.2% (Q3/2026) | 13.3% | 16.9% | 19.5% | 20.9% (Q3/2025) | 16.6% | 3.0pp |
| NP margin QUÝ (19 quý 2022Q1-2026Q3) | 19 | 10.8% (2024Q3) | 13.0% | 18.1% | 28.4% | 35.0% (2022Q1) | 19.6% | 6.8pp |
| NP margin QUÝ (8 quý gần nhất) | 8 | 11.0% (2026Q1) | 12.7% | 17.6% | 21.4% | 21.7% (2025Q3) | 17.1% | 3.8pp |
| GPM_TTM (17 quý, 2022Q3-2026Q3) | 17 | 18.4% (2026Q3) | 20.0% | 22.0% | 33.4% | 37.3% (2022Q3) | 24.5% | 5.6pp |
| GPM_TTM (8 quý gần nhất) | 8 | 18.4% (2026Q3) | 19.6% | 21.6% | 23.4% | 24.4% (2025Q3) | 21.7% | 1.9pp |
| EBITM_TTM (17 quý) | 17 | 13.3% (2024Q3) | 14.6% | 16.4% | 28.3% | 32.5% (2022Q3) | 18.9% | 5.8pp |
| EBITM_TTM (8 quý gần nhất) | 8 | 14.5% (2024Q4) | 14.7% | 16.0% | 18.1% | 18.8% (2025Q3) | 16.3% | 1.5pp |
- Biên gộp **cao nhất**: H1/2022 39,7% (P4 TB 36.218); biên gộp **thấp nhất**: Q3/2026 14,5% (P4 TB 27.606), tiếp theo Q3/2024 18,0% và Q4/2023 18,6%. Cả hai cực đều là kỳ có BCTC gốc hoặc dựng từ neo; không phải kỳ Q1/Q2 riêng.
- EBIT margin **cao nhất**: H1/2022 34,2%; **thấp nhất**: Q3/2024 10,8% (kế: Q3/2026 12,2%, Q4/2023 12,8%).
- Biên LNST quý: cao nhất 35,0% (2022Q1), thấp nhất 10,8% (2024Q3); trong 8 quý gần nhất 11,0% (2026Q1) … 21,7% (2025Q3).
- Biên độ co lại: SD GPM toàn mẫu 7,6 điểm % → 6 kỳ gần nhất 4,2 điểm %; GPM_TTM 8 quý gần nhất dao động 18,4%–24,4%.
- Cảnh báo mẫu: "8 quý gần nhất" của GPM/EBIT = 6 kỳ (Q4/2024, H1/2025, Q3/2025, Q4/2025, H1/2026, Q3/2026) vì Q1/Q2 không tách được; kỳ H1 là trung bình 2 quý. Không có phân vị Q1, Q2 riêng.

## ĐÃ BỎ
- Không đọc/ghi cột Close, Price, PE, PB, PS, PCF, EVEB, PEG, DY, PE_MA*, PB_MA*, EVEB_MA*, EPS-theo-giá của `ticker_financial` (có trong bảng; không chọn). Truy vấn (3) có chọn `EPS_P0` và `OShares` (số liệu doanh nghiệp tính từ lợi nhuận/số cp; không phải giá) nhưng không dùng trong bất kỳ bảng nào ở đây.
- Không dùng `ticker`/`ticker_1m`/`ticker_prune`.
- Không chép tin/giá cổ phiếu PAT nào từ `commodity_prices` registry (registry chỉ chứa giá hàng hoá).

## KHÔNG TÌM ĐƯỢC
- GP/EBIT/SG&A của **riêng Q1 và Q2** từng năm (đã thử: sai phân TTM + 4 neo; BCTC bn26 chỉ có số luỹ kế 6 tháng, không có cột quý; BCTC Q1/2026 và Q2 riêng không có trong thư mục inputs).
- CP bán hàng, QLDN, DT/CP tài chính, EBT, thuế **theo quý** trước 2025 (BQ không có cột; chỉ EBITM TTM → EBIT TTM → suy SG&A tổng theo kỳ).
- Khấu hao theo quý (BQ chỉ có EBITDA TTM; D&A TTM suy ra dùng được từ 2022Q3).
- Chuỗi giá điện; giá bán thực hiện/sản lượng P4; giá chuyển giao nội bộ với DLC.
- Đầu tư nắm giữ đến ngày đáo hạn theo quý (Cash_P0 chỉ là mã 111).

## ĐIỂM MÂU THUẪN
- FY2025: BQ (số công bố trước kiểm toán) và BCTC kiểm toán lệch LNST +4,28 tỷ, GP +3,22, EBIT +4,38, CFO −11,6 (mục 1.4); hai cơ sở được ghi cả hai, không tự chọn.
- GPM_P0 trong BQ có tên như số quý nhưng là TTM (vd 2026Q3 = 18,4%, trong khi GPM quý Q3/2026 theo BCTC = 14,5%); dùng sai sẽ ra biên cao hơn thực.
- Tiền (Cash_P0) vs đầu tư HTM (mục 1.3). Tiền BS 1,246 vs thuyết minh 1,286 tại 30/09/2026 [facts_extracted].
- facts_extracted.md ghi 2026-11-02 là ngày công bố Q3 trong BQ, trong khi BCTC ký 20/10/2026 (ảnh): `Release_Date` BQ là ngày vào cơ sở dữ liệu, không phải ngày ký.

## SQL ĐÃ CHẠY (tái lập)
```
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
-- (1) liệt kê cột
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 "SELECT column_name, data_type FROM tav2_bq.INFORMATION_SCHEMA.COLUMNS WHERE table_name='ticker_financial' ORDER BY ordinal_position"
-- (2) metric_key hàng hoá liên quan
SELECT c.metric_key, c.source, c.cadence, ANY_VALUE(c.unit) unit, MIN(c.observation_date) mn, MAX(c.observation_date) mx, COUNT(*) n FROM tav2_bq.commodity_prices AS c WHERE REGEXP_CONTAINS(c.metric_key, r'(?i)phosph|coke|coal|sulf|sulph|elec|power|silic|quartz|fluor|acid|dap|phosphate|diammon|ammon|gas|lng|yellow') GROUP BY 1,2,3 ORDER BY 1,2,3
```
(3) dữ liệu tài chính PAT — tệp `data/sql_q1_ticker_financial_PAT.sql` (chỉ cột cơ bản):
```
SELECT t.ticker, t.time, t.quarter, t.ID_Release, t.Release_Date, t.OShares,
 t.Revenue_P0,t.Revenue_P1,t.Revenue_P2,t.Revenue_P3,t.Revenue_P4,t.Revenue_P5,t.Revenue_P6,t.Revenue_P7,
 t.NP_P0,t.NP_P1,t.NP_P2,t.NP_P3,t.NP_P4,t.NP_P5,t.NP_P6,t.NP_P7,
 t.GPM_P0,t.GPM_P1,t.GPM_P2,t.GPM_P3,t.GPM_P4,t.GPM_P5,t.GPM_P6,t.GPM_P7,
 t.Inventory_P0,t.Inventory_P1,t.Inventory_P2,t.Inventory_P3,t.Inventory_P4,t.Inventory_P5,t.Inventory_P6,t.Inventory_P7,
 t.CF_OA_P0,t.CF_OA_P1,t.CF_OA_P2,t.CF_OA_P3,t.CF_OA_P4,
 t.EBITM_P0,t.EBITM_P4,t.NPM_P0,t.NPM_P4,t.EBITDA_P0,t.StDebt_P0,t.LtDebt_P0,t.totalAsset_P0,t.StLiab_P0,t.LtLiab_P0,t.Cash_P0,t.AR_P0,t.LtInvest_P0,t.EPS_P0
FROM tav2_bq.ticker_financial AS t WHERE t.ticker='PAT' ORDER BY t.time
```
(4) giá hàng hoá theo quý — tệp `data/sql_q2_commodity_quarterly.sql`:
```
SELECT c.metric_key, c.source, CONCAT(CAST(EXTRACT(YEAR FROM c.observation_date) AS STRING),'Q',CAST(EXTRACT(QUARTER FROM c.observation_date) AS STRING)) AS quarter,
 COUNT(*) AS n_obs, COUNT(DISTINCT c.value) AS n_distinct, AVG(c.value) AS mean_val, APPROX_QUANTILES(c.value,2)[OFFSET(1)] AS median_val, MIN(c.value) AS min_val, MAX(c.value) AS max_val,
 MIN(c.observation_date) AS first_d, MAX(c.observation_date) AS last_d
FROM tav2_bq.commodity_prices AS c
WHERE c.observation_date>='2020-01-01' AND EXTRACT(DAYOFWEEK FROM c.observation_date) NOT IN (1,7)
 AND ((c.metric_key='yellow_phosphorus' AND c.source='sunsirs' AND c.cadence='daily')
   OR (c.metric_key='coke' AND c.source='sunsirs' AND c.cadence='daily')
   OR (c.metric_key='coking_coal' AND c.source='trading_economics' AND c.cadence='daily')
   OR (c.metric_key='sulfur' AND c.source='trading_economics' AND c.cadence='daily')
   OR (c.metric_key='phosphate_rock_cny' AND c.source='trading_economics' AND c.cadence='daily')
   OR (c.metric_key='ferrosilicon' AND c.source='sunsirs' AND c.cadence='daily'))
GROUP BY 1,2,3 ORDER BY 1,3
```
Sau đó: `cd factpack/data && /home/trido/thanhdt/wc_venv/bin/python pat_analysis.py`.
