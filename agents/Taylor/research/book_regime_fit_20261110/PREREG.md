# PREREG — book_regime_fit_20261110 (job Taylor_20261110_082023)
Viết 2026-11-10 ~15:50 ICT, TRƯỚC khi chạy part_b.py / part_c.py. Không sửa sau khi chạy; đổi gì ghi ở mục "Lệch prereg" của REPORT.

## Phần B — live có nằm ngoài phân phối backtest?
- Ledger: (1) `R3-park0-pin0pct-SAN` md5 537e349b (theo yêu cầu dispatch); (2) `LICHSU-V2.3A-E1VFVN30-park70-vintage20260625` md5 65e7bb04 (cấu hình khớp papertrade hơn: park70). Chuỗi = `nav_bal_ref`, `nav_lag_ref` (DAILY).
- Control self-check: CAGR tính lại từ `combined_nav` DAILY phải khớp METRIC cagr (sai < 1e-9); md5 file gunzip khớp tên.
- Cửa sổ H = 90 phiên (= số phiên live 2026-07-01→2026-11-06). Thống kê: lợi suất sổ; excess = sổ − VNINDEX (cùng cửa sổ).
- Phân phối: (a) mọi cửa sổ trượt (mô tả); (b) cửa sổ KHÔNG chồng lấn (N≈34) — percentile chính; (c) stationary block bootstrap lợi suất ngày (L=21, B=20000).
- Có điều kiện: (d) hồi quy OLS ret_book ~ ret_VNI trên cửa sổ không chồng lấn; percentile của residual live; (e) tập cửa sổ trượt có ret_VNI ∈ [−12%, −3%].
- Ngưỡng ngôn ngữ: percentile < 5% ở (b) VÀ (d) ⇒ "lệch có ý nghĩa"; 5–15% ⇒ "đuôi, chưa kết luận"; >15% ⇒ "bình thường". "Gãy edge" CHỈ được nói nếu đủ power (tính power với 1 quan sát 90 phiên: P(phát hiện | edge thật = 0)).

## Phần C — biến chế độ PIT cho từng sổ (N_trials khai trước = 8 biến × 2 sổ × 2 outcome = 32 phép thử)
- Đơn vị: tháng lịch m, 2014-02 → 2026-06 (ledger R3 park0). Tín hiệu = giá trị tại phiên cuối tháng m−1 (biết lúc đóng cửa; lệnh T+1). Biến Mỹ lấy ngày ≤ t−1.
- Outcome: Y1 = lợi suất sổ tháng m (`nav_*_ref`); Y2 = Y1 − lợi suất VNINDEX tháng m.
- 8 biến (breadth-tercile ĐÃ test 0/27 ⇒ KHÔNG đưa lại):
  V1 dt5g_state (1..5, `vnindex_5state_dt5g_live`), V2 VNI/MA200−1, V3 VNI drawdown 252 phiên,
  V4 Value Radar score (rolling-10Y, display-only; nghiên cứu), V5 Δ6 tháng lãi huy động (`deposit_rate_vn.deposit_events_df`, proxy có bias hindsight trước 2026-06),
  V6 VIX (≤ t−1), V7 độ phân tán cắt ngang lợi suất 21 phiên trong universe_pit v1, V8 số lệnh vào MỚI của chính sổ trong 63 phiên trước (độ dồi dào tín hiệu; với LAG ≈ mùa BCTC/số surprise lớn).
- Thước: Spearman IC(V, Y). p-value = circular-shift null (dịch Y so với V mọi độ dời ≥ 12 tháng, giữ tự tương quan cả 2 chuỗi), hai phía.
- BH-FDR q = 0,10 trên 32 phép thử.
- PASS cần đủ CẢ: q_BH < 0,10 toàn mẫu · cùng dấu IS (2014-2019) và OOS (2020-2026-06) · |IC_OOS| ≥ 0,10. Kèm bảng tercile (cutoff IS áp cho OOS) chỉ để mô tả.
- Pre-flight power: N ≈ 149 tháng, IC tối thiểu phát hiện ~ 2/√N ≈ 0,16 (iid); sau BH 32 phép + tự tương quan ⇒ thực tế cần |IC| ≳ 0,25. Edge điều kiện nhỏ hơn thế sẽ KHÔNG thấy được — đó là kết luận hợp lệ.
- Nếu 0 biến PASS: kết luận "không nhận diện được bằng dữ liệu hiện có". Không chạy thêm biến để "tìm cho ra".

## Phần D — mô tả (không có kiểm định chọn biến)
- Đợt giảm lịch sử: VNI 90 phiên ≤ −7% từ 2008, gộp thành đợt rời; so tốc độ (phiên đỉnh→đáy), độ sâu, breadth (MA200, universe_pit) đầu/cuối, DT5G state (từ 2014). Không re-tune DT5G.
