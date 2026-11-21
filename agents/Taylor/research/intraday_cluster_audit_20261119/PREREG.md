# PREREG — kiểm toán cụm intraday HOSE (#1, #4, #2-phần-khả-thi) — 2026-11-19, job Taylor_20261119_044412
Viết TRƯỚC khi tính kết quả. Chỉ đã xem: README export, đếm số ngày signal (in_stats=1) và min/max cột đầu vào. Không đụng dữ liệu live.
Dữ liệu: `data/{insample,holdout}` (md5: data_md5.txt). Python: /home/trido/thanhdt/wc_venv/bin/python, seed 7.

## 1. Đơn vị & cụm (#1)
- Setup xét: FZ-001, FZ-002, C-CEIL, C-NFLOOR, C-NFLOOR3, từng setup RIÊNG (không gộp deal giữa setup — trùng mã/ngày). Chỉ `in_stats==1`.
- **Cụm CHÍNH (E5)**: xếp các `signal_day` riêng của setup theo lịch phiên (lịch = ngày trong data/bq/capit_breadth.csv); hai signal_day cách nhau ≤5 phiên thuộc cùng 1 cụm (chuỗi nối). Cụm = 1 quan sát.
- Phụ (báo cáo, không dùng để PASS): cụm = signal_day (D1); cụm = tuần ISO (W).
- Giá trị cụm = trung bình đều các deal trong cụm (cột đang xét). Excess cấp cụm = trung bình đều theo cụm (KHÔNG trọng số deal).
- Đếm cụm <15 ⇒ "KHÔNG ĐỦ N" cho setup đó (không tính DSR/placebo, vẫn in số mô tả). 15–19 cụm ⇒ không đạt PASS (cần ≥20).
- Khung: in-sample (chỉ ngưỡng/kết luận chính) và holdout (báo cáo riêng, cùng công thức, KHÔNG đặt lại ngưỡng; holdout cụm thường <15 ⇒ chỉ mô tả).

## 2. Chi phí & hurdle
- Engine: 0,03%/chiều + thuế bán 0,1% = 0,16%/vòng. Thật: 0,097%/chiều (bin/dnse_fee_rates.py) + 0,1% = 0,294%/vòng ⇒ điều chỉnh −0,134% mỗi deal (cố định). `excess_adj = excess_ret − 0,00134`; `net_adj = net_ret_total − 0,00134`.
- Hurdle tiền gửi (chỉ cho tiêu chí tuyệt đối, kèm báo cáo): `idle_rate_proxy.r_idle(d,'dep1m')` tại entry_date × (exit_date−entry_date)/365 ; `abs_adj = net_adj − hurdle`. Nếu hàm lỗi ⇒ nêu rõ + dùng 0.
- Tiêu chí PASS dùng `excess_adj` (so thị trường cùng ngày theo kế hoạch D#1). `abs_adj` báo cáo song song, không đổi verdict.

## 3. Danh sách phép thử (cố định, KHÔNG chọn cấu hình) — 10 phép × 5 setup
T1 số cụm E5 · T2 excess cấp cụm thô (in_stats) · T3 excess_adj cấp cụm · T4 CI90 bootstrap theo cụm của T3 (B=10000, percentile, seed 7) · T5 abs_adj cấp cụm (hurdle) · T6 DSR(T=cụm) · T7 placebo khối THÁNG · T8 leave-one-cluster-out (min mean) · T9 tỷ trọng top-5 cụm trong tổng (cụm dương) · T10 holdout (mô tả).
- T6 DSR: Sharpe cấp cụm SR=mean/std của excess_adj theo cụm; skew/kurt từ chuỗi cụm; Bailey–López de Prado; SR0 từ kỳ vọng cực đại N trial, V = 1/(T−1) (phương sai null). **N CHÍNH = 1000** (nền của dự án, `kb/context_pack.md`); độ nhạy N ∈ {250 (số nhóm kia), 65, 30000}. N=65 là tối thiểu liệt kê được: 7 setup export + 42 (event study 14×3 horizon) + 5 ngưỡng tick + 2 (miễn gate) + 9 (3 book × 3 slot) = 65; Optuna 30.000 trial thuộc C-TAMIX/C-ONID (cho vào cột nhạy cảm). Không có số đếm chính xác hơn từ phía nhóm kia ⇒ ghi "ước lượng từ BC".
- T7 placebo: hoán vị DẤU theo khối tháng — mỗi tháng lịch (theo ngày đầu cụm) là 1 khối; lật dấu cả khối ngẫu nhiên (10.000 lần, seed 7), thống kê = excess_adj cấp cụm; p một phía. (Không hoán vị trong năm.) Đây là kiểm tra H0 "excess đối xứng quanh 0 tại mức tháng", không phải placebo thời điểm.
- T8: bỏ lần lượt từng cụm, báo mean thấp nhất/cao nhất, và có đổi dấu không.

## 4. PASS/FAIL (#1, setup nào cũng phải đạt TẤT CẢ, trên in-sample)
(a) ≥20 cụm E5 · (b) excess_adj cấp cụm > 0 · (c) CI90 bootstrap loại 0 (cận dưới >0) · (d) DSR(N=1000) ≥ 0,95 · (e) placebo khối tháng p<0,05. Setup PASS cả 5 ⇒ "GO-research" (vẫn KHÔNG khuyến nghị wire). Báo thêm LOCO, top-5, holdout nhưng KHÔNG nằm trong PASS.
Verdict #1 tổng: GO nếu ≥1 setup PASS; NO-GO nếu không; "KHÔNG ĐỦ N" nếu mọi setup <15 cụm.

## 5. #4 FZ-001 intraday vs daily
- Universe xấp xỉ: tập mã xuất hiện trong mọi deals_*.csv (55 mã) — danh sách top-50 mcap PIT thật của nhóm kia KHÔNG có trong export; đây là xấp xỉ, khai là hạn chế. Dữ liệu daily: tav2_bq.ticker (D_RSI, OHLC) cho các mã này; universe_pit chỉ để kiểm tra thành viên (in_universe). Kiểm tra tái lập: tỷ lệ deal FZ-001 có (D_RSI_mình<0,32 ∧ brd_mình≥3).
- Bản daily = {(mã, D): D_RSI<0,32 ∧ số mã universe D_RSI<0,32 trong ngày ≥3}. Intraday-FZ001 ⊂ daily (thêm fp_last_hour, fp_close_vwap). Engine daily proxy (cùng luật exit: entry=Open D+1, TP+6%, SL=2×ATR14/close, sellable từ T+2, time-exit theo hold_sessions modal của deals FZ-001, mô hình trên giá điều chỉnh tỷ lệ) áp lên TOÀN daily-set; "market drift" = trung bình mọi mã universe cùng ngày cùng luật. Đo chênh cấp cụm E5: (mean excess_proxy tập INTRADAY) − (mean excess_proxy tập DAILY-ONLY phần bù); CI90 bootstrap theo cụm; PASS: chênh>0 và CI90 loại 0.
- Nếu daily proxy không tái lập được (<80% deal FZ-001 nằm trong daily-set) ⇒ báo "không dựng được bản công bằng", không kết luận.
- CAPIT trùng: CAPIT fire D = breadth(top-250 universe_pit_q, D_RSI<0,3) ≥ 0,31 (đúng công thức golive_recommend_v23.py), chuỗi từ data/bq/capit_breadth.sql. Tỷ lệ = (số signal_day FZ-001 có CAPIT fire cùng D)/(số signal_day FZ-001), ở cấp ngày và cấp cụm E5 (cụm trùng nếu ≥1 ngày trùng). PASS: <50%. Phụ: trùng trong cửa sổ 5 phiên trước D.

## 6. #2 độ nhạy lạc quan (từ deal-list; KHÔNG chạy lại engine)
Trên in_stats==1, mean `net_ret_total` (đối chiếu mean gốc), cả in-sample và holdout, mọi setup có deal:
 S1 (C-CEIL): bỏ deal có entry_px ≥ close_raw_D×1,07 − 1 tick (xấp xỉ "vào đúng trần D+1"; tick HOSE 10/50/100 theo mức giá <10k / <50k / ≥50k). S1b: bỏ deal entry/close_raw_D−1 ≥ +5% (gap lớn). Hạn chế: không có low bar 09:15 ⇒ không phân biệt được ATO-trần-vỡ.
 S2: bỏ crosses_exdate==1; đồng thời mean net_ret_cash vs net_ret_total.
 S3: phí −0,134%/deal.
 S4: S1b+S2+S3 gộp.
 PASS (mỗi setup): |Δmean|/|mean| <25% và không đổi dấu. Bảng skipped book3: đếm reason×setup, insample & holdout.
Chưa làm (cần engine nhóm kia): fill ATO thực tế tại trần, rescale TP/SL ngày GDKHQ, T+3 trước 29/08/2022 (không ảnh hưởng 2023+), cổ phiếu thưởng bán ngay, đuôi khoá sàn nhiều phiên.
