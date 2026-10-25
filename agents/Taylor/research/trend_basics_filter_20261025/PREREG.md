# PREREG — "Trending basics" (xu hướng LIÊN TỤC + tương tác value) lọc lệnh LAG/BAL (Giai đoạn 1, READ-ONLY, PAPER-ONLY)
Job `Taylor_20261025_131054` · 2026-10-25 · viết và commit TRƯỚC khi chạy `analyze.py`. Không đổi production/engine/filter, không ghi pin, không replay NAV, không wire.

## 0. Câu hỏi
Xu hướng đo như BIẾN LIÊN TỤC / chất lượng xu hướng, và tương tác value × xu hướng, có phân biệt lệnh vào tốt/xấu trong LAG/BAL **ngoài** những gì đã thử (3 cờ nhị phân A2/F3/F2 — job `ta_trend_entry_filter_20261025`, 0/6 đạt) và **ngoài value** (1/PE, 1/EVEB — job `lag_bal_discriminators_20261025`)? "Không lọc được" là kết quả hợp lệ.

## 1. Dữ liệu (cố định)
- Vị thế: `ta_trend_entry_filter_20261025/positions{,_pin1M}.csv` (gộp holding_id). Nhánh chính: loại ABANDONED_REFUND, MTM/còn mở ⇒ **695 LAG / 299 BAL** (ledger R3-park0-pin0pct-SAN md5 `537e349b5589408c994f8aceafeb9a39`). Độ nhạy: ledger R3-park0-pin1M md5 `a6ba34d83a4d374a73293d897c0b43d9` (sổ lệnh KHÁC, không phải cùng lệnh).
- Value + nhóm ngành G (BANK/FINO/RE/NONFIN): `lag_bal_discriminators_20261025/features{,_pin1M}.csv` (`ey`=1/PE, `ebitda_y`=1/EVEB, PIT đã kiểm bởi skeptic). Join theo `holding_id`.
- Giá: `data/bq_cache_asof20260729_postrestate/ticker/*.parquet` (cùng vintage ledger; 2013-01→2026-07). `Close/High/Low` điều chỉnh, `Volume` thô. VNINDEX lấy cùng nguồn (ticker `VNINDEX`). Universe đã do engine (universe_pit) chọn — job này không chọn universe, chỉ đọc giá các mã trong ledger.
- PIT: mọi chỉ báo tính bằng dữ liệu tới **phiên tín hiệu = phiên giao dịch liền trước entry** (merge_asof backward); không dùng bất kỳ cột `profit_*`.

## 2. Bộ chỉ báo CỐ ĐỊNH (13 biến, hướng khai TRƯỚC; c = Close điều chỉnh, t = phiên tín hiệu)
| # | Tên | Định nghĩa | Hướng kỳ vọng |
|---|---|---|---|
| T1a | `rs60` | ln(c_t/c_{t-60}) − ln(VNI_t/VNI_{t-60}) | + |
| T1b | `rs120` | như trên, 120 phiên | + |
| T2a | `adx14` | ADX Wilder 14 (TR, ±DM làm mượt ewm α=1/14, adjust=False; ADX = ewm α=1/14 của DX) | + |
| T2b | `di_spread` | (+DI − −DI) 14 | + |
| T3a | `d_ma50` | c/MA50 − 1 | + |
| T3b | `d_ma200` | c/MA200 − 1 | + |
| T3c | `slope_ma200` | MA200_t / MA200_{t-20} − 1 | + |
| T4 | `hhhl` | Swing fractal 3: đỉnh tại i nếu High_i = max(High_{i-3..i+3}), đáy tương tự với Low; chỉ dùng swing đã XÁC NHẬN (i+3 ≤ t) và i ∈ (t−120, t]. Điểm = (#đỉnh cao hơn đỉnh trước + #đáy cao hơn đáy trước) − (#đỉnh thấp hơn + #đáy thấp hơn); so sánh đỉnh/đáy đầu tiên trong cửa sổ với swing liền trước nó (có thể ngoài cửa sổ) | + |
| T5a | `up60` | tỉ lệ phiên c_i > c_{i-1} trong 60 phiên | + |
| T5b | `r2s60` | R² hồi quy ln(c) theo thời gian 60 phiên × dấu(độ dốc) (xu hướng "sạch" và đi LÊN) | + |
| T6 | `pos52` | (c − min Low 252) / (max High 252 − min Low 252) | + |
| T7 | `atr_ratio` | ATR20/ATR100 (TR = max(H−L, |H−c_{-1}|, |L−c_{-1}|), trung bình đơn) — co hẹp biên độ | − |
| T8 | `dd120` | c / max(c, 120 phiên) − 1 (≤0; gần 0 = ít sụt) | + |
| T9 | `vol_tr` | ln(TB Volume 20 / TB Volume 100); **chỉ trên tập giá tăng** c_t > c_{t-20} (đúng ý "khi giá tăng") | + |
| T10 | `knife` | cờ c < MA200 VÀ MA200_t < MA200_{t-20} | − (cờ loại) |

Thiếu lịch sử (chưa đủ 252/200/120 phiên) ⇒ NaN, loại khỏi ô của chỉ báo đó (khai N mỗi ô).

## 3. Ô so sánh & thống kê
**Họ chính** (13 × 2 book = 26 ô): xếp hạng phần trăm chỉ báo trong book (toàn mẫu, chỉ để MÔ TẢ, không phải quy tắc), d = ret TB tertile cao (T3) − tertile thấp (T1); T10: d = ret(cờ BẬT) − ret(TẮT).
**Tương tác** (9 ô): trong tertile value CAO (phân vị trong G): LAG×`ey`; BAL×`ey`; BAL×`ebitda_y` (chỉ NONFIN). So lệnh xu hướng TỐT vs XẤU theo: T1b `rs120` (trên/dưới trung vị TRONG ô value cao), T3b `d_ma200` (>0 vs ≤0), T10 `knife` (TẮT vs BẬT). d = TỐT − XẤU, kỳ vọng +. Mô tả kèm ret value-cao-toàn-bộ và value-thấp để thấy "value + xác nhận xu hướng" có hơn "value đơn thuần".
**Tổng N trials khai = 35**; BH-FDR trên cả 35 bằng p cụm QUÝ.

Mỗi ô báo: N vị thế từng nhóm, N tháng & N quý, ret TB/trung vị, d, ρ Spearman (họ chính), CI95.
- p bootstrap cụm **THÁNG** entry và cụm **QUÝ** entry (B=5000, seed 20261025, hai phía). **Cổng = cụm QUÝ** (nắm giữ 38–68 ngày ⇒ cụm tháng gối nhau).
- **Xếp hạng trong năm (G×year)**: tertile lại theo phân vị trong từng (G, năm) [tương tác: phân vị value và trung vị rs120 trong từng năm]; d_y và p_y cụm QUÝ — khử trôi theo thời gian.
- IS ≤2019 / OOS 2020+; bỏ 2020–21; cắt 2% lệnh lãi lớn nhất (ret > phân vị 98 của ô); ledger pin1M.
- **Kiểm soát value**: ret ~ 1 + pr_x + pr_ey (pr_ey = phân vị 1/PE trong G), hệ số pr_x và p cụm QUÝ. (Ô tương tác đã nằm trong value cao ⇒ kiểm soát thêm pr_ey trong ô.)
- Mô tả tương quan Spearman của 13 chỉ báo với nhau và với ey.
- **PIT tertile** (chỉ cho ô nào qua cổng chính): cutoff tertile dựng từ các vị thế ĐÃ entry trước đó cùng book (mở rộng dần, ≥60 vị thế trước), báo d.

## 4. Tiêu chí "đáng xét tiếp" (TẤT CẢ)
(a) dấu d đúng hướng khai trước; (b) |d| ≥ 2pp/vị thế; (c) q < 0,10 (BH 35, cụm QUÝ); (d) p_y < 0,10 (xếp hạng trong năm, cụm QUÝ) cùng dấu; (e) d_IS, d_OOS cùng dấu đúng hướng; (f) bỏ 2020–21 và cắt 2% không đảo dấu; (g) pin1M cùng dấu và |d| ≥ 2pp; (h) kiểm soát value: hệ số cùng dấu và p < 0,10 (cụm QUÝ) — tức còn thông tin SAU value; (i) mỗi nhóm so sánh ≥ 100 vị thế, ngược lại gắn "thiếu mẫu" và không đạt (BAL top-tertile ~100 ⇒ các ô tương tác BAL gần như chắc thiếu mẫu — khai trước).

## 5. Cảnh báo khai trước
- **BAL đã chọn theo momentum (SIGNAL_V11)** ⇒ biến xu hướng/RS/vị trí 52w trong BAL bị **thu hẹp biên độ (range restriction)**: lệnh BAL đều đã "đang tăng"; tác dụng lọc thêm, nếu có, là phần dư bên trong bộ chọn, và dấu có thể ngược (đuổi giá quá xa). Kết quả BAL không được đọc thành "xu hướng không có giá trị" nói chung — chỉ là "không thêm gì trên SIGNAL_V11".
- LAG chọn theo bất ngờ LN (PEAD), không theo giá ⇒ biên độ xu hướng rộng; đây là chỗ "value + xác nhận xu hướng / tránh dao rơi" có cơ hội nhất.
- Các chỉ báo tương quan mạnh với nhau (T1/T3/T6/T8) ⇒ 35 trials KHÔNG độc lập; BH vẫn hợp lệ dưới PRDS nhưng bảo thủ hơn cần thiết — chấp nhận.
- Không lặp lại A2/F3/F2. T10 khác F2 (F2 = trên MA50 & MA50 dốc lên; T10 = dưới MA200 & MA200 dốc xuống).

## 6. Tự kiểm
- Tính tay Python thuần (không numpy/pandas) `rs60`, `d_ma200`, `pos52`, `atr_ratio` (≥3 chỉ báo) cho ≥3 vị thế, khớp engine (sai số tương đối < 1e-9).
- Σ P&L vị thế = TX cash (đọc lại từ ledger) cho cả 2 ledger.
- Chạy lại dưới `env -u TZ` ⇒ output byte-identical.
