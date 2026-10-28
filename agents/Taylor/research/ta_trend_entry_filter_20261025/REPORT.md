# REPORT — Cờ xu hướng (A2/F3/F2) làm bộ lọc lệnh vào LAG/BAL (Giai đoạn 1, PAPER-ONLY)
Job `Taylor_20261025_121521` · 2026-10-25 · PREREG `PREREG.md` (commit `832192373` TRƯỚC khi chạy) · code `analyze.py` · số `results.csv`, `results_sens.csv`, `positions.csv`, `selfcheck.txt`.
Ledger: **R3-park0-pin0pct-SAN md5 `537e349b5589408c994f8aceafeb9a39`** (độ nhạy: R3-park0-pin1M md5 `a6ba34d83a4d374a73293d897c0b43d9`). Giá cờ: `bq_cache_asof20260729_postrestate` (cùng vintage ledger). Không replay NAV, không đề xuất wire.

## Kết luận thẳng
**Không có tác dụng lọc: 0/6 so sánh đạt.** Với LAG, cả 3 cờ không phân biệt được lệnh tốt/xấu (|hiệu| ≤ 3pp, q ≥ 0,44); F2 còn *ngược dấu* (lệnh LAG vào khi đang xu hướng tăng kém hơn −1,8pp). Với BAL, A2 và F2 ngược dấu (cờ BẬT kém hơn 3-4pp). Mọi cờ đều loại 26–82% số lệnh — gần hết vượt trần 40%.
Ô duy nhất đáng chú ý — **BAL × F3** (+7,5pp, IS/OOS cùng dấu) — vẫn **không đạt**: q=0,25 (p=0,04 thô), loại 61% lệnh, IS chỉ 25 lệnh BẬT, và hiệu chủ yếu từ năm 2021 (bỏ 2021 → +2,3pp; cắt 2% lệnh lãi lớn nhất → +3,4pp). Chỉ ghi nhận là giả thuyết, KHÔNG đủ điều kiện mở giai đoạn 2.

## Bảng (nhánh chính: vị thế đã đóng, loại ABANDONED_REFUND; ret = lợi suất ròng tới thoát thật của book)
| So sánh | N BẬT/TẮT | N tháng BẬT/TẮT | ret TB BẬT/TẮT | Hiệu toàn kỳ | Hiệu IS / OOS | p / q(BH, 6) | % lệnh bị loại | Hiệu nhánh +ABANDONED | Hiệu ledger pin1M | contrib TB BẬT/TẮT (bp NAV book) | Đạt? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LAG × A2 | 219/476 | 69/78 | 6,55% / 5,93% | +0,62pp | +1,04 / +0,43 | 0,70 / 0,70 | 68% | −0,06 | +0,31 | 42,4 / 44,9 | không |
| LAG × F3 | 126/569 | 57/79 | 8,56% / 5,59% | +2,97pp | +0,55 / +5,17 | 0,23 / 0,44 | 82% | +0,85 | +1,91 | 47,8 / 43,3 | không |
| LAG × F2 | 299/396 | 74/74 | 5,12% / 6,89% | −1,78pp | −1,80 / −1,37 | 0,29 / 0,44 | 57% | −1,19 | −2,03 | 36,2 / 50,1 | không (ngược dấu) |
| BAL × A2 | 197/102 | 56/49 | 8,36% / 12,26% | −3,91pp | −5,24 / −4,41 | 0,30 / 0,44 | 34% | −3,61 | −3,23 | 63,3 / 94,1 | không (ngược dấu) |
| BAL × F3 | 118/181 | 36/68 | 14,21% / 6,74% | +7,47pp | +0,92 / +9,32 | 0,04 / 0,25 | 61% | +5,52 | +5,97 | 103,1 / 54,7 | không (q, % loại) |
| BAL × F2 | 222/77 | 57/38 | 8,96% / 11,81% | −2,85pp | −2,46 / −4,01 | 0,47 / 0,56 | 26% | −4,02 | −2,30 | 67,7 / 91,6 | không (ngược dấu) |

N vị thế mỗi ô đều ≥100 toàn kỳ (không ô nào "thiếu mẫu" theo PREREG), nhưng **cắt IS thì mỏng**: BAL IS chỉ 83 vị thế (A2 BẬT 42, F3 BẬT 25, F2 TẮT 31) ⇒ dấu IS của BAL không đáng tin. p là bootstrap cụm tháng entry (B=5000); CI 95% hiệu chỉ loại 0 ở BAL×F3 [+0,3; +14,9pp]. Contribution theo vốn cho cùng chiều với ret, không ô nào có ý nghĩa (p_contrib ≥ 0,13).

## Cảnh báo / giới hạn
- **54% vị thế LAG (821/1.517) là ABANDONED_REFUND** (khớp dở rồi hoàn tiền), BAL 96/396 ⇒ nhánh chính chỉ còn 695 LAG / 299 BAL vị thế. Nhánh gộp chúng: 5/6 ô cùng dấu; LAG×A2 đổi dấu (+0,62 → −0,06pp) — càng xác nhận không có tác dụng.
- **Sai trong PREREG §1, ghi lại công khai:** tôi đã giả định ledger pin1M có cùng sổ lệnh với pin0% — SAI (7.230 vs 7.589 dòng TX: tiền nhàn rỗi có lãi đổi cỡ lệnh/lệnh khớp). Đã chạy lại toàn bộ trên ledger pin1M: cùng 0/6, cùng dấu ở cả 6 ô.
- Sửa đổi S1 (PREREG): 1 lệnh bán ghi `holding_id` `VCR_20200427_?` (lỗi ghi của engine) được nối về holding mua duy nhất cùng tiền tố.
- Cờ là TRẠNG THÁI tại phiên trước entry (A2 = Tenkan>Kijun & trên mây; F3 = có phá đỉnh 52 tuần+vol trong 20 phiên; F2 = Close>MA50 & MA50 dốc lên), công thức chép từ `ta_schools_vn_20261025/engine.py`. Chỉ 4 vị thế thiếu lịch sử (cờ TẮT mặc định).
- Không xét chi phí cơ hội vốn nhàn rỗi vì không ô nào qua (a)-(c).

## Tự kiểm
- Σ P&L vị thế = Σ(tiền bán ròng − tiền mua gồm phí) từ TX: lệch **0,0007 VND** (LAG 401.813.479.671 · BAL 157.153.678.308).
- Gộp holding: `AAM_20160722_504` 5 lần khớp mua + 1 bán = 1 vị thế, ret −3,05%.
- Cờ tính tay độc lập (numpy thuần) cho `DPM_20150825_6` và `SD4_20140428_26` khớp engine 3/3 cờ.
- Chạy lại dưới `env -u TZ`: `results.csv`, `positions.csv` byte-identical. Chạy: `$DNA_PYEXE analyze.py` (~11s); độ nhạy: `LEDGER=<pin1M> OUT_TAG=_pin1M $DNA_PYEXE analyze.py`.
