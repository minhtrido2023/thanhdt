# REPORT — Trường phái phân tích kỹ thuật trên dữ liệu VN (thực nghiệm, PAPER-ONLY)
Job `Taylor_20261025_115318` · 2026-10-25 · PREREG: `PREREG.md` (viết trước, không sửa) · code: `engine.py`, `selfcheck.py` · số: `results.csv` (108 dòng), `panel_events.parquet`
Không đề xuất wire production.

## Kết luận thẳng
**Đa số KHÔNG có edge; nhiều trường phái còn thua ngẫu nhiên có ý nghĩa thống kê.** Chỉ có tín hiệu thiên về *xu hướng/breakout* hơn được đối chứng ngẫu nhiên (F1), và không cái nào hơn đối chứng xu hướng (F2). Không cấu hình nào đạt "CÓ + vượt F2".

| Trường phái | Bằng chứng? | Ghi chú (h=20, exF1 = lợi suất trừ rổ ngẫu nhiên cùng ngày + cùng tertile ADV) |
|---|---|---|
| **Ichimoku** | Một phần: chỉ A2 (Tenkan cắt Kijun khi trên mây): +0,93pp vs F1, IS +1,27 / OOS +0,75, q=0,001; **không vượt F2** (+0,32pp, q=0,15) và hết vào h=40 OOS (+0,27pp). A1 (phá mây) và A3 (đủ 3 điều kiện) = **không edge** (±0). | Giá trị gia tăng so với "đang trong xu hướng tăng" chưa chứng minh được. |
| **VSA** | Không. Stopping volume **thua** ngẫu nhiên (−1,83/−1,02pp IS/OOS, q=0,03); Test −3,45 IS (mẫu 344); Upthrust không dự báo giảm (+0,28 OOS, sai dấu). C2b (no-supply trong uptrend) +0,48pp nhưng là hiệu ứng "giá > MA50": **thua F2** (−0,21pp, q=0,05). | C2a không điều kiện: không edge. |
| **Nến Nhật** | Không. Không cấu hình nào hơn F1. Sau xu hướng giảm (bối cảnh mẫu hình đảo chiều dùng) cả 3 mẫu hình **thua** ngẫu nhiên: Hammer −1,29/−0,77pp (q=0,001), Engulfing −1,09/−0,49, Morning star −1,44/−0,26 (mẫu mỏng, N=221). Volume xác nhận không cứu. | Phù hợp thị trường momentum: mua đáy-đảo-chiều ngược dòng thua. |
| **Darvas** | Không, **âm có ý nghĩa**: breakout hộp+vol −0,33/−0,81pp (q=0,001), không vol +0,01/−0,68 (IS→OOS xấu đi). Trong khi F3 (phá đỉnh 52 tuần+vol) dương (+1,24/+0,48) ⇒ hộp 20 phiên quá ngắn / đuổi giá. | |
| **Dòng tiền** | Không. CMF cắt 0: ±0; OBV phá đỉnh: IS+0,40 → OOS −0,19 (đổi dấu, loại); MFI thoát <20: **âm** −0,92/−0,53 (q=0,004). Khối ngoại/tự doanh: **không đo được** (không có cột trong BQ; feeds mới CANDIDATE). | |
| Đối chứng | F2 (trên MA50 dốc lên) +0,03/+0,44 — tự nó hơn F1 rất mỏng (q=0,03); F3 +1,24/+0,48 (q=0,01) và không hơn F2c (+0,17pp, q=0,47). | Xu hướng/breakout 52w là "đường cơ sở" mà mọi tín hiệu phải vượt. |

**Đọc đúng:** (1) cái *có* hoạt động là sức mạnh xu hướng (A2, F3, C2b, F2 cùng họ, không tách biệt nhau); (2) mọi tín hiệu *đảo chiều/bắt đáy* (nến, stopping volume, test, MFI<20) thua rổ ngẫu nhiên; (3) không "trường phái" nào có phần dư độc lập khỏi xu hướng.

## Bảng 1 dòng/tín hiệu (h=20 phiên; pp = điểm %; exF2 = excess vs rổ ngẫu nhiên CHỈ trong mã đang ở xu hướng F2)
| Tín hiệu | N | N ngày | N tháng | exF1@20 IS/OOS (pp) | q(F1) | exF2@20 (pp) | q(F2) | ròng vs VNI (pp) | Kết luận |
|---|---|---|---|---|---|---|---|---|---|
| A1 Kumo breakout | 12087 | 2789 | 153 | -0.23 / +0.05 | 0.864 | -0.65 | 0.001 | -0.10 | không |
| A2 Tenkan×Kijun trên mây | 7086 | 2202 | 153 | +1.27 / +0.75 | 0.001 | +0.32 | 0.154 | +1.02 | CÓ(F1) / không vượt F2 |
| A3 A1+Chikou | 6649 | 2214 | 153 | -0.11 / +0.12 | 0.888 | -0.56 | 0.009 | -0.00 | không |
| B Engulf unc/any | 23976 | 2988 | 153 | +0.24 / -0.08 | 0.873 | -0.50 | 0.008 | -0.18 | không |
| B Engulf unc/vol | 8145 | 2468 | 153 | +0.17 / -0.20 | 0.776 | -0.64 | 0.030 | +0.08 | không |
| B Engulf dt/any | 5302 | 1725 | 153 | -1.09 / -0.49 | 0.025 | -1.13 | 0.074 | -0.84 | không |
| B Engulf dt/vol | 1270 | 813 | 148 | -1.80 / -0.46 | 0.351 | -1.29 | 0.348 | -0.46 | không |
| B Hammer unc/any | 26145 | 3110 | 153 | -0.10 / -0.07 | 0.556 | -0.72 | 0.001 | -0.44 | không |
| B Hammer unc/vol | 5517 | 2319 | 153 | -0.17 / -0.08 | 0.776 | -0.80 | 0.002 | -0.11 | không |
| B Hammer dt/any | 5506 | 1936 | 152 | -1.29 / -0.77 | 0.001 | -1.75 | 0.001 | -1.51 | không |
| B Hammer dt/vol | 1037 | 700 | 141 | -1.55 / -0.71 | 0.039 | -2.05 | 0.001 | -1.23 | không |
| B MornStar unc/any | 932 | 631 | 150 | -0.49 / -0.56 | 0.245 | -1.14 | 0.003 | -0.95 | không |
| B MornStar unc/vol | 293 | 251 | 127 | -0.92 / -0.06 | 0.758 | -0.78 | 0.273 | -0.30 | không |
| B MornStar dt/any | 221 | 172 | 99 | -1.44 / -0.26 | 0.357 | -2.05 | 0.004 | -1.52 | không |
| B MornStar dt/vol | 56 | 52 | 44 | -2.79 / -0.71 | — | -2.37 | — | -1.42 | thiếu mẫu |
| C1 Stopping vol | 1796 | 993 | 151 | -1.83 / -1.02 | 0.028 | -1.74 | 0.135 | -0.87 | không |
| C2a No-supply | 35074 | 3080 | 153 | -0.11 / -0.06 | 0.351 | -0.74 | 0.001 | -0.69 | không |
| C2b No-supply+>MA50 | 17168 | 2865 | 153 | +0.77 / +0.34 | 0.001 | -0.21 | 0.053 | +0.02 | CÓ(F1) / không vượt F2 |
| C3 Upthrust (né) | 5980 | 1925 | 153 | -0.04 / +0.28 | 0.674 | -0.47 | 0.105 | +0.47 | không |
| C4 Test | 344 | 307 | 127 | -3.45 / +0.46 | 0.161 | -2.42 | 0.005 | -2.26 | không |
| D1 Darvas+vol | 8997 | 2412 | 153 | -0.33 / -0.81 | 0.001 | -1.26 | 0.001 | -0.61 | không |
| D2 Darvas | 11235 | 2593 | 153 | +0.01 / -0.68 | 0.007 | -1.01 | 0.001 | -0.44 | không |
| E1 CMF cắt 0 | 17647 | 2980 | 153 | -0.12 / +0.01 | 0.842 | -0.66 | 0.001 | -0.26 | không |
| E2 OBV phá đỉnh | 12866 | 2857 | 153 | +0.40 / -0.19 | 0.959 | -0.53 | 0.001 | -0.05 | không |
| E3 MFI thoát <20 | 7993 | 2244 | 153 | -0.92 / -0.53 | 0.004 | -1.40 | 0.003 | -1.04 | không |
| F2 xu hướng MA50 | 12420 | 2815 | 153 | +0.03 / +0.44 | 0.030 | -0.33 | 0.032 | +0.14 | CÓ(F1) / không vượt F2 |
| F3 52w+vol | 6171 | 2037 | 153 | +1.24 / +0.48 | 0.010 | +0.17 | 0.465 | +0.84 | CÓ(F1) / không vượt F2 |

Cột N ngày = số ngày tín hiệu khác nhau (N hiệu dụng theo ngày); N tháng = số cụm bootstrap. "ròng vs VNI" = trung bình `R−R_VNINDEX−0,394%` (đã trừ chi phí).
"không" = không qua tiêu chí PREREG §4 (không đồng nghĩa luôn âm — xem cột số). Hit rate ròng của mọi cấu hình ở h=20 chỉ 43–50%.

## Cảnh báo / giới hạn
- **Mẫu mỏng:** Morning star (dt/vol N=56 → thiếu mẫu; dt/any N=221, 99 tháng), Test C4 (344), Stopping volume (1.796). Kết luận "không edge" ở các ô này là *không đủ năng lực bác bỏ*, không phải đã chứng minh vô hiệu.
- **Trung bình ≠ trung vị:** phân phối lệch phải ⇒ exF1 trung vị âm cho MỌI cấu hình (kể cả đối chứng); tiêu chí dùng trung bình, có p theo bootstrap cụm tháng. Trượt giá thực tế lệnh lớn/UPCOM kém thanh khoản chưa mô hình hoá.
- **Họ nhiều trial:** 108 trial (27 cấu hình × 4 horizon), 104 đủ mẫu vào BH-FDR; có 45 trial q<0,10 ở F1 (xem `results.csv`), nhưng 33 trong số đó là *âm* (thua ngẫu nhiên), chỉ 12 dương (h5:1, h10:3, h20:4, h40:4; toàn là A2/C2b/F2/F3 — họ xu hướng). p bootstrap sàn 1/5000.
- **Hiệu ứng trục:** tín hiệu có điều kiện trên xu hướng (A2, C2b, F3) bị lẫn với F2; thứ tự lợi suất không tách được bằng 1 trục ⇒ chỉ nói "không hơn F2", không nói "vô dụng".
- **Chọn lọc sống sót:** cửa sổ forward không hoàn tất (mã bị đình chỉ/hủy niêm yết trước t+h) bị loại ở cả tín hiệu lẫn đối chứng ⇒ thiên lệch lạc quan nhỏ, đối xứng giữa các nhánh.
- Tham số CỐ ĐỊNH ở chuẩn sách giáo khoa nhưng định nghĩa cơ học VSA/Darvas/nến là một cách *diễn giải* — người hành nghề có thể đọc khác (chủ quan, theo ngữ cảnh) ⇒ kết quả áp cho phiên bản cơ học này.
- ADV ≥ 1 tỷ VND/ngày, `universe_pit` v1; chỉ LONG; entry Open T+1 (không tính rủi ro biên độ ±7% HOSE/chạm trần-sàn không khớp được).
- IS 2014–19 / OOS 2020+; năm 2021 chiếm nhiều sự kiện nhất (bull retail) nhưng leave-one-year-out vẫn cùng dấu cho A2/C2b/F3 (loyo_min A2 +0,84pp, C2b +0,41pp, F3 +0,60pp).

## Phương pháp & tự kiểm (tóm tắt)
Giá điều chỉnh (`Close/Open/High/Low`), `Volume` thô; loại sự kiện có corp-action (|Δ Close/Price|>3%) trong 25 phiên trước. Kiểm AAA 2014-08-26 (chia tách): từ 2014-08-20 +10 phiên, lợi suất trên giá điều chỉnh **+5,41%** vs trên giá thô **−18,14%** ⇒ dùng giá thô sẽ ghi lỗ giả; không double-count. Self-check thuần Python (`selfcheck.py`): HPG A2 24/24 sự kiện khớp; R20 và control F1 của 1 sự kiện (HPG 2021-04-07: R20=0,272727273, control=−0,033833109 trên 129 mã cùng tertile) khớp engine tới 1e-9. Chạy `engine.py` ≈ 60s: `$DNA_PYEXE engine.py`.
