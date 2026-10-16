# FPT — DCF theo phạm vi SAU khi ngừng hợp nhất FPT Telecom (14/10/2026, job `Taylor_20261014_055001`)

CHỈ NGHIÊN CỨU — không đặt lệnh, không sửa code production/trading_rules. Trả lời phản biện REFUTED của
fundamental-skeptic cho `research/fpt_dd_tech_20261014/README.md`.
Nhãn: **[ĐO]** BQ/DNSE/BCTC qua báo chí có trích · **[ƯỚC]** có công thức · **[GĐ]** giả định · **[KTĐ]** không tìm được.
Tổ hợp thận trọng / cơ sở / lạc quan đã **khai trước** trong `PREREG.md` (md5 `cd17b6dc…`, ghi lên bus lúc
05:58Z, trước khi chạy mô hình). Không đổi tổ hợp sau khi xem kết quả.

## Kết luận: DCF dòng tiền phạm vi mới KHÔNG cho biên an toàn ở 56,7k. Rút lại khuyến nghị "mua chia đợt" dựa trên DCF

| Tổ hợp (khai trước) | g_T | r | FOX chiết khấu | g stage-1 | **FV/cp** | MOS @ 56.700 live | Stop 50,5k < FV? |
|---|---|---|---|---|---|---|---|
| Thận trọng | cpi 3,44% | 15,9% (7,4 + ERP 8,5) | 30% | 9,2% | **33.900** | −67% | **KHÔNG** |
| **Cơ sở** | cpi_gdp_half 6,55% | 14,9% (7,4 + ERP 7,5) | 15% | 12,0% | **49.600** | **−14%** | **KHÔNG** (thấp hơn stop 1,9%) |
| Lạc quan | cap_rf 7,40% | 13,9% (7,4 + ERP 6,5) | 0% | 13,7% | **65.100** | +13% | có |

FCFE gốc = TB 3 năm 2023–25 dòng tiền **core** (hợp nhất cũ − FOX) = **4.348 tỷ** (so với 6.335 tỷ bản cũ, −31%).
Mỗi FV = PV FCFE core + 45,66% × vốn hoá FOX (giá DNSE live) × (1 − chiết khấu), chia 1.714,3tr cp.

- **Bản cũ 78,7k sai cấu trúc**: cùng r/g_T mặc định, chỉ đổi phạm vi (bỏ FOX khỏi FCFE, cộng phần vốn FOX theo
  giá thị trường) FV giảm 75,1k → 62,4k (75,1k chứ không 78,7k vì ma trận dùng chung g lịch sử 17,5%); đổi sang tổ hợp cơ sở → 49,6k.
- **Tam giác PE ngược hướng DCF**: PE forward 2026E = **9,4** (LNST mẹ 2026E ~10.290 tỷ, EPS ~6.000). Đặt ở PE peer
  ELC 9,8 / CMG 11,4 → 58,9–68,7k; SOTP (core × PE 10–12 + FOX thị trường) → 57,0–70,1k. **Chỗ vênh là tỷ lệ
  chuyển lãi thành tiền**: FCF core / LNST core = 0,80 (2023), 0,86 (2024), **0,39 (2025)**; H1/2026 âm. PE coi
  lãi là tiền; DCF thì không. Rẻ theo PE chỉ đúng nếu tỷ lệ chuyển tiền quay về ≥0,8.
- **Stop 50,5k KHÔNG được FV thận trọng đỡ** (33,9k), và còn nằm trên FV cơ sở (49,6k). Đó là stop theo giá/rủi ro,
  không phải sàn giá trị. Câu "50,5k ≈ FV DCF thận trọng nhất" trong README cũ không còn đúng.
- **KQKD 9T/2026: CHƯA công bố** (tra 14/10 ~13:00 ICT; năm 2025 công bố 24/10). Dải trên chưa phản ánh 9T.

**Đề xuất [GĐ, cần user duyệt]:** không mở đợt 1 trước KQKD 9T. Nếu user vẫn muốn mua thăm dò theo luận điểm PE
(cược rẻ theo bội số / hồi về trung bình, không phải theo DCF): ≤1–1,5% NAV/account (1/3 mức cũ); stop đóng cửa
**< 50,5k** (giữ, nhưng gọi đúng tên là stop rủi ro, ≈ −11%); **time-stop 9 tháng (~15/07/2027)**: thoát nếu
CFO core cả năm 2026 < 0,5 × LNST core (báo cáo năm ~cuối 01/2027 là điểm kiểm tra đầu tiên); chốt lời tầng 1 ở
**~65k** (FV lạc quan ≈ SOTP PE 12), tầng 2 ở **+30% (~73,7k)** chỉ khi FCF 2026 xác nhận tỷ lệ chuyển tiền ≥0,8.

### Sau KQKD 9T (~20–25/10) — cái gì sẽ đổi kết luận
| Kết quả 9T | Diễn giải | Hệ quả |
|---|---|---|
| CFO core Q3/26 ≥ ~2.600 tỷ (Q3 2023/24/25 core: 2.596 / 2.585 / 3.279 [ĐO]) VÀ phải thu không tăng tiếp | H1 âm là mùa vụ + lệch thời điểm thu tiền | Nghiêng về biến thể "chuẩn hoá" (cơ sở 60,2k, MOS +6%) — vẫn mỏng |
| CFO Q3 dương nhưng < 1.500 tỷ, hoặc DSO core > 90 ngày | vốn lưu động phình thật | Giữ FV cơ sở 49,6k → không mua |
| LNST mẹ 9T < +12% hoặc ký mới nước ngoài chậm lại | g stage-1 thấp hơn cả tổ hợp thận trọng (15%) | Dải dịch xuống, thoát mọi vị thế thăm dò |

## Ma trận đầy đủ (FV đ/cp; g lịch sử = trung bình cho mọi ô) — `matrix_fv.csv`

| Phạm vi | r | g_T cpi 3,44% | cpi_gdp_half 6,55% | cap_rf 7,40% |
|---|---|---|---|---|
| core + FOX ck 0% | rf 7,4 + ERP 6,5 | 44.015 | 56.829 | 62.416 |
| | rf 7,4 + ERP 7,5 | 41.002 | 51.190 | 55.405 |
| | rf 7,4 + ERP 8,5 | 38.477 | 46.762 | 50.049 |
| | rf chậm MA12 6,26 + ERP 6,5 | 48.251 | 65.496 | 63.162* |
| core + FOX ck 15% | rf 7,4 + ERP 6,5 | 42.380 | 55.193 | 60.781 |
| | rf 7,4 + ERP 7,5 | 39.367 | **49.555** | 53.770 |
| | rf 7,4 + ERP 8,5 | 36.842 | 45.126 | 48.413 |
| | rf chậm MA12 + ERP 6,5 | 46.616 | 63.861 | 61.527* |
| core + FOX ck 30% | rf 7,4 + ERP 6,5 | 40.745 | 53.558 | 59.145 |
| | rf 7,4 + ERP 7,5 | 37.732 | 47.919 | 52.135 |
| | rf 7,4 + ERP 8,5 | 35.207 | 43.491 | 46.778 |
| | rf chậm MA12 + ERP 6,5 | 44.981 | 62.226 | 59.892* |
| legacy (hợp nhất cũ, SAI phạm vi — chỉ để đối chiếu) | rf 7,4 + ERP 6,5 | 48.253 | 66.924 | 75.066 |
| | rf 7,4 + ERP 7,5 | 43.863 | 58.708 | 64.850 |
| | rf 7,4 + ERP 8,5 | 40.183 | 52.255 | 57.045 |
| | rf chậm MA12 + ERP 6,5 | 54.426 | 79.554 | 76.153* |

\* hàng rf chậm: cap_rf tính lại = min(cpi + GDP, rf chậm) = 6,26% (< cpi_gdp_half), nên cột cap_rf thấp hơn.
36 ô phạm vi core: **10/36 ô có FV > giá live**, 16/36 ô có FV > stop 50,5k; trung vị 49,0k, min 35,2k, max 65,5k.
Các ô FV > giá đều cần g_T ≥ 6,55% VÀ ERP ≤ 6,5% (hoặc rf chậm). Hàng rf chậm KHÔNG dùng cho nhãn nào (khai trước).

Biến thể FCFE gốc (khai trước là biến thể, không phải chính): "chuẩn hoá" = 0,66 (FCF/LNST core 2023–25) × LNST
core TTM Q2/26 8.334 = 5.497 tỷ → thận trọng 40,9k / cơ sở 60,2k / lạc quan 79,4k (`labels_fv.csv`).

## 1. Thiểu số — thay "15–20%" không nguồn bằng số có nguồn

- **[ĐO, ACBS Flash Note 23/03/2026, `src_acbs_flashnote_20260323.pdf`]** EAT 2025 hợp nhất cũ **11.232 tỷ**, NPATMI
  9.376 → lợi ích cổ đông không kiểm soát **1.856 tỷ = 16,5% EAT**. FOX đóng góp 31,0% EAT (3.482 tỷ) → 54,34% không
  thuộc FPT ≈ 1.892 tỷ ⇒ **thiểu số ngoài FOX ≈ 0** [ƯỚC] (−36 tỷ, sai số làm tròn). Nghĩa là gần như toàn bộ thiểu số
  nằm ở FOX; bóc FOX ra là bóc luôn thiểu số.
- Không lấy được BCTC kiểm toán 2025 / thuyết minh gốc (link IR fpt.com 404; BQ không có cột MI) [KTĐ]. Số ACBS là
  nguồn thứ cấp nhưng khớp NPATMI BQ (9.376).
- Điều chỉnh "~15–20% dòng tiền" cũ thực tế lớn hơn: FOX chiếm **31% FCF hợp nhất 2023–25** [ĐO BQ] (1.988/6.336 tỷ/năm),
  không phải chỉ phần thiểu số — vì phần 45,66% của FPT trong FOX giờ được định giá riêng.

## 2. FCF H1/2026 âm: mùa vụ hay xấu đi? — `cashflow_scope.csv`

Core 2021–25 = FPT hợp nhất cũ − FOX hợp nhất (BQ cùng quý) [ƯỚC: bỏ qua giao dịch nội bộ FPT↔FOX]; 2026 = số báo cáo.

| Năm | CFO core H1 | CFI core H1 | FCF core H1 | FCF core cả năm | LNST mẹ core | FCF/LNST |
|---|---|---|---|---|---|---|
| 2021 | 997 | −987 | 10 | 1.923 | 3.501 | 0,55 |
| 2022 | −69 | −669 | −737 | 1.890 | 4.313 | 0,44 |
| 2023 | 791 | −1.089 | −298 | 4.329 | 5.384 | 0,80 |
| 2024 | 1.328 | −1.106 | 222 | 5.635 | 6.577 | 0,86 |
| 2025 | 319 | −2.636 | −2.317 | 3.081 | 7.815 | 0,39 |
| **2026** | **−1.146** | −1.336 | **−2.482** | ? | H1 4.198 (+14,1%) | ? |

- **Mùa vụ thật** [ĐO]: FCF core H1 luôn ≈ 0 hoặc âm (−0,7k…+0,2k), cả năm dương 1,9k–5,6k → H2 gánh dòng tiền.
- **Nhưng H1/2026 tệ hơn mùa vụ** [ĐO]: CFO core H1/26 **−1.146** là thấp nhất 6 năm (trước đó −69…+1.328), kém H1/25
  −1.465 tỷ. Nếu cổ tức FOX 2025 (~675 tỷ = 2.000đ × 738,8tr cp × 45,66%) đã về trong H1/26 (nằm ở CFI) thì FCF core
  không gồm cổ tức FOX còn **−3.157** so với −2.317 H1/25 [ƯỚC; ngày trả cổ tức FOX 2025: KTĐ].
- **Phải thu giải thích gần trọn phần hụt CFO** [ĐO/ƯỚC]: DSO core = AR core / doanh thu core TTM × 365: Q2/25
  **80,7** → Q4/25 88,2 → Q2/26 **90,8 ngày**. AR core +2.811 tỷ (+26,7% YoY) trong khi doanh thu core TTM +12,6%.
  +10 ngày DSO × 53.619/365 ≈ **1.470 tỷ** — xấp xỉ đúng mức CFO H1 hụt so với năm trước. (Con số "DSO 64,8 vs 59,8"
  trong README cũ chia AR cho doanh thu khác phạm vi, đừng dùng.)
- Thuế, vốn lưu động theo dự án, tách IT nước ngoài vs nội địa cho dòng tiền: BCTC có, nhưng không lấy được bản gốc [KTĐ].
- FOX tự thân H1/26 cũng âm (−1.314 so +705 H1/25) [ĐO BQ] → nhóm FPT nói chung thu tiền chậm hơn trong 2026.
- 2025 CFI core −2.636 trong riêng H1 (Q1/25 −2.607 hợp nhất): gồm capex AI Factory và/hoặc gửi tiền có kỳ hạn —
  BQ không tách được [KTĐ]. **Thiên lệch đã biết**: nếu một phần CF_Invest là gửi tiền ròng (tài sản vẫn của cổ đông)
  thì FCFE TB 3 năm đánh giá THẤP — đây là lý do giữ biến thể "chuẩn hoá" làm độ nhạy.

## 3. Cầu nối FV và kiểm đếm trùng

FV/cp = [PV(FCFE core) + 45,66% × vốn hoá FOX × (1 − ck)] / 1.714,3tr cp.
- **FCFE core không gồm cổ tức FOX**: 2023–25 tính bằng hợp nhất cũ − FOX, nên cổ tức FOX→FPT đã bị loại khi hợp nhất
  và không quay lại. Không đếm trùng với phần vốn FOX định giá theo thị trường.
- **FOX** [ĐO]: DNSE live 55.400 (11:21 ICT, KL phiên chỉ 25.100 cp — UPCoM rất mỏng) × 738,8tr cp = 40.927 tỷ;
  LNST TTM 3.647 → PE 11,2. Phần 45,66% = 18.687 tỷ = **10.900 đ/cp FPT** (ck 15% → 9.266; ck 30% → 7.631). Giá trị
  sổ LtInvest FPT Q2/26 = 11.131 tỷ (gồm cả khoản đầu tư khác) — thấp hơn thị trường. Chiết khấu holding/thanh khoản
  đáng kể là có lý do: FPT không kiểm soát, Bộ Công an nắm 50,17%, thanh khoản FOX gần bằng 0.
- **Nợ ròng: KHÔNG trừ/cộng.** FCFE = CF_OA + CF_Invest: lãi vay đã nằm trong CFO, lãi tiền gửi + gửi/rút có kỳ hạn
  trong CFI. Tiền ròng core cuối 2025 ≈ 13.490 tỷ (ACBS 19.080 × (1 − 29,3%)) = 7.870 đ/cp — cộng thêm sẽ đếm trùng
  dòng lãi. (Lưu ý: BQ `Cash_P0` không gồm tiền gửi có kỳ hạn nên BQ ra "nợ ròng" ~9,6k còn ACBS ra "tiền ròng" 19,1k —
  README cũ dùng con số BQ là sai dấu.)
- **Đầu tư khác** (FRT ~46%, Synnex FPT…) nằm trong core theo vốn chủ — không định giá riêng [KTĐ thị giá đã kiểm].
- **OShares** 1.714,3tr [ĐO BQ 2026Q2]; `shares_outstanding_live` không có dòng FPT; +0,63% so 2025Q4 (1.703,5tr,
  ACBS 1.704 ngày 20/03) = ESOP.

## 4. Tăng trưởng explicit

g_exp theo đúng công thức production `dcf_valuation.py`: g_T + 0,5 × (g_hist − g_T), clamp g_hist ≤ 20%.
- LNST mẹ core CAGR 2022→25 **21,9%** [ƯỚC, = LNST mẹ − 45,66% × LNST FOX], clamp 20%; H1/26 core +14,1% [ĐO/ƯỚC];
  kế hoạch LNTT 2026 +15% like-for-like [ĐO ĐHĐCĐ]. Kế hoạch theo mảng [ACBS]: công nghệ DT +18,4% / LNTT +24,9%;
  giáo dục-đầu tư-khác DT −3,3% / LNTT +1,3%. H1/26 [Mekong ASEAN]: công nghệ LNTT +16,9%, IT nước ngoài DT +13,4%,
  ký mới nước ngoài +32,3%; 2T/26 giáo dục-đầu tư-khác LNTT −17,3%.
- g_hist: thận trọng 15% (min) / cơ sở 17,5% (TB) / lạc quan 20% (max) → g_exp 9,2% / 12,0% / 13,7%.

## 5. Tam giác PE (d)

| LNST mẹ 2026E (phạm vi mới, đã gồm lãi FOX theo vốn chủ) | tỷ | EPS | PE @ 56,7k |
|---|---|---|---|
| Kế hoạch LNTT 11.629 × (NPATMI/LNTT H1 = 0,885) | 10.288 | 6.001 | 9,4 |
| Run-rate 8T 6.761 × 12/8 (8T: báo chí, chưa kiểm lại) | 10.142 | 5.916 | 9,6 |
| ACBS 03/2026 | 10.696 | 6.239 | 9,1 |

PE × EPS 6.001: ELC 9,8 → 58,9k · FOX 11,2 → 67,1k · CMG 11,4 → 68,7k · PE 13 → 78,0k · trung vị 5 năm FPT 19,7 →
118k. **PE lịch sử FPT là mỏ neo yếu**: nó được định trong thời kỳ thị trường trả giá cho "AI tăng trưởng"; ngành đang
bị xả kỳ vọng AI (Accenture/Cognizant bị hạ bội số) — fleet đã bác CMG ngày 02/10 vì đúng lý do này. Peer nội địa
CMG/ELC cũng PE ~10–11 nhưng tăng trưởng thấp hơn. SOTP: LNST core 2026E ~8.456 [ƯỚC, FOX 2026 = TTM × 1,10 GĐ] ×
PE 10/12/14 + FOX → 57,0–60,2k / 66,8–70,1k / 76,7–80,0k.

## Đo / Ước / Giả định / Không tìm được

- **ĐO**: BQ `ticker_financial` FPT+FOX 2020Q4–2026Q2 (`bq_fin_fpt_fox.csv`); DNSE live 14/10 FPT 56.700 / FOX 55.400 /
  CMG 19.100 / ELC 11.450 (`dnse_live_raw.json`); BQ `ticker_1m` PE 13/10 (`bq_peer_pe.csv`); rf = 7,40%, rf MA12 =
  6,26% (`deposit_rate_vn.consumer_deposit_rate`, 12 đầu tháng 11/2025–10/2026: 5,2→7,5); cpi 5 năm 3,44% (⚠ cpi_vn
  báo khoảng trống 2026-09..12 là forward-fill), GDP thực dài hạn 6,22%.
- **ĐO thứ cấp (báo chí/CTCK)**: ACBS 23/03/2026 (EAT, đóng góp FOX, tiền ròng, kế hoạch mảng); KQKD H1/26 16/07
  (Mekong ASEAN, CafeF); tỷ lệ 45,66% / Bộ Công an 50,17%.
- **ƯỚC**: core = hợp nhất cũ − FOX (bỏ qua nội bộ); LNST core; DSO core; cổ tức FOX→FPT 675 tỷ.
- **GĐ**: chiết khấu FOX 0/15/30%; FOX 2026 = TTM × 1,10; ERP 6,5/7,5/8,5%; g_T theo 3 mode production.
- **KTĐ**: BCTC kiểm toán 2025 + thuyết minh gốc; tách gửi tiền kỳ hạn khỏi capex trong CF_Invest; dòng tiền thuế;
  ngày trả cổ tức FOX 2025; KQKD 9T/2026 (chưa công bố).

## File
`PREREG.md` (khai trước) · `fpt_deconsol_dcf.py` → `out_fpt_deconsol.txt`, `matrix_fv.csv` (48 ô), `labels_fv.csv`,
`cashflow_scope.csv` · input `bq_fin_fpt_fox.csv`, `bq_peer_pe.csv`, `dnse_live_raw.json`, `src_acbs_flashnote_20260323.pdf`.
Control: FCFE legacy tái tạo 6.336 tỷ vs production 6.335 (khớp).
