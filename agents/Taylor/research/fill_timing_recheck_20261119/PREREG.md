# PREREG — fill_timing HYBRID recheck (job Taylor_20261119_044040) — viết TRƯỚC khi chạy engine
Chưa qua quant-skeptic. Chỉ đọc, không đổi config live.

## Dữ liệu (đã đo trước khi viết)
- data/intraday_1m: 16 mã, 1 phút, 2023-09-11 → 2026-06-12 (686 phiên/mã). data/intraday_full.pkl: 335 mã, 15 phút, 2023-09-11 → 2026-05-12 (mtime 2026-05-17).
- data/VNINDEX.csv đóng băng, hết 2026-05-26. KHÔNG có dữ liệu intraday sau 2026-06-12; KHÔNG fetch live.
- Giá nội phiên: chỉ dùng TỶ SỐ trong cùng ngày ⇒ không phụ thuộc điều chỉnh. Control leg (so prior close) kế thừa cách xử lý của intraday_fill_timing.py.
## Thiết kế
- Lịch live đóng băng, 1 trial, KHÔNG tune. BUY blocks 11:00,11:15,13:00,13:15,13:30; SELL blocks 09:15,09:30,09:45,10:00.
- Giá fill tại block = OPEN của bar 1 phút có nhãn HH:MM (bar đầu tiên >= HH:MM). Benchmark = open bar đầu phiên (09:15).
- Chỉ số ticker-ngày: BUY = trung bình 5 block của (px/open_ngày −1)·1e4 bps; SELL = trung bình 4 block, cùng công thức. BUY âm = rẻ hơn open (tốt); SELL dương = cao hơn open (tốt).
- N = PHIÊN: trung bình cắt ngang các mã theo ngày → chuỗi ngày. CI95 = bootstrap khối theo tuần ISO, 10000 lần, seed 0, trên mean của chuỗi ngày.
- Nhóm ngày giảm: median cắt ngang (16 mã) close-to-close < 0 (VNINDEX.csv hết 05-26 nên dùng proxy này; ghi rõ).
## Cửa sổ
- A "gốc": 2023-09-11→2025-12-31. B "gần nhất": 2026-01-01→2026-06-12. LƯU Ý: toàn bộ dữ liệu có TRƯỚC khi luật được thiết kế/duyệt (bus 06-26, live 08-26) ⇒ B KHÔNG phải OOS thật; OOS thật (06-13→11/2026) = KHOẢNG TRỐNG. Không kết luận "còn đúng ở thị trường giảm 05→11/2026".
- Thanh khoản thấp: 5 mã có median(giá·KL ngày) thấp nhất trong 16 mã (báo riêng). Robustness phụ: 335 mã 15 phút (bar 15m, block dùng open bar cùng nhãn; 11:00 có, các nhãn 15m khớp), đến 2026-05-12.
## Tiêu chí
- PASS BUY: mean(BUY)<=−5 bps, CI95 trên <0, và mean nhóm ngày giảm không đổi dấu (<0). PASS SELL: mean(SELL)>=+5 bps, CI95 dưới >0, nhóm ngày giảm không đổi dấu (>0).
- FAIL/đề xuất rollback: mean BUY-vs-open > +22 bps (ngưỡng current_ops). Ngoài ra = INCONCLUSIVE (nói rõ).
## Self-check
- Control: tái lập intraday_fill_timing.py (open vs prior close, 11:15 close vs prior close): kỳ vọng +18.7 / +1.1 bps (±0.5 trên cùng data); chạy bằng chính script cũ + engine mới, so.
- Không sửa file ngoài thư mục này.
