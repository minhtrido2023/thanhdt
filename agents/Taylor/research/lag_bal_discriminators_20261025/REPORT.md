# REPORT — Chỉ báo fundamental phân biệt lệnh vào tốt/xấu trong LAG và BAL (Giai đoạn 1, PAPER-ONLY)
Job `Taylor_20261025_123115` · 2026-10-25 · PREREG `PREREG.md` (commit `cb622b159`, TRƯỚC khi chạy) · code `analyze.py` · số `results.csv`, `tertiles.csv`, `loo.csv`, `corr.csv`, `describe.csv`, `features{,_pin1M}.csv`.
Ledger R3-park0-pin0pct-SAN md5 `537e349b5589408c994f8aceafeb9a39` (sens: pin1M md5 `a6ba34d83a4d374a73293d897c0b43d9`), vị thế = `positions*.csv` của job `Taylor_20261025_121521` (gộp holding_id, loại ABANDONED_REFUND/MTM) ⇒ **695 LAG / 299 BAL**. Fundamental PIT từ `bq_cache_asof20260729_postrestate` (cùng vintage ledger). Không replay NAV, không đề xuất wire.

## Kết luận thẳng
**Đa số KHÔNG phân biệt được: 46/50 ô không đạt.** 4 ô đạt đủ tiêu chí khai trước, nhưng gom lại chỉ là **1 hiệu ứng: định giá (value)** — không có chỉ báo chất lượng/cổ tức/tăng trưởng/công bố nào đạt.
- **LAG × 1/PE** (+5,6pp T3−T1, q=0,09) — đây là BIẾN KIỂM SOÁT, factor trội đã biết; xác nhận lại nó cũng có tác dụng TRONG book LAG (lệnh LAG rẻ theo LN tốt hơn lệnh đắt), không phải phát hiện mới.
- **LAG × EBITDA-yield (1/EVEB)** (+7,0pp, q=0,09) — **proxy của value**: tương quan với 1/PE 0,64, hệ số mất ý nghĩa khi kiểm soát 1/PE (p=0,13).
- **BAL × 1/PCF** (+12,5pp, q=0,09) và **BAL × 1/EVEB** (+12,9pp, q=0,09) — chỉ trên phi tài chính; **còn ý nghĩa sau khi kiểm soát 1/PE** (p=0,003 / 0,0004). Hai chỉ báo tương quan 0,54 với nhau ⇒ đếm là **1 hiệu ứng: "rẻ theo dòng tiền/EV" trong BAL phi tài chính**.

**Đủ điều kiện giai đoạn 2 (replay NAV, cần user duyệt + quant-skeptic):** chỉ ứng viên BAL × dòng tiền (1/PCF, 1/EVEB), có rủi ro đọc sai lớn (dưới đây). LAG × value không đề xuất giai đoạn 2 riêng: nó gần với "composite v3 làm bộ chọn lệnh vào" đã NO-GO — muốn mở lại phải nói rõ khác chỗ nào.

## Cổ tức tiền mặt (user hỏi) — KHÔNG đạt, LAG còn NGƯỢC hướng
| Book × chỉ báo | T1 (thấp) ret TB / N | T2 | T3 (cao) ret TB / N | T3−T1 | IS / OOS | q | pin1M |
|---|---|---|---|---|---|---|---|
| LAG × payout 1 năm | 8,4% / 233 | 6,5% / 184 | 5,4% / 211 | **−3,0pp** | −0,2 / −4,8 | 0,43 | −2,8 |
| LAG × payout 3 năm | 7,6% / 216 | 8,3% / 204 | 4,3% / 212 | **−3,3pp** | −1,0 / −5,4 | 0,32 (p thô 0,049) | −3,6 |
| BAL × payout 1 năm | 8,8% / 100 | 11,4% / 81 | 10,5% / 93 | +1,7pp | +14,8 / −2,3 | 0,81 | −0,4 |
| BAL × payout 3 năm | 11,0% / 90 | 10,6% / 90 | 9,1% / 93 | −1,9pp | +4,9 / −3,7 | 0,81 | −4,2 |
Đọc: trong LAG, mã chi trả cao (T3, trung vị payout ~74%) lại kém hơn ~3pp — đúng ngược giả thuyết khai trước, ổn định khi bỏ từng năm (−1,5…−4,6pp) nhưng không qua FDR. Giải thích kinh tế khả dĩ (chưa kiểm): PEAD mạnh hơn ở mã giữ lại LN để tăng trưởng; payer cao là mã trưởng thành, bất ngờ LN ít "kéo dài". BAL: dấu IS/OOS đảo, không có gì. DY, trả đều 3 năm, tăng/giảm cổ tức: cả 2 book |hiệu| ≤ 2,7pp, q ≥ 0,73. ⇒ **Payout không đáng đưa vào xét tiếp.**

## Bảng 4 ô đạt (đủ: đúng hướng, |d|≥2pp, IS/OOS cùng dấu, q<0,10, ρ cùng dấu, bỏ 2021 & cắt đuôi 2% không đảo, pin1M ≥2pp)
| Ô | N vị thế / N tháng | T1 / T3 ret | d | IS / OOS (N) | CI95 d | bỏ 2021 / cắt 2% | LOO min–max | pin1M | kiểm soát 1/PE: hệ số, p |
|---|---|---|---|---|---|---|---|---|---|
| LAG × ey | 690 / 82 | 2,7% / 8,3% | +5,6 | +6,1 / +5,4 (309/381) | [+1,6; +9,3] | +4,8 / +4,3 | +4,3…+6,9 | +5,8 | (là chính nó) |
| LAG × 1/EVEB | 531 / 82 | 2,0% / 9,0% | +7,0 | +9,5 / +4,9 (263/268) | [+2,5; +11,7] | +7,0 / +4,3 | +5,3…+8,2 | +7,8 | +5,2pp, p=0,13 ⇒ proxy value |
| BAL × 1/PCF | 157 / **36** | 1,0% / 13,4% | +12,5 | +17,1 / +11,3 (**28**/129) | [+3,5; +21,3] | +14,8 / +8,7 | +6,4…+15,2 | +5,9 | +18,6pp, p=0,003 |
| BAL × 1/EVEB | 158 / **36** | 5,9% / 18,8% | +12,9 | +18,0 / +12,5 (**29**/129) | [+3,5; +22,0] | +16,8 / +11,9 | +8,5…+16,8 | +12,4 | +25,8pp, p=0,0004 |

## Rủi ro đọc sai (BAL × dòng tiền)
1. **Mẫu mỏng & dồn cục**: chỉ 157 lệnh BAL phi tài chính trong **36 tháng**; IS chỉ 28 lệnh; 70/157 lệnh ở 2020–2021. q=0,09 sát ngưỡng; với 100 phép thử, 4 ô q<0,10 là đúng mức kỳ vọng nếu có ~1 hiệu ứng thật.
2. **Hiệu ứng nằm ở đuôi dưới, không đơn điệu**: BAL 1/PCF T1 = 1,0% nhưng T2 (16,5%) > T3 (13,4%). T1 có trung vị 1/PCF ≈ 0 ⇒ chủ yếu là **mã có CFO trailing ≤ 0** (PCF âm) được BAL chọn nhờ 1/PE cao. Cơ chế khả dĩ: LN kế toán không có tiền đi kèm. Nhưng cfo/NP và accrual (cùng câu hỏi, đo trực tiếp) lại KHÔNG đạt (BAL accrual −9,2pp đúng hướng, q=0,15; IS N mỏng) ⇒ chưa chắc đây là "chất lượng LN" chứ không phải nhiễu.
3. **BAL đã xếp hạng theo 1/PE + 1/PCF** (yieldcombo). Hiệu ứng này = "trong tập đã chọn, 1/PCF vẫn còn thông tin" ⇒ giai đoạn 2 thực chất là **đổi trọng số/thêm sàn CFO>0 cho bộ chọn BAL** — đụng engine production, cần replay đầy đủ (tái phân bổ vốn có thể ăn hết hiệu, như BAL MAX_POS NO-GO 10-09).
4. pin1M: BAL 1/PCF yếu đi một nửa (+5,9 vs +12,5pp) dù vẫn qua ngưỡng — độ nhạy theo sổ lệnh đáng kể.

## Phần còn lại (chi tiết `table.md`, `results.csv`)
- Chất lượng LN (cfo/NP, accrual, biên gộp, Δbiên, ROE, ΔROA): không ô nào đạt. LAG ROE +3,8pp (q=0,30) mất sạch khi kiểm soát 1/PE (p=0,78) ⇒ proxy value. LAG biên gộp và tồn kho/phải thu đều ngược hướng.
- Bảng cân đối (nợ/vốn, nợ ròng/EBITDA, tồn kho/DT, phải thu/DT): không đạt; BAL nợ ròng/EBITDA −7,9pp đúng hướng nhưng q=0,40.
- Tăng trưởng (DT YoY, LN YoY, gia tốc): không đạt, LN YoY trong LAG ≈ 0 (d=+0,0pp) — đúng như kỳ vọng sau SUE-tilt NO-GO: trong nhóm đã chọn theo bất ngờ, độ lớn bất ngờ không thêm gì.
- Thanh khoản (ADV): không đạt cả 2 book.
- Công bố: LAG `gap` **suy biến** (75% lệnh vào đúng 5 phiên sau công bố — tertile thấp chỉ 8 lệnh ⇒ thiếu mẫu). BAL `gap` +8,0pp **ngược hướng** (vào muộn sau BCTC tốt hơn), IS/OOS cùng dấu, q=0,32 — chỉ là giả thuyết, có thể là hiệu ứng lịch tái cân bằng. Phản ứng giá ngày công bố: không đạt.
- Mô tả (ngoài họ kiểm định, `describe.csv`): LAG theo state engine CRISIS 2,9% → BULL 8,5% (N mỏng ở cực); mùa BCTC Q3 kém nhất (2,4%); BAL vào theo BCTC Q4 ≈ 0,6% vs 12–17% các quý khác (N 96 / 23 tháng) — đáng ghi nhận như câu hỏi riêng, KHÔNG kết luận. Breadth-tercile: không đo trong job này.
- **Không đo được**: vốn hoá (OShares TRAP), free-float/room ngoại (không có cột), SUE (không có chuỗi PIT cùng vintage), khả năng trả lãi (IntCov hộp đen vendor).

## Phương pháp & giới hạn
Phân vị trong (book × nhóm ngành BANK/FINO-CK-BH/RE/NONFIN), chỉ báo dòng tiền/nợ/tồn kho/định giá-EV chỉ trên NONFIN. Hiệu = ret TB tertile cao − thấp tới thoát thật. p bootstrap cụm tháng entry B=5000; ρ trong bootstrap tính bằng Pearson trên hạng cố định toàn mẫu (xấp xỉ Spearman). **BH-FDR trên 100 p** (25 chỉ báo × 2 book × {tertile, ρ}). PIT: dòng BCTC hiệu lực = max(time, Release_Date) ≤ phiên tín hiệu, thiếu Release_Date ⇒ time+11 ngày; 0 vi phạm PIT. Giới hạn: cỡ mẫu ≤ 695 vị thế/82 tháng (LAG), ≤ 299/73 (BAL); tertile pool qua thời gian (mức định giá trôi theo năm chưa khử).

## Tự kiểm
- Tính tay độc lập (Python thuần, đọc parquet thô): payout1Y và cfo/NP cho `DNC_20140206_7` (LAG) và `HPG_20140509_1` (BAL) khớp engine tới 1e-8 (`selfcheck_hand.txt`).
- ΣP&L vị thế = tiền mặt TX theo book: lệch 14 / 12 VND (pin0 LAG/BAL), 1,5 / 0,7 VND (pin1M) — nằm trong sai số làm tròn 10 chữ số của `positions.csv` (cận 3.439 / 1.149 VND); job trước khớp 0,0007 VND trên số chưa làm tròn.
- `env -u TZ` chạy lại: `results.csv`, `features.csv`, `tertiles.csv` byte-identical. Chạy: `$DNA_PYEXE analyze.py` (~18s).

## Phụ lục — mọi ô (d, IS/OOS, bỏ2021/cắt2%, pin1M: pp; q: BH trên 100)
| Book | Chỉ báo | Hướng | N / N tháng | d | IS / OOS | ρ | q | bỏ 2021 / cắt 2% | pin1M | Kết quả |
|---|---|---|---|---|---|---|---|---|---|---|
| LAG | payout1Y | + | 628 / 82 | -3,0 | -0,2 / -4,8 | -0.06 | 0.43 | -2,0 / -2,8 | -2,8 | không |
| LAG | payout3Y | + | 632 / 82 | -3,3 | -1,0 / -5,4 | -0.09 | 0.32 | -3,0 / -3,2 | -3,6 | không |
| LAG | DY | + | 657 / 82 | -0,2 | +2,7 / -1,6 | +0.02 | 0.95 | +0,8 / -1,1 | +0,0 | không |
| LAG | div3y | + | 662 / 82 | -1,2 | -0,4 / -1,7 | -0.04 | 0.73 | -0,6 / -1,3 | -0,9 | không |
| LAG | div_chg | + | 468 / 82 | -0,8 | +0,2 / -0,4 | -0.03 | 0.81 | -1,4 / -2,2 | -0,8 | không |
| LAG | cfo_np | + | 482 / 82 | +2,4 | +3,8 / +1,1 | +0.04 | 0.60 | +1,8 / +1,7 | +3,4 | không |
| LAG | accrual | − | 508 / 82 | -1,6 | -2,8 / -0,3 | -0.04 | 0.74 | -1,1 / -1,8 | -2,3 | không |
| LAG | gpm | + | 534 / 82 | -2,0 | -2,3 / -1,6 | -0.02 | 0.57 | -2,0 / -2,2 | -3,0 | không |
| LAG | d_gpm | + | 534 / 82 | -2,1 | -0,9 / -3,4 | +0.01 | 0.60 | -1,8 / -2,2 | -1,9 | không |
| LAG | roe | + | 655 / 82 | +3,8 | +1,7 / +5,9 | +0.08 | 0.30 | +2,1 / +2,6 | +3,2 | không |
| LAG | d_roa | + | 695 / 82 | +2,3 | +5,1 / +0,3 | +0.03 | 0.55 | +0,8 / +1,0 | +2,1 | không |
| LAG | de | − | 534 / 82 | +3,0 | +6,1 / +0,7 | +0.03 | 0.46 | +2,3 / +1,3 | +2,6 | không |
| LAG | nd_ebitda | − | 470 / 80 | -1,0 | +3,8 / -5,2 | -0.05 | 0.81 | -0,3 / +0,3 | -1,3 | không |
| LAG | inv_rev | − | 530 / 82 | -2,5 | +0,1 / -4,6 | -0.04 | 0.47 | -2,1 / -1,2 | -2,0 | không |
| LAG | ar_rev | − | 530 / 82 | -3,1 | -0,6 / -4,9 | -0.07 | 0.36 | -2,7 / -3,2 | -3,9 | không |
| LAG | rev_yoy | + | 687 / 82 | +2,1 | +6,2 / -0,7 | +0.02 | 0.70 | +0,1 / +2,0 | +2,2 | không |
| LAG | np_yoy | + | 657 / 82 | +0,0 | +6,1 / -4,8 | -0.03 | 1.00 | -0,2 / -0,9 | -0,4 | không |
| LAG | np_accel | + | 626 / 82 | -1,5 | +1,1 / -3,8 | -0.06 | 0.74 | -0,6 / -1,6 | -0,8 | không |
| LAG | ey | + | 690 / 82 | +5,6 | +6,1 / +5,4 | +0.12 | 0.09 | +4,8 / +4,3 | +5,8 | ĐẠT |
| LAG | by | + | 695 / 82 | +1,8 | +6,1 / -0,7 | +0.05 | 0.60 | +2,7 / +2,1 | +2,3 | không |
| LAG | cfy | + | 531 / 82 | +3,5 | +4,2 / +2,8 | +0.08 | 0.36 | +3,1 / +3,3 | +4,4 | không |
| LAG | ebitda_y | + | 531 / 82 | +7,0 | +9,5 / +4,9 | +0.12 | 0.09 | +7,0 / +4,3 | +7,8 | ĐẠT |
| LAG | adv | − | 427 / 79 | +0,9 | +3,7 / -3,7 | +0.01 | 0.81 | +0,3 / -0,8 | -1,6 | không |
| LAG | gap | − | 695 / 82 | +2,5 | +0,0 / +9,4 | +0.13 | 0.81 | +2,5 / -0,4 | -2,5 | thiếu mẫu |
| LAG | react | + | 694 / 82 | -0,6 | -0,8 / -0,7 | -0.00 | 0.86 | -0,9 / -0,1 | -0,6 | không |
| BAL | payout1Y | + | 274 / 71 | +1,7 | +14,8 / -2,3 | +0.04 | 0.81 | +1,8 / +3,1 | -0,4 | không |
| BAL | payout3Y | + | 273 / 71 | -1,9 | +4,9 / -3,7 | +0.00 | 0.81 | +0,5 / +0,7 | -4,2 | không |
| BAL | DY | + | 276 / 71 | +2,7 | +11,7 / +0,2 | +0.08 | 0.74 | +1,1 / +2,9 | +2,0 | không |
| BAL | div3y | + | 277 / 71 | -1,3 | +0,1 / -1,9 | +0.01 | 0.83 | -2,3 / +0,1 | -2,2 | không |
| BAL | div_chg | + | 151 / 56 | +1,3 | -4,6 / +2,9 | -0.00 | 0.86 | -0,9 / -0,7 | +2,2 | không |
| BAL | cfo_np | + | 153 / 36 | +6,0 | +15,6 / +3,5 | +0.12 | 0.45 | +7,4 / +1,9 | +0,9 | không |
| BAL | accrual | − | 157 / 36 | -9,2 | -16,9 / -7,3 | -0.15 | 0.15 | -10,3 / -5,4 | -4,4 | không |
| BAL | gpm | + | 158 / 36 | +8,5 | +4,7 / +9,5 | +0.14 | 0.35 | +6,7 / +8,7 | +1,3 | không |
| BAL | d_gpm | + | 158 / 36 | -4,1 | -16,1 / -0,1 | -0.08 | 0.74 | -9,9 / -2,8 | -7,7 | không |
| BAL | roe | + | 288 / 71 | +5,3 | -9,0 / +11,6 | +0.04 | 0.50 | +3,3 / +3,0 | +5,6 | không |
| BAL | d_roa | + | 299 / 73 | +1,3 | -3,8 / +3,2 | -0.03 | 0.86 | -0,1 / -0,9 | +2,0 | không |
| BAL | de | − | 158 / 36 | -1,4 | -10,2 / +0,7 | -0.05 | 0.86 | -5,1 / -2,5 | -4,5 | không |
| BAL | nd_ebitda | − | 157 / 36 | -7,9 | -12,6 / -7,0 | -0.17 | 0.40 | -9,7 / -6,7 | -8,5 | không |
| BAL | inv_rev | − | 158 / 36 | -2,6 | -14,8 / +0,2 | -0.03 | 0.77 | -5,9 / -4,0 | -5,4 | không |
| BAL | ar_rev | − | 158 / 36 | +3,3 | +5,8 / +2,8 | +0.02 | 0.77 | +0,5 / +2,3 | +2,5 | không |
| BAL | rev_yoy | + | 299 / 73 | -1,8 | -1,2 / -2,1 | +0.01 | 0.81 | +1,0 / +1,4 | +0,2 | không |
| BAL | np_yoy | + | 282 / 73 | -2,7 | -7,3 / -1,4 | -0.06 | 0.74 | -3,6 / -3,2 | -2,6 | không |
| BAL | np_accel | + | 273 / 73 | -1,0 | -0,8 / -1,1 | -0.03 | 0.88 | +2,0 / -1,6 | +0,0 | không |
| BAL | ey | + | 298 / 73 | +6,4 | -6,8 / +11,9 | +0.15 | 0.43 | +6,2 / +6,5 | +6,0 | không |
| BAL | by | + | 299 / 73 | +2,2 | +0,7 / +2,9 | +0.09 | 0.77 | +2,9 / +4,7 | +3,3 | không |
| BAL | cfy | + | 157 / 36 | +12,5 | +17,1 / +11,3 | +0.23 | 0.09 | +14,8 / +8,7 | +5,9 | ĐẠT |
| BAL | ebitda_y | + | 158 / 36 | +12,9 | +18,0 / +12,5 | +0.25 | 0.09 | +16,8 / +11,9 | +12,4 | ĐẠT |
| BAL | adv | − | 298 / 73 | +1,9 | +4,6 / +0,9 | +0.04 | 0.81 | +2,0 / +0,6 | +0,9 | không |
| BAL | gap | − | 299 / 73 | +8,0 | +11,6 / +6,8 | +0.08 | 0.32 | +8,3 / +4,4 | +7,6 | không |
| BAL | react | + | 271 / 68 | +5,7 | -2,6 / +7,4 | +0.08 | 0.36 | +4,7 / +3,9 | +2,4 | không |
