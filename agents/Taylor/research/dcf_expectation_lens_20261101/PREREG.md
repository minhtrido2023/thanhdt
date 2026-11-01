# PREREG — Lăng kính kỳ vọng thị trường ("DCF nhẹ") — job Taylor_20261101_165940
Viết 02/11/2026 ~00:10 ICT, TRƯỚC khi chạy bất kỳ số nào của job này. R&D, không wire, không sửa `dcf_valuation.py`.
Nền: `../dcf_vn_calibration_20261101/` (engine, panel tháng, row_inputs; kết luận A: tăng trưởng NP VN mean-revert
trong < 1 năm, ngoại suy càng nhiều càng sai).

## 0. Dữ liệu (tra `kb/data_registry/` 02/11)
- `data/bq_cache/ticker_financial.parquet` (CANONICAL; vintage 30/10/2026): NP_P0..P7, Revenue_P0..P7, NPM_P0 (TTM —
  bẫy 10-28), ROE_Trailing, CF_*; ngày khả dụng PIT = `time` của dòng (như engine). `OShares` TRAP ⇒ KHÔNG tự tính
  vốn hoá/EPS; mọi tăng trưởng dùng TỔNG NP/doanh thu (không per-share).
- `data/bq_cache/ticker/*.parquet` (2013→30/10/2026): `PE`, `PCF`, `EVEB` (CANONICAL, cơ sở `Price` thô, PIT — KHÔNG nhân
  Price/Close), `Close` (điều chỉnh, cho lợi suất), `Trading_Value` (quy mô/thanh khoản). PE 2008-2012 cuối tháng kéo
  từ BQ (`tav2_bq.ticker`, chỉ phiên cuối tháng) để có lịch sử tự thân từ 2014.
  ⚠️ PE dùng EPS = NP_TTM/OShares ⇒ vẫn dính OShares (bẫy đã biết; lệch mức theo mã, không theo thời gian). Ghi caveat.
- Universe: `universe_pit` (in_universe) phi tài chính (route 8L PIT như engine). KHÔNG `ticker_prune`. KHÔNG `profit_*`.
- SUE: đúng công thức LAG (`pt_v23_audit_2014.py` dòng ~1059): surprise_B_MA = (NP_P0 − mean(NP_P1..P4)) /
  max(|mean|, 1e9), kẹp ±5; `NP_R` (YoY quý) cũng là biến LAG.
- Value Radar: `data/value_radar_series.csv` (display-only).

## 1. Định nghĩa biến (khai trước)
Tăng trưởng đối xứng sg(a,b) = 2(a−b)/(|a|+|b|) ∈ [−2,2] (chịu được NP âm/0). Với dòng q:
TTM0 = ΣNP_P0..P3, TTM1 = ΣNP_P4..P7 (cùng dòng); TTMk (k≥2) = ΣNP_P4..P7 của dòng 4(k−1) quý trước (đã công bố trước ⇒ PIT).
- `gQ2` = sg(NP_P0+NP_P1, NP_P4+NP_P5) (2 quý gần nhất YoY) · `g1` = sg(TTM0,TTM1) · `g2` = sg(TTM0,TTM2)/2
- `g3` = sg(TTM0,TTM3)/3 · `g5` = sg(TTM0,TTM5)/5 · `acc` = g1 − g1(dòng 4 quý trước) · `accS` = gQ2 − g1
- `rg1`, `rg2`: như g1/g2 cho doanh thu.
- Tăng trưởng TƯƠNG LAI (chỉ làm biến kết quả, không bao giờ làm filter): `f1` = sg(TTM của dòng q+4, TTM0), `f2` = …/2 (q+8).
- PE tự thân: percentile của PE cuối tháng (chỉ PE > 0) trong 60 tháng TRƯỚC đó của chính mã (tối thiểu 24 quan sát).
- Mom 12-1 từ Close cuối tháng. Quy mô = log TB Trading_Value 3 tháng.

## 2. Câu hỏi & kiểm định (mỗi dòng = 1 trial được đếm)
**Q1 — cửa sổ ngoại suy.** Fama-MacBeth theo tháng (cuối tháng 2014-01 → 2026-10), biến phụ thuộc log(PE) [PE∈(0,200)];
phụ: log(P/CF) [PCF>0], log(EV/EBITDA) [>0]. Biến giải thích chuẩn hoá hạng trong cắt ngang (−0,5..0,5). (a) đơn biến từng
cửa sổ {gQ2,g1,g2,g3,g5,acc,accS,rg1,rg2}: R² trung bình, hệ số, t Newey-West (lag 12) IS/OOS; (b) mô hình chung
{gQ2,g1,g2,g3,g5} ± kiểm soát {ROE_Trailing, quy mô}; (c) **phép thử ngoại suy kiểu LSV**: cùng hồi quy với biến phụ
thuộc f1, f2 (tăng trưởng tương lai thật). Thị trường "ngoại suy" cửa sổ w nếu hệ số log(PE) lên w > 0 (t>2 cả IS và OOS)
trong khi hệ số f1/f2 lên w ≤ 0 hoặc nhỏ hơn nhiều. "Đúng 1-2 năm" nếu cửa sổ R² OOS cao nhất ∈ {gQ2,g1,g2} và trong
mô hình chung g3/g5 không có hệ số dương có ý nghĩa ngoài g1/g2.

**Q2 — DCF nhẹ.** Trên base FCFE của engine (base = (CF_OA_3Y+CF_Invest_3Y)/3 > 0), r 12,25%:
- `S0`: g = g_T = 4,5% (đề xuất bài trước) · `CUR`: engine hiện tại (s 0,5, N 5, g_T panel ≤ 5,5%)
- `L{N}_{src}`: N ∈ {1,2,3} năm tường minh với g_recent ∈ {g1_simple, gQ2_simple} (tỷ số thường, kẹp [−30%, +50%]), rồi
  g_T 4,5% ⇒ 6 biến thể · `PEGY`: g1_simple/PE (xếp hạng kiểu PEG, chỉ IC).
Tiêu chí (KHÔNG tự mô tả giá): (i) giải thích giá: var cắt ngang log(P/FV) — R²_rel = 1 − var(v)/var(S0) cùng mẫu, OOS
2020+; (ii) sai số dự báo NP 1 và 2 năm: trung vị |log(TTM thật / TTM dự)|, chỉ cặp dương; bias; IS/OOS;
(iii) IC hạng MoS (FV/P) với lợi suất 3/6/12T, IS/OOS, CI bootstrap khối năm; phân phối ngũ phân vị.
Quy tắc: "cơ sở xếp hạng" chỉ khi ΔIC12 OOS vs S0 ≥ +0,01, CI khối năm không chứa 0 VÀ phần dư sau trực giao hoá Q6 còn
≥ +0,01. "Display-only (giá đang tính tăng trưởng X%)" nếu (i) R²_rel OOS ≥ 0,05 mà (ii)/(iii) không ủng hộ. Kèm tăng
trưởng ngầm định 2 năm (giải ngược từ giá với base FCFE và E) cho live 30/10/2026.

**Q3 — de-rating.** Dòng quý universe_pit phi tài chính 2014+. Chuỗi = ≥ 4 dòng liên tiếp g1_simple ≥ 20% (TTM1 > 0).
Sự kiện E1 = dòng đầu tiên sau chuỗi có g1_simple < 10%; E2 (phụ) = g1_simple giảm ≥ 20 điểm % so với dòng trước khi đang
trong chuỗi. Ngày sự kiện = `time` dòng (khả dụng). Đo: lợi suất −63..0, 0..63/126/252 phiên từ phiên đầu ≥ ngày sự kiện,
trừ trung vị đối chứng (cùng tháng, cùng ICB cấp 1, cùng tercile quy mô, không có sự kiện trong ±2 quý); Δlog PE 0→126/252.
Dấu hiệu sớm ở dòng TRƯỚC sự kiện, so với dòng chuỗi KHÔNG dẫn tới sự kiện ở dòng kế: acc<0, accS<0, NPM_P0 < max 4 dòng
trước, ROE_Trailing < max 4 dòng trước, PE tự thân > 80 ⇒ AUC từng dấu hiệu + lợi suất 6T sau theo dấu hiệu trong nhóm chuỗi.
N = số sự kiện (ticker), CI khối năm. Case bắt buộc: DGC, VCS, MWG, FPT; đối chứng VNM (bảng quý 2014-2026 + hình).

**Q4 — 3×3.** Tháng: nhóm tăng trưởng = tercile cắt ngang của `acc`; nhóm định giá tự thân = PE tự thân <33/33-67/>67.
Lợi suất vượt TB cắt ngang 3/6/12T từng ô, CI khối năm. Fama-MacBeth lợi suất 12T lên hạng {pe_own, EP cắt ngang,
mom12_1, SUE, NP_R, acc, pe_own×acc}. "Ô khác thật" chỉ khi: CI ô loại 0 với Bonferroni 27 (α 0,05/27) VÀ tương tác
pe_own×acc có t_NW > 2 ở IS và cùng dấu OOS. Nếu không: báo là mô tả (giống breadth-tercile), không suy tín hiệu.

**Q5 — Value Radar vs DCF.** Tại 30/10/2026: phân phối PE tự thân (trung vị, % < 20, % < 33); cùng cho P/CF tự thân;
%RẺ của S0 (để đối chiếu 53,1% bài trước); phân vị lịch sử của trung vị log(P/FV_S0) và trung vị PE cắt ngang; tách nguyên
nhân: (a) tăng trưởng TTM NP 2 năm vs base FCFE-3Y, (b) tỷ lệ mã còn đọc BCTC Q2, (c) PE thấp vì E tăng hay giá giảm.
KHÔNG chỉnh tham số cho khớp.

**Q6 — trực giao.** IC của các MoS DCF nhẹ & biến Q4 sau khi trừ phần giải thích bởi {EP, FCFE yield (=S0), SUE, NP_R,
mom12_1} (hồi quy hạng cắt ngang, lấy phần dư). Nếu phần dư IC12 OOS < 0,01 ⇒ nói thẳng "LAG/yield đã có".

## 3. Đếm trial & thống kê
- Q1: 9 đơn biến × 3 biến phụ thuộc + 2 mô hình chung + 9 LSV × 2 = 47 hồi quy (mô tả, không chọn tham số).
- Q2: 9 biến thể (S0, CUR, 6 L, PEGY) × 3 kỳ hạn ⇒ N_trials IC = 27 (khai cho DSR); DSR trên IC12 tháng 12 hằng năm.
- Q3: 2 định nghĩa sự kiện × 5 dấu hiệu sớm = 10. Q4: 27 ô + 1 FM. Q6: ≤ 10.
- Tổng ≈ 120 phép thử ⇒ mọi p thô phải đọc với Bonferroni/BH; N độc lập = số NĂM (13) cho IC, số sự kiện cho Q3.
- IS 2014-2019 / OOS 2020+. threads=1. Không tối ưu tham số trên OOS. Mọi số trong REPORT đo trong phiên, nguồn `out/`.
- Nếu phải thêm phân tích ngoài danh sách: ghi "HẬU NGHIỆM" và cộng vào N.
