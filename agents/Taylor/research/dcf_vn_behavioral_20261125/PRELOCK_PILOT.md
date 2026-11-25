# PRELOCK — pilot G0 "tâm tham chiếu hành vi" (khoá TRƯỚC khi chạy; job Taylor_20261125_104308)

Mục đích: kiểm RẺ xem đặc trưng neo giá (đỉnh 52 tuần, giá vốn đám đông) có thêm kỹ năng dự báo lợi suất tương đối
12/24 tháng NGOÀI những gì đã có (đà/đảo chiều, E/P, khoảng cách tới tâm nội tại) hay không. Không phải backtest NAV.

## 1. Dữ liệu (tái dùng khung V3.1 đã qua skeptic V3)
- Panel tháng `dcf_vn_redesign_20261125c/out_F/vp2.parquet` (md5 ghi ở MD5SUMS): nhãn `fwd12_h50`, `fwd24_h50`
  (log, Close điều chỉnh, mã ngừng giao dịch mất 50%; cận h0/h100 báo kèm), cổng `in_universe` (universe_pit + cổng tự
  dựng cho mã vắng BQ), `lv_ENS2` (log tâm nội tại/vốn hoá, mù giá), `lv_L2_ENS2` (lớp 2), `ep`, `N`.
- Giá ngày một vintage: `data/bq_cache/ticker` (2013+) + `out/px_pre2013_d.csv` (2006–2013) + `out/delisted/px_*.csv`
  (mã vắng BQ) — đúng 3 nguồn mà `b_panel.py` dùng. Không `profit_*`, không `ticker_prune`.

## 2. Đặc trưng (tính tới phiên cuối tháng as-of, chỉ dùng dữ liệu ≤ ngày đó)
- `hi52` = log(Close / max Close 252 phiên gần nhất, gồm hôm nay) (≥ 120 phiên).
- `cgo` = log(Close / RP), RP_t = (1 − to_t)·RP_{t−1} + to_t·Close_t, to_t = min(Volume_t / N, 1) (N = số CP PIT của
  panel, ffill theo mã), khởi tạo RP = Close phiên đầu; cần ≥ 250 phiên lịch sử. (Grinblatt–Han dạng đệ quy.)
- `mom` = log(Close_{−21} / Close_{−252}); `rev1` = log(Close / Close_{−21}) (đếm theo phiên có giá của mã).
- `ep`, `lv_ENS2`, `lv_L2_ENS2` lấy từ panel.
Mọi đặc trưng đổi sang hạng trong tháng (in-universe), co về [−0,5; +0,5].

## 3. Mô hình (hồi quy cắt ngang từng tháng kiểu Fama–MacBeth trên y khử trung bình tháng, winsor 1/99 khi fit)
B1 = {mom, rev1} · B2 = {ep} · B3 = {lv_ENS2} · B4 = {lv_L2_ENS2} · **F0 = {mom, rev1, ep, lv_ENS2}** ·
**F = F0 + {hi52, cgo}** · A = {lv_ENS2, hi52, cgo} · RW = dự báo 0 (giá tương đối không đổi).
Hệ số tại tháng t = trung bình hệ số các tháng s có nhãn đã đóng (s + h ≤ t), s ≥ 2013-01, cần ≥ 12 tháng.
- IS (cuốn chiếu PIT): h=12 as-of 2015-01→2019-12; h=24 as-of 2016-01→2019-12.
- OOS (ĐÓNG BĂNG hệ số tại 2019-12: s ≤ 2018-12 với h=12; s ≤ 2017-12 với h=24): h=12 as-of 2020-01→2025-10;
  h=24 as-of 2020-01→2024-10. Mẫu chung: dòng in-universe có đủ MỌI đặc trưng của F và nhãn.

## 4. Thước đo
(1) IC = Spearman theo tháng giữa dự báo và nhãn, trung bình; CI bootstrap khối NĂM as-of (B = 2000, seed 20261125);
hiệu IC giữa hai mô hình bootstrap cặp. (2) Kỹ năng sai số tương đối = 1 − MAE(y_dm − ŷ)/MAE(y_dm) (RW = 0).
(3) Sai số tuyệt đối log: ŷ + μ_t (μ_t = trung bình cuốn chiếu lợi suất EW h tháng đã đóng) so với RW (0) và RW + μ_t.
(4) Tỉ lệ đúng chiều tương đối ở tercile dự báo cao nhất / thấp nhất. (5) IC trong tercile rẻ / đắt theo `lv_ENS2`.
(6) Mô tả: bảng 2×2 (nội tại rẻ/đắt × thành phần hành vi cao/thấp) của y_dm 12 và 24 tháng.

## 5. Luật quyết định pilot (MỘT phép thử chính)
Phép thử chính: **ΔIC(F − F0) ở h = 12**.
- **CÓ TÍN HIỆU**: ΔIC > 0, CI 95% khối năm không chứa 0 ở CẢ IS và OOS, và kỹ năng sai số tương đối của F > F0 ở cả hai.
- **YẾU**: đạt ở đúng một era, hoặc dấu dương cả hai nhưng CI chứa 0.
- **KHÔNG CÓ TÍN HIỆU**: còn lại ⇒ nói thẳng, đề xuất dừng nhánh "neo giá thêm kỹ năng dự báo".
Phụ (không quyết định): h = 24; A so B3; F so B1, B2, B3, B4; phân phía rẻ/đắt.
Số phép thử: 1 chính + 1 horizon phụ; mọi thứ thêm sau khi thấy số gắn nhãn "giả thuyết".
N độc lập: IS 5 năm as-of (h=12) — sức mạnh yếu, nói rõ trong kết quả. Không đo NAV ⇒ không có TC/pin; khi sang G1
dùng TC 0,1%/chiều, pin0% (sàn).
