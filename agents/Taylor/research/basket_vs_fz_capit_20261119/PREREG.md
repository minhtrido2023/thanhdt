# PREREG — "FZ có phải chủ yếu là cược thời điểm hồi?" rổ vs FZ vs CAPIT — 2026-11-19, job Taylor_20261119_051521
Viết TRƯỚC khi tính. Đã xem: README+PREREG audit cụm, tên cột deal-list, mô tả `market_drift_same_day` (= trung bình net_ret_total khi mua MỌI mã universe tại ATO D+1, cùng luật exit). CHƯA tính bất kỳ số nào của phép so này (chỉ đã thấy các số do audit trước/Mike tính tay).
Nguồn: `../intraday_cluster_audit_20261119/data/{insample,holdout}/deals_fz-00{1,2}.csv`, `data/bq/{capit_breadth,daily_ohlc}.csv` (md5 ghi trong data_md5.txt). Python $DNA_PYEXE, seed 7, B=10000. Chỉ `in_stats==1`. Cụm = E5 (signal_day cách ≤5 phiên nối chuỗi, lịch = capit_breadth.csv), 1 cụm = 1 quan sát, mỗi cụm = trung bình đều deal (giữ nguyên PREREG audit).
Đã tra data_registry: universe_pit_q (không phải ticker_prune) cho breadth CAPIT; universe xấp xỉ = 55 mã trong deal-list (hạn chế, khai).

## 1. Ba đường (cùng kỳ, cùng exit)
(a) **FZ deal-set**: net_ret_total cấp cụm.
(b) **Rổ-ngày-signal-FZ**: `market_drift_same_day` của engine (mua toàn bộ universe top-50 mcap PIT tại ATO D+1, TP+6%/SL/time-exit 10 phiên theo từng mã) — cấp cụm = trung bình đều của cột đó trên deal cụm. Đây là rổ thật của engine (không phải proxy).
(c) **Rổ-ngày-CAPIT-fire**: ngày D có breadth(top-250 universe_pit_q, D_RSI<0,3) ≥ 0,31 (capit_breadth.csv). Rổ = mua 55 mã universe xấp xỉ có in_universe tại Open D+1, cùng luật exit proxy của audit trước (TP+6%, SL 2×ATR14, sellable T+2, time-exit phiên thứ 10, phí engine 0,16%). Cụm E5 riêng trên các ngày CAPIT fire. Hiệu chuẩn proxy: trên ngày signal FZ so proxy-rổ với (b); nếu corr cấp ngày <0,8 ⇒ nói rõ (c) kém tin cậy.
Phí thật: engine dùng 0,16%/vòng; thật 0,294%/vòng (0,097%×2+0,1%) ⇒ −0,134% cho MỖI đường (a)(b)(c). Rổ nhiều mã: phần trăm phí/mã như nhau, phí cấp rổ = phí trung bình ⇒ −0,134% (không giả định ETF rẻ hơn; ghi chú nếu có ETF thì rổ rẻ hơn ⇒ excess FZ còn nhỏ hơn). **Vì (a),(b) cùng điều chỉnh nên excess FZ−rổ không đổi sau phí; excess nêu cả hai dạng cho đủ.**

## 2. Phép đo (FZ-001, FZ-002 riêng)
M1 mean cấp cụm của (a),(b); tỷ lệ rổ/deal = mean(b)/mean(a) (CI90 bootstrap theo cụm, cặp). M2 excess cấp cụm = mean(a−b) sau phí, CI90 bootstrap theo cụm (percentile). M3 DSR(T=cụm, N=1000, độ nhạy 65/250/30000) + placebo lật dấu khối tháng trên excess. M4 LOCO + top-5. M5 holdout mô tả (cụm <15 ⇒ không suy luận). M6 mean (c) trên cụm CAPIT riêng và trên cụm FZ có CAPIT fire (cửa sổ [đầu cụm−5 phiên, cuối cụm]).
Tương quan ngày FZ vs CAPIT: (i) phi trên lịch phiên (chỉ báo "có signal FZ" vs "CAPIT fire") cả kỳ; (ii) tỷ lệ cụm FZ có CAPIT fire. 
**FZ-có-CAPIT-không**: cụm FZ không có CAPIT fire trong cửa sổ trên ⇒ excess so với rổ-FZ và deal-mean; **N cụm <15 ⇒ chỉ in số mô tả, ghi "không đủ N", không kết luận**.

## 3. Tiêu chí khai trước
"FZ thêm giá trị so với rổ" ⇔ excess cấp cụm sau phí > 0 ∧ CI90 loại 0 (cận dưới>0) ∧ ≥20 cụm E5 (in-sample). Thiếu bất kỳ ⇒ kết luận "FZ ≈ cược thời điểm hồi", và nếu cụm FZ chủ yếu trùng cụm CAPIT thì "CAPIT đã phủ phần lớn". DSR, placebo báo cáo kèm, không đổi verdict. FZ-001 (17 cụm) và FZ-002 (15 cụm) đã biết <20 từ audit trước ⇒ tiêu chí (≥20) không thể đạt: ghi thẳng là FAIL-bởi-N, và báo thêm hai điều kiện còn lại để người đọc phân biệt "không đủ N" với "không có edge".
## 4. Hạn chế khai trước
Universe xấp xỉ 55 mã (c); in-sample là cận trên (nhóm kia tìm setup trên đó); engine proxy ≠ engine thật; holdout ≤4 cụm; (b) dùng chính engine nhóm kia (không độc lập).
