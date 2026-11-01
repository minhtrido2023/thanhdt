# Hiệu chuẩn DCF cho thị trường VN — 3 vấn đề (job Taylor_20261101_155145, 01/11/2026)
R&D, KHÔNG wire production, không sửa default `dcf_valuation.py`. PREREG `ff2272e90` (22:55 ICT, trước mọi số).
Mọi số dưới đây đo trong phiên; nguồn ở `out/run_*.txt` + `out/*.csv`. Engine tái lập `fair_value` (domestic_v2,
OShares quý) **lệch 0 VND** trên 400 cặp ngẫu nhiên (189 ok / 211 NOT_COMPUTED khớp cả hai phía) và V0 của bảng
biến thể = engine (lệch tương đối max 0,0) — `SELFCHECK.md`.

## Khuyến nghị tham số VN

| Hạng mục | Hiện tại | Đề xuất | Bằng chứng chính | Loại |
|---|---|---|---|---|
| Lịch chạy | cron ngày 11 hằng tháng + trigger lãi suất ≥1pp (dưới domestic_v2 r hằng ⇒ trigger **no-op**) | Lượt quét toàn universe **15/02, 15/05, 15/08, 15/11** (sau p95 công bố + ~2 tuần nạp vendor) + lượt sớm 05/02, 05/05, 03/08, 03/11. Không chạy lại FV giữa quý; MoS tính lại theo giá mỗi lần dùng (đã là hành vi `dcf_check`). Cờ **STALE khi tuổi BCTC > 105 ngày** | §1 | vận hành |
| Beta | không có (r = 12,25% mọi mã) | **Không đưa beta vào xếp hạng MoS.** Nếu cần Ke hiển thị theo mã: β Blume (0,67β+0,33) **ngày, 1 năm, vs VNINDEX**, dùng dạng tương đối β/median, kẹp **0,6–1,6** | §2 | display |
| Số giai đoạn | 2 tầng, tường minh 5 năm | Thực chất **1 tầng** (khi shrink = 0, N không còn tác dụng). 3 tầng / H-model / N = 3,7,10 không cải thiện gì | §3b | level |
| Tăng trưởng giai đoạn 1 | TB 3 năm, shrink 0,5 về g_T, kẹp [−2%, +20%] | **shrink 0** (g_exp = g_T); chấp nhận được tới 0,25 | §3a, §3b | level (IC trung tính) |
| g ổn định | min(CPI+GDP, 5,5%) — cap chạm 100% số tháng | **4,5%** (LOYO 4,25–4,75; IS-only 4,0; OOS-only 5,0) | §3d | level |

**Hiện tại vs đề xuất** (universe_pit phi tài chính, cuối tháng 2013-12 → 2026-10; live = 30/10/2026, 147 mã tính được):

| Bộ | Trung vị P/FV lịch sử (IS / OOS) | Khoảng theo năm | % RẺ lịch sử | Live: FV trung vị vs hiện tại | Live % RẺ | Live RICH sâu | IC12 (IS / OOS) | ΔIC12 vs hiện tại [CI95 khối năm] |
|---|---|---|---|---|---|---|---|---|
| **Hiện tại** (s 0,5, N5, g_T 5,5) | 0,795 (0,742 / 0,844) | 0,46–1,00 | 58,4 | — | 67,3 | 27 | 0,065 (0,053 / 0,078) | — |
| s = 0, g_T 5,5 | 0,883 (0,847 / 0,916) | 0,52–1,09 | 54,3 | −25,7% | 57,8 | 32 | 0,062 (0,049 / 0,075) | −0,0035 [−0,011; +0,005] |
| **Đề xuất: s = 0, g_T 4,5** | **1,024 (0,982 / 1,062)** | 0,60–1,26 | 49,3 | **−35,9%** | **53,1** | **36** | 0,062 (0,049 / 0,075) | −0,0035 [−0,012; +0,005] |
| Hiện tại + beta tương đối 0,6–1,6 | 0,759 | 0,48–0,96 | 58,9 | 0,0% | 67,3 | 26 | 0,084 (0,084 / 0,084) | +0,019 [+0,001; +0,037]; **OOS +0,006** |

Lật trạng thái live dưới đề xuất: 21 mã RẺ→ĐẮT, 0 mã ĐẮT→RẺ (đo `fv_variants.parquet` t = 2026-10-30).

**Đọc dứt khoát:**
1. **Đề xuất là LEVEL/DISPLAY fix, không phải alpha** — đúng tiền lệ 07-2026. Nó đưa trung vị P/FV về ≈ 1 (hết thiên lệch
   "đọc mọi thứ RẺ"), nhưng IC không cải thiện (−0,0035, CI chứa 0). Lý do nên đổi là sai số dự báo cơ bản thấp hơn (§3b)
   và level đúng hơn, KHÔNG phải vì sinh lời.
2. **Beta riêng không qua cổng khai trước** (OOS ΔIC ≥ +0,01): OOS chỉ +0,006. Phần tăng IC ở IS (+0,031) gần như toàn bộ
   là hiệu ứng low-beta trộn vào: −β một mình có IC12 0,080 (IS 0,135 / OOS 0,023); MoS-beta sau khi trung hoà β có IC12
   0,0685 so với MoS hiện tại trung hoà β 0,0651. Một tổ hợp thẳng rank(MoS) + 0,5·rank(−β) cho 0,0985 — tức nếu muốn
   khai thác low-beta thì làm như MỘT YẾU TỐ RIÊNG, không giấu trong r của DCF (đề xuất R&D riêng, chưa kiểm OOS đủ).
3. **Thời điểm chạy không phải nút thắt của tín hiệu** — IC MoS không giảm theo tuổi BCTC. Nút thắt thật là FV nhảy trung
   vị ~20% (log) mỗi lần có BCTC mới và vendor trễ 1–2 tuần.

## 1. Vấn đề 1 — thời điểm chạy (`timing.py`, `out/run_timing.txt`)

**(a) Ngày công bố.** `Release_Date` có ở 18.521/18.670 dòng universe 2014+ (149 NULL). Trễ (ngày sau cuối quý):

| Kỳ | Q1 p50/p95 | Q2 p50/p95 | Q3 p50/p95 | Q4 p50/p95 | % ≤ 45 ngày |
|---|---|---|---|---|---|
| 2014-19 | 33 / 35 | 32 / 34 | 31 / 34 | 32 / 33 | ≥ 99,9% |
| 2020+ | 27 / 34 | 32 / 34 | 28 / 32 | 28 / 38 | 100% |

Ngày lịch đạt 50/80/95% (2020+): Q1 27/04 · 04/05 · 04/05; Q2 01/08 · 01/08 · 03/08; Q3 28/10 · 31/10 · 01/11; Q4 28/01 · 02/02 · 07/02.
- Vendor ghi BCTC **quý** (hạn TT96: 20 ngày riêng lẻ / 30 ngày hợp nhất), KHÔNG ghi bản soát xét bán niên (45 ngày) hay
  kiểm toán năm (90 ngày) thành dòng riêng. Giả định (chưa kiểm): bản kiểm toán Q4 nếu có thì ghi ĐÈ dòng cũ — rủi ro
  look-ahead nhỏ chưa đo.
- 2014-19, 34,3% dòng có trễ **đúng 32 ngày** (01/02, 02/05, 01/08, 01/11) ⇒ phần lớn là ngày vendor chụp, không phải ngày
  công bố thật. Với hệ thống này đó vẫn là ngày PIT đúng (ngày dữ liệu có thể dùng).
- **Trễ nạp vendor** (so vintage 07-28/07-29 với 10-30): dòng công bố 0–7 ngày trước vintage chỉ có 66–73%; 8–14 ngày 88–92%.
  Vintage 30/10/2026: **166/339** mã universe đã có 2026Q3 (Q2: 339/339) — nửa universe còn đang đọc BCTC Q2.

**(b) Suy giảm theo tuổi BCTC** (tuổi = t − ngày dòng mới nhất; phân bố p50 43, p95 91, p99 100 ngày; > 125 ngày: 0%):

| Tuổi | n | Sai số NP 1 năm (trung vị \|log\|) | lệch so TB cùng mã×năm | Sai số FCFE | IC3 MoS gộp (OOS) [CI] | IC12 gộp |
|---|---|---|---|---|---|---|
| 0–30 | 7.498 | 0,301 | −0,007 | 0,721 | 0,024 (0,027) [−0,014; 0,057] | 0,055 |
| 31–60 | 6.940 | 0,311 | +0,005 | 0,721 | 0,015 (0,017) [−0,018; 0,045] | 0,056 |
| 61–90 | 5.170 | 0,310 | +0,001 | 0,719 | 0,027 (0,049) [−0,003; 0,063] | 0,061 |
| > 90 | 1.366 | 0,317 | +0,010 | 0,713 | 0,054 (0,081) [−0,002; 0,116] | 0,096 |

Sai số cơ bản tăng rất ít theo tuổi (+0,016 log từ nhóm tươi nhất tới cũ nhất); IC **không** giảm (nhóm cũ còn cao hơn, CI
chồng nhau — không kết luận là "cũ tốt hơn"). Tuổi trùng gần như hoàn toàn với tháng lịch (tuổi trung vị: tháng 1/4/7/10 ≈ 10
ngày; tháng 3/6/9/12 ≈ 60), nên phép đo này ≈ "IC theo tháng trong quý".

**(c) Ai làm MoS đổi.** Biến đổi tháng của log(P/FV): var(ΔlogP) 0,023 vs var(ΔlogFV) 0,122 ⇒ phần giá chỉ ~16%. FV đổi ở
20% số tháng (chỉ khi có dòng BCTC mới; g_T bị cap 5,5% ở 100% số tháng nên không đổi theo CPI), và khi đổi thì trung vị
|ΔlogFV| = 0,196 (p75 0,457); giá chỉ 0,060/tháng.

**Lịch đề xuất:** quét đầy đủ 15/02 · 15/05 · 15/08 · 15/11 (p95 công bố + 14 ngày trễ vendor), lượt sớm 05/02 · 05/05 · 03/08 ·
03/11 cho các mã đã có. Thay cron ngày 11 (không khớp mùa nào: 11/08 và 11/11 vẫn trước khi vendor nạp đủ) — trigger lãi suất
hiện no-op vì r hằng. Không chạy lại FV giữa quý: giá đã vào MoS mỗi lần dùng, và "sự kiện lớn" duy nhất làm FV đổi giữa quý
là số CP (đã có nhánh OShares live). Cờ **STALE > 105 ngày** (p99 tuổi = 100) để đánh dấu mã nộp muộn/vendor thiếu — cờ
**chất lượng dữ liệu**, không phải vì tín hiệu suy giảm (không đo được suy giảm).

## 2. Vấn đề 2 — beta (`beta.py`, `beta_eval.py`, `out/run_beta_eval.txt`)

98 biến thể = tần suất {ngày, tuần W-FRI, tháng} × cửa sổ {1,2,3,5 năm} × {OLS, Blume, Vasicek, Dimson (−1..+1), Scholes-
Williams (ngày)} × {VNINDEX, VN30} + bottom-up ngành ICB2 + hằng 1. VNALL KHÔNG có trong dữ liệu (không thay thế). 49 quý
2013Q4–2025Q3, 14.222 cặp chung (mọi biến thể đánh giá trên cùng cặp có đủ 5Y ngày). "Sự thật" khai trước = beta Dimson tuần
(lag 0,1) 12 tháng kế tiếp.

| (OOS 2020+, 24 quý) | Spearman vs beta thật tuần | vs thật ngày | Spearman vs lợi suất tuần VNINDEX giảm | MSE mức | IS Spearman |
|---|---|---|---|---|---|
| **Ngày 1Y Blume VNINDEX** | 0,501 | 0,683 | −0,466 | **0,433** (thấp nhất) | 0,438 |
| Ngày 1Y Vasicek | 0,504 | 0,688 | −0,471 | 0,453 | 0,443 |
| Ngày 2Y Blume | 0,480 | 0,668 | −0,438 | 0,467 | 0,431 |
| Tuần 2Y Vasicek | 0,466 | 0,617 | −0,438 | 0,510 | 0,405 |
| Ngày 1Y Dimson / SW | 0,481 / 0,483 | 0,619 / 0,623 | −0,448 / −0,451 | 0,504 / 0,498 | 0,396 / 0,398 |

TB theo chiều (OOS): ngày 0,457 > tuần 0,427 > tháng 0,402; 2Y MSE thấp nhất trung bình, 5Y kém nhất (lệch −0,203);
VNINDEX 0,440 > VN30 0,427 (VN30 lệch mức −0,17). Hiệu chỉnh giao dịch thưa (Dimson/SW) **không** cải thiện xếp hạng — lệch
mức gần 0 nhưng MSE cao hơn Blume. Pha hạ (Spearman beta trước pha vs lợi suất pha; âm = đúng):

| Pha | VNINDEX | Ngày 1Y OLS | Tuần 2Y Vasicek | Ngày 2Y Dimson | Bottom-up ngành |
|---|---|---|---|---|---|
| 04/2018–07/2018 | −25,3% | **−0,470** | −0,342 | −0,339 | −0,106 |
| 01/2020–03/2020 | −32,6% | **−0,378** | −0,348 | −0,364 | +0,056 |
| 04/2022–11/2022 | −40,2% | **−0,514** | −0,365 | −0,345 | −0,114 |

Mức beta không ổn định giữa các thời kỳ: trung vị beta thật 0,69 (IS) vs 0,99 (OOS); 30/09/2026 Blume 1Y trung vị 0,72
(p5 0,38, p95 1,02). Dùng β THÔ trong r làm FV trung vị nhảy +30% tại 30/10/2026 chỉ vì cả thị trường có β thấp năm qua ⇒
nếu dùng thì dùng **β tương đối** (β/median; p5 0,53, p95 1,41 hôm nay) để không trôi mức. Sàn/trần PREREG (p5/p95 beta
thật = 0,05/2,37 ở lần chạy 23 quý dùng cho bảng biến thể; lần chạy cuối 49 quý 0,03/2,34) cho r 7,0–19,8% — quá rộng cho Gordon; kẹp 0,6–1,6 cho kết quả IC gần như nhau (bảng biến thể).
`risk_rating.Beta` là **bin 1–5** (84% NaN), khớp tốt nhất với **beta ngày 5 năm** (Spearman 0,940, lệch 1 quý) ⇒ không
dùng được làm β cho Ke.

**Kết luận beta:** không dùng beta riêng cho xếp hạng (OOS ΔIC +0,006 < +0,01; phần tăng là low-beta, OOS low-beta chỉ 0,023).
Ke hiển thị theo mã (nếu muốn): ngày · 1 năm · Blume · VNINDEX · tương đối · kẹp 0,6–1,6.

## 3. Vấn đề 3 — giai đoạn & tăng trưởng (`growth.py`, `out/run_growth.txt`)

**(a) Tăng trưởng NP ở VN trở về trung bình NGAY trong 1 năm** (phi tài chính, năm tài chính 2009+, 12–16 năm):
- Tương quan hạng g năm t với t+1: **−0,092**; t+2 −0,108; t+3..5 ≈ 0 (−0,05…0,00). Top quintile còn top: 0,22 / 0,21 /
  0,21 / 0,26 / 0,22 (ngẫu nhiên = 0,20).
- Nhóm CAGR 3Y cao nhất (trung vị +65,6%/năm): năm sau **−2,5%**, rồi +1,3%, +6,6%, +5,5%, +4,9%. Nhóm thấp nhất (−39,6%)
  hồi +57,5% năm sau. Tỷ lệ NP ≤ 0 sau 5 năm: 12,4% (top) / 4,9% (giữa) / 21,2% (đáy).
- Không nhóm nào giữ tăng trưởng: top quintile theo ROE cao (−9,5% năm 1), quy mô lớn (−2,5%), chuỗi ≥ 4 năm liên tiếp
  g > 15% (P(năm sau > 15%) = 0,42 vs 0,38 nhóm chuỗi 0). Hồi quy g năm 1 lên g3 quá khứ: hệ số **−0,95 (IS) / −2,12 (OOS)**.
  ⇒ "nhóm tăng trưởng cao bền bao lâu": trung bình **< 1 năm**; không có giai đoạn tăng trưởng nhanh nào đo được.

**(b) Đường tăng trưởng vs NP thực** (Σ NP K năm sau / Σ dự, trung vị |log|; gốc dòng Q4 2009+):

| Biến thể | K=3 (IS / OOS) | K=5 (IS / OOS) | bias K=5 | FCFE K=5 |
|---|---|---|---|---|
| **s = 0 (g = g_T)** | **0,452** (0,479 / 0,428) | **0,502** (0,549 / 0,465) | +0,028 | 0,738 |
| s = 0,25 | 0,458 | 0,513 | −0,007 | 0,755 |
| H-model s 0,5 h2 | 0,466 | 0,518 | −0,024 | 0,766 |
| **Hiện tại s 0,5 N5** | 0,471 (0,499 / 0,458) | 0,530 (0,563 / 0,503) | −0,053 | 0,773 |
| 3 tầng s 0,5 N3 + fade 5 | 0,471 | 0,530 | −0,050 | 0,772 |
| s = 1 N5 (ngoại suy đủ) | 0,505 | 0,590 | −0,141 | 0,811 |
| g = 0 | 0,453 | 0,539 | +0,191 | 0,731 |

Ngoại suy càng nhiều càng sai và càng dự báo **quá cao** (bias âm), ở cả IS lẫn OOS, cả K = 3 lẫn 5, cả NP lẫn FCFE. Hậu
nghiệm (ngoài PREREG, +2 trial): đúng cả trong nhóm ROE5Y ≥ 20% (MAE K=5: s0 0,356 < s0,5 0,396 < s1 0,468); shrink có điều
kiện theo ROE làm IC12 kém hơn (0,056–0,060). Chưa bootstrap CI cho chênh MAE giữa s0 và s0,25 (0,011) — coi là ngang nhau.

**(c) g ổn định & nhất quán nội tại.** FCFE3Y/NP3Y trung vị **0,15** (ROE cao 0,45, ROE thấp âm) ⇒ doanh nghiệp VN tái đầu
tư ~85% lợi nhuận; g ngầm định ROE×(1 − FCFE/NI) trung vị 8,5%. Nếu ROE_T hội tụ về Ke 12,25%: g_T 4,5 cần FCFE/NI 0,63;
5,5 cần 0,55; 7 cần 0,43. Mô hình dùng base FCFE (đã trừ tái đầu tư hiện tại, tỷ lệ 0,15) rồi tăng ở g_T ⇒ terminal **thận
trọng hơn** công thức nhất quán, không cần trừ thêm. g_T 7% bị loại (vượt tương thích với ROE_T = Ke và đẩy level xa 1:
P/FV 0,63).

**(d) Level — chỉ hiệu chuẩn tổng thể.** Lưới g_T 3,0–8,0% bước 0,25 để TB log trung vị P/FV = 0:

| Cấu trúc | Toàn kỳ | IS-only | OOS-only | LOYO min–max |
|---|---|---|---|---|
| s 0,5 (hiện tại) | 3,25% | 3,00% | 4,00% | 3,00–3,50% |
| **s 0** | **4,50%** | 4,00% | 5,00% | **4,25–4,75%** |
| s 0,25 | 3,75% | 3,25% | 4,50% | 3,75–4,25% |

Giữ s 0,5 thì g_T phải 3,0–3,5% mới hết thiên lệch — thấp phi lý so với GDP danh nghĩa 8,8–16,5% ⇒ thiên lệch level hiện tại
chủ yếu đến từ **ngoại suy tăng trưởng**, không phải g_T. Với s = 0, g_T 4,5% (khoảng 4,0–5,0) là bộ ít tham số nhất đưa level
về 1. Năm lệch nhiều nhất còn lại (s0, g_T 5,5): 2013 −0,66, 2014 −0,36, 2015 −0,41, 2020 −0,34, 2026 −0,23 log — giai đoạn
lãi suất cao 2013-15 (r hằng 12,25% thấp hơn thực tế lúc đó) và cú sập 2020; tháng 10/2026 thị trường cũng đang rẻ so với mô
hình. Đây là cái giá có chủ đích của r hằng (domestic_v2), không chỉnh ở đây.

## 4. VNM và panel (`case.py`, `out/t4_case_*.csv`, `out/t4_case_panel.png`)

Panel PIT theo tiêu chí khai trước (top-30 vốn hoá phi tài chính 01/2014, ≥ 90% tháng trong universe, ≥ 80% tháng tính được):
BMP, DHG, DRC, FPT, GAS, LAS, VNM. Ngoài tiêu chí (theo yêu cầu): MWG, PNJ, DGC, REE, CTR.

| Mã | P/FV hiện tại (trung vị) | P/FV đề xuất (trung vị; p10–p90) | g ngầm định 1 tầng @r 12,25 | r ngầm định (đường hiện tại) | 30/10: giá / FV hiện tại / FV đề xuất |
|---|---|---|---|---|---|
| VNM | 1,53 | 1,82 (1,30–2,64) | 7,8% | 9,9% | 56.900 / 59.628 / 45.503 |
| FPT | 1,61 | 2,49 (1,17–3,66) | 9,0% | 9,7% | 52.700 / 69.472 / 45.299 |
| DHG | 1,76 | 2,08 | 8,4% | 9,3% | 86.900 / 73.534 / 74.410 |
| GAS | 1,13 | 1,43 | 6,7% | 11,5% | 78.000 / 57.816 / 55.548 |
| BMP | 0,79 | 1,00 | 4,5% | 14,1% | 137.500 / 224.902 / 188.293 |
| DRC | 0,74 | 0,81 | 2,8% | 14,6% | (tới 12/2024) |
| LAS | 0,64 | 0,74 | 2,0% | 15,8% | 11.400 / 5.975 / 5.318 |
| DGC* | 0,74 | 1,03 | 4,7% | 14,6% | 33.300 / 74.747 / 75.638 |
| MWG* / PNJ* / REE* / CTR* | 2,39 / 3,73 / 1,35 / 1,63 | 2,51 / 5,22 / 1,85 / 1,98 | 9,0 / 10,7 / 7,9 / 8,2% | 8,3 / 7,3 / 10,5 / 9,7% | |

\* ngoài tiêu chí. Giá = `Price` thô BQ; OShares quý (TRAP — xem §6).

**VNM** (tỷ số các trung vị năm, `out/t4_vnm_by_year.csv`): P/FV hiện tại 1,78–2,21 (2016–2019) → 1,45 / 1,32 (2024 / 2025). g ngầm định
giảm từ 8,9–9,2% (2016–19) về 6,2–6,7% (2022–26), cùng lúc tăng trưởng NP thực của VNM về ≈ 0/âm (g_raw +2,6% năm 2020 →
−8,1% năm 2023 → −2,7% năm 2025). Giá điều chỉnh
30/04/2018 → 31/12/2025: **×0,695** (VNINDEX ×1,699). Tức thị trường năm 2016–18 trả cho VNM một mức tăng trưởng ~9%/năm vô
hạn mà doanh nghiệp không đạt; DCF đọc "đắt" là đúng **về cơ bản**, và khoảng lệch thu hẹp khi giá điều chỉnh xuống. Phần lệch
còn lại hôm nay (P/FV đề xuất ~1,25) là thị trường vẫn trả ~6,3% tăng trưởng vĩnh viễn (ở r 12,25) / Ke ngầm định 10,1–11,9% (2022–26) cho một thương hiệu chi
trả cao, beta thấp — **không chỉnh tham số để xoá phần này** (sẽ làm MoS VNM = 0 theo cấu tạo).

**Ngược lại FPT**: mô hình đọc đắt (P/FV 1,6 hiện tại, 2,5 đề xuất) suốt kỳ, trong khi giá điều chỉnh ×6,43 (2018-04 → 2025-12).
Đây là giới hạn cố hữu: hiệu chuẩn trên TRUNG BÌNH (tăng trưởng trở về ngay) phạt nặng số ít doanh nghiệp compounder thật. Shrink
0 làm việc đó nặng hơn (FPT 1,61 → 2,49). Vì vậy dù sai số TB tốt hơn, IC giảm nhẹ (−0,0035) — chính là thông tin compounder
bị mất. Mẫu chung của panel: thị trường trả premium cho chất lượng/tăng trưởng (DHG, FPT, VNM, MWG, PNJ: P/FV > 1,5) và chiết
khấu cho chu kỳ/hàng hoá (DRC, LAS, BMP, DGC: < 1) — phù hợp kết quả RICH-outlook 24/10 (RICH sâu có NP Q+1 cao hơn).

## 5. N trials & DSR
- Beta: 98 biến thể chấm trên tiêu chí không phải giá; 3 biến thể beta vào bảng IC.
- Bảng IC: 23 biến thể (+2 hậu nghiệm ROE-shrink) ⇒ N = 25.
- DSR trên IC12 không chồng lấp (tháng 12 mỗi năm, T = 12): hiện tại 0,961; s0 0,929; s0,25 0,941; beta tương đối 0,987;
  s0 + beta 0,979. SR0 = 0,234. T = 12 điểm nên DSR kém phân giải; không dùng DSR để biện minh beta (đã có kiểm low-beta).
- Độ bền (loại 37,3% ticker-date có OShares đổi > 10% trong ±4 quý): IC12 hiện tại 0,076 (OOS 0,089), s0 0,069 (0,085),
  beta tương đối 0,100 (0,098) — thứ tự và kết luận không đổi (beta OOS +0,008 < +0,01).

## 6. Tự tấn công (chuẩn bị cho quant-skeptic)
1. **Level calibration = giả định thị trường đúng trung bình.** Mục tiêu median P/FV = 1 là quy ước; nếu VN định giá thấp hệ
   thống (room ngoại, NĐT cá nhân) thì g_T 4,5% đang "fit giá" ở cấp tổng thể. Đã giới hạn bằng LOYO + 1 tham số; vẫn là
   lựa chọn, không phải phát hiện.
2. **s = 0 biến DCF thành xếp hạng FCFE yield.** Với s = 0, MoS là hàm đơn điệu của F/P (F = FCFE 3Y bình quân/CP) — DCF
   không còn thêm gì ngoài lợi suất FCFE. Đó là hệ quả trung thực của dữ liệu (§3a), nhưng phải nói rõ: chiều "tăng trưởng"
   của mô hình hiện tại có IC dương nhỏ (s 0,75–1 cho IC3 cao hơn: 0,027–0,029 vs 0,025) dù dự báo cơ bản tệ hơn ⇒ hai tiêu chí
   chỉ hướng ngược nhau; tôi chọn tiêu chí không-phải-giá theo yêu cầu.
3. **Survivorship trong panel tăng trưởng**: chỉ dòng Q4 có NP > 0 đầu kỳ và đủ K năm sau ⇒ loại công ty biến mất/hủy niêm yết;
   12,4% top quintile có NP ≤ 0 sau 5 năm và bị loại khỏi MAE (đã báo tỷ lệ riêng). Panel tăng trưởng KHÔNG lọc universe_pit
   (dùng mọi mã phi tài chính có BCTC) — khác panel IC.
4. **OShares TRAP**: FV/CP dùng OShares quý bị restate; đã kiểm loại 37% ticker-date bất ổn — kết luận giữ, nhưng mức IC đổi
   (0,065 → 0,076) ⇒ có nhiễu từ số CP.
5. **Release_Date 2014-19 phần lớn là ngày vendor chụp (mode 32 ngày)** ⇒ §1 nói về "ngày dữ liệu có thể dùng", không phải ngày
   công bố pháp lý. Bản kiểm toán ghi đè dòng Q4: chưa đo.
6. **Tuổi BCTC trùng tháng lịch** ⇒ §1b không tách được "tuổi" khỏi mùa vụ trong quý. Không có cách tách với dữ liệu này.
7. **Beta "sự thật" chọn tuần Dimson** có thể thiên vị kỹ thuật tuần — vậy mà ngày vẫn thắng; ngược lại thì không chắc. Pha hạ
   chỉ 3 sự kiện (N = 3) ⇒ minh hoạ, không phải kiểm định.
8. **IC IS 2014-19 của bảng biến thể dùng giá từ 2013**; beta 5Y cho 2013–2014 dùng giá BQ 2008–2012 tải trong phiên
   (`data/px_2008_2012.csv`, kiểm nối 2012/2013 liên tục cho VNM, FPT, VNINDEX).
9. **Không đo**: tác động lên plan/LAG gate cụ thể từng mã (36 RICH sâu vs 27 là số universe, chưa giao với danh mục live);
   VNALL; benchmark beta theo sàn HNX/UPCOM; smoothing FV qua nhiều quý (ý tưởng từ §1c, chưa thử).

## 7. Những gì KHÔNG chứng minh được
- g_T không kiểm được bằng dữ liệu thực hiện (vĩnh viễn); 4,5% là level, khoảng 4,0–5,0.
- Không có bằng chứng beta riêng cải thiện định giá OOS; cũng không chứng minh được là KHÔNG có (CI ΔIC OOS chưa tính riêng,
  ước lượng điểm +0,006).
- Chạy theo mùa không làm tăng IC (đo không thấy suy giảm theo tuổi); lợi ích là vận hành (số liệu đầy đủ, không chạy lúc
  vendor mới nạp 49%).

## 8. Đề xuất code (chưa làm thay đổi production)
**Chưa viết code** (đổi level lớn, cần user quyết hướng trước). Nếu user muốn thử: knob `DCF_PARAM_SET` mặc định `v2` (byte-identical), `vn_v3` = GROWTH_SHRINK 0 + G_T 4,5% + trường
`fin_age_days`/`stale` (> 105 ngày). Lịch: thay cron `dcf_refresh_gate` ngày 11 bằng 4 lượt/năm ngày 15 tháng 2/5/8/11 — cần
user duyệt (§11 cron_registry). Cần quant-skeptic trước. Tác động đã đo: FV trung vị −35,9%, %RẺ 67,3 → 53,1, RICH sâu 27 → 36,
21 lật RẺ→ĐẮT — **lớn**, nên nếu bật phải kiểm cổng `DCF_RICH` của LAG và `dcf_override_reason` trên danh mục live trước.

## Tái lập
`$DNA_PYEXE engine.py build` → `engine.py selfcheck` → `timing.py` → `beta.py` → `beta_eval.py` → `growth.py` → `variants.py`
→ `robust.py` → `case.py` → `explore_roe_shrink.py`. Đầu vào: `data/bq_cache/*` vintage 30/10/2026 + `data/px_2008_2012.csv`
(BQ 01/11). `SELFCHECK.md`.
