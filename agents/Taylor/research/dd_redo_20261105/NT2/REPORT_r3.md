# DD REDO VÒNG 3 — NT2 (Điện lực Dầu khí Nhơn Trạch 2, HOSE) · job `Taylor_20261108_153742` · 08/11/2026

> Chỉ NGHIÊN CỨU, không khuyến nghị. Áp `../TOP5B_CORRECTIONS_20261108.md` (mục NT2, 6 điểm) + `../STANDARD_r2.md`. Số: `calc_r3/model_r3.py` → `calc_r3/model_r3_out.txt/json`; `calc_r3/make_summary_r3.py` → `SUMMARY.json` (bản r2 lưu `SUMMARY_r2.json`). Giả định khoá ở `calc_r3/assumptions_r3.json`; `calc_r3/LOCK_md5.txt` (19 file đầu vào, gồm file giả định mới, dữ liệu BQ mới, model, thư viện) **chốt 22:41 ICT trước khi chạy model_r3** (lưu ý trung thực: `assumptions_r3.json` ghi 15:40 UTC, sau khi CSV giá 06/11 đã tải 15:38 UTC và giá đã nằm trong file đính chính — nên giả định KHÔNG được khoá mù trước mọi tiếp xúc với giá; LOCK_md5 sửa sau khi chạy để bổ sung `cctg_rate_vn.py` + `cctg_rate_vn_events.csv` và làm mới md5 text-only của `assumptions_r3.json`/trình bày). Chạy 2 lần trùng byte (`run1.md5` = `run2.md5`; SUMMARY 2 lần trùng md5).
> Số BCTC giữ nguyên r2 (BCTC riêng 30/09/2026, `src/Q3_2026_hopnhat_va_giaitrinh.pdf`). Giá tham chiếu **22.200 đ** = đóng cửa 06/11/2026 (BQ `tav2_bq.ticker`, `calc_r3/px_nt2_r3_20261106.csv`; đã ex-div 1.000 đ GDKHQ 29/10). r = 13,5% + 1,0×(7,40% − 7,40%) = **13,50%** (CCTG 12M 02/11/2026). Đơn vị tỷ đồng.

## 0. Kết luận — headline ở cỡ CK tham chiếu 5 tỷ (ADV250)

| | đ/cp |
|---|---|
| **Tâm** = kỳ vọng có trọng số của lưới (trước / sau CK 0,92%) | 24.226 / **24.003** |
| **P50** kết cục (sau CK) | 24.075 |
| Giá trị tại tham số trung tâm (LNST 800, 10 năm, r 13,5%, FCF = LNST; sau CK) | 24.211 |
| **P10 / P90** kết cục (sau CK) | **18.301 / 29.619** |
| n kết cục · % trọng số dưới giá · kết cục thấp nhất | 225 · **35,7%** · 14.624 |
| Giá 22.200 so tâm | **−7,5% ⇒ TRONG vùng** (nhãn không đổi so r2) |

**Cỡ sleeve thật** (10–40 triệu; NAV SpaceX ≈ 0,94 tỷ): CK 0,04–0,08% ⇒ tâm **24.206–24.216**, nhãn không đổi.
**So r2**: tâm 23.617 → 24.003 (**+1,6%**, +386 đ). So vùng cũ 26/10 (25.400, cum-div): −5,5%. Khoảng skeptic 23.400–24.300 (điểm 24.111) chứa tâm r3; chênh −108 so điểm skeptic là do giải phóng vốn lưu động ở t=1 năm thay vì t=0 (§2 đ.2).
Ba con số (điều 4): tâm 24.003 ≈ P50 24.075 ≈ tham số trung tâm 24.211 — lệch <1%, lưới đối xứng; không có nhánh trọng số nhỏ nào quyết định P10/P90. Kết cục thấp nhất 14.624 = LNST 450 × 5 năm × r 14,5% × FCF −150.

## 1. Cầu r2 → r3 (`bridge_r2_to_r3`)
| Bước | Tâm sau CK | Δ | P10 / P50 / P90 | n | % trọng số < 22.200 |
|---|---|---|---|---|---|
| 0 r2 tái lập (giá + CK 04/11) — **khớp r2 trùng số** | 23.617 | — | 18.386 / 23.669 / 28.278 | 45 | (37,5% @22.650) |
| 1 giá + CK 06/11 (đ.3) | 23.618 | +0 | 18.386 / 23.669 / 28.278 | 45 | 32,5% |
| 2 trục thời hạn 5/8/10/12/15 (.1/.2/.4/.2/.1) (đ.1) | 23.475 | −142 | 18.088 / 23.498 / 28.470 | 75 | 36,0% |
| 3 NWC chuẩn hoá theo DT 7.137, phần dư giải phóng t=1 (đ.2) | 24.003 | +528 | 18.491 / 24.045 / 29.169 | 75 | 32,5% |
| 4 trục FCF − LNST ±150 (.25/.5/.25) (đ.4) = **HEADLINE** | 24.003 | +0 | 18.301 / 24.075 / 29.619 | 225 | 35,7% |
Giá/tâm r2 ở giá 06/11: 22.200/23.617 − 1 = **−6,0%** (skeptic đúng; r2 ghi −4,1% ở giá 04/11).

## 2. Kiểm từng đính chính (không chép mù)
| # | Kết luận | Bằng chứng calc |
|---|---|---|
| 1 Thời hạn chỉ mở phía tăng | **ĐÚNG — áp** | Tái lập tâm 23.475 / P10 18.088 trùng skeptic (bước 2). Chiều giảm có nguồn: khí mỏ hiện hữu cạn ~2030 [WEB-2], PPA gốc 2011–2020, sau 2020 chưa xác minh (`dd_blind_NT2_20261026/CYCLE_BLOCK.md` mục C–D). Chiều tăng cũng có nguồn: GSA 25 năm ký 2010 (~2035), PL13 bổ sung khí Hải Thạch–Mộc Tinh 2026–2039 (chờ ĐHCĐ) ⇒ lưới đối xứng 5–15 là headline. Nút 4 năm trọng số 0,2 (skeptic) chỉ là song song A: tâm **23.139** trên lưới r3 đầy đủ (skeptic 22.780 trên khung r2 chưa chuẩn hoá NWC). |
| 2 NWC 837 khoá ở mức đỉnh DT | **ĐÚNG về hướng, sửa thời điểm** | Thêm cơ sở dữ liệu: phải thu/DT TTM ổn định **37–49%** 2022Q1–2026Q3 (BQ `AR_P0`, `calc_r3/ar_nt2_r3.csv`) ⇒ NWC tỷ lệ theo DT; DT 9T/26 năm hoá 10.404 (TTM 10.325) vs DT chuẩn hoá 7.137 mà dòng LNST đang dùng ⇒ NWC chuẩn hoá 837,2 × 7.137/10.404 = **574,3**, dư **262,9**. Giải phóng ở t=1 năm (vòng quay phải thu ~5 tháng), không phải t=0 ⇒ +528 (skeptic +646). |
| 3 Giá 22.200 | **ĐÚNG — áp** | BQ đóng cửa 06/11 = 22.200; % dưới giá trên lưới r2 = 32,5% (trùng skeptic). |
| 4 FCF = LNST thiếu cơ sở | **ĐÚNG — và dữ liệu có sẵn chỉ ra chiều XUỐNG** | Capex BQ (`CF_Invest_P0`): 2,5 tỷ 9T/26, 1,2–10,6 tỷ/năm 2015–26 — xác nhận. `CF_OA_P0` đã có trong `calc_r3/fin_nt2_r3.csv`: (CFO + CFI − LNST) 2022/2023/2024 = 498,5 / 358,7 / 441,3 ⇒ TB **~433/năm**, so khấu hao lịch sử ~550/năm (556 trước khi hết khấu hao) ⇒ phần dư **~−110/năm** (2025: −136; 2026 9T: +252). ⇒ nút −150 **CÓ cơ sở dữ liệu**, không phải [UL] thuần; câu “dữ liệu nghiêng LÊN (+110)” ở bản trước bỏ sót CFO và đã bị bỏ. Chiều lên (+110…+150) chỉ đúng nếu khấu hao còn 115–153/năm (sau khi hết khấu hao máy chính) > capex và đại tu tiền mặt ≈ phân bổ trả trước (bản D, 25.975) — **chưa kiểm**: lịch sử chi phí trả trước 2015–25 không có trong BQ, mã 271 hiện 262,9. ⇒ Trục đối xứng ±150 vào lưới (tâm không đổi, P10 −190, P90 +450); base FCF = LNST giữ nguyên (gốc 0 vẫn là điểm trung tâm của lưới đối xứng). Bản +110 base (D) chỉ là độ nhạy. ±150 tỷ/năm = **±2.772 đ/cp** ở 10 năm (hệ số niên kim 10 năm 5,320 @13,5% ⇒ 798 tỷ / 287,9 tr cp; không phải 2.746) — trục lớn nhất, xem §8 mục 9. |
| 5 LNST 800 chỉ neo CTCK | **ĐÚNG — thêm dòng cơ sở** | Tái lập: biên LNST TB/trung vị 2015–25 = **10,39% / 10,20%** × 7.137 = **742 / 728**; 9T/26 906/7.803 = 11,6% ⇒ **829** (`calc_r3/fin_nt2_r3.csv`). 800 nằm trong khoảng 728–829 ⇒ giữ. Song song E (735) / F (829). Lập luận biên EBITDA ở ADDENDUM_5F không dùng để nâng tâm (đồng ý skeptic). |
| 6 WARNING thiếu | **ĐÚNG — áp** | §6 mục 7–8. Ghi thêm: BQ `NP_P0` 9T/26 = 1.002 vs BCTC 906 (chênh 96 ≈ phần soát xét H1 chưa cập nhật vào BQ). |

## 3. Lưới (điều 1–2)
- 4 trục, mỗi ô = 1 kết cục tất định ⇒ phân vị trên 225 ô bằng `_shared/wpct.py`, trọng số = tích trọng số trục.
- **Có trong lưới (cả hai chiều)**: LNST chuẩn hoá {450; 625; 800; 975; 1.150} (0,1/0,2/0,4/0,2/0,1) [UL, cơ sở 728–829 ở §2]; thời hạn {5; 8; 10; 12; 15} năm (0,1/0,2/0,4/0,2/0,1) **mới r3**; r {12,5; 13,5; 14,5}% (¼–½–¼); FCF − LNST {−150; 0; +150} tỷ/năm (¼–½–¼) **mới r3** [UL].
- **Loại + cơ sở + bản song song**:

| Trục loại | Lý do | Bản CÓ trục |
|---|---|---|
| Nút 4 năm (khí cạn 2030, không PL13) | chiều tăng PL13 2026–2039 cũng có nguồn; giữ lưới đối xứng | A: tâm 23.139, P10/P90 17.956/28.941 |
| NT5 dùng tiền NT2 | luật dự án mới 03/11 ⇒ NPV 0 ⇒ bản có trục = bản không trục | — |
| Rủi ro đối tác tiền gửi SHB | không có thuyết minh tiền gửi theo NH | WARNING, không lượng hoá |
| Giá trị sau thời hạn > 0 (WIDE moat) | moat NONE (`ADDENDUM_5F.md`) | độ nhạy WIDE trong ADDENDUM (trên khung r2) |

## 4. Headline vs biến thể song song (`headline_vs_alternatives`; sau CK 5 tỷ, nhãn so giá 22.200)
| Bản | Tâm | P10 / P50 / P90 | % < giá | Nhãn |
|---|---|---|---|---|
| **HEADLINE r3** | **24.003** | 18.301 / 24.075 / 29.619 | 35,7% | TRONG |
| A nút 4 năm trọng số 0,2 (skeptic) | 23.139 | 17.956 / 22.788 / 28.941 | 46,0% | TRONG |
| B không chuẩn hoá NWC (837 thu hồi cuối hạn) | 23.475 | 17.773 / 23.499 / 29.060 | 40,2% | TRONG |
| C không trục FCF | 24.003 | 18.491 / 24.045 / 29.169 | 32,5% | TRONG |
| D FCF base +110 (khấu hao − capex, đại tu ổn định) | 25.975 | 20.215 / 25.918 / 31.778 | 19,6% | TRONG |
| E LNST neo lịch sử 735 | 22.838 | 17.078 / 22.875 / 28.399 | 44,6% | TRONG |
| F LNST neo 9T/26 829 | 24.523 | 18.808 / 24.593 / 30.189 | 32,3% | TRONG |
| G thời hạn r2 8/10/12 | 24.155 | 18.283 / 24.205 / 29.424 | 34,4% | TRONG |
Nhãn TRONG ở mọi biến thể; tâm dao động 22.838–25.975. Giá cách P10 ≥ 1.985 đ (gần nhất: bản D, P10 20.215) và cách P90 ≥ 6.199 đ (bản E) ở mọi bản ⇒ không ở ranh giới.

## 5. Giá ngụ ý (`implied_by_price`) & cross-check
- Ở giá 22.200 (= giá trị sau CK): thị trường tính **LNST cố định ~690 tỷ/năm trong 10 năm** (NWC chuẩn hoá; 720 nếu giữ NWC 837 cuối hạn), hoặc LNST 800 trong **~7 năm**, hoặc r ngụ ý **18,0%** ở tham số trung tâm. Net cash 11.398 đ/cp = **51% giá**. (Skeptic: ~720 cố định 10 năm hoặc 800 ~8 năm — khớp bản NWC 837; bản chuẩn hoá NWC kéo xuống 690 / 7 năm.)
- 690 thấp hơn cận dưới cơ sở lịch sử 728 ⇒ giá đang định giá dưới biên LNST lịch sử, nhưng phần chênh nhỏ hơn 1 nấc lưới.
- Gordon g=0 vô hạn (cận trên, bỏ qua thời hạn PPA): có lãi tiền gửi **20.585**; không lãi tiền gửi + net cash **27.649**; ROE có lãi 15,6%, ROE vận hành 34,3% (artifact khấu hao hết — ADDENDUM_5F §2). Lưới nằm giữa hai biến thể.

## 6. Thanh khoản (điều 6)
| Cỡ | ADV 250 phiên (17,8 tỷ; σ 1,73%) | ADV 60 phiên (13,8 tỷ; σ 1,39%) |
|---|---|---|
| 10 / 20 / 40 triệu (sleeve thật) | 0,04% / 0,06% / 0,08% | 0,04% / 0,05% / 0,07% |
| 1 tỷ | 0,41% (Q/ADV 5,6%) | 0,37% (7,2%) |
| **5 tỷ (tham chiếu headline)** | **0,92% — Q/ADV 28,1%, NGOÀI vùng hiệu chỉnh ≤10%** | 0,83% (36,2%, ngoài) |
Vùng hiệu chỉnh ≤10% ADV là quy ước job [UL]; ở 5 tỷ luật căn bậc hai là ngoại suy.

## 7. Độ nhạy r theo lãi huy động (tâm sau CK, lưới đầy đủ)
β=1: −100bp 24.528 (+2,2%) · −50bp +1,1% · +50bp −1,0% · +100bp 23.513 (−2,0%). β=0,5: +1,1% / +0,5% / −0,5% / −1,0%.

## 8. ⚠️ WARNING pháp lý/quản trị/số liệu — không loại, không trừ base
1. **Xung đột lợi ích POW (59,4%)**: chia cổ tức hay giữ tiền cho NT5; quỹ đầu tư phát triển 791,2 gắn NT5 [elibook 22/10/2026]. NPV 0 ở base.
2. **Tiền gửi tập trung SHB** [Vietstock, DD 26/10] — chưa đối chiếu thuyết minh.
3. **Lịch sử số liệu**: đính chính BCTC Q4/2022; phạt thuế 10,6 tỷ (2020); TTCP QHĐ VII (lịch sử); ĐHCĐ 28/05/2026 miễn nhiệm 1 TV BKS (lý do chưa rõ).
4. **NQ HĐQT 08/07/2026** lấy ý kiến cổ đông về Phụ lục 13 HĐ mua bán khí PV Gas [24hmoney] — nội dung chưa đọc; là mốc xác minh trục thời hạn.
5. "Chưa thấy vụ việc pháp lý đang mở chạm tài sản lõi": nguồn = báo chí trong DD 26/10/2026 + web search 05/11/2026 (r2 §6); **không tra lại trong r3**.
6. Rating 8L = 3 là kết quả cơ học `power_lens.csv` cũ (08-28) — không phải cờ chất lượng.
7. **Hạn PPA — 2 nguồn mâu thuẫn** (MỚI r3): ~2036 (substack, 1 nguồn) vs PPA gốc 2011–2020 (MBS 2016), trạng thái sau 2020 **chưa xác minh**; khí mỏ hiện hữu cạn ~2030. Trục thời hạn 5–15 phủ cả hai chiều; nút 4 năm ở song song A.
8. **Số Q3/2026 tự lập, chưa soát xét** (MỚI r3); tiền lệ soát xét bán niên 2026 giảm LNST ~94 tỷ do chi phí bảo trì định kỳ ghi thiếu ⇒ 9T/26 có thể còn bị điều chỉnh khi kiểm toán năm.
9. **FCF chiều xuống — có cơ sở một phần, chưa kiểm hết** (MỚI r3): (CFO+CFI−LNST) 2022–24 TB ~433/năm < khấu hao ~550 ⇒ phần dư ~−110/năm (nút −150 có cơ sở dữ liệu); lịch sử chi đại tu/chi phí trả trước 2015–25 chưa lấy nên độ lớn ±150 vẫn là [UL]; độ nhạy: mỗi ±50 tỷ/năm dịch base ±924 đ/cp ở 10 năm (tuyến tính; ±150 = ±2.772).

## 9. Mốc đổi nhận định (hai chiều) + HARD ABANDON
| Mốc | Ngày chấm | Lên | Xuống |
|---|---|---|---|
| Qc 2027 phân bổ | ~31/12/2026 | Qc ≥ 2026 ⇒ LNST ~1.000 | Qc giảm mạnh ⇒ LNST 450–625 |
| BCTC Q4/2026 + kiểm toán năm | 31/01 & ~03/2027 | LNST Q4 ≥150, CFO dương, không soát xét giảm | điều chỉnh giảm 9T; phải thu EVN > 5.000 |
| Phụ lục 13 GSA / BCTN: thời hạn PPA-GSA | khi đọc được | >2036 ⇒ nhánh 12–15 năm | PPA hết hạn/không gia hạn ⇒ nhánh 4–5 năm (song song A) |
| Lịch sử chi phí trả trước đại tu (BCTC năm) | khi lấy được | khấu hao 115–153 > capex và đại tu tiền mặt ≈ phân bổ ⇒ bản D (FCF base +110, tâm 25.975) | đại tu > phân bổ (phần dư ~−110/năm như 2022–24) ⇒ nhánh −150 |
| ĐHĐCĐ 2027 | 30/04/2027 | cổ tức tiền ≥1.500 đ | phần lớn tiền vào NT5 khi chưa có cơ chế giá LNG |
**HARD ABANDON**: (a) quyết định chuyển tiền/cho POW hoặc bên liên quan vay không lãi/không bảo đảm; (b) kết luận thanh tra/khởi tố chạm pháp nhân NT2; (c) tiền gửi bị phong toả/không rút được. Cỡ sleeve 10–40 tr ⇒ không cần chia tranche.
**Sleeve fear-buy §2.5: KHÔNG đủ điều kiện** — không có khủng hoảng; giá ≈ tâm (−7,5%). Chỉ xét lại khi giá ≤ ~18.300 (P10) mà net cash ≥3.000 tỷ và không có quyết định rót vốn NT5.

## 10. Giả định khoá (`assumptions`, file `calc_r3/assumptions_r3.json`)
r 13,50% (công thức neo) · giá 22.200 (06/11, BQ) · số BCTC 30/09/2026 giữ r2 · LNST tâm 800 (5 mức, cơ sở 728–829) · thời hạn 5–15 · NWC chuẩn hoá 574,3 + giải phóng 262,9 t=1 · FCF − LNST ±150 tâm 0 · giá trị sau thời hạn 0 · CK 5 tỷ ADV250 (Y=1). Mỗi mục có basis + source trong `SUMMARY.json.assumptions`.

## 11. Mở
Thời hạn PPA/GSA (Phụ lục 13 chưa đọc) · lịch sử chi phí trả trước đại tu 2015–25 · công thức pass-through · Qc 2027 · thuyết minh tiền gửi theo NH, phải thu EPTC quá hạn. Chưa qua phản biện cuối (Mike chạy). Không ghi `kb/dd_price_zones.json`.
