# A (H2) — khai báo TRƯỚC khi fit (14/11/2026, job Taylor_20261114_063556)
Dữ liệu: agents/Mike/research/livermore_stock_battery_20261105/{livermore_results.csv, SEALED_truth.json, cases/S*.csv} (N=100, 1 lượt, khoá 05/11).
Đặc trưng (tính từ CHÍNH file case Livermore đã đọc, 250 phiên, chỉ ≤ as-of):
- mom20 = close[249]/close[229] − 1 ; mom60 = close[249]/close[189] − 1
- rp250 = (close[249] − min(low[0..249])) / (max(high[0..249]) − min(low[0..249]))
Không thêm đặc trưng nào khác vào hồi quy chính.
Biến phụ thuộc: (y1) H20_P_UP liên tục — OLS; (y2) H20_DIR (UP=1) — xác suất tuyến tính OLS + logistic (McFadden R²).
Báo: R², R² hiệu chỉnh, R² LOO-CV (out-of-sample) cho cả y1, y2. Ngưỡng G0 theo §8: R² ≥ 0,5 ⇒ "Livermore = mom ngược".
Luật cơ học "mom ngược": R1 DOWN nếu mom20>0; R2 DOWN nếu mom60>0; R3 DOWN nếu rp250>0,5. Báo: % đồng ý với call Livermore, hit vs truth.
Đối chứng "mom thuận" là phần bù của R1/R2 (hit = 100 − hit ngược).
Tách RECOGNIZED true/false (nếu nhóm true rỗng thì ghi rõ).
